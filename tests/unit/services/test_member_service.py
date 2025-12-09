import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import HTTPException
from asyncpg.exceptions import UniqueViolationError

from src.services.member_service import MemberService

# Sample test data
SAMPLE_MEMBER_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "address": "123 Main St",
    "status": "Active"
}

SAMPLE_MEMBER_RESPONSE = {
    "member_id": 1,
    **SAMPLE_MEMBER_DATA,
    "membership_date": "2024-01-01"
}

SAMPLE_MEMBERS_LIST = [
    {**SAMPLE_MEMBER_RESPONSE, "member_id": 1},
    {**SAMPLE_MEMBER_RESPONSE, "member_id": 2, "email": "jane.doe@example.com", "first_name": "Jane"}
]


@pytest.fixture
def mock_pool():
    """Mock database connection pool"""
    return AsyncMock()


@pytest.fixture
def mock_connect_db(mock_pool):
    """Mock connect_db function"""
    with patch('src.services.member_service.connect_db', return_value=mock_pool):
        yield mock_pool


class TestMemberService:

    # ========================
    # Test create_member method
    # ========================

    @pytest.mark.asyncio
    async def test_create_member_success(self, mock_connect_db):
        """Test successful member creation"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = SAMPLE_MEMBER_DATA

        # Create an AsyncMock for the repository method
        with patch('src.services.member_service.MemberRepository.create_member',
                   new_callable=AsyncMock) as mock_create_member:
            mock_create_member.return_value = 1

            # Act
            result = await MemberService.create_member(mock_member)

            # Assert
            mock_create_member.assert_called_once_with(mock_connect_db, SAMPLE_MEMBER_DATA)
            assert result == {"message": "Member created successfully", "member_id": 1}

    @pytest.mark.asyncio
    async def test_create_member_duplicate_email(self, mock_connect_db):
        """Test member creation with duplicate email"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = SAMPLE_MEMBER_DATA

        with patch('src.services.member_service.MemberRepository.create_member',
                   new_callable=AsyncMock) as mock_create_member:
            mock_create_member.side_effect = UniqueViolationError

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.create_member(mock_member)

            # Assert
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Email already exists"
            mock_create_member.assert_called_once_with(mock_connect_db, SAMPLE_MEMBER_DATA)

    @pytest.mark.asyncio
    async def test_create_member_database_error(self, mock_connect_db):
        """Test member creation with database error"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = SAMPLE_MEMBER_DATA

        with patch('src.services.member_service.MemberRepository.create_member',
                   new_callable=AsyncMock) as mock_create_member:
            mock_create_member.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await MemberService.create_member(mock_member)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ======================
    # Test get_member method
    # ======================

    @pytest.mark.asyncio
    async def test_get_member_success(self, mock_connect_db):
        """Test successful member retrieval"""
        # Arrange
        # Create a mock that behaves like a dictionary and also has a dict() method
        mock_row = MagicMock()
        mock_row.items.return_value = SAMPLE_MEMBER_RESPONSE.items()
        mock_row.keys.return_value = SAMPLE_MEMBER_RESPONSE.keys()
        mock_row.values.return_value = SAMPLE_MEMBER_RESPONSE.values()
        mock_row.__getitem__.side_effect = lambda key: SAMPLE_MEMBER_RESPONSE[key]

        with patch('src.services.member_service.MemberRepository.get_member',
                   new_callable=AsyncMock) as mock_get_member:
            mock_get_member.return_value = mock_row

            # Act
            result = await MemberService.get_member(1)

            # Assert
            mock_get_member.assert_called_once_with(mock_connect_db, 1)
            assert result == SAMPLE_MEMBER_RESPONSE

    @pytest.mark.asyncio
    async def test_get_member_not_found(self, mock_connect_db):
        """Test member retrieval when member doesn't exist"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.get_member',
                   new_callable=AsyncMock) as mock_get_member:
            mock_get_member.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.get_member(999)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Member not found"
            mock_get_member.assert_called_once_with(mock_connect_db, 999)

    @pytest.mark.asyncio
    async def test_get_member_database_error(self, mock_connect_db):
        """Test member retrieval with database error"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.get_member',
                   new_callable=AsyncMock) as mock_get_member:
            mock_get_member.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await MemberService.get_member(1)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ==========================
    # Test get_all_members method
    # ==========================

    @pytest.mark.asyncio
    async def test_get_all_members_success(self, mock_connect_db):
        """Test successful listing of members"""
        # Arrange
        # Create mock rows that can be converted to dict using dict()
        mock_rows = []
        for member_data in SAMPLE_MEMBERS_LIST:
            mock_row = MagicMock()
            mock_row.items.return_value = member_data.items()
            mock_row.keys.return_value = member_data.keys()
            mock_row.values.return_value = member_data.values()
            mock_row.__getitem__.side_effect = lambda key, md=member_data: md[key]
            mock_rows.append(mock_row)

        with patch('src.services.member_service.MemberRepository.get_all_members',
                   new_callable=AsyncMock) as mock_get_all_members:
            mock_get_all_members.return_value = mock_rows

            # Act
            result = await MemberService.get_all_members()

            # Assert
            mock_get_all_members.assert_called_once_with(mock_connect_db)
            assert result == SAMPLE_MEMBERS_LIST
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_members_empty(self, mock_connect_db):
        """Test listing members when no members exist"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.get_all_members',
                   new_callable=AsyncMock) as mock_get_all_members:
            mock_get_all_members.return_value = []

            # Act
            result = await MemberService.get_all_members()

            # Assert
            mock_get_all_members.assert_called_once_with(mock_connect_db)
            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_members_database_error(self, mock_connect_db):
        """Test listing members with database error"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.get_all_members',
                   new_callable=AsyncMock) as mock_get_all_members:
            mock_get_all_members.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await MemberService.get_all_members()

            # Assert
            assert str(exc_info.value) == "Database error"

    # ==========================
    # Test update_member method
    # ==========================

    @pytest.mark.asyncio
    async def test_update_member_success(self, mock_connect_db):
        """Test successful member update"""
        # Arrange
        mock_member = MagicMock()
        update_data = {"first_name": "Updated John", "email": "updated.john@example.com"}
        mock_member.dict.return_value = update_data

        with patch('src.services.member_service.MemberRepository.update_member',
                   new_callable=AsyncMock) as mock_update_member:
            mock_update_member.return_value = 1

            # Act
            result = await MemberService.update_member(1, mock_member)

            # Assert
            mock_update_member.assert_called_once_with(
                mock_connect_db, 1, update_data
            )
            assert result == {"message": "Member updated successfully"}

    @pytest.mark.asyncio
    async def test_update_member_not_found(self, mock_connect_db):
        """Test member update when member doesn't exist"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = {"first_name": "Updated John"}

        with patch('src.services.member_service.MemberRepository.update_member',
                   new_callable=AsyncMock) as mock_update_member:
            mock_update_member.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.update_member(999, mock_member)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Member not found"
            mock_update_member.assert_called_once_with(
                mock_connect_db, 999, {"first_name": "Updated John"}
            )

    @pytest.mark.asyncio
    async def test_update_member_database_error(self, mock_connect_db):
        """Test member update with database error"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = {"first_name": "Updated John"}

        with patch('src.services.member_service.MemberRepository.update_member',
                   new_callable=AsyncMock) as mock_update_member:
            mock_update_member.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await MemberService.update_member(1, mock_member)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ==========================
    # Test delete_member method
    # ==========================

    @pytest.mark.asyncio
    async def test_delete_member_success(self, mock_connect_db):
        """Test successful member deletion"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.delete_member',
                   new_callable=AsyncMock) as mock_delete_member:
            mock_delete_member.return_value = "DELETE 1"

            # Act
            result = await MemberService.delete_member(1)

            # Assert
            mock_delete_member.assert_called_once_with(mock_connect_db, 1)
            assert result == {"message": "Member deleted successfully"}

    @pytest.mark.asyncio
    async def test_delete_member_not_found(self, mock_connect_db):
        """Test member deletion when member doesn't exist"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.delete_member',
                   new_callable=AsyncMock) as mock_delete_member:
            mock_delete_member.return_value = "DELETE 0"

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.delete_member(999)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Member not found"
            mock_delete_member.assert_called_once_with(mock_connect_db, 999)

    @pytest.mark.asyncio
    async def test_delete_member_database_error(self, mock_connect_db):
        """Test member deletion with database error"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.delete_member',
                   new_callable=AsyncMock) as mock_delete_member:
            mock_delete_member.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await MemberService.delete_member(1)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ========================
    # Test edge cases
    # ========================

    @pytest.mark.asyncio
    async def test_create_member_with_none_data(self, mock_connect_db):
        """Test member creation with None member object"""
        # Arrange
        mock_member = None

        # Act & Assert
        with pytest.raises(AttributeError):
            await MemberService.create_member(mock_member)

    @pytest.mark.asyncio
    async def test_get_member_with_invalid_id(self, mock_connect_db):
        """Test member retrieval with invalid ID"""
        # Arrange
        with patch('src.services.member_service.MemberRepository.get_member',
                   new_callable=AsyncMock) as mock_get_member:
            mock_get_member.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.get_member(-1)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Member not found"

    @pytest.mark.asyncio
    async def test_update_member_with_empty_data(self, mock_connect_db):
        """Test member update with empty update data"""
        # Arrange
        mock_member = MagicMock()
        mock_member.dict.return_value = {}

        with patch('src.services.member_service.MemberRepository.update_member',
                   new_callable=AsyncMock) as mock_update_member:
            mock_update_member.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await MemberService.update_member(999, mock_member)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Member not found"
            mock_update_member.assert_called_once_with(mock_connect_db, 999, {})

    # ========================
    # Test concurrency
    # ========================

    @pytest.mark.asyncio
    async def test_concurrent_member_operations(self, mock_connect_db):
        """Test concurrent member operations"""
        # Arrange
        mock_member1 = MagicMock()
        mock_member1.dict.return_value = SAMPLE_MEMBER_DATA

        # Mock row for get_member
        mock_row = MagicMock()
        mock_row.items.return_value = SAMPLE_MEMBER_RESPONSE.items()
        mock_row.keys.return_value = SAMPLE_MEMBER_RESPONSE.keys()
        mock_row.values.return_value = SAMPLE_MEMBER_RESPONSE.values()
        mock_row.__getitem__.side_effect = lambda key: SAMPLE_MEMBER_RESPONSE[key]

        # Mock rows for get_all_members
        mock_rows = []
        for member_data in SAMPLE_MEMBERS_LIST:
            mock_row_list = MagicMock()
            mock_row_list.items.return_value = member_data.items()
            mock_row_list.keys.return_value = member_data.keys()
            mock_row_list.values.return_value = member_data.values()
            mock_row_list.__getitem__.side_effect = lambda key, md=member_data: md[key]
            mock_rows.append(mock_row_list)

        # Mock repository methods with AsyncMock
        with patch('src.services.member_service.MemberRepository.create_member',
                   new_callable=AsyncMock) as mock_create_member, \
                patch('src.services.member_service.MemberRepository.get_member',
                      new_callable=AsyncMock) as mock_get_member, \
                patch('src.services.member_service.MemberRepository.get_all_members',
                      new_callable=AsyncMock) as mock_get_all_members:
            mock_create_member.return_value = 1
            mock_get_member.return_value = mock_row
            mock_get_all_members.return_value = mock_rows

            # Act - Run operations concurrently
            tasks = [
                MemberService.create_member(mock_member1),
                MemberService.get_member(1),
                MemberService.get_all_members()
            ]

            results = await asyncio.gather(*tasks)

            # Assert
            assert len(results) == 3
            assert results[0] == {"message": "Member created successfully", "member_id": 1}
            assert results[1] == SAMPLE_MEMBER_RESPONSE
            assert results[2] == SAMPLE_MEMBERS_LIST