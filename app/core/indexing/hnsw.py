# src/vectordb/core/indexing/hnsw.py
import heapq
from typing import List, Tuple

import numpy as np


class HNSWIndex:
    def __init__(self, m: int = 5, ef: int = 10, m0: int = None):
        self.m = m  # Number of connections per layer
        self.ef = ef  # Search scope
        self.m0 = m0 or m * 2
        self.layers = []  # Layer 0 is the base layer
        self.entry_point = None

    def _search_layer(self, q: np.ndarray, ep: dict, ef: int, layer: int):
        candidates = [(-np.linalg.norm(q - ep['vector']), ep)]
        visited = set([ep['id']])
        heap = []

        while candidates:
            dist, node = heapq.heappop(candidates)
            heapq.heappush(heap, (-dist, node))

            for neighbor in node['neighbors'].get(layer, []):
                if neighbor['id'] not in visited:
                    visited.add(neighbor['id'])
                    dist = -np.linalg.norm(q - neighbor['vector'])
                    heapq.heappush(candidates, (dist, neighbor))

        return [item[1] for item in heapq.nlargest(ef, heap)]

    def add_vector(self, vector: List[float], vector_id: str):
        # Implementation omitted for brevity
        pass

    def search(self, query: List[float], k: int = 5) -> List[Tuple[str, float]]:
        # Implementation omitted for brevity
        pass