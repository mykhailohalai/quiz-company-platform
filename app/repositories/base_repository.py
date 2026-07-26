import logging
import re
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

EntityType = TypeVar("EntityType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[EntityType, UpdateSchemaType]):
    model: type[EntityType]
    not_found_exception: type[Exception]
    already_exists_exception: type[Exception]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 10) -> tuple[list[EntityType], int]:
        total = await self.session.scalar(select(func.count()).select_from(self.model))
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all(), total

    async def get_by_id(self, id: UUID) -> EntityType:
        entity = await self.session.get(self.model, id)
        if entity is None:
            raise self.not_found_exception(id)
        return entity

    async def create(self, entity: EntityType) -> EntityType:
        self.session.add(entity)
        try:
            await self.session.flush()
        except IntegrityError as ex:
            logger.error("IntegrityError on create: %s", ex.orig)
            raise self.already_exists_exception(self._conflict_field(ex))
        return entity

    async def update(self, id: UUID, updated_entity: UpdateSchemaType) -> EntityType:
        entity = await self.get_by_id(id)
        try:
            for field, value in updated_entity.model_dump(exclude_unset=True).items():
                setattr(entity, field, value)
            await self.session.flush()
        except IntegrityError as ex:
            raise self.already_exists_exception(self._conflict_field(ex))
        return entity

    async def delete(self, id: UUID) -> bool:
        entity = await self.get_by_id(id)
        await self.session.delete(entity)
        return True

    @staticmethod
    def _conflict_field(ex: IntegrityError) -> str:
        match = re.search(r"Key \((\w+)\)=", str(ex.orig))
        return match.group(1) if match else "field"
