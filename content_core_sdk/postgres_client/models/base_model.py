from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Base class for all models
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  

    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
