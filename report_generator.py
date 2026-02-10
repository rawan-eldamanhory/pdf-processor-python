"""
PDF Report Generator.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

BRAND_DARK = colors.HexColor("#1A237E")   # deep navy
BRAND_MID = colors.HexColor("#3949AB")    # indigo
BRAND_ACCENT = colors.HexColor("#42A5F5") # blue
BRAND_LIGHT = colors.HexColor("#E3F2FD")  # very light blue
GREY_DARK = colors.HexColor("#424242")
GREY_MID = colors.HexColor("#757575")
GREY_LIGHT = colors.HexColor("#F5F5F5")
WHITE = colors.white
BLACK = colors.black


# ---------------------------------------------------------------------------
# Style factory
# ---------------------------------------------------------------------------


def _build_styles() -> Dict[str, ParagraphStyle]:
    """Build and return the custom paragraph style dictionary."""
    base = getSampleStyleSheet()

    styles: Dict[str, ParagraphStyle] = {}

    styles["Title"] = ParagraphStyle(
        "ReportTitle",
        parent=base["Normal"],
        fontSize=28,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    styles["Subtitle"] = ParagraphStyle(
        "ReportSubtitle",
        parent=base["Normal"],
        fontSize=14,
        fontName="Helvetica",
        textColor=BRAND_ACCENT,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    styles["H1"] = ParagraphStyle(
        "H1",
        parent=base["Normal"],
        fontSize=18,
        fontName="Helvetica-Bold",
        textColor=BRAND_DARK,
        spaceBefore=16,
        spaceAfter=8,
    )

    styles["H2"] = ParagraphStyle(
        "H2",
        parent=base["Normal"],
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=BRAND_MID,
        spaceBefore=12,
        spaceAfter=6,
    )

    styles["H3"] = ParagraphStyle(
        "H3",
        parent=base["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=GREY_DARK,
        spaceBefore=8,
        spaceAfter=4,
    )

    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=GREY_DARK,
        leading=14,
        spaceAfter=6,
    )

    styles["Bullet"] = ParagraphStyle(
        "Bullet",
        parent=base["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=GREY_DARK,
        leading=14,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=3,
    )

    styles["Caption"] = ParagraphStyle(
        "Caption",
        parent=base["Normal"],
        fontSize=9,
        fontName="Helvetica-Oblique",
        textColor=GREY_MID,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    styles["Footer"] = ParagraphStyle(
        "Footer",
        parent=base["Normal"],
        fontSize=8,
        fontName="Helvetica",
        textColor=GREY_MID,
        alignment=TA_CENTER,
    )

    return styles


# ---------------------------------------------------------------------------
# Page template callbacks
# ---------------------------------------------------------------------------


class _PageTemplate:
    """Callable used by SimpleDocTemplate for headers/footers."""

    def __init__(
        self,
        title: str,
        author: str,
        show_header: bool = True,
        show_footer: bool = True,
    ):
        self.title = title
        self.author = author
        self.show_header = show_header
        self.show_footer = show_footer

    def __call__(self, canvas, doc):
        canvas.saveState()
        w, h = doc.pagesize

        if self.show_header and doc.page > 1:
            # Blue header bar
            canvas.setFillColor(BRAND_DARK)
            canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)
            canvas.setFillColor(WHITE)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawString(1.5 * cm, h - 0.8 * cm, self.title)
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(w - 1.5 * cm, h - 0.8 * cm, self.author)

        if self.show_footer:
            # Light footer bar
            canvas.setFillColor(GREY_LIGHT)
            canvas.rect(0, 0, w, 0.9 * cm, fill=1, stroke=0)
            canvas.setFillColor(GREY_MID)
            canvas.setFont("Helvetica", 8)
            date_str = datetime.now().strftime("%B %d, %Y")
            canvas.drawString(1.5 * cm, 0.3 * cm, date_str)
            canvas.drawCentredString(w / 2, 0.3 * cm, "CONFIDENTIAL")
            canvas.drawRightString(
                w - 1.5 * cm, 0.3 * cm, f"Page {doc.page}"
            )

        canvas.restoreState()


# ---------------------------------------------------------------------------
# Table builder helper
# ---------------------------------------------------------------------------


def _build_pdf_table(
    headers: List[str],
    rows: List[List[Any]],
    col_widths: Optional[List[float]] = None,
    page_width: float = 17 * cm,
) -> Table:
    """
    Build a styled ReportLab Table.

    Args:
        headers: Column header labels.
        rows: Data rows (list of lists).
        col_widths: Optional explicit column widths in points.
        page_width: Available width used for auto-sizing.

    Returns:
        Styled ReportLab Table object.
    """
    styles = _build_styles()

    # Auto-distribute widths if not provided
    if col_widths is None:
        n = max(len(headers), 1)
        col_widths = [page_width / n] * n

    # Build data matrix
    header_cells = [
        Paragraph(f"<b>{h}</b>", styles["Body"]) for h in headers
    ]
    data: List[List[Any]] = [header_cells]

    for row in rows:
        data.append(
            [Paragraph(str(cell), styles["Body"]) for cell in row]
        )

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                # Alternating rows
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BRAND_LIGHT]),
                # All cells
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDBDBD")),
                ("LINEBELOW", (0, 0), (-1, 0), 1.5, BRAND_MID),
            ]
        )
    )
    return tbl


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_text_report(
    title: str,
    sections: List[Dict],
    output_path: str,
    author: str = "",
    subtitle: str = "",
    page_size: Any = A4,
) -> str:
    """
    Generate a professional text-only PDF report.

    Args:
        title: Report title.
        sections: List of section dicts. Each dict may have:
                  - "heading" (str)  → section heading
                  - "body" (str)     → paragraph text
                  - "bullets" (list) → bullet-point list
        output_path: Where to write the PDF.
        author: Author name shown in header.
        subtitle: Optional subtitle on title page.
        page_size: ReportLab page size (default A4).

    Returns:
        output_path
    """
    styles = _build_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    story: List[Any] = []

    # ---- Cover page --------------------------------------------------------
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(title, styles["Title"]))

    if subtitle:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(subtitle, styles["Subtitle"]))

    story.append(Spacer(1, 0.5 * cm))
    date_line = datetime.now().strftime("%B %d, %Y")
    if author:
        date_line = f"{author}  ·  {date_line}"
    story.append(Paragraph(date_line, styles["Caption"]))
    story.append(HRFlowable(width="100%", color=BRAND_ACCENT, thickness=2))
    story.append(PageBreak())

    # ---- Sections ----------------------------------------------------------
    for sec in sections:
        heading = sec.get("heading", "")
        body = sec.get("body", "")
        bullets = sec.get("bullets", [])
        level = sec.get("level", 1)

        heading_style = styles["H1"] if level == 1 else styles["H2"]

        if heading:
            story.append(Paragraph(heading, heading_style))
            story.append(
                HRFlowable(
                    width="100%",
                    color=BRAND_ACCENT if level == 1 else GREY_LIGHT,
                    thickness=1,
                )
            )
            story.append(Spacer(1, 0.2 * cm))

        if body:
            # Replace newlines with <br/> so ReportLab renders them
            body_html = body.replace("\n", "<br/>")
            story.append(Paragraph(body_html, styles["Body"]))

        for bullet in bullets:
            story.append(Paragraph(f"• {bullet}", styles["Bullet"]))

        story.append(Spacer(1, 0.3 * cm))

    doc.build(
        story,
        onFirstPage=_PageTemplate(title, author),
        onLaterPages=_PageTemplate(title, author),
    )

    return output_path


def generate_table_report(
    title: str,
    tables: List[Dict],
    output_path: str,
    author: str = "",
    intro: str = "",
    page_size: Any = A4,
) -> str:
    """
    Generate a PDF report that contains one or more data tables.

    Args:
        title: Report title.
        tables: List of table dicts. Each dict:
                  - "heading" (str)      → table heading
                  - "headers" (list)     → column headers
                  - "rows" (list[list])  → data rows
                  - "caption" (str)      → optional caption
        output_path: Where to write the PDF.
        author: Author name.
        intro: Introductory paragraph text.
        page_size: ReportLab page size.

    Returns:
        output_path
    """
    styles = _build_styles()
    w, _h = page_size
    usable_w = w - 4 * cm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    story: List[Any] = []

    # Cover
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(title, styles["Title"]))
    date_line = datetime.now().strftime("%B %d, %Y")
    if author:
        date_line = f"{author}  ·  {date_line}"
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(date_line, styles["Caption"]))
    story.append(HRFlowable(width="100%", color=BRAND_ACCENT, thickness=2))
    story.append(PageBreak())

    # Intro
    if intro:
        story.append(Paragraph(intro.replace("\n", "<br/>"), styles["Body"]))
        story.append(Spacer(1, 0.5 * cm))

    # Tables
    for tbl_def in tables:
        heading = tbl_def.get("heading", "")
        headers = tbl_def.get("headers", [])
        rows = tbl_def.get("rows", [])
        caption = tbl_def.get("caption", "")

        if heading:
            story.append(Paragraph(heading, styles["H1"]))
            story.append(
                HRFlowable(width="100%", color=BRAND_ACCENT, thickness=1)
            )
            story.append(Spacer(1, 0.2 * cm))

        if headers and rows:
            tbl = _build_pdf_table(headers, rows, page_width=usable_w)
            story.append(tbl)

        if caption:
            story.append(Spacer(1, 0.15 * cm))
            story.append(Paragraph(caption, styles["Caption"]))

        story.append(Spacer(1, 0.6 * cm))

    doc.build(
        story,
        onFirstPage=_PageTemplate(title, author),
        onLaterPages=_PageTemplate(title, author),
    )

    return output_path


def generate_full_report(
    title: str,
    output_path: str,
    author: str = "",
    subtitle: str = "",
    sections: Optional[List[Dict]] = None,
    tables: Optional[List[Dict]] = None,
    summary: str = "",
    page_size: Any = A4,
) -> str:
    """
    Generate a complete multi-section PDF report combining text and tables.

    Args:
        title: Report title.
        output_path: Destination path.
        author: Author name.
        subtitle: Cover subtitle.
        sections: List of text-section dicts (heading, body, bullets, level).
        tables: List of table dicts (heading, headers, rows, caption).
        summary: Optional summary paragraph printed at end.
        page_size: Page size.

    Returns:
        output_path
    """
    styles = _build_styles()
    w, _h = page_size
    usable_w = w - 4 * cm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    story: List[Any] = []

    # ---- Cover -------------------------------------------------------------
    story.append(Spacer(1, 1.5 * cm))

    # Navy cover banner
    banner_data = [[Paragraph(title, styles["Title"])]]
    banner = Table(banner_data, colWidths=[usable_w])
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
                ("TOPPADDING", (0, 0), (-1, -1), 18),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
                ("LEFTPADDING", (0, 0), (-1, -1), 20),
                ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ]
        )
    )
    story.append(banner)

    if subtitle:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(subtitle, styles["Subtitle"]))

    story.append(Spacer(1, 0.4 * cm))
    date_line = datetime.now().strftime("%B %d, %Y")
    if author:
        date_line = f"Prepared by: {author}  ·  {date_line}"
    story.append(Paragraph(date_line, styles["Caption"]))
    story.append(HRFlowable(width="100%", color=BRAND_ACCENT, thickness=2))
    story.append(PageBreak())

    # ---- Text sections -----------------------------------------------------
    for sec in sections or []:
        level = sec.get("level", 1)
        heading = sec.get("heading", "")
        body = sec.get("body", "")
        bullets = sec.get("bullets", [])

        heading_style = styles["H1"] if level == 1 else styles["H2"]

        if heading:
            story.append(Paragraph(heading, heading_style))
            story.append(
                HRFlowable(
                    width="100%",
                    color=BRAND_ACCENT if level == 1 else GREY_LIGHT,
                    thickness=1,
                )
            )
            story.append(Spacer(1, 0.2 * cm))

        if body:
            story.append(Paragraph(body.replace("\n", "<br/>"), styles["Body"]))

        for bullet in bullets:
            story.append(Paragraph(f"• {bullet}", styles["Bullet"]))

        story.append(Spacer(1, 0.4 * cm))

    # ---- Tables ------------------------------------------------------------
    for tbl_def in tables or []:
        heading = tbl_def.get("heading", "")
        headers = tbl_def.get("headers", [])
        rows = tbl_def.get("rows", [])
        caption = tbl_def.get("caption", "")

        if heading:
            story.append(Paragraph(heading, styles["H1"]))
            story.append(
                HRFlowable(width="100%", color=BRAND_ACCENT, thickness=1)
            )
            story.append(Spacer(1, 0.2 * cm))

        if headers and rows:
            story.append(_build_pdf_table(headers, rows, page_width=usable_w))

        if caption:
            story.append(Spacer(1, 0.15 * cm))
            story.append(Paragraph(caption, styles["Caption"]))

        story.append(Spacer(1, 0.5 * cm))

    # ---- Summary -----------------------------------------------------------
    if summary:
        story.append(HRFlowable(width="100%", color=BRAND_MID, thickness=1))
        story.append(Paragraph("Summary", styles["H1"]))
        story.append(Paragraph(summary.replace("\n", "<br/>"), styles["Body"]))

    doc.build(
        story,
        onFirstPage=_PageTemplate(title, author),
        onLaterPages=_PageTemplate(title, author),
    )

    return output_path
