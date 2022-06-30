import asyncio
import aiohttp
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://api.github.com"
token = "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"
org = "xxjarkoxx"

class usoGit:
    async def directoContrGit(user):
        header = {'Authorization': "token "+token,'Accept': 'application/vnd.github.v3+json'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/orgs/"+org+"/actions/runner-groups",headers=header,verify_ssl=False) as r:
                resultado = await r.json()
                print(resultado)
                return resultado

    async def listarRepos(user):
        header = {'Authorization': "token "+token,'Accept': 'application/vnd.github.v3+json'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/user/repos",headers=header,verify_ssl=False) as r:
                resultado = await r.json()
                print(resultado)
                return resultado

    async def creaRepo(user,name):
        yml={}
        yml["name"] = name
        yml["description"] = "prueba contra el api de github"
        yml["private"] = False
        yml["auto_init"] = True
        header = {'Authorization': "token "+token,'Accept': 'application/vnd.github.v3+json'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url+"/user/repos",headers=header,json=yml,verify_ssl=False) as r:
                resultado = await r.json()
                print(resultado)
                return resultado