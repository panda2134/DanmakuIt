from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence,  Union
from pymongo import DESCENDING, ASCENDING
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import app_config

class MongoCollectionInterface(ABC):
    @abstractmethod
    async def insert_one(self, document, bypass_document_validation: bool, session) -> InsertOneResult:
        pass

    @abstractmethod
    async def update_one(self, filter, update, upsert=False, bypass_document_validation=False, collation=None, array_filters=None, hint=None, session=None) -> UpdateResult:
        pass

    @abstractmethod
    async def delete_one(self, filter, collation=None, hint=None, session=None) -> DeleteResult:
        pass

    @abstractmethod
    def find(self, filter: Union[Mapping, None], projection: Union[Sequence, Mapping], *args, **kwargs) -> "MongoCursorInterface":
        pass

    @abstractmethod
    async def find_one(self, filter: Union[Mapping, str, None], *args, **kwargs) -> Optional[Mapping]:
        pass


class MongoCursorInterface(ABC):
    @abstractmethod
    async def to_list(self) -> Sequence[Mapping]:
        pass

    @abstractmethod
    def sort(self, key_or_list, direction=None) -> "MongoCursorInterface":
        pass

db = AsyncIOMotorClient(app_config.mongo_url)[app_config.mongo_db_name]

room_collection: MongoCollectionInterface = db['room']