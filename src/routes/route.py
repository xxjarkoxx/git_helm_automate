from fastapi import APIRouter,Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import urllib3

urllib3.disable_warnings()

route = APIRouter()

@route.get("/listUsers",response_description="Lista de usuarios del git",tags=["v1"])
async def listUsers(user):
    result_json = jsonable_encoder(await obtenerRepos(user) )
    return JSONResponse(result_json)
