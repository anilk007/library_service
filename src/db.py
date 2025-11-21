import asyncpg

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/library_system"

async def connect_db():
    return await asyncpg.create_pool(DATABASE_URL)
