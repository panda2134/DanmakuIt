from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence, Union, AsyncIterable
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.collection import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import app_config


class MongoCollectionInterface(ABC):
    @abstractmethod
    async def insert_one(self, document: Mapping, bypass_document_validation=False, session=None) -> InsertOneResult:
        pass

    @abstractmethod
    async def update_one(self, filter: Mapping, update: Mapping, upsert=False,
                         bypass_document_validation=False, collation=None,
                         array_filters=None, hint=None, session=None) -> UpdateResult:
        pass

    @abstractmethod
    async def delete_one(self, filter: Mapping, collation=None, hint=None, session=None) -> DeleteResult:
        pass

    @abstractmethod
    async def replace_one(self, filter: Mapping, replacement: Mapping, upsert=False,
                          bypass_document_validation=False, collation=None,
                          hint=None, session=None) -> UpdateResult:
        pass

    @abstractmethod
    async def find_one_and_update(self, filter: Mapping, update: Mapping, projection=None, sort=None, upsert=False,
                                  return_document=ReturnDocument.BEFORE,
                                  array_filters=None, hint=None, session=None,
                                  **kwargs) -> Optional[Mapping]:
        pass

    @abstractmethod
    def find(self, filter: Optional[Mapping], projection: Union[Sequence, Mapping] = None, *args, **kwargs)\
            -> "MongoCursorInterface":
        pass

    @abstractmethod
    async def find_one(self, filter: Union[Mapping, str, None], *args, **kwargs) -> Optional[Mapping]:
        pass

    @abstractmethod
    async def count_documents(self, filter: Mapping, session=None, **kwargs) -> int:
        pass


class MongoCursorInterface(AsyncIterable):
    @abstractmethod
    async def to_list(self, length=None) -> Sequence[Mapping]:
        pass

    @abstractmethod
    def sort(self, key_or_list, direction=None) -> "MongoCursorInterface":
        pass

Database = Mapping[str, MongoCollectionInterface]

def _():
    db: Optional[Database] = None
    async def get_db():
        nonlocal db
        if db is None:
            db: Database = AsyncIOMotorClient(app_config.mongo_uri)[app_config.mongo_db_name]
        return db
    return get_db
get_db = _()
_ = None
