from linebot.v3.webhooks import PostbackEvent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, TemplateMessage, \
    FlexMessage, FlexCarousel, FlexBubble
from app.linebot import configuration, handler
from app.logger import logger
from app.linebot.fetchQuestion.quick_reply_wrapper import JSON_formated_content as quick_replys
from app.linebot.fetchQuestion.buttons_template import JSON_formated_content as buttons_templates
from app.linebot.fetchQuestion.flex_carousel_wrapper import JSON_formated_content as flex_carousels
from app.linebot.question_forum.template import JSON_formated_content as question_forum_templates
from app.model import models
from app.services import user as user_service
from app.services import post as post_service
from app.services import system_file as file_service
from app.services import questions as questions_service
from app.services.post import get_my_question_list, get_all_question_list
from app.langchain_module.Chat_module import ChatBOT
from app.services.redis import use_credit


# Define a function to handle LineBot postback events
@handler.add(PostbackEvent)
def handle_postback_event(event):
    data = event.postback.data

    if data:
        handle_postback_data(event, data)
    else:
        logger.info("No valid data in the postback event")


def handle_postback_data(event, data):
    line_bot_api = get_line_bot_api()

    print("----------\nHERE is EVENT:\n", event)
    print("----------\nHERE is DATA:\n", data)

    # A功能 生成考題
    if 'action=fetchQuestion' in data:
        handle_fetch_question_postback(event, line_bot_api)
    elif 'action=select_course' in data:
        handle_select_course_postback(event, data, line_bot_api)
    elif 'action=select_question_professor' in data:
        handle_select_professor_postback(event, data, line_bot_api)
    elif 'action=select_question_exam_type' in data:
        handle_select_exam_type_postback(event, data, line_bot_api)
    elif 'action=generate_similar_question' in data:
        if use_credit(event.source.user_id):
            handle_generate_similar_question_postback(event, data, line_bot_api)
        else:
            handle_no_credit_postback(event, line_bot_api)
    elif 'action=answer_to_db_question' in data:
        if use_credit(event.source.user_id):
            handle_answer_to_db_question_postback(event, data, line_bot_api)
        else:
            handle_no_credit_postback(event, line_bot_api)
    elif 'action=return_question_text' in data:
        handle_return_question_text_postback(event, line_bot_api)
    elif 'action=answer_to_AI_question' in data:
        if use_credit(event.source.user_id):
            handle_answer_to_AI_question_postback(event, line_bot_api)
        else:
            handle_no_credit_postback(event, line_bot_api)
    # B功能 貢獻文件
    elif 'action=contributeDocDB' in data:
        handle_contribute_doc_db_postback(event, line_bot_api)
    elif 'action=uploadDocument' in data:
        handle_upload_document_postback(event, line_bot_api)
    elif 'action=checkUploadStatus' in data:
        handle_check_upload_status_postback(event, line_bot_api)
    # C 功能 發現新功能
    elif 'action=findnew_feature' in data:
        handle_findnew_feature(event, line_bot_api)
    # D功能 答題
    elif 'action=question_forum' in data:
        handle_question_forum(event, line_bot_api)
    elif 'action=list_all_question' in data:
        handle_list_all_question_postback(event, line_bot_api)
    elif 'action=list_my_question' in data:
        handle_list_my_question_postback(event, line_bot_api)
    elif 'action=create_question' in data:
        handle_create_question_postback(event, line_bot_api)
    elif 'action=delete_question&question_id=' in data:
        handle_delete_question_postback(event, line_bot_api)
    elif 'action=show_all_text&question_id=' in data:
        handle_show_all_text_postback(event, line_bot_api)
    elif 'action=response_question' in data:
        handle_response_question_postback(event, line_bot_api)
    # E功能 投稿一則快訊
    elif 'action=commit_post' in data:
        handle_commit_post_postback(event, line_bot_api)
    # F功能 填寫反饋
    elif 'action=commit_feedback' in data:
        handle_commit_feedback_postback(event, line_bot_api)
    else:
        logger.info("Unhandled postback event with data: " + data)


def get_line_bot_api():
    with ApiClient(configuration) as api_client:
        return MessagingApi(api_client)


# Define functions for each action

