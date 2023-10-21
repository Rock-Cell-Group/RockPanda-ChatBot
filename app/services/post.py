from contextlib import contextmanager

from linebot.v3.messaging import MessagingApi, ApiClient, TextMessage, BroadcastRequest, PushMessageRequest
from sqlalchemy import desc, func

from app.linebot import configuration
from app.model import models
from app.model.database import SessionLocal
from app.utils import POST_QUEUE, ANSWER_QUEUE


# Function to get the database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_question_to_db(event):
    with get_db() as db:
        new_post = models.Posts(
            poster_uid=event.source.user_id,
            raw_text=event.message.text,
            post_type=event.message.type,
            post_id=event.message.id,
            tags=0  # 0:問答專區(提問) 1:問答專區(回答) 2:系統問題 3:投稿
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post


def save_answer_to_db(event):
    with get_db() as db:
        # 檢查回答的問題是否存在
        question_instance = db.query(models.Posts).filter(
            (event.message.text.split("建議答案：")[0][5:] == models.Posts.id)
            & (models.Posts.status != 'DELETED') & (models.Posts.tags == 0)
        ).first()
        if question_instance is None:
            return None
        # 檢查完才存入db
        new_post = models.Posts(
            poster_uid=event.source.user_id,
            raw_text=event.message.text,
            post_type=event.message.type,
            post_id=event.message.id,
            tags=1,  # 0:問答專區(提問) 1:問答專區(回答) 2:系統問題 3:投稿
            origin_msg_id=event.message.text.split("建議答案：")[0][5:],
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post


def get_my_question_list(user_id):
    with get_db() as db:
        question_list = db.query(models.Posts).filter(
            (models.Posts.poster_uid == user_id) & (models.Posts.status != 'DELETED') & (models.Posts.tags == 0)
        ).order_by(func.random()).limit(10).all()  # 隨機10筆
        return question_list


def get_all_question_list():
    with get_db() as db:
        question_list = db.query(models.Posts).filter(
            (models.Posts.status != 'DELETED') & (models.Posts.tags == 0)
        ).order_by(func.random()).limit(10).all()  # 隨機10筆
    return question_list


def get_question_by_id(question_id):
    with get_db() as db:
        question = db.query(models.Posts).filter(models.Posts.id == question_id).first()
        return question


def delete_question_by_id(question_id):
    with get_db() as db:
        question = db.query(models.Posts).filter(models.Posts.id == question_id).first()
        question.status = 'DELETED'
        db.commit()
        db.refresh(question)
        return question


def save_post_to_db(event):
    with get_db() as db:
        new_post = models.Posts(
            # 先放這些好像就夠整個機制運作了
            poster_uid=event.source.user_id,
            raw_text=event.message.text,
            post_type=event.message.type,
            post_id=event.message.id,
            tags=3  # 0:問答專區(提問) 1:問答專區(回答) 2:系統問題 3:投稿
        )
        """
        type='message'
        source=UserSource(type='user', user_id='U4df6a2535fcae2dc9277c39aec86ca66')
        timestamp=1696510062549 mode=<EventMode.ACTIVE: 'active'>
        webhook_event_id='01HBZY2CEH1X18QWSD0BE4563Y'
        delivery_context=DeliveryContext(is_redelivery=False)
        reply_token='b8de1ad34f4d458ba809b15d112afdb4'
        message=TextMessageContent(
                        type='text',
                        id='475933980647227698',
                        text='阿',
                        emojis=None,
                        mention=None,
                        quote_token='FRFluR9XUTXMGz7fwz2emx1UZ57tFl9eI5T1gA28L1WdjcF9geaOm0s6G-HS4BLQkCFl9yVXcTfIg3NDKXzJh-9OtbknGt58j2zR1fQDqVR-VqHHXtojfxsHgxX4ptbv-a8TGO7OhqiRKkxPfbBYsw',
                        quoted_message_id=None
                        )
        """
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post


def post_to_line(queue):
    message = POST_QUEUE.dequeue()
    if message is not None:
        # post to line user who subscribe the bot

        with get_db() as db:
            post = db.query(models.Posts).filter(models.Posts.id == message).first()
            print("即將發布以下投稿")
            # print(post.post_type)
            print(post.raw_text)

            # DONE 推播給所有訂閱這個bot的user
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.broadcast_with_http_info(
                    BroadcastRequest(
                        messages=[
                            TextMessage(
                                type=post.post_type,
                                text=post.raw_text + f"\n投稿時間:{post.create_at}\n發布時間:{post.modify_at}"
                            )
                        ]
                    )
                )

        return {"message": f"{message} has been dequeued."}
    else:
        return {"message": "Queue is empty."}


def answer_to_poster(queue):
    message = ANSWER_QUEUE.dequeue()
    if message is not None:
        # post to line user who subscribe the bot

        with get_db() as db:
            post = db.query(models.Posts).filter(models.Posts.id == message).first()
            print("即將推播以下回應")
            print(post.raw_text)
            # 找出該問題的origin_msg_id (key)搜尋RAG_POST.id 原始問題的編號
            # 抓到該原始問題的poster_uid 作為reply_uid
            origin_question_id = post.origin_msg_id # 原始問題的編號，以此尋找提問者
            questioner_post = db.query(models.Posts).filter(models.Posts.id == origin_question_id).first()
            
            reply_uid = questioner_post.poster_uid
            print(f"原始發問者id : {reply_uid}")

            # 推播給發問者
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message_with_http_info(
                    PushMessageRequest(
                        to=reply_uid,
                        messages=[
                            TextMessage(
                                type=post.post_type,
                                text=post.raw_text + f"\n回答時間:{post.create_at}\nby 匿名的善心人士"
                            )
                        ]
                    )
                )

        return {"message": f"{message} has been dequeued."}
    else:
        return {"message": "Queue is empty."}
