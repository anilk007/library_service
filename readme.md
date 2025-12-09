
py -m pip install -r requirements.txt

(1) py -m pip install asyncpg --only-binary=all

>pip install -r requirements.txt

py -m pip install -r requirements.txt

pip install fastapi uvicorn[standard] asyncpg pydantic python-dotenv

py -m pip install fastapi

py -m pip install uvicorn[standard]

py -m pip install pydantic

py -m pip install python-dotenv

py -m pip install asyncpg

py -m pip install "pydantic[email]"

"C:\Users\hello\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv

python -m venv venv

py -m venv venv

venv\Scripts\activate

>uvicorn main:app --reload

(2) PostgreSQL Schema script is available in postgresql_scripts folder.

(3) Generate the Protobuf Message File

protoc --js_out=import_style=commonjs,binary:. --proto_path=. book.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. member.proto
protoc --js_out=import_style=commonjs,binary:. --proto_path=. borrowing_records.proto

(4) pip install grpcio grpcio-tools

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. book.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. member.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. borrowing_records.proto

(5) py server.py

gRPC Book Service server is listening on port 50051.

(6) Run tests

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_book_service.py -v

# Run with coverage
pytest --cov=src.services.book_service

# Run specific test method
pytest tests/test_book_service.py::TestBookService::test_add_book_success -v

(7)
pytest --cov=src

(8)
# Run all member service tests
pytest tests/unit/services/test_member_service.py -v

# Run with coverage
pytest tests/unit/services/test_member_service.py --cov=src.services.member_service --cov-report=term-missing

# Run all service tests
pytest tests/unit/services/ --cov=src.services --cov-report=term-missing

# Run all transaction service tests
pytest tests/unit/services/test_book_transaction_service.py -v

# Run with coverage
pytest tests/unit/services/test_book_transaction_service.py --cov=src.services.book_transaction_service --cov-report=term-missing

# Run all service tests
pytest tests/unit/services/ --cov=src.services --cov-report=term-missing

(6) issues

(a) access denied