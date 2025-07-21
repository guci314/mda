from __future__ import annotations

import datetime

from sqlalchemy import Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)
    article: Mapped["Article"] = relationship(back_populates="comments")

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="comments")

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
