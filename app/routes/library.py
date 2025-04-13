
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path

from app.core.v_db import VectorDB
from app.schemas import Library, LibraryCreate, LibraryUpdate
from app.utils import get_db

router = APIRouter()




@router.post("/", response_model=Library, status_code=status.HTTP_201_CREATED)
def create_library(library: LibraryCreate, db: VectorDB = Depends(get_db)):
    library_id = db.create_library(library.name, library.metadata)
    return db.get_library(library_id)


@router.get("/", response_model=List[Library])
def list_libraries(db: VectorDB = Depends(get_db)):
    return db.get_all_libraries()


@router.get("/{library_id}", response_model=Library)
def get_library(
        library_id: str = Path(..., description="The ID of the library"),
        db: VectorDB = Depends(get_db)
):
    library = db.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library


@router.put("/{library_id}", response_model=Library)
def update_library(
        library_id: str,
        library_update: LibraryUpdate,
        db: VectorDB = Depends(get_db)
):
    if not db.library_exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")

    db.update_library(library_id, library_update.name, library_update.metadata)
    return db.get_library(library_id)


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(
        library_id: str,
        db: VectorDB = Depends(get_db)
):
    if not db.delete_library(library_id):
        raise HTTPException(status_code=404, detail="Library not found")