from fastapi import FastAPI

from app.routes import library_router, document_router, chunk_router

app = FastAPI(title="TAH Task BE(VectorDB)")

# Register routes
app.include_router(library_router, prefix="/v1/library", tags=["Library"])
app.include_router(document_router, prefix="/v1/document", tags=["Document"])
app.include_router(chunk_router, prefix="/v1/chunk", tags=["Chunk"])
