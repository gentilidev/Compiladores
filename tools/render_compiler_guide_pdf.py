from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "material_estudo" / "guia_compilador_python.md"
OUTPUT = ROOT / "material_estudo" / "guia_compilador_python.pdf"


ACCENT = colors.HexColor("#1F5F6B")
ACCENT_DARK = colors.HexColor("#153E47")
MUTED = colors.HexColor("#5B6770")
LIGHT_BG = colors.HexColor("#EEF6F7")
CODE_BG = colors.HexColor("#F6F8FA")
RULE = colors.HexColor("#D8E2E4")


class CompilerGuideDoc(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, pagesize=A4, **kwargs)
        width, height = A4
        frame = Frame(
            2.0 * cm,
            1.85 * cm,
            width - 4.0 * cm,
            height - 3.7 * cm,
            id="normal",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[frame], onPage=self._cover_page),
                PageTemplate(id="body", frames=[frame], onPage=self._body_page),
            ]
        )

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = getattr(flowable, "plain_text", "")
            level = getattr(flowable, "toc_level", None)
            if level is not None:
                key = f"h-{abs(hash((text, self.page, level)))}"
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (level, text, self.page, key))

    def _cover_page(self, canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(ACCENT_DARK)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#2D7C88"))
        canvas.rect(0, 0, 1.25 * cm, height, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#8AC4CB"))
        canvas.setLineWidth(1.2)
        canvas.line(2.0 * cm, 3.2 * cm, width - 2.0 * cm, 3.2 * cm)
        canvas.restoreState()

    def _body_page(self, canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(2.0 * cm, height - 1.35 * cm, width - 2.0 * cm, height - 1.35 * cm)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(2.0 * cm, height - 1.05 * cm, "Guia de estudo: compilador didático em Python")
        canvas.drawRightString(width - 2.0 * cm, 1.2 * cm, str(doc.page))
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=32,
            alignment=TA_LEFT,
            textColor=colors.white,
            spaceAfter=18,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverSubtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=12.5,
            leading=18,
            textColor=colors.HexColor("#D7ECEF"),
            spaceAfter=14,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverMeta",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#A9D4D9"),
            uppercase=True,
        )
    )
    base.add(
        ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=23,
            textColor=ACCENT_DARK,
            spaceBefore=18,
            spaceAfter=8,
            keepWithNext=True,
        )
    )
    base.add(
        ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13.2,
            leading=17,
            textColor=ACCENT,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        )
    )
    base.add(
        ParagraphStyle(
            "BodyCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.4,
            leading=15.3,
            textColor=colors.HexColor("#222B31"),
            spaceAfter=7,
        )
    )
    base.add(
        ParagraphStyle(
            "SmallMuted",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            spaceAfter=5,
        )
    )
    base.add(
        ParagraphStyle(
            "BulletCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.2,
            leading=14.4,
            leftIndent=0,
            textColor=colors.HexColor("#222B31"),
        )
    )
    base.add(
        ParagraphStyle(
            "CodeCustom",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.7,
            leading=9.5,
            leftIndent=0,
            firstLineIndent=0,
            textColor=colors.HexColor("#202428"),
        )
    )
    base.add(
        ParagraphStyle(
            "CalloutCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.0,
            leading=14.2,
            textColor=ACCENT_DARK,
            spaceAfter=0,
        )
    )
    base.add(
        ParagraphStyle(
            "TOCTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=ACCENT_DARK,
            spaceAfter=12,
        )
    )
    return base


