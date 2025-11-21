from src.services.member_service import MemberService
from src.models.member_model import Member

class MemberController:

    @staticmethod
    async def create_member(member: Member):
        return await MemberService.create_member(member)

    @staticmethod
    async def get_member(member_id: int):
        return await MemberService.get_member(member_id)

    @staticmethod
    async def list_members():
        return await MemberService.get_all_members()

    @staticmethod
    async def update_member(member_id: int, member: Member):
        return await MemberService.update_member(member_id, member)

    @staticmethod
    async def delete_member(member_id: int):
        return await MemberService.delete_member(member_id)
