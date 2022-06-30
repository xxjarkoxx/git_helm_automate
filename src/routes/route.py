from fastapi import APIRouter,Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.Functions import git
import urllib3


urllib3.disable_warnings()

route = APIRouter()

@route.get("/listUsers",response_description="Lista de usuarios del git",tags=["v1"])
async def listUsers(user):
    #result_json = jsonable_encoder(await obtenerRepos(user) )
    #return JSONResponse(result_json)
    return "yeah"

@route.get("/listRepositories",response_description="Lista de usuarios del git",tags=["v1"])
async def listRepositories(user):    
    result_json = jsonable_encoder(await git.usoGit.listarRepos(user))
    return JSONResponse(result_json)

@route.get("/runner-groups",response_description="Github Actions",tags=["v1"])
async def runner_groups(user):
    result_json = jsonable_encoder(await git.usoGit.directoContrGit(user))
    return JSONResponse(result_json)

@route.post("/creaRepo",response_description="creación de repos via api github",tags=["v1"])
async def crea_repo(user,name):
    result_json = jsonable_encoder(await git.usoGit.creaRepo(user,name))
    return JSONResponse(result_json)