def inline_markup(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = text.replace("->", "&#8594;")
    return text


def code_table(code: str, st):
    code = code.rstrip("\n")
    flow = Preformatted(code, st["CodeCustom"], maxLineLength=92)
    table = Table([[flow]], colWidths=[17.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#D0D7DE")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return KeepTogether([Spacer(1, 3), table, Spacer(1, 7)])


def callout(text: str, st):
    p = Paragraph(inline_markup(text), st["CalloutCustom"])
    table = Table([[p]], colWidths=[17.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BBDADF")),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return KeepTogether([Spacer(1, 3), table, Spacer(1, 8)])


def paragraph(text: str, st):
    return Paragraph(inline_markup(text), st["BodyCustom"])


def heading(text: str, level: int, st):
    style = st["H1Custom"] if level == 1 else st["H2Custom"]
    p = Paragraph(inline_markup(text), style)
    p.toc_level = level - 1
    p.plain_text = text
    return p


def flush_paragraph(lines, story, st):
    if not lines:
        return []
    text = " ".join(line.strip() for line in lines).strip()
    if text:
        story.append(paragraph(text, st))
    return []


def flush_bullets(items, story, st):
    if not items:
        return []
    flow_items = [
        ListItem(Paragraph(inline_markup(item), st["BulletCustom"]), leftIndent=12)
        for item in items
    ]
    story.append(
        ListFlowable(
            flow_items,
            bulletType="bullet",
            start="circle",
            leftIndent=18,
            bulletFontName="Helvetica",
            bulletFontSize=8,
            bulletColor=ACCENT,
            spaceAfter=7,
        )
    )
    return []


def parse_markdown(markdown: str, st):
    story = []
    lines = markdown.splitlines()
    i = 0
    para_lines = []
    bullet_items = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            story.append(code_table("\n".join(code_lines), st))
            i += 1
            continue

        if not stripped:
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            i += 1
            continue

        if stripped == "---":
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            story.append(PageBreak())
            i += 1
            continue

        if stripped.startswith("# "):
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            story.append(heading(stripped[2:].strip(), 1, st))
            i += 1
            continue

        if stripped.startswith("## "):
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            story.append(heading(stripped[3:].strip(), 2, st))
            i += 1
            continue

        if stripped.startswith("> "):
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            story.append(callout(stripped[2:].strip(), st))
            i += 1
            continue

        if stripped.startswith("- "):
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items.append(stripped[2:].strip())
            i += 1
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            para_lines = flush_paragraph(para_lines, story, st)
            bullet_items = flush_bullets(bullet_items, story, st)
            story.append(Paragraph(inline_markup(stripped), st["BodyCustom"]))
            i += 1
            continue

        para_lines.append(line)
        i += 1

    flush_paragraph(para_lines, story, st)
    flush_bullets(bullet_items, story, st)
    return story


def build():
    st = styles()
    doc = CompilerGuideDoc(
        str(OUTPUT),
        title="Guia de Estudo: Como Construir um Compilador Didático em Python",
        author="Codex",
        subject="Compiladores",
        creator="Codex + ReportLab",
    )

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            fontName="Helvetica-Bold",
            name="TOCHeading1",
            fontSize=10.5,
            leading=14,
            firstLineIndent=0,
            leftIndent=0,
            textColor=ACCENT_DARK,
        ),
        ParagraphStyle(
            fontName="Helvetica",
            name="TOCHeading2",
            fontSize=9.5,
            leading=12,
            firstLineIndent=0,
            leftIndent=16,
            textColor=MUTED,
        ),
    ]

    story = [
        NextPageTemplate("cover"),
        Spacer(1, 5.4 * cm),
        Paragraph("Guia de Estudo:<br/>Compilador Didático em Python", st["CoverTitle"]),
        Paragraph(
            "Fundamentos, estrutura mental, exemplos pequenos e roteiro prático para você desenvolver seu próprio compilador.",
            st["CoverSubtitle"],
        ),
        Spacer(1, 0.6 * cm),
        Paragraph("Material de apoio ao projeto de Compiladores", st["CoverMeta"]),
        Paragraph("Foco: estudar, entender e implementar com autonomia", st["CoverMeta"]),
        NextPageTemplate("body"),
        PageBreak(),
        Paragraph("Sumário", st["TOCTitle"]),
        toc,
        PageBreak(),
    ]

    markdown = SOURCE.read_text(encoding="utf-8")
    story.extend(parse_markdown(markdown, st))

    doc.multiBuild(story)


if __name__ == "__main__":
    build()
