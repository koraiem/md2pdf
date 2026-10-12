#!/usr/bin/env python3
"""
Convert Markdown documents to high-fidelity, executive-ready PDF files using
marked, KaTeX, Mermaid.js, and Chrome headless.

Features:
- Dynamic metadata cards for RFCs, specs, and proposals (from headers or tables)
- Vector-rendered Mermaid diagrams (Flowcharts, Sequence diagrams, ERDs, etc.)
- Math formula rendering with KaTeX ($$math$$ and $inline$)
- GitHub-style alert callouts ([!NOTE], [!WARNING], [!TIP], etc.)
- Pixel-perfect ASCII architecture diagrams (no wrapping or broken boxes)
- Styled chat transcripts and conversation logs
- Clean table formatting with zebra striping and avoided page breaks
- Formal sign-off and approval signature cards
- CSS Paged Media running headers and footers with page numbering
- Suppressed browser header/footer clutter
"""

import sys
import os
import re
import shutil
import argparse
import tempfile
import subprocess

def find_chrome():
    env_chrome = os.environ.get("CHROME_PATH")
    if env_chrome and os.path.exists(env_chrome):
        return env_chrome

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def convert_md_to_html(md_path):
    cmd = ["npx", "--yes", "marked", "-i", md_path, "--gfm"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout

def enhance_html(html, doc_title_hint=None, paper_size="A4"):
    extracted_title = doc_title_hint or "Document Specification"
    extracted_ref = "SPECIFICATION"
    extracted_status = "Approved"

    # 1. Check for Table-based Metadata Header (e.g. RFC-0001 style)
    # <h1>RFC-0001: ...</h1>\n<table>...<th>Metadata</th><th>Details</th>...</table>
    table_meta_pattern = r"<h1>(.*?)</h1>\s*<table>\s*<thead>\s*<tr>\s*<th[^>]*>Metadata</th>\s*<th[^>]*>Details</th>\s*</tr>\s*</thead>\s*<tbody>(.*?)</tbody>\s*</table>"
    table_meta_match = re.search(table_meta_pattern, html, re.DOTALL)

    if table_meta_match:
        raw_h1 = table_meta_match.group(1).strip()
        tbody = table_meta_match.group(2)
        extracted_title = raw_h1

        rows = re.findall(r"<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>", tbody, re.DOTALL)
        meta_items = []
        for k_raw, v_raw in rows:
            k = re.sub(r"</?[a-z0-9]+[^>]*>", "", k_raw).strip()
            v = re.sub(r"</?[a-z0-9]+[^>]*>", "", v_raw).strip()
            meta_items.append((k, v))
            if "rfc id" in k.lower() or "id" in k.lower() or "reference" in k.lower():
                extracted_ref = v
            elif "status" in k.lower():
                extracted_status = v

        grid_html = "".join([
            f'<div class="meta-box"><div class="meta-label">{k.upper()}</div><div class="meta-val">{v}</div></div>'
            for k, v in meta_items
        ])
        header_html = f"""
        <header class="doc-header">
          <div class="doc-top-bar">
            <div class="badge-group">
              <span class="badge badge-primary">ENTERPRISE SPEC</span>
              <span class="badge badge-ref">{extracted_ref}</span>
            </div>
            <span class="badge badge-status">{extracted_status}</span>
          </div>
          <h1 class="doc-title">{raw_h1}</h1>
          <div class="meta-grid">
            {grid_html}
          </div>
        </header>
        """
        html = re.sub(table_meta_pattern, header_html, html, count=1, flags=re.DOTALL)
    else:
        # Paragraph-based metadata header (RFC / Spec style)
        header_pattern = r"<h1>(?:RFC:\s*)?(.*?)</h1>\s*<p>(.*?)</p>\s*<hr>"
        header_match = re.search(header_pattern, html, re.DOTALL)
        if header_match:
            raw_title = header_match.group(1).strip()
            raw_meta = header_match.group(2).strip()
            extracted_title = raw_title
            meta_items = []
            lines = [line.strip() for line in re.split(r"<br\s*/?>|\n", raw_meta) if line.strip()]
            for line in lines:
                kv_match = re.search(r"<strong>(.*?)(?::)?</strong>\s*:\s*(.*)", line)
                if kv_match:
                    k = kv_match.group(1).strip()
                    v = re.sub(r"</?[a-z0-9]+[^>]*>", "", kv_match.group(2)).strip()
                    meta_items.append((k, v))
                    if "reference" in k.lower() or "rfc" in k.lower() or "doc" in k.lower():
                        extracted_ref = v
                    elif "status" in k.lower():
                        extracted_status = v

            if meta_items:
                grid_html = "".join([
                    f'<div class="meta-box"><div class="meta-label">{k.upper()}</div><div class="meta-val">{v}</div></div>'
                    for k, v in meta_items
                ])
                header_html = f"""
                <header class="doc-header">
                  <div class="doc-top-bar">
                    <div class="badge-group">
                      <span class="badge badge-primary">DOCUMENT SPEC</span>
                      <span class="badge badge-ref">{extracted_ref}</span>
                    </div>
                    <span class="badge badge-status">{extracted_status}</span>
                  </div>
                  <h1 class="doc-title">{raw_title}</h1>
                  <div class="meta-grid">
                    {grid_html}
                  </div>
                </header>
                """
                html = re.sub(header_pattern, header_html, html, count=1, flags=re.DOTALL)
        else:
            h1_match = re.search(r"<h1>(.*?)</h1>", html)
            if h1_match:
                extracted_title = h1_match.group(1).strip()
                simple_header = f"""
                <header class="doc-header-simple">
                  <h1 class="doc-title">{extracted_title}</h1>
                </header>
                """
                html = re.sub(r"<h1>(.*?)</h1>", simple_header, html, count=1)

    # 2. Render Mermaid Diagrams
    # Match <pre><code class="language-mermaid"> or any code block starting with mermaid keywords
    def replace_mermaid(match):
        code = match.group(1)
        # Unescape basic HTML entities marked might have introduced
        clean_code = code.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"')
        return f"""
        <div class="mermaid-diagram-card">
          <pre class="mermaid">{clean_code}</pre>
        </div>
        """

    html = re.sub(r'<pre><code class="(?:language-)?mermaid">(.*?)</code></pre>', replace_mermaid, html, flags=re.DOTALL)
    # Also catch <pre><code> starting with flowchart, sequenceDiagram, erDiagram, classDiagram, graph
    html = re.sub(r'<pre><code>\s*((?:flowchart|sequenceDiagram|erDiagram|classDiagram|graph\s+TD|graph\s+LR|stateDiagram).*?)</code></pre>', replace_mermaid, html, flags=re.DOTALL)

    # 3. GitHub-style Alert Callouts ([!NOTE], [!WARNING], [!TIP], etc.)
    def replace_callouts(m):
        kind = m.group(1).lower()
        content = m.group(2).strip()
        icon_map = {
            "note": "ℹ️",
            "tip": "💡",
            "important": "📌",
            "warning": "⚠️",
            "caution": "🛑"
        }
        icon = icon_map.get(kind, "ℹ️")
        return f'<div class="callout callout-{kind}"><div class="callout-header"><span class="callout-icon">{icon}</span> {kind.upper()}</div><div class="callout-body">{content}</div></div>'

    html = re.sub(
        r'<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:<br\s*/?>)?\s*(.*?)</p>\s*</blockquote>',
        replace_callouts,
        html,
        flags=re.DOTALL
    )

    # 4. Architecture & Box-drawing diagrams / Chat transcripts in remaining code blocks
    def replace_special_code(match):
        content = match.group(1)
        # Unicode box drawing characters
        if any(c in content for c in "┌─┐│└┘├┤┬┴┼╔═╗║╚╝"):
            return f"""
            <div class="diagram-wrapper">
              <div class="diagram-toolbar">
                <div class="diagram-dots">
                  <span class="dot dot-r"></span>
                  <span class="dot dot-y"></span>
                  <span class="dot dot-g"></span>
                </div>
                <span class="diagram-caption">System Architecture &bull; Technical Schematic</span>
              </div>
              <pre class="diagram-code"><code>{content}</code></pre>
            </div>
            """
        # Chat conversations
        if any(marker in content for marker in ["[User]", "[User]:", "[Agent]", "[Agent]:", "User:", "Agent:", "Assistant:"]):
            caption = "Interaction Transcript &bull; Message Exchange"
            formatted = content
            formatted = re.sub(r"\[User(.*?)\]:?", r'<span class="speaker-user">👤 User\1</span>:', formatted)
            formatted = re.sub(r"\[Agent(.*?)\]:?", r'<span class="speaker-agent">🤖 Agent\1</span>:', formatted)
            formatted = re.sub(r'(https?://[^\s<>"]+)', r'<a href="\1" class="chat-link" target="_blank">\1</a>', formatted)

            return f"""
            <div class="chat-wrapper">
              <div class="chat-toolbar">
                <span class="chat-icon">💬</span>
                <span class="chat-caption">{caption}</span>
              </div>
              <div class="chat-body">{formatted}</div>
            </div>
            """

        return f'<pre class="standard-pre"><code>{content}</code></pre>'

    html = re.sub(r"<pre><code>(.*?)</code></pre>", replace_special_code, html, flags=re.DOTALL)

    # 5. Formal Approval & Sign-Off Section
    sec_approval_pattern = r"<h2>(?:\d+\.\s*)?Approval &amp; Sign-Off</h2>.*?(?=</body>|$)"
    if re.search(sec_approval_pattern, html, re.DOTALL):
        sec_approval_replacement = f"""
        <div class="approval-section-wrapper">
          <h2>Approval &amp; Sign-Off</h2>
          <p>Please review and sign below to confirm approval of this specification document.</p>

          <div class="approval-grid">
            <div class="approval-card">
              <div class="approval-title">Approved on behalf of Client / Sponsor</div>
              <div class="sig-group">
                <div class="sig-field">
                  <span class="sig-lbl">Name / Title</span>
                  <div class="sig-line"></div>
                </div>
                <div class="sig-field">
                  <span class="sig-lbl">Signature</span>
                  <div class="sig-line"></div>
                </div>
                <div class="sig-field">
                  <span class="sig-lbl">Date</span>
                  <div class="sig-line"></div>
                </div>
              </div>
            </div>
            <div class="approval-card">
              <div class="approval-title">Approved on behalf of Technical Architecture</div>
              <div class="sig-group">
                <div class="sig-field">
                  <span class="sig-lbl">Name / Title</span>
                  <div class="sig-line"></div>
                </div>
                <div class="sig-field">
                  <span class="sig-lbl">Signature</span>
                  <div class="sig-line"></div>
                </div>
                <div class="sig-field">
                  <span class="sig-lbl">Date</span>
                  <div class="sig-line"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        html = re.sub(sec_approval_pattern, sec_approval_replacement, html, count=1, flags=re.DOTALL)

    # Clean document title for running header
    clean_title = re.sub(r"<[^>]+>", "", extracted_title).strip()
    if len(clean_title) > 60:
        clean_title = clean_title[:57] + "..."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{clean_title}</title>

<!-- KaTeX support -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});">
</script>

<!-- Mermaid support -->
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{
    startOnLoad: false,
    theme: "neutral",
    securityLevel: "loose",
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
  }});

  window.addEventListener("DOMContentLoaded", async () => {{
    const elements = document.querySelectorAll(".mermaid");
    for (let i = 0; i < elements.length; i++) {{
      const el = elements[i];
      const code = el.textContent;
      try {{
        const id = "diagram-" + i;
        const {{ svg }} = await mermaid.render(id, code);
        el.innerHTML = svg;
      }} catch (err) {{
        console.error("Mermaid error on diagram " + i, err);
      }}
    }}
  }});
</script>

<style>
  @page {{
    size: {paper_size};
    margin: 18mm 16mm 18mm 16mm;
    @top-left {{
      content: "{clean_title}";
      font-size: 7.2pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #94a3b8;
      font-weight: 500;
    }}
    @top-right {{
      content: "{extracted_ref}";
      font-size: 7.2pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #94a3b8;
      font-weight: 600;
    }}
    @bottom-left {{
      content: "Confidential Document";
      font-size: 7.2pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #94a3b8;
    }}
    @bottom-right {{
      content: "Page " counter(page);
      font-size: 7.2pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #94a3b8;
      font-weight: 600;
    }}
  }}

  @page :first {{
    @top-left {{ content: ""; }}
    @top-right {{ content: ""; }}
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 9.2pt;
    margin: 0;
    padding: 0;
  }}

  .page-break-before {{
    break-before: page;
    page-break-before: always;
  }}

  .step-group {{
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  /* Typography */
  h1, h2, h3, h4 {{
    color: #0f172a;
    font-weight: 700;
    break-after: avoid;
    page-break-after: avoid;
    letter-spacing: -0.2px;
  }}

  h1 {{
    font-size: 18pt;
    line-height: 1.25;
    margin: 10px 0 14px;
  }}

  h2 {{
    font-size: 13pt;
    margin-top: 22px;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1.5px solid #e2e8f0;
    color: #0f172a;
  }}

  h3 {{
    font-size: 10.5pt;
    margin-top: 16px;
    margin-bottom: 6px;
    color: #1e293b;
    break-after: avoid;
    page-break-after: avoid;
  }}

  p {{
    margin: 6px 0;
  }}

  ul, ol {{
    margin: 6px 0;
    padding-left: 20px;
  }}

  li {{
    margin-bottom: 3px;
  }}

  strong {{
    color: #0f172a;
    font-weight: 600;
  }}

  code {{
    font-family: "SF Mono", "Cascadia Code", Menlo, Monaco, Consolas, monospace;
    font-size: 8.3pt;
    background: #f1f5f9;
    color: #4338ca;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}

  /* GitHub Alert Callouts */
  .callout {{
    border-radius: 8px;
    padding: 10px 14px;
    margin: 14px 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .callout-header {{
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .callout-body p {{
    margin: 4px 0 0;
    font-size: 8.8pt;
    line-height: 1.5;
  }}
  .callout-note {{
    background: #f0f7ff;
    border: 1px solid #c7dfff;
    border-left: 4px solid #3b82f6;
    color: #1e3a8a;
  }}
  .callout-note .callout-header {{ color: #1d4ed8; }}
  .callout-warning {{
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    color: #78350f;
  }}
  .callout-warning .callout-header {{ color: #b45309; }}
  .callout-tip {{
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-left: 4px solid #10b981;
    color: #064e3b;
  }}
  .callout-tip .callout-header {{ color: #047857; }}
  .callout-important {{
    background: #fdf2f8;
    border: 1px solid #fbcfe8;
    border-left: 4px solid #ec4899;
    color: #831843;
  }}
  .callout-important .callout-header {{ color: #be185d; }}
  .callout-caution {{
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #ef4444;
    color: #7f1d1d;
  }}
  .callout-caution .callout-header {{ color: #b91c1c; }}

  blockquote {{
    margin: 10px 0;
    padding: 8px 14px;
    background: #f8fafc;
    border-left: 3.5px solid #6366f1;
    border-radius: 0 6px 6px 0;
    color: #334155;
    font-style: italic;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  blockquote p {{
    margin: 0;
  }}

  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
  }}

  /* Document Header Card */
  .doc-header {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 20px;
    border-top: 5px solid #4f46e5;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  }}

  .doc-header-simple {{
    background: #ffffff;
    border-left: 5px solid #4f46e5;
    padding: 10px 16px;
    margin-bottom: 18px;
  }}

  .doc-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}

  .badge-group {{
    display: flex;
    gap: 8px;
    align-items: center;
  }}

  .badge {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 9999px;
    font-size: 7.2pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}

  .badge-primary {{
    background: #e0e7ff;
    color: #3730a3;
  }}

  .badge-ref {{
    background: #f1f5f9;
    color: #475569;
    font-family: "SF Mono", Menlo, monospace;
  }}

  .badge-status {{
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
  }}

  .doc-title {{
    font-size: 16.5pt;
    font-weight: 800;
    color: #0f172a;
    margin: 8px 0 14px;
    line-height: 1.3;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    background: #f8fafc;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }}

  .meta-box {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .meta-label {{
    font-size: 6.8pt;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}

  .meta-val {{
    font-size: 8.8pt;
    font-weight: 600;
    color: #1e293b;
  }}

  /* Mermaid Diagram Card */
  .mermaid-diagram-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
    margin: 16px 0 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  .mermaid {{
    width: 100%;
    display: flex;
    justify-content: center;
    background: transparent;
  }}

  .mermaid svg {{
    max-width: 100% !important;
    height: auto !important;
  }}

  /* ASCII Diagram Card */
  .diagram-wrapper {{
    background: #0f172a;
    border-radius: 8px;
    border: 1px solid #1e293b;
    margin: 14px 0 20px;
    overflow: hidden;
    break-inside: avoid;
    page-break-inside: avoid;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
  }}

  .diagram-toolbar {{
    background: #1e293b;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid #334155;
  }}

  .diagram-dots {{
    display: flex;
    gap: 5px;
  }}

  .diagram-dots .dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }}

  .dot-r {{ background: #ef4444; }}
  .dot-y {{ background: #f59e0b; }}
  .dot-g {{ background: #10b981; }}

  .diagram-caption {{
    color: #94a3b8;
    font-size: 7.2pt;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}

  .diagram-code {{
    margin: 0;
    padding: 12px 14px;
    background: transparent;
    color: #f1f5f9;
    font-family: "SF Mono", "Cascadia Code", Menlo, Monaco, Consolas, "Courier New", monospace;
    font-size: 7.3pt;
    line-height: 1.15;
    letter-spacing: 0px;
    white-space: pre;
    overflow-x: visible;
  }}

  .diagram-code code {{
    color: inherit;
    background: transparent;
    padding: 0;
    border: none;
    font-family: inherit;
    font-size: inherit;
  }}

  /* Chat Transcripts */
  .chat-wrapper {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #4f46e5;
    border-radius: 8px;
    margin: 12px 0 18px;
    overflow: hidden;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  .chat-toolbar {{
    background: #f1f5f9;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #e2e8f0;
  }}

  .chat-icon {{
    font-size: 8.5pt;
  }}

  .chat-caption {{
    font-size: 7.2pt;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .chat-body {{
    padding: 10px 14px;
    font-family: "SF Mono", Menlo, Consolas, monospace;
    font-size: 8.2pt;
    line-height: 1.5;
    color: #1e293b;
    white-space: pre-wrap;
    word-break: break-word;
  }}

  .speaker-user {{
    color: #2563eb;
    font-weight: 700;
  }}

  .speaker-agent {{
    color: #059669;
    font-weight: 700;
  }}

  .chat-link {{
    color: #4f46e5;
    text-decoration: underline;
    word-break: break-all;
  }}

  /* Standard Code Blocks */
  pre.standard-pre {{
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 8.2pt;
    line-height: 1.45;
    overflow-x: auto;
    break-inside: avoid;
  }}

  pre.standard-pre code {{
    background: transparent;
    color: inherit;
    border: none;
    padding: 0;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 14px 0 20px;
    font-size: 8.5pt;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  thead th {{
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 2px solid #cbd5e1;
    font-size: 7.8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  tbody td {{
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    line-height: 1.45;
    vertical-align: top;
  }}

  tbody tr:nth-child(even) {{
    background: #f8fafc;
  }}

  tbody tr:last-child td {{
    border-bottom: none;
  }}

  /* Sign-Off Block */
  .approval-section-wrapper {{
    break-inside: avoid;
    page-break-inside: avoid;
    margin-top: 20px;
  }}

  .approval-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-top: 16px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  .approval-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 16px;
    border-top: 4px solid #4f46e5;
  }}

  .approval-title {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 12px;
    padding-bottom: 5px;
    border-bottom: 1px solid #e2e8f0;
  }}

  .sig-group {{
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .sig-field {{
    display: flex;
    flex-direction: column;
    gap: 3px;
  }}

  .sig-lbl {{
    font-size: 7.2pt;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .sig-line {{
    border-bottom: 1px solid #94a3b8;
    height: 16px;
  }}
</style>
</head>
<body>
{html}
</body>
</html>
"""

def md_to_pdf(input_md, output_pdf=None, paper_size="A4", title=None):
    if not os.path.exists(input_md):
        raise FileNotFoundError(f"Markdown file not found: {input_md}")

    if not output_pdf:
        base, _ = os.path.splitext(input_md)
        output_pdf = f"{base}.pdf"

    chrome_bin = find_chrome()
    if not chrome_bin:
        raise RuntimeError(
            "Google Chrome / Chromium binary was not found. Please set CHROME_PATH or install Google Chrome."
        )

    # Convert MD to raw HTML
    raw_html = convert_md_to_html(input_md)

    # Enhance HTML with executive styling
    final_html = enhance_html(raw_html, doc_title_hint=title, paper_size=paper_size)

    # Write temporary HTML file
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(final_html)
        tmp_path = tmp.name

    try:
        cmd = [
            chrome_bin,
            "--headless",
            "--disable-gpu",
            "--virtual-time-budget=12000",
            "--no-pdf-header-footer",
            "--generate-pdf-document-outline",
            f"--print-to-pdf={output_pdf}",
            tmp_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return os.path.abspath(output_pdf)

def main():
    parser = argparse.ArgumentParser(description="md2pdf - Convert Markdown to executive PDF")
    parser.add_argument("input", help="Path to input markdown (.md) file")
    parser.add_argument("output", nargs="?", default=None, help="Path to output PDF (.pdf) file")
    parser.add_argument("--paper", default="A4", choices=["A4", "letter", "Letter"], help="Paper size (default: A4)")
    parser.add_argument("--title", default=None, help="Custom document title override")

    args = parser.parse_args()

    try:
        out = md_to_pdf(args.input, args.output, paper_size=args.paper, title=args.title)
        print(f"Successfully generated: {out}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
