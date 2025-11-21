from asyncpg import Pool

class BookRepository:

    @staticmethod
    async def create_book(pool: Pool, book_data: dict):
        query = """
            INSERT INTO books
            (title, author, isbn, publication_year, publisher, genre, total_copies, available_copies)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING book_id;
        """
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *book_data.values())

    @staticmethod
    async def get_book_by_id(pool: Pool, book_id: int):
        async with pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM books WHERE book_id = $1", book_id)

    @staticmethod
    async def get_all_books(pool: Pool):
        async with pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM books ORDER BY created_at DESC")

    @staticmethod
    async def update_book(pool: Pool, book_id: int, book_data: dict):
        fields = ", ".join([f"{k} = ${i+1}" for i, k in enumerate(book_data.keys())])
        values = list(book_data.values())
        values.append(book_id)

        query = f"UPDATE books SET {fields} WHERE book_id = ${len(values)} RETURNING book_id"

        async with pool.acquire() as conn:
            return await conn.fetchval(query, *values)

    @staticmethod
    async def delete_book(pool: Pool, book_id: int):
        async with pool.acquire() as conn:
            return await conn.execute("DELETE FROM books WHERE book_id = $1", book_id)
