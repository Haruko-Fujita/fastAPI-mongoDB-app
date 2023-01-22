from fastapi import APIRouter
from fastapi import Response, Request, HTTPException, Depends # 引数の型
from fastapi.encoders import jsonable_encoder # JSON型からdict型に変換
from schemas import Todo, TodoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_get_single_todo, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List
# from fastapi_csrf_protect import CsrfProtect
# from auth_utils import AuthJwtCsrf

router = APIRouter() # インスタンス化
# auth = AuthJwtCsrf()


# todo作成API
@router.post("/api/todo", response_model=Todo)
async def create_todo(request: Request, response: Response, data: TodoBody):
# async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
#     new_token = auth.verify_csrf_update_jwt(
#         request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED # create成功時のstatus codeを200から201にする
#     response.set_cookie(
#         key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Create task failed")


# todo一覧取得API
@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request):
    # auth.verify_jwt(request)
    res = await db_get_todos()
    return res


# todoのid指定で取得
@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(request: Request, response: Response, id: str):
    # new_token, _ = auth.verify_update_jwt(request)
    res = await db_get_single_todo(id)
    # response.set_cookie(
    #     key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail=f"Task of ID:{id} doesn't exist") # 変数とテキストを結合するf(=format)


@router.put("/api/todo/{id}", response_model=Todo)
async def update_todo(request: Request, response: Response, id: str, data: TodoBody):
# async def update_todo(request: Request, response: Response, id: str, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
#     new_token = auth.verify_csrf_update_jwt(
#         request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, todo)
#     response.set_cookie(
#         key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Update task failed")


@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, id: str):
# async def delete_todo(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
#     new_token = auth.verify_csrf_update_jwt(
#         request, csrf_protect, request.headers)
    res = await db_delete_todo(id)
    # response.set_cookie(
#         key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return {'message': 'Successfully deleted'}
    raise HTTPException(
        status_code=404, detail="Delete task failed")