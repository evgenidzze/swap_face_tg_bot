import asyncio
import datetime
import logging
from copy import deepcopy
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_timepicker.panel import FullTimePicker

from create_bot import bot, scheduler
from utils.db_manage import update_last_pack_num_sql, mark_blocked_users, users_count_not_finished, \
    users_wc_pack, update_wc_users_last_pack,  users_by_last_pack
from keyboards.admin_kb import user_category_kb, manage_panel_kb, stop_mail_btn, change_delay_btn
from keyboards.client_kb import geo_kb
from utils.utils_module import send_mail, FSMAdmin, time_for_mailing, kb_random_choice, stage_names, ADMINS, wc_job_in_stage,rega

interval_time = 7200
interval_time_wc_pack = 180
main_mail_running = {'AZ': False, 'BR': False}
welcome_mail_running = {'AZ': False, 'BR': False}


async def auto_mailing_geo(message: types.CallbackQuery, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.reset_state()
        await FSMAdmin.auto_mail_geo.set()
        text = 'Оберіть гео авто-розсилки або налаштуйте затримку:'
        for geo in ("AZ", "BR"):
            job = scheduler.get_job(geo)
            if job:
                text += f'\n\n⏱ Затримка між розсилками: {str(job.trigger).split("[")[1][:-1]} (год:хв:сек)\n'
                if job.next_run_time:
                    now = datetime.datetime.now()
                    local_now = now.astimezone()
                    text += f'🔜 Наступна розсилка: {job.next_run_time.strftime("%H:%M")} по {local_now.tzinfo.tzname(local_now)}'
        kb = deepcopy(geo_kb)
        kb.add(change_delay_btn)
        if isinstance(message, types.Message):
            await message.answer(text, reply_markup=kb)
        else:
            try:
                await message.message.edit_text(text, reply_markup=kb)
            except:
                await message.message.answer(text, reply_markup=kb)


async def change_delay_auto_mail(message: types.CallbackQuery):
    await FSMAdmin.mail_delay.set()
    await message.message.edit_text(
        "Будь ласка оберіть час: ",
        reply_markup=await FullTimePicker().start_picker()
    )


async def load_time_delay(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    r = await FullTimePicker().process_selection(callback_query, callback_data)
    if r.selected:
        hours = r.time.hour
        minutes = r.time.minute
        seconds = r.time.second
        for geo in ("AZ", 'BR'):
            job = scheduler.get_job(geo)
            if job:
                job_data = job.kwargs.get('data')
                job.remove()
                scheduler.add_job(send_messages_auto, trigger='interval', hours=hours, minutes=minutes, seconds=seconds,
                                  id=geo, name=geo,
                                  kwargs={'data': job_data})
                job.pause()
        kb = deepcopy(geo_kb)
        kb.add(change_delay_btn)
        await callback_query.message.edit_text(text='Час затримки змінено, оберіть гео:', reply_markup=kb)
        await FSMAdmin.auto_mail_geo.set()
    elif r.status.name == 'CANCELED':
        await auto_mailing_geo(callback_query, state)
        return


async def start_stop_settings_mail(message: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    bot_info = await bot.get_me()
    bot_name = bot_info.first_name
    # bot_name = 'aviatr_hackers_bot'
    if message.data in ("AZ", "BR"):
        await state.update_data(auto_mail_geo=message.data)
        auto_mail_geo = message.data
    else:
        fsm_data = await state.get_data()
        auto_mail_geo = fsm_data.get('auto_mail_geo')
    user_count = await users_count_not_finished(auto_mail_geo, bot_name=bot_name)

    text = f'Регіон: {auto_mail_geo}\n' \
           'Статус: Неактивна 🔴\n' \
           f'К-сть користувачів, які не пройшли: {user_count}\n' \
           f'Приблизний час розсилки ≈ {int(user_count) // 1000}хв\n\n' \
           'Панель управління авто-розсилки:'
    kb = deepcopy(manage_panel_kb)
    uz_job = scheduler.get_job('AZ')
    br_job = scheduler.get_job('BR')
    all_jobs_by_geo = [job for job in scheduler.get_jobs() if 'wc' in job.id]
    if ((auto_mail_geo == 'AZ' and uz_job and uz_job.next_run_time)
            or (auto_mail_geo == 'BR' and br_job and br_job.next_run_time)
            ):
        text = f'Регіон: {auto_mail_geo}\n' \
               'Статус: Активна 🟢\n' \
               f'К-сть користувачів, які не пройшли: {user_count}\n' \
               f'Приблизний час розсилки ≈ {int(user_count) // 1000}хв\n\n' \
               'Панель управління авто-розсилки:'
        kb.inline_keyboard[0][0] = stop_mail_btn
    await message.message.answer(text, reply_markup=kb)


async def start_auto_mail(message: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    fsm_data = await state.get_data()
    geo = fsm_data.get('auto_mail_geo')
    # job = scheduler.get_job(job_id=geo)
    all_jobs_by_geo = [job for job in scheduler.get_jobs() if job.id == geo or f'{geo}_' in job.id]
    if message.data == 'start_mail':
        if any(job for job in all_jobs_by_geo):
            for job in all_jobs_by_geo:
                job.resume()
                logging.info(f'Job {job.id} RESUMED {job}')
        else:
            scheduler.add_job(send_messages_auto, trigger='interval', seconds=interval_time, id=geo, name=geo,
                              kwargs={'data': fsm_data})
    elif message.data == 'stop_mail':
        if any(job for job in all_jobs_by_geo):
            for job in all_jobs_by_geo:
                job.pause()
                logging.info(f'Job {job.id} PAUSED {job}')
    message.data = 'no_job'
    await start_stop_settings_mail(message, state)


async def pick_stage(message: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    geo = fsm_data.get('auto_mail_geo')
    await message.message.edit_text(text=f'Регіон: {geo}\n\n'
                                         f'Оберіть етап:', reply_markup=user_category_kb)
    await FSMAdmin.stage.set()


async def send_messages_auto(data):
    geo = data.get('auto_mail_geo')
    while welcome_mail_running['AZ'] or welcome_mail_running['BR']:
        await asyncio.sleep(30)
    else:
        global main_mail_running
        main_mail_running[geo] = True
        bot_info = await bot.get_me()
        bot_name = bot_info.username
        # bot_name = 'aviatr_hackers_bot'
        # if True:
        if await time_for_mailing(geo):
            sent_count_stges = {'Всі інші':0, 'Баланс 0':0, 'Не достатньо':0, 'Повний деп':0}
            job = scheduler.get_job(geo)
            job_data = job.kwargs.get('data')
            tasks = []
            blocked_users = set()
            for stage in stage_names:
                wc_in_stage = await wc_job_in_stage(geo, stage)
                stage_data = job_data.get(stage)
                print(stage)
                print(stage_data)
                if stage_data:
                    packs = stage_data.get('packs')
                    print(packs)
                    for pack in packs:
                        pack_data = stage_data['packs'][pack]
                        pack_number = int(pack.split('_')[-1])
                        users = await users_by_last_pack(bot_name=bot_name, geo=geo,
                                                         last_pack_number=pack_number,
                                                         wc_in_stage=bool(wc_in_stage), stage=stage)
                        for user in users:
                            user_id = user[0]
                            stream_link = user[1]
                            post_text = pack_data.get('post_text')
                            entities = pack_data.get('entities')
                            if stream_link and post_text:
                                if geo == "AZ":
                                    rega_link = rega[0].format(STREAM='mailing'+f'_{stage_names.index(stage)}'+f'_{pack_number}', USERID=user_id, GEO=geo)
                                else:
                                    rega_link = rega[1].format(STREAM='mailing'+f'_{stage_names.index(stage)}'+f'_{pack_number}', USERID=user_id, GEO=geo)
                                post_text: str = post_text.format(rega=rega_link)
                            media_files = pack_data.get('loaded_post_files')
                            voice = pack_data.get('voice')
                            video_note = pack_data.get('video_note')
                            kb_inline = pack_data.get('inline_kb')
                            randomed_text_kb = InlineKeyboardMarkup()
                            if kb_inline:
                                for buttons in kb_inline.inline_keyboard:
                                    for button in buttons:
                                        if 'google.com' in button.url:
                                            randomed_text_kb.add(
                                                InlineKeyboardButton(text=button.text[0], url=rega[0].format(STREAM='mailing'+f'_{stage_names.index(stage)}'+f'_{pack_number}', USERID=user_id, GEO=geo)))
                                        else:
                                            randomed_text_kb.add(
                                                InlineKeyboardButton(text=button.text[0], url=button.url))
                            task = asyncio.create_task(
                                send_mail(post_media_files=media_files, post_text=post_text, bot=bot,
                                          post_voice=voice,
                                          post_video_note=video_note,
                                          inline_kb=randomed_text_kb, user_id=user_id, stage=stage, pack=pack,
                                          data=pack_data, entities=entities))
                            tasks.append(task)

                            if len(list(tasks)) >= 30 or user == users[-1]:
                                results = await asyncio.gather(*tasks)
                                sent_count_stges[stage] += results.count(
                                    True)  # додаємо цифру скільки розіслалось по даній категорії
                                results = set(results)
                                results.discard(None)
                                results.discard(True)
                                blocked_users.update(results)
                                tasks.clear()
                                await asyncio.sleep(1)
                        if blocked_users:
                            await mark_blocked_users(user_set=blocked_users)
                    await update_last_pack_num_sql(state=geo, stage=stage, pack_len=len(packs), bot_name=bot_name,
                                                   wc_pack_exist=bool(wc_job_in_stage))
            # for chat_id in ('397875584',):
            for chat_id in ADMINS:
                try:
                    await bot.send_message(chat_id=chat_id, text='Авто-розсилка відпрацювала:\n\n'
                                                             f'Розіслано: {sent_count_stges}\n')
                except:
                    continue
        main_mail_running[geo] = False


async def send_wc_message(data):
    geo = data.get('auto_mail_geo')
    while main_mail_running['AZ'] or main_mail_running['BR']:
        await asyncio.sleep(30)
    else:
        global welcome_mail_running
        welcome_mail_running[geo] = True
        bot_info = await bot.get_me()
        bot_name = bot_info.first_name
        # bot_name = 'aviatr_hackers_bot'
        if await time_for_mailing(geo):
            # if True:
            sent_count_stges = {'Всі інші':0, 'Баланс 0':0, 'Не достатньо':0, 'Повний деп':0}
            job = scheduler.get_job(f'{geo}_wc')
            job_data = job.kwargs.get('data')
            tasks = []
            for stage in stage_names:
                stage_data = job_data.get(stage)
                if stage_data:
                    packs = stage_data.get('packs')
                    for pack in packs:
                        pack_number = int(pack.split('_')[-1])
                        pack_data = stage_data['packs'][pack]
                        minute_delay_wc = pack_data.get('minute_delay_wc')
                        users = await users_wc_pack(stage, bot_name, geo, pack_number, minute_delay_wc)
                        for user in users:
                            print( user[0])
                            user_id = user[0]
                            post_text = pack_data.get('post_text')
                            entities = pack_data.get('entities')
                            media_files = pack_data.get('loaded_post_files')
                            voice = pack_data.get('voice')
                            video_note = pack_data.get('video_note')
                            kb_inline = pack_data.get('inline_kb')
                            randomed_text_kb = InlineKeyboardMarkup()
                            if kb_inline:
                                await kb_random_choice(kb_inline, randomed_text_kb)
                            # task = asyncio.create_task(
                            #     send_mail(post_media_files=media_files, post_text=post_text, bot=bot,
                            #               post_voice=voice,
                            #               post_video_note=video_note,
                            #               inline_kb=randomed_text_kb, user_id=user_id, stage=stage,
                            #               pack=f'{geo}_{stage}_wc',
                            #               data=pack_data, entities=entities))
                            # tasks.append(task)
                            if len(list(tasks)) >= 30 or user == users[-1]:
                                results = await asyncio.gather(*tasks)
                                sent_count_stges[stage] += results.count(
                                    True)
                                results = set(results)
                                results.discard(None)
                                results.discard(True)
                                tasks.clear()
                                await asyncio.sleep(1)
                        await update_wc_users_last_pack(state=geo, stage=stage, bot_name=bot_name, pack_len=len(packs),
                                                        minute_delay_wc=minute_delay_wc, last_wc_pack_number=pack_number)
            # for chat_id in ADMINS:
            #     # for chat_id in ('397875584',):
            #     try:
            #         await bot.send_message(chat_id=chat_id, text='Авто-розсилка вітальних паків відпрацювала:\n\n'
            #                                               f'Розіслано: {sent_count_stges}\n')
            #     except:
            #         continue
        welcome_mail_running[geo] = False