def handle_no_credit_postback(event, line_bot_api):
    """
    # 'action=no_credit'
    # 如果使用者已用完今日額度，則回傳此訊息
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="您今日的額度已用完，請明日再來使用本服務。")]
        )
    )


def handle_fetch_question_postback(event, line_bot_api):
    """
    # 'action=fetchQuestion'
    # A功能：查詢題目-> 選項式
    """
    # 這一步驟每次執行都會從db撈最新的科目按鈕。好像也只能這樣
    # 以下是action=fetchQuestion觸發的
    if len(file_service.get_column_value_set(models.FileSystem, "question_course")) == 0:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="資料庫中沒搜尋到任何課程")]
            )
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage.from_dict(
                    quick_replys.get_course_quick_reply_dict(models.FileSystem, "question_course"))]
            )
        )


def handle_select_course_postback(event, data, line_bot_api):
    """
    # 'action=select_course'
    # A功能：查詢題目 -> 選項式 -> 選擇科目
    """
    selected_course_value = data.split("@")[1]
    condition = [("question_course", selected_course_value)]
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage.from_dict(quick_replys.get_quick_reply_dict_by_former(
                models.FileSystem, condition, "question_professor"))]
        )
    )
    # 告訴資料庫他選了甚麼課程
    user_service.commit_user_new_column_value(event.source.user_id, "last_postback_course_reply", selected_course_value)


def handle_select_professor_postback(event, data, line_bot_api):
    """
    # 'action=select_question_professor'
    # A功能：查詢題目 -> 選項式 -> 選擇科目 -> 選擇教授
    """
    previous_selected_course = user_service.get_user_column_value(event.source.user_id, "last_postback_course_reply")
    selected_professor_value = data.split("@")[1]
    condition = [("question_course", previous_selected_course), ("question_professor", selected_professor_value)]
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage.from_dict(quick_replys.get_quick_reply_dict_by_former(
                models.FileSystem, condition, "question_exam_type"))]
        )
    )
    # 告訴資料庫他選了甚麼教授
    user_service.commit_user_new_column_value(event.source.user_id, "last_postback_professor_reply",
                                              selected_professor_value)


def handle_select_exam_type_postback(event, data, line_bot_api):
    """
    # 'action=select_question_exam_type'
    # A功能：查詢題目 -> 選項式 -> 選擇科目 -> 選擇教授 -> 選擇考試類型
    """
    previous_selected_course = user_service.get_user_column_value(event.source.user_id, "last_postback_course_reply")
    previous_selected_professor = user_service.get_user_column_value(event.source.user_id, "last_postback_professor_reply")
    selected_exam_type_value = data.split("@")[1]
    condition = [("question_course", previous_selected_course), ("question_professor",previous_selected_professor), ("question_exam_type",selected_exam_type_value)]
    fileIDs = file_service.get_column_value_set_by_conditions(models.FileSystem, condition, "id")
    questionIDs = questions_service.get_random_k_question_ids_by_fileIDs(fileIDs, 3) # 這邊的3就是隨機選幾題
    if questionIDs:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text=f"題目查詢結果",
                        contents=FlexCarousel(
                            contents=flex_carousels().wrapping_bubbles_in_carousel_content_list(questionIDs)
                        )
                    )
                ]
            )
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="資料庫中找不到此檔案的任何問題")]

            )
        )


    # 告訴資料庫他選了甚麼考試類型
    user_service.commit_user_new_column_value(event.source.user_id, "last_postback_exam_type_reply",
                                              selected_exam_type_value)


# 從舊題目生成新題目
def handle_generate_similar_question_postback(event, data, line_bot_api):
    question_id = data.split("@")[1]
    original_question = questions_service.get_column_value_by_question_id(question_id, "raw_text")
    new_question = ChatBOT().generate_similar_question(original_question)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                FlexMessage(
                    alt_text=f"AI生成的類似題目",
                    contents=FlexBubble.from_dict(flex_carousels().get_question_bubble_dict_by_user_id(new_question, event.source.user_id)
                    )
                )
            ]
        )
    )
    # 告訴資料庫他剛剛生成的新題目
    user_service.commit_user_new_column_value(event.source.user_id, "last_generated_question", new_question)


# 回答舊題目
def handle_answer_to_db_question_postback(event, data, line_bot_api):
    question_id = data.split("@")[1]
    original_question = questions_service.get_column_value_by_question_id(question_id, "raw_text")
    explanation = ChatBOT().answer_to_this_question(original_question)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=explanation)]
        )
    )

# 把生成的題目丟回給他讓他複製
def handle_return_question_text_postback(event, line_bot_api):
    last_generated_question = user_service.get_user_column_value(event.source.user_id, "last_generated_question")
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=last_generated_question)]
        )
    )

# 回答生成出的新題目
def handle_answer_to_AI_question_postback(event, line_bot_api):
    last_generated_question = user_service.get_user_column_value(event.source.user_id, "last_generated_question")
    explanation = ChatBOT().answer_to_this_question(last_generated_question)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=explanation)]
        )
    )



def handle_contribute_doc_db_postback(event, line_bot_api):
    """
    # 'action=contributeDocDB'
    # B功能：貢獻文件
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TemplateMessage.from_dict(buttons_templates.bottoms_2)]
        )
    )


