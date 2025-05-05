import asyncio
import logging
import random
import datetime
import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import bot, scheduler
import os
import urllib3
import json
import ast
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
import os.path

from keyboards.admin_kb import create_new_pack_btn, add_welcome_pack
from utils.db_manage import get_users_by_stage

stage_names = ['Всі інші', 'Баланс 0', 'Не достатньо', 'Повний деп']
ADMINS = [397875584, 1311521096, 1311521096, 397875584, 6204985621, 419445433, 1249829378, 6193745344,
          7335647672]

async def get_player_status(uuid):
    url = 'https://gendalf.xyz/api/bot-user-info/' + uuid
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    result = json.loads(response.data.decode('utf-8'))
    return int(result['data']['code']), result['data']['message']


class FSMClient(StatesGroup):
    text = State()
    geo = State()
    user_id = State()
    ID = State()


class FSMAdmin(StatesGroup):
    minute_delay_wc = State()
    change_stream_link = State()
    stream = State()
    blok_stage = State()
    blok_message = State()
    new_text = State()
    text_number = State()
    change_text_geo = State()
    rega_for_new_stream = State()
    new_stream = State()
    new_rega = State()
    stream_edit = State()
    mail_delay = State()
    pack = State()
    del_media_answer = State()
    stage_auto = State()
    auto_mail_geo = State()
    del_voice_or_vnote_answer = State()
    loaded_post_files = State()
    media_answer = State()
    posts_by_data = State()
    job_id = State()
    inline_to_delete = State()
    inline_link = State()
    inline_text = State()
    new_inline_link = State()
    change_button_index = State()
    time_planning = State()
    date_planning = State()

    stage = State()
    post_text = State()
    geo = State()


# rega = ['https://bit.ly/3QUKkgR', 'https://bit.ly/3SQmqWB']  # малий
rega = [
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}',
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}'] # великий
# ls = 'https://bit.ly/47291Op'  # малий
ls = 'https://t.me/Team_Farrux'  # великий
inline_uz = ["✅SIGNALLARNI YOQISH", '✅TAYYOR', '🗣 Otzivlar', "↩️ ORQAGA QAYTISH",
             '✅BOTni aktivlashtirish', "✅DAVOM ETISH", "📝 Qanday qilib ro'yxatdan o'tish kerak?",
             "💰 Hisobni qanday to'ldirish kerak?", '❔ tez-tez beriladigan savollarga javoblar',
             "📩 PLAYER-RAQAMI yuborish",
             "↩️Asosiy sahifaga qaytish"]
inline_br = ['✅ CONECTAR SINAIS', '✅ CONCLUÍDO', '🗣 Feedback ', '↩️ Voltar atrás',
             '✅ Juntar-se ao grupo!', '✅ Continuar', '📝 Como registar?', '💰 Como depositar?',
             '❔ Porquê seguir estes passos? ', '✅ INTRODUZA PLAYER-ID ✅', '↩️ Retornar ao menu principal']

media_file_path = os.path.join(os.path.dirname(__file__), '../media')

