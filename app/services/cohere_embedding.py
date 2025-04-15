import cohere

from app.core.config import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)


def get_embedding(text: str) -> list[float]:
    response = co.embed(texts=[text], model="embed-english-v3.0")
    return response.embeddings[0]
