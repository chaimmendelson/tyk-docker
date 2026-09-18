from typing import List, Optional

import strawberry
import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Book:
    id: int
    title: str
    author: str


books: List[Book] = [
    Book(id=1, title="Dune", author="Frank Herbert"),
    Book(id=2, title="Neuromancer", author="William Gibson"),
]


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> List[Book]:
        return books

    @strawberry.field
    def book(self, id: int) -> Optional[Book]:
        return next((b for b in books if b.id == id), None)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        new_book = Book(id=len(books) + 1, title=title, author=author)
        books.append(new_book)
        return new_book


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(
    version="1.0.0",
)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
