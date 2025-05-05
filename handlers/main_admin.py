import datetime
import logging
import time
from copy import deepcopy
from typing import List
import pymysql.err
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest
from aiogram_calendar import SimpleCalendar
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from create_bot import scheduler, bot
from handlers.mailing import auto_mailing_geo, start_stop_settings_mail, pick_stage, start_auto_mail, \
    send_messages_auto, interval_time, change_delay_auto_mail, load_time_delay, interval_time_wc_pack, \
    send_wc_message
from utils.aiogram_media_group.handler import media_group_handler
from keyboards.admin_kb import enter_text_kb, post_formatting_kb, user_category_kb, change_create_post_kb, \
    create_post_inline_kb, main_kb, del_post_inline, create_post_inline, \
    back_to_my_posts_inline, media_kb, back_kb, del_voice_kb, auto_mail_formatting_kb, create_new_pack_btn, \
    add_welcome_pack, back_to_stream_btn, delete_edit_kb, back_to_edit_btn, create_stream_btn, \
    save_edit_kb,to_all
from keyboards.client_kb import geo_kb
from utils.db_manage import    users_count_by_stage, users_count_by_stream, \
    get_users_stream,users_count_by_stage_and_stream
from utils.utils_module import FSMAdmin, add_mails_to_kb, show_message, pressed_back_button, \
    restrict_media, send_voice_from_audio, alert_vnote_text, send_messages, add_data_to_job, set_caption, \
    add_packs_to_kb, text_and_inline_by_geo, change_text_json, update_page_num, \
    catalog_paginate, stage_names, ADMINS,rega
from aiogram_timepicker.panel import FullTimePicker, full_timep_callback
from aiogram_calendar import simple_cal_callback
from handlers.stage_edite import edit_stage_stream,edit_stage,add_stage,stage_add_delate,create_stage,create_stage2,save_stage,\
    option_stage,delate_mail

async def admin_start(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)
    if message.from_user.id in ADMINS:
        await bot.send_message(chat_id=message.from_user.id, text='Адмін панель управління розсилками.\n'
                                                                  'Скористайтесь меню нижче ⬇️', reply_markup=main_kb)


