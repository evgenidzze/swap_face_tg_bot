import functools
import json
from datetime import datetime, timedelta
from aiomysql import Pool, create_pool, Cursor
import logging
from create_bot import dp, bot, scheduler
import aioredis
import os


class user_jimpartner_res():
    user_list = {}
    user_mailling = {}


async def on_startup_db(dp):

    logging.warning(
        'Starting connection pool to MySQL'
    )
    pool = await create_pool(
        host='130.0.238.226',
        user='Zhenya',
        password='AaLaBu14!W',
        db='supergra',
        autocommit=True,
        maxsize=10,
    )
    bot_info = await bot.get_me()
    bot_name = bot_info.username
    dp['bot_name'] = bot_name
    dp['db_pool'] = pool
    from utils.test_db_manage import test_user_actions_insert
    await test_user_actions_insert()


def log_exceptions(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            err_text = f"Exception in {func.__name__}: {e}"
            logging.error(err_text, exc_info=True)
            # await bot.send_message(chat_id=397875584, text=err_text)
            await bot.send_message(chat_id=419445433, text=err_text)

    return wrapper


@log_exceptions
async def Redis_subscribe(date):
    print('Start Redis')
    logging.info(f'Start Redis\n{date}')
    r = aioredis.Redis(
        host='138.68.128.22',
        port=6379,
        health_check_interval=30,
        password="AaLaBu14!",
        db=0
    )
    pubsub = r.pubsub()
    await pubsub.subscribe(date)
    async for message in pubsub.listen():
        data = message.get('data')
        # await asyncio.sleep(300)
        if type(data) != int:
            data = data.decode()
            data = json.loads(data)
            user_jimpartner_res.user_mailling = {}
            if data["utm_content"] not in user_jimpartner_res.user_list:
                user_jimpartner_res.user_list.update(
                    {data["utm_content"]: {"dep": None, "sum": 0, "click_reg": None, "is_registered": None}})
            if user_jimpartner_res.user_list[data["utm_content"]]["is_registered"] != data["is_registered"] or \
                    user_jimpartner_res.user_list[data["utm_content"]]["sum"] != data["full_sum"]:
                if not data["is_registered"]:
                    user_jimpartner_res.user_mailling.update(
                        {data["utm_content"]: ['Всі інші', data['utm_term']]})
                elif data["full_sum"] == 0:
                    user_jimpartner_res.user_mailling.update(
                        {data["utm_content"]: ["Баланс 0", data['utm_term']]})
                elif data["full_sum"] <= 14:
                    user_jimpartner_res.user_mailling.update({data["utm_content"]: ["Не достатньо", data['utm_term']]})
                elif data["full_sum"] > 14:
                    user_jimpartner_res.user_mailling.update(
                        {data["utm_content"]: ["Повний деп", data['utm_term']]})
            user_jimpartner_res.user_list[data["utm_content"]] = {"dep": data["dep"], "sum": data["full_sum"],
                                                                  "click_reg": None,
                                                                  "is_registered": data["is_registered"]}
            if len(user_jimpartner_res.user_mailling) != 0:
                logging.info(str(user_jimpartner_res.user_mailling))
                from utils.utils_module import for_rega_mail
                scheduler.add_job(for_rega_mail, trigger='date',
                                  run_date=datetime.now() + timedelta(seconds=10),
                                  kwargs={'date': user_jimpartner_res.user_mailling,'number':1})
                # scheduler.add_job(pre_server, trigger='date',
                #                   run_date=datetime.now() + timedelta(seconds=15),
                #                   kwargs={'date': user_jimpartner_res.user_mailling})
                scheduler.add_job(update_last_stage, trigger='date',
                                  run_date=datetime.now() + timedelta(seconds=20),
                                  kwargs={'date': user_jimpartner_res.user_mailling})
            with open('user.json', 'w') as f:
                f.write(str(user_jimpartner_res.user_list))


@log_exceptions
async def user_actions_insert(call, geo, stage, stream, link_usage=0):
    # if call.from_user.id in [1311521096, 419445433]:
    #     stage = 'admin'
    pool: Pool = dp['db_pool']
    action_time = datetime.now()
    bot_name = dp['bot_name']
    if call.from_user.username:
        username = f'https://t.me/{call.from_user.username}'
    else:
        username = call.from_user.first_name
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            logging.info(f'INSERTING USER WITH ID {call.from_user.id}')
            await cursor.execute('INSERT INTO supergra.user_actions'
                                 '(action_time, username, user_id, state, stage, bot, link_usage, stream_link)'
                                 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                 (action_time, username, str(call.from_user.id) + f'_{bot_name}', geo, stage, bot_name,
                                  link_usage, stream))
            await conn.commit()


@log_exceptions
async def player_id_insert(user_id_telegram, user_id_web, balance):
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute('INSERT INTO supergra.player_id'
                                     '(user_id_telegram, user_id_web,balance)'
                                     'VALUES (%s, %s,%s)',
                                     (user_id_telegram, user_id_web, balance))
                await conn.commit()
                return True
            except Exception as er:
                logging.info(str(er))
                return False


@log_exceptions
async def users_insert(id_user, used_pass, username, geo):
    pool: Pool = dp['db_pool']
    bot_name = dp['bot_name']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT INTO supergra.users'
                                 '(id_user, used_pass,username,geo)'
                                 'VALUES (%s, %s, %s, %s)',
                                 (str(id_user) + f'_{bot_name}', used_pass, username, geo))
            await conn.commit()


