import logging.config

# 1. Import the configuration dictionary
from src.config.logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

# Call the logging methods
logger.info("Configuration loaded successfully and application started.")

from fastapi import FastAPI
from src.routes.book_routes import router as book_router
from src.routes.member_routes import router as member_router
from src.routes.book_transaction_routes import router as book_transaction_router

app = FastAPI()

app.include_router(book_router)
app.include_router(member_router)
app.include_router(book_transaction_router)


@app.get("/")
def root():
    return {"message": "Library Service Running..."}