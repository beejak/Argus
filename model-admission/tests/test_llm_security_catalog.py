"""Ensure the shared LLM security test catalog loads in this package's pytest session."""


def test_llm_security_test_catalog_fixture(llm_security_test_catalog: dict) -> None:
    assert llm_security_test_catalog.get("catalog_version")
    assert isinstance(llm_security_test_catalog.get("cases"), list)
