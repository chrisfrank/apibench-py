import asyncio
import time
import sqlite3

import aiohttp
import databases
import requests


class SQLClient:
    def __init__(self):
        self.sync_db = sqlite3.connect('testposts.db', check_same_thread=False)
        self.sync_db.row_factory = sqlite3.Row
        self.async_db = databases.Database("sqlite:///testposts.db")

    def fetch_posts(self):
        with self.sync_db as db:
            results = db.execute(" SELECT * FROM posts ORDER BY id DESC limit 10")
            return [dict(row) for row in results]

    async def fetch_posts_async(self):
        async with self.async_db.transaction():
            query = "SELECT * FROM posts ORDER BY id DESC limit 10"
            rows = await self.async_db.fetch_all(query)
            return [dict(row) for row in rows]

class HTTPClient:
    def __init__(self):
        self.async_session = aiohttp.ClientSession()
        self.sync_session = requests.Session()

    def fetch_users(self):
        url = "https://jsonplaceholder.typicode.com/users"
        res = self.sync_session.get(url, timeout=5)
        return res.json()

    async def fetch_users_async(self):
        url = "https://jsonplaceholder.typicode.com/users"
        async with self.async_session.get(url, timeout=5) as res:
            return await res.json()
