import logging

from asyncpg import Pool
from typing import List, Optional, Dict, Any
from datetime import date

logger = logging.getLogger(__name__)

from src.models.book_transaction import TransactionStatus

class BookTransactionRepository:

    @staticmethod
    async def create_transaction(pool: Pool, transaction_data: dict) -> Dict[str, Any]:
        logger.info("create_transaction...", transaction_data)
        logger.debug("2nd debug create_transaction...", transaction_data)

        query = """
            INSERT INTO book_transactions 
            (book_id, member_id, issue_date, due_date, return_date, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *;
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                transaction_data['book_id'],
                transaction_data['member_id'],
                transaction_data.get('issue_date', date.today()),
                transaction_data['due_date'],
                transaction_data.get('return_date'),
                transaction_data.get('status', 'Issued')
            )

            # Reduce available copies
            await conn.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = $1",
                transaction_data['book_id']
            )

            return dict(row) if row else None

    @staticmethod
    async def get_transaction_by_id(pool: Pool, transaction_id: int) -> Optional[Dict[str, Any]]:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM book_transactions WHERE transaction_id = $1",
                transaction_id
            )
            return dict(row) if row else None

    @staticmethod
    async def get_all_transactions(pool: Pool, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM book_transactions 
            ORDER BY created_at DESC 
            LIMIT $1 OFFSET $2
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, limit, skip)
            return [dict(row) for row in rows]

    @staticmethod
    async def update_transaction(pool: Pool, transaction_id: int, update_data: dict) -> Optional[Dict[str, Any]]:
        if not update_data:
            return await BookTransactionRepository.get_transaction_by_id(pool, transaction_id)

        fields = ", ".join([f"{k} = ${i + 1}" for i, k in enumerate(update_data.keys())])
        values = list(update_data.values())
        values.append(transaction_id)

        query = f"""
            UPDATE book_transactions 
            SET {fields} 
            WHERE transaction_id = ${len(values)} 
            RETURNING *
        """

        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None

    @staticmethod
    async def delete_transaction(pool: Pool, transaction_id: int) -> bool:
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM book_transactions WHERE transaction_id = $1",
                transaction_id
            )
            return "DELETE 1" in result

    @staticmethod
    async def get_transactions_by_book(pool: Pool, book_id: int) -> List[Dict[str, Any]]:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM book_transactions WHERE book_id = $1 ORDER BY created_at DESC",
                book_id
            )
            return [dict(row) for row in rows]

    @staticmethod
    async def get_transactions_by_member(pool: Pool, member_id: int) -> List[Dict[str, Any]]:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM book_transactions WHERE member_id = $1 ORDER BY created_at DESC",
                member_id
            )
            return [dict(row) for row in rows]

    @staticmethod
    async def get_active_transactions(pool: Pool) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM book_transactions 
            WHERE status IN ('Issued', 'Overdue')
            ORDER BY due_date ASC
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    @staticmethod
    async def get_overdue_transactions(pool: Pool) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM book_transactions 
            WHERE status IN ('Issued', 'Overdue') 
            AND due_date < CURRENT_DATE
            ORDER BY due_date ASC
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    @staticmethod
    async def mark_as_returned(pool: Pool, transaction_id: int, return_date: date = None) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE book_transactions 
            SET return_date = $1, status = 'Returned'
            WHERE transaction_id = $2
            RETURNING *
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, return_date or date.today(), transaction_id)
            if not row:
                return None

                # Increase available copies
            await conn.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = $1",
                row['book_id']
            )

            return dict(row)

    @staticmethod
    async def update_overdue_status(pool: Pool) -> int:
        query = """
            UPDATE book_transactions 
            SET status = 'Overdue'
            WHERE status = 'Issued' 
            AND due_date < CURRENT_DATE
        """
        async with pool.acquire() as conn:
            result = await conn.execute(query)
            if "UPDATE" in result:
                return int(result.split()[1])
            return 0

    @staticmethod
    async def is_book_available(pool: Pool, book_id: int) -> bool:
        """Check if a book is available (not currently issued)"""
        query = """
            SELECT COUNT(*) as active_count FROM book_transactions 
            WHERE book_id = $1 AND status IN ('Issued', 'Overdue')
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, book_id)
            return row['active_count'] == 0

    @staticmethod
    async def get_member_active_books_count(pool: Pool, member_id: int) -> int:
        """Get count of active books issued to a member"""
        query = """
            SELECT COUNT(*) as active_count FROM book_transactions 
            WHERE member_id = $1 AND status IN ('Issued', 'Overdue')
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, member_id)
            return row['active_count']

    @staticmethod
    async def get_book_issued_members(pool, book_id: int) -> List[Dict[str, Any]]:

        try:
            async with pool.acquire() as connection:
                query = """
                        SELECT 
                            m.member_id,
                            m.first_name,
                            m.last_name,
                            m.email,
                            m.phone,
                            bt.issue_date,
                            bt.due_date,
                            bt.transaction_id,
                            bt.status
                        FROM book_transactions bt
                        JOIN members m ON bt.member_id = m.member_id
                        WHERE bt.book_id = $1 
                        AND bt.status IN ($2, $3)
                        AND bt.return_date IS NULL
                        ORDER BY bt.issue_date DESC
                    """

                rows = await connection.fetch(
                    query,
                    book_id,
                    TransactionStatus.ISSUED.value,
                    TransactionStatus.OVERDUE.value
                )

                members = []
                for row in rows:
                    member_data = {
                        "member_id": row["member_id"],
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "issue_date": row["issue_date"].isoformat() if row["issue_date"] else None,
                        "due_date": row["due_date"].isoformat() if row["due_date"] else None,
                        "transaction_id": row["transaction_id"],
                        "status": row["status"]
                    }
                    members.append(member_data)

                return members

        except Exception as e:
            logger.error(f"Error getting book issued members: {str(e)}")
            raise

