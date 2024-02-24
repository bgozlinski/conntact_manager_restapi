import os
from fastapi import FastAPI
import uvicorn
from src.routes import contacts, auth, users
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from src.load_dotenv import dotenv_load

# Load environment variables from .env file
dotenv_load()

# Create FastAPI application instance
app = FastAPI()

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:8000"
    ]

# Add CORS middleware to allow requests from the defined origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from the 'src.routes' package for contacts, authentication, and users
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    Asynchronous startup event handler to initialize Redis connection for rate limiting.

    This function is executed when the FastAPI application starts, setting up a Redis connection
    using environment variables for the host and port configuration. The connection is then used
    to initialize the FastAPILimiter for rate limiting support across the application.
    """
    r = await redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        db=0,
        encoding="utf-8",
        decode_responses=True,
        password=None  # Assumes no password for Redis; modify as needed
    )

    # Initialize FastAPILimiter with the Redis connection
    await FastAPILimiter.init(r)


@app.get('/')
def read_root():
    """
    Default root path handler.

    Returns:
        dict: A simple dictionary response indicating the application is running.
    """
    return {"Hello": "World"}


# Condition to run the application directly with uvicorn when the script is executed
if __name__ == '__main__':
    # Optionally, add 'startup' event handler explicitly if needed
    app.add_event_handler('startup', startup)
    # Run the application with uvicorn on localhost port 8000
    uvicorn.run(app, host='localhost', port=8000)