async def fill_medias(mode):
    az_id_list = {}
    br_id_list = {}
    if mode == 'main':
        media_file_paths = os.path.join(os.path.dirname(__file__), '../media/main')
    else:
        media_file_paths = media_file_path
    az = os.listdir(os.path.join(media_file_paths, 'AZ'))
    br = os.listdir(os.path.join(media_file_paths, 'BR'))
    az.sort()
    br.sort()
    for i in az:
        az_id_list.update({str(i):[]})
        stream=os.listdir(media_file_paths+"/AZ/"+i)
        stream.sort()
        for media in  stream:
            media_file = types.InputFile(os.path.join(media_file_paths, f'AZ/{i}/') + media)
            file_type = os.path.splitext(media)
            if file_type[1] in '.mp4':
                if 'note' in file_type[0]:
                    message = await bot.send_video_note(chat_id='419445433', video_note=media_file)
                    az_id_list[str(i)].append(message.video_note.file_id)
                else:
                    message = await bot.send_video(chat_id='419445433', video=media_file)
                    az_id_list[str(i)].append(message.video.file_id)
            elif file_type[1] in ['.jpg', '.png']:
                message = await bot.send_photo(chat_id='419445433', photo=media_file)
                az_id_list[str(i)].append(message.photo[0].file_id)
            elif file_type[1] in ['.ogg']:
                message = await bot.send_voice(chat_id='419445433', voice=media_file)
                az_id_list[str(i)].append(message.voice.file_id)
            elif file_type[1] in ['.apk']:
                message = await bot.send_document(chat_id='419445433', document=media_file)
                az_id_list[str(i)].append(message.document.file_id)
    for i in br:
        br_id_list.update({str(i):[]})
        stream=os.listdir(media_file_paths+"/BR/"+i)
        stream.sort()
        for media in  stream:
            media_file = types.InputFile(os.path.join(media_file_paths, f'BR/{i}/') + media)
            file_type = os.path.splitext(media)
            if file_type[1] in '.mp4':
                message = await bot.send_video(chat_id='419445433', video=media_file)
                br_id_list[str(i)].append(message.video.file_id)
            elif file_type[1] in ['.jpg', '.png']:
                message = await bot.send_photo(chat_id='419445433', photo=media_file)
                br_id_list[str(i)].append(message.photo[0].file_id)
            elif file_type[1] in ['.ogg']:
                message = await bot.send_voice(chat_id='419445433', voice=media_file)
                br_id_list[str(i)].append(message.voice.file_id)
            elif file_type[1] in ['.apk']:
                message = await bot.send_document(chat_id='419445433', document=media_file)
                br_id_list[str(i)].append(message.document.file_id)

    with open(os.path.join(media_file_path, f'{mode}_id.json'), 'w+', encoding='utf-8') as file:
        file.seek(0)  # перейти на початок файлу
        file_data = {
            'AZ': az_id_list,
            'BR': br_id_list
        }
        file.seek(0)
        json.dump(file_data, file, indent=4)


async def get_main_part(geo, mode):
    if os.path.exists(os.path.join(media_file_path, f'{mode}_id.json')):
        with open(os.path.join(media_file_path, f'{mode}_id.json'), 'r', encoding='utf-8') as file:
            file_data = json.load(file)
            return file_data

    else:
        await fill_medias(mode=mode)
        with open(os.path.join(media_file_path, f'{mode}_id.json'), 'r', encoding='utf-8') as file:
            file_data = json.load(file)
            return file_data

