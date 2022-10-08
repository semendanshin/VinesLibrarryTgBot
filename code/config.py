from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton


TG_TOKEN = '1724139018:AAEGBeBLgg-__WGfBxYiaaCml7AIF9RyfWg'


class Texts:
    ASK_FOR_FILL_WITH_BARCODE = 'Отлично, давайте добавим новое вино.\nЕсли вы уже писали отзыв об этом вине, то ' \
                                'можно автоматически заполнить некоторые пункты, ' \
                                'отсканировав штрих-код бутылки. Хотите?'
    FILL_WITH_BARCODE_SUCCESS = 'Отлично, осталась всего половина полей.'
    EMPTY_USER_DB = 'Необходимо сделать хотя бы одну запись.'
    NAME = 'Напишите, пожалуйста название вина.'
    VINE_TYPE = 'Хорошо, какой тип вина?'
    DATE = 'Напишите дату, когда вы его попробовали в формате ГГГГ-ММ-ДД.'
    VARIETY = 'Хорошо, а теперь сорт(а) винограда.'
    PLACE = 'Отлично, напишите место производства вина.'
    MARK = 'Оцените вино от 0 до 10.'
    PRICE = 'Сколько стоило вино в рублях?'
    COMM = 'Напишите краткий комментарий (до 512 символов).'
    ASK_FOR_BARCODE = 'Вы может сохранить штрих-код вина, чтобы в будущем быстро его находить.'
    BARCODE = 'Отлично! Пришлите мне фото штрих-кода в хорошем качестве.'
    BARCODE_NOT_FOUND = 'Никак не могу отыскать штрих-код на этой фотографии. Попробуйте прислать фото получше.'
    ASK_FOR_PHOTO = 'Хотите добавить фото?'
    PHOTO = 'Хорошо, пришлите фото.'
    WELCOME_TEXT = 'Привет!\nЯ - винный библиотекарь. Здесь ты можешь хранить информацию о винах, которые ты '\
                   'попробовал.\nНапиши /add_vine, чтобы добавить новую запись.'
    WROTE = 'Записал.'
    ERROR = 'Простите, произошла ошибка'
    END_CONVERSATION = 'Хорошо, вышел из дилога.'
    DATA_BASE_MENU_TEXT = 'Меню просмотра базы данных'
    VINE_TEMPLATE = "•Название вина - {name}\n" \
                    "•Тип - {type}\n" \
                    "•Сорт винограда - {variety}\n" \
                    "•Место производства - {place}\n"
    COMMENT_TEMPLATE = "•Дата пробы - {date}\n" \
                       "•Оценка - {mark}/10\n" \
                       "•Цена - {price} руб.\n" \
                       "•Комментарий - {comm}\n"


class AskForSomethingKeyboard:
    CALLBACK_BUTTON_YES = 'ask_for_something_callback_button_yes'
    CALLBACK_BUTTON_NO = 'ask_for_something_callback_button_no'

    PATTERN = r'ask_for_something_callback\w'

    BUTTONS_TEXT = {
        CALLBACK_BUTTON_YES: 'Да',
        CALLBACK_BUTTON_NO: 'Нет'
    }

    KEYBOARD = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    BUTTONS_TEXT[CALLBACK_BUTTON_YES],
                    callback_data=CALLBACK_BUTTON_YES
                ),
                InlineKeyboardButton(
                    BUTTONS_TEXT[CALLBACK_BUTTON_NO],
                    callback_data=CALLBACK_BUTTON_NO
                )
            ]
        ]
    )


class MainKeyboard:
    ADD_VINE_TEXT = 'Добавить 🍷'
    VIEW_VINES_TEXT = 'Просмотр 🍷'
    BARCODE_SEARCH_TEXT = 'Поиск по штрихкоду 🍷'
    NEAREST_STORE = 'Ближайший магазин'

    KEYBOARD = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(ADD_VINE_TEXT),
                KeyboardButton(VIEW_VINES_TEXT)
            ],
            [
                KeyboardButton(BARCODE_SEARCH_TEXT),
                KeyboardButton(NEAREST_STORE, request_location=True)
            ]
        ],
        one_time_keyboard=False,
        resize_keyboard=True
    )


class CancelKeyboard:
    CANCEL_TEXT = 'Отмена 🚫'
    KEYBOARD = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(CANCEL_TEXT)
            ]
        ],
        one_time_keyboard=False,
        resize_keyboard=True
    )


class DBMenuListKeyboard:
    CALLBACK_BUTTON_REWIND_PATTERN = r'show_db_menu_rewind\w'
    CALLBACK_BUTTON_REWIND_NEXT = 'show_db_menu_rewind_next'
    CALLBACK_BUTTON_REWIND_PREVIOUS = 'show_db_menu_rewind_previous'

    CALLBACK_BUTTON_SORT_BY_PATTERN = r'show_db_menu_sort_by\w'
    CALLBACK_BUTTON_SORT_BY_PRICE = 'show_db_menu_sort_by_price'
    CALLBACK_BUTTON_SORT_BY_MARK = 'show_db_menu_sort_by_mark'
    CALLBACK_BUTTON_SORT_BY_DATE = 'show_db_menu_sort_by_date'
    CALLBACK_BUTTON_SORT_BY_NAME = 'show_db_menu_sort_by_name'

    CALLBACK_BUTTON_ITEM_PATTERN = r'show_db_menu_item\w'
    CALLBACK_BUTTON_ITEM = 'show_db_menu_item_{}'

    UP_SYM = '⬆️'
    DOWN_SYM = '⬇️'

    BUTTONS_TEXT = {
        CALLBACK_BUTTON_REWIND_NEXT: 'Следующие',
        CALLBACK_BUTTON_REWIND_PREVIOUS: 'Предыдущие',
        CALLBACK_BUTTON_SORT_BY_PRICE: 'Цена',
        CALLBACK_BUTTON_SORT_BY_MARK: 'Оценка',
        CALLBACK_BUTTON_SORT_BY_DATE: 'Дата',
        CALLBACK_BUTTON_SORT_BY_NAME: 'Название',
    }


class DBMenuItemKeyboard:
    CALLBACK_BUTTON_BACK = 'show_item_back'
    CALLBACK_BUTTON_DELETE = 'show_item_delete'
    BUTTONS_TEXT = {
        CALLBACK_BUTTON_BACK: 'Назад',
        CALLBACK_BUTTON_DELETE: 'Удалить все отзывы'
    }


LOGGING = {
    'disable_existing_loggers': True,
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(module)s.%(funcName)s | %(asctime)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
