from typing import List, Tuple

import numpy as np


class BruteForce:
    def __init__(self):
        self.vectors = []
        self.ids = []

    def add_vector(self, vector: List[float], vector_id: str):
        self.vectors.append(np.array(vector))
        self.ids.append(vector_id)

    def search(self, query: List[float], k: int = 5) -> List[Tuple[str, float]]:
        if not self.vectors:
            return []

        query_vec = np.array(query)
        distances = np.linalg.norm(self.vectors - query_vec, axis=1)
        indices = np.argpartition(distances, k)[:k]
        return [(self.ids[i], float(distances[i])) for i in indices]