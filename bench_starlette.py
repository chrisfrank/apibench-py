import json

from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

import db


db_client = db.SQLClient()
http_client = db.HTTPClient()

def list_posts(request):
    posts = db_client.fetch_posts()
    return Response(
        json.dumps({ "data": posts }, default=str),
        media_type="application/json"
    )

async def list_posts_async(request):
    """
    In this test, async DB access is considerably slower
    """

    posts = await db_client.fetch_posts_async()
    return Response(
        json.dumps({ "data": posts }, default=str),
        media_type="application/json"
    )

async def list_users(request):
    users = await http_client.fetch_users_async()
    return JSONResponse({ "data": users })

async def hello(request):
    return JSONResponse({ "hello": "world" })


app = Starlette(
    on_startup=[db_client.async_db.connect],
    routes=[
        Route('/posts', list_posts),
        Route('/users', list_users),
        Route('/hi', hello),
    ]
)
