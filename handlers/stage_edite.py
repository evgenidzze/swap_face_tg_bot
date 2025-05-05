import datetime
import json
import logging
import time
from copy import deepcopy
from typing import List
import pymysql.err
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import BadRequest
from aiogram_calendar import SimpleCalendar
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from utils.utils_module import FSMAdmin, add_mails_to_kb, show_message, pressed_back_button, \
    restrict_media, send_voice_from_audio, alert_vnote_text, send_messages, add_data_to_job, set_caption, \
    add_packs_to_kb, text_and_inline_by_geo, change_text_json, update_page_num, \
    catalog_paginate, stage_names, ADMINS,rega,get_Structure,write_file_Structure
from keyboards.client_kb import geo_kb
from keyboards.admin_kb import save_edit_kb,post_formatting_kb_stage,post_formatting_kb_stage_2

async def edit_stage_stream(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.update_data(stage_stream=True)
        if isinstance(message, types.CallbackQuery):
            await message.answer()
            await message.message.answer(text='Оберіть гео:', reply_markup=geo_kb)
        else:
            await message.answer(text='Оберіть гео:', reply_markup=geo_kb)
        await FSMAdmin.geo.set()


async def ask_new_text(message: types.Message, state: FSMContext):
    new_text = message.html_text
    geo=await state.get_data()
    if geo['change_text_geo']=='AZ':
        new_text = message.html_text.replace('http://google.com/', '{rega[0]}')
        new_text = new_text.replace('https://google.com/', '{rega[0]}')
    else:
        new_text = message.html_text.replace('http://google.com/', '{rega[1]}')
        new_text = new_text.replace('https://google.com/', '{rega[1]}')
    await state.update_data(new_text=new_text)
    await message.answer(text=new_text, reply_markup=save_edit_kb,parse_mode='html')
    await state.reset_state(with_data=False)

async def edit_stage(call: types.CallbackQuery, state: FSMContext):
    data=await state.get_data()
    structure=await get_Structure(data['geo'])
    if data['stream_edit'] in structure.keys():
        structure_data = structure[data['stream_edit']]
    else:
        structure_data=structure['default']
    streamKeyboard = InlineKeyboardMarkup()
    await state.update_data(structure=structure_data)
    for i in structure_data:
        streamKeyboard_btn = InlineKeyboardButton(text=i, callback_data=i)
        streamKeyboard.add(streamKeyboard_btn)
    add_stream_btn = InlineKeyboardButton(text='Додати блок', callback_data='add_stage')
    back_to_edit_btn = InlineKeyboardButton(text='« Назад', callback_data='Редагувати Потоки')
    streamKeyboard.add(add_stream_btn).add(back_to_edit_btn)
    await FSMAdmin.blok_stage.set()
    await call.message.edit_text('Виберіть дію:',reply_markup=streamKeyboard)

async def stage_add_delate(call: types.CallbackQuery, state: FSMContext):
    data=await state.get_data()
    await state.reset_state(with_data=False)
    await state.update_data(text=None,file=None, type=None,button_text=None,Keyboard=None,new_time=None,new_stage=None)
    await FSMAdmin.blok_message.set()
    streamKeyboard = InlineKeyboardMarkup()
    add_message = InlineKeyboardButton(text='Додати повідомлення', callback_data='add_message')
    add_message_change = InlineKeyboardButton(text='Додати повідомлення автопереходу', callback_data='add_auto_change')
    delate_rega_btn = InlineKeyboardButton(text='Видалити блок', callback_data='delate_stage')
    back_to_edit_btn = InlineKeyboardButton(text='« Назад', callback_data='edit_stage')
    if call.data=='add_stage':
        structure_data=data['structure']
        id=len(structure_data)-1
        for ii in [ i for  i in range(len(structure_data)-1)]+['check_dep']:
            if str(ii) not in structure_data.keys():
                id=ii
        print(id)
        structure_data.update({str(id):{}})
        await state.update_data(structure=structure_data,block=str(id))
        await call.message.answer('Блок доданий')
        texts, inline, file_id, structure = await text_and_inline_by_geo(data.get('geo'), link=data.get('stream_edit'))
        block=str(id)
    else:
        texts, inline, file_id, structure = await text_and_inline_by_geo(data.get('geo'), link=data.get('stream_edit'),stage=call.data)
        await state.update_data(block=call.data)
        block=call.data
        for i in structure:
            streamKeyboard_btn = InlineKeyboardButton(text=i, callback_data=i)
            streamKeyboard.add(streamKeyboard_btn)
    await state.update_data(texts=texts, inline=inline, file_id=file_id)
    streamKeyboard.add(add_message,add_message_change).add(delate_rega_btn).add(back_to_edit_btn)
    await call.message.edit_text(f'Посилання : https://t.me/{data["bot_name"]}?start=geo-{data.get("geo")}_channel-{data.get("stream_edit")}_stage-{block}\nВиберість дію',reply_markup=streamKeyboard)

async def add_stage(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.reset_state(with_data=False)
    Keyboard = post_formatting_kb_stage
    if call.data=='delate_stage':
        structure_data = data['structure']
        structure_data.pop(data['block'])
        await state.update_data(structure=structure_data)
        return await save_stage(call,state)
    elif call.data=='delete_message':
        structure_data = data['structure']
        structure_data[data['block']].pop(data['message'])
        await state.update_data(structure=structure_data)
        return await save_stage(call,state)
    elif call.data in ['text_change_end','button_change_end','media_change_end','time_change_end','stage_change_end']:
        structure_data = data['structure']
        if call.data=='text_change_end':
            if data['text'] in data['texts']:
                structure_data[data['block']][data['message']]['text_id']=data['texts'].index(data['text'])
            else:
                data['texts'].insert(-1,data['text'])
                structure_data[data['block']][data['message']]['text_id']=len(data['texts'])-2
                await state.update_data(texts=data['texts'])
        elif call.data=='button_change_end':
            if data['Keyboard'] in data['inline']:
                structure_data[data['block']][data['message']]['inline']=data['inline'].index(data['Keyboard'])
            else:
                data['inline'].insert(-1,data['Keyboard'])
                structure_data[data['block']][data['message']]['inline']=len(data['inline'])-2
                await state.update_data(inline=data['inline'])
        elif call.data=='media_change_end':
            if data['file'] in  data['file_id']:
                structure_data[data['block']][data['message']]['file_id']=data['file_id'].index(data['file'])
            else:
                data['file_id'].insert(-1,data['file'])
                structure_data[data['block']][data['message']]['file_id']=len(data['file_id'])-2
                await state.update_data(file_id=data['file_id'])
            structure_data[data['block']][data['message']]['type']=data['type']
        elif call.data=='time_change_end':
            structure_data[data['block']][data['message']]['time']=int(data['new_time'])
        elif call.data=='stage_change_end':
            structure_data[data['block']][data['message']]['stage']=data['new_stage']
            Keyboard = post_formatting_kb_stage_2
        await state.update_data(structure=structure_data,task=None)
        message = structure_data[data['block']][data['message']]
    elif call.data=='add_message':
        structure_data = data['structure']
        message={"type": "text", "file_id": -1, "text_id": -1, "inline": -1, "time": 0}
        id=len(structure_data[data['block']])
        for i in range(id):
            if str(i) not in structure_data[data['block']].keys():
                id=i
        structure_data[data['block']].update({str(id):message})
        await state.update_data(structure=structure_data,message=str(id),task=None)
    elif call.data == 'add_auto_change':
        structure_data = data['structure']
        message={"type": "auto_redirect", "file_id": -1, "text_id": -1, "inline": -1, "time": 0,'stage':str(int(data['block'])+1)}
        for i in structure_data[data['block']].keys():
            if structure_data[data['block']][i]["type"]== "auto_redirect":
                message=structure_data[data['block']][i]["type"]
                id = int(i)
                break
            id=int(i)+1
        structure_data[data['block']].update({str(id):message})
        await state.update_data(structure=structure_data,message=str(id),task=None)
        Keyboard=post_formatting_kb_stage_2
    elif call.data!='add_message':
        structure_data = data['structure']
        message=structure_data[data['block']][call.data]
        await state.update_data(message=call.data,task=None)
    texts, inline, file_id = data['texts'].copy(), data['inline'].copy(), data['file_id'].copy()
    await message_represent(texts, inline, file_id, message, call)
    await call.message.answer('Choose action:',reply_markup=Keyboard)


async def message_represent(texts, inline, file_id,message,call):
    await call.message.answer(f'Time delay: {message["time"]}')
    if message['type']== 'auto_redirect':
        await call.message.answer("Stage redirect: "+message['stage'])
    elif  message['type']== 'video':
        messages = {'video': file_id[message['file_id']], 'caption': texts[message['text_id']],
                    'reply_markup': inline[message['inline']]}
        await call.message.answer_video(**messages,parse_mode='html')
    elif  message['type']== 'video_note':
        messages = {'video_note': file_id[message['file_id']]}
        await call.message.answer_video_note(**messages)
    elif  message['type']== 'photo':
        messages = {'photo': file_id[message['file_id']], 'caption': texts[message['text_id']],
                    'reply_markup': inline[message['inline']]}
        await call.message.answer_photo(**messages,parse_mode='html')
    elif  message['type'] == 'animation':
        messages = {'animation': file_id[message['file_id']], 'caption': texts[message['text_id']],
                    'reply_markup': inline[message['inline']]}
        await call.message.answer_animation(**messages,parse_mode='html')
    elif  message['type'] == 'voice':
        messages = {'voice': file_id[message['file_id']]}
        await call.message.answer_voice(**messages)
    elif  message['type'] == 'text' and texts[message['text_id']]!=None:
        messages = {'text': texts[message['text_id']], 'reply_markup': inline[message['inline']]}
        await call.message.answer(**messages,parse_mode='html')


async def create_stage(c:types.CallbackQuery, state: FSMContext):
    date=await state.get_data()
    if not date['task']:
        if c.data == 'text_change':
            button_1 = InlineKeyboardButton("Змінити текст", callback_data='text_change')
            button_2 = InlineKeyboardButton("Видалити текст", callback_data='text_delete')
        elif c.data == 'media_change':
            button_1 = InlineKeyboardButton("Змінити медіа", callback_data='media_change')
            button_2 = InlineKeyboardButton("Видалити медіа", callback_data='media_delete')
        elif c.data == 'button_change':
            button_1 = InlineKeyboardButton("Змінити інлайн", callback_data='button_change')
            button_2 = InlineKeyboardButton("Видалити інлайн", callback_data='button_delete')
        await state.update_data(task=c.data)
        if c.data not in ['time_change',"stage_change"]:
            greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(button_1).add(button_2)
            await c.message.answer('Виберіть дію:', reply_markup=greet_kb)
        else:
            await create_stage(c,state)
    else:
        await FSMAdmin.new_text.set()
        if c.data == 'text_change':
            await state.update_data(text=None)
            await c.message.answer('Надішліть текст:')
        elif c.data == 'media_change':
            await state.update_data(file=None, type=None)
            await c.message.answer('Надішліть media:')
        elif c.data == 'button_change':
            await state.update_data(button_text=None,Keyboard=None)
            await c.message.answer('Надішліть button текст:')
        elif c.data == 'time_change':
            await state.update_data(new_time=None)
            await c.message.answer('Надішліть час в секундах текст:')
        elif c.data == 'stage_change':
            await state.update_data(new_stage=None)
            await c.message.answer('Надішліть stage текст:')

async def create_stage2(m:types.Message, state: FSMContext):
    date = await state.get_data()
    if date['task']== 'text_change':
        await get_text(m,state)
    elif date['task']== 'media_change':
        await get_media(m,state)
    elif date['task']== 'button_change':
        await get_inline(m,state)
    elif date['task']== 'time_change':
        if m.html_text.isdigit():
            await state.update_data(new_time=m.html_text)
            button_1 = InlineKeyboardButton("Так", callback_data='time_change_end')
            button_2 = InlineKeyboardButton("Ні", callback_data='time_change')
            greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(button_1).add(button_2)
            await state.reset_state(with_data=False)
            await m.answer(m.html_text)
            await m.answer("Все вірно?", reply_markup=greet_kb)
        else:
            await m.answer('Введіть тільки цифри')
    elif  date['task']== 'stage_change':
        await state.update_data(new_stage=m.html_text)
        button_1 = InlineKeyboardButton("Так", callback_data='stage_change_end')
        button_2 = InlineKeyboardButton("Ні", callback_data='stage_change')
        greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(button_1).add(button_2)
        await state.reset_state(with_data=False)
        await m.answer(m.html_text)
        await m.answer("Все вірно?", reply_markup=greet_kb)

async def option_stage(c: types.CallbackQuery, state: FSMContext):
    if c.data == 'text':
        button_1 = InlineKeyboardButton("Змінити текст", callback_data='text_change')
        button_2 = InlineKeyboardButton("Видалити текст", callback_data='text_delete')
    elif c.data == 'media':
        button_1 = InlineKeyboardButton("Змінити медіа", callback_data='media_change')
        button_2 = InlineKeyboardButton("Видалити медіа", callback_data='media_delete')
    elif c.data == 'inline':
        button_1 = InlineKeyboardButton("Змінити інлайн", callback_data='button_change')
        button_2 = InlineKeyboardButton("Видалити інлайн", callback_data='button_delete')
    greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(button_1).add(button_2)
    await c.message.answer('Виберіть дію:', reply_markup=greet_kb)


async def delate_mail(c: types.CallbackQuery, state: FSMContext):
    date = await state.get_data()
    structure_data = date['structure']
    if c.data == 'text_delete':
        structure_data[date['block']][date['message']]['text_id']=-1
        await state.update_data(text=None)
    elif c.data == 'media_delete':
        structure_data[date['block']][date['message']]['file_id']=-1
        await state.update_data(file=None, event='text')
    elif c.data == 'button_delete':
        structure_data[date['block']][date['message']]['inline']=-1
        await state.update_data(button_text=None,Keyboard=None)
    await state.update_data(structure=structure_data)
    await c.message.answer("Виконано")
    call = types.CallbackQuery(message=c.message, data=date['message'])
    await add_stage(call,state)


async def get_text(m: types.Message, state: FSMContext):
    date = await state.get_data()
    text=m.html_text.replace('http://google.com/','{rega}')
    text=text.replace('https://google.com/','{rega}')
    await state.update_data(text=text)
    button_1 = InlineKeyboardButton("Так", callback_data='text_change_end')
    button_2 = InlineKeyboardButton("Ні", callback_data='text_change')
    greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(button_1).add(button_2)
    await state.reset_state(with_data=False)
    await m.answer(text)
    await m.answer("Все вірно?", reply_markup=greet_kb)


async def get_media(m: types.Message, state: FSMContext):
    greet_kb = InlineKeyboardMarkup(resize_keyboard=True)
    date = await state.get_data()
    if m.video:
        file = m.video.file_id
        event = 'video'
        await m.answer_video(file)
    elif m.photo:
        file = m.photo[0].file_id
        event = 'photo'
        await m.answer_photo(file)
    elif m.animation:
        file = m.animation.file_id
        event = 'animation'
        await m.answer_animation(file)
    elif m.voice:
        file = m.voice.file_id
        event = 'voice'
        await m.answer_voice(file)
    elif m.video_note:
        file = m.video_note.file_id
        event = 'video_note'
        await m.answer_video_note(file)
    await state.update_data(file=file, type=event)
    button_1 = InlineKeyboardButton("Так", callback_data='media_change_end')
    button_2 = InlineKeyboardButton("Ні", callback_data='media_change')
    greet_kb.add(button_1).add(button_2)
    await state.reset_state(with_data=False)
    await m.answer("Все вірно?", reply_markup=greet_kb)


async def get_inline(m: types.Message, state: FSMContext):
    date = await state.get_data()
    if not date['button_text'] and m.text!='СТОП_КВ':
        await state.update_data(button_text=m.text)
        await m.answer('Для меню відправте -1 :')
    elif date['button_text']:
        if '.' in m.text:
            buttom=InlineKeyboardButton(date['button_text'], url=m.text)
        elif '-1'==m.text:
            buttom=KeyboardButton(text=date['button_text'])
        else:
            buttom =InlineKeyboardButton(date['button_text'], callback_data=m.text)
        if date['Keyboard']==None:
            if type(buttom) == types.inline_keyboard.InlineKeyboardButton:
                greet_kb = InlineKeyboardMarkup(resize_keyboard=True)
            else:
                greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
        else:
            greet_kb=date['Keyboard']
        greet_kb.add(buttom)
        await state.update_data(button_text=None)
        await state.update_data(Keyboard=greet_kb)
        await m.answer('Для зупинки відправте СТОП_КВ для додавання іншої кнопки відправте інший текст',reply_markup=greet_kb)
    else:
        await state.reset_state(with_data=False)
        greet_kb = date['Keyboard']
        await m.answer('????',reply_markup=greet_kb)
        await state.update_data(Keyboard=json.loads(str(date['Keyboard'])))
        greet_kb = InlineKeyboardMarkup(resize_keyboard=True)
        button_1 = InlineKeyboardButton("Так", callback_data='button_change_end')
        button_2 = InlineKeyboardButton("Ні", callback_data='button_change')
        greet_kb.add(button_1).add(button_2)
        await m.answer("Все вірно?", reply_markup=greet_kb)

async def save_stage(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    geo=data['geo']
    stream=data['stream_edit']
    rega = [
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}',
    'https://slottica-bonus.com/registration/c=0241LyA9F-iPHPb5bac4b3ebec4237&utm_source=bonusbot&utm_campaign={STREAM}&utm_content={USERID}&utm_term={GEO}']
    if geo == "AZ":
        rega = rega[0].format(STREAM=stream, USERID=f'0_{data["bot_name"]}', GEO=geo)
        texts = [text.replace(rega, '{rega}') for text in data['texts'] if text]
    else:
        rega = rega[1].format(STREAM=stream, USERID=f'0_{data["bot_name"]}', GEO=geo)
        texts = [text.replace(rega, '{rega}') for text in data['texts'] if text]
    await write_file_Structure(geo,stream,{'structure':data['structure'],'texts':texts,'main_id':data['file_id'][:-1],'button':data['inline'][:-1]})
    if call.data=='delate_stage':
        await edit_stage(call, state)
    else:
        call = types.CallbackQuery(message=call.message, data=data['block'])
        await stage_add_delate(call,state)