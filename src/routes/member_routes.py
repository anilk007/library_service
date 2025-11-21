from fastapi import APIRouter
from src.models.member_model import Member
from src.controllers.member_controller import MemberController

router = APIRouter(prefix="/members", tags=["Members"])

@router.post("")
async def create_member(member: Member):
    return await MemberController.create_member(member)

@router.get("/{member_id}")
async def get_member(member_id: int):
    return await MemberController.get_member(member_id)

@router.get("")
async def list_members():
    return await MemberController.list_members()

@router.put("/{member_id}")
async def update_member(member_id: int, member: Member):
    return await MemberController.update_member(member_id, member)

@router.delete("/{member_id}")
async def delete_member(member_id: int):
    return await MemberController.delete_member(member_id)
