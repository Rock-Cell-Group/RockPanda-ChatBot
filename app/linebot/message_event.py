from linebot.v3.webhooks import MessageEvent, TextMessageContent, FileMessageContent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from app.config import settings
from app.langchain_module.Chat_module import ChatBOT
from app.linebot import configuration, handler
from app.logger import logger
from app.utils import POST_QUEUE, ANSWER_QUEUE
from app.services import user as user_service
import app.services.system_file as file_service
import app.services.post as post_service
from app.model import models
from app.services import redis
# lineBot文件處理器


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file_message(event):
    logger.info("Got FileMessageContent event message id: " + str(event.message.id))
    print(f"{event}")
    user_state = redis.get_user_state(event.source.user_id)
    is_update_succesful = False
    document_metadata = user_state.get(event.source.user_id)
    if document_metadata:
        # 如果有投稿資訊
        is_update_succesful = file_service.update_file_by_metadata(event)
        if is_update_succesful:
            # 若用戶成功上傳題目投稿，清除meta data狀態
            user_state[event.source.user_id] = None
            redis.save_user_state(event.source.user_id, user_state)

    # TODO 有時間可以做大型檔案檢查，因為line好像沒擋大檔案
    # is_system_file_saved = file_service.is_file_saved(event)  # 我只需要message_id "476366252647121285"
    if is_update_succesful:
        reply_text = "感謝您的文件投稿，審核後會立即通知您！"
    else:
        reply_text = "投稿失敗，請再試一次！"
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


# lineBot訊息處理器
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event != None:
        # event_to_store = str(event)
        logger.info("Got TextMessageContent event message id: " + str(event.message.id))
    print(f"{event}")
    # 檢查user是否已註冊至db內 (TODO 這是default的user insert，如果使用者有心走完資料填寫流程，那可以存到更多資訊)
    user = user_service.is_user_registered(event.source.user_id)
    if user is None:
        user = user_service.create_user(event.source.user_id)

    # 開始處理訊息內容
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Get the user's message
        user_message = event.message.text

        # 初始化cmd為null
        cmd = None
        # 我們定義的行為'/!'
        if '/' in user_message:
            split_lines = user_message.splitlines()
            if len(split_lines) > 1:
                cmd = split_lines[0]
                # user_message_content = "\n".join(split_lines[1:])
            else:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="格式有誤請重新點選！")]
                    )
                )

        # "/"傳文件資訊行為
        if cmd == "/!文件資訊":

            print(f"來自{event.source.user_id}的文件資訊，已儲存至文件id：...")
            user_message = user_message.replace("/!文件資訊", "").strip()
            document_metadata = {}
            lines = user_message.split("\n")
            for line in lines:
                key, value = line.split("=")
                document_metadata[key.strip()] = value.strip()

            # 從字典中提取課程、授課老師和類型
            course = document_metadata.get("課程")
            teacher = document_metadata.get("授課老師")
            exam_type = document_metadata.get("類型")

            if len(document_metadata) > 0:
                user_state = redis.get_user_state(event.source.user_id)
                # 將科目、教授、類別資訊暫存至全域變數或redis，等待文件上傳
                user_state[event.source.user_id] = {'subject': course, 'professor': teacher, 'exam_type': exam_type}
                redis.save_user_state(event.source.user_id, user_state)
                # saved_metadata = file_service.save_metadata_to_db(event) //TODO 如果metadata都先存到全域變數或redis，那這裡就沒必要先存到db
                # 請求使用者上傳文件
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="已登記您的文件資訊，請於一天內分享文件給我！")]
                    )
                )
            else:
                # 回覆使用者格式不正確
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="格式不正確，請再試一次！")]
                    )
                )

        # "/!投稿"行為
        elif cmd == "/!投稿":
            # TODO 檢查投稿格式
            event.message.text = "\n".join(user_message.split("\n")[1:])
            result = post_service.save_post_to_db(event)
            POST_QUEUE.enqueue(result.id)
            print(f"來自{event.source.user_id}的投稿，已儲存至id：{result.id}")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="感謝您的文字投稿，我們會盡快審核並發布！")]
                )
            )

        elif cmd == "/!feedback":
            # TODO 意見存到db。
            if user_service.append_user_column_value(event.source.user_id, "feedbacks", user_message):
                print(f"來自{event.source.user_id}的反饋，已儲存至feedbacks")
            else:
                print("儲存反饋時出現錯誤")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="感謝您的回饋，我們會盡快答覆您！")]
                )
            )

        elif cmd == "/!快速發問":
            event.message.text = "\n".join(user_message.split("\n")[1:])
            print(f"**** msg length = {len(event.message.text)}\n")
            if len(event.message.text) < 15:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="字數太少囉，請再輸入一次")]
                    )
                )
            elif len(event.message.text) > 1500:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="字數太多囉，請再輸入一次")]
                    )
                )
            else:
                result = post_service.save_question_to_db(event)
                print(f"來自{event.source.user_id}的提問，已儲存至id：{result.id}")
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="已將您的提問發布於問答平台上！")]
                    )
                )

        elif cmd == "/!我來回答":
            event.message.text = "\n".join(user_message.split("\n")[1:])
            if len(event.message.text) < 15:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="字數太少囉，請再輸入一次")]
                    )
                )
            elif len(event.message.text) > 1500:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="字數太多囉，請再輸入一次")]
                    )
                )
            else:
                result = post_service.save_answer_to_db(event)
                if result is None:  # 如果使用者亂試問題編號，會被擋
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="格式錯誤！")]
                        )
                    )
                    return
                ANSWER_QUEUE.enqueue(result.id)
                print(f"來自{event.source.user_id}的答案，已儲存至id：{result.id}")
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="感謝您的回答，我們會盡快傳送給發問者！")]
                    )
                )

        elif cmd == "/!查看全文":
            pass

        #  一般機器人問答
        else:
            # 如果是本機，就直接回覆一樣的話，以免誤用openAI的錢
            if settings.CONFIG_TYPE == "BaseConfig":
                # line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=user_message)]
                    )
                )
            # 如果是正式機，就用openAI回答
            else:
                # Call the ChatBOT module to get a response
                response = ChatBOT().retrieval_answer(user_message, "namespace", "manual")
                '''
                # Call the ChatBOT module to get a response with metadata filter
                # metadata filter usage example:
                response = ChatBOT().retrieval_answer(user_message, "namespace", "about_course") # namespace is metadata_key, about_course is metadata_value
                '''

                # Send the response back to the Line chat
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=response)]
                    )
                )
