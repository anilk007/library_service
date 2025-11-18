import asyncio
from concurrent import futures
import time

import grpc

# Import the generated stubs and messages
# Note: These files (book_pb2.py and book_pb2_grpc.py) must be generated
# using the 'protoc' command (see instructions above)
import book_pb2
import book_pb2_grpc

# In-memory "database" to store created books
BOOK_DATABASE = []


class BookServiceServicer(book_pb2_grpc.BookServiceServicer):
    """Implements the gRPC BookService defined in the proto file."""

    async def CreateBook(self, request, context):
        """Handles the CreateBook RPC."""
        book = request.book

        # Simple validation: Check if required fields are present
        if not book.title or not book.author:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Book title and author are required.")
            return book_pb2.CreateBookResponse(
                success=False,
                message="Missing required book information."
            )

        # Process the request: Store the book in the database
        BOOK_DATABASE.append({
            "title": book.title,
            "author": book.author,
            "timestamp": time.time()
        })

        print(f"Server received and stored new book:")
        print(f"  Title: {book.title}")
        print(f"  Author: {book.author}")
        print("-" * 20)

        # Return a successful response
        return book_pb2.CreateBookResponse(
            success=True,
            message=f"Book '{book.title}' created successfully."
        )


async def serve():
    """Starts the gRPC asynchronous server."""
    # Using the asynchronous server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    book_pb2_grpc.add_BookServiceServicer_to_server(
        BookServiceServicer(), server
    )

    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("gRPC Book Service server started. Listening on port 50051...")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Stop the server cleanly on keyboard interrupt
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(serve())