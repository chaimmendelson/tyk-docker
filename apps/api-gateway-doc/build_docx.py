"""Build the API Gateway Enterprise Architecture Standard (.docx).

    ../.venv/bin/python build_docx.py             # build the working copy
    ../.venv/bin/python build_docx.py --archive   # ...and archive it as versions/v<version>/

Inputs : content.py (the document as data), figures.py (diagrams)
Outputs: API_Gateway_Enterprise_Architecture_Standard.docx, CHANGES.md
"""
import os
import re
import shutil
import sys
from datetime import datetime

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_TAB_ALIGNMENT,
                            WD_TAB_LEADER)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import content as C
import figures

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DOCX = os.path.join(HERE, "API_Gateway_Enterprise_Architecture_Standard.docx")
OUT_CHANGES = os.path.join(HERE, "CHANGES.md")
README = os.path.join(HERE, "README.md")

FONT, MONO = "Calibri", "Consolas"
NAVY, BLUE, GRAY = RGBColor(0x1F, 0x38, 0x64), RGBColor(0x2F, 0x54, 0x96), RGBColor(0x59, 0x59, 0x59)
NAVY_HEX, BLUE_HEX, LIGHT_HEX, GRID_HEX = "1F3864", "2F5496", "EAF0F9", "BFBFBF"
TEXT_W_CM = 16.0
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
             "rPr", "sectPr", "pPrChange"]
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
               "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd",
               "tblLayout", "tblCellMar", "tblLook"]
SECTPR_ORDER = ["headerReference", "footerReference", "footnotePr", "endnotePr", "type", "pgSz", "pgMar",
                "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols", "formProt", "vAlign", "noEndnote",
                "titlePg", "textDirection", "bidi", "rtlGutter", "docGrid", "printerSettings"]

errors = []


# ---------------------------------------------------------------------------
# Low-level XML helpers
# ---------------------------------------------------------------------------

def insert_ordered(parent, child, order):
    """Insert child into parent at the schema-correct position."""
    tag = child.tag.split("}")[1]
    for existing in parent.findall(child.tag):        # replace same-tag element
        parent.remove(existing)
    idx = order.index(tag)
    for el in list(parent):
        name = el.tag.split("}")[1]
        if name in order and order.index(name) > idx:
            el.addprevious(child)
            return child
    parent.append(child)
    return child


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(f"w:{k}"), str(v))
    return e


def para_border(pPr, side, color, sz, space=1):
    bdr = pPr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = insert_ordered(pPr, el("w:pBdr"), PPR_ORDER)
    for old in bdr.findall(qn(f"w:{side}")):
        bdr.remove(old)
    order = ["top", "left", "bottom", "right", "between", "bar"]
    new = el(f"w:{side}", val="single", sz=sz, space=space, color=color)
    for sib in list(bdr):
        if order.index(sib.tag.split("}")[1]) > order.index(side):
            sib.addprevious(new)
            return
    bdr.append(new)


def para_shade(pPr, fill):
    insert_ordered(pPr, el("w:shd", val="clear", color="auto", fill=fill), PPR_ORDER)


def set_style_font(style, name=FONT, size=None, bold=None, italic=None, color=None):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for a in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        if qn(f"w:{a}") in rfonts.attrib:
            del rfonts.attrib[qn(f"w:{a}")]
    for a in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{a}"), name)
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    if color is not None:
        style.font.color.rgb = color


def get_or_add_style(doc, name, base="Normal"):
    styles = doc.styles
    try:
        return styles[name]
    except KeyError:
        s = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        if base:
            s.base_style = styles[base]
        return s


# ---------------------------------------------------------------------------
# Numbering pass and reference resolution
# ---------------------------------------------------------------------------

class Nums:
    ch, sec, fig, tbl = {}, {}, {}, {}
    toc, figlist, tbllist, changes = [], [], [], []


