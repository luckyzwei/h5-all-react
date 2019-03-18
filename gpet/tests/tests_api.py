import asyncio
import unittest

from ut.base import SanicRedis, SanicPostgresql
from app import create_app, db, redis
from config import settings

loop = asyncio.get_event_loop()


def _run(coro):
    """Run the given coroutine."""
    return loop.run_until_complete(coro)


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sanic_db = SanicPostgresql()
        sanic_redis = SanicRedis()
        cls.db = _run(sanic_db.init_app(loop, settings['DATABASES']))
        cls.redis = sanic_redis.init_app(loop, settings['REDIS'])

    @classmethod
    def tearDownClass(cls):
        _run(cls.db.close())
        cls.redis.connection_pool.disconnect()

    def setUp(self):
        self.union_id = 'oVzypxKN0AhfXT-U8i8duAmSmbHM'
        self.app = create_app(settings)
        self.client = self.app.test_client

    def _connect_db_redis(self):
        _run(db.init_app(loop, settings['DATABASES']))
        redis.init_app(loop, settings['REDIS'])

    def get_api_headers(self, union_id):
        request, response = self.client.post('/auth', json={'union_id': union_id})
        data = response.json
        self.assertEqual(response.status, 200)
        self.assertEqual(data['code'], 1200)
        return {
            'Authorization': f'Bearer {data["access_token"]}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    async def get_user_lasted_robot_distribute(self, user_id):
        async with self.db.acquire() as con:
            st = await con.fetchrow('select robot_id from "robot_distribute" where user_id=$1 order by create_date desc', user_id)
        return st

    async def get_robot_info(self, robot_id):
        async with self.db.acquire() as con:
            robot = await con.fetchrow('select head_url, qr_code, wechat_no, name from "robot" where id=$1', robot_id)
        return robot

    async def get_user_info(self, union_id):
        async with self.db.acquire() as con:
            user = await con.fetchrow('select * from "user" where union_id=$1', union_id)
        return user

    def test_auth_token(self):
        request, response = self.client.post('/auth', json={'union_id': self.union_id})
        data = response.json
        self.assertEqual(response.status, 200)
        self.assertEqual(data['code'], 1200)

    def test_exist_user_robot_distribute(self):
        user = _run(self.get_user_info(self.union_id))
        self.assertIsNotNone(user)
        request, response = self.client.post('/robot/distribution',
                                             json={"open_id": user['open_id'], "union_id": user['union_id']})
        data = response.json
        self.assertEqual(response.status, 200)
        self.assertEqual(data['code'], 1200)

    def test_enter_homepage(self):
        auth_headers = self.get_api_headers(self.union_id)
        request, response = self.client.get('/groups?status=1&current_page=0&page_size=10', headers=auth_headers)
        data = response.json
        self.assertEqual(response.status, 200)
        self.assertEqual(data['code'], 1200)
