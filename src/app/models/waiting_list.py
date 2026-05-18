from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class WaitingList(Base):
    __tablename__ = "waiting_list"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_wait_user_course"),
        UniqueConstraint("course_id", "position", name="uq_wait_course_position"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
