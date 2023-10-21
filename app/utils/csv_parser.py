import csv
from contextlib import contextmanager
from app.model import models
from app.model.database import SessionLocal


# Function to get the database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_question_csv_to_db(input_path: str):
    """
    將csv檔案的資料存入資料庫，
    對應欄位  id, file_id, number_in_file, type, raw_text, reference_answer
    """
    with get_db() as db:
        with open(input_path, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # skip header
            for row in csv_reader:
                id, file_id, number_in_file, type, raw_text, reference_answer = row
                # id = Column(Integer, primary_key=True, autoincrement=True)
                # file_id = Column(String(255), default="")
                # number_in_file = Column(String(255), default="")
                # type = Column(String(255), default="")
                # raw_text = Column(LONGTEXT, default="")
                # reference_answer = Column(String(255), default="")
                question = models.Questions(
                    file_id=file_id,
                    number_in_file=number_in_file,
                    type=type,
                    raw_text=raw_text,
                    reference_answer=reference_answer
                )
                db.add(question)
                db.commit()
                db.refresh(question)
            print(f"DONE: {input_path}")


# parse_question_csv_to_db('C:/Users/kwz50/PycharmProjects/RAG_ChatBot/data/Question_Data/rag_questions.csv')


def parse_file_system_csv_to_db(input_path: str):
    """
    將csv檔案的資料存入資料庫，
    對應欄位  id, user_id, file_name, file_path, file_size, file_extension, file_status, create_at, note, uuid_name, azure_container_name, azure_blob_name, file_purpose, is_file_useful, manager_id, manager_comment, censor_status, ocr_status, ocr_text, knowledge_department, knowledge_professor, knowledge_course, knowledge_year, question_department, question_professor, question_course, question_year, question_semester, question_exam_type, question_exam_question_type
    """
    with get_db() as db:
        with open(input_path, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # skip header
            for row in csv_reader:
                id, user_id, file_name, file_path, file_size, file_extension, file_status, create_at, note, uuid_name, azure_container_name, azure_blob_name, file_purpose, is_file_useful, manager_id, manager_comment, censor_status, ocr_status, ocr_text, knowledge_department, knowledge_professor, knowledge_course, knowledge_year, question_department, question_professor, question_course, question_year, question_semester, question_exam_type, question_exam_question_type = row
                # id = Column(Integer, primary_key=True, autoincrement=True)
                # user_id = Column(String(255), default="")
                # file_name = Column(String(255), default="")
                # file_path = Column(String(255), default="")
                # file_size = Column(String(255), default="")
                # file_extension = Column(String(255), default="")
                # file_status = Column(String(255), default="")
                # create_at = Column(DateTime, default=func.now())
                # note = Column(String(255), default="")
                #
                # # 開AZURE_BLOB儲存空間欄位
                # uuid_name = Column(String(255), default="")
                # azure_container_name = Column(String(255), default="")
                # azure_blob_name = Column(String(255), default="")
                #
                # # 檔案審查欄位
                # file_purpose = Column(String(255), default="")  # 檔案目的： question:考題上傳 knowledge：專科知識上傳 others：其他
                # is_file_useful = Column(Boolean)  # 管理者審核這個檔案是否有用
                # manager_id = Column(String(255), default="")
                # manager_comment = Column(String(255), default="")
                # censor_status = Column(Integer, default=0)  # 0:未審核 1:審核中 2:審核通過 3:審核不通過
                # ocr_status = Column(Integer, default=0)  # 0:未OCR 1:OCR中 2:OCR完成
                # ocr_text = Column(LONGTEXT, default="")  # OCR辨識文字
                #
                # # 專科知識類
                # knowledge_department = Column(String(255), default="")  # 科系 生科系
                # knowledge_professor = Column(String(255), default="")  # 指定用書教授名
                # knowledge_course = Column(String(255), default="")  # 課程 生物學
                # knowledge_year = Column(String(255), default="")  # 出場年份 1999
                #
                # # 考題類
                # question_department = Column(String(255), default="")  # 科系 生科系
                # question_professor = Column(String(255), default="")  # 出題教授名 王大明
                # question_course = Column(String(255), default="")  # 課程 生物學
                # question_year = Column(String(255), default="")  # 出題學年 110
                # question_semester = Column(String(255), default="")  # 學期 上學期 #亦烜拿來存學期
                # question_exam_type = Column(String(255), default="")  # 考試類型 期中考
                # question_exam_question_type = Column(Integer, default=0)  # 題型 0:未分類 1:選擇題 2:填充題 3:問答題 4:簡答題 5:計算題 6:繪圖題 7:其他

                file_system = models.FileSystem(
                    user_id=None if user_id == 'NULL' else user_id,
                    file_name=None if file_name == 'NULL' else file_name,
                    file_path=None if file_path == 'NULL' else file_path,
                    file_size=None if file_size == 'NULL' else file_size,
                    file_extension=None if file_extension == 'NULL' else file_extension,
                    file_status=None if file_status == 'NULL' else file_status,
                    create_at=None if create_at == 'NULL' else create_at,
                    note=None if note == 'NULL' else note,
                    uuid_name=None if uuid_name == 'NULL' else uuid_name,
                    azure_container_name=None if azure_container_name == 'NULL' else azure_container_name,
                    azure_blob_name=None if azure_blob_name == 'NULL' else azure_blob_name,
                    file_purpose=None if file_purpose == 'NULL' else file_purpose,
                    is_file_useful=None if is_file_useful == 'NULL' else is_file_useful,
                    manager_id=None if manager_id == 'NULL' else manager_id,
                    manager_comment=None if manager_comment == 'NULL' else manager_comment,
                    censor_status=None if censor_status == 'NULL' else censor_status,
                    ocr_status=None if ocr_status == 'NULL' else ocr_status,
                    ocr_text=None if ocr_text == 'NULL' else ocr_text,
                    knowledge_department=None if knowledge_department == 'NULL' else knowledge_department,
                    knowledge_professor=None if knowledge_professor == 'NULL' else knowledge_professor,
                    knowledge_course=None if knowledge_course == 'NULL' else knowledge_course,
                    knowledge_year=None if knowledge_year == 'NULL' else knowledge_year,
                    question_department=None if question_department == 'NULL' else question_department,
                    question_professor=None if question_professor == 'NULL' else question_professor,
                    question_course=None if question_course == 'NULL' else question_course,
                    question_year=None if question_year == 'NULL' else question_year,
                    question_semester=None if question_semester == 'NULL' else question_semester,
                    question_exam_type=None if question_exam_type == 'NULL' else question_exam_type,
                    question_exam_question_type=None if question_exam_question_type == 'NULL' else question_exam_question_type,
                )
                db.add(file_system)
                db.commit()
                db.refresh(file_system)
            print(f"DONE: {input_path}")


# parse_file_system_csv_to_db('C:/Users/kwz50/PycharmProjects/RAG_ChatBot/data/Question_Data/rag_file_system.csv')