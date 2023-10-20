from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from app.services import user as user_service
from app.linebot import configuration, handler
from app.logger import logger


# 檢查剛加入好友的user是否已註冊至db內，然後加入 (TODO 這是default的user insert，如果使用者有心走完資料填寫流程，那可以存到更多資訊)
@handler.add(FollowEvent)
def handle_follow(event):
    user = user_service.is_user_registered(event.source.user_id)
    if user is None:
        user = user_service.create_user(event.source.user_id)
    # user_id = event.source.user_id
    # user.insertOne(user_id)
    logger.info("Got Follow event:" + event.source.user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        welcome_text = '''我是清華大助教，會出考卷也會複習教學內容，如果有我題庫及知識庫中沒有的知識歡迎上傳給我，為您建立個人化資料庫。'''
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome_text)]
            )
        )
