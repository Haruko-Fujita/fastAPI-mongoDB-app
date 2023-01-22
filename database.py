from decouple import config # 環境変数読み込み
# from fastapi import HTTPException
from typing import Union # union型
import motor.motor_asyncio # mongoDBとの連携
from bson import ObjectId # BSONはmongoDBの保存型、string型からオブジェクト型に変換
# from auth_utils import AuthJwtCsrf
# import asyncio

# mongoDBと連携するための処理
MONGO_API_KEY = config('MONGO_API_KEY')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
# client.get_io_loop = asyncio.get_event_loop
database = client.API_DB # mongoDBで設定したdatabaseとcollectionをfastAPIで使えるようにする
collection_todo = database.todo
collection_user = database.user
# auth = AuthJwtCsrf()


# mongoDBのオブジェクトidクラスから生成されたインスタンスを辞書型に変換する
def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"]
    }


# def user_serializer(user) -> dict:
    # return {
    #     "id": str(user["_id"]),
    #     "email": user["email"],
    # }


# todo作成
async def db_create_todo(data: dict) -> Union[dict, bool]: # returnの方が複数、union型
    todo = await collection_todo.insert_one(data) # moterモジュールでmongoDBにinserted_idドキュメントを生成
    new_todo = await collection_todo.find_one({"_id": todo.inserted_id}) # mongoDBからidドキュメントを取得
    if new_todo:
        return todo_serializer(new_todo)
    return False


# todo一覧取得
async def db_get_todos() -> list:
    todos = []
    # motorメソッドfind、awaitは必要ないが、to_listでDBとの通信を行うときにawaitが必要、length max100件
    for todo in await collection_todo.find().to_list(length=100):
        todos.append(todo_serializer(todo))
    return todos


# todoのid指定で取得
async def db_get_single_todo(id: str) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)}) # _idの型をstring型からオブジェクト型に変換して渡す
    if todo:
        return todo_serializer(todo)
    return False


# todo更新
async def db_update_todo(id: str, data: dict) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)}) # 引数のidが存在するか確認
    if todo:
        updated_todo = await collection_todo.update_one(
            {"_id": ObjectId(id)}, {"$set": data} # set dataで更新内容を渡す
        )
        # 更新成功時はupdate_oneの返り値modified_countに更新したドキュメント数が入る
        if (updated_todo.modified_count > 0):
            new_todo = await collection_todo.find_one({"_id": ObjectId(id)})
            return todo_serializer(new_todo)
    return False


# todo削除
async def db_delete_todo(id: str) -> bool:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        deleted_todo = await collection_todo.delete_one({"_id": ObjectId(id)})
        # 更新成功時はdelete_oneの返り値deleted_countに削除したドキュメント数が入る
        if (deleted_todo.deleted_count > 0):
            return True
    return False


# async def db_signup(data: dict) -> dict:
#     email = data.get("email")
#     password = data.get("password")
#     overlap_user = await collection_user.find_one({"email": email})
#     if overlap_user:
#         raise HTTPException(status_code=400, detail='Email is already taken')
#     if not password or len(password) < 6:
#         raise HTTPException(status_code=400, detail='Password too short')
#     user = await collection_user.insert_one({"email": email, "password": auth.generate_hashed_pw(password)})
#     new_user = await collection_user.find_one({"_id": user.inserted_id})
#     return user_serializer(new_user)


# async def db_login(data: dict) -> str:
#     email = data.get("email")
#     password = data.get("password")
#     user = await collection_user.find_one({"email": email})
#     if not user or not auth.verify_pw(password, user["password"]):
#         raise HTTPException(
#             status_code=401, detail='Invalid email or password')
#     token = auth.encode_jwt(user['email'])
#     return token