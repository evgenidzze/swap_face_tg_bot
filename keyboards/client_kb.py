from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup

from utils.utils_module import inline_br, inline_uz,ls

uz_geo_btn = InlineKeyboardButton('🇦🇿 Azerbaijan', callback_data='AZ')
br_geo_btn = InlineKeyboardButton('🇧🇷 Brasil', callback_data='BR')
geo_kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(uz_geo_btn)

get_bot_free_uz_btn = InlineKeyboardButton('✅TAYYOR', callback_data='1.1')
get_bot_free_uz_kb = InlineKeyboardMarkup(resize_keyboard=True).add(get_bot_free_uz_btn)

join_group_btn = InlineKeyboardButton(inline_br[0], callback_data='1.1')
how_works_br_btn = InlineKeyboardButton(inline_br[1], callback_data='1.2')
feedback_btn = InlineKeyboardButton(inline_br[2], callback_data='1.3')
join_group_br_kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(join_group_btn)

activate_btn = InlineKeyboardButton(inline_uz[0], callback_data='1.0')
activate_bot_uz_kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(activate_btn)

register_uz_btn = InlineKeyboardButton("👨‍💻 Roʻyxatdan oʻting va hisobingizni toʻldiring ➡️💸",
                                       url='https://bit.ly/3R0mDF8')
ask_question_uz_btn = InlineKeyboardButton("✍️ SAVOL BERISH", url=ls)#'https://t.me/Team_Farrux')
register_uz_kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add( ask_question_uz_btn)

register_br_btn = InlineKeyboardButton("👨‍💻 Cadastre-se e recarregue sua conta ➡️💸",
                                       url='https://bit.ly/40VwWh2')
ask_question_br_btn = InlineKeyboardButton("✍️ Faça uma pergunta ", url='https://t.me/VictoriaMendes_BR')
register_br_kb = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(register_br_btn)

BOTni_faollashtirish_btn = InlineKeyboardButton('🟢 BOTU AKTİV ET 🤖',
                                                url='https://t.me/AviaAZ_signal_bot?start=sdafavd')
load_pl_id_uz_kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1).add(BOTni_faollashtirish_btn)   ####

entre_no_grupo = InlineKeyboardButton('🟢 CONECTAR O ROBÔ 🤖', url='https://t.me/AviaAZ_signal_bot?start=sdafavd')
entre_no_grupo1 = InlineKeyboardButton('👑 Canal VIP. 24/7', url='https://t.me/+orrN8EIJ-dw3MDQ0')
load_lp_id_br_kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1).add(entre_no_grupo,entre_no_grupo1)


rega_bt = InlineKeyboardButton('👉 ЗАРЕГИСТРИРОВАТЬСЯ И ИГРАТЬ 👈', url='Rega https://referencemen.net/ktVmDV?c=02344WCeSw_RP08f54f277d1450389&')
rega_bt_kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1).add(rega_bt)

load_lp_robo_br_kb=InlineKeyboardMarkup().add(entre_no_grupo)

buttom2 = InlineKeyboardButton(text='✅TAYYOR', callback_data='2.1')
waite_kb=InlineKeyboardMarkup().add(buttom2)


button_1 = KeyboardButton(inline_uz[0])
invitor_link = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1)
