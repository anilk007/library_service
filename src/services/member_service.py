from fastapi import HTTPException
from asyncpg import UniqueViolationError

from src.db import connect_db
from src.repositories.member_repository import MemberRepository

class MemberService:

    @staticmethod
    async def create_member(member):
        pool = await connect_db()

        try:
            member_id = await MemberRepository.create_member(pool, member.dict())
            return {"message": "Member created successfully", "member_id": member_id}

        except UniqueViolationError:
            raise HTTPException(status_code=400, detail="Email already exists")

    @staticmethod
    async def get_member(member_id: int):
        pool = await connect_db()
        result = await MemberRepository.get_member(pool, member_id)

        if not result:
            raise HTTPException(status_code=404, detail="Member not found")

        return dict(result)

    @staticmethod
    async def get_all_members():
        pool = await connect_db()
        rows = await MemberRepository.get_all_members(pool)
        return [dict(r) for r in rows]

    @staticmethod
    async def update_member(member_id: int, member):
        pool = await connect_db()

        updated_id = await MemberRepository.update_member(
            pool, member_id, member.dict(exclude_unset=True)
        )

        if not updated_id:
            raise HTTPException(status_code=404, detail="Member not found")

        return {"message": "Member updated successfully"}

    @staticmethod
    async def delete_member(member_id: int):
        pool = await connect_db()

        result = await MemberRepository.delete_member(pool, member_id)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Member not found")

        return {"message": "Member deleted successfully"}
