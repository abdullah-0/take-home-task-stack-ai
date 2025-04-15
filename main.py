from fastapi import FastAPI

from app.routes import library_router, document_router, chunk_router

app = FastAPI(title="TAH Task BE(VectorDB)")

# Register routes
app.include_router(library_router)
app.include_router(document_router)
app.include_router(chunk_router)
