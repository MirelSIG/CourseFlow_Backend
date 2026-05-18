from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    token = Column(String(500), primary_key=True, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
