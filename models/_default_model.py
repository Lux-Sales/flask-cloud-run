from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.types import DateTime

from .utils import generate_uuid


class DefaultModel:

    __mapper_args__ = {"always_refresh": True, "confirm_deleted_rows": False}

    id = Column(BIGINT, primary_key=True, autoincrement=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def id_(self):
        return str(self.id)

    def __init__(self, **kwargs):
        self.id = generate_uuid()
        for k, val in kwargs.items():
            self.__setattr__(k, val)
