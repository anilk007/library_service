import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from asyncpg.exceptions import UniqueViolationError

from src.services.book_transaction_service import BookTransactionService
from src.models.book_transaction import TransactionStatus, BookTransactionCreate, BookTransactionUpdate

# Sample test data
SAMPLE_TRANSACTION_DATA = {
    "book_id": 1,
    "member_id": 1,
    "issue_date": date(2024, 1, 1),
    "due_date": date(2024, 1, 15),
    "return_date": None,
    "status": TransactionStatus.ISSUED
}

SAMPLE_TRANSACTION_RESPONSE = {
    "transaction_id": 1,
    **SAMPLE_TRANSACTION_DATA,
    "created_at": "2024-01-01"
}

# Mock date for consistent testing
MOCK_TODAY = date(2024, 1, 10)


@pytest.fixture
def mock_pool():
    """Mock database connection pool"""
    return AsyncMock()


@pytest.fixture
def mock_connect_db(mock_pool):
    """Mock connect_db function"""
    with patch('src.services.book_transaction_service.connect_db', return_value=mock_pool):
        yield mock_pool


@pytest.fixture
def mock_today():
    """Mock today's date for consistent testing"""
    with patch('src.services.book_transaction_service.date') as mock_date:
        mock_date.today.return_value = MOCK_TODAY
        yield mock_date


