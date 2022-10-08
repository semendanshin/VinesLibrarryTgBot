from telegram import Bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.utils.request import Request

from config import TG_TOKEN
from config import DBMenuListKeyboard
from config import DBMenuItemKeyboard
from config import AskForSomethingKeyboard
from config import MainKeyboard
from config import CancelKeyboard

from handlers import AddVineConversation
from handlers import SearchByBarcode
from handlers import DataBaseMenu
from handlers import OtherFunctions


#  Тэг бота в телеграме - @wine_library_bot


def main():
    """Инициализация бота, заполнение хендлеров и запуск бота"""

    bot = Bot(
        token=TG_TOKEN,
        request=Request(con_pool_size=8)
    )
    updater = Updater(
        bot=bot,
        use_context=True
    )

    add_vine_conversation = AddVineConversation(bot)
    search_by_barcode = SearchByBarcode(bot)
    other_functions = OtherFunctions(bot)
    data_base_menu = DataBaseMenu(bot)

    updater.dispatcher.add_handler(
        CommandHandler('start', other_functions.welcome_message, pass_user_data=False)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.location, other_functions.find_near_store)
    )
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.text(MainKeyboard.BARCODE_SEARCH_TEXT), search_by_barcode.start),
                      CommandHandler('search_by_barcode', search_by_barcode.start)],
        states={'SEARCH': [MessageHandler(Filters.photo, search_by_barcode.search)]},
        fallbacks=[
            CommandHandler('cancel', search_by_barcode.cancel),
            MessageHandler(Filters.text(CancelKeyboard.CANCEL_TEXT), search_by_barcode.cancel)
        ],
    ))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('add_vine', add_vine_conversation.start),
            MessageHandler(Filters.text(MainKeyboard.ADD_VINE_TEXT), add_vine_conversation.start)
        ],
        states={
            'ASK_FOR_FILL_WITH_BARCODE': [
                CallbackQueryHandler(
                    callback=add_vine_conversation.ask_for_fill_with_barcode,
                    pattern=AskForSomethingKeyboard.PATTERN
                )
            ],
            'FILL_WITH_BARCODE': [
                MessageHandler(Filters.photo, add_vine_conversation.fill_with_barcode)
            ],
            'NAME': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.name
                )
            ],
            'VINE_TYPE': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.vine_type
                )
            ],
            'DATE': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.date
                )
            ],
            'VARIETY': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.variety
                )
            ],
            'PLACE': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.place
                )
            ],
            'MARK': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.mark
                )
            ],
            'PRICE': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.price
                )
            ],
            'COMM': [
                MessageHandler(
                    Filters.text & (~Filters.command) & (~Filters.text(CancelKeyboard.CANCEL_TEXT)),
                    add_vine_conversation.comm
                )
            ],
            'ASK_FOR_BARCODE': [
                CallbackQueryHandler(
                    callback=add_vine_conversation.ask_for_barcode,
                    pattern=AskForSomethingKeyboard.PATTERN
                )
            ],
            'BARCODE': [
                MessageHandler(Filters.photo, add_vine_conversation.barcode)
            ],
            'ASK_FOR_PHOTO': [
                CallbackQueryHandler(
                    callback=add_vine_conversation.ask_for_photo,
                    pattern=AskForSomethingKeyboard.PATTERN
                )
            ],
            'PHOTO': [
                MessageHandler(Filters.photo, add_vine_conversation.photo)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', add_vine_conversation.cancel),
            MessageHandler(Filters.text(CancelKeyboard.CANCEL_TEXT), add_vine_conversation.cancel)
        ],
    ))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text(MainKeyboard.VIEW_VINES_TEXT), data_base_menu.start)
    )
    updater.dispatcher.add_handler(
        CommandHandler('show_db', data_base_menu.start)
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=data_base_menu.sort_by,
            pattern=DBMenuListKeyboard.CALLBACK_BUTTON_SORT_BY_PATTERN
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=data_base_menu.rewind_set,
            pattern=DBMenuListKeyboard.CALLBACK_BUTTON_REWIND_PATTERN
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=data_base_menu.show_item,
            pattern=DBMenuListKeyboard.CALLBACK_BUTTON_ITEM_PATTERN
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=data_base_menu.hide_item,
            pattern=DBMenuItemKeyboard.CALLBACK_BUTTON_BACK
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            callback=data_base_menu.delete_item,
            pattern=DBMenuItemKeyboard.CALLBACK_BUTTON_DELETE
        )
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
