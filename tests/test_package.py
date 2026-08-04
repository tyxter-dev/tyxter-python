import re

from tyxter import Tyxter, __version__

# PEP 440: release segment, with optional pre/post/dev suffixes. Asserting the
# shape rather than a literal keeps this test about "the package exports a
# usable version" — its actual subject — instead of failing on every release.
# A malformed version is the real failure here, because hatchling reads
# __version__ as the package version and packaging would break on it.
_PEP440 = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$")


def test_package_exports_client_and_version() -> None:
    client = Tyxter(api_key="tx_sandbox_test", base_url="http://localhost:3001/")

    assert isinstance(__version__, str)
    assert _PEP440.match(__version__), f"{__version__!r} is not a valid PEP 440 version"
    assert client.api_key == "tx_sandbox_test"
    assert client.base_url == "http://localhost:3001"


def test_client_requires_api_key() -> None:
    try:
        Tyxter(api_key="")
    except ValueError as exc:
        assert str(exc) == "api_key is required"
    else:
        raise AssertionError("expected ValueError")
