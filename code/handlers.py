from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update
from telegram import Bot

from config import *

from db_methods import get_sorted_and_filtered_vines
from db_methods import get_comments_by_filter
from db_methods import write_new_vine
from db_methods import get_vine_by_filter
from db_methods import delete_comments_by_vine_id

from db_data_classes import Comments
from db_data_classes import Vines

from small_yandex_api import OrganisationsAPI
from small_yandex_api import StaticAPI

from services import save_image
from services import logger
from services import debug

from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode
from datetime import date
from io import BytesIO
from PIL import Image
from re import match


class DataBaseMenu:
    """Группа функций, отвечающая за просмотр информации из БД"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @debug
    def start(self, update: Update, context: CallbackContext):
        context.user_data['item_id'] = None
        context.user_data['set_id'] = 0
        context.user_data['sort_by'] = (Vines.name, False)
        self.update_vines_data(update, context)
        if context.user_data['vines']:
            context.user_data['last_message_id'] = self.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Texts.DATA_BASE_MENU_TEXT,
                reply_markup=self.get_keyboard(context),
            ).message_id
        else:
            self.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Texts.EMPTY_USER_DB
            )

    @debug
    def sort_by(self, update: Update, context: CallbackContext):
        if update.effective_message.message_id == context.user_data.get('last_message_id'):
            data = update.callback_query.data
            if data == DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_PRICE:
                sort_by = Comments.price
            elif data == DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_MARK:
                sort_by = Comments.mark
            elif data == DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_DATE:
                sort_by = Comments.date
            else:
                sort_by = Vines.name
            context.user_data['sort_by'] = (sort_by, (
                not context.user_data['sort_by'][1]) if (
                    context.user_data['sort_by'][0] == sort_by) else False)
            context.user_data['set_id'] = 0
            self.update_vines_data(update, context)
            self.update_message(update, context)
        else:
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            self.start(update, context)

    @debug
    def rewind_set(self, update: Update, context: CallbackContext):
        if update.effective_message.message_id == context.user_data.get('last_message_id'):
            data = update.callback_query.data
            if data == DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_NEXT:
                context.user_data['set_id'] += 1
            if data == DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PREVIOUS:
                context.user_data['set_id'] -= 1
            self.update_message(update, context)
        else:
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            self.start(update, context)

    @debug
    def show_item(self, update: Update, context: CallbackContext):
        if update.effective_message.message_id == context.user_data.get('last_message_id'):
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            context.user_data['item_id'] = update.callback_query.data.split('_')[-1]
            vine = get_vine_by_filter(Vines.id == int(context.user_data['item_id']))
            text = Texts.VINE_TEMPLATE.format(
                name=vine.name or '...',
                place=vine.place or '...',
                type=vine.vine_type or '...',
                variety=vine.variety or '...'
            ) + '\n'
            comments = get_comments_by_filter(Comments.vine_id == vine.id)
            for comment in comments:
                text += Texts.COMMENT_TEMPLATE.format(
                    date=comment.date or '...',
                    mark=comment.mark or '...',
                    price=comment.price or '...',
                    comm=comment.commentary or '...'
                ) + '\n'
            if vine.photo_path:
                with open(f'img/{vine.photo_path}', 'rb') as photo:
                    context.user_data['last_message_id'] = self.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        caption=text,
                        photo=photo,
                        reply_markup=self.get_keyboard(context)
                    ).message_id
            else:
                context.user_data['last_message_id'] = self.bot.send_message(
                    text=text,
                    chat_id=update.effective_chat.id,
                    reply_markup=self.get_keyboard(context)
                ).message_id
        else:
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            self.start(update, context)

    @debug
    def hide_item(self, update: Update, context: CallbackContext):
        if update.effective_message.message_id == context.user_data.get('last_message_id'):
            self.update_vines_data(update, context)
            context.user_data['item_id'] = None
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            context.user_data['last_message_id'] = self.bot.send_message(
                chat_id=update.effective_chat.id,
                text=Texts.DATA_BASE_MENU_TEXT,
                reply_markup=self.get_keyboard(context)
            ).message_id
        else:
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            self.start(update, context)

    @debug
    def delete_item(self, update: Update, context: CallbackContext):
        if update.effective_message.message_id == context.user_data.get('last_message_id'):
            delete_comments_by_vine_id(context.user_data['item_id'])
            self.hide_item(update, context)
        else:
            self.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            self.start(update, context)

    @debug
    def update_message(self, update: Update, context: CallbackContext):
        self.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reply_markup=self.get_keyboard(context)
        )

    @debug
    def update_vines_data(self, update: Update, context: CallbackContext):
        context.user_data['vines'] = get_sorted_and_filtered_vines(
            Comments.chat_id == int(update.effective_chat.id),
            *context.user_data['sort_by']
        )

    @debug
    def get_keyboard(self, context: CallbackContext):
        if context.user_data['item_id']:
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            DBMenuItemKeyboard.BUTTONS_TEXT[DBMenuItemKeyboard.CALLBACK_BUTTON_BACK],
                            callback_data=DBMenuItemKeyboard.CALLBACK_BUTTON_BACK
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            DBMenuItemKeyboard.BUTTONS_TEXT[DBMenuItemKeyboard.CALLBACK_BUTTON_DELETE],
                            callback_data=DBMenuItemKeyboard.CALLBACK_BUTTON_DELETE
                        )
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_DATE] + (
                                '' if context.user_data['sort_by'][0] != Comments.date else (
                                    DBMenuListKeyboard.UP_SYM if (
                                        context.user_data['sort_by'][1]) else DBMenuListKeyboard.DOWN_SYM)),
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_DATE
                        ),
                        InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_NAME] + (
                                '' if context.user_data['sort_by'][0] != Vines.name else (
                                    DBMenuListKeyboard.UP_SYM if (
                                        context.user_data['sort_by'][1]) else DBMenuListKeyboard.DOWN_SYM)),
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_NAME
                        ),
                        InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_PRICE] + (
                                '' if context.user_data['sort_by'][0] != Comments.price else (
                                    DBMenuListKeyboard.UP_SYM if (
                                        context.user_data['sort_by'][1]) else DBMenuListKeyboard.DOWN_SYM)),
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_PRICE
                        ),
                        InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_MARK] + (
                                '' if context.user_data['sort_by'][0] != Comments.mark else (
                                    DBMenuListKeyboard.UP_SYM if (
                                        context.user_data['sort_by'][1]) else DBMenuListKeyboard.DOWN_SYM)),
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_MARK
                        ),
                    ],
                    ([InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_NEXT],
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_NEXT
                        )] if context.user_data['set_id'] == 0 and len(context.user_data['vines']) > 5 else []),
                    [InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PREVIOUS],
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PREVIOUS
                        ),
                        InlineKeyboardButton(
                            DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_NEXT],
                            callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_NEXT
                        )] if 0 < context.user_data['set_id'] < (len(context.user_data['vines']) - 1) // 5 else [],
                    ([InlineKeyboardButton(
                        DBMenuListKeyboard.BUTTONS_TEXT[DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PREVIOUS],
                        callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PREVIOUS
                    )] if context.user_data['set_id'] >= (len(context.user_data['vines']) - 1) // 5 else []),
                    *[
                        [InlineKeyboardButton(f'{el.comment[-1].date} / {el.name} / '
                                              f'{el.comment[-1].price} / {el.comment[-1].mark}',
                                              callback_data=DBMenuListKeyboard.CALLBACK_BUTTON_ITEM.format(
                                                  el.id))]
                        for i, el in enumerate(context.user_data['vines'][5 * context.user_data['set_id']:(
                                5 * (context.user_data['set_id'] + 1))])
                    ]
                ]
            )


class AddVineConversation:
    """Группа функций, отвечающая за добаление новых записей в БД"""
    def __init__(self, bot: Bot):
        self.bot = bot

    @debug
    def start(self, update: Update, context: CallbackContext):
        if 'CHAT_ID' not in context.user_data:
            context.user_data['CHAT_ID'] = update.message.chat_id
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.ASK_FOR_FILL_WITH_BARCODE,
                reply_markup=AskForSomethingKeyboard.KEYBOARD
            )
            return 'ASK_FOR_FILL_WITH_BARCODE'
        else:
            return ConversationHandler.END

    @debug
    def ask_for_fill_with_barcode(self, update: Update, context: CallbackContext):
        self.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        data = update.callback_query.data
        if data == AskForSomethingKeyboard.CALLBACK_BUTTON_YES:
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.BARCODE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'FILL_WITH_BARCODE'
        elif data == AskForSomethingKeyboard.CALLBACK_BUTTON_NO:
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.NAME,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'NAME'

    @debug
    def fill_with_barcode(self, update: Update, context: CallbackContext):
        photo = Image.open(BytesIO(self.bot.get_file(update.message.photo.pop(-1)).download_as_bytearray()))
        decoded_objs = decode(photo, symbols=[ZBarSymbol.EAN13])
        if decoded_objs:
            code = int(decoded_objs[0].data.decode('UTF-8'))
            vine = get_vine_by_filter(Vines.barcode == code)
            if vine:
                context.user_data['VINE_ID'] = vine.id
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=Texts.FILL_WITH_BARCODE_SUCCESS,
                    reply_markup=CancelKeyboard.KEYBOARD
                )
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=Texts.DATE,
                    reply_markup=CancelKeyboard.KEYBOARD
                )
                return 'DATE'
            else:
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Не удалось найти запись с таким штрих-кодом.',
                    reply_markup=CancelKeyboard.KEYBOARD
                )
                return 'NAME'
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.BARCODE_NOT_FOUND
            )
            return 'FILL_WITH_BARCODE'

    @debug
    def name(self, update: Update, context: CallbackContext):
        context.user_data['NAME'] = update.message.text
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.VINE_TYPE,
            reply_markup=CancelKeyboard.KEYBOARD
        )
        return 'VINE_TYPE'

    @debug
    def vine_type(self, update: Update, context: CallbackContext):
        context.user_data['VINE_TYPE'] = update.message.text
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.ASK_FOR_BARCODE,
            reply_markup=AskForSomethingKeyboard.KEYBOARD
        )
        return 'ASK_FOR_BARCODE'

    @debug
    def ask_for_barcode(self, update: Update, context: CallbackContext):
        self.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        data = update.callback_query.data
        if data == AskForSomethingKeyboard.CALLBACK_BUTTON_YES:
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.BARCODE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'BARCODE'
        elif data == AskForSomethingKeyboard.CALLBACK_BUTTON_NO:
            context.user_data['BARCODE'] = ''
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.ASK_FOR_PHOTO,
                reply_markup=AskForSomethingKeyboard.KEYBOARD
            )
            return 'ASK_FOR_PHOTO'

    @debug
    def barcode(self, update: Update, context: CallbackContext):
        photo = Image.open(BytesIO(self.bot.get_file(update.message.photo.pop(-1)).download_as_bytearray()))
        decoded_objs = decode(photo, symbols=[ZBarSymbol.EAN13])
        if decoded_objs:
            code = int(decoded_objs[0].data.decode('UTF-8'))
            context.user_data['BARCODE'] = code
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.ASK_FOR_PHOTO,
                reply_markup=AskForSomethingKeyboard.KEYBOARD
            )
            return 'ASK_FOR_PHOTO'
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.BARCODE_NOT_FOUND
            )
            return 'BARCODE'

    @debug
    def ask_for_photo(self, update: Update, context: CallbackContext):
        self.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id
        )
        data = update.callback_query.data
        if data == AskForSomethingKeyboard.CALLBACK_BUTTON_YES:
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.PHOTO,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'PHOTO'
        elif data == AskForSomethingKeyboard.CALLBACK_BUTTON_NO:
            context.user_data['PHOTO'] = ''
            self.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=Texts.VARIETY,
                reply_markup=MainKeyboard.KEYBOARD
            )
            return 'VARIETY'

    @debug
    def photo(self, update: Update, context: CallbackContext):
        context.user_data['PHOTO'] = save_image(
            self.bot.get_file(update.message.photo.pop(-1)).download_as_bytearray()
        )
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.VARIETY,
            reply_markup=CancelKeyboard.KEYBOARD
        )
        return 'VARIETY'

    @debug
    def variety(self, update: Update, context: CallbackContext):
        context.user_data['VARIETY'] = update.message.text
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.PLACE,
            reply_markup=CancelKeyboard.KEYBOARD
        )
        return 'PLACE'

    @debug
    def place(self, update: Update, context: CallbackContext):
        context.user_data['PLACE'] = update.message.text
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.DATE,
            reply_markup=CancelKeyboard.KEYBOARD
        )
        return 'DATE'

    @debug
    def date(self, update: Update, context: CallbackContext):
        data = update.message.text
        try:
            if match(r'\d\d\d\d-\d\d-\d\d', data) and date(*map(int, data.split('-'))) <= date.today():
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=Texts.MARK,
                    reply_markup=CancelKeyboard.KEYBOARD
                )
                context.user_data['DATE'] = date(*map(int, data.split('-')))
                return 'MARK'
            else:
                raise ValueError
        except ValueError:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.DATE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'DATE'


    @debug
    def mark(self, update: Update, context: CallbackContext):
        data = update.message.text
        if data.isdigit() and int(data) in range(1, 11):
            context.user_data['MARK'] = int(data)
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.PRICE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'PRICE'
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.MARK,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'MARK'

    @debug
    def price(self, update: Update, context: CallbackContext):
        data = update.message.text
        if data.isdigit():
            context.user_data['PRICE'] = int(data)
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.COMM,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'COMM'
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.PRICE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'PRICE'

    @debug
    def comm(self, update: Update, context: CallbackContext):
        data = update.message.text
        if len(data) < 512:
            context.user_data['COMM'] = data
            write_new_vine(user_data=context.user_data)
            context.user_data.clear()
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.WROTE,
                reply_markup=MainKeyboard.KEYBOARD
            )
            return ConversationHandler.END
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.COMM,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'COMM'

    @debug
    def cancel(self, update: Update, context: CallbackContext):
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.END_CONVERSATION,
            reply_markup=MainKeyboard.KEYBOARD
        )
        context.user_data.clear()
        return ConversationHandler.END


class SearchByBarcode:
    """Группа функций, отвачающая за поиск вин по штрих-коду"""
    @debug
    def __init__(self, bot: Bot):
        self.bot = bot

    @debug
    def start(self, update: Update, context: CallbackContext):
        if not context.user_data.get('in_search'):
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.BARCODE,
                reply_markup=CancelKeyboard.KEYBOARD
            )
            return 'SEARCH'

    @debug
    def search(self, update: Update, context: CallbackContext):
        photo = Image.open(BytesIO(self.bot.get_file(update.message.photo.pop(-1)).download_as_bytearray()))
        decoded_objs = decode(photo, symbols=[ZBarSymbol.EAN13])
        if decoded_objs:
            context.user_data['in_search'] = True
            code = int(decoded_objs[0].data.decode('UTF-8'))
            vine = get_vine_by_filter(Vines.barcode == code)
            if vine:
                text = Texts.VINE_TEMPLATE.format(
                    name=vine.name or '...',
                    place=vine.place or '...',
                    type=vine.vine_type or '...',
                    variety=vine.variety or '...'
                ) + '\n'
                comments = get_comments_by_filter(Comments.vine_id == vine.id)
                for comment in comments:
                    text += Texts.COMMENT_TEMPLATE.format(
                        date=comment.date or '...',
                        mark=comment.mark or '...',
                        price=comment.price or '...',
                        comm=comment.commentary or '...'
                    ) + '\n'
                if vine.photo_path:
                    with open(f'img/{vine.photo_path}', 'rb') as photo:
                        self.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            caption=text,
                            photo=photo,
                            reply_markup=MainKeyboard.KEYBOARD
                        )
                else:
                    self.bot.send_message(
                        text=text,
                        chat_id=update.effective_chat.id,
                        reply_markup=MainKeyboard.KEYBOARD
                    )
                context.user_data['in_search'] = False
                return ConversationHandler.END
            else:
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Не удалось найти вино с таким штрих-кодом',
                    reply_markup=MainKeyboard.KEYBOARD
                )
                context.user_data['in_search'] = False
                return ConversationHandler.END
        else:
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.BARCODE_NOT_FOUND
            )
            return 'SEARCH'

    @debug
    def cancel(self, update: Update, context: CallbackContext):
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.END_CONVERSATION,
            reply_markup=MainKeyboard.KEYBOARD
        )
        context.user_data['in_search'] = False
        return ConversationHandler.END


class OtherFunctions:
    """Группа, объединяющая единичные функции"""
    @debug
    def __init__(self, bot: Bot):
        self.bot = bot
        self.organisations_api = OrganisationsAPI(
            apikey='dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
            text="супермаркет",
            lang="ru_RU",
            type="biz",
            results='1'
        )
        self.static_api = StaticAPI(
            l='map',
            size='450,450'
        )

    @debug
    def welcome_message(self, update: Update, _):
        self.bot.send_message(
            chat_id=update.message.chat_id,
            text=Texts.WELCOME_TEXT,
            reply_markup=MainKeyboard.KEYBOARD
        )

    @debug
    def find_near_store(self, update: Update, _):
        user_coordinates = (update.message.location.longitude, update.message.location.latitude)
        user_point = (*user_coordinates, 'pm2rdl')
        response = self.organisations_api.get(ll=','.join(map(str, user_coordinates)))
        if response:
            data = response.json()
            if response.json()['features']:
                store_coordinates = data['features'][0]['geometry']['coordinates']
                store_name = data['features'][0]['properties']['CompanyMetaData']['name']
                store_point = (*store_coordinates, 'org')
                response = self.static_api.get(
                    pt='~'.join(','.join(map(str, el)) for el in (user_point, store_point)),
                )
                if response:
                    self.bot.send_photo(
                        chat_id=update.message.chat_id,
                        photo=response.content,
                        caption=f'Ближайший магазин "{store_name}"'
                    )
                else:
                    logger.exception(f'Ошибка Yandex Static API\n{response.url}')
                    self.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=Texts.ERROR
                    )
            else:
                self.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Не удлось найти магазин рядом с вами.'
                )
        else:
            logger.exception(f'Ошибка Yandex Organisations API\n{response.url}')
            self.bot.send_message(
                chat_id=update.message.chat_id,
                text=Texts.ERROR
            )
