import requests
from app.core import get_settings

settings = get_settings()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return a readable summary of the top results."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    if not isinstance(max_results, int):
        max_results = 5
    max_results = max(1, min(max_results, 10))

    api_key = getattr(settings, "tavily_api_key", "")
    if not api_key:
        raise RuntimeError(
            "Web search is not configured: set TAVILY_API_KEY in your environment/.env "
            "(free key at https://tavily.com)"
        )

    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
    }

    response = requests.post(TAVILY_SEARCH_URL, json=payload, timeout=15)
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Web search failed ({response.status_code}): {detail}")

    data = response.json()
    results = data.get("results", [])

    if not results:
        return f"No web results found for '{query}'."

    lines = [f"🔎 Web search results for '{query}':"]

    answer = data.get("answer")
    if answer:
        lines.append(f"Summary: {answer}")

    for i, r in enumerate(results, start=1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        content = (r.get("content") or "").strip()
        if len(content) > 240:
            content = content[:240].rsplit(" ", 1)[0] + "…"
        lines.append(f"{i}. {title}\n   {url}\n   {content}")

    return "\n".join(lines)
