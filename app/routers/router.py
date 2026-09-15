from fastapi import APIRouter
from .chat import chat

router = APIRouter()
router.add_route(chat)
