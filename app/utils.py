import math
from typing import List


def linear_scan(vectors: List[List[float]], query: List[float], top_k: int):
    similarities = [
        (i, cosine_similarity(vec, query)) for i, vec in enumerate(vectors)
    ]
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot / (norm1 * norm2 + 1e-10)



class GridIndex:
    def __init__(self, bin_size: float):
        self.bins = {}  # e.g., {(0, 1, 2): [chunk_ids]}
        self.bin_size = bin_size

    def _get_bin_key(self, vector):
        return tuple(int(x // self.bin_size) for x in vector)

    def add(self, vector: List[float], chunk_id: str):
        key = self._get_bin_key(vector)
        self.bins.setdefault(key, []).append((chunk_id, vector))

    def search(self, query_vector: List[float]):
        key = self._get_bin_key(query_vector)
        return self.bins.get(key, [])


class InvertedIndex:
    def __init__(self):
        self.index = {}

    def add(self, token: str, chunk_id: str):
        self.index.setdefault(token.lower(), set()).add(chunk_id)

    def search(self, token: str) -> set:
        return self.index.get(token.lower(), set())

