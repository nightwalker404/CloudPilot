import requests
from app.core import get_settings

settings = get_settings()

def web_search(query: str, max_results: int = 5) -> str:
    """Search the web through the local SearXNG instance."""

    if not query or not query.strip():
        raise ValueError("query must not be empty")

    if not isinstance(max_results, int):
        max_results = 5

    max_results = max(1, min(max_results, 10))

    searxng_url = getattr(settings, "searxng_url", "http://searxng:8080").rstrip("/")

    response = requests.get(
        f"{searxng_url}/search",
        params={
            "q": query,
            "format": "json",
            "categories": "general",
        },
        timeout=15,
    )

    if not response.ok:
        raise RuntimeError(
            f"SearXNG search failed ({response.status_code}): "
            f"{response.text[:500]}"
        )

    data = response.json()
    results = data.get("results", [])

    if not results:
        return f"No web results found for '{query}'."

    lines = [f"🔎 Web search results for '{query}':"]

    for i, result in enumerate(results[:max_results], start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = (result.get("content") or "").strip()

        if len(content) > 300:
            content = content[:300].rsplit(" ", 1)[0] + "…"

        lines.append(
            f"{i}. {title}\n"
            f"   {url}\n"
            f"   {content}"
        )

    return "\n".join(lines)