"""
Public, unauthenticated pages for Google OAuth app verification.

Google's brand verification requires a publicly reachable home page that
explains the app's purpose and uses the same app name as the OAuth consent
screen, plus a privacy policy that describes how Google user data is handled.
These pages are served by the MCP server itself so they always describe the
deployment that actually requests the scopes.

Configuration (all optional):
    WORKSPACE_MCP_BRAND_NAME      App name shown on the pages. Must match the
                                  app name on the Google OAuth consent screen.
    WORKSPACE_MCP_CONTACT_EMAIL   Contact address listed on the pages.
"""

import html
import os
from datetime import date

from auth.scopes import SCOPES

DEFAULT_BRAND_NAME = "Google Workspace MCP"
POLICY_LAST_UPDATED = date(2026, 9, 30)

_SCOPE_PURPOSES = [
    ("Gmail", "gmail", "Search, read, label, draft, and send email when you ask."),
    ("Google Drive", "drive", "Search, read, create, and update files when you ask."),
    ("Google Docs", "documents", "Read and edit documents when you ask."),
    ("Google Sheets", "spreadsheets", "Read and edit spreadsheets when you ask."),
    ("Google Calendar", "calendar", "Read and manage events when you ask."),
    ("Google Tasks", "tasks", "Read and manage task lists when you ask."),
    (
        "Apps Script",
        "script",
        "Read, edit, and run your Apps Script projects when you ask.",
    ),
    ("Account info", "userinfo", "Identify which Google account is signed in."),
]


def _brand_name() -> str:
    return os.getenv("WORKSPACE_MCP_BRAND_NAME", "").strip() or DEFAULT_BRAND_NAME


def _contact_email() -> str:
    return os.getenv("WORKSPACE_MCP_CONTACT_EMAIL", "").strip()


def _requested_products() -> list[tuple[str, str]]:
    """Return (product, purpose) rows for the scopes this server requests."""
    joined = " ".join(SCOPES)
    return [
        (product, purpose)
        for product, needle, purpose in _SCOPE_PURPOSES
        if f"/auth/{needle}" in joined
    ]


def _contact_html() -> str:
    email = _contact_email()
    if not email:
        return "the operator of this deployment"
    safe = html.escape(email)
    return f'<a href="mailto:{safe}">{safe}</a>'


def _page(title: str, body: str) -> str:
    name = html.escape(_brand_name())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: light dark; --fg: #1a1a1a; --muted: #555; --bg: #fff; --line: #e5e5e5; --link: #0b57d0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fg: #e8e8e8; --muted: #a8a8a8; --bg: #121212; --line: #2a2a2a; --link: #8ab4f8; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 720px; margin: 0 auto; padding: 32px 16px 64px; }}
  nav {{ display: flex; gap: 16px; flex-wrap: wrap; padding-bottom: 16px; border-bottom: 1px solid var(--line); }}
  nav strong {{ margin-right: auto; }}
  a {{ color: var(--link); }}
  h1 {{ font-size: 28px; line-height: 1.25; margin: 32px 0 8px; }}
  h2 {{ font-size: 20px; margin: 32px 0 8px; }}
  .muted {{ color: var(--muted); }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; vertical-align: top; padding: 8px 8px 8px 0; border-bottom: 1px solid var(--line); }}
  footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 14px; }}
</style>
</head>
<body>
<main>
<nav><strong>{name}</strong><a href="/">Home</a><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Service</a></nav>
{body}
<footer class="muted">{name} &middot; <a href="/privacy">Privacy Policy</a> &middot; <a href="/terms">Terms of Service</a></footer>
</main>
</body>
</html>"""


def render_home_page() -> str:
    name = html.escape(_brand_name())
    rows = "".join(
        f"<tr><th>{html.escape(product)}</th><td>{html.escape(purpose)}</td></tr>"
        for product, purpose in _requested_products()
    )
    body = f"""
<h1>{name}</h1>
<p>{name} is a private Model Context Protocol (MCP) server. It lets an AI assistant
that you connect yourself (such as Claude) work with your own Google Workspace
account: reading and drafting email, finding and editing files, and managing your
calendar and tasks. It acts only when you ask it to in your assistant.</p>

<h2>How it works</h2>
<ol>
  <li>You add this server as a connector in your AI assistant.</li>
  <li>You sign in with Google and approve the permissions listed below.</li>
  <li>When you ask your assistant to do something in Google Workspace, the assistant
      calls this server, which makes the matching Google API request on your behalf
      and returns the result to your assistant.</li>
</ol>

<h2>What it accesses and why</h2>
<table>{rows}</table>

<h2>What it does not do</h2>
<ul>
  <li>It does not sell Google user data or use it for advertising.</li>
  <li>It does not use Google user data to train AI or machine learning models.</li>
  <li>It does not generate, store, or distribute images of any kind, including
      AI-generated intimate imagery.</li>
  <li>It is not a public service. Access is limited to accounts the operator has
      approved.</li>
</ul>

