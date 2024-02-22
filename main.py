import os
from fastapi import FastAPI
import uvicorn
from src.routes import contacts, auth
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from src.load_dotenv import dotenv_load

dotenv_load()

app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=0,
        encoding="utf-8",
        decode_responses=True,
        password=None
    )

    await FastAPILimiter.init(r)


@app.get('/')
def read_root():
    return {"Hello": "World"}


if __name__ == '__main__':
    app.add_event_handler('startup', startup)
    uvicorn.run(app, host='localhost', port=8000)
