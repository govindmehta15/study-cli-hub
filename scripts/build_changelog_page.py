# build_changelog_page.py - renders the GitHub Pages changelog from the
# repo's own GitHub Releases, so there's exactly one place release notes are
# written (gh release create --generate-notes) and this page never drifts
# out of sync with reality. Run by .github/workflows/pages.yml on every
# release publish - reads release JSON from stdin, writes a static HTML
# page to stdout. No commit to `main` involved (see that workflow's
# comments for why - branch protection would block it).
import html
import json
import sys

try:
    import markdown as _markdown
except ImportError:
    _markdown = None

REPO_URL = "https://github.com/govindmehta15/study-cli-hub"


def _render_body(body):
    text = (body or "").strip()
    if not text:
        return "<p><em>No release notes.</em></p>"
    if _markdown:
        # gh release --generate-notes always emits "## What's Changed" /
        # "## New Contributors" - shift those down two levels so they don't
        # collide with this card's own <h2> title.
        shifted = "\n".join(
            "#### " + line[3:] if line.startswith("## ") else line
            for line in text.splitlines()
        )
        return _markdown.markdown(shifted, extensions=["extra"])
    return f"<pre>{html.escape(text)}</pre>"


def _release_card(release):
    tag = html.escape(release.get("tag_name", ""))
    name = html.escape(release.get("name") or release.get("tag_name", ""))
    published = (release.get("published_at") or "")[:10]
    prerelease = release.get("prerelease")
    url = html.escape(release.get("html_url", REPO_URL))
    badge = '<span class="badge badge-pre">pre-release</span>' if prerelease else '<span class="badge">latest-eligible</span>'
    return f"""
    <article class="release">
      <header>
        <h2><a href="{url}">{name}</a></h2>
        <div class="meta">
          <code>{tag}</code>
          <time datetime="{published}">{published}</time>
          {badge if prerelease else ""}
        </div>
      </header>
      <div class="body">{_render_body(release.get("body"))}</div>
    </article>
    """


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CLI Study Hub &mdash; Release Notes</title>
<meta name="description" content="Version history and release notes for CLI Study Hub.">
<style>
  :root {{
    color-scheme: light dark;
    --bg: #ffffff; --fg: #1a1a1a; --muted: #6b7280; --card: #f7f7f8;
    --border: #e5e7eb; --accent: #2563eb; --code-bg: #eef0f3;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0e0f12; --fg: #e6e6e6; --muted: #9aa0a8; --card: #17181c;
      --border: #2a2b30; --accent: #6ea8fe; --code-bg: #1f2024;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 0 1.25rem 4rem;
    background: var(--bg); color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
  }}
  header.page-header {{
    max-width: 760px; margin: 0 auto; padding: 3rem 0 1rem;
  }}
  header.page-header h1 {{ margin: 0 0 0.25rem; font-size: 1.9rem; }}
  header.page-header p {{ color: var(--muted); margin: 0; }}
  header.page-header a {{ color: var(--accent); }}
  main {{ max-width: 760px; margin: 0 auto; }}
  .release {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem 1.5rem; margin: 1.5rem 0;
  }}
  .release h2 {{ margin: 0 0 0.35rem; font-size: 1.25rem; }}
  .release h2 a {{ color: var(--fg); text-decoration: none; }}
  .release h2 a:hover {{ color: var(--accent); }}
  .meta {{
    display: flex; gap: 0.75rem; align-items: center;
    color: var(--muted); font-size: 0.85rem; margin-bottom: 0.75rem;
  }}
  .meta code {{ background: var(--code-bg); padding: 0.1rem 0.4rem; border-radius: 4px; }}
  .badge {{
    background: var(--accent); color: #fff; border-radius: 999px;
    padding: 0.1rem 0.6rem; font-size: 0.75rem;
  }}
  .badge-pre {{ background: var(--muted); }}
  .body :is(ul, ol) {{ padding-left: 1.25rem; }}
  .body pre {{ overflow-x: auto; background: var(--code-bg); padding: 0.75rem; border-radius: 6px; }}
  .body code {{ background: var(--code-bg); padding: 0.1rem 0.35rem; border-radius: 4px; }}
  .body a {{ color: var(--accent); }}
  footer {{ max-width: 760px; margin: 2rem auto 0; color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
  <header class="page-header">
    <h1>🧠 CLI Study Hub &mdash; Release Notes</h1>
    <p>
      Every published version, generated automatically from
      <a href="{repo_url}/releases">GitHub Releases</a> &mdash;
      <a href="{repo_url}">source</a> ·
      <a href="https://pypi.org/project/study-cli-hub/">PyPI</a>
    </p>
  </header>
  <main>
    {releases_html}
  </main>
  <footer>
    Generated automatically on every release publish. Nothing here is
    hand-edited &mdash; if a release's notes are wrong, fix them on the
    <a href="{repo_url}/releases">release itself</a> and this page updates
    on the next publish.
  </footer>
</body>
</html>
"""


def build_page(releases):
    releases = sorted(releases, key=lambda r: r.get("published_at") or "", reverse=True)
    releases_html = "\n".join(_release_card(r) for r in releases) or "<p>No releases yet.</p>"
    return PAGE_TEMPLATE.format(repo_url=REPO_URL, releases_html=releases_html)


def main():
    releases = json.load(sys.stdin)
    sys.stdout.write(build_page(releases))


if __name__ == "__main__":
    main()
