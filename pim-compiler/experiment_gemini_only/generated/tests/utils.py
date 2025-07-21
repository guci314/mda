import random
import string

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate
from app.schemas.article import ArticleCreate
from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_user_authentication_headers(
    *, client: AsyncClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password} # In login form username is used for email
    r = await client.post(f"{settings.API_V1_STR}/users/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


async def create_random_user(db: AsyncSession) -> dict:
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, email=email, password=password)
    user = await crud.crud_user.create(db=db, obj_in=user_in)
    return {"user": user, "password": password}

async def create_random_article(db: AsyncSession, author_id: int) -> dict:
    title = random_lower_string()
    content = random_lower_string()
    article_in = ArticleCreate(title=title, content=content, tag_names=["test", "random"])
    article = await crud.crud_article.create_with_author(db=db, obj_in=article_in, author_id=author_id)
    return {"article": article}
