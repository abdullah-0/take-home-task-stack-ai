from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.document import Document


class LibraryBase(BaseModel):
    name: str
    metadata: Optional[dict] = None


class LibraryCreate(LibraryBase):
    pass


class LibraryUpdate(LibraryBase):
    pass


class Library(LibraryBase):
    id: str
    created_at: datetime
    documents: List[Document] = Field(default_factory=list)