@log_exceptions
async def is_user(message):
    pool: Pool = dp['db_pool']
    bot_name = dp['bot_name']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f"SELECT EXISTS (SELECT 1 FROM supergra.users WHERE id_user = '{str(message.from_user.id)}_{bot_name}') AS result;")
            result = await cursor.fetchone()
            if result:
                user_exists = result[0]
                return user_exists
            else:
                return False


@log_exceptions
async def user_in_players(message, player_id):
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            query = f"SELECT EXISTS (SELECT 1 FROM supergra.player_id WHERE user_id_telegram = {message.from_user.id} AND user_id_web = '{player_id}') AS result;"
            await cursor.execute(query)
            result = await cursor.fetchone()
            user_exists = bool(result[0])
            return user_exists


@log_exceptions
async def get_users_by_stage(stage, bot_name, geo, stream_link) -> tuple:
    if stream_link:
        query = (f"""
                    SELECT user_id,stream_link FROM supergra.last_user_actions
                    WHERE stage LIKE '%{stage}%'
                    AND bot = '{bot_name}'
                    AND state = '{geo}'
                    AND stream_link = '{stream_link}'
                    AND bot_blocked != 1
                    AND TIMESTAMPDIFF(HOUR, action_time, NOW()) >= 1;
                    """)
    else:
        query = (f"""
                    SELECT user_id,stream_link FROM supergra.last_user_actions
                    WHERE stage LIKE '%{stage}%'
                    AND bot = '{bot_name}'
                    AND state = '{geo}'
                    AND bot_blocked != 1
                    AND TIMESTAMPDIFF(HOUR, action_time, NOW()) >= 1;
                    """)
    result = await make_select_query(query)
    return result


@log_exceptions
async def delete_users(user_set: set, bot_name):
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            delete_query = f"DELETE FROM supergra.user_actions WHERE bot = %s AND user_id IN ({','.join(['%s' for _ in user_set])})"
            await cursor.execute(delete_query, (bot_name, *user_set))
            await conn.commit()
            logging.info(f'BANNED USERS DELETED: ({len(user_set)})')


@log_exceptions
async def make_select_query(query):
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            cursor: Cursor
            await cursor.execute(query)
            result = await cursor.fetchall()
            return result