class TestBookTransactionService:

    # =============================
    # Test create_transaction method
    # =============================

    @pytest.mark.asyncio
    async def test_create_transaction_success(self, mock_connect_db):
        """Test successful transaction creation with all data"""
        # Arrange
        mock_transaction = MagicMock()
        mock_transaction.dict.return_value = SAMPLE_TRANSACTION_DATA

        # Create a simple dictionary-like mock
        mock_result = SAMPLE_TRANSACTION_RESPONSE

        with patch('src.services.book_transaction_service.BookTransactionRepository.create_transaction',
                   new_callable=AsyncMock) as mock_create_transaction:
            mock_create_transaction.return_value = mock_result

            # Act
            result = await BookTransactionService.create_transaction(mock_transaction)

            # Assert
            mock_create_transaction.assert_called_once_with(mock_connect_db, SAMPLE_TRANSACTION_DATA)
            assert result == {
                "message": "Transaction created successfully.<>..",
                "transaction": SAMPLE_TRANSACTION_RESPONSE
            }

    @pytest.mark.asyncio
    async def test_create_transaction_failure(self, mock_connect_db):
        """Test transaction creation failure"""
        # Arrange
        mock_transaction = MagicMock()
        mock_transaction.dict.return_value = SAMPLE_TRANSACTION_DATA

        with patch('src.services.book_transaction_service.BookTransactionRepository.create_transaction',
                   new_callable=AsyncMock) as mock_create_transaction:
            mock_create_transaction.return_value = None

            # Act
            result = await BookTransactionService.create_transaction(mock_transaction)

            # Assert
            assert result == {"error": "Failed to create transaction"}

    # ===========================
    # Test issue_book method
    # ===========================

    @pytest.mark.asyncio
    async def test_issue_book_success(self, mock_connect_db, mock_today):
        """Test successful book issuance"""
        # Arrange
        expected_result = {
            "transaction_id": 1,
            "issue_date": MOCK_TODAY,
            "due_date": MOCK_TODAY + timedelta(days=14)
        }

        with patch('src.services.book_transaction_service.BookTransactionRepository.is_book_available',
                   new_callable=AsyncMock) as mock_is_available, \
                patch('src.services.book_transaction_service.BookTransactionRepository.create_transaction',
                      new_callable=AsyncMock) as mock_create_transaction, \
                patch('src.services.book_transaction_service.BookLibraryConfig.DEFAULT_DUE_DAYS', 14):
            mock_is_available.return_value = True
            mock_create_transaction.return_value = expected_result

            # Act
            result = await BookTransactionService.issue_book(1, 1)

            # Assert
            mock_is_available.assert_called_once_with(mock_connect_db, 1)
            assert result == {
                "message": "Book issued successfully",
                "transaction_id": 1,
                "issue_date": MOCK_TODAY,
                "due_date": MOCK_TODAY + timedelta(days=14),
                "due_days": 14
            }

    @pytest.mark.asyncio
    async def test_issue_book_already_issued(self, mock_connect_db):
        """Test book issuance when book is already issued"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.is_book_available',
                   new_callable=AsyncMock) as mock_is_available:
            mock_is_available.return_value = False

            # Act
            result = await BookTransactionService.issue_book(1, 1)

            # Assert
            mock_is_available.assert_called_once_with(mock_connect_db, 1)
            assert result == {"error": "Book is already issued"}

    @pytest.mark.asyncio
    async def test_issue_book_failure(self, mock_connect_db, mock_today):
        """Test book issuance failure"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.is_book_available',
                   new_callable=AsyncMock) as mock_is_available, \
                patch('src.services.book_transaction_service.BookTransactionRepository.create_transaction',
                      new_callable=AsyncMock) as mock_create_transaction:
            mock_is_available.return_value = True
            mock_create_transaction.return_value = None

            # Act
            result = await BookTransactionService.issue_book(1, 1)

            # Assert
            assert result == {"error": "Failed to issue book"}

    # ===========================
    # Test return_book method
    # ===========================

    @pytest.mark.asyncio
    async def test_return_book_success(self, mock_connect_db):
        """Test successful book return"""
        # Arrange
        mock_transaction = {"return_date": None}

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction, \
                patch('src.services.book_transaction_service.BookTransactionRepository.mark_as_returned',
                      new_callable=AsyncMock) as mock_mark_returned:
            mock_get_transaction.return_value = mock_transaction
            mock_mark_returned.return_value = {"transaction_id": 1}

            # Act
            result = await BookTransactionService.return_book(1)

            # Assert
            mock_get_transaction.assert_called_once_with(mock_connect_db, 1)
            mock_mark_returned.assert_called_once_with(mock_connect_db, 1)
            assert result == {"message": "Book returned successfully"}

    @pytest.mark.asyncio
    async def test_return_book_transaction_not_found(self, mock_connect_db):
        """Test book return when transaction doesn't exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction:
            mock_get_transaction.return_value = None

            # Act
            result = await BookTransactionService.return_book(999)

            # Assert
            assert result == {"error": "Transaction not found"}

    @pytest.mark.asyncio
    async def test_return_book_already_returned(self, mock_connect_db):
        """Test book return when book is already returned"""
        # Arrange
        mock_transaction = {"return_date": date(2024, 1, 5)}

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction:
            mock_get_transaction.return_value = mock_transaction

            # Act
            result = await BookTransactionService.return_book(1)

            # Assert
            assert result == {"error": "Book already returned"}

    @pytest.mark.asyncio
    async def test_return_book_failure(self, mock_connect_db):
        """Test book return failure"""
        # Arrange
        mock_transaction = {"return_date": None}

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction, \
                patch('src.services.book_transaction_service.BookTransactionRepository.mark_as_returned',
                      new_callable=AsyncMock) as mock_mark_returned:
            mock_get_transaction.return_value = mock_transaction
            mock_mark_returned.return_value = None

            # Act
            result = await BookTransactionService.return_book(1)

            # Assert
            assert result == {"error": "Failed to return book"}

    # ===============================
    # Test get_issued_books method
    # ===============================

    @pytest.mark.asyncio
    async def test_get_issued_books_success(self, mock_connect_db):
        """Test successful retrieval of issued books"""
        # Arrange
        sample_transactions = [
            {"transaction_id": 1, "book_id": 1, "status": "Issued"},
            {"transaction_id": 2, "book_id": 2, "status": "Issued"}
        ]

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_active_transactions',
                   new_callable=AsyncMock) as mock_get_active:
            mock_get_active.return_value = sample_transactions

            # Act
            result = await BookTransactionService.get_issued_books()

            # Assert
            mock_get_active.assert_called_once_with(mock_connect_db)
            assert result == {"issued_books": sample_transactions}

    @pytest.mark.asyncio
    async def test_get_issued_books_empty(self, mock_connect_db):
        """Test retrieval of issued books when none exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_active_transactions',
                   new_callable=AsyncMock) as mock_get_active:
            mock_get_active.return_value = []

            # Act
            result = await BookTransactionService.get_issued_books()

            # Assert
            assert result == {"issued_books": []}

    # ===============================
    # Test get_overdue_books method
    # ===============================

    @pytest.mark.asyncio
    async def test_get_overdue_books_success(self, mock_connect_db):
        """Test successful retrieval of overdue books"""
        # Arrange
        sample_transactions = [
            {"transaction_id": 1, "book_id": 1, "status": "Overdue"},
            {"transaction_id": 2, "book_id": 2, "status": "Overdue"}
        ]

        with patch('src.services.book_transaction_service.BookTransactionRepository.update_overdue_status',
                   new_callable=AsyncMock) as mock_update_status, \
                patch('src.services.book_transaction_service.BookTransactionRepository.get_overdue_transactions',
                      new_callable=AsyncMock) as mock_get_overdue:
            mock_update_status.return_value = None
            mock_get_overdue.return_value = sample_transactions

            # Act
            result = await BookTransactionService.get_overdue_books()

            # Assert
            mock_update_status.assert_called_once_with(mock_connect_db)
            mock_get_overdue.assert_called_once_with(mock_connect_db)
            assert result == {"overdue_books": sample_transactions}

    @pytest.mark.asyncio
    async def test_get_overdue_books_empty(self, mock_connect_db):
        """Test retrieval of overdue books when none exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.update_overdue_status',
                   new_callable=AsyncMock) as mock_update_status, \
                patch('src.services.book_transaction_service.BookTransactionRepository.get_overdue_transactions',
                      new_callable=AsyncMock) as mock_get_overdue:
            mock_update_status.return_value = None
            mock_get_overdue.return_value = []

            # Act
            result = await BookTransactionService.get_overdue_books()

            # Assert
            assert result == {"overdue_books": []}

    # ====================================
    # Test get_member_issued_books method
    # ====================================

    @pytest.mark.asyncio
    async def test_get_member_issued_books_success(self, mock_connect_db):
        """Test successful retrieval of member's issued books"""
        # Arrange
        sample_transactions = [
            {"transaction_id": 1, "book_id": 1, "status": "Issued"},
            {"transaction_id": 2, "book_id": 2, "status": "Overdue"}
        ]

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transactions_by_member',
                   new_callable=AsyncMock) as mock_get_member_transactions:
            mock_get_member_transactions.return_value = sample_transactions

            # Act
            result = await BookTransactionService.get_member_issued_books(1)

            # Assert
            mock_get_member_transactions.assert_called_once_with(mock_connect_db, 1)
            assert result == sample_transactions  # Returns as-is, service doesn't filter

    @pytest.mark.asyncio
    async def test_get_member_issued_books_empty(self, mock_connect_db):
        """Test retrieval of member's issued books when none exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transactions_by_member',
                   new_callable=AsyncMock) as mock_get_member_transactions:
            mock_get_member_transactions.return_value = []

            # Act
            result = await BookTransactionService.get_member_issued_books(1)

            # Assert
            assert result == []

    # ================================
    # Test get_transaction method
    # ================================

    @pytest.mark.asyncio
    async def test_get_transaction_success(self, mock_connect_db):
        """Test successful transaction retrieval"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction:
            mock_get_transaction.return_value = SAMPLE_TRANSACTION_RESPONSE

            # Act
            result = await BookTransactionService.get_transaction(1)

            # Assert
            mock_get_transaction.assert_called_once_with(mock_connect_db, 1)
            assert result == {"transaction": SAMPLE_TRANSACTION_RESPONSE}

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, mock_connect_db):
        """Test transaction retrieval when transaction doesn't exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transaction_by_id',
                   new_callable=AsyncMock) as mock_get_transaction:
            mock_get_transaction.return_value = None

            # Act
            result = await BookTransactionService.get_transaction(999)

            # Assert
            assert result == {"error": "Transaction not found"}

    # =================================
    # Test update_transaction method
    # =================================

    @pytest.mark.asyncio
    async def test_update_transaction_success(self, mock_connect_db):
        """Test successful transaction update"""
        # Arrange
        mock_update_data = MagicMock()
        update_dict = {"return_date": date(2024, 1, 5), "status": TransactionStatus.RETURNED}
        mock_update_data.dict.return_value = update_dict

        expected_result = {**SAMPLE_TRANSACTION_RESPONSE, **update_dict}

        with patch('src.services.book_transaction_service.BookTransactionRepository.update_transaction',
                   new_callable=AsyncMock) as mock_update_transaction:
            mock_update_transaction.return_value = expected_result

            # Act
            result = await BookTransactionService.update_transaction(1, mock_update_data)

            # Assert
            mock_update_transaction.assert_called_once_with(mock_connect_db, 1, update_dict)
            assert result == {
                "message": "Transaction updated successfully",
                "transaction": expected_result
            }

    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, mock_connect_db):
        """Test transaction update when transaction doesn't exist"""
        # Arrange
        mock_update_data = MagicMock()
        mock_update_data.dict.return_value = {"return_date": date(2024, 1, 5)}

        with patch('src.services.book_transaction_service.BookTransactionRepository.update_transaction',
                   new_callable=AsyncMock) as mock_update_transaction:
            mock_update_transaction.return_value = None

            # Act
            result = await BookTransactionService.update_transaction(999, mock_update_data)

            # Assert
            assert result == {"error": "Transaction not found"}

    # ========================================
    # Test get_book_issued_members method
    # ========================================

    @pytest.mark.asyncio
    async def test_get_book_issued_members_success(self, mock_connect_db):
        """Test successful retrieval of book issued members"""
        # Arrange
        sample_members = [
            {"member_id": 1, "first_name": "John", "last_name": "Doe"},
            {"member_id": 2, "first_name": "Jane", "last_name": "Smith"}
        ]

        with patch('src.services.book_transaction_service.BookTransactionRepository.get_book_issued_members',
                   new_callable=AsyncMock) as mock_get_issued_members:
            mock_get_issued_members.return_value = sample_members

            # Act
            result = await BookTransactionService.get_book_issued_members(1)

            # Assert
            mock_get_issued_members.assert_called_once_with(mock_connect_db, 1)
            assert result == {"book_issued_members": sample_members}

    @pytest.mark.asyncio
    async def test_get_book_issued_members_empty(self, mock_connect_db):
        """Test retrieval of book issued members when none exist"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_book_issued_members',
                   new_callable=AsyncMock) as mock_get_issued_members:
            mock_get_issued_members.return_value = []

            # Act
            result = await BookTransactionService.get_book_issued_members(1)

            # Assert
            assert result == {"book_issued_members": []}

    # ========================
    # Test edge cases
    # ========================

    @pytest.mark.asyncio
    async def test_create_transaction_with_none_data(self, mock_connect_db):
        """Test transaction creation with None data"""
        # Arrange
        mock_transaction = None

        # Act & Assert
        with pytest.raises(AttributeError):
            await BookTransactionService.create_transaction(mock_transaction)

    @pytest.mark.asyncio
    async def test_get_member_issued_books_with_invalid_id(self, mock_connect_db):
        """Test member issued books with invalid member ID"""
        # Arrange
        with patch('src.services.book_transaction_service.BookTransactionRepository.get_transactions_by_member',
                   new_callable=AsyncMock) as mock_get_member_transactions:
            mock_get_member_transactions.return_value = []

            # Act
            result = await BookTransactionService.get_member_issued_books(-1)

            # Assert
            assert result == []