def handle_upload_document_postback(event, line_bot_api):
    """
    # 'action=uploadDocument'
    # B功能：貢獻文件 -> 上傳文件
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text='''先填資訊 → 再傳文件
    -------資訊格式--------
    /!文件資訊
    課程=程式設計一
    授課老師=聘任中
    類型=第二次期中考
    -----上傳檔案的方法-----
      1. 將文件儲存至您的LINE keep
      2. 至LINE keep將該文件以分享的方式分享至此聊天室(清華大助教)
    ----------------------
    完成後請靜候審核通知''')]
        )
    )


def handle_check_upload_status_postback(event, line_bot_api):
    """
    # 'action=checkUploadStatus'
    # B功能：貢獻文件 -> 查詢先前上傳狀態
    type='message'
    source=UserSource(type='user', user_id='Ua3b11ac6aa2b65baee995dc7a1d95c72') 
    timestamp=1697377046793 
    mode=<EventMode.ACTIVE: 'active'> 
    webhook_event_id='01HCSRWMH57B6Y2KK7VGFBCAFH' 
    delivery_context=DeliveryContext(is_redelivery=False) 
    reply_token='9cca239077024f148a0fdd7e03eac2f4' 
    message=TextMessageContent(type='text',
         id='477388538766164195',
           text='查詢先前上傳結果',
             emojis=None, 
             mention=None, 
             quote_token='EDodXA1Y3zpMs3L__FmuwnXTy1FN0APf_-XC5gXUieGYtfmVCed0Dgq_BSVwGRKBypfxxGe_U4QFdhxrAyn-QFnx3yinxxdIM9Ee3hzovjluvrXKU8hQvxkFylk-qneupLEm4VDxjdPJB5oJ-zxQ7w',
               quoted_message_id=None)
    """
    print(f"查詢上傳檔案狀態 Event : {event}")
    user_id = event.source.user_id
    conditions = [("user_id", user_id),]
    uploaded_files = file_service.get_column_value_set_by_conditions(models.FileSystem, conditions)
    status_msg = "以下是您上傳過的文件狀態：\n"
    try:
        if len(uploaded_files) > 0:
            for i, file_status in enumerate(uploaded_files):
                status_msg += f"\n{i+1}. 文件: {file_status.file_name}\n    審核狀態: {'已審核通過' if file_status.censor_status else '尚未審核' }。\n"
        else:
            status_msg += "您尚未上傳過文件。\n"

    except Exception as e:
        print(f"Error in handle_check_upload_status_postback(): {e}")
        return None

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=status_msg)]
        )
    )

def handle_findnew_feature(event, line_bot_api):
    """
    # 'action=commit_feedback'
    # C功能：發現新功能
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="目前還沒有什麼有趣的功能喔，但是我們會持續更新和改善系統，敬請期待！")]
        )
    )


def handle_question_forum(event, line_bot_api):
    """
    # 'action=question_forum'
    # D功能：問題討論區
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TemplateMessage.from_dict(question_forum_templates.bottoms_1)]
        )
    )


def handle_list_all_question_postback(event, line_bot_api):
    """
    # 'action=list_all_question'
    # D功能：問題討論區 -> 我是學霸
    """
    # 取得所有使用者的所有提問
    all_question_list = get_all_question_list()
    all_question_flex_bubbles_list = []
    if len(all_question_list) == 0:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(
                    text='目前還沒有人提問過哦!'
                )]
            )
        )

    else:
        for question in all_question_list:
            title = question.raw_text.split("問題：")[0][3:]
            content = question.raw_text.split("問題：")[1]
            all_question_flex_bubbles_list.append(
                FlexBubble.from_dict(
                    question_forum_templates().get_open_question_bubble_dict(
                        f'{title}',
                        f'{content}',
                        f'提問時間：{question.create_at.strftime("%Y-%m-%d %H:%M:%S")}',
                        # f'https://line.me/ti/p/~@524repmb',
                        str(question.id)
                    )
                )
            )

        # 將所有提問包裝成flex carousel
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text=f"query record: column",
                        contents=FlexCarousel(
                            contents=all_question_flex_bubbles_list
                        )
                    )
                ]
            )
        )


def handle_response_question_postback(event, line_bot_api):
    """
    # 'action=response_question'
    # D功能：問題討論區 -> 我是學霸 -> 我來回答
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(
                text='- - - - - - 填寫範例 - - - - - '
                     '-\n/!我來回答\n問題編號：666\n'
                     '建議答案：機器學習是一種人工智慧技術，它使機器能夠通過從數據中學習和改進，'
                     '而不需要明確的編程。通過統計和算法，機器學習使機器能夠自動識別模式，做出預測和做出決策，'
                     '廣泛應用於圖像識別、自然語言處理和預測分析等領域。\n- - - - - - - - - - - - - - - - - - - -')]
        )
    )


