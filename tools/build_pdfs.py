"""Build self-contained, printable manuals from the published Markdown sources.

Requires reportlab and Windows Meiryo fonts (embedded as PDF subsets).
"""
from pathlib import Path
import re
from html import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, LongTable, TableStyle, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/pdf'
OUTPUT.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('Body', 'C:/Windows/Fonts/meiryo.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/meiryob.ttc', subfontIndex=0))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')
INK = colors.HexColor('#24474C')
TEAL = colors.HexColor('#347D7C')
PALE = colors.HexColor('#EDF5F2')
VERSION = (ROOT / 'VERSION').read_text().strip()


def markup(text):
    text = text.replace('—', '-').replace('–', '-').replace('\u2011', '-')
    text = escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<b>\1</b>', text)


class Document(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'Heading':
            self.outline_number = getattr(self, 'outline_number', 0) + 1
            key = 'section-' + str(self.outline_number)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0)


def create(kind, lang):
    jp = lang == 'ja'
    hint = kind == 'HINTBOOK'
    label = ('考え方のヒントブック' if hint else '操作と仕掛けのマニュアル') if jp else ('Technique Hintbook' if hint else 'Player Manual')
    path = OUTPUT / f'PAWS-PARTNERS-{"Hintbook" if hint else "Manual"}-{lang}.pdf'
    doc = Document(str(path), pagesize=A4, leftMargin=48, rightMargin=48,
                   topMargin=50, bottomMargin=46, title='PAWS PARTNERS - ' + label,
                   author='kanon-ai', pageCompression=1)
    styles = {
        'body': ParagraphStyle('Body', fontName='Body', fontSize=10, leading=16,
                               textColor=INK, spaceAfter=7, wordWrap='CJK' if jp else None),
        'heading': ParagraphStyle('Heading', fontName='Bold', fontSize=14, leading=21,
                                  textColor=TEAL, spaceBefore=17, spaceAfter=8, keepWithNext=True),
        'title': ParagraphStyle('Title', fontName='Bold', fontSize=23, leading=31,
                                textColor=INK, spaceAfter=12),
        'cell': ParagraphStyle('Cell', fontName='Body', fontSize=9, leading=14,
                               textColor=INK, wordWrap='CJK' if jp else None),
        'hint': ParagraphStyle('Hint', fontName='Bold', fontSize=10, leading=16,
                               textColor=TEAL, spaceBefore=9, spaceAfter=4, keepWithNext=True),
    }
    def para(text, style='body'):
        return Paragraph(markup(text), styles[style])
    story = [para('PAWS PARTNERS', 'title'), para(label, 'heading'),
             para(f'v{VERSION}  /  日本語' if jp else f'v{VERSION}  /  English'), Spacer(1, 9)]
    lines = (ROOT / f'docs/{kind}.{lang}.md').read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        text = lines[i].strip()
        i += 1
        if not text or text.startswith('# ') or text in ('<details>', '</details>'):
            continue
        if text.startswith('[English]') or text.startswith('[日本語]'):
            continue
        if text.startswith('## '):
            story.append(para(text[3:], 'heading'))
        elif text.startswith('<summary>'):
            story.append(para(re.sub(r'</?summary>', '', text), 'hint'))
        elif text.startswith('!['):
            match = re.match(r'!\[([^]]*)\]\(([^)]+)\)', text)
            image = Image(str(ROOT / 'docs' / match[2]))
            scale = min(doc.width / image.imageWidth, 230 / image.imageHeight, 1.0)
            image.drawWidth = image.imageWidth * scale
            image.drawHeight = image.imageHeight * scale
            image.hAlign = 'CENTER'
            story.append(KeepTogether([Spacer(1, 5), image, Spacer(1, 10)]))
        elif text.startswith('|'):
            rows = [text]
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            data = []
            for row in rows:
                if re.fullmatch(r'[|:\-\s]+', row):
                    continue
                data.append([para(cell.strip(), 'cell') for cell in row.strip('|').split('|')])
            widths = [doc.width * .29, doc.width * .71] if len(data[0]) == 2 else [doc.width * .20, doc.width * .22, doc.width * .58]
            if len(data[0]) == 4:
                widths = [doc.width / 4] * 4
            table = LongTable(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D5EAE4')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PALE]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('LINEBELOW', (0, 0), (-1, 0), .6, TEAL),
            ]))
            story.extend([table, Spacer(1, 10)])
        else:
            if text.startswith('> '):
                text = text[2:]
            elif text.startswith('- '):
                text = '• ' + text[2:]
            story.append(para(text))

    if hint:
        groups = []
        group = []
        for item in story:
            if isinstance(item, Paragraph) and item.style.name == 'Heading' and group:
                groups.append(KeepTogether(group)); group = []
            group.append(item)
        if group: groups.append(KeepTogether(group))
        story = groups

    def page(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#B7D3CB'))
        canvas.line(48, 38, A4[0]-48, 38)
        canvas.setFillColor(INK)
        canvas.setFont('Body', 8)
        canvas.drawString(48, 25, 'PAWS PARTNERS  |  v' + VERSION)
        canvas.drawRightString(A4[0]-48, 25, str(document.page))
        canvas.restoreState()
    doc.build(story, onFirstPage=page, onLaterPages=page)
    print(path)


if __name__ == '__main__':
    for kind in ['MANUAL', 'HINTBOOK']:
        for lang in ['ja', 'en']:
            create(kind, lang)
