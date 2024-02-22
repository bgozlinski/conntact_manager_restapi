from fastapi import FastAPI, Depends
import uvicorn

from src.routes import contacts, auth

from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from fastapi_limiter.depends import RateLimiter


app = FastAPI()

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host='127.0.0.1',
        port=6379,
        db=0,
        encoding="utf-8",
        decode_responses=True,
        password=None
    )

    await FastAPILimiter.init(r)


@app.get('/', dependencies=[Depends(RateLimiter(times=3, seconds=10))])
def read_root():
    return {"Hello": "World"}


if __name__ == '__main__':
    # app.add_event_handler('startup', startup)
    uvicorn.run(app, host='localhost', port=8000)
