import asyncpg

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/library_system"

pool = None  # global connection pool

async def connect_db():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return pool
