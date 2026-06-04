from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def build(
        cls, items: list[T], total: int, page: int, per_page: int
    ) -> "PaginatedResponse[T]":
        pages = (total + per_page - 1) // per_page if per_page else 0
        return cls(items=items, total=total, page=page, per_page=per_page, pages=pages)


class MessageResponse(BaseModel):
    """Respuesta genérica con un mensaje y bandera de éxito."""

    success: bool = True
    message: str = "OK"
