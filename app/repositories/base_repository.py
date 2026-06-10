from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

EntityType = TypeVar("EntityType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[EntityType, UpdateSchemaType]):
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> tuple[list[EntityType], int]:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> EntityType | None:
        pass

    @abstractmethod
    async def create(self, entity: EntityType) -> EntityType:
        pass

    @abstractmethod
    async def update(self, id: UUID, updated_entity: UpdateSchemaType) -> EntityType | None:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
