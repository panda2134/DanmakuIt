from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import app_config

db: AsyncIOMotorDatabase = motor_asyncio.AsyncIOMotorClient(app_config.mongo_url)[app_config.mongo_db_name]