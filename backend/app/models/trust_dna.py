import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TrustDNAModel(Base):
    __tablename__ = "trust_dna"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )

    known_countries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    known_devices: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    usual_login_hours: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    known_sim_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    session_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )