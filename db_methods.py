from db_session import global_init, create_session
from db_data_classes import Vines, Comments
from typing import Any
from services import debug


global_init('vines.sqlite3')


@debug
def write_new_vine(user_data: dict) -> None:
    """Запись нового вина и/или комментария о нём"""
    db_sess = create_session()
    new_vine = Vines()
    if not user_data.get('VINE_ID'):
        new_vine.name = user_data['NAME']
        new_vine.variety = user_data['VARIETY']
        new_vine.vine_type = user_data['VINE_TYPE']
        new_vine.place = user_data['PLACE']
        new_vine.photo_path = user_data['PHOTO']
        new_vine.barcode = user_data['BARCODE']
        db_sess.add(new_vine)
        db_sess.commit()
        vine_id = new_vine.id
    else:
        vine_id = user_data.get('VINE_ID')
    new_comment = Comments()
    new_comment.vine_id = vine_id
    new_comment.chat_id = user_data['CHAT_ID']
    new_comment.date = user_data['DATE']
    new_comment.price = user_data['PRICE']
    new_comment.mark = user_data['MARK']
    new_comment.commentary = user_data['COMM']
    db_sess.add(new_comment)
    db_sess.commit()


@debug
def get_sorted_and_filtered_vines(filter_by: Any, sort_by: Any, sort_direction: bool) -> list[Comments]:
    """Возвращает вино и комметарии, относящиеся к нему, по фильтру"""
    db_sess = create_session()
    return db_sess.query(Vines).outerjoin(Comments).filter(filter_by)\
        .order_by(sort_by if sort_direction else sort_by.desc()).all()


@debug
def get_vine_by_filter(filter_by: Any) -> Vines:
    """Возвращает запись о вине по фильру"""
    db_sess = create_session()
    return db_sess.query(Vines).filter(filter_by).first()


@debug
def get_comments_by_filter(filter_by: Any) -> list[Comments]:
    """Возвращет комметраий по фильтру"""
    db_sess = create_session()
    return db_sess.query(Comments).filter(filter_by).order_by(Comments.date.desc()).all()


@debug
def delete_comments_by_vine_id(vine_id: int) -> None:
    """Удаляет все комментарии о вине"""
    db_sess = create_session()
    for el in db_sess.query(Comments).filter(Comments.vine_id == vine_id).all():
        db_sess.delete(el)
    db_sess.commit()
