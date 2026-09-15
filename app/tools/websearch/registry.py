from .functions import web_search
from .schema import WEB_SEARCH_SCHEMA

# Combine them
TOOLS_MAP = {
    "web_search": web_search,
}

# Combine schemas
TOOLS_SCHEMA = [
    WEB_SEARCH_SCHEMA,
]
