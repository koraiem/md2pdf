# md2pdf

> **High-fidelity, executive-ready PDF generation from Markdown files using marked, Mermaid.js, KaTeX, and headless Chrome.**

`md2pdf` turns standard Markdown documents (`.md`) — including technical RFCs, architecture proposals, meeting notes, and mathematical documentation — into styled, publication-ready PDF documents (`.pdf`).

It is designed both as a standalone command-line tool and as a Google Antigravity agent skill.

---

## 🌟 Key Features

### 1. Executive Document Headers
- Automatically detects document metadata (RFC ID, document reference, client, author, date, status, target milestone) from YAML frontmatter, markdown header blocks, or metadata tables.
- Renders them into a polished metadata card with status badges and an accent top bar.

### 2. Vector Mermaid Graphs & Diagrams
- Renders all Mermaid diagrams into crisp vector SVG graphics:
  - `flowchart` (System context, pipelines)
  - `sequenceDiagram` (Multi-party protocols, API lifecycles)
  - `erDiagram` (Database and entity relationships)
  - `classDiagram` and `stateDiagram`
- **Collision-Free Rendering**: Uses sequential unique diagram IDs (`diagram-0`, `diagram-1`, ...) so documents with dozens of diagrams render cleanly without SVG clip-path or ID collisions.

### 3. KaTeX Mathematical Typesetting
- Full LaTeX math rendering for equations and formulas:
  - Display math: `$$...$$`
  - Inline math: `$..$`

### 4. GitHub-Style Alert Callouts
- Automatically transforms GitHub alert syntax into styled callout containers:
  - `> [!NOTE]` (Blue info callout)
  - `> [!TIP]` (Green success callout)
  - `> [!IMPORTANT]` (Pink/Purple alert)
  - `> [!WARNING]` (Amber warning)
  - `> [!CAUTION]` (Red danger callout)

### 5. Pixel-Perfect ASCII Architecture Schematics
- Automatically detects Unicode box-drawing characters (`┌`, `─`, `│`, `└`, etc.) in code blocks.
- Wraps them in dark terminal cards with macOS-style window controls and zero-wrap monospace typography to keep boxes aligned.

### 6. Conversational Chat Transcripts
- Formats multi-turn chat dialogues (`[User]:`, `[Agent]:`, `User:`, `Assistant:`) into conversational threads with speaker badges (`👤 User`, `🤖 Agent`), code snippets, and active hyperlinks.

### 7. Clean Table Formatting
- Applies subtle zebra striping, dark slate headers, and clean borders.
- Enforces `page-break-inside: avoid` on table rows to prevent awkward page splits.

### 8. Paged Media & Running Headers/Footers
- Uses CSS Paged Media `@page` margin boxes:
  - Running top headers with document title and reference ID.
  - Running footers with confidentiality notices and dynamic page counters (`Page X`).
  - Automatically suppresses top headers on the cover/first page (`@page :first`).
  - Strips default browser URL, date, and page print headers.

### 9. Formal Sign-Off Blocks
- Converts signature sections (`Approved on behalf of...`, `Signature:`, `Date:`) into side-by-side formal approval cards.

---

## 🛠️ Prerequisites

Before running `md2pdf`, ensure you have:

1. **Python 3.8+**: Standard Python installation.
2. **Node.js & npx**: Required for running `marked` (no global npm package installations required; runs via `npx --yes marked`).
3. **Google Chrome / Chromium**: Any standard installation of Google Chrome, Chromium, or Brave Browser.
   - *macOS*: `/Applications/Google Chrome.app` (detected automatically)
   - *Linux*: `google-chrome`, `google-chrome-stable`, or `chromium`
   - *Windows*: Standard Chrome program files path
   - *Custom Path*: Set the `CHROME_PATH` environment variable if Chrome is installed in a non-standard location.

---

## 🚀 Installation & Setup

### Option A: Install as an Antigravity Skill

To make `md2pdf` available to Antigravity agents across all workspaces:

```bash
mkdir -p ~/.gemini/config/skills/md2pdf
cp -r * ~/.gemini/config/skills/md2pdf/
```

Once installed, you can invoke the skill in conversation:
> *"Use `@skill:md2pdf` on `RFC-0001.md`"*  
> *"Convert `architecture_proposal.md` to PDF using md2pdf"*

### Option B: Standalone CLI Tool

Clone or copy this directory to your development environment:

```bash
git clone https://github.com/your-username/md2pdf.git ~/dev/md2pdf
chmod +x ~/dev/md2pdf/scripts/md2pdf.py
```

Optionally symlink it to your `PATH`:

```bash
ln -s ~/dev/md2pdf/scripts/md2pdf.py /usr/local/bin/md2pdf
```

---

## 📖 CLI Usage

```bash
python3 scripts/md2pdf.py <input.md> [output.pdf] [options]
```

### Positional Arguments
- `input`: Path to the input `.md` file.
- `output` *(optional)*: Path to the destination `.pdf` file. Defaults to `<input_dir>/<input_basename>.pdf`.

### Options
- `--paper {A4,letter,Letter}`: Paper format (default: `A4`).
- `--title TITLE`: Optional document title override for the cover header and running header.

### Examples

**Convert in-place (creates `spec.pdf` alongside `spec.md`):**
```bash
python3 scripts/md2pdf.py ./spec.md
```

**Specify custom output destination:**
```bash
python3 scripts/md2pdf.py ./docs/architecture.md ./dist/architecture-v1.pdf
```

**Use US Letter paper format:**
```bash
python3 scripts/md2pdf.py ./report.md ./report.pdf --paper letter
```

---

## 📂 Repository Structure

```
md2pdf/
├── README.md             # Project documentation
├── SKILL.md              # Antigravity skill specification
├── LICENSE               # Apache 2.0 license
├── .gitignore            # Git ignore rules
└── scripts/
    └── md2pdf.py         # Main converter script
```

---

## 📄 License

Licensed under the [Apache License, Version 2.0](LICENSE).
