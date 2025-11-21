from asyncpg import Pool

class MemberRepository:

    @staticmethod
    async def create_member(pool: Pool, data: dict):
        query = """
            INSERT INTO members 
            (first_name, last_name, email, phone, address, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING member_id;
        """
        values = list(data.values())

        async with pool.acquire() as conn:
            return await conn.fetchval(query, *values)

    @staticmethod
    async def get_member(pool: Pool, member_id: int):
        query = "SELECT * FROM members WHERE member_id = $1"
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, member_id)

    @staticmethod
    async def get_all_members(pool: Pool):
        query = "SELECT * FROM members ORDER BY membership_date DESC"
        async with pool.acquire() as conn:
            return await conn.fetch(query)

    @staticmethod
    async def update_member(pool: Pool, member_id: int, data: dict):
        fields = ", ".join([f"{k} = ${i+1}" for i, k in enumerate(data.keys())])
        values = list(data.values())
        values.append(member_id)

        query = f"""
            UPDATE members 
            SET {fields}
            WHERE member_id = ${len(values)} 
            RETURNING member_id
        """

        async with pool.acquire() as conn:
            return await conn.fetchval(query, *values)

    @staticmethod
    async def delete_member(pool: Pool, member_id: int):
        query = "DELETE FROM members WHERE member_id = $1"
        async with pool.acquire() as conn:
            return await conn.execute(query, member_id)
