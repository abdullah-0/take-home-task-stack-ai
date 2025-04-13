from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel


class ChunkBase(BaseModel):
    text: str
    embedding: List[float]
    metadata: Dict[str, str] = {}


class ChunkCreate(ChunkBase):
    pass
class ChunkUpdate(ChunkBase):
    pass

class Chunk(ChunkBase):
    id: str
    document_id: str
    created_at: datetime


class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass


class Document(DocumentBase):
    id: str
    library_id: str
    chunks: List[Chunk] = []
    created_at: datetime


class LibraryBase(BaseModel):
    name: str


class LibraryCreate(LibraryBase):
    pass

class LibraryUpdate(LibraryBase):
    pass


class Library(LibraryBase):
    id: str
    documents: List[Document] = []
    created_at: datetime
