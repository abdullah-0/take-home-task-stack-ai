import datetime
import json
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
                "chunks": self.chunks,
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

    # === LIBRARY ===
    def create_library(self, name: str, metadata: dict = None) -> str:
        with self.lock:
            library_id = f"lib_{uuid4().hex}"
            self.libraries[library_id] = {
                "id": library_id,
                "name": name,
                "metadata": metadata or {},
                "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            }
            self.save_to_disk()
            return library_id

    def get_library(self, library_id: str) -> Optional[dict]:
        library = self.libraries.get(library_id)
        if not library:
            return None

        # Deep copy to avoid mutating original
        library_copy = library.copy()
        documents = []
        for doc_id, doc in self.documents.items():
            if doc["library_id"] == library_id:
                doc_copy = doc.copy()
                doc_copy["chunks"] = [
                    self.chunks[chk_id]
                    for chk_id, chk in self.chunks.items()
                    if chk["document_id"] == doc_id
                ]
                documents.append(doc_copy)

        library_copy["documents"] = documents
        return library_copy

    def get_all_libraries(self) -> List[dict]:
        return list(self.libraries.values())

    def update_library(self, library_id: str, name: str, metadata: dict):
        with self.lock:
            if library_id in self.libraries:
                self.libraries[library_id]["name"] = name
                self.libraries[library_id]["metadata"] = metadata or {}
                self.save_to_disk()

    def delete_library(self, library_id: str) -> bool:
        with self.lock:
            if library_id in self.libraries:
                # Also delete related documents and chunks
                doc_ids = [
                    doc_id
                    for doc_id, doc in self.documents.items()
                    if doc["library_id"] == library_id
                ]
                for doc_id in doc_ids:
                    self.delete_document(doc_id)
                del self.libraries[library_id]
                self.save_to_disk()
                return True
            return False

    def library_exists(self, library_id: str) -> bool:
        return library_id in self.libraries

    # === DOCUMENT ===
    def create_document(
        self, library_id: str, title: str, metadata: dict = None
    ) -> str:
        with self.lock:
            document_id = f"doc_{uuid4().hex}"
            self.documents[document_id] = {
                "id": document_id,
                "library_id": library_id,
                "title": title,
                "metadata": metadata or {},
                "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            }
            self.save_to_disk()
            return document_id

    def get_document(self, document_id: str) -> Optional[dict]:
        document = self.documents.get(document_id)
        if not document:
            return None

        document_copy = document.copy()
        document_copy["chunks"] = [
            self.chunks[chk_id]
            for chk_id, chk in self.chunks.items()
            if chk["document_id"] == document_id
        ]
        return document_copy

    def update_document(self, document_id: str, title: str, metadata: dict):
        with self.lock:
            if document_id in self.documents:
                self.documents[document_id]["title"] = title
                self.documents[document_id]["metadata"] = metadata or {}
                self.save_to_disk()

    def delete_document(self, document_id: str) -> bool:
        with self.lock:
            if document_id in self.documents:
                # Also delete associated chunks
                chunk_ids = [
                    cid
                    for cid, c in self.chunks.items()
                    if c["document_id"] == document_id
                ]
                for cid in chunk_ids:
                    del self.chunks[cid]
                del self.documents[document_id]
                self.save_to_disk()
                return True
            return False

    def document_exists(self, document_id: str) -> bool:
        return document_id in self.documents

    # === CHUNK ===
    def create_chunk(
        self,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: dict = None,
    ) -> str:
        with self.lock:
            chunk_id = f"chk_{uuid4().hex}"
            self.chunks[chunk_id] = {
                "id": chunk_id,
                "document_id": document_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            }
            self.save_to_disk()
            return chunk_id

    def get_chunk(self, chunk_id: str) -> Optional[dict]:
        chunk = self.chunks.get(chunk_id)
        if not chunk:
            return None

        chunk_copy = chunk.copy()
        doc = self.documents.get(chunk["document_id"])
        if doc:
            chunk_copy["document_title"] = doc["title"]
            chunk_copy["library_id"] = doc["library_id"]
        return chunk_copy

    def update_chunk(
        self, chunk_id: str, content: str, embedding: List[float], metadata: dict
    ):
        with self.lock:
            if chunk_id in self.chunks:
                self.chunks[chunk_id]["content"] = content
                self.chunks[chunk_id]["embedding"] = embedding
                self.chunks[chunk_id]["metadata"] = metadata or {}
                self.save_to_disk()

    def delete_chunk(self, chunk_id: str) -> bool:
        with self.lock:
            if chunk_id in self.chunks:
                del self.chunks[chunk_id]
                self.save_to_disk()
                return True
            return False

    def chunk_exists(self, chunk_id: str) -> bool:
        return chunk_id in self.chunks

    def get_chunk_embedding(self, chunk_id: str) -> Optional[List[float]]:
        chunk = self.chunks.get(chunk_id)
        return chunk.get("embedding") if chunk else None
