from typing import List, Tuple

import numpy as np
from sklearn.cluster import KMeans


class IVFIndex:
    def __init__(self, n_clusters: int = 100):
        self.n_clusters = n_clusters
        self.clusters = {}
        self.centroids = None

    def train(self, vectors: List[List[float]]):
        if len(vectors) < self.n_clusters:
            self.n_clusters = max(1, len(vectors) // 2)

        kmeans = KMeans(n_clusters=self.n_clusters)
        self.centroids = kmeans.fit(vectors).cluster_centers_

        for i, vec in enumerate(vectors):
            cluster_id = np.argmin(np.linalg.norm(self.centroids - vec, axis=1))
            if cluster_id not in self.clusters:
                self.clusters[cluster_id] = []
            self.clusters[cluster_id].append((i, vec))

    def search(self, query: List[float], k: int = 5) -> List[Tuple[str, float]]:
        if not self.centroids:
            return []

        query_vec = np.array(query)
        closest_cluster = np.argmin(np.linalg.norm(self.centroids - query_vec, axis=1))
        candidates = self.clusters.get(closest_cluster, [])

        distances = [np.linalg.norm(vec - query_vec) for _, vec in candidates]
        indices = np.argpartition(distances, min(k, len(distances)))[:k]
        return [(candidates[i][0], float(distances[i])) for i in indices]
