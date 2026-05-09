from tyxter import Tyxter, __version__


def test_package_exports_client_and_version() -> None:
    client = Tyxter(api_key="tx_sandbox_test", base_url="http://localhost:3001/")

    assert __version__ == "0.1.0a0"
    assert client.api_key == "tx_sandbox_test"
    assert client.base_url == "http://localhost:3001"


def test_client_requires_api_key() -> None:
    try:
        Tyxter(api_key="")
    except ValueError as exc:
        assert str(exc) == "api_key is required"
    else:
        raise AssertionError("expected ValueError")
