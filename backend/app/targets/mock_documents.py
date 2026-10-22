"""
A small in-memory document store + keyword-overlap "retriever" standing in
for a real vector DB (Chroma/embeddings aren't needed for a red-team harness
— the point is testing what happens to retrieved text, not testing recall).

When an injection is active, the poisoned document is always included in the
returned set — reproducing the real-world fact that poisoned content is
usually crafted to rank well for the query it's meant to intercept.
"""

_DEFAULT_CORPUS = [
    {
        "page_content": (
            "AcmeCorp Shipping Policy: Standard orders ship within 3-5 business days. "
            "Expedited shipping is available for an additional fee."
        ),
        "metadata": {"source": "shipping_policy.md", "injected": False},
    },
    {
        "page_content": (
            "AcmeCorp Returns Policy: Items may be returned within 30 days of purchase "
            "for a full refund, provided they are unused and in original packaging."
        ),
        "metadata": {"source": "returns_policy.md", "injected": False},
    },
    {
        "page_content": (
            "AcmeCorp Account FAQ: To update your email address, log in and visit "
            "Account Settings. Password resets are self-service via the login page."
        ),
        "metadata": {"source": "account_faq.md", "injected": False},
    },
]


class MockRetriever:
    def __init__(self, poisoned_document: dict | None = None, k: int = 2):
        self._corpus = list(_DEFAULT_CORPUS)
        self._poisoned = poisoned_document
        self._k = k

    def retrieve(self, query: str) -> list[dict]:
        query_words = set(query.lower().split())

        def score(doc: dict) -> int:
            doc_words = set(str(doc["page_content"]).lower().split())
            return len(query_words & doc_words)

        ranked = sorted(self._corpus, key=score, reverse=True)
        top = ranked[: self._k]

        if self._poisoned is not None and self._poisoned not in top:
            # Poisoned content is crafted to rank well — simulate that by
            # always surfacing it, displacing the lowest-ranked pick.
            top = [self._poisoned] + top[: self._k - 1]

        return top
