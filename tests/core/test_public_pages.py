import json

import pytest
from starlette.requests import Request

from core import public_pages
from core.server import home_page, privacy_page, terms_page


def _request(path: str, accept: str = "") -> Request:
    headers = [(b"accept", accept.encode())] if accept else []
    return Request({"type": "http", "method": "GET", "path": path, "headers": headers})


@pytest.fixture(autouse=True)
def _branding(monkeypatch):
    monkeypatch.setenv("WORKSPACE_MCP_BRAND_NAME", "Private MCP")
    monkeypatch.setenv("WORKSPACE_MCP_CONTACT_EMAIL", "owner@example.com")


def test_home_page_names_app_and_explains_purpose():
    page = public_pages.render_home_page()
    assert "<title>Private MCP</title>" in page
    assert "Model Context Protocol" in page
    assert "Gmail" in page and "Google Drive" in page
    assert "does not use Google user data to train" in page
    assert 'href="/privacy"' in page


def test_privacy_page_has_limited_use_disclosure_and_contact():
    page = public_pages.render_privacy_page()
    assert "api-services-user-data-policy" in page
    assert "Limited Use" in page
    assert "mailto:owner@example.com" in page
    assert "<!--email_off-->" in page
    assert "September 30, 2026" in page
    assert "https://www.googleapis.com/auth/gmail.readonly" in page


def test_brand_name_is_escaped(monkeypatch):
    monkeypatch.setenv("WORKSPACE_MCP_BRAND_NAME", "<script>x</script>")
    page = public_pages.render_home_page()
    assert "<script>x</script>" not in page
    assert "&lt;script&gt;" in page


def test_defaults_without_env(monkeypatch):
    monkeypatch.delenv("WORKSPACE_MCP_BRAND_NAME")
    monkeypatch.delenv("WORKSPACE_MCP_CONTACT_EMAIL")
    page = public_pages.render_privacy_page()
    assert public_pages.DEFAULT_BRAND_NAME in page
    assert "mailto:" not in page


@pytest.mark.asyncio
async def test_root_serves_html_to_browsers():
    response = await home_page(_request("/", "text/html,application/xhtml+xml"))
    assert response.media_type == "text/html"
    assert b"Private MCP" in response.body


@pytest.mark.asyncio
@pytest.mark.parametrize("accept", ["", "*/*"])
async def test_root_serves_html_to_generic_clients(accept):
    # Google's verification checker does not always send Accept: text/html.
    response = await home_page(_request("/", accept))
    assert response.media_type == "text/html"


@pytest.mark.asyncio
async def test_root_keeps_json_health_for_json_clients():
    response = await home_page(_request("/", "application/json"))
    assert json.loads(response.body)["status"] == "healthy"


@pytest.mark.asyncio
async def test_privacy_and_terms_routes():
    privacy = await privacy_page(_request("/privacy"))
    terms = await terms_page(_request("/terms"))
    assert b"Privacy Policy" in privacy.body
    assert b"Terms of Service" in terms.body
