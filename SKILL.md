---
name: md2pdf
description: Converts Markdown (.md) documents to high-fidelity, executive-ready PDF files with rendered formatting, syntax highlighting, vector Mermaid diagrams, KaTeX math formulas, alert callouts, Unicode ASCII diagrams, conversation transcripts, tables, running headers/footers, and formal sign-offs using marked and headless Google Chrome. Use whenever the user asks to convert, render, compile, or export Markdown (.md) files to PDF, or mentions md2pdf.
license: Apache-2.0
metadata:
  version: v1
  publisher: local
---

# md2pdf — Markdown to PDF Conversion Skill

This skill provides an automated, high-fidelity pipeline for converting Markdown documents (`.md`) into executive-ready, beautifully styled PDF files (`.pdf`).

## Capabilities

1. **Executive Document Header**:
   - Detects document reference, client/partner, author, date, and status tags from markdown frontmatter, RFC/spec headers, or top metadata tables.
   - Formats them into an executive metadata grid with status badges.
2. **Mermaid Graphs & Diagrams**:
   - Automatically detects and renders all Mermaid diagrams (`flowchart`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `stateDiagram`) into crisp vector SVG graphics.
   - Uses sequential unique ID rendering to prevent ID collisions and diagram overlapping across multi-diagram documents.
3. **KaTeX Mathematical Formula Rendering**:
   - Full typesetting for mathematical formulas and equations using KaTeX (`$$...$$` display math and `$..$` inline math).
4. **GitHub Alert Callouts**:
   - Converts `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]` blockquotes into modern styled callout containers.
5. **ASCII & Architecture Schematics**:
   - Detects Unicode box-drawing characters (`┌`, `─`, `│`, `└`, etc.) in fenced code blocks.
   - Renders them in a dark terminal card with macOS-style traffic lights and precise monospace typography without wrapping or broken lines.
6. **Conversational Transcripts & Chat Logs**:
   - Identifies multi-turn dialogues (`[User]:`, `[Agent]:`, `User:`, `Assistant:`).
   - Formats them into clean message transcript containers with speaker badges (`👤 User`, `🤖 Agent`) and clickable URLs.
7. **Structured Tables**:
   - Formats GFM tables with subtle zebra striping, dark slate headers, and clean borders.
   - Automatically prevents awkward page breaks inside rows and tables (`break-inside: avoid`).
8. **Paged Media & Document Numbering**:
   - Dynamic running headers with document title and document reference.
   - Running footers with confidentiality notices and live page counters (`Page X`).
   - Suppresses top header on the cover/first page (`@page :first`).
9. **Formal Approval & Sign-Off**:
   - Converts approval sections into side-by-side formal signature blocks.
10. **Clean Engine**:
   - Uses `npx marked` for fast, zero-dependency Markdown parsing.
   - Leverages headless Google Chrome for pixel-perfect PDF rendering with embedded document outlines and bookmarks.

---

## Workflow & Execution

When asked to convert any Markdown file to PDF, run the bundled conversion script:

```bash
python3 ~/.gemini/config/skills/md2pdf/scripts/md2pdf.py "<path_to_markdown_file.md>" ["<path_to_output.pdf>"]
```

### CLI Options

- `input` (required): Path to the input `.md` file.
- `output` (optional): Path to the destination `.pdf` file. Defaults to the same directory and basename as the input file.
- `--paper`: Paper size (`A4` [default] or `letter`).
- `--title`: Optional document title override.

### Example Commands

Convert in-place (creates `report.pdf` next to `report.md`):
```bash
python3 ~/.gemini/config/skills/md2pdf/scripts/md2pdf.py ./report.md
```

Specify custom output path and Letter paper format:
```bash
python3 ~/.gemini/config/skills/md2pdf/scripts/md2pdf.py ./docs/rfc-01.md ./build/rfc-01.pdf --paper letter
```

---

## Verification

After generating the PDF:
1. Verify the file exists and check its size:
   ```bash
   ls -lh "<path_to_output.pdf>"
   ```
2. Inspect the generated PDF visually using `view_file` to verify page breaks, diagram alignment, and typography.
3. Provide the user with a clickable link to the generated PDF: `[filename.pdf](file:///absolute/path/to/filename.pdf)`.
