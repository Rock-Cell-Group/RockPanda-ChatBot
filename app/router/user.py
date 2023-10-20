from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

import app.services.user as user_service
from app.model import schemas
from app.model.database import get_db

router = APIRouter(
    prefix="/api/v1/user",
    tags=['Users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    """註冊帳號 / add user new"""
    new_user = await user_service.new_user_register(request, db)
    return new_user

# @router.get("/", response_model=schemas.UserOut)
# async def fetch_current_user(db: Session = Depends(get_db),
#                              current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """查看當前使用者 / guest, user or admin fetch user"""
#     return await services.get_user_by_id(current_user.id, db)
#
#
# @router.get("/all", response_model=List[schemas.UserOut])
# async def fetch_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """查看所有使用者 / admin fetch all users"""
#     services.user_role_is_admin(current_user, True)
#     users = await services.all_users(db)
#     return users
#
#
# @router.get("/{user_id}", response_model=schemas.UserOut)
# async def fetch_user_by_user_id(user_id: int = Path(example=1, description="輸入使用者Id"),
#                                 db: Session = Depends(get_db),
#                                 current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """用id查使用者 / user or admin find users by username"""
#     services.user_role_is_admin(current_user, True)
#     user = await services.get_user_by_id(user_id, db)
#     return user
#
#
# @router.put("/{user_id}", response_model=schemas.UserSelfOut)
# async def update_user(user_id: int = Path(example=1, description="輸入使用者Id"),
#                       updated_user: schemas.UserUpdateRequest = schemas.UserUpdateRequest.Config.schema_extra,
#                       db: Session = Depends(get_db),
#                       current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """使用者更新個人資料 / user or admin update hisself/herself account information"""
#     services.user_role_is_guest(current_user, False)
#     return await services.update_user_by_his_id(user_id, updated_user, current_user, db)
#
#
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: int = Path(example=1, description="輸入使用者Id"),
#                       db: Session = Depends(get_db),
#                       current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """使用者刪除個人帳號 / user or admin delete his/her account,
#     刪除帳號後只要有檢查權限，就會因為
#     AttributeError: 'NoneType' object has no attribute 'roles' 而報錯
#     也算是另類的logout"""
#     services.user_role_is_guest(current_user, False)
#     await services.delete_user_by_id(user_id, db)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
#
#
# @router.put("/verification/{user_id}", response_model=schemas.UserOut)
# async def verify_guest(user_id: int = Path(example=1, description="輸入使用者Id"),
#                        db: Session = Depends(get_db),
#                        current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """管理員驗證使用者身分(啟用權限) / admin verify guest to user """
#     # 操作者是否為admin
#     services.user_role_is_admin(current_user, True)
#     # 被操作者是否為guest
#     user = await services.get_user_by_id(user_id, db)
#     services.user_role_is_guest(user, True)
#     # 開始更新
#     user_roles_user_dict = {"roles": "user"}
#     user_query = db.query(models.User).filter_by(id=user_id)
#     user_query.update(user_roles_user_dict, synchronize_session=False)
#     db.commit()
#     return user
#
#
# @router.put("/enable/{user_id}", response_model=schemas.UserOut)
# async def enable_user(user_id: int = Path(example=1, description="輸入使用者Id"),
#                       db: Session = Depends(get_db),
#                       current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """使用者復職 / user 復職"""
#     # 操作者是否為admin
#     services.user_role_is_admin(current_user, True)
#     # 被操作者是否為disable
#     user = services.check_user_status(user_id, Status.USER_STATUS_DISABLE, db)
#     # 開始更新
#     user_status_user_dict = {"status": Status.USER_STATUS_WORKING}
#     user_query = db.query(models.User).filter_by(id=user_id)
#     user_query.update(user_status_user_dict, synchronize_session=False)
#     db.commit()
#     return user
#
#
# @router.put("/disable/{user_id}", response_model=schemas.UserOut)
# async def disable_user(user_id: int = Path(example=1, description="輸入使用者Id"),
#                        db: Session = Depends(get_db),
#                        current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """使用者離職 / user 離職"""
#     # 操作者是否為admin
#     services.user_role_is_admin(current_user, True)
#     # 被操作者是否為working
#     user = services.check_user_status(user_id, Status.USER_STATUS_WORKING, db)
#     # 開始更新
#     user_status_user_dict = {"status": Status.USER_STATUS_DISABLE}
#     user_query = db.query(models.User).filter_by(id=user_id)
#     user_query.update(user_status_user_dict, synchronize_session=False)
#     db.commit()
#     return user
#
#
# @router.put("/password/{user_id}", response_model=schemas.UserOut)
# async def reset_user_password(user_id: int = Path(example=1, description="輸入使用者Id"),
#                               updated_user: schemas.UserPasswordReset = schemas.UserPasswordReset.Config.schema_extra,
#                               db: Session = Depends(get_db),
#                               current_user: schemas.User = Depends(oauth2.get_current_user)):
#     """使用者重設個人密碼 / user 忘記密碼"""
#     user = await services.get_current_user_by_his_id(user_id, current_user, db)
#     # 開始更新密碼(加密-->更新)
#     hashed_password = utils.hash(updated_user.password)
#     user_password_user_dict = {"password": hashed_password}
#     user_query = db.query(models.User).filter_by(id=user_id)
#     user_query.update(user_password_user_dict, synchronize_session=False)
#     db.commit()
#     return user
