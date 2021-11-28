from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence,  Union
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.collection import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import app_config

class MongoCollectionInterface(ABC):
    @abstractmethod
    async def insert_one(self, document, bypass_document_validation=False, session=None) -> InsertOneResult:
        pass

    @abstractmethod
    async def update_one(self, filter, update, upsert=False,
                         bypass_document_validation=False, collation=None,
                         array_filters=None, hint=None, session=None) -> UpdateResult:
        pass

    @abstractmethod
    async def delete_one(self, filter, collation=None, hint=None, session=None) -> DeleteResult:
        pass

    @abstractmethod
    async def find_one_and_update(self, filter, update, projection=None, sort=None, upsert=False,
                                  return_document=ReturnDocument.BEFORE,
                                  array_filters=None, hint=None, session=None,
                                  **kwargs) -> Optional[Mapping]:
        pass

    @abstractmethod
    def find(self, filter: Union[Mapping, None], projection: Union[Sequence, Mapping] = None, *args, **kwargs)\
            -> "MongoCursorInterface":
        pass

    @abstractmethod
    async def find_one(self, filter: Union[Mapping, str, None], *args, **kwargs) -> Optional[Mapping]:
        pass

    @abstractmethod
    async def count_documents(self, filter: Union[Mapping, str, None], session=None, **kwargs) -> int:
        pass


class MongoCursorInterface(ABC):
    @abstractmethod
    async def to_list(self, length=None) -> Sequence[Mapping]:
        pass

    @abstractmethod
    def sort(self, key_or_list, direction=None) -> "MongoCursorInterface":
        pass


db_client = AsyncIOMotorClient(app_config.mongo_url)
db = db_client[app_config.mongo_db_name]

room_collection: MongoCollectionInterface = db['room']
