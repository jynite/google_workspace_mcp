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

from auth.scopes import get_current_scopes

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
    joined = " ".join(get_current_scopes())
    return [
        (product, purpose)
        for product, needle, purpose in _SCOPE_PURPOSES
        if f"/auth/{needle}" in joined
    ]


def _scope_list_html() -> str:
    return "".join(
        f"<li><code>{html.escape(scope)}</code></li>"
        for scope in sorted(set(get_current_scopes()))
    )


def _contact_html() -> str:
    email = _contact_email()
    if not email:
        return "the operator of this deployment"
    safe = html.escape(email)
    # email_off stops Cloudflare Email Obfuscation from replacing the address
    # with "[email protected]" for reviewers and crawlers that don't run JS.
    return f'<!--email_off--><a href="mailto:{safe}">{safe}</a><!--/email_off-->'


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
<p>This policy explains what data {name} ("the app") collects, how it is used,
stored, and shared, and how you can have it deleted, including data received from
Google APIs.</p>

<h2>Who operates the app</h2>
<p>{name} is a privately operated Model Context Protocol (MCP) server hosted at
this domain. It connects an AI assistant that you choose (such as Claude) to your
Google Workspace account. Contact: {_contact_html()}.</p>

<h2>1. Data the app accesses</h2>
<p>The app only accesses Google data after you sign in with Google and approve the
requested permissions, and only reads or changes that data when your AI assistant
makes a request on your behalf. Depending on what you ask for, that includes:</p>
<table>
  <tr><th>Source</th><th>Data</th><th>Why</th></tr>
  <tr><td>Google account</td><td>Name, email address, profile picture URL,
      Google account ID</td><td>Identify which account is signed in and keep its
      tokens separate from other accounts.</td></tr>
  <tr><td>Gmail</td><td>Message headers, bodies, attachments, labels, drafts,
      filters, vacation/auto-reply settings</td><td>Search and read the messages you
      ask about, draft and send email you request, and manage labels and filters you
      ask to change.</td></tr>
  <tr><td>Google Drive</td><td>File names, metadata, contents, folders, sharing
      permissions</td><td>Find, read, create, update, or share the files you
      name.</td></tr>
  <tr><td>Docs, Sheets</td><td>Document and spreadsheet contents and
      comments</td><td>Read and edit the documents and spreadsheets you
      request.</td></tr>
  <tr><td>Calendar</td><td>Calendars, events, attendees, free/busy
      information</td><td>Show your schedule and create or update the events you
      request.</td></tr>
  <tr><td>Tasks</td><td>Task lists and tasks</td><td>Read and manage the tasks you
      request.</td></tr>
  <tr><td>Apps Script</td><td>Script projects, code, deployments, run
      metrics</td><td>Read, edit, deploy, or run the scripts you request.</td></tr>
</table>
<p>The exact permissions (OAuth scopes) the app requests are:</p>
<ul>{_scope_list_html()}</ul>
<p>The app does not collect data from any source other than Google APIs and the
requests your AI assistant sends. It does not use cookies for tracking or
analytics; the only cookies it sets are short-lived security cookies used during
sign-in.</p>

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
