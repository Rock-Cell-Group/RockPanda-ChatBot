from contextlib import contextmanager
from typing import Union, List, Tuple
from sqlalchemy import not_, or_
from app.model import models
from app.model.database import SessionLocal
import uuid


# Function to get the database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_metadata_to_db(event):
    user_message = event.message.text.replace("/Document_information", "").strip()
    document_metadata = {}
    lines = user_message.split("\n")
    for line in lines:
        key, value = line.split("=")
        document_metadata[key.strip()] = value.strip()

    # 從字典中提取課程、授課老師和類型
    course = document_metadata.get("課程")
    teacher = document_metadata.get("授課老師")
    exam_type = document_metadata.get("類型")
    with get_db() as db:
        """
        question_course = Column(String(255), default="")  # 課程 生物學
        question_professor = Column(String(255), default="")  # 出題教授名 王大明
        question_exam_type = Column(String(255), default="")  # 考試類型 期中考
        """

        new_file = models.FileSystem(
            user_id=event.source.user_id,
            question_course=course,
            question_professor=teacher,
            question_exam_type=exam_type
        )

        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file
"""
Event: type='message' 
source=UserSource(type='user', user_id='U94617f94e42a2d172f600b0e02f2204c') 
timestamp=1697120172431 
mode=<EventMode.ACTIVE: 'active'> 
webhook_event_id='01HCJ3XEKEGPRVM8Z6T714JCSA' 
delivery_context=DeliveryContext(is_redelivery=False) 
reply_token='e33931b497e5473e929cc3a4610aadb6' 
message=TextMessageContent(type='text',
    id='476957575037321555',
    text='/Document_information\n課程=微積分\n授課老師=王小明\n類型=期中考', 
    emojis=None, 
    mention=None, 
    quote_token='IDHMbjQptp077dRGeslBrpSe2izsy4ke6-zKuE5Cp1xOtFoHXjYKtiVDjFaM80oP7lVmvKcYC8hzFEhns9HvFBFK0QEHm_fMavZ7BO1wBWnRfjpWTDsltGC_uRzdnp0UmDWoixot7BX6r4mDIgHWkA', 
    quoted_message_id=None)
"""


def is_file_saved(event):
    with get_db() as db:
        # 檢查file是否已存到專案目錄內及db內
        dialogue = db.query(models.Dialogue).filter(models.Dialogue.message_id == event.message.id).first()
        file = db.query(models.FileSystem).filter(models.FileSystem.id == dialogue.file_id).first()
        if dialogue and file:
            return True
        else:
            return False

        """
        type='message' 
        source=UserSource(type='user', user_id='U4df6a2535fcae2dc9277c39aec86ca66') 
        timestamp=1696767716822 
        mode=<EventMode.ACTIVE: 'active'> 
        webhook_event_id='01HC7KSBG9BZDMDJH10G8QEGJ7' 
        delivery_context=DeliveryContext(is_redelivery=False) 
        reply_token='84f068f079004a6793b63b8a82f79563' 
        message=FileMessageContent(
                    type='file', 
                    id='476366252647121285', 
                    file_name='493563768(2).pdf', 
                    file_size=481971)
        """


def get_column_value_set_by_conditions(model_class, conditions, column_name_to_query=None):
    """
    Example:
    conditions = [
        ("question_course", "calculus1"),
        ("semester", "Spring"),
        # Add more conditions as needed
    ]
    result = get_column_value_set_by_conditions(models.FileSystem, conditions, "question_professor")
    """
    with get_db() as db:
        try:
            # 創建一個初始的查詢
            if column_name_to_query:
                # 指定搜尋某欄位
                query = db.query(getattr(model_class, column_name_to_query))
            else:
                # 搜尋所有欄位
                query = db.query(model_class)

            # 添加多個 filter 條件
            for column_name, column_value in conditions:
                query = query.filter(getattr(model_class, column_name) == column_value)
               
            # 去除重複值
            result = query.distinct().all()

            # 提取結果
            if column_name_to_query:
                result = [row[0] for row in result]
            
            return result
        except Exception as e:
            # 處理錯誤
            print(f"get_column_value_set_by_conditions() 發生錯誤：{e}")
            return []

