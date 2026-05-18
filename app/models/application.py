from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_application"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    has_darde = Column(Boolean, nullable=True)
    previous_education = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