# async def users_by_last_pack(bot_name, geo, last_pack_number, wc_pack_exist, stage):
#     if wc_pack_exist:
#         second_pack_number = last_pack_number
#     else:
#         if last_pack_number == 1:
#             second_pack_number = 0
#         else:
#             second_pack_number = last_pack_number
#     query = (f"""
#             SELECT user_id, stream_link FROM supergra.last_user_actions
#             WHERE stage LIKE '%{stage}%'
#             AND bot = '{bot_name}'
#             AND state = '{geo}'
#             AND bot_blocked != 1
#             AND last_pack_number in ('{last_pack_number}', '{second_pack_number}')
#             AND TIMESTAMPDIFF(HOUR, action_time, NOW()) >= 1;
#             """)
#     result = await make_select_query(query)
#     return result

@log_exceptions
async def users_by_last_pack(bot_name, geo, last_pack_number, wc_in_stage, stage):
    if wc_in_stage:
        last_wc_pack_number_str = 'AND last_wc_pack_number = 0'
    else:
        last_wc_pack_number_str = ''
    query = (f"""
            SELECT user_id, stream_link FROM supergra.last_user_actions
            WHERE stage LIKE '%{stage}%'
            AND bot = '{bot_name}'
            AND state = '{geo}'
            AND bot_blocked != 1
            AND last_pack_number = '{last_pack_number}'
            {last_wc_pack_number_str}
            AND TIMESTAMPDIFF(HOUR, action_time, NOW()) >= 1;
            """)
    result = await make_select_query(query)
    return result


@log_exceptions
async def update_last_pack_num_sql(pack_len, stage, state, bot_name, wc_pack_exist):
    if wc_pack_exist:
        update_wc_pack_exist = ', last_wc_pack_number = 0'
    else:
        update_wc_pack_exist = ''
    query = (f"""
                    UPDATE supergra.last_user_actions 
                        SET last_pack_number = IF(last_pack_number >= {pack_len}, 1, last_pack_number + 1){update_wc_pack_exist}
                        WHERE bot = '{bot_name}' 
                        AND state = '{state}' 
                        AND stage LIKE '%{stage}%'
                        AND TIMESTAMPDIFF(HOUR, action_time, NOW()) >= 1;
                    """)
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            await conn.commit()


@log_exceptions
async def update_wc_users_last_pack(state, stage, bot_name, pack_len, minute_delay_wc, last_wc_pack_number):
    pool: Pool = dp['db_pool']
    query_update = (f"""
                    UPDATE supergra.last_user_actions 
                    SET last_wc_pack_number = IF(last_wc_pack_number >= {pack_len}, 0, last_wc_pack_number + 1),
                    last_wc_pack_time = '{datetime.now()}'
                    WHERE bot = '{bot_name}' 
                    AND state = '{state}' 
                    AND stage LIKE '%{stage}%'
                    AND last_wc_pack_number = '{last_wc_pack_number}'
                    AND TIMESTAMPDIFF(MINUTE, action_time, NOW()) >= {minute_delay_wc};
                    """
                    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query_update)
            await conn.commit()


