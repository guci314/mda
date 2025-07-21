import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import crud
from app.core.config import settings
from app.models.article import ArticleStatus
from tests.utils import create_random_user, get_user_authentication_headers, create_random_article

pytestmark = pytest.mark.asyncio


async def test_create_comment_on_article(client: AsyncClient, db_session: AsyncSession) -> None:
    # Create user and article
    user_data = await create_random_user(db_session)
    user = user_data["user"]
    password = user_data["password"]
    article_data = await create_random_article(db_session, author_id=user.id)
    article = article_data["article"]

    # Get auth headers for another user who will comment
    commenter_data = await create_random_user(db_session)
    commenter = commenter_data["user"]
    commenter_password = commenter_data["password"]
    headers = await get_user_authentication_headers(
        client=client, email=commenter.username, password=commenter_password
    )

    comment_content = "This is a test comment."
    data = {"content": comment_content}
    r = await client.post(
        f"{settings.API_V1_STR}/articles/{article.id}/comments/",
        headers=headers,
        json=data,
    )

    assert r.status_code == status.HTTP_201_CREATED
    comment = r.json()
    assert comment["content"] == comment_content
    assert comment["author"]["id"] == commenter.id


async def test_get_comments_for_article(client: AsyncClient, db_session: AsyncSession) -> None:
    # Create user and article
    user_data = await create_random_user(db_session)
    user = user_data["user"]
    article_data = await create_random_article(db_session, author_id=user.id)
    article = article_data["article"]

    # Create some comments
    await crud.crud_comment.create_with_author_and_article(
        db=db_session,
        obj_in=type("obj", (object,), {"content": "First comment"})(),
        author_id=user.id,
        article_id=article.id,
    )
    await crud.crud_comment.create_with_author_and_article(
        db=db_session,
        obj_in=type("obj", (object,), {"content": "Second comment"})(),
        author_id=user.id,
        article_id=article.id,
    )

    r = await client.get(f"{settings.API_V1_STR}/articles/{article.id}/comments/")
    assert r.status_code == status.HTTP_200_OK
    comments = r.json()
    assert len(comments) == 2
    assert comments[0]["content"] == "First comment"
    assert comments[1]["content"] == "Second comment"
