from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import AgglomerativeClustering
import numpy as np


class Clustering:
    def __init__(self, sentences):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.sentences = sentences

    def cluster(self):
        corpus_embeddings = self.embedder.encode(self.sentences)
        corpus_embeddings = corpus_embeddings / \
            np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
        clustering_model = AgglomerativeClustering(
            n_clusters=None, distance_threshold=1, compute_full_tree=True, linkage="ward")
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_
        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            clustered_sentences[self.sentences[sentence_id]] = cluster_id
        return clustered_sentences
