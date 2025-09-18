from uuid import UUID

from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, DateTime
import sqlalchemy

from datetime import datetime

Base = declarative_base()


class MessageLog(Base):
    __tablename__ = 'message_logs'

    id: Mapped[UUID] = mapped_column(sqlalchemy.UUID, primary_key=True)

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    original_text: Mapped[str] = mapped_column(Text)
    edited_text: Mapped[str] = mapped_column(Text, nullable=True)

    is_deleted: Mapped[int] = mapped_column(BigInteger, default=0)

    event_type: Mapped[str] = mapped_column(String(20))  # 'created', 'edited', 'deleted'

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    from_user_id: Mapped[int] = mapped_column(BigInteger)
