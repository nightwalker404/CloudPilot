from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.configs import get_settings
from contextlib import asynccontextmanager


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    settings = get_settings()
    mongodb.client = AsyncIOMotorClient(settings.mongo_uri)
    mongodb.db = mongodb.client[settings.mongo_db_name]
    
    await mongodb.db.conversations.create_index([("user_id", 1), ("created_at", -1)])
    await mongodb.db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
    
    print(f"Connected to MongoDB: {settings.mongo_db_name}")


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    return mongodb.db