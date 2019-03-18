from sanic import Sanic
from sanic_cors import CORS
from sanic_jwt import Initialize

from ut.authenticate import CustomAuthentication, CustomerResponses
from ut.base import db, redis, sanic_mq, inner_mq, csa
from app.urls import bp as bp_pet
from ut.log_config import LOGGING_CONFIG_FILE_HANDLER


def create_app(settings):
    app = Sanic(__name__, log_config=LOGGING_CONFIG_FILE_HANDLER)
    CORS(app, automatic_options=True)
    app.config.update(**settings)
    app.config.update({'LOGO': None})
    app.blueprint(bp_pet)

    from app.receiver import on_message, on_message_common, on_message_member

    @app.listener('before_server_start')
    async def before_server_start(_app, _loop):
        _app.db = await db.init_app(_loop, _app.config['DATABASES'])
        _app.redis = redis.init_app(_loop, _app.config['REDIS'])
        _app.client_session = csa.init_session(loop=_loop)
        _app.mq = await sanic_mq.init_app(_loop, _app.config['MQ_CONFIG'])
        _app.inner_mq = await inner_mq.init_app(_loop, _app.config['INNER_MQ_CONFIG'])
        await inner_mq.channel()
        await inner_mq.exchange('gemii.gpet.topic')
        await sanic_mq.channel()
        await sanic_mq.exchange('gemii.gbot.topic')
        await sanic_mq.bind_async_receiver('queue.bot.msg.pet', 'queue.bot.msg.pet', on_message)
        await sanic_mq.bind_async_receiver('queue.bot.member.pet', 'queue.bot.member.pet', on_message_member)
        await sanic_mq.bind_async_receiver('queue.bot.common.pet', 'queue.bot.common.pet', on_message_common)

    @app.listener('after_server_stop')
    async def after_server_stop(_app, _loop):
        await _app.client_session.close()
        await _app.db.close()
        _app.redis.connection_pool.disconnect()
        await sanic_mq.disconnection()

    Initialize(app,
               authentication_class=CustomAuthentication,
               responses_class=CustomerResponses,
               refresh_token_enabled=False,
               secret=settings['JWT_SECRET'],
               expiration_delta=1*60*60)
    return app
