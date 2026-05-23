from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, field_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response envelope.

    Every list endpoint returns this shape so callers always know the
    true total count and can build subsequent page requests.

    Example::

        {
          "items":  [...],
          "total":  142,
          "offset": 0,
          "limit":  50
        }
    """

    items: list[T]
    total: int
    offset: int
    limit: int

    @field_validator("limit")
    @classmethod
    def _limit_cap(cls, v: int) -> int:
        if v > 200:
            raise ValueError("limit may not exceed 200")
        return v
