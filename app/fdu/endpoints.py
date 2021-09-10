import json
import uuid
from pprint import pprint

from fastapi import APIRouter, Depends, Request
from fastapi_sqlalchemy import db
from sqlalchemy.exc import NoResultFound

from app.auth.crud.user_token import get_current_user
from app.fdu.models import Article
from app.fdu import schema
from app.utils import slugify

fdu_router = APIRouter()


@fdu_router.get('/article/list')
async def list_article(request: Request):
    _Local = request.headers["Accept-Language"]
    articles = db.session.query(Article).distinct(Article.slug).filter_by(lang=_Local).all()
    response = {'result': True}
    response.update(schema.ArticleList.parse_obj({'articles': articles}))
    return response


@fdu_router.post('/article/{slug}/post')
async def edit_article(request: Request, slug: str, article_data: schema.ArticleFDUForm):
    _Local = request.headers["Accept-Language"]

    try:
        article = db.session.query(Article).filter_by(slug=slug).one()
        if article.lang == _Local:
            article.title = article_data.title
            article.content = json.dumps(article_data.content)
            db.session.add(article)
            db.session.commit()
            return {'result': True, "reload": False, 'slug': article.slug}

        # Пробуем найти в случае если переключили язык и перезагружаем
        try:
            print("переключил язык и пробуем сохранить")

            article = db.session.query(Article).filter_by(uuid=article.uuid, lang=_Local, ).one()
            article.title = article_data.title
            article.content = json.dumps(article_data.content)
            db.session.add(article)
            db.session.commit()
            return {'result': True, "reload": True, 'slug': article.slug}
        except NoResultFound:
            # Статья еще не была создана на этом языке
            print("статья еще не была создана")
            article = Article(
                title=article_data.title,
                content=json.dumps(article_data.content),
                slug=slugify(article_data.title),
                lang=_Local,
                user_id=article.user_id,
                uuid=article.uuid
            )
            db.session.add(article)
            db.session.commit()
            return {'result': True, "reload": True, 'slug': article.slug}
    except NoResultFound:
        return {'result': True, "errors": "Статья не найдена."}


@fdu_router.delete('/article/{slug}/delete')
async def delete_article(slug: str):
    articles = db.session.query(Article).filter_by(slug=slug).all()
    for article in articles:
        db.session.delete(article)
    db.session.commit()
    return {'result': True}


@fdu_router.put('/article/put')
async def put_article(article_data: schema.ArticleFDUForm, request: Request, user=Depends(get_current_user)):
    print(article_data.title)
    _Local = request.headers["Accept-Language"]
    article = Article(
        title=article_data.title,
        content=json.dumps(article_data.content),
        slug=slugify(article_data.title),
        lang=_Local, user=user,
        uuid=str(uuid.uuid4())
    )
    db.session.add(article)
    db.session.commit()
    return {'result': True}


@fdu_router.get('/article/get/{slug}')
async def get_article_by_uuid(request: Request, slug: str):
    _Local = request.headers["Accept-Language"]
    try:
        article = db.session.query(Article).filter_by(slug=slug).one()
        if article.lang == _Local:
            return {'result': True, "article": schema.Article.from_orm(article)}
        try:
            article = db.session.query(Article).filter_by(uuid=article.uuid, lang=_Local, ).one()
            return {'result': True, "slug": article.slug, "reload": True}
        except NoResultFound:
            return {'result': True, "article": {
                "lang": _Local,
                "content": "",
                "slug": "",
                "uuid": article.uuid,
                "title": ""
            }}
    except NoResultFound:
        return {'result': True, "errors": "Статья не найдена."}

@fdu_router.get('/article/form')
async def get_article_form():
    return {'result': True, 'headers': schema.ArticleFDUForm.get_headers()}

@fdu_router.get('/tree')
async def get_fdu_tree():
    with open('fdu_tree.json', 'r', encoding='utf-8') as tree_json:
        tree = json.load(tree_json)
    return {'result': True, 'tree': tree}

# TODO: исправить этот ужас

@fdu_router.get('/node/form')
async def get_node_form():
    return {'result': True, 'headers': schema.TreeNodeForm.get_headers()}


@fdu_router.post('/node/set_comment/{id}')
async def get_set_comment(request: Request, id: int, tree_node: schema.TreeNodeForm):
    result = []
    def find_node_by_id(tree, id):
        for node in tree:
            if node["id"] == id:
                return result.append(node)
            elif "children" in node.keys() and len(node["children"]) != 0:
                find_node_by_id(node["children"], id)

    with open('fdu_tree.json', 'r', encoding='utf-8') as tree_json:
        tree = json.load(tree_json)

    find_node_by_id(tree, id)
    _Local = request.headers["Accept-Language"]
    result[0][_Local]["comment"] = tree_node.comment
    pprint(tree_node.comment)
    with open('fdu_tree.json', 'w', encoding='utf-8') as tree_json:
        tree_json.write(json.dumps(tree, ensure_ascii=False), )
    return {'result': True}