async def get_Structure(geo):
    with open(os.path.join(media_file_path, f'structure.json'), 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        geo_data = file_data[geo]
    return geo_data

async def write_file_Structure(geo,stream,data):
    for i in ['structure','texts','main_id','button']:
        with open(os.path.join(media_file_path, f'{i}.json'), 'r', encoding='utf-8') as file:
            file_data = json.load(file)
        x=file_data.copy()
        x[geo].update({stream:data[i]})
        with open(os.path.join(media_file_path, f'{i}.json'),'w', encoding='utf-8') as f:
            json.dump(x,f)
        if i=='main_id':
            await write_media(geo,stream,data[i])

async def write_media(geo,stream,media_list):
    media_file_paths = os.path.join(os.path.dirname(__file__), '../media/main')+f'/{geo}/{stream}/'
    try:
        os.makedirs(media_file_paths)
    except FileExistsError:
        # directory already exists
        pass
    for i in range(len(media_list)):
        file = await bot.get_file(media_list[i])
        logging.info(str(media_list[i]))
        logging.info(str(file))
        type=file.file_path.rsplit('.')[1]
        logging.info(str(file))
        if not os.path.isfile(media_file_paths+f'{i}.{type}'):
            x = await file.download(media_file_paths+f'{i}.{type}')

async def text_and_inline_by_geo(geo,user_id=0000000 ,link='default',stage='check_dep'):
    rega = [
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}',
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}']
    bot_info = await bot.get_me()
    bot_name = bot_info.username
    if geo == "AZ":
        rega = rega[0].format(STREAM=link, USERID=f'{user_id}_{bot_name}', GEO=geo)
    else:
        rega = rega[1].format(STREAM=link, USERID=f'{user_id}_{bot_name}', GEO=geo)
    geo_data =await get_Structure(geo)
    if link in geo_data.keys():
        bloc_data = geo_data[link]
    else:
        link = 'default'
        bloc_data = geo_data['default']
    if stage in bloc_data.keys():
        structure = bloc_data[stage]
    else:
        stage='check_dep'
        structure = bloc_data['check_dep']
    file_id = await get_main_part(geo, mode='main')
    file_id = file_id[geo][link]
    file_id.append(None)
    with open(os.path.join(media_file_path, f'texts.json'), 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        texts = file_data[geo][link]
        texts = [text.format(rega=rega) for text in texts if text]
        texts.append(None)
    with open(os.path.join(media_file_path, f'button.json'), 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        buttons = file_data[geo][link]
        for i in range(len(buttons)):
            if buttons[i]:
                buttons[i] = str(buttons[i]).replace('google.com', rega)
                buttons[i]=ast.literal_eval(buttons[i])
        buttons.append(None)
    return texts, buttons,file_id,structure


def add_random_media(media_files, data, cat_name):
    random_photos_number = data.get('random_photos_number')
    random_videos_number = data.get('random_videos_number')

    if random_photos_number:
        r_photos = get_random_photos(count=int(random_photos_number), cat_name=cat_name)
        for rand_photo in r_photos:
            media_files.attach_photo(rand_photo)

    if random_videos_number:
        r_videos = get_random_videos(count=int(random_videos_number), cat_name=cat_name)
        for rand_video in r_videos:
            media_files.attach_video(rand_video)


def get_random_photos(count, cat_name) -> list:
    with open('data.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        res = []
        photos_id = file_data['catalogs'][cat_name]['photos']
        random.shuffle(photos_id)
        for i in range(count):
            res.append(photos_id[i])
        return res


def get_random_videos(count, cat_name) -> list:
    with open('data.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        res = []
        videos_id = file_data['catalogs'][cat_name]['videos']

        random.shuffle(videos_id)
        for i in range(count):
            res.append(videos_id[i])
        return res


def set_caption(media, text, entities=None):
    for m in range(len(media.media)):
        if m > 0:
            if 'caption' in media.media[m]:
                media.media[m].caption = None
        else:
            media.media[m].caption = text
            media.media[m].caption_entities = entities


async def show_message(message, state: FSMContext, send_to_channel=False):
    data = await state.get_data()
    job_id = data.get('job_id')
    auto_geo = data.get('auto_mail_geo')
    if auto_geo:
        stage = data.get('stage')
        pack = data.get('pack')
        is_wc_pack = True if pack and 'wc' in pack else False
        if is_wc_pack:
            job = scheduler.get_job(f'{auto_geo}_wc')
        else:
            job = scheduler.get_job(auto_geo)

        if job:
            job_data = job.kwargs.get('data')
            stage_data = job_data.get(stage)
            data = stage_data['packs'][pack]
        else:
            return
    elif job_id:
        job = scheduler.get_job(job_id)
        data = job.kwargs.get('data')

    post_media_files = data.get('loaded_post_files')
    kb_inline: InlineKeyboardMarkup = data.get('inline_kb')
    randomed_text_kb = InlineKeyboardMarkup()
    if kb_inline:
        await kb_random_choice(kb_inline, randomed_text_kb)

    post_voice = data.get('voice')
    video_note = data.get('video_note')
    random_v_notes_id = data.get('random_v_notes_id')
    chat_id = message.from_user.id
    text = data.get('post_text')
    entities = data.get('entities')
    if send_to_channel:
        chat_id = data.get('channel_id')
        if isinstance(text, list):
            text = random.choice(text)
    if isinstance(text, list) and not send_to_channel:
        text = '"Текст буде обраний рандомно."'
    if job_id:
        if scheduler.get_job(job_id).name == 'send_message_cron':
            text = (f"{text}\n"
                    "————————\n"
                    f"🌀")
        elif scheduler.get_job(job_id).name == 'send_message_time':
            text = (f"{text}\n"
                    "————————\n"
                    f"🗓")
    try:
        if post_media_files:
            if len(post_media_files.media) == 1:
                m = post_media_files.media[0]
                if m.type == 'video':
                    await bot.send_video(chat_id=chat_id, video=m.media, caption=text, reply_markup=randomed_text_kb,
                                         caption_entities=entities, parse_mode='html')
                elif m.type == 'photo':
                    await bot.send_photo(chat_id=chat_id, photo=m.media, caption=text, reply_markup=randomed_text_kb,
                                         caption_entities=entities, parse_mode='html')
                elif m.type == 'document':
                    await bot.send_document(chat_id=chat_id, document=m.media, caption=text,
                                            reply_markup=randomed_text_kb, caption_entities=entities, parse_mode='html')
            else:
                set_caption(text=text, media=post_media_files, entities=entities),
                await bot.send_media_group(chat_id=chat_id, media=post_media_files)
        elif post_voice:
            await bot.send_voice(chat_id=chat_id, voice=post_voice, caption=text, reply_markup=randomed_text_kb,
                                 caption_entities=entities, parse_mode='html')
        elif video_note:
            await bot.send_video_note(chat_id=chat_id, video_note=video_note, reply_markup=randomed_text_kb)
        elif random_v_notes_id:
            await bot.send_video_note(chat_id=chat_id, video_note=random.choice(random_v_notes_id),
                                      reply_markup=randomed_text_kb)
        elif text:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=randomed_text_kb, entities=entities,
                                   parse_mode='html')
    except Exception as er:
        await bot.send_message(chat_id=chat_id, text=f"{er}\n{text if text else ''}", reply_markup=randomed_text_kb)


def add_mails_to_kb(jobs, edit_kb):
    for j in jobs:
        date_p: datetime = j.next_run_time
        job_data = j.kwargs['data']

        if not job_data.get('post_text'):
            job_post_text = ''
        elif not job_data.get('post_text') and job_data.get('random_v_notes_id'):
            job_post_text = '- кругляш'
        else:
            job_post_text = f'- "{job_data.get("post_text")}"'
        trigger_name = str(j.trigger).split('[')[0]
        if trigger_name == 'date':
            text = f"{job_data.get('stage')} - {job_data.get('geo')} - {date_p.date()} о {date_p.strftime('%H:%M')} {job_post_text}"
        elif trigger_name in ('interval', 'cron'):
            if trigger_name == 'interval':
                skip_days = job_data.get('skip_days_loop') if job_data.get(
                    'skip_days_loop') is not None else job_data.get('skip_days_loop_vnotes')
                start_loop_date = job_data.get('start_loop_date').strftime("%d.%m.%Y")
                skip_days = int(skip_days)
                if skip_days == 0:
                    text = f"З {start_loop_date} - кожного дня о {date_p.strftime('%H:%M')} {job_post_text}"
                elif skip_days == 1:
                    text = f"Початок {start_loop_date} - пропуск 1 день о {date_p.strftime('%H:%M')} {job_post_text}"
                else:
                    text = f"Початок {start_loop_date} - пропуск {skip_days} дні(-в) о {date_p.strftime('%H:%M')} {job_post_text}"
            else:
                text = f"Кожного дня о {date_p.strftime('%H:%M')} {job_post_text}"

        else:
            text = 'Без імені'

        edit_kb.add(InlineKeyboardButton(text=text,
                                         callback_data=j.id))


def pressed_back_button(message):
    if isinstance(message, types.CallbackQuery):
        call: types.CallbackQuery = message
        if call.data == 'back':
            return True
        else:
            return False


async def restrict_media(messages, state, data, post_formatting_kb):
    # якщо надсилаємо (відео фото документ) при цьому войс у даних - заборонити
    if messages[0].content_type in ('video', 'photo', 'document') and 'voice' in data:
        await messages[0].answer(text='❌ Голосове повідомлення не можна публікувати у групі з іншими медіа',
                                 reply_markup=post_formatting_kb)
        await state.reset_state(with_data=False)
        return True
    if messages[0].content_type in ('audio', 'voice'):
        if 'loaded_post_files' in data:
            await messages[0].answer(text='❌ Голосове повідомлення не можна публікувати у групі з іншими медіа',
                                     reply_markup=post_formatting_kb)
            await state.reset_state(with_data=False)
            return True

        if len(messages) > 1:
            await messages[0].answer(text='❌ У пості може бути тільки 1 голосове.',
                                     reply_markup=post_formatting_kb)
            await state.reset_state(with_data=False)
            return True
    if data.get('voice'):
        await messages[0].answer(text='❌ У пості може бути тільки 1 голосове.',
                                 reply_markup=post_formatting_kb)
        await state.reset_state(with_data=False)
        return True


async def send_voice_from_audio(message: types.Message, bot):
    file_info = await bot.get_file(message.audio.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    return await message.answer_voice(downloaded_file)


async def alert_vnote_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('post_text') and data.get('video_note'):
        await message.answer(text='⚠️ Текст з посту видалено.\n'
                                  '<i>Текст неможоливо додати до відеоповідомлення.</i>', parse_mode='html')


async def send_mail(post_media_files: types.MediaGroup, post_text, bot, post_voice,
                    post_video_note, user_id,inline_kb=None, data=None, stage=None, pack=None, entities=None):
    try:
        id_user=user_id.split("_")[0]
        if post_media_files:
            set_caption(text=post_text, media=post_media_files, entities=entities),
            if len(post_media_files.media) == 1:
                if post_media_files.media[0]['type'] == 'photo':
                    await bot.send_photo(chat_id=id_user, photo=post_media_files.media[0]['media'], caption=post_text,
                                         reply_markup=inline_kb, caption_entities=entities, parse_mode='html')
                elif post_media_files.media[0]['type'] == 'video':
                    await bot.send_video(chat_id=id_user, video=post_media_files.media[0]['media'], caption=post_text,
                                         reply_markup=inline_kb, caption_entities=entities, parse_mode='html')
                elif post_media_files.media[0]['type'] == 'document':
                    await post_media_files.bot.send_document(chat_id=id_user,
                                                             document=post_media_files.media[0]['media'],
                                                             caption=post_text,
                                                             reply_markup=inline_kb, caption_entities=entities,
                                                             parse_mode='html')
            else:
                await bot.send_media_group(chat_id=id_user, media=post_media_files)
        elif post_voice:
            await bot.send_voice(chat_id=id_user, voice=post_voice, caption=post_text, reply_markup=inline_kb,
                                 caption_entities=entities, parse_mode='html')
        elif post_video_note:
            await bot.send_video_note(chat_id=id_user, video_note=post_video_note, reply_markup=inline_kb)
        else:
            await bot.send_message(chat_id=id_user, text=post_text, reply_markup=inline_kb, entities=entities,
                                   parse_mode='html')

        return True
    except Exception as err:
        if type(err) is aiogram.utils.exceptions.BotBlocked:
            return user_id


async def send_messages(data):
    sent_count = 0
    tasks = []
    entities = data.get('entities')
    geo = data.get('geo')
    stage = data.get('stage')
    stream_link=data.get('stream')
    media_files = data.get('loaded_post_files')
    voice = data.get('voice')
    video_note = data.get('video_note')
    kb_inline = data.get('inline_kb')
    bot_info = await bot.get_me()
    bot_name = bot_info.username
    # bot_name = 'Aviator Hacker BOT'
    users = await get_users_by_stage(stage=stage, bot_name=bot_name, geo=geo,stream_link=stream_link)

    # if kb_inline:
    #     await kb_random_choice(kb_inline, randomed_text_kb)

    user_ids = []
    for user_id in users:
        user_ids.append(user_id[0])

    with open(os.path.join(os.path.dirname(__file__), '../logs.log'), 'w'):  # clear logs
        pass
    print(users)
    for user in users:
        post_text = data.get('post_text')
        # for user in [['397875584', '397875584']]:
        user_id = user[0]
        stream_link = user[1]
        if stream_link and post_text:
            if geo == "AZ":
                rega_link = rega[0].format(STREAM='Mailing2', USERID=user_id, GEO=geo)
            else:
                rega_link = rega[1].format(STREAM='Mailing2', USERID=user_id, GEO=geo)
            post_text: str = post_text.format(rega=rega_link)
        randomed_text_kb = InlineKeyboardMarkup()
        if kb_inline:
            for buttons in kb_inline.inline_keyboard:
                for button in buttons:
                    if 'google.com' in button.url:
                        randomed_text_kb.add(
                            InlineKeyboardButton(text=button.text[0], url=rega_link))
                    else:
                        randomed_text_kb.add(
                            InlineKeyboardButton(text=button.text[0], url=button.url))
        task = asyncio.create_task(
            send_mail(post_media_files=media_files, post_text=post_text, bot=bot, post_voice=voice,
                      post_video_note=video_note,
                      inline_kb=randomed_text_kb, user_id=user_id, data=data, entities=entities))
        tasks.append(task)
        if len(list(tasks)) >= 30 or user == users[-1]:
            results = await asyncio.gather(*tasks)
            sent_count += results.count(True)  # додаємо цифру скільки розіслалось по даній категорії
            results = set(results)
            results.discard(None)
            results.discard(True)
            tasks.clear()
            await asyncio.sleep(1)

    for admin_id in ADMINS:
        try:
            await bot.send_message(chat_id=admin_id, text=f'Розсилка закінчилась.\n\n'
                                                          f'Всього користувачів {len(users)}\n'
                                                          f'Розіслано: {sent_count}\n')
        except:
            pass


async def add_data_to_job(fsm_data, auto_job, geo, data_type, media_data):
    pack = fsm_data.get('pack')
    stage = fsm_data.get('stage')
    is_wc_pack = True if pack and pack.split('_')[-1] == 'wc' else False
    if auto_job:
        if is_wc_pack:
            job_data = auto_job.kwargs.get('data', {})
            job_id = f"{geo}_{stage}_wc"
        else:
            job_data = auto_job.kwargs.get('data', {})
            stage_data = job_data.get(stage, {})
            stage_data['packs'][pack][data_type] = media_data
            job_data[stage] = stage_data
            job_id = geo
        scheduler.modify_job(job_id=job_id, kwargs={'data': job_data})
    else:
        from handlers.mailing import send_messages_auto
        from handlers.mailing import interval_time
        job_id = geo
        if is_wc_pack:
            job_id = f"{geo}_{stage}_wc"
        scheduler.add_job(send_messages_auto, trigger='interval', seconds=interval_time, id=job_id, name=job_id,
                          kwargs={'data': fsm_data})
        scheduler.pause_job(job_id=job_id)


async def add_packs_to_kb(kb: InlineKeyboardMarkup, packs, wc_packs):
    if wc_packs:
        for pack in wc_packs:
            wc_pack_btn = InlineKeyboardButton(text=f"👋🏻 Вітальний пак {pack.split('_')[-1]}", callback_data=pack)
            kb.add(wc_pack_btn)
    if packs:
        for pack in  sorted(packs,key=lambda x:x.split('_')[-1][0]):
            pack: str
            kb.add(InlineKeyboardButton(text=f"Пак {pack.split('_')[-1]}", callback_data=pack))
    kb.add(create_new_pack_btn, add_welcome_pack,
           InlineKeyboardButton(text='« Назад', callback_data='mail_settings'))


async def time_for_mailing(geo):
    from_time_uz = datetime.datetime.now().replace(hour=5, minute=0, second=0)
    from_time_br = datetime.datetime.now().replace(hour=10, minute=0, second=0)
    now_time = datetime.datetime.now()
    if (geo == 'BR' and from_time_br < now_time < from_time_br + datetime.timedelta(hours=12)) or (
            geo == 'AZ' and from_time_uz < now_time < from_time_uz + datetime.timedelta(hours=12)):
        return True
    else:
        return False


async def kb_random_choice(kb_inline, randomed_text_kb):
    for buttons in kb_inline.inline_keyboard:
        for button in buttons:
            randomed_text_kb.add(
                InlineKeyboardButton(text=random.choice(button.text), url=button.url))


async def resume_pause_wc_job(geo, action: str):
    for stage in stage_names:
        job_id = f"{geo}_{stage}_wc"
        try:
            if action == 'resume':
                scheduler.resume_job(job_id)
                logging.info(f'Job {job_id} RESUMED {scheduler.get_job(job_id)}')

            elif action == 'pause':
                scheduler.pause_job(job_id)
                logging.info(f'Job {job_id} PAUSED {scheduler.get_job(job_id)}')
        except:
            pass


async def change_text_json(geo, text_index, new_text):
    file_path = os.path.join(media_file_path, 'texts.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data[geo][text_index] = new_text

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def create_streams_kb(stream_dict: dict):
    kb = InlineKeyboardMarkup()
    for stream, rega_link in stream_dict.items():
        kb.add(InlineKeyboardButton(text=f"{stream} - {rega_link}", callback_data=stream))
    return kb


async def update_page_num(data, operation, state):
    page_num = data.get('page_num')
    if page_num and operation == '+':
        await state.update_data(page_num=page_num + 1)
    elif page_num and operation == '-' and page_num > 1:
        await state.update_data(page_num=page_num - 1)
    elif not page_num:
        await state.update_data(page_num=1)


async def paginate(kb: types.InlineKeyboardMarkup):
    back_btn = InlineKeyboardButton(text='⬅️', callback_data='-')
    page_btn = InlineKeyboardButton(text='1', callback_data='1')
    next_btn = InlineKeyboardButton(text='➡️', callback_data='+')
    kb.add(back_btn, page_btn, next_btn)


async def create_catalogs_kb(dict_stream, page=None):
    catalogs_kb = InlineKeyboardMarkup()
    catalog_by_page = list(dict_stream)[(page - 1) * 3:3 * page]
    for cat_name in catalog_by_page:
        catalogs_kb.add(InlineKeyboardButton(text=cat_name, callback_data=cat_name))
    return catalogs_kb


async def catalog_paginate(state, dict_stream):
    data = await state.get_data()
    if not data.get('page_num'):
        await state.update_data(page_num=1)
    data = await state.get_data()
    page_num = data.get('page_num')
    catalogs_kb = await create_catalogs_kb(dict_stream, page=page_num)
    await paginate(catalogs_kb)
    catalogs_kb.inline_keyboard[-1][-2].text = page_num
    return catalogs_kb


async def wc_job_in_stage(geo, stage):
    job = scheduler.get_job(f'{geo}_wc')
    if job:
        job_data = job.kwargs.get('data')
        if stage in job_data:
            return True
    return False

async def for_rega_mail(date,number):
    users=date
    sent_count = 0
    job_az = scheduler.get_job(f'AZ_wc')
    tasks=[]
    users_2={}
    for key,val in users.items():
        if  await time_for_mailing(val[1]):
            if val[1] in ['AZ',None] and job_az:
                try:
                    if pack:=job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}']:
                        if job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}'].get('inline_kb'):
                            if job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}']['inline_kb'] and len(job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}']['inline_kb'].inline_keyboard)!=0:
                                kb = job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}']['inline_kb']
                                kb.inline_keyboard[0][0].url =rega[0].format(STREAM='mailing'+f'_{stage_names.index(val[0])}_wp', USERID=key, GEO=val[1])
                                kb_inline: InlineKeyboardMarkup = kb
                                randomed_text_kb = InlineKeyboardMarkup()
                                if kb_inline:
                                    await kb_random_choice(kb_inline, randomed_text_kb)
                                pack['inline_kb']=randomed_text_kb
                        pack['post_text']=job_az.kwargs['data'][val[0]]['packs'][f'wc_pack_{number}']['post_text'].format(rega=rega[0].format(STREAM='mailing'+f'_{stage_names.index(val[0])}_wp', USERID=key, GEO=val[1]))
                        if 'minute_delay_wc' in pack.keys():
                            pack.pop('minute_delay_wc')
                        pack.update({'post_media_files':None,'post_voice':None,'post_video_note':None})
                        task = asyncio.create_task(send_mail( bot=bot, user_id=key,**pack))
                        tasks.append(task)
                        users_2.update({key: val})
                except:
                    continue
            if len(list(tasks)) >= 30 or key == list(users.keys())[-1]:
                results = await asyncio.gather(*tasks)
                sent_count += results.count(True)  # додаємо цифру скільки розіслалось по даній категорії
                results = set(results)
                results.discard(None)
                results.discard(True)
                tasks.clear()
                await asyncio.sleep(1)
    if len(users_2)>0:
        await asyncio.sleep(20)
        await for_rega_mail(users_2,str(int(number)+1))
