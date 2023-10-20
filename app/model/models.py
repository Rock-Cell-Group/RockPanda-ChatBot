from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, Boolean, String, DateTime, Enum, Index
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Users(Base):
    __tablename__ = 'RAG_USER'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), unique=True, default='')  # event.source.user_id
    openai_api_key = Column(String(255), default='')

    status = Column(String(255), default='active')
    post_count = Column(Integer, default=5)  # 一天最多發文數 TODO 再寫一個排程去重置
    follow_groups = Column(BigInteger, default=0)
    # 010 = 3，用bitmap存 2^0 (乞丐超人), 2^1 (校安類), 2^2 (C類) 2^3, 2^4, 2^5, 2^6, 2^7

    last_chat_category = Column(String(255))
    last_chat_status = Column(String(255))
    last_chat_content = Column(String(255))
    last_chat_reply = Column(String(255))

    last_postback_course_reply = Column(String(255))  # 存last postback course
    last_postback_professor_reply = Column(String(255))  # 存last postback professor
    last_postback_exam_type_reply = Column(String(255))  # 存last postback exam_type
    last_generated_question = Column(LONGTEXT, default="") # 存上一次生成的相似題目，用來再生成下一個相似題目或是問答案用的
    feedbacks = Column(String(255))  # 存用戶給的反饋(可能有多則，用/分)

    create_at = Column(DateTime, default=func.now())
    modify_at = Column(DateTime, default=func.now(), onupdate=func.current_timestamp())

    note = Column(String(255), default='')

    group_id = Column(String(255))
    user_name = Column(String(255), default='')
    first_name = Column(String(255), default='')
    last_name = Column(String(255), default='')
    is_ban = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    prefer_anonymous = Column(Boolean)
    notification = Column(Boolean, default=True)
    accept_count = Column(Integer)
    reject_count = Column(Integer)
    expired_post_count = Column(Integer)
    review_count = Column(Integer)
    experience = Column(BigInteger)
    level = Column(Integer)
    private_chat_id = Column(String(255), default=-1)

    def __repr__(self):
        if not self.username:
            return f'{self.fullname}(#{self.userid})'
        else:
            return f'{self.fullname}(@{self.username})'

    def HtmlUserLink(self):
        nick = self.EscapedFullName()
        if not self.username:
            return f'<a href="tg://user?id={self.userid}">{nick}</a>'
        else:
            return f'<a href="https://t.me/{self.username}">{nick}</a>'

    def EscapedFullName(self):
        return self.fullname.escape_html()


class Posts(Base):
    __tablename__ = 'RAG_POST'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_text = Column(String(2000), default="")  # event.message.text
    post_type = Column(String(255), default='Unknown')  # event.message.type
    poster_uid = Column(String(255), default=-1)  # event.source.user_id
    post_id = Column(String(255), default=-1)  # event.message.id
    create_at = Column(DateTime, default=func.now())
    modify_at = Column(DateTime, default=func.now(), onupdate=func.current_timestamp())
    tags = Column(Integer)  # 0:問答專區(提問) 1:問答專區(回答) 2:系統問題 3:投稿 # TODO 這個欄位要使用enum
    note = Column(String(255), default='')
    origin_msg_id = Column(String(255), default=-1)  # answer要推播前，這裡存的question id可以用來檢查post是否合法(未被刪除&&tags=0)

    origin_chat_id = Column(String(255), default=-1)
    origin_action_chat_id = Column(String(255), default=-1)
    origin_action_msg_id = Column(String(255), default=-1)
    review_chat_id = Column(String(255), default=-1)
    review_msg_id = Column(String(255), default=-1)
    review_action_chat_id = Column(String(255), default=-1)
    review_action_msg_id = Column(String(255), default=-1)
    public_msg_id = Column(String(255), default=-1)
    warn_text_id = Column(String(255), default=-1)
    anonymous = Column(Boolean)
    text = Column(String(2000), default="")
    channel_id = Column(String(255), default=-1)
    channel_msg_id = Column(String(255), default=-1)
    status = Column(String(255), default='Unknown')
    origin_media_group_id = Column(String(255), default="")
    review_media_group_id = Column(String(255), default="")
    publish_media_group_id = Column(String(255), default="")

    has_spoiler = Column(Boolean)
    reject_reason = Column(String(255), default="")
    count_reject = Column(Boolean)
    reviewer_uid = Column(BigInteger, default=-1)