async def create_mailing(message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.reset_state()
        if isinstance(message, types.CallbackQuery):
            await message.answer()
            await message.message.edit_text(text='Оберіть гео для розсилки:', reply_markup=geo_kb)
        else:
            await bot.send_message(chat_id=message.from_user.id, text='Оберіть гео для розсилки:', reply_markup=geo_kb)
        await FSMAdmin.geo.set()


async def choose_user_stream(call: types.CallbackQuery, state: FSMContext):
    if call.data != 'back_choose_user_category':
        await state.update_data(geo=call.data)
    await call.answer()
    await streams(call,state)

async def choose_user_category(call: types.CallbackQuery, state: FSMContext):
    if call.data in ('+', "-"):
        data = await state.get_data()
        await update_page_num(data, call.data, state)
        await streams(call, state)
    else:
        if call.data == 'all':
            await state.update_data(stream=None)
        elif call.data != 'back_choose_user_category':
            await state.update_data(stream=call.data)
        await call.answer()
        await call.message.edit_text(text='Оберіть категорію користувачів:', reply_markup=user_category_kb)
        await FSMAdmin.stage.set()


async def load_geo(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    fsm_data = await state.get_data()
    auto_geo = fsm_data.get('auto_mail_geo')
    bot_info = await bot.get_me()
    bot_name = bot_info.username
    if auto_geo:
        await state.reset_state(with_data=False)
        if call.data in stage_names:
            await state.update_data(stage=call.data)
            stage = call.data
        else:
            fsm_data = await state.get_data()
            stage = fsm_data.get('stage')
        kb = InlineKeyboardMarkup(row_width=1)
        job = scheduler.get_job(auto_geo)
        wc_job = scheduler.get_job(f'{auto_geo}_wc')
        packs = None
        wc_packs = None
        if job:
            job_data = job.kwargs.get('data')
            stage_data = job_data.get(stage)
            if stage_data:
                packs = stage_data.get('packs')
        if wc_job:
            wc_job_data = wc_job.kwargs.get('data')
            wc_stage_data = wc_job_data.get(stage)
            if wc_stage_data:
                wc_packs = wc_stage_data.get('packs')
        await add_packs_to_kb(kb, packs, wc_packs)

        users_by_stage = await users_count_by_stage(geo=auto_geo, stage=stage, bot_name=bot_name)
        try:
            await call.message.edit_text(
                text=f'Користувачів: {users_by_stage}\n'
                     'Оберіть пак, або створіть новий:', reply_markup=kb)
            await FSMAdmin.pack.set()
        except:
            pass
        return
    else:
        if call.data in stage_names:
            await state.update_data(stage=call.data)
        else:
            await state.update_data(stage='')
    try:
        data = await state.get_data()
        users_in_stage = await users_count_by_stage_and_stream(geo=data.get('geo'), stage=data.get('stage'),stream_link=data.get('stream'), bot_name=bot_name)
        await call.message.edit_text(
            text=f'Користувачів: {users_in_stage}\n'
                 f'Надішліть текст розсилки:',
            reply_markup=enter_text_kb, parse_mode='html')
    except:
        pass
    await FSMAdmin.post_text.set()


async def load_text(message: types.Message, state: FSMContext):
    if await state.get_state() == 'FSMAdmin:pack':
        await state.update_data(pack=message.data)
    data = await state.get_data()
    post_text = data.get('post_text')
    # entities = data.get('entities')
    job_id = data.get('job_id')
    if isinstance(message, types.Message):
        post_text = message.html_text.replace('http://google.com/','{rega}')
        post_text = post_text.replace('https://google.com/','{rega}')
        # entities = str(message.entities)
    else:
        await message.answer()

    kb = post_formatting_kb
    message_text = 'Налаштуйте повідомлення розсилки.'
    if job_id:
        job = scheduler.get_job(job_id)
        data = job.kwargs.get('data')
        data['post_text'] = post_text
        # data['entities'] = entities
        job.modify(kwargs={'data': data})
    else:
        if 'auto_mail_geo' in data:
            kb = auto_mail_formatting_kb
            geo = data.get('auto_mail_geo')
            stage = data.get('stage')
            pack = data.get('pack')
            message_text = (f'Регіон: {geo}\n\n'
                            'Налаштуйте повідомлення розсилки.')
            await state.update_data({stage: {'post_text': post_text}})
            job_id_mail = geo
            if pack and 'wc' in pack:
                job_id_mail = f'{job_id_mail}_wc'
            job = scheduler.get_job(job_id=job_id_mail)
            if (isinstance(message, types.CallbackQuery) and message.data == 'no_text' or
                    isinstance(message, types.Message)):  # якщо кнопка БЕЗ ТЕКСТУ або повідомлення текстове
                data = await state.get_data()
                if job:
                    job_data = job.kwargs.get('data', {})
                    pack = data.get('pack')
                    stage_data = job_data.get(stage, {})
                    stage_data['packs'][pack]['post_text'] = post_text
                    # stage_data['packs'][pack]['entities'] = entities
                    job_data[stage] = stage_data
                    scheduler.modify_job(job_id=job_id_mail, kwargs={'data': job_data})
                else:
                    scheduler.add_job(send_messages_auto, trigger='interval', seconds=interval_time, id=job_id_mail,
                                      name=job_id_mail,
                                      kwargs={'data': data})
                    scheduler.pause_job(job_id=job_id_mail)
            elif await state.get_state() == 'FSMAdmin:pack':
                if not job:
                    scheduler.add_job(send_messages_auto, trigger='interval', seconds=interval_time, id=job_id_mail,
                                      name=job_id_mail,
                                      kwargs={'data': {stage: {'auto_mail_geo': geo, 'packs': {message.data: {}}}}})
                    scheduler.pause_job(job_id=job_id_mail)
        else:
            await state.update_data(post_text=post_text)
    await show_message(message, state)
    await bot.send_message(chat_id=message.from_user.id, text=message_text,
                           reply_markup=kb, parse_mode='html')
    await state.reset_state(with_data=False)


async def create_wc_pack(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    geo = data.get('auto_mail_geo')
    job = scheduler.get_job(f'{geo}_wc')
    text = 'Вкажіть затримку перед відправкою <b>👋🏻 Вітальний пак {pack_num}</b>:'
    if job:
        job_data = job.kwargs.get('data')
        pack_len = len(job_data.get(job_data.get('stage')).get('packs'))
        text = text.format(pack_num=pack_len + 1)
    else:
        text = text.format(pack_num=1)
    await FSMAdmin.minute_delay_wc.set()
    await call.message.edit_text(text=text, reply_markup=await FullTimePicker().start_picker(), parse_mode='html')


async def create_pack(call: types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    fsm_data = await state.get_data()
    geo = fsm_data.get('auto_mail_geo')
    if not geo:
        logging.warning('No geo found in FSM data.')
        return
    if callback_data and callback_data.get('act') == 'CANCEL':
        await load_geo(call, state)
        return
    if callback_data:
        r = await FullTimePicker().process_selection(call, callback_data)
        if r.selected:
            hour = callback_data.get('hour')
            minute = callback_data.get('minute')
            fsm_data['minute_delay_wc'] = int(hour) * 60 + int(minute)
            job_id = f'{geo}_wc'
            seconds = interval_time_wc_pack
            # seconds = 30
            func = send_wc_message
        else:
            return
    else:
        job_id = geo
        seconds = interval_time
        # seconds = 30
        func = send_messages_auto
    job = scheduler.get_job(job_id)
    if not job:
        scheduler.add_job(func, trigger='interval', seconds=seconds,
                          id=job_id,
                          name=job_id,
                          kwargs={'data': fsm_data})
        job = scheduler.get_job(job_id)
        job.pause()
    job_data = job.kwargs.get('data')
    stage = fsm_data.get('stage')
    stage_data = job_data.get(stage, {})
    packs = stage_data.get('packs', {})
    new_pack_num=1
    for i in range(1,len(packs)+1):
        if f'pack_{i}' not in packs.keys():
            new_pack_num = int(i)
            break
        new_pack_num = int(i) + 1
    # new_pack_num = len(packs) + 1
    new_pack_name = f'pack_{new_pack_num}'
    if callback_data:
        for i in range(1, len(packs) + 1):
            if f'wc_pack_{i}' not in packs.keys():
                new_pack_num = int(i)
                break
            new_pack_num = int(i) + 1
        new_pack_name = f'wc_pack_{new_pack_num}'
    packs[new_pack_name] = {'minute_delay_wc': fsm_data.get('minute_delay_wc')}
    stage_data['packs'] = packs
    job_data[stage] = stage_data
    data = job_data
    job.modify(kwargs={'data': data})
    await load_geo(call, state)
    return


async def delete_pack(call: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    geo = fsm_data.get('auto_mail_geo')
    stage = fsm_data.get('stage')
    pack_to_delete = fsm_data.get('pack')
    is_wc_pack = True if pack_to_delete and 'wc' in pack_to_delete else False
    job_id = f"{geo}_wc" if is_wc_pack else geo
    job = scheduler.get_job(job_id)
    job_data = job.kwargs.get('data')
    del job_data[stage]['packs'][pack_to_delete]
    job.modify(kwargs={'data': job_data})
    await load_geo(call, state)
    return


async def send_now(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('job_id')
    if job_id:
        job = scheduler.get_job(job_id)
        data = job.kwargs.get('data')
    geo = data.get('geo')
    if not geo:
        await bot.send_message(chat_id=call.from_user.id, text='Оберіть гео для розсилки:', reply_markup=geo_kb)
        await FSMAdmin.geo.set()
        return
    keys_to_check = ['post_text', 'loaded_post_files', 'voice', 'video_note', 'random_photos_number',
                     'random_videos_number']
    if any(data.get(key) for key in keys_to_check):
        await call.message.answer(text=f'Розсилка почалась')
        await send_messages(data)
    else:
        await call.answer()
        await call.message.answer(text='❌ Ви не можете розіслати повідомлення, так як у ньому немає контенту.\n'
                                       'Наповніть повідомлення текстом або медіа:',
                                  reply_markup=post_formatting_kb)


async def choose_plan_date(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    job_id = data.get('job_id')

    if job_id:
        job = scheduler.get_job(job_id)
        data = job.kwargs.get('data')
        data['post_type'] = 'planned'
        job.modify(kwargs={'data': data})
    else:
        await state.update_data(post_type='planned')

    await FSMAdmin.date_planning.set()
    await call.message.edit_text(text="Оберіть дату: ", reply_markup=await SimpleCalendar().start_calendar())


async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date_planning=date)
        await state.reset_state(with_data=False)
        await FSMAdmin.time_planning.set()
        await callback_query.message.edit_text(
            f'Ви обрали: {date.strftime("%d/%m/%Y")}\n'
            "Будь ласка оберіть час: ",
            reply_markup=await FullTimePicker().start_picker()
        )


async def full_picker_handler(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback_query.answer()
    r = await FullTimePicker().process_selection(callback_query, callback_data)
    fsm_data = await state.get_data()
    job_id = fsm_data.get('job_id')
    job = None
    if job_id:
        job = scheduler.get_job(job_id)
    if callback_data['act'] == 'CANCEL':
        await state.update_data(date_planning=None)
        await state.update_data(start_loop_date=None)
        await callback_query.message.edit_text(text='Налаштуйте повідомлення розсилки:',
                                               reply_markup=post_formatting_kb)
    if r.selected:
        await state.update_data(time_planning=r.time)
        data = await state.get_data()
        selected_time: time = data.get("time_planning")
        selected_date: datetime = data.get("date_planning")
        selected_date = selected_date.replace(hour=selected_time.hour, minute=selected_time.minute)

        selected_time_str = r.time.strftime("%H:%M")
        selected_date_str = data.get("date_planning").strftime("%d/%m/%Y")
        if job:
            job.remove()
            await callback_query.message.answer(
                f'Планування змінено на {selected_time_str} - {selected_date_str}',
                reply_markup=post_formatting_kb)
        else:
            await callback_query.message.answer(
                f'Публікацію заплановано на {selected_time_str} - {selected_date_str}',
                reply_markup=change_create_post_kb)
            await callback_query.message.delete_reply_markup()
        new_job = scheduler.add_job(send_messages, trigger='date', run_date=selected_date,
                                    kwargs={'data': data})
        data['job_id'] = new_job.id
        new_job.modify(kwargs={'data': data})
        await state.reset_state(with_data=False)
        logging.info(f'POST PLANNED {data}')


async def enter_change_text(message: types.CallbackQuery, state: FSMContext):
    await FSMAdmin.post_text.set()
    try:
        await message.message.edit_text(
            text=f'Надішліть текст: ',
            reply_markup=enter_text_kb, parse_mode='html')
    except:
        pass
    await message.answer()


async def reset_post(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        await call.message.edit_text(text='✅ Налаштування посту скинуто.', reply_markup=change_create_post_kb)
    except:
        pass


async def edit_mailing_list(message: types.CallbackQuery, state: FSMContext):
    if message.from_user.id in ADMINS:
        jobs = [job for job in scheduler.get_jobs() if job.id not in ('AZ', 'BR') and job.next_run_time]

        edit_kb = InlineKeyboardMarkup()
        jobs = sorted(jobs, key=lambda job: job.next_run_time)

        if jobs:
            add_mails_to_kb(jobs=jobs, edit_kb=edit_kb)
            if isinstance(message, types.CallbackQuery):
                await message.answer()
            await bot.send_message(chat_id=message.from_user.id, text='Ваші заплановані розсилки.\n'
                                                                      'Оберіть потрібну вам:', reply_markup=edit_kb)
            await FSMAdmin.job_id.set()
        else:
            if isinstance(message, types.CallbackQuery):
                await message.answer()
                try:
                    await message.message.edit_text('У вас немає запланованих розсилок.',
                                                    reply_markup=create_post_inline_kb)
                except:
                    pass
            else:
                await bot.send_message(chat_id=message.from_user.id, text='У вас немає запланованих розсилок.',
                                       reply_markup=create_post_inline_kb)


async def change_job(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    job_id = call.data
    await state.update_data(job_id=job_id)
    await show_message(call, state)
    await state.reset_state(with_data=False)
    kb = post_formatting_kb
    if job_id:
        kb = deepcopy(post_formatting_kb)
        del kb.inline_keyboard[-1]
        kb.add(del_post_inline)
    await call.message.answer(
        text='Налаштуйте оформлення розсилки', reply_markup=kb)


async def del_post(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    fsm_data = await state.get_data()
    job_id = fsm_data.get('job_id')
    scheduler.remove_job(job_id)
    await call.message.answer(text='Розсилку видалено ✅\n'
                                   'Головне меню ⬇️', reply_markup=main_kb)


async def my_posts_menu(call, state: FSMContext):
    if call.from_user.id in ADMINS:
        await state.finish()
        all_jobs = scheduler.get_jobs()
        if all_jobs:
            await FSMAdmin.posts_by_data.set()
            if isinstance(call, types.CallbackQuery):
                await call.message.edit_text(text='Оберіть дату розсилки:',
                                             reply_markup=await SimpleCalendar().start_calendar())
            else:
                await bot.send_message(chat_id=call.from_user.id, text='Оберіть дату розсилки:',
                                       reply_markup=await SimpleCalendar().start_calendar())

        else:
            try:
                await call.message.edit_text(text='Немає запланованих розсилок.',
                                             reply_markup=InlineKeyboardMarkup().add(create_post_inline))
            except:
                await bot.send_message(chat_id=call.from_user.id, text='Немає запланованих розсилок.',
                                       reply_markup=InlineKeyboardMarkup().add(create_post_inline))


async def my_posts_by_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        all_jobs_by_date = []
        for job in scheduler.get_jobs():
            if job.next_run_time and job.next_run_time.date() == date.date():
                all_jobs_by_date.append(job)
        kb = InlineKeyboardMarkup()
        for job_in_channel in all_jobs_by_date:
            job_in_channel_data = job_in_channel.kwargs.get('data')
            post_type = job_in_channel_data.get('post_type')
            if post_type == 'planned':
                time_planning: datetime.time = job_in_channel.next_run_time.strftime('%H:%M')
                kb.add(
                    InlineKeyboardButton(text=f"Пост о {time_planning} для {job_in_channel_data['stream']} {job_in_channel_data['stage']} - {job_in_channel_data.get('post_text')} ",
                                         callback_data=job_in_channel.id))
            else:
                time_loop: datetime.time = job_in_channel.next_run_time.strftime('%H:%M')
                if job_in_channel_data.get('random_v_notes_id') or job_in_channel_data.get('video_note'):
                    kb.add(
                        InlineKeyboardButton(text=f"Відеоповідомлення о {time_loop}",
                                             callback_data=job_in_channel.id))
                elif job_in_channel_data.get('voice'):
                    kb.add(
                        InlineKeyboardButton(text=f"Голосове о {time_loop}",
                                             callback_data=job_in_channel.id))
                else:
                    try:
                        kb.add(
                            InlineKeyboardButton(
                                text=f"Пост о {time_loop} для {job_in_channel_data['stream']} {job_in_channel_data['stage']} - {job_in_channel_data.get('post_text')}",
                                callback_data=job_in_channel.id))
                    except:
                        continue

        kb.add(back_to_my_posts_inline)
        await FSMAdmin.job_id.set()
        try:
            await callback_query.message.edit_text(
                text=f'Ваші заплановані та зациклені пости {date.strftime("%d.%m.%y")}.\n'
                     'Оберіть будь-який, щоб змінити.', reply_markup=kb)
        except:
            await callback_query.message.answer(
                text=f'Ваші заплановані та зациклені пости {date.strftime("%d.%m.%y")}.\n'
                     'Оберіть будь-який, щоб змінити.', reply_markup=kb)


async def formatting_main_menu(message, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('job_id')
    if job_id:
        job = scheduler.get_job(job_id)
        data = job.kwargs.get('data')
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        try:
            await message.message.edit_text(text='Налаштуйте оформлення посту.',
                                            reply_markup=media_kb)
        except:
            await message.message.answer(text='Налаштуйте оформлення посту.',
                                         reply_markup=media_kb)
    else:
        await message.answer(text='Налаштуйте оформлення посту.',
                             reply_markup=media_kb)
    await state.reset_state(with_data=False)
    await FSMAdmin.media_answer.set()


async def load_media_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = call.data
    fsm_data = await state.get_data()

    if data == 'send_by_self':
        await FSMAdmin.loaded_post_files.set()
        await call.message.edit_text(text='🎞 Надішліть або перешліть сюди медіа.\n'
                                          'Можете також надіслати згруповані фото або відео:\n'
                                          '\t<i>-фото;</i>\n'
                                          '\t<i>-відео;</i>\n'
                                          '\t<i>-голосове повідомлення;</i>\n'
                                          '\t<i>-файл;</i>', parse_mode='html', reply_markup=back_kb)

    elif data == 'remove_media':
        geo = fsm_data.get('auto_mail_geo')
        if geo:
            stage = fsm_data.get('stage')
            job = scheduler.get_job(geo)
            job_data = job.kwargs.get('data')
            fsm_data = job_data.get(stage)
            fsm_data = fsm_data['packs'][pack]
        if not fsm_data.get('job_id'):
            if any(fsm_data.get(key) for key in ('voice', 'loaded_post_files', 'video_note')):
                voice = fsm_data.get('voice')
                loaded_post_files = fsm_data.get('loaded_post_files')
                video_note = fsm_data.get('video_note')
                if voice:
                    fsm_data.pop('voice')
                elif video_note:
                    fsm_data.pop('video_note')
                elif loaded_post_files:
                    fsm_data.pop('loaded_post_files')
                if geo:
                    job.modify(kwargs={'data': job_data})
                else:
                    await state.update_data(loaded_post_files= None)
            else:
                try:
                    await call.message.edit_text(text="У пості немає медіа.", reply_markup=media_kb)
                except:
                    pass

        elif fsm_data.get('job_id'):
            job = scheduler.get_job(fsm_data.get('job_id'))
            job_data = job.kwargs.get('data')

            if any(job_data.get(key) for key in ('voice', 'loaded_post_files')):
                voice = job_data.get('voice')
                loaded_post_files = job_data.get('loaded_post_files')
                if voice:
                    await FSMAdmin.del_voice_or_vnote_answer.set()
                    await call.message.answer_voice(voice=voice)
                    await call.message.answer(text='Бажаєте видалити голосове з посту?', reply_markup=del_voice_kb)
                if loaded_post_files:
                    media: types.MediaGroup = job_data.get('loaded_post_files')
                    for m in range(len(media.media)):
                        if media.media[m].type == 'video':
                            await call.message.answer_video(video=media.media[m].media, caption=m + 1)
                        elif media.media[m].type == 'photo':
                            await call.message.answer_photo(photo=media.media[m].media, caption=m + 1)
                        elif media.media[m].type == 'document':
                            await call.message.answer_document(document=media.media[m].media, caption=m + 1)
                    await FSMAdmin.del_media_answer.set()
                    await call.message.answer(text='Надішліть номер медіа, яке хочете прибрати з посту:')
            else:
                await state.reset_state(with_data=False)
                try:
                    await call.message.edit_text(text="У пості немає медіа.", reply_markup=post_formatting_kb)
                except:
                    pass


@media_group_handler
async def load_media_file(messages: List[types.Message], state: FSMContext):
    data = await state.get_data()
    if pressed_back_button(messages[0]):
        await state.reset_state(with_data=False)
        if data.get('auto_mail_geo'):
            await formatting_main_menu(messages[0], state)
        else:
            await load_media_answer(call=messages[0], state=state)
        return
    job_id = data.get('job_id')
    pack = data.get('pack')
    geo = data.get('geo', data.get('auto_mail_geo'))
    stage = data.get('stage')
    is_wc_pack = True if pack and pack.split('_')[-1] == 'wc' else False
    job_id_auto = geo
    if is_wc_pack:
        geo = data.get('auto_mail_geo')
        job_id_auto = f"{geo}_{stage}_wc"
    auto_job = None
    if job_id_auto:
        auto_job = scheduler.get_job(job_id=job_id_auto)
    # if job_id то дані будуть з джоба
    if job_id:
        job = scheduler.get_job(job_id)
        data = scheduler.get_job(job_id).kwargs.get('data')

    if data.get('random_photos_number'):
        await messages[0].answer(text='⚠️ Рандом-медіа налаштування скинуті.')
        if job_id:
            data['random_photos_number'] = None
            job.modify(kwargs={'data': data})
        else:
            await state.update_data(random_photos_number=None)

    text = data.get('post_text')
    media: types.MediaGroup = data.get('loaded_post_files')

    # якщо медіа раніше не створена то створюємо нову
    if not media:
        media = types.MediaGroup()

    if await restrict_media(messages=messages, state=state, data=data, post_formatting_kb=post_formatting_kb):
        return

    for message_num in range(len(messages)):
        if messages[message_num].content_type in ('audio', 'voice', 'video_note'):
            if 'audio' in messages[0]:
                voice_message = await send_voice_from_audio(message=messages[0], bot=bot)
                if job_id or is_wc_pack:
                    data['voice'] = voice_message.voice.file_id
                    if job_id:
                        job.modify(kwargs={'data': data})
                    elif auto_job:
                        auto_job.modify(kwargs={'data': data})
                elif data.get('auto_mail_geo'):
                    await state.update_data({stage: {'voice': voice_message.voice.file_id}})
                    await add_data_to_job(fsm_data=await state.get_data(), auto_job=auto_job, geo=geo,
                                          data_type='voice', media_data=voice_message.voice.file_id)
                else:
                    await state.update_data(voice=voice_message.voice.file_id)
            elif 'voice' in messages[0]:
                await messages[0].answer_voice(messages[0].voice.file_id, caption=text)
                if job_id or is_wc_pack:
                    data['voice'] = messages[0].voice.file_id
                    if job_id:
                        job.modify(kwargs={'data': data})
                    elif auto_job:
                        auto_job.modify(kwargs={'data': data})
                elif data.get('auto_mail_geo'):
                    await state.update_data({stage: {'voice': messages[0].voice.file_id}})
                    await add_data_to_job(fsm_data=await state.get_data(), auto_job=auto_job, geo=geo,
                                          data_type='voice', media_data=messages[0].voice.file_id)
                else:
                    await state.update_data(voice=messages[0].voice.file_id)
            elif 'video_note' in messages[0]:
                await messages[0].answer_video_note(messages[0].video_note.file_id)
                if job_id or is_wc_pack:
                    data['video_note'] = messages[0].video_note.file_id
                    if job_id:
                        job.modify(kwargs={'data': data})
                    elif auto_job:
                        auto_job.modify(kwargs={'data': data})
                elif data.get('auto_mail_geo'):
                    await state.update_data({stage: {'video_note': messages[0].video_note.file_id}})
                    await add_data_to_job(fsm_data=await state.get_data(), auto_job=auto_job, geo=geo,
                                          data_type='video_note', media_data=messages[0].video_note.file_id)
                else:
                    await state.update_data(video_note=messages[0].video_note.file_id)

            await state.reset_state(with_data=False)
            break
        if 'video' in messages[message_num]:
            media.attach_video(video=messages[message_num].video.file_id)
        elif 'photo' in messages[message_num]:
            media.attach_photo(photo=messages[message_num].photo[0].file_id)
        elif 'document' in messages[message_num]:
            media.attach_document(messages[message_num].document.file_id)

    if media.media:
        if job_id or is_wc_pack:
            data['loaded_post_files'] = media
            if job_id:
                job.modify(kwargs={'data': data})
            elif auto_job:
                auto_job.modify(kwargs={'data': data})
        elif data.get('auto_mail_geo'):
            await state.update_data({stage: {'loaded_post_files': media}})
            await add_data_to_job(fsm_data=await state.get_data(), auto_job=auto_job, geo=geo,
                                  data_type='loaded_post_files', media_data=media)
        else:
            await state.update_data(loaded_post_files=media)

        try:
            await show_message(message=messages[0], state=state)
        except BadRequest:
            await messages[0].answer(text='❌ Цей тип медіа не може бути згрупований з попередніми медіа.')
            media.media.pop()

    await alert_vnote_text(messages[0], state)
    kb = post_formatting_kb
    if data.get('auto_mail_geo'):
        kb = auto_mail_formatting_kb

    await messages[0].answer(text='Оформіть пост або оберіть варіант публікації.',
                             reply_markup=kb)
    await state.reset_state(with_data=False)


async def del_voice_or_video_note(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    fsm_data = await state.get_data()
    job_id = fsm_data.get('job_id')
    if call.data == 'yes':
        if job_id:
            job = scheduler.get_job(job_id)
            job_data = job.kwargs.get('data')
            if 'voice' in job_data:
                job_data['voice'] = None
                await call.message.answer(text='✅ Голосове видалено.', reply_markup=post_formatting_kb)
            elif 'video_note' in job_data:
                job_data['video_note'] = None
                await call.message.answer(text='✅ Відео-повідомлення видалено.', reply_markup=post_formatting_kb)
            job.modify(kwargs={'data': job_data})
        else:
            if 'voice' in fsm_data:
                await state.update_data(voice=None)
                await call.message.answer(text='✅ Голосове видалено.', reply_markup=post_formatting_kb)
            elif 'video_note' in fsm_data:
                await state.update_data(video_note=None)
                await call.message.answer(text='✅ Відео-повідомлення видалено.', reply_markup=post_formatting_kb)
    elif call.data == 'no':
        try:
            await call.message.edit_text(
                text='Налаштуйте оформлення посту.',
                reply_markup=post_formatting_kb)
        except:
            pass

    else:
        return
    await state.reset_state(with_data=False)


async def del_media(message: types.Message, state: FSMContext):
    fsm_data = await state.get_data()
    geo = fsm_data.get('auto_mail_geo')
    if geo:
        stage = fsm_data.get('stage')
        job_auto = scheduler.get_job(geo)
        job_data = job_auto.kwargs.get('data')
        fsm_data = job_data.get(stage)
    inline_kb = fsm_data.get('inline_kb')
    if isinstance(message, types.CallbackQuery):
        if message.data == 'back':
            await state.reset_state(with_data=False)
            try:
                await message.message.edit_text(text='Обрати медіа з бази чи додати самостійно?',
                                                reply_markup=media_kb)
            except:
                pass

    elif isinstance(message, types.Message):
        job_id = fsm_data.get('job_id')
        job = None
        if job_id:
            job = scheduler.get_job(job_id)
            job_data = job.kwargs.get('data')
            post_text = job_data.get('post_text')
            entities = job_data.get('entities')
            media: types.MediaGroup = job_data.get('loaded_post_files')

        else:
            post_text = fsm_data.get('post_text')
            entities = fsm_data.get('entities')
            media: types.MediaGroup = fsm_data.get('loaded_post_files')

        if not post_text:
            post_text = ''
        try:
            del media.media[int(message.text) - 1]
        except:
            await message.answer(text='❌ Невірний формат.\n'
                                      'Введіть 1 номер.')
        if len(media.media) > 0:
            set_caption(text=post_text, media=media, entities=entities),
            if job:
                job_data['loaded_post_files'] = media
                job.modify(kwargs={'data': job_data})
            else:
                await state.update_data(loaded_post_files=media)
            if len(media.media) == 1 and inline_kb:
                m = media.media[0]
                if m.type == 'video':
                    await message.answer_video(video=m.media, caption=post_text, reply_markup=inline_kb,
                                               caption_entities=entities)
                elif m.type == 'photo':
                    await message.answer_photo(photo=m.media, caption=post_text, reply_markup=inline_kb,
                                               caption_entities=entities)
                elif m.type == 'document':
                    await message.answer_document(document=m.media, caption=post_text, reply_markup=inline_kb,
                                                  caption_entities=entities)
            else:
                await message.answer_media_group(media=media)
        else:
            if job:
                del job_data['loaded_post_files']
                job.modify(kwargs={'data': job_data})
            elif geo:
                await state.update_data({stage: {'loaded_post_files': None}})
                await add_data_to_job(fsm_data=await state.get_data(), auto_job=job_auto, geo=geo,
                                      data_type='loaded_post_files', media_data=None)
            else:
                await state.update_data(loaded_post_files=None)
        await show_message(message, state)
        await message.answer(text=f'Медіа №{message.text} видалено з посту.\n'
                                  f'Налаштуйте оформлення посту.', reply_markup=media_kb)
        await state.reset_state(with_data=False)
        await FSMAdmin.media_answer.set()





async def streams(message, state: FSMContext):
    if message.from_user.id in ADMINS:
        bot_info = await bot.get_me()
        bot_name = bot_info.username
        date=await state.get_data()
        if 'stage_stream' in date.keys():
            text = '👇 Оберіть поток щоб редагувати або створіть новий:'
            await FSMAdmin.stream_edit.set()
            dict_stream=await get_users_stream(date['geo'],bot_name)
            catalogs_kb = await catalog_paginate(state,dict_stream)
        else:
            text = '👇 Оберіть поток:'
            await FSMAdmin.stream.set()
            dict_stream=await get_users_stream(date['geo'],bot_name)
            catalogs_kb = await catalog_paginate(state,dict_stream)
            catalogs_kb.add(to_all)
        if isinstance(message, types.CallbackQuery):
            await message.answer()
            try:
                await message.message.edit_text(text=text, reply_markup=catalogs_kb)
            except Exception as exe:
                await message.message.answer(text=text, reply_markup=catalogs_kb)
                pass
        else:
            await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=catalogs_kb)


async def edit_stream(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data in ('+', "-"):
        await update_page_num(data, call.data, state)
        await streams(call, state)
        return
    if call.data != 'edit_stream':
        await state.update_data(stream_edit=call.data)
    bot_info = await bot.get_me()
    bot_name = bot_info.username
    # bot_name = 'aviatr_hackers_bot'
    data = await state.get_data()
    stream = data.get('stream_edit')
    texts, inline, file_id,structure =await text_and_inline_by_geo(data.get('geo'),link=data.get('stream_edit'))
    count = await users_count_by_stream(stream, bot_name)
    await state.update_data(bot_name=bot_name)
    await state.reset_state(with_data=False)
    await call.message.edit_text(text=f"Користувачів: {count}\n"
                                      f'Потік: {stream}\n'
                                      f'Кільксть кнопок:{len(inline)}\n'
                                      f'Кільксть текстів:{len(texts)}\n'
                                      f'Кільксть медіа:{len(file_id)}\n'
                                      f'👇 Що бажаєте зробити?', reply_markup=delete_edit_kb,parse_mode='html')


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=['admin'], state='*')
    dp.register_callback_query_handler(admin_start, Text(equals='admin'), state='*')

    dp.register_callback_query_handler(reset_post, Text(equals='reset_post'), state='*')
    dp.register_callback_query_handler(del_post, Text(equals='delete_mail'))

    dp.register_message_handler(create_mailing, Text(equals='Створити розсилку'), state='*')
    dp.register_callback_query_handler(create_mailing, Text(equals='Створити розсилку'), state='*')
    dp.register_message_handler(my_posts_menu, Text(equals='Мої розсилки'), state='*')
    dp.register_callback_query_handler(my_posts_menu, Text(equals='Мої розсилки'), state='*')
    dp.register_message_handler(auto_mailing_geo, Text(equals='Авто-розсилка'), state='*')
    dp.register_callback_query_handler(auto_mailing_geo, Text(equals='Авто-розсилка'), state='*')
    dp.register_message_handler(edit_stage_stream, Text(equals='Редагувати Потоки'), state='*')
    # dp.register_callback_query_handler(edit_stage_stream, Text(equals='Редагувати Потоки'), state='*')
    dp.register_callback_query_handler(change_delay_auto_mail, Text(equals='change_delay'), state='*')
    dp.register_callback_query_handler(start_stop_settings_mail, state=FSMAdmin.auto_mail_geo)
    dp.register_callback_query_handler(start_stop_settings_mail, Text(equals='pick_stage_auto'), state='*')
    dp.register_callback_query_handler(my_posts_by_date, simple_cal_callback.filter(),
                                       state=FSMAdmin.posts_by_data)

    dp.register_callback_query_handler(choose_user_category, state=FSMAdmin.stream)
    dp.register_callback_query_handler(load_geo, state=FSMAdmin.stage)
    dp.register_callback_query_handler(load_geo, Text(equals='choose_pack'), state="*")
    dp.register_callback_query_handler(choose_user_stream, state=FSMAdmin.geo)
    dp.register_callback_query_handler(streams, Text(equals='Редагувати Потоки'), state="*")
    dp.register_callback_query_handler(choose_user_category, Text(equals='back_choose_user_category'), state='*')
    dp.register_message_handler(load_text, state=FSMAdmin.post_text)
    dp.register_callback_query_handler(load_text, state=FSMAdmin.post_text)
    dp.register_callback_query_handler(load_text, Text(equals='formatting_main_menu'), state="*")
    dp.register_callback_query_handler(enter_change_text, Text(equals='Змінити текст'), state='*')
    dp.register_callback_query_handler(edit_mailing_list, Text(equals='Змінити розсилку'), state='*')
    dp.register_message_handler(edit_mailing_list, Text(equals='Змінити розсилку'), state='*')

    dp.register_callback_query_handler(choose_plan_date, Text(equals='Запланувати'), state='*')
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(),
                                       state=FSMAdmin.date_planning)
    dp.register_callback_query_handler(full_picker_handler, full_timep_callback.filter(), state=FSMAdmin.time_planning)

    dp.register_callback_query_handler(send_now, Text(equals='Опублікувати'))
    dp.register_callback_query_handler(change_job, state=FSMAdmin.job_id)

    dp.register_callback_query_handler(formatting_main_menu, Text(equals='Налаштувати медіа'))
    dp.register_callback_query_handler(load_media_answer, state=FSMAdmin.media_answer)
    dp.register_callback_query_handler(load_media_file, state=FSMAdmin.loaded_post_files)
    dp.register_message_handler(load_media_file, state=FSMAdmin.loaded_post_files,
                                content_types=types.ContentType.all())
    dp.register_callback_query_handler(del_voice_or_video_note, state=FSMAdmin.del_voice_or_vnote_answer)

    """auto mailing"""
    dp.register_callback_query_handler(load_time_delay, full_timep_callback.filter(), state=FSMAdmin.mail_delay)

    dp.register_callback_query_handler(pick_stage, Text(equals='mail_settings'), state='*')
    dp.register_callback_query_handler(create_pack, Text(equals='create_pack'), state='*')
    dp.register_callback_query_handler(create_pack, full_timep_callback.filter(), state=FSMAdmin.minute_delay_wc)
    dp.register_callback_query_handler(create_wc_pack, Text(equals='add_wc_pack'), state='*')
    dp.register_callback_query_handler(delete_pack, Text(equals='delete_pack'), state='*')
    dp.register_callback_query_handler(load_text, state=FSMAdmin.pack)

    dp.register_callback_query_handler(start_auto_mail, Text(equals='start_mail'))
    dp.register_callback_query_handler(start_auto_mail, Text(equals='stop_mail'))
    dp.register_message_handler(del_media, state=FSMAdmin.del_media_answer)

    # dp.register_callback_query_handler(edit_stream_list, Text(equals='edit_stream_link'), state='*')
    dp.register_callback_query_handler(edit_stream, state=FSMAdmin.stream_edit)
    dp.register_callback_query_handler(edit_stream, Text(equals='edit_stream'), state='*')
    dp.register_callback_query_handler(edit_stage,text='edit_stage',state="*")
    dp.register_callback_query_handler(stage_add_delate, state=FSMAdmin.blok_stage)
    dp.register_callback_query_handler(add_stage, state=FSMAdmin.blok_message)
    dp.register_callback_query_handler(add_stage, text=['text_change_end','button_change_end','media_change_end','time_change_end','stage_change_end','delete_message'],state="*" )
    dp.register_callback_query_handler(create_stage, text=['text_change','button_change','media_change','time_change','stage_change'],state="*")
    dp.register_callback_query_handler(delate_mail, text=['text_delete','button_delete','media_delete','time_delete'],state="*")
    dp.register_callback_query_handler(save_stage, text=['save_now'],state="*")
    dp.register_message_handler(create_stage2,state=FSMAdmin.new_text, content_types=types.ContentType.ANY)