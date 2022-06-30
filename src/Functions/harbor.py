import asyncio
from base64 import b64encode
import aiohttp

class usoHarbor:
    async def obtenerTokenHarbor(user,contraseña):
        usuario = ""
        usuario = user+":"+contraseña
        userAndPaas = b64encode(usuario.encode('ascii')).decode("ascii")
        headers = {'Authorization': 'Basic %s' % userAndPaas,'Accept': 'text/plain; charset=utf-8'}
        async with aiohttp.ClientSession() as session:
            async with session.get("/service/token?service=harbor-registry",headers=headers,verify_ssl=False) as r:
                resultado = await r.text()
                status = r.status
                if status == 200:
                    return resultado
                else:
                    return "en tu corazon"

    async def obtenerIDProyecto(token):
        headers = {'Accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.get("/api/projects",headers=headers,verify_ssl=False) as r:
                resultado = await r.json()
                status = r.status
                return resultado

    async def validarTagImagen(tag,data,dc):
        headers = {'Accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.get("/api/repositories/shuttle-san/fast-api-template/"+tag,headers=headers,verify_ssl = False) as r:
                status = r.status
                if status == 200:
                    resultado = await r.json()
                    return 1
                else:
                    return 0