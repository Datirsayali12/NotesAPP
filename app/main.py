from fastapi import FastAPI
from app.routers.notes import router

app = FastAPI()

# Include the router
app.include_router(router)