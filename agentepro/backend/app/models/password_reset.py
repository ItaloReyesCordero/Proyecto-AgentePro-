from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResetStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"


class PasswordResetRequest(Base):
    """Solicitud de recuperación de contraseña de un dueño de negocio.

    NO se cambia ninguna contraseña aquí: solo queda registrada la petición para
    que el super admin la revise, confirme que es el dueño real y recién entonces
    genere una contraseña nueva al azar (ver `admin.py`). Las cuentas superadmin
    nunca generan solicitudes (su contraseña no se recupera por este flujo).
    """

    __tablename__ = "password_reset_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[ResetStatus] = mapped_column(
        SAEnum(ResetStatus, name="reset_status_enum"),
        nullable=False,
        default=ResetStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<PasswordResetRequest(email={self.email}, status={self.status})>"
