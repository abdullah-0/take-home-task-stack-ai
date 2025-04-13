
import json
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Dict, List, Optional
from uuid import uuid4


class VectorDB:
    def __init__(self, storage_path: str = "data/vectordb"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.libraries: Dict[str, dict] = {}
        self.documents: Dict[str, dict] = {}
        self.chunks: Dict[str, dict] = {}
        self.lock = RLock()

        self.load_from_disk()

    def save_to_disk(self):
        with self.lock:
            data = {
                "libraries": self.libraries,
                "documents": self.documents,
                "chunks": self.chunks
            }
            with open(self.storage_path / "db.json", "w") as f:
                json.dump(data, f, default=str)

    def load_from_disk(self):
        try:
            with open(self.storage_path / "db.json", "r") as f:
                data = json.load(f)
                self.libraries = data.get("libraries", {})
                self.documents = data.get("documents", {})
                self.chunks = data.get("chunks", {})
        except FileNotFoundError:
            pass

    # Library CRUD
    def create_library(self, name: str, metadata: dict = None) -> str:
        with self.lock:
            library_id = f"lib_{uuid4().hex}"
            self.libraries[library_id] = {
                "id": library_id,
                "name": name,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            self.save_to_disk()
            return library_id

    # Add similar methods for documents/chunks
    # ...

    def get_chunk_embedding(self, chunk_id: str) -> Optional[List[float]]:
        with self.lock:
            chunk = self.chunks.get(chunk_id)
            return chunk.get("embedding") if chunk else None