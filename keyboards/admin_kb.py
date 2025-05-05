from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

create_mailing = KeyboardButton(text='Створити розсилку')
edit_mailing = KeyboardButton(text='Змінити розсилку')
my_mails = KeyboardButton(text='Мої розсилки')
auto_mailing_btn = KeyboardButton(text='Авто-розсилка')
change_texts = KeyboardButton(text='Змінити потоків')
streams_btn = KeyboardButton(text='Редагувати Потоки')

main_kb.add(create_mailing, edit_mailing, my_mails, auto_mailing_btn, streams_btn, change_texts)

enter_text_kb = InlineKeyboardMarkup(row_width=1)
no_text_inline = InlineKeyboardButton(text='Без тексту', callback_data='no_text')
back_to_admin_geo = InlineKeyboardButton(text='« Назад', callback_data='back_choose_user_category')
enter_text_kb.add(no_text_inline, back_to_admin_geo)

post_formatting_kb = InlineKeyboardMarkup(row_width=2)
plan_menu = InlineKeyboardButton(text='🗓 Запланувати', callback_data='Запланувати')
change_text = InlineKeyboardButton(text='📝 Змінити текст', callback_data='Змінити текст')
del_post_inline = InlineKeyboardButton(text='❌ Видалити розсилку', callback_data='delete_mail')
inlines = InlineKeyboardButton(text='Інлайни', callback_data='inlines')
media_settings = InlineKeyboardButton(text='🎞 Налаштувати медіа', callback_data='Налаштувати медіа')
reset_post = InlineKeyboardButton(text='❌ Скинути повідомлення', callback_data='reset_post')
post_now = InlineKeyboardButton(text='Розіслати зараз 🚀', callback_data='Опублікувати')

post_formatting_kb.add(plan_menu, media_settings, change_text, inlines, reset_post, post_now)
back = InlineKeyboardButton(text='« Назад', callback_data='back')

user_category_kb = InlineKeyboardMarkup(row_width=1)
start_cat = InlineKeyboardButton(text='Всі інші', callback_data='Всі інші')#'Всі інші', 'Баланс 0', 'Не достатньо', 'Повний деп'
# player_input = InlineKeyboardButton(text='Отримав регу', callback_data='Отримав регу')
input_cat_btn = InlineKeyboardButton(text='Баланс 0', callback_data='Баланс 0')
wrong_id_cat_btn = InlineKeyboardButton(text='Не достатньо', callback_data='Не достатньо')
error_cat = InlineKeyboardButton(text='Повний деп', callback_data='Повний деп')

to_all = InlineKeyboardButton(text='Всім', callback_data='all')
back_to_main_btn = InlineKeyboardButton(text='« Назад', callback_data='pick_stage_auto')
user_category_kb.add(start_cat, input_cat_btn, wrong_id_cat_btn, error_cat, to_all, back_to_main_btn)

change_create_post_kb = InlineKeyboardMarkup(row_width=2)
create_post_inline = InlineKeyboardButton(text='Створити розсилку', callback_data='Створити розсилку')
change_post = InlineKeyboardButton(text='Змінити розсилку', callback_data='Змінити розсилку')
back_edit_post_inline = InlineKeyboardButton(text='« Назад', callback_data='Змінити розсилку')

my_posts_inline = InlineKeyboardButton(text='Мої розсилки', callback_data='Мої розсилки')
back_to_my_posts_inline = InlineKeyboardButton(text='« Назад', callback_data='admin')
change_create_post_kb.add(create_post_inline, change_post, my_posts_inline)

inlines_menu_kb = InlineKeyboardMarkup(row_width=2)
add_inline = InlineKeyboardButton(text='Додати інлайн', callback_data='add_inline')
del_inline = InlineKeyboardButton(text='Видалити інлайн', callback_data='del_inline')
edit_inline_link = InlineKeyboardButton(text='Змінити посилання', callback_data='edit_inline_link')
back_to_formatting = InlineKeyboardButton(text='« Назад', callback_data='formatting_main_menu')

inlines_menu_kb.add(add_inline, edit_inline_link, back_to_formatting, del_inline)

inlines_menu_kb = InlineKeyboardMarkup(row_width=2)
add_inline = InlineKeyboardButton(text='Додати інлайн', callback_data='add_inline')
del_inline = InlineKeyboardButton(text='Видалити інлайн', callback_data='del_inline')
edit_inline_link = InlineKeyboardButton(text='Змінити посилання', callback_data='edit_inline_link')
back_to_inlines = InlineKeyboardButton(text='« Назад', callback_data='inlines')
inlines_menu_kb.add(add_inline, edit_inline_link, back_to_formatting, del_inline)

back_kb = InlineKeyboardMarkup()
back_kb.add(back)

