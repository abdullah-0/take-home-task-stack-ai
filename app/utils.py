from datetime import datetime
from uuid import uuid4

from app.core.v_db import VectorDB


def generate_id() -> str:
    return f"lib_{uuid4().hex}"


def get_current_time() -> datetime:
    return datetime.now()


def get_db():
    db = VectorDB()
    try:
        yield db
    finally:
        db.save_to_disk()
