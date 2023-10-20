from contextlib import contextmanager
from typing import Optional, List
import json
from fastapi import HTTPException, status

from app.model import models
from app.model.database import SessionLocal


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def new_user_register(request, db) -> models.Users:
    # create new user, set value for other params
    new_user = models.Users(**request.dict())
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=e)
    db.refresh(new_user)
    print(new_user.user_name)

    return new_user


def is_user_registered(user_id):
    with get_db() as db:
        # 檢查user是否已註冊至db內
        check_user = db.query(models.Users).filter(models.Users.user_id == user_id).count()
        if check_user == 1:
            return db.query(models.Users).filter(models.Users.user_id == user_id)
        else:
            return None


def create_user(user_id):
    with get_db() as db:
        new_user = models.Users(
            user_id=user_id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


# 這是更改欄位值
def commit_user_new_column_value(user_id: str, columnname: str, tobecommit):
    with get_db() as db:
        # 選擇要更新的用戶
        user_to_update = db.query(models.Users).filter_by(user_id=user_id).first()

        if user_to_update:
            # 更新欄位
            setattr(user_to_update, columnname, tobecommit)
            # 提交更動
            db.commit()
        else:
            print("找不到要更新的用戶")


# 直接一直接下去，不改原始值
def append_user_column_value(user_id: str, columnname: str, tobeappend):
    with get_db() as db:
        # 選擇要更新的用戶
        user_to_update = db.query(models.Users).filter_by(user_id=user_id).first()

        if user_to_update:
            # 檢查用戶屬性是否存在
            if hasattr(user_to_update, columnname):
                # 直接將 tobeappend 字符串附加到列中
                # 如果屬性值為空或不存在，則初始化為一個包含 tobeappend 的列表
                if getattr(user_to_update, columnname) is None:
                    setattr(user_to_update, columnname, tobeappend)
                else:
                    # 如果屬性不為空，將 tobeappend 字符串添加到列中
                    value_old = getattr(user_to_update, columnname)
                    if isinstance(value_old, str):
                        current_value = value_old+tobeappend
                    setattr(user_to_update, columnname, current_value)
                # 提交更改
                db.commit()
                return True
            else:
                print(f"屬性 {columnname} 不存在。")
        else:
            print("找不到要更新的用戶")

# 找某用戶某欄的值
def get_user_column_value(user_id: str, columnname: str):
    with get_db() as db:
        # 取出要查的用戶
        exist_user = db.query(models.Users).filter_by(user_id=user_id).first()

        if exist_user:
            return getattr(exist_user, columnname)
        else:
            return None
        
# 找所有feedbacks有值的用戶
def get_users_with_feedbacks():
    with get_db() as db:
        # 獲取所有用戶的數據
        all_users = db.query(models.Users).all()

        users_with_feedbacks = []

        for user in all_users:
            if hasattr(user, 'feedbacks') and user.feedbacks:
                user_data = {
                    'user_id': user.user_id,
                    'feedbacks': user.feedbacks
                }
                users_with_feedbacks.append(user_data)

        return users_with_feedbacks
    

def delete_first_n_feedback_records(user_id: str, n: int):
    with get_db() as db:
        # 獲取用戶記錄
        user_to_update = db.query(models.Users).filter_by(user_id=user_id).first()

        if user_to_update:
            # 檢查用戶屬性是否存在
            if hasattr(user_to_update, "feedbacks"):
                # 獲取屬性值
                column_value = getattr(user_to_update, "feedbacks")
                if not column_value:
                    return
                # 將字符串按照"/feedback"分隔為列表
                feedbacks_list = column_value.split('/feedback')
                
                # 檢查n是否大於等於列表的長度
                if n > len(feedbacks_list):
                    print(f"n 大於或等於屬性 feedbacks 中目前的記錄數，沒有記錄可刪除。")
                elif n == len(feedbacks_list):
                    setattr(user_to_update, "feedbacks", None)
                    db.commit()
                    print(f"用戶 {user_id} 的屬性 feedbacks 已無記錄。")
                else:
                    # 刪除前n條記錄
                    feedbacks_list = feedbacks_list[n:]
                    
                    # 更新屬性為以"/feedback"分隔的字符串
                    updated_feedbacks = '/feedback'.join(feedbacks_list)
                    setattr(user_to_update, "feedbacks", updated_feedbacks)
                    
                    # 提交更改
                    db.commit()
                    print(f"用戶 {user_id} 的屬性 feedbacks 已刪除前 {n} 條記錄。")
            else:
                print(f"用戶 {user_id} 的屬性 feedbacks 不存在。")
        else:
            print(f"找不到用戶 {user_id}。")
        
# def delete_first_n_feedback_records(user_id: str, n: int):
#     with get_db() as db:
#         # 獲取用戶記錄
#         user_to_update = db.query(models.Users).filter_by(user_id=user_id).first()

#         if user_to_update:
#             # 檢查用戶屬性是否存在
#             if hasattr(user_to_update, "feedbacks"):
#                 # 獲取屬性值
#                 column_value = getattr(user_to_update, "feedbacks")
                
#                 # 解碼JSON字符串為Python列表
#                 data = json.loads(column_value)

#                 # 刪除前n條記錄
#                 if n > 0:
#                     data = data[n:]

#                     # 更新屬性為編碼後的JSON字符串
#                     updated_json_data = json.dumps(data, ensure_ascii=False)
#                     setattr(user_to_update, "feedbacks", updated_json_data)
                    
#                     # 提交更改
#                     db.commit()
#                     print(f"用戶 {user_id} 的屬性 feedbacks 已刪除前 {n} 條記錄。")
#                 else:
#                     print("n 必須是正整數。")
#             else:
#                 print(f"用戶 {user_id} 的屬性 feedbacks 不存在。")
#         else:
#             print(f"找不到用戶 {user_id}。")