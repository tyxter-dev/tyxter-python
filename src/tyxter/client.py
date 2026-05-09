from __future__ import annotations


class Tyxter:
    """Synchronous Tyxter API client.

    The resource surface is added incrementally in R5a. The constructor
    already fixes the stable configuration shape used by later steps.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.tyxter.com",
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
