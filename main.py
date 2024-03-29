from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from db.database import init_db, async_session
from db.db_handlers import create_initial_data
from routes.tweets_routes import router as tweets_routes
from routes.users_routes import router as users_routes
from routes.medias_routes import router as medias_routes

app = FastAPI()

app.include_router(tweets_routes)
app.include_router(users_routes)
app.include_router(medias_routes)

app.mount("/static", StaticFiles(directory="static"), name="static")


async def fill_database():
    async with async_session() as session:
        await create_initial_data(session)


@app.on_event("startup")
async def startup_event():
    await init_db()
    await fill_database()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        {
            "result": False,
            "error_type": "HTTPException",
            "error_message": str(exc.detail),
        }
    )
