import ujson

import aio_pika
import asyncpg
import aredis
import aiohttp


class SanicRedis(object):
    def __init__(self):
        self.conn = None

    def init_app(self, loop, config):
        _c = dict(loop=loop, url=config)
        _redis = aredis.StrictRedis.from_url(config, decode_responses=True)
        self.conn = _redis
        return self.conn


class SanicPostgresql(object):
    def __init__(self):
        self.conn = None

    async def init_app(self, loop, config):
        _c = dict(loop=loop, dsn=config)
        _pgsql = await asyncpg.create_pool(**_c)
        self.conn = _pgsql
        return self.conn


class SanicRabbitMq(object):
    def __init__(self):
        self.conn = None
        self._channel = None
        self._exchange = None
        self._queues = None

    async def init_app(self, loop, config):
        _c = dict(loop=loop, url=config)
        _mq = await aio_pika.connect_robust(**_c)
        self.conn = _mq
        return self.conn

    async def channel(self):
        self._channel = await self.conn.channel()
        await self._channel.set_qos(prefetch_count=1)

    async def exchange(self, exchange):
        self._exchange = await self._channel.declare_exchange(
            exchange, aio_pika.ExchangeType.TOPIC, durable=True)

    async def bind_async_receiver(self, queue_name, routing_key, callback_func):
        queue = await self._channel.declare_queue(queue_name, durable=True)
        await queue.bind(self._exchange, routing_key)
        await queue.consume(callback_func)

    async def disconnection(self):
        await self.conn.close()

    async def send(self, routing_key, data):
        await self._exchange.publish(
            aio_pika.Message(
                body=ujson.dumps(data).encode('utf-8'), content_type='json'
            ), routing_key=routing_key)


class ClientSessionAgent(object):
    def __init__(self):
        self._session = None

    @property
    def session(self):
        return self._session

    def init_session(self, loop):
        connector = aiohttp.TCPConnector(ttl_dns_cache=300)
        self._session = aiohttp.ClientSession(connector=connector, loop=loop)
        return self._session


db = SanicPostgresql()
redis = SanicRedis()
sanic_mq = SanicRabbitMq()  # gbot mq
inner_mq = SanicRabbitMq()  # gpet内部mq
csa = ClientSessionAgent()
