from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from app.core.mongodb import get_database
from app.schemas.request import Message


class MongoConversation:
    def __init__(self, doc: dict):
        self.id = str(doc["_id"])
        self.user_id = doc["user_id"]
        self.title = doc["title"]
        self.messages = [Message(**m) for m in doc.get("messages", [])]
        self.created_at = doc["created_at"]
        self.updated_at = doc["updated_at"]
        self.model = doc.get("model")

    def to_dict(self) -> dict:
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "user_id": self.user_id,
            "title": self.title,
            "messages": [m.model_dump() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
        }


class MongoConversationStore:
    def __init__(self):
        self._db: Optional[AsyncIOMotorDatabase] = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_database()
        return self._db

    async def create(self, user_id: str, title: str = "New Conversation", model: Optional[str] = None) -> MongoConversation:
        now = datetime.now()
        doc = {
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "model": model,
        }
        result = await self.db.conversations.insert_one(doc)
        doc["_id"] = result.inserted_id
        return MongoConversation(doc)

    async def get(self, conversation_id: str, user_id: str) -> Optional[MongoConversation]:
        try:
            doc = await self.db.conversations.find_one({"_id": ObjectId(conversation_id), "user_id": user_id})
            return MongoConversation(doc) if doc else None
        except Exception:
            return None

    async def get_messages(self, conversation_id: str, user_id: str) -> Optional[List[Message]]:
        conv = await self.get(conversation_id, user_id)
        return conv.messages if conv else None

    async def add_message(self, conversation_id: str, user_id: str, message: Message) -> bool:
        result = await self.db.conversations.find_one_and_update(
            {"_id": ObjectId(conversation_id), "user_id": user_id},
            {"$push": {"messages": message.model_dump()}, "$set": {"updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER
        )
        return result is not None

    async def add_messages(self, conversation_id: str, user_id: str, messages: List[Message]) -> bool:
        if not messages:
            return True
        result = await self.db.conversations.find_one_and_update(
            {"_id": ObjectId(conversation_id), "user_id": user_id},
            {"$push": {"messages": {"$each": [m.model_dump() for m in messages]}}, "$set": {"updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER
        )
        return result is not None

    async def replace_messages(self, conversation_id: str, user_id: str, messages: List[Message]) -> bool:
        result = await self.db.conversations.find_one_and_update(
            {"_id": ObjectId(conversation_id), "user_id": user_id},
            {"$set": {"messages": [m.model_dump() for m in messages], "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER
        )
        return result is not None

    async def delete(self, conversation_id: str, user_id: str) -> bool:
        result = await self.db.conversations.delete_one({"_id": ObjectId(conversation_id), "user_id": user_id})
        return result.deleted_count > 0

    async def list_user_conversations(self, user_id: str, limit: int = 50, skip: int = 0) -> List[MongoConversation]:
        cursor = self.db.conversations.find({"user_id": user_id}).sort("updated_at", -1).skip(skip).limit(limit)
        conversations = []
        async for doc in cursor:
            conversations.append(MongoConversation(doc))
        return conversations


conversation_store = MongoConversationStore()