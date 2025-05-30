class MockLiteLLM:
    """Simulate LiteLLM responses."""

    def completion(self, model: str, messages: list) -> dict:
        return {"id": "mock-123", "choices": [{"message": {"content": "Simulated response"}}]}

class MockADK:
    """Simulate Google ADK services."""

    def google_search(self, query: str) -> dict:
        return {"results": [f"Result for {query} #1", f"Result for {query} #2"]}

class MockQdrant:
    """Simulate vector database operations."""

    def store(self, vectors: list) -> str:
        return "collection-id"

    def search(self, vector: list) -> list:
        return [0]