<p>Details are in the <a href="/privacy">Privacy Policy</a> and
<a href="/terms">Terms of Service</a>. Questions: {_contact_html()}.</p>
"""
    return _page(_brand_name(), body)


def render_privacy_page() -> str:
    name = html.escape(_brand_name())
    d = POLICY_LAST_UPDATED
    updated = f"{d:%B} {d.day}, {d:%Y}"
    body = f"""
<h1>Privacy Policy</h1>
<p class="muted">Last updated: {updated}</p>
<p>This policy explains how {name} ("the app") handles information, including
data received from Google APIs.</p>

<h2>1. Data the app accesses</h2>
<p>After you sign in with Google and grant permission, the app can access the
Google Workspace data covered by the permissions you approved: Gmail messages and
settings, Google Drive files, Docs, Sheets, Calendar events, Tasks, Apps Script
projects, and your basic Google account profile (name and email address). The app
only reads or changes this data when your AI assistant makes a request on your
behalf.</p>

<h2>2. How the app uses Google user data</h2>
<p>Google user data is used only to provide the features you request through your
connected AI assistant: for example, returning the email you asked to see, creating
the draft you asked for, or updating the spreadsheet you named. The result of each
request is returned only to the AI assistant you connected, which is the client you
chose to use.</p>

<h2>3. What the app stores</h2>
<ul>
  <li><strong>OAuth tokens.</strong> Access and refresh tokens issued by Google are
      stored encrypted on the server so you don't have to sign in on every request.</li>
  <li><strong>Temporary files.</strong> Attachments you ask to download are kept
      temporarily and deleted automatically after about one hour.</li>
  <li><strong>Operational logs.</strong> Request logs (such as timestamps, endpoints,
      and error messages) are kept for troubleshooting and security. They are not
      used to build profiles of users.</li>
</ul>
<p>The app does not keep a copy of your email, files, or calendar content beyond
what is needed to complete a request.</p>

<h2>4. Sharing and transfer</h2>
<p>Google user data is not sold, rented, or shared with third parties, except that
results are returned to the AI assistant you connected at your direction. Data is
not used for advertising, is not used to determine credit-worthiness or for lending
purposes, and is not used to develop, improve, or train generalized AI or machine
learning models. No human reads your data unless you give explicit permission for
a specific support request, it is necessary for security purposes, or it is
required by law.</p>

<h2>5. Google API Services User Data Policy</h2>
<p>The app's use and transfer of information received from Google APIs adheres to the
<a href="https://developers.google.com/terms/api-services-user-data-policy">Google
API Services User Data Policy</a>, including the Limited Use requirements.</p>

<h2>6. Security</h2>
<p>All traffic to the app uses HTTPS. Stored tokens are encrypted, and access to the
server is restricted to the operator.</p>

<h2>7. Retention and deletion</h2>
<p>Tokens are kept until you revoke access or ask for deletion. You can revoke the
app's access at any time at
<a href="https://myaccount.google.com/connections">myaccount.google.com/connections</a>,
after which the stored tokens stop working. To have all stored tokens and any
related records deleted, contact {_contact_html()}; requests are handled within
30 days.</p>

<h2>8. Children</h2>
<p>The app is not directed to children under 13 and does not knowingly collect their
information.</p>

<h2>9. Changes</h2>
<p>If this policy changes, the updated version will be posted on this page with a
new "Last updated" date.</p>

<h2>10. Contact</h2>
<p>Questions about this policy: {_contact_html()}.</p>
"""
    return _page(f"Privacy Policy – {_brand_name()}", body)


def render_terms_page() -> str:
    name = html.escape(_brand_name())
    body = f"""
<h1>Terms of Service</h1>
<p>By connecting to {name} ("the app"), you agree to these terms.</p>

<h2>1. The service</h2>
<p>The app is a private MCP server that lets an AI assistant you connect act on your
Google Workspace account at your request. Access is limited to accounts approved
by the operator and may be withdrawn at any time.</p>

<h2>2. Your responsibilities</h2>
<p>You are responsible for the requests your assistant makes through the app,
including emails it sends and files it changes. Review actions before approving
them in your assistant. Do not use the app to violate the law, Google's terms, or
anyone's rights, and do not use it to create or share non-consensual intimate
imagery or any other abusive content.</p>

<h2>3. Privacy</h2>
<p>How data is handled is described in the <a href="/privacy">Privacy Policy</a>.</p>

<h2>4. No warranty</h2>
<p>The app is provided "as is" without warranties of any kind. To the extent
permitted by law, the operator is not liable for any loss resulting from use of
the app, including data changed or sent at your assistant's request.</p>

<h2>5. Termination</h2>
<p>You can stop using the app at any time by removing the connector and revoking
access at <a href="https://myaccount.google.com/connections">myaccount.google.com/connections</a>.</p>

<h2>6. Contact</h2>
<p>Questions: {_contact_html()}.</p>
"""
    return _page(f"Terms of Service – {_brand_name()}", body)
