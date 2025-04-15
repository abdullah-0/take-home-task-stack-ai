from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.core.v_db import VectorDB
from app.schemas.library import Library, LibraryCreate, LibraryUpdate

router = APIRouter(prefix="/v1/library",tags=["Library"])
db = VectorDB()


@router.post("/", response_model=Library, status_code=status.HTTP_201_CREATED)
def create_library(library: LibraryCreate):
    library_id = db.create_library(name=library.name, metadata=library.metadata)
    created = db.get_library(library_id)
    if not created:
        raise HTTPException(status_code=500, detail="Library creation failed")
    return created


@router.get("/", response_model=List[Library])
def list_libraries():
    return db.get_all_libraries()  # already includes documents & chunks


@router.get("/{library_id}", response_model=Library)
def get_library(library_id: str = Path(..., description="The ID of the library")):
    lib = db.get_library(library_id)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib  # already enriched


@router.put("/{library_id}", response_model=Library)
def update_library(library_id: str, library_update: LibraryUpdate):
    if not db.library_exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    db.update_library(
        library_id, name=library_update.name, metadata=library_update.metadata
    )
    updated = db.get_library(library_id)
    return updated


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(library_id: str):
    deleted = db.delete_library(library_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Library not found")
