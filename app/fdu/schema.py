from typing import Any, List

from pydantic import Field

from app.utils import BaseSchema


class ArticleFDUForm(BaseSchema):
    title: str = Field(title='Заголовок', min_length=3)
    content: Any = Field(extended_type='editor')


class Article(BaseSchema):
    title: str
    content: str
    slug: str

    class Config:
        orm_mode = True

class ArticleList(BaseSchema):
    articles: List[Article]
