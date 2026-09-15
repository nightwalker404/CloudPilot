import json
import re
from typing import Optional

from fastapi import Request

from app.tools.registry import TOOLS_SCHEMA, execute_tool
from app.prompts import load_prompt
from app.schemas.request import Message
from app.services.mongo_conversation import conversation_store


def extract_tool_call_from_content(content: str) -> dict | None:
    """
    Parse a tool call emitted as plain JSON text.

    Supports:
        {"name": "web_search", "arguments": {...}}

    and:
        {"function": {"name": "web_search", "arguments": {...}}}
    """

    if not content:
        return None

    text = content.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    # Remove Ollama-style wrapper tags
    text = re.sub(
        r"<tool_call>|</tool_call>|<tools>|</tools>",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    # Format:
    # {"name": "...", "arguments": {...}}
    if "name" in data and "arguments" in data:
        return {
            "name": data["name"],
            "arguments": data["arguments"],
        }

    # Format:
    # {"function": {"name": "...", "arguments": {...}}}
    function = data.get("function")

    if isinstance(function, dict):
        if "name" in function and "arguments" in function:
            return {
                "name": function["name"],
                "arguments": function["arguments"],
            }

    return None


def _messages_to_dict(messages: list[Message]) -> list[dict]:
    """Convert Message objects into Ollama-compatible dictionaries."""

    result = []

    for msg in messages:

        msg_dict = {
            "role": msg.role,
            "content": msg.content,
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls

        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id

        result.append(msg_dict)

    return result


def _dict_to_message(data: dict) -> Message:
    """Convert a dictionary into a Message object."""

    return Message(
        role=data.get("role", "assistant"),
        content=data.get("content", ""),
        tool_calls=data.get("tool_calls"),
        tool_call_id=data.get("tool_call_id"),
    )


def _normalize_arguments(arguments) -> dict:
    """
    Ollama may return function arguments as either
    a dictionary or a JSON string.
    """

    if isinstance(arguments, dict):
        return arguments

    if isinstance(arguments, str):

        try:
            parsed = json.loads(arguments)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return {}


def _normalize_tool_calls(
    assistant_message: dict,
) -> list[dict]:
    """
    Normalize native Ollama tool calls and tool calls
    emitted as JSON text.
    """

    # ---------------------------------------------------------
    # Native Ollama tool calls
    # ---------------------------------------------------------

    tool_calls = assistant_message.get("tool_calls")

    if tool_calls:
        return tool_calls

    # ---------------------------------------------------------
    # Fallback: model emitted JSON in content
    # ---------------------------------------------------------

    content = assistant_message.get("content", "")

    parsed = extract_tool_call_from_content(content)

    if parsed:

        return [
            {
                "function": {
                    "name": parsed["name"],
                    "arguments": parsed["arguments"],
                }
            }
        ]

    return []


async def llm_service(
    request: Request,
    messages: list[Message],
    conversation_id: Optional[str] = None,
    user_id: str = "anonymous",
    model: Optional[str] = None,
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> tuple[str, list[Message], Optional[str]]:

    settings = request.app.state.settings
    client = request.app.state.llm_client

    target_model = model or settings.model

    # ---------------------------------------------------------
    # System prompt
    # ---------------------------------------------------------

    system_messages = load_prompt("v2")

    # ---------------------------------------------------------
    # Initial conversation
    # ---------------------------------------------------------

    full_messages = (
        system_messages
        + _messages_to_dict(messages)
    )

    # Messages that will be saved to MongoDB
    conversation_messages = list(messages)

    # ---------------------------------------------------------
    # Ollama options
    # ---------------------------------------------------------

    options = {
        "temperature": temperature,
    }

    if max_tokens:
        options["num_predict"] = max_tokens

    # =========================================================
    # STEP 1
    # Ask the model whether it needs a tool
    # =========================================================

    print(
        f"[LLM] Calling model {target_model} "
        f"with tools enabled"
    )

    response = client.chat(
        model=target_model,
        messages=full_messages,
        stream=False,
        tools=TOOLS_SCHEMA,
        options=options,
    )

    assistant_message = response["message"]

    print(
        "[LLM] First response:",
        assistant_message,
    )

    # ---------------------------------------------------------
    # Detect tool calls
    # ---------------------------------------------------------

    tool_calls = _normalize_tool_calls(
        assistant_message
    )

    # =========================================================
    # CASE 1
    # Model answered without using a tool
    # =========================================================

    if not tool_calls:

        final_content = assistant_message.get(
            "content",
            "",
        )

        final_msg = Message(
            role="assistant",
            content=final_content,
        )

        conversation_messages.append(final_msg)

        response_text = final_content

    # =========================================================
    # CASE 2
    # Model requested one or more tools
    # =========================================================

    else:

        # Keep the assistant tool-call message in context
        full_messages.append(
            assistant_message
        )

        tool_results = []

        # -----------------------------------------------------
        # Execute requested tools
        # -----------------------------------------------------

        for tool_call in tool_calls:

            function = tool_call.get(
                "function",
                {},
            )

            tool_name = function.get(
                "name"
            )

            if not tool_name:
                continue

            tool_args = _normalize_arguments(
                function.get(
                    "arguments",
                    {},
                )
            )

            print(
                f"[TOOL] Executing {tool_name}"
                f" with {tool_args}"
            )

            try:

                result = execute_tool(
                    tool_name,
                    tool_args,
                )

                print(
                    f"[TOOL] {tool_name} result:"
                    f" {str(result)[:1000]}"
                )

            except Exception as exc:

                result = (
                    f"Error executing {tool_name}: "
                    f"{exc}"
                )

                print(
                    f"[TOOL] {tool_name} failed: "
                    f"{exc}"
                )

            result_text = str(result)

            tool_results.append(
                result_text
            )

            # -------------------------------------------------
            # Send tool result back to Ollama
            # -------------------------------------------------

            tool_message = {
                "role": "tool",
                "content": result_text,
            }

            full_messages.append(
                tool_message
            )

            conversation_messages.append(
                Message(
                    role="tool",
                    content=result_text,
                )
            )

        # =====================================================
        # STEP 2
        # Ask the model to answer using the tool result.
        #
        # IMPORTANT:
        # Tools are deliberately NOT supplied here.
        #
        # This prevents the small model from repeatedly
        # requesting web_search.
        # =====================================================

        answer_messages = list(full_messages)

        answer_messages.append(
            {
                "role": "system",
                "content": (
                    "The requested tool has already been "
                    "executed. Use the tool result above to "
                    "answer the user's original request. "
                    "Do not request or call another tool. "
                    "Provide the final answer directly."
                ),
            }
        )

        print(
            "[LLM] Generating final answer "
            "with tools disabled"
        )

        try:

            final_response = client.chat(
                model=target_model,
                messages=answer_messages,
                stream=False,
                options=options,
            )

            final_assistant = (
                final_response["message"]
            )

            final_content = (
                final_assistant.get(
                    "content",
                    "",
                ).strip()
            )

            print(
                "[LLM] Final response:",
                final_content,
            )

        except Exception as exc:

            print(
                f"[LLM] Final answer generation failed: "
                f"{exc}"
            )

            final_content = ""

        # -----------------------------------------------------
        # Fallback
        #
        # If the model fails to produce a final response,
        # return the actual tool result instead of an error.
        # -----------------------------------------------------

        if not final_content:

            if tool_results:

                final_content = "\n\n".join(
                    tool_results
                )

            else:

                final_content = (
                    "The tool request completed, "
                    "but no result was returned."
                )

        final_msg = Message(
            role="assistant",
            content=final_content,
        )

        conversation_messages.append(
            final_msg
        )

        response_text = final_content

    # =========================================================
    # SAVE CONVERSATION
    # =========================================================

    if conversation_id:

        existing = await conversation_store.get(
            conversation_id,
            user_id,
        )

        if existing:

            await conversation_store.replace_messages(
                conversation_id,
                user_id,
                conversation_messages,
            )

        else:

            conv = await conversation_store.create(
                user_id,
                model=target_model,
            )

            await conversation_store.replace_messages(
                conv.id,
                user_id,
                conversation_messages,
            )

            conversation_id = conv.id

    else:

        conv = await conversation_store.create(
            user_id,
            model=target_model,
        )

        await conversation_store.replace_messages(
            conv.id,
            user_id,
            conversation_messages,
        )

        conversation_id = conv.id

    # =========================================================
    # RETURN
    # =========================================================

    return (
        response_text,
        conversation_messages,
        conversation_id,
    )