''''
# 使用示例
conditions = [
    ("question_course", "calculus1"),
    ("semester", "Spring")
]
result = get_column_value_set_by_conditions(models.FileSystem, conditions, "question_professor")
'''


def update_file_by_metadata(event, conditions):
    
    dialogue = get_column_value_set_by_conditions(models.Dialogue, [("message_id", event.message.id)])[0]
    model_class = models.FileSystem
    try:
        with get_db() as db:    
            query = db.query(model_class)

            # add filter conditions
            for column_name, column_value in conditions:
                query = query.filter(getattr(model_class, column_name) == column_value)
            
            selected_row = query.distinct().all()[0]            
            file_path = file_fetcher(dialogue)

            selected_row.file_path = file_path
            selected_row.file_name = event.message.file_name
            selected_row.file_extension = dialogue.message_file_extension
            selected_row.file_size = event.message.file_size
            selected_row.censor_status = 0
            db.commit()

            return selected_row
            
    except Exception as e:
        # 處理錯誤
        print(f"update_file_by_metadata() 發生錯誤：{e}")
        return None
            
    """
    type='message'
    source=UserSource(type='user', user_id='U94617f94e42a2d172f600b0e02f2204c') 
    timestamp=1697352244741 
    mode=<EventMode.ACTIVE: 'active'> 
    webhook_event_id='01HCS17R01Z09A583F8ZPEQVGC' 
    delivery_context=DeliveryContext(is_redelivery=False) 
    reply_token='c2c2dd89313741438399e47a455657d2' 
    message=FileMessageContent(type='file', id='477346927479357716', file_name='NTHU_112-1_calendar.pdf', file_size=184541)

    """


def file_fetcher(dialogue):
    """
    # API文件寫法
    # GET https://api-data.line.me/v2/bot/message/{messageId}/content
    #
    # curl -v -X GET https://api-data.line.me/v2/bot/message/{messageId}/content \
    # -H 'Authorization: Bearer {channel access token}'
    """

    import requests
    from dotenv import load_dotenv
    from os import environ

    load_dotenv()
    channel_access_token = environ.get("CHANNEL_ACCESS_TOKEN")

    url = f"https://api-data.line.me/v2/bot/message/{dialogue.message_id}/content"
    headers = {
        "Authorization": f"Bearer {channel_access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_path = f"./data/Upload_Data/{uuid.uuid4()}.{dialogue.message_file_extension}"
        with open(file_path, "wb") as f:
            f.write(response.content)
            return file_path

    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response content: {response.text}")

    return None

        
"""
type='message'
source=UserSource(type='user', user_id='U94617f94e42a2d172f600b0e02f2204c')
timestamp=1697350357574 
mode=<EventMode.ACTIVE: 'active'> 
webhook_event_id='01HCRZE4RSZEYSZYR3BT6WWFZQ' 
delivery_context=DeliveryContext(is_redelivery=False) 
reply_token='df5e9b1b6f344382beddb8efa503b7ba' 
message=FileMessageContent(type='file', id='477343761400594851', file_name='NTHU_112-1_calendar.pdf', file_size=184541)

***** document_metadata = {'subject': '微積分', 'professor': '王小明', 'exam_type': '期中考'}
"""

        
def get_column_value_set(model_class, column_name: str):
    with get_db() as db:
        try:
            # 下面那種不知為啥都返回空的。
            result = db.query(getattr(model_class, column_name)).distinct().filter(
                or_(
                    getattr(model_class, column_name) != None,
                    getattr(model_class, column_name) != ""
                )
            ).all()

            # 這種的result都是空的
            # result = db.query(getattr(model_class, column_name)).filter(
            #     not_(getattr(model_class, column_name).in_([None, ""]))
            # ).distinct().all()


            # 提取結果
            column_values = [row[0] for row in result]

            return column_values
        except Exception as e:
            # 處理錯誤
            print(f"發生錯誤：{e}")
            return []
        
# 根據特定file id回傳某個欄位的值
def get_column_value_by_file_id(file_id: str, column_name: str):
    with get_db() as db:
        query_result =  db.query(getattr(models.FileSystem, column_name)).filter_by(id=file_id).first()
        result, = query_result
        return result
    
