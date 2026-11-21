"""Create an academic DOCX review copy from canonical FINAL_REPORT.md.

Run from the Project root: python scripts/export_report_docx.py OUTPUT.docx
The Markdown source remains authoritative; this export never edits it.
"""
from pathlib import Path
import re
import sys

from docx import Document
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "FINAL_REPORT.md"


def plain(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "").replace("*", "")


def export(destination: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(.75)
    section.left_margin = section.right_margin = Inches(.8)
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].paragraph_format.space_after = Pt(5)
    for style, size in [("Title", 18), ("Heading 1", 14), ("Heading 2", 12)]:
        styles[style].font.name = "Times New Roman"
        styles[style].font.size = Pt(size)
        styles[style].font.color.rgb = None
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i]); i += 1
            p = doc.add_paragraph("\n".join(code))
            p.style = "Normal"
            for run in p.runs:
                run.font.name = "Consolas"; run.font.size = Pt(8)
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip()); i += 1
            rows = [[plain(x.strip()) for x in row.strip("|").split("|")] for row in block]
            rows = [row for row in rows if not all(re.fullmatch(r":?-+:?", x) for x in row)]
            table = doc.add_table(rows=0, cols=len(rows[0]))
            table.style = "Light Shading Accent 1"
            for row in rows:
                cells = table.add_row().cells
                for cell, value in zip(cells, row):
                    cell.text = value
                    for para in cell.paragraphs:
                        for run in para.runs:
                            run.font.size = Pt(8)
            continue
        image = re.fullmatch(r"!\[[^]]*\]\(([^)]+)\)", line)
        if image:
            path = ROOT / image.group(1)
            if path.exists():
                doc.add_picture(str(path), width=Inches(6.3))
            else:
                doc.add_paragraph(f"[Missing figure: {path.name}]")
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            doc.add_paragraph(plain(heading.group(2)), style="Title" if level == 1 else f"Heading {level-1}")
            i += 1
            continue
        if line.startswith("> "):
            doc.add_paragraph(plain(line[2:]))
        elif re.match(r"^\d+\. ", line):
            # Keep explicit source numbering: separate References and Appendix B
            # must each begin at 1 after DOCX/Google Docs conversion.
            doc.add_paragraph(plain(line))
        elif line.startswith("* ") or line.startswith("- "):
            doc.add_paragraph(plain(line[2:]), style="List Bullet")
        else:
            doc.add_paragraph(plain(line))
        i += 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destination)


if __name__ == "__main__":
    export(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "submission/FINAL_REPORT.docx")