def number_document():
    n = 0
    tbl_n = fig_n = 0
    for ch in C.CHAPTERS:
        if ch["appendix"]:
            label = f"Appendix {ch['appendix']}"
            prefix = ch["appendix"]
            ch["heading"] = f"{label} — {ch['title']}"
        else:
            n += 1
            label = f"Chapter {n}"
            prefix = str(n)
            ch["heading"] = f"{n}\t{ch['title']}"
        ch["label"], ch["prefix"] = label, prefix
        Nums.ch[ch["code"]] = label
        Nums.toc.append((1, ch["heading"]))
        sec_i, cur_sec = 0, None
        for b in ch["blocks"]:
            t = b["t"]
            if b.get("chg"):
                Nums.changes.append((cur_sec or f"{ch['label']} {ch['title']}", b["chg"]))
            if t == "h2":
                sec_i += 1
                b["num"] = f"{prefix}.{sec_i}"
                cur_sec = f"{b['num']} {b['title']}"
                Nums.sec[b["key"]] = f"Section {b['num']}"
                Nums.toc.append((2, f"{b['num']}\t{b['title']}"))
            elif t == "tbl":
                tbl_n += 1
                b["no"] = tbl_n
                Nums.tbl[b["key"]] = f"Table {tbl_n}"
                Nums.tbllist.append(f"Table {tbl_n} — {b['caption']}")
            elif t == "fig":
                fig_n += 1
                b["no"] = fig_n
                Nums.fig[b["key"]] = f"Figure {fig_n}"
                Nums.figlist.append(f"Figure {fig_n} — {b['caption']}")


REF = re.compile(r"\{(ch|sec|fig|tbl):(\w+)\}")


def resolve(s):
    def rep(m):
        kind, key = m.groups()
        table = {"ch": Nums.ch, "sec": Nums.sec, "fig": Nums.fig, "tbl": Nums.tbl}[kind]
        if key not in table:
            errors.append(f"unresolved reference {m.group(0)}")
            return m.group(0)
        return table[key]
    return REF.sub(rep, s).replace(", Section ", ", ")


# ---------------------------------------------------------------------------
# Inline text, fields, lists, tables
# ---------------------------------------------------------------------------

TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`|\[\[.+?\]\])")


def add_inline(par, text, size=None, bold=None, color=None):
    text = resolve(text)
    for tok in TOKEN.split(text):
        if not tok:
            continue
        run_kw = {}
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            tok, run_kw["bold"] = tok[2:-2], True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            tok, run_kw["italic"] = tok[1:-1], True
        elif tok.startswith("`") and tok.endswith("`"):
            tok, run_kw["mono"] = tok[1:-1], True
        elif tok.startswith("[[") and tok.endswith("]]"):
            tok, run_kw["hl"] = "[" + tok[2:-2] + "]", True
        run = par.add_run(tok)
        if size:
            run.font.size = Pt(size)
        if bold or run_kw.get("bold"):
            run.font.bold = True
        if run_kw.get("italic"):
            run.font.italic = True
        if color is not None:
            run.font.color.rgb = color
        if run_kw.get("mono"):
            run.font.name = MONO
            run.font.size = Pt((size or 10.5) - 1)
        if run_kw.get("hl"):
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return par


def add_field(par, instr, cached, size=None, bold=None):
    def marker(kind):
        r = par.add_run()
        r._r.append(el("w:fldChar", fldCharType=kind))
    marker("begin")
    r = par.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r._r.append(it)
    marker("separate")
    run = par.add_run(cached)
    if size:
        run.font.size = Pt(size)
    if bold:
        run.font.bold = True
    marker("end")


def add_field_block(doc, instr, entries):
    """A multi-paragraph field (TOC / table of figures) with cached entries.
    entries: [(style_name, text)]"""
    paras = []
    for style, text in entries:
        p = doc.add_paragraph(style=style)
        paras.append(p)
        for i, part in enumerate(text.split("\t")):
            if i:
                p.add_run("\t")
            p.add_run(part)
    if not paras:
        return
    first, last = paras[0], paras[-1]
    begin = OxmlElement("w:r")
    begin.append(el("w:fldChar", fldCharType="begin"))
    ins = OxmlElement("w:r")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    ins.append(it)
    sep = OxmlElement("w:r")
    sep.append(el("w:fldChar", fldCharType="separate"))
    anchor = first._p.find(qn("w:pPr"))
    for r in (sep, ins, begin):                         # insert after pPr, in order begin, instr, separate
        anchor.addnext(r)
    end = OxmlElement("w:r")
    end.append(el("w:fldChar", fldCharType="end"))
    last._p.append(end)


def add_bullet(container, text, left_cm, hang_cm=0.5, size=None, keep_next=False, style="List Bullet",
               space_after=2):
    p = container.add_paragraph(style=style)
    pf = p.paragraph_format
    pf.left_indent, pf.first_line_indent = Cm(left_cm), Cm(-hang_cm)
    pf.space_after = Pt(space_after)
    pf.keep_with_next = keep_next
    add_inline(p, text, size=size)
    return p


def set_cell_shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:shd")):
        tcPr.remove(old)
    order = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
             "textDirection", "tcFitText", "vAlign", "hideMark"]
    insert_ordered(tcPr, el("w:shd", val="clear", color="auto", fill=fill), order)


def fill_cell(cell, value, header=False, bold=False):
    cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)   # remove default empty paragraph
    if isinstance(value, list):
        for item in value:
            add_bullet(cell, item, 0.42, 0.34, size=9.5, style="List Bullet", space_after=1)
        return
    lines = str(value).split("\n") if value != "" else [""]
    for ln in lines:
        p = cell.add_paragraph(style="Table Text")
        add_inline(p, ln, bold=header or bold, color=RGBColor(0xFF, 0xFF, 0xFF) if header else None)


def add_table(doc, headers, rows, widths, first_bold=True):
    ncols = len(widths)
    body_rows = len(rows)
    tbl = doc.add_table(rows=body_rows + (1 if headers else 0), cols=ncols)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    total = int(sum(widths) * 567)
    insert_ordered(tblPr, el("w:tblW", w=total, type="dxa"), TBLPR_ORDER)
    borders = el("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(el(f"w:{side}", val="single", sz=4, space=0, color=GRID_HEX))
    insert_ordered(tblPr, borders, TBLPR_ORDER)
    insert_ordered(tblPr, el("w:tblLayout", type="fixed"), TBLPR_ORDER)
    mar = el("w:tblCellMar")
    for side, w in (("top", 50), ("left", 100), ("bottom", 50), ("right", 100)):
        mar.append(el(f"w:{side}", w=w, type="dxa"))
    insert_ordered(tblPr, mar, TBLPR_ORDER)
    for gc, w in zip(tbl._tbl.tblGrid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w * 567)))

    all_rows = ([headers] if headers else []) + rows
    for ri, (row, data) in enumerate(zip(tbl.rows, all_rows)):
        is_head = bool(headers) and ri == 0
        trPr = row._tr.get_or_add_trPr()
        trPr.append(el("w:cantSplit"))
        if is_head:
            trPr.append(el("w:tblHeader"))
        for ci, (cell, val) in enumerate(zip(row.cells, data)):
            cell.width = Cm(widths[ci])
            fill_cell(cell, val, header=is_head, bold=(ci == 0 and first_bold and not is_head))
            if is_head:
                set_cell_shade(cell, NAVY_HEX)
            elif ci == 0 and first_bold:
                set_cell_shade(cell, "F2F5FA")
    return tbl


def caption(doc, kind, no, text, keep_next):
    p = doc.add_paragraph(style="Caption")
    p.paragraph_format.keep_with_next = keep_next
    p.add_run(f"{kind} ")
    add_field(p, f"SEQ {kind} \\* ARABIC", str(no))
    add_inline(p, f" — {text}")
    return p


# ---------------------------------------------------------------------------
# Styles, page setup, header and footer
# ---------------------------------------------------------------------------

def setup_styles(doc):
    st = doc.styles
    normal = st["Normal"]
    set_style_font(normal, FONT, 10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.1
    normal.paragraph_format.widow_control = True

    h1 = st["Heading 1"]
    set_style_font(h1, FONT, 17, bold=True, color=NAVY)
    h1.paragraph_format.space_before, h1.paragraph_format.space_after = Pt(26), Pt(10)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.left_indent, h1.paragraph_format.first_line_indent = Cm(1.3), Cm(-1.3)
    h1.paragraph_format.tab_stops.add_tab_stop(Cm(1.3))
    para_border(h1.element.get_or_add_pPr(), "bottom", BLUE_HEX, 8, space=3)

    h2 = st["Heading 2"]
    set_style_font(h2, FONT, 13, bold=True, color=BLUE)
    h2.paragraph_format.space_before, h2.paragraph_format.space_after = Pt(16), Pt(6)
    h2.paragraph_format.keep_with_next = True
    h2.paragraph_format.left_indent, h2.paragraph_format.first_line_indent = Cm(1.3), Cm(-1.3)
    h2.paragraph_format.tab_stops.add_tab_stop(Cm(1.3))

    cap = st["Caption"]
    set_style_font(cap, FONT, 9.5, bold=True, italic=False, color=NAVY)
    cap.paragraph_format.space_before, cap.paragraph_format.space_after = Pt(8), Pt(4)

    lb = st["List Bullet"]
    set_style_font(lb, FONT, 10.5)
    ppr = lb.element.get_or_add_pPr()
    for cs in ppr.findall(qn("w:contextualSpacing")):    # template suppresses spacing between bullets
        ppr.remove(cs)

    note = get_or_add_style(doc, "Note")
    note.paragraph_format.space_before, note.paragraph_format.space_after = Pt(4), Pt(8)
    note.paragraph_format.left_indent = Cm(0.3)
    note.paragraph_format.keep_together = True
    pPr = note.element.get_or_add_pPr()
    para_border(pPr, "left", BLUE_HEX, 24, space=6)
    para_shade(pPr, LIGHT_HEX)

    tt = get_or_add_style(doc, "Table Text")
    set_style_font(tt, FONT, 9.5)
    tt.paragraph_format.space_after, tt.paragraph_format.line_spacing = Pt(2), 1.05

    tocw = get_or_add_style(doc, "Front Heading")
    set_style_font(tocw, FONT, 17, bold=True, color=NAVY)
    tocw.paragraph_format.space_before, tocw.paragraph_format.space_after = Pt(4), Pt(10)
    tocw.paragraph_format.keep_with_next = True
    para_border(tocw.element.get_or_add_pPr(), "bottom", BLUE_HEX, 8, space=3)

    sub = get_or_add_style(doc, "Front Subheading")
    set_style_font(sub, FONT, 12, bold=True, color=BLUE)
    sub.paragraph_format.space_before, sub.paragraph_format.space_after = Pt(14), Pt(4)
    sub.paragraph_format.keep_with_next = True

    # Word's built-in TOC styles are looked up by these lower-case names.
    for name, left, tab in (("toc 1", 0, 1.3), ("toc 2", 0.6, 1.9), ("table of figures", 0, None)):
        s = get_or_add_style(doc, name)
        set_style_font(s, FONT, 10.5 if name != "toc 2" else 10, bold=(name == "toc 1"))
        s.paragraph_format.left_indent = Cm(left)
        s.paragraph_format.space_after = Pt(3 if name != "toc 1" else 4)
        s.paragraph_format.space_before = Pt(6 if name == "toc 1" else 0)
        if tab:
            s.paragraph_format.tab_stops.add_tab_stop(Cm(tab))
        s.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    for name in ("Header", "Footer"):
        s = st[name]
        set_style_font(s, FONT, 9, color=GRAY)
        s.paragraph_format.tab_stops.clear_all()
        s.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W_CM), WD_TAB_ALIGNMENT.RIGHT)
    # document language
    rpr = normal.element.get_or_add_rPr()
    rpr.append(el("w:lang", val="en-GB", eastAsia="en-GB"))


def setup_page(doc):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.5)
    sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.3)
    sec.header_distance, sec.footer_distance = Cm(1.2), Cm(1.1)


def tabbed_paragraph(par, left):
    add_inline(par, left)
    par.add_run("\t")


def fill_header_footer(sec0, sec1):
    hp = sec0.header.paragraphs[0]
    tabbed_paragraph(hp, C.META["title"])
    add_inline(hp, C.META["classification"])
    para_border(hp._p.get_or_add_pPr(), "bottom", GRID_HEX, 4, space=4)

    for sec, total in ((sec0, False), (sec1, True)):
        if sec is sec1:
            sec.footer.is_linked_to_previous = False
        fp = sec.footer.paragraphs[0]
        tabbed_paragraph(fp, f"Version {C.META['version']} — {C.META['status']}")
        fp.add_run("Page ")
        add_field(fp, "PAGE", "1")
        if total:
            fp.add_run(" of ")
            add_field(fp, "SECTIONPAGES", "1")
        para_border(fp._p.get_or_add_pPr(), "top", GRID_HEX, 4, space=4)


def set_section_numbering(sec, fmt, start=None):
    sectPr = sec._sectPr
    attrs = {"fmt": fmt}
    if start is not None:
        attrs["start"] = start
    insert_ordered(sectPr, el("w:pgNumType", **attrs), SECTPR_ORDER)


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def spacer(doc, pts):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(pts)
    return p


def build_cover(doc):
    meta = C.META
    spacer(doc, 60)
    p = doc.add_paragraph()
    add_inline(p, meta["org"], size=14, bold=True, color=GRAY)
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(30), Pt(6)
    add_inline(p, meta["title"], size=32, bold=True, color=NAVY)
    para_border(p._p.get_or_add_pPr(), "bottom", BLUE_HEX, 12, space=10)
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(10), Pt(80)
    add_inline(p, meta["subtitle"], size=16, color=GRAY)
    add_table(doc, None,
              [["Version", f"{meta['version']}"], ["Status", meta["status"]], ["Date", meta["date"]],
               ["Document ID", meta["doc_id"]], ["Classification", meta["classification"]]],
              [4.0, 8.0])
    doc.add_page_break()


def build_document_control(doc):
    meta = C.META
    doc.add_paragraph("Document Control", style="Front Heading")
    add_table(doc, None,
              [["Document title", meta["title"]], ["Document ID", meta["doc_id"]],
               ["Version", meta["version"]], ["Status", meta["status"]],
               ["Classification", meta["classification"]], ["Document owner", meta["owner"]],
               ["Author", meta["author"]], ["Effective date", meta["effective"]],
               ["Review cycle", meta["review_cycle"]], ["Next review date", meta["next_review"]]],
              [4.6, 11.4])
    doc.add_paragraph("Revision History", style="Front Subheading")
    add_table(doc, ["Version", "Date", "Author", "Description"],
              [[r["version"], r["date"], r["author"], r["desc"]] for r in reversed(C.REVISIONS)],
              [2.2, 2.8, 3.6, 7.4], first_bold=False)
    doc.add_paragraph("Approval", style="Front Subheading")
    add_table(doc, ["Role", "Name", "Signature", "Date"],
              [["[[Role]]", "[[Name]]", "", ""], ["[[Role]]", "[[Name]]", "", ""],
               ["[[Role]]", "[[Name]]", "", ""]],
              [4.6, 4.6, 4.0, 2.8], first_bold=False)
    doc.add_page_break()


def build_contents(doc):
    doc.add_paragraph("Contents", style="Front Heading")
    add_field_block(doc, 'TOC \\o "1-2" \\h \\z \\u',
                    [(f"toc {lvl}", text) for lvl, text in Nums.toc])
    doc.add_paragraph("List of Figures", style="Front Subheading").paragraph_format.page_break_before = True
    add_field_block(doc, 'TOC \\h \\z \\c "Figure"', [("table of figures", t) for t in Nums.figlist])
    doc.add_paragraph("List of Tables", style="Front Subheading")
    add_field_block(doc, 'TOC \\h \\z \\c "Table"', [("table of figures", t) for t in Nums.tbllist])


# ---------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------

def render_picture(doc, b):
    path = os.path.join(figures.OUT_DIR, b["image"])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(path, width=Cm(b["width_cm"]))
    docpr = run._r.xpath(".//wp:docPr")[0]
    docpr.set("descr", b["alt"])
    docpr.set("title", b["caption"])
    cp = caption(doc, "Figure", b["no"], b["caption"], keep_next=False)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(10)


def build_body(doc):
    for ch in C.CHAPTERS:
        h = doc.add_paragraph(style="Heading 1")
        if ch["appendix"]:
            h.paragraph_format.page_break_before = True
            h.paragraph_format.left_indent = h.paragraph_format.first_line_indent = Cm(0)
        h.paragraph_format.space_before = Pt(0 if (ch["prefix"] == "1" or ch["appendix"]) else 26)
        h.add_run(ch["heading"])
        for b in ch["blocks"]:
            t = b["t"]
            if t == "h2":
                hp = doc.add_paragraph(style="Heading 2")
                if ch["appendix"]:
                    hp.paragraph_format.left_indent = Cm(1.3)
                hp.add_run(f"{b['num']}\t{b['title']}")
            elif t == "p":
                add_inline(doc.add_paragraph(), b["text"])
            elif t == "note":
                p = doc.add_paragraph(style="Note")
                if not b["text"].startswith("**"):
                    p.add_run("Note. ").font.bold = True
                add_inline(p, b["text"])
            elif t == "bul":
                for item in b["items"]:
                    add_bullet(doc, item, 0.9, 0.5, space_after=3)
            elif t == "tbl":
                caption(doc, "Table", b["no"], b["caption"], keep_next=True)
                add_table(doc, b["headers"], b["rows"], b["widths"], first_bold=b["first_bold"])
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            elif t == "fig":
                render_picture(doc, b)


# ---------------------------------------------------------------------------
# Document-level settings
# ---------------------------------------------------------------------------

def enable_update_fields(doc):
    settings = doc.settings.element
    zoom = settings.find(qn("w:zoom"))                  # template ships zoom without the required percent
    if zoom is not None:
        for a in list(zoom.attrib):
            del zoom.attrib[a]
        zoom.set(qn("w:percent"), "100")
    node = el("w:updateFields", val="true")
    compat = settings.find(qn("w:compat"))
    (compat.addprevious(node) if compat is not None else settings.append(node))


def set_properties(doc):
    cp = doc.core_properties
    cp.title, cp.subject = C.META["title"], C.META["subtitle"]
    cp.author = cp.last_modified_by = ""
    cp.keywords = "API Gateway; architecture; operating model; standard"
    cp.created = cp.modified = datetime.fromisoformat(C.META["date_iso"]).replace(hour=12)
    cp.comments = "Draft. Converted from README.md."


def strip_template_thumbnail(path):
    """The python-docx template carries a thumbnail of a blank page; drop it so the
    file preview is not misleading (Word regenerates it on save)."""
    import zipfile
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/thumbnail.jpeg":
                continue
            if item.filename == "_rels/.rels":
                data = re.sub(rb"<Relationship [^>]*thumbnail[^>]*/>", b"", data)
            zout.writestr(item, data)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    figures.generate_all()
    number_document()
    doc = Document()
    setup_page(doc)
    setup_styles(doc)

    build_cover(doc)
    build_document_control(doc)
    build_contents(doc)
    doc.add_section(WD_SECTION.NEW_PAGE)
    build_body(doc)

    sec0, sec1 = doc.sections[0], doc.sections[1]
    sec0.different_first_page_header_footer = True     # clean cover page
    sec1.different_first_page_header_footer = False
    set_section_numbering(sec0, "lowerRoman", start=1)
    set_section_numbering(sec1, "decimal", start=1)
    fill_header_footer(sec0, sec1)
    enable_update_fields(doc)
    set_properties(doc)

    if errors:
        print("BUILD ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    doc.save(OUT_DOCX)
    strip_template_thumbnail(OUT_DOCX)
    return doc


# ---------------------------------------------------------------------------
# CHANGES.md
# ---------------------------------------------------------------------------

def readme_sections():
    out = {}
    with open(README, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#{1,2}\s+(\d+)\.\s+(.+?)\s*$", line)
            if m:
                out[int(m.group(1))] = m.group(2)
    return out


def write_changes():
    titles = readme_sections()
    where = {}
    for ch in C.CHAPTERS:
        for s in ch["src"]:
            where.setdefault(s, []).append(f"{ch['label']} {ch['title']}")
        for b in ch["blocks"]:
            if b["t"] == "h2":
                for s in b["src"]:
                    where.setdefault(s, []).append(f"{b['num']} {b['title']}")
    missing = [i for i in range(1, 41) if i not in where]
    if missing:
        errors.append(f"README sections not mapped: {missing}")

    L = [f"# Change log: README.md → API Gateway Enterprise Architecture Standard (version {C.META['version']})", "",
         "Generated by `build_docx.py`. Review this file first: it lists every place where the rewrite "
         "changed meaning, not only wording.", "",
         "## How the wording was converted", "",
         "From version 1.2 the document is continuous prose, without numbered requirements. Obligations "
         "are carried by the wording of the sentence:", "",
         "- **must / must not** ← README *must*, *required*, *mandatory*, *not permitted*, and items marked "
         "'Required' or 'separate' in the README capability summary (§38).",
         "- **should / is recommended** ← README *should* where it expresses a preference or recommendation.",
         "- **can / may** ← README *can*, *may*, *optional*.",
         "- **Present tense** ← descriptive statements in the README (for example 'The application remains "
         "responsible for…', 'The Gateway validates…'), which set out how the platform is required to operate.", "",
         "Versions 1.0 and 1.1 (in `versions/`) use numbered requirements with *shall*, *should* and *may*.", "",
         "## Places where the meaning differs from the README", "",
         "Almost all are a README 'should' strengthened to 'must' or to the present tense. Please confirm "
         "each, or downgrade it to 'should'. The security-core rules (C2B/B2B tokens, no reliance on "
         "undocumented manual production configuration) were made mandatory by a review decision; other "
         "'should' statements are unchanged.", "",
         "| Section | Change |", "|---|---|"]
    for section, chg in Nums.changes:
        L.append(f"| {section} | {resolve(chg)} |")
    L += ["", "## Inconsistencies in the README and how they were resolved", ""]
    L += [f"{i}. {resolve(t)}" for i, t in enumerate(C.RESOLVED, 1)]
    L += ["", "## New content (not in the README)", ""] + [f"- {resolve(t)}" for t in C.NEW_CONTENT]
    L += ["", "## Decisions taken during review", "",
          "Open issues from the first draft that were settled. Each is now written into the document.", "",
          "| Topic | Decision and where it is recorded |", "|---|---|"]
    L += [f"| {topic} | {resolve(text)} |" for topic, text in C.DECISIONS]
    L += ["", "## Where each README section went", "",
          "| README § | README title | Location in the standard |", "|---|---|---|"]
    appx = {}
    for i in range(1, 41):
        loc = "; ".join(where.get(i, [])) or appx.get(i, "—")
        L.append(f"| {i} | {titles.get(i, '')} | {loc} |")
    L += ["", "## Placeholders to complete", "",
          "Highlighted yellow in the document: organization name, document ID, classification, document "
          "owner, author, effective date, review cycle, next review date, approver roles and names, and "
          "the two organizational references in Section 1.6.", "",
          "## Decisions the README does not make", "",
          f"See {resolve('{ch:APC}')} of the document (OI-01).", ""]
    with open(OUT_CHANGES, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------------------
# Version archive
# ---------------------------------------------------------------------------

VERSIONS_DIR = os.path.join(HERE, "versions")
DOC_STEM = "API_Gateway_Enterprise_Architecture_Standard"


def write_index():
    """versions/INDEX.md: one row per archived version, from C.REVISIONS."""
    rows = []
    for r in reversed(C.REVISIONS):
        folder = f"v{r['version']}"
        if os.path.isdir(os.path.join(VERSIONS_DIR, folder)):
            rows.append(f"| {r['version']} | {r['date']} | [{folder}/{DOC_STEM}_{folder}.docx]"
                        f"({folder}/{DOC_STEM}_{folder}.docx) | {resolve(r['desc']).replace('[', '').replace(']', '')} |")
    text = ["# Document versions", "",
            "Every issued version of the API Gateway Enterprise Architecture Standard. Archived versions "
            "are never overwritten; a change is issued as a new version.", "",
            "| Version | Date | File | Summary |", "|---|---|---|---|", *rows, "",
            "Each folder holds the .docx and the `CHANGES.md` that was current when it was issued. "
            "The latest working copy is `../" + DOC_STEM + ".docx`.", ""]
    with open(os.path.join(VERSIONS_DIR, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(text))


def archive():
    ver = C.META["version"]
    if not C.REVISIONS or C.REVISIONS[-1]["version"] != ver:
        print(f"cannot archive: latest REVISIONS entry is not version {ver}")
        return 1
    dest = os.path.join(VERSIONS_DIR, f"v{ver}")
    if os.path.exists(dest):
        print(f"cannot archive: {dest} already exists. Archived versions are not overwritten; "
              "bump META['version'] and add a REVISIONS entry.")
        return 1
    os.makedirs(dest)
    shutil.copy(OUT_DOCX, os.path.join(dest, f"{DOC_STEM}_v{ver}.docx"))
    shutil.copy(OUT_CHANGES, os.path.join(dest, "CHANGES.md"))
    write_index()
    print(f"archived version {ver} -> {dest}")
    return 0


# ---------------------------------------------------------------------------
# Verification of the saved file
# ---------------------------------------------------------------------------

def verify():
    doc = Document(OUT_DOCX)
    problems = []
    styles = [p.style.name for p in doc.paragraphs]

    # heading order: no H2 without a preceding H1
    seen_h1 = False
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            seen_h1 = True
        elif p.style.name == "Heading 2" and not seen_h1:
            problems.append(f"H2 before any H1: {p.text}")

    # wording: prose document, no numbered requirements, no 'shall'
    body_text = " ".join(p.text for p in doc.paragraphs)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                body_text += " " + cell.text
    if re.search(r"\bshall\b", body_text, re.I):
        problems.append("the word 'shall' is still used")
    if re.search(r"\bGW-[A-Z]+-\d+", body_text):
        problems.append("requirement identifiers are still present")
    words = len(body_text.split())
    modals = {w: len(re.findall(rf"\b{w}\b", body_text)) for w in ("must", "should", "may", "can")}

    # figures: alt text and caption; tables: caption count
    pics = doc.element.body.xpath(".//wp:docPr")
    if not pics or any(not d.get("descr") for d in pics):
        problems.append("figure without alt text")
    cap_fig = sum(1 for p in doc.paragraphs if p.style.name == "Caption" and p.text.startswith("Figure"))
    cap_tbl = sum(1 for p in doc.paragraphs if p.style.name == "Caption" and p.text.startswith("Table"))
    if cap_fig != len(pics):
        problems.append(f"{len(pics)} figures but {cap_fig} figure captions")
    if cap_tbl != len(Nums.tbllist):
        problems.append(f"{len(Nums.tbllist)} captioned tables expected, {cap_tbl} found")

    # placeholders must be highlighted; no leftover markup or unresolved refs
    def all_runs():
        for p in doc.paragraphs:
            yield from p.runs
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        yield from p.runs
    for r in all_runs():
        if "[" in r.text and r.font.highlight_color is None:
            problems.append(f"unhighlighted placeholder: {r.text[:50]}")
        if REF.search(r.text) or "**" in r.text or "[[" in r.text:
            problems.append(f"leftover markup: {r.text[:50]}")
        if re.search(r"\b(TBD|TODO|XXX)\b", r.text):
            problems.append(f"unfinished marker: {r.text[:50]}")

    # every README section 1-40 is mapped
    mapped = set()
    for ch in C.CHAPTERS:
        mapped.update(ch["src"])
        for b in ch["blocks"]:
            if b["t"] == "h2":
                mapped.update(b["src"])
    if not set(range(1, 41)) <= mapped:
        problems.append(f"README sections not covered: {sorted(set(range(1, 41)) - mapped)}")

    print(f"paragraphs={len(doc.paragraphs)} tables={len(doc.tables)} figures={len(pics)} "
          f"sections={len(doc.sections)} words={words} modal verbs={modals}")
    if not C.REVISIONS or C.REVISIONS[-1]["version"] != C.META["version"]:
        problems.append("META version does not match the latest REVISIONS entry")
    if problems:
        print("VERIFY PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1
    print("verify: OK")
    return 0


if __name__ == "__main__":
    build()
    write_changes()
    if errors:
        print("ERRORS:", *errors, sep="\n  - ")
        sys.exit(1)
    print(f"wrote {OUT_DOCX}")
    print(f"wrote {OUT_CHANGES}")
    status = verify()
    if status == 0 and "--archive" in sys.argv:
        status = archive()
    sys.exit(status)
