import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import HTTPException
from asyncpg.exceptions import UniqueViolationError

from src.services.book_service import BookService

# Sample test data
SAMPLE_BOOK_DATA = {
    "title": "Test Book",
    "author": "Test Author",
    "isbn": "1234567890",
    "publication_year": 2024,
    "publisher": "Test Publisher",
    "genre": "Fiction",
    "total_copies": 10,
    "available_copies": 10
}

SAMPLE_BOOK_RESPONSE = {
    "book_id": 1,
    **SAMPLE_BOOK_DATA,
    "created_at": "2024-01-01"
}

SAMPLE_BOOKS_LIST = [
    {**SAMPLE_BOOK_RESPONSE, "book_id": 1},
    {**SAMPLE_BOOK_RESPONSE, "book_id": 2, "title": "Another Book"}
]


@pytest.fixture
def mock_pool():
    """Mock database connection pool"""
    return AsyncMock()


@pytest.fixture
def mock_connect_db(mock_pool):
    """Mock connect_db function"""
    with patch('src.services.book_service.connect_db', return_value=mock_pool):
        yield mock_pool


class TestBookService:

    # ====================
    # Test add_book method
    # ====================

    @pytest.mark.asyncio
    async def test_add_book_success(self, mock_connect_db):
        """Test successful book addition"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = SAMPLE_BOOK_DATA

        # Create an AsyncMock for the repository method
        with patch('src.services.book_service.BookRepository.create_book', new_callable=AsyncMock) as mock_create_book:
            mock_create_book.return_value = 1

            # Act
            result = await BookService.add_book(mock_book)

            # Assert
            mock_create_book.assert_called_once_with(mock_connect_db, SAMPLE_BOOK_DATA)
            assert result == {"message": "Book added successfully", "book_id": 1}

    @pytest.mark.asyncio
    async def test_add_book_duplicate_isbn(self, mock_connect_db):
        """Test book addition with duplicate ISBN"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = SAMPLE_BOOK_DATA

        with patch('src.services.book_service.BookRepository.create_book', new_callable=AsyncMock) as mock_create_book:
            mock_create_book.side_effect = UniqueViolationError

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.add_book(mock_book)

            # Assert
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "ISBN already exists"
            mock_create_book.assert_called_once_with(mock_connect_db, SAMPLE_BOOK_DATA)

    @pytest.mark.asyncio
    async def test_add_book_database_error(self, mock_connect_db):
        """Test book addition with database error"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = SAMPLE_BOOK_DATA

        with patch('src.services.book_service.BookRepository.create_book', new_callable=AsyncMock) as mock_create_book:
            mock_create_book.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await BookService.add_book(mock_book)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ====================
    # Test get_book method
    # ====================

    @pytest.mark.asyncio
    async def test_get_book_success(self, mock_connect_db):
        """Test successful book retrieval"""
        # Arrange
        # Create a mock that behaves like a dictionary and also has a dict() method
        mock_row = MagicMock()
        mock_row.items.return_value = SAMPLE_BOOK_RESPONSE.items()
        mock_row.keys.return_value = SAMPLE_BOOK_RESPONSE.keys()
        mock_row.values.return_value = SAMPLE_BOOK_RESPONSE.values()
        mock_row.__getitem__.side_effect = lambda key: SAMPLE_BOOK_RESPONSE[key]

        # Mock the dict() function when called on the row
        with patch('src.services.book_service.BookRepository.get_book_by_id', new_callable=AsyncMock) as mock_get_book:
            mock_get_book.return_value = mock_row

            # Act
            result = await BookService.get_book(1)

            # Assert
            mock_get_book.assert_called_once_with(mock_connect_db, 1)
            assert result == SAMPLE_BOOK_RESPONSE

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, mock_connect_db):
        """Test book retrieval when book doesn't exist"""
        # Arrange
        with patch('src.services.book_service.BookRepository.get_book_by_id', new_callable=AsyncMock) as mock_get_book:
            mock_get_book.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.get_book(999)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Book not found"
            mock_get_book.assert_called_once_with(mock_connect_db, 999)

    @pytest.mark.asyncio
    async def test_get_book_database_error(self, mock_connect_db):
        """Test book retrieval with database error"""
        # Arrange
        with patch('src.services.book_service.BookRepository.get_book_by_id', new_callable=AsyncMock) as mock_get_book:
            mock_get_book.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await BookService.get_book(1)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ======================
    # Test list_books method
    # ======================

    @pytest.mark.asyncio
    async def test_list_books_success(self, mock_connect_db):
        """Test successful listing of books"""
        # Arrange
        # Create mock rows that can be converted to dict using dict()
        mock_rows = []
        for book_data in SAMPLE_BOOKS_LIST:
            mock_row = MagicMock()
            mock_row.items.return_value = book_data.items()
            mock_row.keys.return_value = book_data.keys()
            mock_row.values.return_value = book_data.values()
            mock_row.__getitem__.side_effect = lambda key, bd=book_data: bd[key]
            mock_rows.append(mock_row)

        with patch('src.services.book_service.BookRepository.get_all_books',
                   new_callable=AsyncMock) as mock_get_all_books:
            mock_get_all_books.return_value = mock_rows

            # Act
            result = await BookService.list_books()

            # Assert
            mock_get_all_books.assert_called_once_with(mock_connect_db)
            assert result == SAMPLE_BOOKS_LIST
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_books_empty(self, mock_connect_db):
        """Test listing books when no books exist"""
        # Arrange
        with patch('src.services.book_service.BookRepository.get_all_books',
                   new_callable=AsyncMock) as mock_get_all_books:
            mock_get_all_books.return_value = []

            # Act
            result = await BookService.list_books()

            # Assert
            mock_get_all_books.assert_called_once_with(mock_connect_db)
            assert result == []

    @pytest.mark.asyncio
    async def test_list_books_database_error(self, mock_connect_db):
        """Test listing books with database error"""
        # Arrange
        with patch('src.services.book_service.BookRepository.get_all_books',
                   new_callable=AsyncMock) as mock_get_all_books:
            mock_get_all_books.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await BookService.list_books()

            # Assert
            assert str(exc_info.value) == "Database error"

    # ========================
    # Test update_book method
    # ========================

    @pytest.mark.asyncio
    async def test_update_book_success(self, mock_connect_db):
        """Test successful book update"""
        # Arrange
        mock_book = MagicMock()
        update_data = {"title": "Updated Title", "author": "Updated Author"}
        mock_book.dict.return_value = update_data

        with patch('src.services.book_service.BookRepository.update_book', new_callable=AsyncMock) as mock_update_book:
            mock_update_book.return_value = 1

            # Act
            result = await BookService.update_book(1, mock_book)

            # Assert
            mock_update_book.assert_called_once_with(
                mock_connect_db, 1, update_data
            )
            assert result == {"message": "Book updated successfully"}

    @pytest.mark.asyncio
    async def test_update_book_not_found(self, mock_connect_db):
        """Test book update when book doesn't exist"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = {"title": "Updated Title"}

        with patch('src.services.book_service.BookRepository.update_book', new_callable=AsyncMock) as mock_update_book:
            mock_update_book.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.update_book(999, mock_book)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Book not found"
            mock_update_book.assert_called_once_with(
                mock_connect_db, 999, {"title": "Updated Title"}
            )

    @pytest.mark.asyncio
    async def test_update_book_database_error(self, mock_connect_db):
        """Test book update with database error"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = {"title": "Updated Title"}

        with patch('src.services.book_service.BookRepository.update_book', new_callable=AsyncMock) as mock_update_book:
            mock_update_book.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await BookService.update_book(1, mock_book)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ========================
    # Test delete_book method
    # ========================

    @pytest.mark.asyncio
    async def test_delete_book_success(self, mock_connect_db):
        """Test successful book deletion"""
        # Arrange
        with patch('src.services.book_service.BookRepository.delete_book', new_callable=AsyncMock) as mock_delete_book:
            mock_delete_book.return_value = "DELETE 1"

            # Act
            result = await BookService.delete_book(1)

            # Assert
            mock_delete_book.assert_called_once_with(mock_connect_db, 1)
            assert result == {"message": "Book deleted successfully"}

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, mock_connect_db):
        """Test book deletion when book doesn't exist"""
        # Arrange
        with patch('src.services.book_service.BookRepository.delete_book', new_callable=AsyncMock) as mock_delete_book:
            mock_delete_book.return_value = "DELETE 0"

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.delete_book(999)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Book not found"
            mock_delete_book.assert_called_once_with(mock_connect_db, 999)

    @pytest.mark.asyncio
    async def test_delete_book_database_error(self, mock_connect_db):
        """Test book deletion with database error"""
        # Arrange
        with patch('src.services.book_service.BookRepository.delete_book', new_callable=AsyncMock) as mock_delete_book:
            mock_delete_book.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await BookService.delete_book(1)

            # Assert
            assert str(exc_info.value) == "Database error"

    # ========================
    # Test edge cases
    # ========================

    @pytest.mark.asyncio
    async def test_add_book_with_none_data(self, mock_connect_db):
        """Test book addition with None book object"""
        # Arrange
        mock_book = None

        # Act & Assert
        with pytest.raises(AttributeError):
            await BookService.add_book(mock_book)

    @pytest.mark.asyncio
    async def test_get_book_with_invalid_id(self, mock_connect_db):
        """Test book retrieval with invalid ID"""
        # Arrange
        with patch('src.services.book_service.BookRepository.get_book_by_id', new_callable=AsyncMock) as mock_get_book:
            mock_get_book.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.get_book(-1)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Book not found"

    @pytest.mark.asyncio
    async def test_update_book_with_empty_data(self, mock_connect_db):
        """Test book update with empty update data"""
        # Arrange
        mock_book = MagicMock()
        mock_book.dict.return_value = {}

        with patch('src.services.book_service.BookRepository.update_book', new_callable=AsyncMock) as mock_update_book:
            mock_update_book.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await BookService.update_book(999, mock_book)

            # Assert
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Book not found"
            mock_update_book.assert_called_once_with(mock_connect_db, 999, {})

    # ========================
    # Test concurrency
    # ========================

    @pytest.mark.asyncio
    async def test_concurrent_book_operations(self, mock_connect_db):
        """Test concurrent book operations"""
        # Arrange
        mock_book1 = MagicMock()
        mock_book1.dict.return_value = SAMPLE_BOOK_DATA

        # Mock row for get_book
        mock_row = MagicMock()
        mock_row.items.return_value = SAMPLE_BOOK_RESPONSE.items()
        mock_row.keys.return_value = SAMPLE_BOOK_RESPONSE.keys()
        mock_row.values.return_value = SAMPLE_BOOK_RESPONSE.values()
        mock_row.__getitem__.side_effect = lambda key: SAMPLE_BOOK_RESPONSE[key]

        # Mock rows for list_books
        mock_rows = []
        for book_data in SAMPLE_BOOKS_LIST:
            mock_row_list = MagicMock()
            mock_row_list.items.return_value = book_data.items()
            mock_row_list.keys.return_value = book_data.keys()
            mock_row_list.values.return_value = book_data.values()
            mock_row_list.__getitem__.side_effect = lambda key, bd=book_data: bd[key]
            mock_rows.append(mock_row_list)

        # Mock repository methods with AsyncMock
        with patch('src.services.book_service.BookRepository.create_book', new_callable=AsyncMock) as mock_create_book, \
                patch('src.services.book_service.BookRepository.get_book_by_id',
                      new_callable=AsyncMock) as mock_get_book, \
                patch('src.services.book_service.BookRepository.get_all_books',
                      new_callable=AsyncMock) as mock_get_all_books:
            mock_create_book.return_value = 1
            mock_get_book.return_value = mock_row
            mock_get_all_books.return_value = mock_rows

            # Act - Run operations concurrently
            tasks = [
                BookService.add_book(mock_book1),
                BookService.get_book(1),
                BookService.list_books()
            ]

            results = await asyncio.gather(*tasks)

            # Assert
            assert len(results) == 3
            assert results[0] == {"message": "Book added successfully", "book_id": 1}
            assert results[1] == SAMPLE_BOOK_RESPONSE
            assert results[2] == SAMPLE_BOOKS_LIST