@log_exceptions
async def update_last_stage(date):
    dict2 = {}
    action_time = datetime.now()
    bot_name = dp['bot_name']
    inserts = []
    for k, v in date.items():
        dict2[v[0]] = dict2.get(v[0], []) + [k]
        try:
            stream = await select_user_action(k.split('_')[0])
            inserts.append((action_time, stream[0][2], k, stream[0][4], v[0], bot_name, "0", stream[0][-1]))
        except:
            logging.warning('Update_eror' + str(k))
    # for key,val in dict2.items():
    #     query = (f"""UPDATE supergra.last_user_actions
    #                  SET stage = '{key}'
    #                  WHERE user_id IN {tuple(val)};""")
    #     if len(val)==1:
    #         query = (f"""UPDATE supergra.last_user_actions
    #                      SET stage = '{key}'
    #                      WHERE user_id IN ({val[0]});""")
    #     pool: Pool = dp['db_pool']
    #     async with pool.acquire() as conn:
    #         async with conn.cursor() as cursor:
    #             await cursor.execute(query)
    #             await conn.commit()
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.executemany('INSERT INTO supergra.user_actions'
                                     '(action_time, username, user_id, state, stage, bot, link_usage, stream_link)'
                                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', inserts)
            await conn.commit()


@log_exceptions
async def mark_blocked_users(user_set):
    pool: Pool = dp['db_pool']
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            text = "'" + ""','"".join(map(str, user_set)) + "'"
            query = (
                f"UPDATE supergra.last_user_actions "
                f"SET bot_blocked = 1 "
                f"WHERE user_id IN ({text});"
            )
            await cursor.execute(query)
            await conn.commit()


@log_exceptions
async def users_count_not_finished(geo, bot_name):
    query = (f"""
                SELECT count(*) 
                FROM supergra.last_user_actions 
                WHERE state = '{geo}'  
                AND bot = '{bot_name}'
                AND stage NOT LIKE '%Player ID | Пройшов%'
                AND bot_blocked = 0;
             """)
    res = await make_select_query(query)
    return res[0][0]


@log_exceptions
async def users_count_by_stage(geo, stage, bot_name):
    query = (f"""
                SELECT count(*) 
                FROM supergra.last_user_actions 
                WHERE state = '{geo}'  
                AND bot = '{bot_name}'
                AND stage LIKE '%{stage}%'
                AND bot_blocked = 0;
             """)
    res = await make_select_query(query)
    return res[0][0]


@log_exceptions
async def users_count_by_stage_and_stream(geo, stage, bot_name, stream_link):
    if stream_link:
        query = (f"""
                    SELECT count(*) 
                    FROM supergra.last_user_actions 
                    WHERE state = '{geo}'  
                    AND bot = '{bot_name}'
                    AND stream_link='{stream_link}'
                    AND stage LIKE '%{stage}%' AND bot_blocked = 0;
                 """)
    else:
        query = (f"""
                    SELECT count(*) 
                    FROM supergra.last_user_actions 
                    WHERE state = '{geo}'  
                    AND bot = '{bot_name}'
                    AND stage LIKE '%{stage}%'
                    AND bot_blocked = 0;
                 """)
    res = await make_select_query(query)
    return res[0][0]


@log_exceptions
async def users_wc_pack(stage, bot_name, geo, pack_number, minute_delay_wc):
    query = (f"""
                SELECT user_id FROM supergra.last_user_actions
                WHERE bot = '{bot_name}' 
                AND state = '{geo}' 
                AND stage LIKE '%{stage}%'
                AND bot_blocked != 1
                AND last_wc_pack_number = '{pack_number}'
                AND TIMESTAMPDIFF(MINUTE, last_wc_pack_time, NOW()) >= {minute_delay_wc};
                """
             )
    result = await make_select_query(query)
    return result


@log_exceptions
async def get_links_stream(id_user, geo):
    bot_name = dp['bot_name']
    query = (f"""SELECT stream
                       FROM supergra.jimpartners 
                       WHERE user_id = '{id_user}_{bot_name}';
                   """)
    result = await make_select_query(query)
    if result:
        user_exists = result[0][0]
        return user_exists
    else:
        return 0


@log_exceptions
async def users_count_by_stream(stream, bot_name):
    query = (f"""SELECT count(*) 
                FROM supergra.last_user_actions 
                WHERE stream_link = '{stream}'
                AND bot = '{bot_name}'
                AND bot_blocked = 0;""")
    result = await make_select_query(query)
    return result[0][0]


@log_exceptions
async def check_if_user_exist(user_id):
    bot_name = dp['bot_name']
    query = (f"""SELECT dep,sum,click_reg,is_registered
                    FROM supergra.jimpartners 
                    WHERE user_id = '{user_id}_{bot_name}';
                """)
    result = await make_select_query(query)
    if len(result) != 0:
        return result[0]
    else:
        return False


@log_exceptions
async def jimpartner_insert(user_id, link, geo,friend=None):
    pool: Pool = dp['db_pool']
    bot_name = dp['bot_name']
    source = 'bonusbot'
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            user_jimpartner_res.user_list.update(
                {f'{user_id}_{bot_name}': {"dep": None, "sum": None, "click_reg": None, "is_registered": None}})
            if friend:
                await cursor.execute('INSERT INTO supergra.jimpartners'
                                     '(user_id,stream, utm_source,utm_term,friend)'
                                     'VALUES (%s, %s, %s, %s, %s)',
                                     (f'{user_id}_{bot_name}', link, source, geo,f'{friend}_{bot_name}'))
            else:
                await cursor.execute('INSERT INTO supergra.jimpartners'
                                     '(user_id,stream, utm_source,utm_term)'
                                     'VALUES (%s, %s, %s, %s)',
                                     (f'{user_id}_{bot_name}', link, source, geo))
            await conn.commit()


# @log_exceptions
# async def manadger_dict(date):
#     for i,val in date.items():
#         if val['is_registered']==1  and val['sum']==0:
#             res = await message_hendl(i)
# @log_exceptions
# async def message_hendl(i):
#     from utils.utils_module import FSMClient
#     state: FSMContext = FSMContext(  # объект бота
#         storage=dp.storage,  # dp - экземпляр диспатчера
#         chat=i, user=i)
#     if await state.storage.get_state(chat=i, user=i) == None:
#         x = await state.storage.set_state(chat=i, user=i,
#                                           state=FSMClient.ID)
#         return True
#     else:
#         return False
# @log_exceptions
# async def pre_server(date):
#     for i,val in date.items():
#         if val[0]=='Error setting for brand 0':
#             res=await message_hendl(i)
#             if res:
#                 try:
#                     await send_to_server([i,*val])
#                 except:
#                     logging.error(f'Not send to server: {i}')
# @log_exceptions
# async def send_to_server(m):
#     bot_name = await bot.get_me()
#     bot_name = bot_name.username
#     if type(m) is list:
#         id = m[0]
#         data = await bot.get_chat(id)
#         datas = {'chat': int(id), 'username': data.mention, 'name': data.first_name,'GEO':m[2]}
#         datas.update({'text': 'Чат почався'})
#         logging.info(f'Try send to server: {id}')
#     else:
#         datas = {'chat': m.from_user.id, 'username': m.from_user.username, 'name': m.from_user.first_name}
#         if m.text:
#             datas.update({'text': m.text})
#         else:
#             if m.caption:
#                 datas.update({'caption': m.caption})
#             else:
#                 datas.update({'caption': None})
#             if m.video:
#                 file = m.video.file_id
#                 event = 'video'
#                 format = 'mp4'
#             elif m.photo:
#                 file = m.photo[1].file_id
#                 event = 'photo'
#                 format = 'png'
#             elif m.voice:
#                 file = m.voice.file_id
#                 event = 'voice'
#                 format = 'ogg'
#             datas.update({'file': file, 'type': event, 'format': format})
#     x = pickle.dumps(datas)
#     requests.post(f'http://138.68.128.22:3999/bot/{bot_name}', x)
@log_exceptions
async def webhook_check(id, geo):
    bot_name = dp['bot_name']
    query = f"SELECT EXISTS (SELECT 1 FROM supergra.users WHERE id_user = '{str(id)}_{bot_name}') AS result;"
    result = await make_select_query(query)
    if result[0][0] == 0:
        query = f"SELECT username FROM supergra.last_user_actions where user_id='{str(id)}_{bot_name}';"
        result = await make_select_query(query)
        await users_insert(id_user=id, used_pass='autodep',
                           username=result[0][0], geo=geo)


@log_exceptions
async def select_user_action(id):
    bot_name = dp['bot_name']
    query = f"SELECT * FROM supergra.user_actions where user_id='{str(id)}_{bot_name}' limit 1;"
    result = await make_select_query(query)
    return result


@log_exceptions
async def get_users_stream(geo, bot_name):
    query = f"select distinct(stream_link) from supergra.last_user_actions where bot='{bot_name}' and state='{geo}';"
    result = await make_select_query(query)
    result = {rec[0]: rec[0] for rec in result}
    return result