create_post_inline_kb = InlineKeyboardMarkup(row_width=2)
create_post_inline_kb.add(create_post_inline, back_edit_post_inline)

media_kb = InlineKeyboardMarkup(row_width=2)
remove_media = InlineKeyboardButton(text='❌ Видалити медіа', callback_data='remove_media')
load_media = InlineKeyboardButton(text='Додати медіа', callback_data='send_by_self')
media_kb.add(load_media, remove_media, back_to_formatting)

del_voice_kb = InlineKeyboardMarkup()
del_voice_kb.add(InlineKeyboardButton(text='Так', callback_data='yes'))
del_voice_kb.add(InlineKeyboardButton(text='Ні', callback_data='no'))

"""AUTO MAILING"""

manage_panel_kb = InlineKeyboardMarkup(row_width=2)
start_mail_btn = InlineKeyboardButton(text='Запустити', callback_data='start_mail')
stop_mail_btn = InlineKeyboardButton(text='Зупинити', callback_data='stop_mail')
mail_settings_btn = InlineKeyboardButton(text='Налаштування', callback_data='mail_settings')
manage_panel_kb.add(start_mail_btn, mail_settings_btn,
                    InlineKeyboardButton(text='« Назад', callback_data='Авто-розсилка'))

auto_mail_formatting_kb = InlineKeyboardMarkup(row_width=2)
back_settings_media_auto = InlineKeyboardButton(text='« Назад', callback_data='choose_pack')
delete_pack_btn = InlineKeyboardButton('❌ Видалити пак', callback_data='delete_pack')
auto_mail_formatting_kb.add(media_settings, change_text, delete_pack_btn, inlines, back_settings_media_auto)

media_kb_auto = InlineKeyboardMarkup(row_width=2)
remove_media = InlineKeyboardButton(text='❌ Видалити медіа', callback_data='remove_media')
load_media = InlineKeyboardButton(text='Додати медіа', callback_data='send_by_self')
media_kb_auto.add(load_media, remove_media, back_settings_media_auto)

create_new_pack_btn = InlineKeyboardButton(text='➕ Створити пак', callback_data='create_pack')

change_delay_btn = InlineKeyboardButton(text='Змінити проміжок часу', callback_data='change_delay')
add_welcome_pack = InlineKeyboardButton(text='➕ Додати вітальний пак', callback_data='add_wc_pack')

save_text_btn = InlineKeyboardButton(text='✅ Зберегти', callback_data='save_text')
change_text_btn = InlineKeyboardButton(text='✏️ Редагувати', callback_data='change_text')
save_edit_kb = InlineKeyboardMarkup().add(save_text_btn, change_text_btn)
save_edit_kb.add(back_to_my_posts_inline)

create_stream_btn = InlineKeyboardButton(text='Створити поток', callback_data='create_stream')
edit_stream_btn = InlineKeyboardButton(text='Редагувати поток', callback_data='edit_stream_link')
stream_kb = InlineKeyboardMarkup().add(create_stream_btn, edit_stream_btn)

back_to_stream_btn = InlineKeyboardButton(text='« Назад', callback_data='Редагувати Потоки')
back_to_edit_btn = InlineKeyboardButton(text='« Назад', callback_data='edit_stream')

delete_stream_btn = InlineKeyboardButton(text='Редагувати блок', callback_data='edit_stage')
# change_rega_btn = InlineKeyboardButton(text='Видалити блок', callback_data='delate_stage')
delete_edit_kb = InlineKeyboardMarkup().add(delete_stream_btn).add(back_to_stream_btn)

post_formatting_kb_stage = InlineKeyboardMarkup(row_width=2)
change_text = InlineKeyboardButton(text='📝 Змінити текст', callback_data='text_change')
inlines = InlineKeyboardButton(text='Кнопки', callback_data='button_change')
media_settings = InlineKeyboardButton(text='🎞 Налаштувати медіа', callback_data='media_change')
post_now = InlineKeyboardButton(text='Час до наступного повідомлення', callback_data='time_change')
stage_change = InlineKeyboardButton(text='Блок на який перейти', callback_data='stage_change')
save_now = InlineKeyboardButton(text='Зберегти', callback_data='save_now')
delate_now = InlineKeyboardButton(text='Видалити', callback_data='delete_message')
back_to_edit_stage_btn = InlineKeyboardButton(text='« Назад', callback_data='edit_stage')
post_formatting_kb_stage.add(change_text, inlines, media_settings, post_now, save_now, delate_now, back_to_edit_stage_btn)
post_formatting_kb_stage_2 = InlineKeyboardMarkup(row_width=2)
post_formatting_kb_stage_2.add(post_now,stage_change,save_now,delate_now,back_to_edit_stage_btn)