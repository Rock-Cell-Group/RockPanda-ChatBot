from contextlib import contextmanager
from typing import Optional, List

from sqlalchemy import not_
from sqlalchemy import func

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

# 根據特定file_id，回傳問題id列表，隨機k個
def get_random_k_question_ids_by_fileIDs(fileIDs: List[str], k: Optional[int] = 1) -> List[str]:
    """
    Example:
    fileIDs = [5, 9, 16
        # Add more fileIDs as needed
    ]
    result = get_random_k_questions_by_fileIDs(fileIDs, 4)
    """

    # 確保k不超過10，因為carousel只能放10個
    k = min(k, 10)

    with get_db() as db:
        try:
            # 創建一個初始的查詢, 僅返回那些 file_id 值存在於 fileIDs 列表中的記錄
            query = db.query(models.Questions.id).filter(models.Questions.file_id.in_(fileIDs))

            # 限制筆數k
            query = query.order_by(func.random()).limit(k)

            # 執行查詢並取得 rawtext 欄位值
            question_ids_list = [row.id for row in query.all()]

            return question_ids_list
        except Exception as e:
            # 處理異常
            print(f"Error: {str(e)}")
            return []

# 根據question id列表回傳raw_text
def get_rawtext_for_question_ids(question_ids: List[str]):
    with get_db() as db:
        raw_texts = []
        # 查询每个问题ID对应的rawtext
        for question_id in question_ids:
            result = db.query(models.Questions.raw_text).filter_by(id=question_id).first()
            if result:
                raw_texts.append(result[0])
            else:
                raw_texts.append(None)
        return raw_texts

# 根據特定question id回傳某個欄位的值
def get_column_value_by_question_id(question_id: str, column_name: str):
    with get_db() as db:
        query_result = db.query(getattr(models.Questions, column_name)).filter_by(id=question_id).first()
        result, = query_result
        return result