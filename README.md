# Tyxter Python SDK

Python SDK for the Tyxter Messaging API.

The package is currently an in-repo R5a alpha. It starts with a sync
client, public `/v1/*` resource helpers, typed API errors, and webhook
signature verification.

```bash
pip install -e ".[dev]"
pytest
```

```python
from tyxter import Tyxter

client = Tyxter(api_key="tx_sandbox_...")
```