class Dialogue(Base):
    __tablename__ = 'RAG_DIALOGUE'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_node = Column(String(255), default="")
    create_at = Column(DateTime, default=func.now())
    note = Column(String(255), default="")
    dialogue_type = Column(String(255), default="")  # callback or reply

    # callback destination
    dialogue_destination = Column(String(255), default="")

    # callback event
    event_type = Column(String(255), default="")
    event_webhook_event_id = Column(String(255), default="")
    # event_delivery_context = Column(String(255), default="") # deprecated
    event_timestamp = Column(String(255), default="")
    event_source_type = Column(String(255), default="")
    event_source_user_id = Column(String(255), default="")
    event_reply_token = Column(String(255), default="")
    event_mode = Column(String(255), default="")

    # callback event message 文字 new column
    message_type = Column(String(255), default="")
    message_id = Column(String(255), default="")
    message_quote_token = Column(String(255), default="")
    message_text = Column(String(255), default="")

    # callback event message 貼圖 new column
    message_sticker_id = Column(String(255), default="")
    message_package_id = Column(String(255), default="")
    message_sticker_resource_type = Column(String(255), default="")

    # callback event message 圖片 new column
    message_content_provider_type = Column(String(255), default="")

    # callback event message 影片 new column
    # TODO 有需要再開

    # callback event message 音訊 new column
    # TODO 有需要再開

    # callback event message 檔案 new column
    message_file_name = Column(String(255), default="")
    message_file_size = Column(String(255), default="")
    message_file_extension = Column(String(255), default="")  # parsing from file_name，失敗就留空
    message_file_content_provider_type = Column(String(255), default="")

    # callback event message 圖片、影片、音訊、檔案 會需要去打API要檔案，所以要有個file_id
    file_id = Column(BigInteger)

    # reply event new column # TODO 有需要再把callback跟reply分開
    message_emojis = Column(String(255), default="")
    message_mention = Column(String(255), default="")
    message_quoted_message_id = Column(String(255), default="")

    # report censorship
    is_dialogue_useful = Column(Boolean)  # 使用者回傳這則對話是否有用
    manager_id = Column(String(255), default="")
    manager_comment = Column(String(255), default="")
    is_manager_read = Column(Boolean)


class FileSystem(Base):
    def __getitem__(self, field):
        return self.__dict__[field]

    __tablename__ = 'RAG_FILE_SYSTEM'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), default="")
    file_name = Column(String(255), default="")
    file_path = Column(String(255), default="")
    file_size = Column(String(255), default="")
    file_extension = Column(String(255), default="")
    file_status = Column(String(255), default="")
    create_at = Column(DateTime, default=func.now())
    note = Column(String(255), default="")

    # 開AZURE_BLOB儲存空間欄位
    uuid_name = Column(String(255), default="")
    azure_container_name = Column(String(255), default="")
    azure_blob_name = Column(String(255), default="")

    # 檔案審查欄位
    file_purpose = Column(String(255), default="")  # 檔案目的： question:考題上傳 knowledge：專科知識上傳 others：其他
    is_file_useful = Column(Boolean)  # 管理者審核這個檔案是否有用
    manager_id = Column(String(255), default="")
    manager_comment = Column(String(255), default="")
    censor_status = Column(Integer, default=0)  # 0:未審核 1:審核中 2:審核通過 3:審核不通過
    ocr_status = Column(Integer, default=0)  # 0:未OCR 1:OCR中 2:OCR完成
    ocr_text = Column(LONGTEXT, default="")  # OCR辨識文字

    # 專科知識類
    knowledge_department = Column(String(255), default="")  # 科系 生科系
    knowledge_professor = Column(String(255), default="")  # 指定用書教授名
    knowledge_course = Column(String(255), default="")  # 課程 生物學
    knowledge_year = Column(String(255), default="")  # 出場年份 1999

    # 考題類
    question_department = Column(String(255), default="")  # 科系 生科系
    question_professor = Column(String(255), default="")  # 出題教授名 王大明
    question_course = Column(String(255), default="")  # 課程 生物學
    question_year = Column(String(255), default="")  # 出題學年 110
    question_semester = Column(String(255), default="")  # 學期 上學期 #亦烜拿來存學期
    question_exam_type = Column(String(255), default="")  # 考試類型 期中考
    question_exam_question_type = Column(Integer, default=0)  # 題型 0:未分類 1:選擇題 2:填充題 3:問答題 4:簡答題 5:計算題 6:繪圖題 7: 是非題 8:其他

class Questions(Base):
    __tablename__ = 'RAG_QUESTIONS'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(255), default="")
    number_in_file = Column(String(255), default="")
    type = Column(String(255), default="")
    raw_text = Column(LONGTEXT, default="")
    reference_answer = Column(String(255), default="")



# Deprecated 因為直接存dialogue裡就好
# class DialogueFeedback(Base):
#     __tablename__ = 'RAG_DIALOGUE_FEEDBACK'