def handle_list_my_question_postback(event, line_bot_api):
    """
    # 'action=list_my_question'
    # D功能：問題討論區 -> 我是學渣
    """

    # 取得該使用者的所有提問
    my_question_list = get_my_question_list(event.source.user_id)
    my_question_flex_bubbles_list = []
    if len(my_question_list) == 0:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(
                    text='您目前還沒提問過哦!'
                )]
            )
        )
        
    else:
        for question in my_question_list:
            title = question.raw_text.split("問題：")[0][3:]
            content = question.raw_text.split("問題：")[1]
            my_question_flex_bubbles_list.append(
                FlexBubble.from_dict(
                    question_forum_templates().get_my_question_bubble_dict(
                        f'{title}',
                        f'{content}',
                        f'提問時間：{question.create_at.strftime("%Y-%m-%d %H:%M:%S")}',
                        str(question.id)
                    )
                )
            )

        # 將所有提問包裝成flex carousel
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text=f"query record: column",
                        contents=FlexCarousel(
                            contents=my_question_flex_bubbles_list
                        )
                    )
                ]
            )
        )


def handle_create_question_postback(event, line_bot_api):
    """
    # 'action=list_my_question'
    # D功能：問題討論區 -> 快速發問
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(
                text='- - - - - - 填寫範例 - - - - - -\n/!快速發問\n領域：機器學習\n問題：甚麼是機器學習?\n- - - - - - - - - - - - - - - - - - - -')]
        )
    )


def handle_delete_question_postback(event, line_bot_api):
    """
    # 'action=delete_question&question_id='
    # D功能：問題討論區 -> 我是學渣 -> 刪除問題
    """
    deleted_question = post_service.delete_question_by_id(event.postback.data.split("=")[2])
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="該提問已成功刪除")]
        )
    )


def handle_show_all_text_postback(event, line_bot_api):
    """
    # 'action=show_all_text&question_id='
    # D功能：問題討論區 -> 我是學渣 -> 點擊問題
    """
    question_instance = post_service.get_question_by_id(event.postback.data.split("=")[2])
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=question_instance.raw_text.split("問題：")[1])]
        )
    )


def handle_commit_post_postback(event, line_bot_api):
    """
    # 'action=commit_post'
    # E功能：投稿一則快訊
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text='''***不傳播謠言和假訊息***
    我們歡迎您在我們的平台上參與互動，並分享您的觀點和觀點。為了維護一個安全、健康的平台，我們要求您遵守以下原則：

        1. 不散播謠言和假訊息： 請不要故意傳播假訊息、不實傳言或未經核實的消息。發布假訊息可能會誤導他人並造成不必要的恐慌或混淆。
        2. 事實核實： 在發布訊息之前，請確保您的內容基於可靠的事實和準確的訊息來源。不要發布未經證實的傳聞或不實陳述。
        3. 隱私尊重： 請尊重他人的隱私和個人訊息。不要散布他人的私人訊息，包括但不限於電話號碼、地址、電子郵件地址等。
        4. 法律遵守： 您應當遵守所有適用的法律和法規。散布假訊息可能會觸犯法律，您將對自己的行為承擔法律責任。
        5. 舉報假訊息： 如果您認為在我們的平台上發現了假訊息，請及時舉報。我們將積極處理假訊息舉報，並采取適當的措施。

    我們將盡最大努力確保我們的平台免受假訊息的侵害，同時也希望每位用戶能夠共同維護一個真實可信的社區環境。感謝您的合作，共同努力防止假訊息的傳播。''')]
        )
    )


def handle_commit_feedback_postback(event, line_bot_api):
    """
    # 'action=commit_feedback'
    # F功能：填寫反饋
    """
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="任何使用上的問題或意見都可以提出呦，說吧說吧")]
        )
    )