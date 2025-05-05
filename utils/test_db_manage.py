import logging

from start_bot import dp
from utils.db_manage import user_actions_insert


# Set up logging
logging.basicConfig(level=logging.INFO)


class FakeUser:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.first_name = 'Test'


class FakeMessage:
    def __init__(self, user):
        self.from_user = user


async def test_user_exist(user_id):
    pool = dp['db_pool']
    bot_name = dp['bot_name']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f"SELECT EXISTS (SELECT 1 FROM supergra.user_actions WHERE user_id = '{str(user_id)}_{bot_name}') AS result;")
            result = await cursor.fetchone()
            if result:
                user_exists = result[0]
                return user_exists
            return False


async def delete_user(user_id):
    print(user_id)
    pool = dp['db_pool']
    bot_name = dp['bot_name']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            delete_query = f"DELETE FROM supergra.user_actions WHERE user_id = '{str(user_id)}_{bot_name}'"
            await cursor.execute(delete_query)
            await conn.commit()
            logging.info(F'TEST USER {user_id} DELETED')


async def test_user_actions_insert():
    user = FakeUser('000000000', 'test_username')
    call = FakeMessage(user)
    geo = 'UZ'
    stage = 'START'
    stream = 'test_stream'
    await user_actions_insert(call, geo, stage, stream, link_usage=0)
    is_user = await test_user_exist(call.from_user.id)
    if not is_user:
        raise Exception('TEST USER WAS NOT CREATED SUCCESSFULLY')
    else:
        await delete_user(call.from_user.id)
