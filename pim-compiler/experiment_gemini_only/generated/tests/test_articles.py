import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import crud
from app.core.config import settings
from app.models.article import ArticleStatus
from tests.utils import create_random_user, get_user_authentication_headers

pytestmark = pytest.mark.asyncio


async def test_create_article(client: AsyncClient, db_session: AsyncSession) -> None:
    user_data = await create_random_user(db_session)
    user = user_data["user"]
    password = user_data["password"]
    headers = await get_user_authentication_headers(
        client=client, email=user.username, password=password
    )

    title = "Test Article"
    content = "This is the content of the test article."
    data = {"title": title, "content": content, "tag_names": ["test", "fastapi"]}
    r = await client.post(f"{settings.API_V1_STR}/articles/", headers=headers, json=data)

    assert r.status_code == status.HTTP_201_CREATED
    article = r.json()
    assert article["title"] == title
    assert article["content"] == content
    assert article["author"]["id"] == user.id
    assert "test" in [tag["name"] for tag in article["tags"]]
    assert "fastapi" in [tag["name"] for tag in article["tags"]]


async def test_get_published_article(client: AsyncClient, db_session: AsyncSession) -> None:
    user_data = await create_random_user(db_session)
    user = user_data["user"]

    # Create a published article
    article_in = {"title": "Published Article", "content": "...", "status": ArticleStatus.PUBLISHED}
    article = await crud.crud_article.create_with_author(db=db_session, obj_in=type("obj", (object,), article_in)(), author_id=user.id)

    # Create a draft article
    draft_in = {"title": "Draft Article", "content": "...", "status": ArticleStatus.DRAFT}
    await crud.crud_article.create_with_author(db=db_session, obj_in=type("obj", (object,), draft_in)(), author_id=user.id)

    r = await client.get(f"{settings.API_V1_STR}/articles/{article.id}")
    assert r.status_code == status.HTTP_200_OK
    fetched_article = r.json()
    assert fetched_article["title"] == article.title

    # Trying to fetch a draft should fail
    r_draft = await client.get(f"{settings.API_V1_STR}/articles/{article.id + 1}")
    assert r_draft.status_code == status.HTTP_403_FORBIDDEN


async def test_get_articles_list(client: AsyncClient, db_session: AsyncSession) -> None:
    user_data = await create_random_user(db_session)
    user = user_data["user"]

    # Create some articles
    await crud.crud_article.create_with_author(db=db_session, obj_in=type("obj", (object,), {"title": "A1", "status": ArticleStatus.PUBLISHED, "tag_names": ["tech"]})(), author_id=user.id)
    await crud.crud_article.create_with_author(db=db_session, obj_in=type("obj", (object,), {"title": "A2", "status": ArticleStatus.PUBLISHED, "tag_names": ["news"]})(), author_id=user.id)
    await crud.crud_article.create_with_author(db=db_session, obj_in=type("obj", (object,), {"title": "A3", "status": ArticleStatus.DRAFT, "tag_names": ["tech"]})(), author_id=user.id)

    # Test getting all published articles
    r = await client.get(f"{settings.API_V1_STR}/articles/")
    assert r.status_code == status.HTTP_200_OK
    articles = r.json()
    assert len(articles) == 2
    assert "A3" not in [a["title"] for a in articles]

    # Test filtering by tag
    r_tagged = await client.get(f"{settings.API_V1_STR}/articles/?tag_name=tech")
    assert r_tagged.status_code == status.HTTP_200_OK
    tagged_articles = r_tagged.json()
    assert len(tagged_articles) == 1
    assert tagged_articles[0]["title"] == "A1"
