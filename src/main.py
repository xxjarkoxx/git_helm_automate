from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.routes import route

app = FastAPI(
    title="Git HELM Integrate with OKTETO CLOUD",
    description="Git HELM Integrate with OKTETO CLOUD",
    version="1.0",
    openapi_url="/api/v1/openapi.json"
)

origins = [
    "localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/health", tags=["healthcheck"])
async def healthcheck():
    return "server OK"


app.include_router(route.route,tags=["v1"])
app.include_router(route.route,tags=["v1"])

