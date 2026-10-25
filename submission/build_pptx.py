"""
Generate AutoProcure.AI pitch deck as a native .pptx (editable in PowerPoint).
Thai text uses Tahoma (ships with Windows) for correct rendering.

Run:  python submission/build_pptx.py
Out:  submission/AutoProcure_AI_Pitch.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---- palette ----
NAVY = RGBColor(0x0F, 0x17, 0x2A)
BLUE = RGBColor(0x25, 0x63, 0xEB)
GREEN = RGBColor(0x05, 0x96, 0x69)
RED = RGBColor(0xDC, 0x26, 0x26)
SLATE = RGBColor(0x47, 0x55, 0x69)
LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0xD9, 0x77, 0x06)
FONT = "Tahoma"

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height


def _set(run, size, color, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic


def bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def box(slide, x, y, w, h, fill=None, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(1)
    shp.shadow.inherit = False
    return shp


def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """runs = list of paragraphs; each paragraph = list of (txt,size,color,bold,italic)."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(4)
        for seg in para:
            r = p.add_run(); r.text = seg[0]
            _set(r, seg[1], seg[2], seg[3] if len(seg) > 3 else False,
                 seg[4] if len(seg) > 4 else False)
    return tb


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


def tag(slide, label):
    """small criterion tag top-right."""
    b = box(slide, SW - Inches(2.3), Inches(0.25), Inches(2.0), Inches(0.42), fill=BLUE)
    text(slide, SW - Inches(2.3), Inches(0.28), Inches(2.0), Inches(0.38),
         [[(label, 10, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def header(slide, title, sub=None):
    box(slide, Inches(0.5), Inches(0.35), Inches(0.14), Inches(0.75), fill=BLUE)
    text(slide, Inches(0.8), Inches(0.33), Inches(9.5), Inches(0.9),
         [[(title, 28, NAVY, True)]])
    if sub:
        text(slide, Inches(0.82), Inches(1.15), Inches(11.5), Inches(0.5),
             [[(sub, 14, SLATE, False, True)]])


def bullets(slide, x, y, w, items, size=15):
    runs = []
    for it in items:
        runs.append([("•  ", size, BLUE, True), (it, size, SLATE)])
    text(slide, x, y, w, Inches(4.5), runs, spacing=1.15)


def stat_card(slide, x, y, w, big, small, color=BLUE):
    box(slide, x, y, w, Inches(1.25), fill=LIGHT)
    text(slide, x, y + Inches(0.15), w, Inches(0.6), [[(big, 26, color, True)]],
         align=PP_ALIGN.CENTER)
    text(slide, x, y + Inches(0.78), w, Inches(0.4), [[(small, 11, SLATE)]],
         align=PP_ALIGN.CENTER)


def simple_table(slide, x, y, w, rows, col_w, head_fill=NAVY, highlight_rows=None,
                 row_h=0.46, fs=11):
    highlight_rows = highlight_rows or {}
    n_rows, n_cols = len(rows), len(rows[0])
    gt = slide.shapes.add_table(n_rows, n_cols, x, y, w, Inches(row_h * n_rows)).table
    for ci, cw in enumerate(col_w):
        gt.columns[ci].width = Inches(cw)
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            c = gt.cell(ri, ci)
            c.margin_left = Inches(0.08); c.margin_right = Inches(0.06)
            c.margin_top = Inches(0.02); c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; r = p.add_run(); r.text = str(cell)
            if ri == 0:
                c.fill.solid(); c.fill.fore_color.rgb = head_fill
                _set(r, fs, WHITE, True)
            else:
                fill = highlight_rows.get(ri)
                c.fill.solid(); c.fill.fore_color.rgb = fill if fill else WHITE
                _set(r, fs, NAVY if fill else SLATE, bool(fill))
    return gt


def footer(slide, n):
    text(slide, SW - Inches(2.2), SH - Inches(0.45), Inches(2.0), Inches(0.3),
         [[(f"AutoProcure.AI  ·  {n}/17", 9, SLATE)]], align=PP_ALIGN.RIGHT)


# ============================ SLIDES ============================

# 1 — Title
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
box(s, Inches(0.9), Inches(1.6), Inches(0.2), Inches(1.4), fill=BLUE)
text(s, Inches(1.3), Inches(1.5), Inches(11), Inches(1.4),
     [[("AutoProcure.AI", 54, WHITE, True)]])
text(s, Inches(1.35), Inches(2.9), Inches(11), Inches(0.8),
     [[("พนักงานจัดซื้อ AI ที่เจรจาต่อรองราคากับซัพพลายเออร์ได้เอง ตลอด 24 ชั่วโมง", 18, RGBColor(0x93,0xC5,0xFD))]])
for i,(b,sm) in enumerate([("฿172 ล้าน","งบจัดซื้อที่บริหาร"),("฿25 ล้าน","ประหยัดได้จริง"),("61 ดีล","เจรจาอัตโนมัติ")]):
    x = Inches(1.35 + i*3.6)
    text(s, x, Inches(4.3), Inches(3.3), Inches(0.7), [[(b, 32, GREEN if i==1 else WHITE, True)]])
    text(s, x, Inches(5.05), Inches(3.3), Inches(0.4), [[(sm, 13, RGBColor(0xCB,0xD5,0xE1))]])
text(s, Inches(1.35), Inches(6.5), Inches(11), Inches(0.5),
     [[("หัวข้อ Manufacturing   ·   ทีมข้าวต้มมัดไส้กล้วย   ·   NTT DATA Digital Innovation Challenge 2026", 12, RGBColor(0x94,0xA3,0xB8))]])
notes(s, "สวัสดีครับ วันนี้ขอแนะนำ AutoProcure.AI ลองนึกภาพว่าโรงงานมีพนักงานจัดซื้อที่ไม่เคยพัก เจรจาต่อรองราคาได้ตลอด 24 ชั่วโมงกับซัพพลายเออร์ทุกราย ในโครงการนี้ระบบบริหารงบ 172 ล้านบาท และประหยัดได้จริง 25 ล้านบาท")

# 2 — Problem
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "01 Problem")
header(s, "ทำไมโรงงานถึงจ่ายค่าอะไหล่แพงเกินจำเป็น?")
text(s, Inches(0.8), Inches(1.5), Inches(7.0), Inches(2.6), [
    [("โรงงานต้องซื้ออะไหล่ซ่อมบำรุงจำนวนมาก เช่น ตลับลูกปืน สายพาน เซนเซอร์ วาล์วลม", 15, SLATE)],
    [("แต่ละครั้งมูลค่าไม่มาก เลยไม่มีใครมานั่งต่อรองราคา — ส่วนใหญ่ 'ซื้อด่วนหน้าร้าน'", 15, SLATE)],
    [("ในราคาที่เขาตั้งมา ทำให้จ่ายแพงกว่าที่ควรทุกครั้ง", 15, SLATE)],
    [("พอรวมกันทั้งปี กลายเป็นเงินก้อนใหญ่ที่รั่วไหลไปเงียบ ๆ", 15, NAVY, True)],
], spacing=1.2)
for i,(b,sm) in enumerate([("2,489","ใบสั่งซื้อ/ปี"),("5","โรงงาน"),("฿172.6M","งบรวม/ปี"),("61","กลุ่มสินค้า")]):
    stat_card(s, Inches(0.8 + i*3.0), Inches(4.4), Inches(2.75), b, sm, RED if i==2 else BLUE)
text(s, Inches(8.3), Inches(1.6), Inches(4.4), Inches(2.8), [
    [("[📷 ใส่กราฟ Pareto —", 12, SLATE, False, True)],
    [("slide02_problem_pareto]", 12, SLATE, False, True)],
], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
box(s, Inches(8.3), Inches(1.6), Inches(4.4), Inches(2.6), line=RGBColor(0xCB,0xD5,0xE1))
footer(s, 2)
notes(s, "ปัญหาที่เราเจอคือโรงงานซื้ออะไหล่ซ่อมบำรุงเป็นพัน ๆ ใบต่อปี แต่ละใบมูลค่าไม่เยอะ เลยไม่มีเวลาต่อรอง ซื้อด่วนหน้าร้านในราคาที่เขาตั้งมา พอรวมทั้งปีคือ 172 ล้านบาทที่จ่ายแพงเกินจำเป็น นี่คือเงินที่รั่วไหลโดยไม่มีใครเห็น")

# 3 — Persona
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "01 Problem")
header(s, "ใครเจ็บปวดกับปัญหานี้?")
personas = [
    ("หัวหน้าฝ่ายจัดซื้อ", "\"ดูแลสินค้า 61 กลุ่ม แต่มีเวลาต่อรองจริงแค่ 5 ดีลใหญ่ ที่เหลือปล่อยตามมีตามเกิด\""),
    ("วิศวกรโรงงาน", "\"เครื่องจักรเสีย ต้องการอะไหล่ด่วน แต่ขั้นตอนจัดซื้อช้า\""),
    ("ผู้บริหาร (CPO)", "\"ต้องมั่นใจว่าโปร่งใส ตรวจสอบย้อนหลังได้ ก่อนเซ็นอนุมัติ\""),
]
for i,(name,quote) in enumerate(personas):
    x = Inches(0.8 + i*4.05)
    box(s, x, Inches(1.7), Inches(3.8), Inches(2.6), fill=LIGHT)
    text(s, x+Inches(0.2), Inches(1.9), Inches(3.5), Inches(0.5), [[(name, 16, BLUE, True)]])
    text(s, x+Inches(0.2), Inches(2.5), Inches(3.5), Inches(1.7), [[(quote, 13, SLATE, False, True)]], spacing=1.15)
box(s, Inches(0.8), Inches(4.7), Inches(11.75), Inches(1.0), fill=RGBColor(0xFE,0xF2,0xF2), line=RED)
text(s, Inches(1.0), Inches(4.8), Inches(11.4), Inches(0.9), [
    [("ขั้นตอนเดิม:  ", 14, RED, True), ("ใบขอซื้อกระจาย → ซื้อด่วนแยกใบ → ไม่ได้ต่อรอง → จ่ายแพง → ไม่มีบันทึกตรวจสอบ", 14, SLATE)],
], anchor=MSO_ANCHOR.MIDDLE)
footer(s, 3)
notes(s, "คนที่เจ็บปวดมี 3 กลุ่ม หัวหน้าจัดซื้อที่งานล้นมือ วิศวกรที่รอของนาน และผู้บริหารที่ต้องการความโปร่งใส ขั้นตอนเดิมคือซื้อแยกใบ ไม่มีการต่อรอง และตรวจสอบย้อนหลังแทบไม่ได้")

# 4 — Business
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "06 Business")
header(s, "โอกาสทางธุรกิจ + โมเดลรายได้")
text(s, Inches(0.8), Inches(1.55), Inches(6.2), Inches(0.5), [[("ขนาดตลาด (จากกว้างไปแคบ)", 15, NAVY, True)]])
for i,(lbl,desc,col) in enumerate([
    ("ตลาดรวม","งบจัดซื้ออะไหล่ซ่อมบำรุงภาคการผลิตไทย (EEC) — หลักหมื่นล้าน/ปี", RGBColor(0xBF,0xDB,0xFE)),
    ("ที่เข้าถึงได้","โรงงานกลาง-ใหญ่ที่ใช้ SAP/ERP", RGBColor(0x60,0xA5,0xFA)),
    ("ลูกค้ากลุ่มแรก","5 โรงงาน = งบ ฿172.6 ล้าน/ปี", BLUE),
]):
    y = Inches(2.05 + i*0.95); w = Inches(6.2 - i*1.2)
    box(s, Inches(0.8), y, w, Inches(0.8), fill=col)
    text(s, Inches(0.95), y, w-Inches(0.2), Inches(0.8),
         [[(lbl+": ", 12, NAVY, True),(desc, 11, NAVY)]], anchor=MSO_ANCHOR.MIDDLE)
box(s, Inches(7.4), Inches(1.7), Inches(5.1), Inches(3.9), fill=LIGHT)
text(s, Inches(7.6), Inches(1.85), Inches(4.7), Inches(0.5), [[("โมเดลรายได้ (SaaS)", 15, GREEN, True)]])
text(s, Inches(7.6), Inches(2.5), Inches(4.7), Inches(3.0), [
    [("1. Success-based", 14, NAVY, True)],
    [("คิดค่าบริการเป็น % จากเงินที่ลูกค้าประหยัดได้จริง — ลูกค้าได้ผลก่อนจ่าย ความเสี่ยงต่ำ", 12, SLATE)],
    [("", 6, SLATE)],
    [("2. Subscription", 14, NAVY, True)],
    [("รายเดือนต่อจำนวนผู้ใช้/โรงงาน — รายได้สม่ำเสมอ", 12, SLATE)],
], spacing=1.15)
footer(s, 4)
notes(s, "นี่ไม่ใช่แค่โปรเจกต์เดโม แต่เป็นธุรกิจจริง เราคิดค่าบริการแบบแบ่งจากเงินที่ลูกค้าประหยัดได้ ลูกค้าเห็นผลก่อนจ่าย ความเสี่ยงต่ำ และตลาดนี้ในไทยมีมูลค่าหลักหมื่นล้านบาทต่อปี")

# 5 — Solution overview
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "05 UX")
header(s, "วิธีแก้: ทำงาน 3 ขั้น")
steps = [
    ("1. รวมยอด", "จับใบขอซื้อ 2,489 ใบที่กระจาย มารวมเป็น 61 กลุ่มสินค้า เกิดอำนาจต่อรองจากปริมาณ", BLUE),
    ("2. เจรจา", "AI หลายตัวทำงานร่วมกัน เจรจาภาษาไทยเชิงธุรกิจ อ้างอิงราคากลางตลาด", GREEN),
    ("3. ปิดดีล", "ตกลงได้ → ผู้บริหารเซ็นอนุมัติ → ออกใบสั่งซื้อเข้า SAP อัตโนมัติ", NAVY),
]
for i,(t,d,col) in enumerate(steps):
    x = Inches(0.8 + i*4.05)
    box(s, x, Inches(2.0), Inches(3.8), Inches(3.2), fill=LIGHT)
    box(s, x, Inches(2.0), Inches(3.8), Inches(0.75), fill=col)
    text(s, x, Inches(2.05), Inches(3.8), Inches(0.65), [[(t, 18, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x+Inches(0.25), Inches(3.0), Inches(3.3), Inches(2.0), [[(d, 14, SLATE)]], spacing=1.2)
footer(s, 5)
notes(s, "วิธีแก้มี 3 ขั้นง่าย ๆ หนึ่งรวมใบขอซื้อที่กระจายให้เป็นกลุ่มใหญ่เพื่อให้มีอำนาจต่อรอง สองให้ AI เจรจาแทนคน และสามปิดดีลออกใบสั่งซื้อเข้า SAP อัตโนมัติ ครบวงจรจริง")

# 6 — Why multi-agent
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "02 Agentic")
header(s, "ทำไมต้องเป็น 'หลาย AI' ไม่ใช่ AI ตัวเดียว?")
rows = [
    ["แนวทาง","ข้อดี","ข้อเสีย","เหมาะกับงานนี้?"],
    ["AI ตัวเดียว ครอบทุกงาน","ทำง่าย โค้ดน้อย","ใช้โมเดลใหญ่แพงกับทุกงาน / ตรวจสอบยาก","❌ เปลืองและคุมยาก"],
    ["หลาย AI แยกตามหน้าที่ (ของเรา)","เลือกโมเดลเหมาะแต่ละงาน คุม cost / ตรวจสอบได้ / ต่อยอดง่าย","ออกแบบซับซ้อนกว่า","✅ เหมาะกับงานเจรจา"],
]
simple_table(s, Inches(0.8), Inches(1.7), Inches(11.75), rows, [2.6,3.6,3.6,1.95],
             highlight_rows={2: RGBColor(0xD1,0xFA,0xE5)}, row_h=1.0, fs=12)
box(s, Inches(0.8), Inches(5.1), Inches(11.75), Inches(0.95), fill=RGBColor(0xEF,0xF6,0xFF), line=BLUE)
text(s, Inches(1.0), Inches(5.2), Inches(11.4), Inches(0.8), [
    [("เราเลือกแบบหลาย AI เพราะงานเจรจามีหลายขั้นที่ความยากต่างกัน — งานง่ายใช้โมเดลถูก งานยากใช้โมเดลเก่ง ประหยัดเงินและตรวจสอบได้", 13, NAVY, True)]
], anchor=MSO_ANCHOR.MIDDLE)
footer(s, 6)
notes(s, "คำถามแรกคือจะใช้ AI ตัวเดียวหรือหลายตัว เราเลือกหลายตัวเพราะงานเจรจามีทั้งงานง่ายอย่างการอ่านข้อความ และงานยากอย่างการวางกลยุทธ์ ถ้าใช้ตัวเดียวต้องจ่ายค่าโมเดลแพงกับทุกงาน การแยกหน้าที่ทำให้เลือกโมเดลให้เหมาะและคุมต้นทุนได้")

# 7 — 5 agents
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "02 Agentic")
header(s, "สถาปัตยกรรม 5 AI Agent")
agents = [
    ("1  ยามความปลอดภัย","Compliance Guardrail","กันการหลอก/โจมตี + ล็อกเพดานราคา", RED),
    ("2  ตัวอ่านข้อความ","Router · Nova Micro","อ่านว่าเสนออะไร: ราคา เครดิต ประกัน", BLUE),
    ("3  นักวิเคราะห์ราคา","Market Intelligence","ดึงราคากลางตลาด มาเป็นแต้มต่อ", GREEN),
    ("4  นักเจรจา","Negotiator · Nova Pro","วางกลยุทธ์ เจรจาไทย + ทฤษฎีเกม", NAVY),
    ("5  กรรมการตัดสิน","Central Arbitrator","ให้คะแนนรวม TCO + จัดอันดับเจ้าที่คุ้มสุด", AMBER),
]
for i,(t,sub,d,col) in enumerate(agents):
    x = Inches(0.6 + i*2.45)
    box(s, x, Inches(2.0), Inches(2.25), Inches(3.4), fill=LIGHT, line=col)
    box(s, x, Inches(2.0), Inches(2.25), Inches(0.5), fill=col)
    text(s, x, Inches(2.02), Inches(2.25), Inches(0.45), [[(t, 12, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x+Inches(0.12), Inches(2.6), Inches(2.0), Inches(0.6), [[(sub, 11, col, True)]])
    text(s, x+Inches(0.12), Inches(3.3), Inches(2.0), Inches(2.0), [[(d, 11, SLATE)]], spacing=1.1)
text(s, Inches(0.6), Inches(5.6), Inches(11.9), Inches(0.5),
     [[("ส่งต่องานเป็นสายพาน (pipeline) — ไม่ใช่ prompt เดียวครอบทุกอย่าง", 13, NAVY, True)]], align=PP_ALIGN.CENTER)
footer(s, 7)
notes(s, "ระบบแบ่งเป็น 5 AI ที่ทำงานต่อกันเป็นสายพาน เริ่มจากยามตรวจความปลอดภัย ตัวอ่านข้อเสนอ นักวิเคราะห์ราคาตลาด นักเจรจา และกรรมการที่ตัดสินว่าเจ้าไหนคุ้มที่สุด แต่ละตัวมีหน้าที่ชัดเจน")

# 8 — Agentic evidence
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "02 Agentic")
header(s, "หลักฐานว่าเป็น Agent จริง (ไม่ใช่แค่ Chatbot)")
ev = [
    ("แผนการทำงานที่มองเห็นได้","ระบบบันทึก audit trace ทุกขั้น: ขั้นที่ / AI ตัวไหน / คิดอะไร / เรียกเครื่องมืออะไร"),
    ("เรียกเครื่องมือจริง","คำนวณต้นทุนรวม · คำนวณจุดแลกเปลี่ยน (ทฤษฎีเกม) · ตรวจความปลอดภัย · ดึงราคากลาง"),
    ("ดึงความรู้จากคลัง (RAG)","คลังราคาอะไหล่ไทย 10 หมวด → ค้นด้วยรหัส/แบรนด์/คีย์เวิร์ด → ได้ช่วงราคากลาง"),
    ("เลือกโมเดลตามงาน","Nova Micro (อ่าน) / Nova Pro (เจรจา)"),
]
for i,(t,d) in enumerate(ev):
    y = Inches(1.6 + i*0.92)
    box(s, Inches(0.8), y, Inches(6.9), Inches(0.82), fill=LIGHT)
    text(s, Inches(1.0), y, Inches(6.6), Inches(0.82), [[(f"{i+1}. {t}  ", 13, BLUE, True),(d, 11, SLATE)]], anchor=MSO_ANCHOR.MIDDLE, spacing=1.05)
box(s, Inches(8.0), Inches(1.6), Inches(4.55), Inches(3.9), line=RGBColor(0xCB,0xD5,0xE1))
text(s, Inches(8.0), Inches(1.6), Inches(4.55), Inches(3.9), [
    [("[📷 Screenshot จากเว็บ:", 12, SLATE, False, True)],
    [("Audit Trace / Reasoning", 12, SLATE, False, True)],
    [("Timeline 6 ขั้นในห้องเจรจา]", 12, SLATE, False, True)],
    [("", 8, SLATE)],
    [("← หลักฐาน agentic ที่แข็งสุด", 11, RED, True)],
], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 8)
notes(s, "กรรมการอยากเห็นว่าเป็น Agent จริงไหม เรามีครบ: ระบบบันทึกแผนการทำงานทุกขั้นให้เห็น เรียกเครื่องมือคำนวณจริง ดึงราคากลางจากคลังข้อมูลแบบ RAG และเลือกโมเดลให้เหมาะกับงาน นี่คือภาพ audit trace จริงที่โชว์ทุกการตัดสินใจของ AI")

# 9 — Model comparison
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "02+06")
header(s, "เลือกโมเดลยังไง + ทำไมถึงประหยัด")
rowsA = [
    ["โมเดล","ราคา เข้า/ออก ($/1M)","ภาษาไทย","การตัดสินใจ"],
    ["Nova Micro","$0.035 / $0.14","พอใช้","✅ ตัวอ่านข้อความ (งานไม่ลึก)"],
    ["Nova Lite","$0.06 / $0.24","ดี","สำรอง (tier กลาง)"],
    ["Nova Pro","$0.80 / $3.20","ดีมาก","✅ นักเจรจา (งานกลยุทธ์)"],
    ["Claude 3.5 Sonnet","$3.00 / $15.00","ดีมาก","❌ แพงกว่า Pro ~4 เท่า + ข้ามค่าย"],
]
simple_table(s, Inches(0.8), Inches(1.55), Inches(7.1), rowsA, [1.8,2.1,1.1,2.1],
             highlight_rows={1: RGBColor(0xD1,0xFA,0xE5), 3: RGBColor(0xD1,0xFA,0xE5), 4: RGBColor(0xFE,0xE2,0xE2)}, row_h=0.6, fs=11)
text(s, Inches(8.15), Inches(1.55), Inches(4.4), Inches(0.4), [[("ต้นทุนต่อการเจรจา 1 รอบ", 13, NAVY, True)]])
rowsB = [
    ["กลยุทธ์","$/รอบ","เทียบ"],
    ["Claude ทุกงาน","~$0.011","1.0×"],
    ["Nova Pro ทุกงาน","~$0.0014","0.13×"],
    ["Micro + Pro (ของเรา)","~$0.0011","0.10×"],
]
simple_table(s, Inches(8.15), Inches(2.0), Inches(4.4), rowsB, [2.2,1.2,1.0],
             highlight_rows={3: RGBColor(0xD1,0xFA,0xE5)}, row_h=0.58, fs=11)
text(s, Inches(0.8), Inches(5.3), Inches(11.75), Inches(1.0), [
    [("เลือก Nova เพราะอยู่ใน AWS เดียวกัน ถูกกว่า Claude หลายเท่า และภาษาไทยดีพอสำหรับงานเจรจาจริง → ต้นทุนถูกลงเกือบ 10 เท่า", 13, GREEN, True)],
    [("ราคาอ้างอิง: AWS Bedrock / Amazon Nova pricing (ต.ค. 2026)", 10, SLATE, False, True)],
])
footer(s, 9)
notes(s, "เราไม่ได้เลือกโมเดลมั่ว ๆ เราเทียบก่อน Claude Sonnet เก่งก็จริงแต่แพงกว่า Nova Pro ถึง 4 เท่าและต้องข้ามค่าย เราเลยเลือก Nova Pro ที่ภาษาไทยดีพอกันแต่ถูกกว่ามาก งานอ่านง่าย ๆ ใช้ Nova Micro ที่ถูกสุด รวมแล้วต้นทุนต่อการเจรจาถูกลงเกือบ 10 เท่าเทียบกับใช้ Claude ทั้งหมด")

# 10 — Live demo
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "03 Prototype")
header(s, "ตัวอย่างการทำงานจริง (Live Demo)")
text(s, Inches(0.8), Inches(1.5), Inches(11.5), Inches(1.3), [
    [("ซัพพลายเออร์เสนอ ฿440", 14, SLATE), ("  →  ", 14, BLUE, True), ("AI อ้างราคากลางตลาด ฿380-470", 14, SLATE),
     ("  →  ", 14, BLUE, True), ("เสนอสัญญารายปีแลกราคา ฿398", 14, SLATE), ("  →  ", 14, BLUE, True),
     ("ตกลง → เลื่อนเป็น 'รออนุมัติ PO' อัตโนมัติ", 14, GREEN, True)],
], spacing=1.3)
box(s, Inches(0.8), Inches(2.9), Inches(5.75), Inches(3.3), line=RGBColor(0xCB,0xD5,0xE1))
text(s, Inches(0.8), Inches(2.9), Inches(5.75), Inches(3.3), [[("[📷 Supplier Portal ขณะเจรจา]", 13, SLATE, False, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
box(s, Inches(6.8), Inches(2.9), Inches(5.75), Inches(3.3), line=RGBColor(0xCB,0xD5,0xE1))
text(s, Inches(6.8), Inches(2.9), Inches(5.75), Inches(3.3), [[("[📷 Buyer Dashboard เด้งสด]", 13, SLATE, False, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
box(s, Inches(0.8), Inches(6.35), Inches(11.75), Inches(0.5), fill=RGBColor(0xEF,0xF6,0xFF))
text(s, Inches(0.8), Inches(6.35), Inches(11.75), Inches(0.5), [[("รันจริงบน AWS Bedrock — ข้อความ AI มาจาก Nova Pro สด ๆ", 12, BLUE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 10)
notes(s, "นี่คือการทำงานจริง ซัพพลายเออร์เสนอราคา 440 บาท AI ตอบกลับเป็นภาษาไทยเชิงธุรกิจ อ้างราคากลางตลาดเป็นหลักฐาน แล้วเสนอทำสัญญารายปีแลกกับราคาที่ดีกว่า พอตกลงได้ดีลก็เลื่อนสถานะอัตโนมัติ ทั้งหมดรันจริงบน AWS Bedrock")

# 11 — AWS architecture
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "03 Prototype")
header(s, "สถาปัตยกรรม AWS + การ Deploy")
svcs = [
    ("Amazon Bedrock","เรียกใช้ Nova Micro/Pro"),
    ("Bedrock Guardrails","กันการโจมตี AI"),
    ("App Runner / Fargate","รันแอป จ่ายตามใช้จริง"),
    ("Amazon ECR","เก็บ Docker image"),
    ("RDS PostgreSQL","ฐานข้อมูล"),
    ("Amazon SES","ส่งอีเมลเชิญซัพพลายเออร์"),
    ("Secrets Manager","เก็บความลับ/คีย์"),
    ("CloudWatch","ติดตามระบบ"),
]
for i,(n,d) in enumerate(svcs):
    col = i % 2; row = i // 2
    x = Inches(0.8 + col*6.0); y = Inches(1.7 + row*1.05)
    box(s, x, y, Inches(5.7), Inches(0.9), fill=LIGHT)
    text(s, x+Inches(0.2), y, Inches(5.4), Inches(0.9), [[(n+"  ", 13, BLUE, True),(d, 11, SLATE)]], anchor=MSO_ANCHOR.MIDDLE)
text(s, Inches(0.8), Inches(6.3), Inches(11.5), Inches(0.5), [[("Serverless ทั้งหมด — build เป็น Docker → ECR → App Runner พร้อม RDS + Secrets Manager ระดับ production", 12, NAVY, True)]], align=PP_ALIGN.CENTER)
footer(s, 11)
notes(s, "ระบบรันบน AWS แบบ serverless ทั้งหมด ใช้ Bedrock สำหรับ AI, Fargate รันแอปแบบจ่ายตามใช้จริง, RDS เก็บข้อมูล, SES ส่งคำเชิญ เป็นสถาปัตยกรรมระดับ production ที่พร้อมใช้งานจริง")

# 12 — Responsible AI
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "04 Responsible AI")
header(s, "AI ที่รับผิดชอบและปลอดภัย")
pillars = [
    ("คนตัดสินใจสุดท้าย","AI แค่เสนอ — ผู้บริหารต้องเซ็นอนุมัติเองก่อนออกใบสั่งซื้อ (Human-in-the-Loop)", GREEN),
    ("กันการหลอก AI","ป้องกันการพิมพ์หลอก เช่น 'หัวหน้าคุณสั่งมาแล้ว' + ล็อกเพดานราคาที่ห้ามเกิน (ทดสอบ 8/8 ผ่าน)", RED),
    ("ลิงก์เฉพาะตัว","ซัพพลายเออร์แต่ละเจ้าเข้าได้แค่ห้องตัวเอง สวมรอยข้ามเจ้าไม่ได้", BLUE),
    ("บันทึกตรวจสอบได้","ทุกการตัดสินใจถูกบันทึก: ใช้โมเดลไหน เวลาเท่าไหร่ คะแนนเท่าไหร่ ย้อนดูได้ 100%", NAVY),
]
for i,(t,d,col) in enumerate(pillars):
    col_i = i % 2; row = i // 2
    x = Inches(0.8 + col_i*6.0); y = Inches(1.8 + row*1.75)
    box(s, x, y, Inches(5.7), Inches(1.55), fill=LIGHT, line=col)
    text(s, x+Inches(0.2), y+Inches(0.15), Inches(5.3), Inches(0.5), [[(t, 15, col, True)]])
    text(s, x+Inches(0.2), y+Inches(0.65), Inches(5.3), Inches(0.85), [[(d, 12, SLATE)]], spacing=1.1)
footer(s, 12)
notes(s, "เรื่องความรับผิดชอบคือหัวใจ AI แค่เสนอ แต่คนเป็นคนเซ็นอนุมัติ มีระบบกันการหลอก AI ลิงก์เฉพาะตัวกันการสวมรอย และบันทึกทุกการตัดสินใจให้ตรวจสอบย้อนหลังได้ครบ")

# 13 — Creativity & UX
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "05 UX")
header(s, "ความคิดสร้างสรรค์ & ประสบการณ์ใช้งาน")
bullets(s, Inches(0.8), Inches(1.7), Inches(7.0), [
    "เห็นการเจรจาสด (Real-time): ผู้บริหารเห็นแชตเด้งขึ้นจอทันที ไม่ต้องรีเฟรช",
    "กระดานเทียบเจ้า (Award Board): จัดอันดับซัพพลายเออร์อัตโนมัติว่าเจ้าไหนคุ้มสุด",
    "เฝ้าระวังการดองเรื่อง (SLA Monitor): เตือนถ้าเจ้าไหนเงียบนานเกินกำหนด",
], size=15)
box(s, Inches(0.8), Inches(4.3), Inches(7.0), Inches(1.4), fill=RGBColor(0xEF,0xF6,0xFF), line=BLUE)
text(s, Inches(1.0), Inches(4.45), Inches(6.6), Inches(1.1), [
    [("จุดต่างสำคัญ:", 14, BLUE, True)],
    [("AI พูดภาษาจัดซื้อไทยได้เนียนระดับมืออาชีพ — เครื่องมือต่างชาติทำไม่ได้", 13, NAVY)],
], spacing=1.15)
box(s, Inches(8.1), Inches(1.7), Inches(4.45), Inches(4.0), line=RGBColor(0xCB,0xD5,0xE1))
text(s, Inches(8.1), Inches(1.7), Inches(4.45), Inches(4.0), [[("[📷 Award Board +", 12, SLATE, False, True)],[("SLA Monitor]", 12, SLATE, False, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 13)
notes(s, "จุดเด่นด้านการใช้งานคือทุกอย่างเกิดสด ผู้บริหารเห็นการเจรจาแบบ real-time มีกระดานจัดอันดับซัพพลายเออร์อัตโนมัติ และที่สำคัญ AI พูดภาษาจัดซื้อไทยได้เนียนมาก ซึ่งเป็นสิ่งที่เครื่องมือต่างชาติทำไม่ได้")

# 14 — Before / After
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "06 Business")
header(s, "เทียบก่อน-หลัง ใช้ AutoProcure.AI")
rows = [
    ["เรื่อง","❌ แบบเดิม","✅ ใช้ AutoProcure.AI","ผลที่ได้"],
    ["การซื้อ","แยกใบ ซื้อด่วนหน้าร้าน","รวมเป็นกลุ่มใหญ่","มีอำนาจต่อรอง"],
    ["การต่อรอง","เฉพาะ 5 ดีลใหญ่","AI ต่อรองทุกดีล 24 ชม.","ครอบคลุม 100%"],
    ["ราคา","ตามที่ร้านตั้ง","อ้างราคากลางตลาด","ถูกลง 14.5%"],
    ["เวลา/ดีล","วัน-สัปดาห์","นาที","เร็วขึ้นมาก"],
    ["ตรวจสอบ","แทบทำไม่ได้","บันทึกทุกขั้น","โปร่งใสเต็มที่"],
    ["ออกใบสั่งซื้อ","คีย์มือเข้า SAP","อัตโนมัติ","ลดความผิดพลาด"],
]
simple_table(s, Inches(0.8), Inches(1.6), Inches(11.75), rows, [2.3,3.5,3.5,2.45],
             highlight_rows={3: RGBColor(0xD1,0xFA,0xE5)}, row_h=0.62, fs=12)
footer(s, 14)
notes(s, "เทียบให้เห็นชัด ๆ จากเดิมซื้อแยกใบจ่ายแพง เป็นรวมยอดให้ AI ต่อรองทุกดีล ราคาถูกลง 14.5% เร็วขึ้นจากสัปดาห์เหลือนาที และตรวจสอบได้ทุกขั้นตอน")

# 15 — ROI
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "06 Business")
header(s, "ความคุ้มค่า: ลงทุนนิดเดียว ประหยัดมหาศาล")
stat_card(s, Inches(0.8), Inches(1.9), Inches(3.7), "฿25.0M", "ประหยัดได้/ปี (−14.5%)", GREEN)
stat_card(s, Inches(4.8), Inches(1.9), Inches(3.7), "< 0.01%", "ต้นทุน AWS เทียบเงินที่ประหยัด", BLUE)
stat_card(s, Inches(8.8), Inches(1.9), Inches(3.7), "เดือนแรก", "คืนทุนทันที", NAVY)
box(s, Inches(0.8), Inches(3.5), Inches(11.75), Inches(2.3), fill=LIGHT)
text(s, Inches(1.1), Inches(3.75), Inches(11.2), Inches(2.0), [
    [("ต้นทุน AWS: ", 15, NAVY, True),("หลักสิบดอลลาร์/เดือน (~หลักพันบาท/ปี)", 15, SLATE)],
    [("เทียบมาตรฐานอุตสาหกรรม: ", 15, NAVY, True),("การลดต้นทุนจัดซื้ออะไหล่จิปาถะทั่วไป 5–15%", 15, SLATE)],
    [("เราทำได้ 14.5% — อยู่ปลายสูงของช่วง", 16, GREEN, True)],
    [("[📷 กราฟเทียบ ต้นทุน vs เงินประหยัด — slide15_cost_value]", 12, SLATE, False, True)],
], spacing=1.3)
footer(s, 15)
notes(s, "ความคุ้มค่าชัดมาก เราลงทุนค่า AWS แค่หลักพันบาทต่อปี แต่ช่วยลูกค้าประหยัดได้ 25 ล้านบาทต่อปี คิดเป็นไม่ถึง 0.01% ของเงินที่ประหยัด และตัวเลข 14.5% อยู่ปลายสูงของมาตรฐานอุตสาหกรรมที่ 5-15%")

# 16 — Roadmap
s = prs.slides.add_slide(BLANK); bg(s, WHITE); tag(s, "Roadmap")
header(s, "แผนต่อยอด (Roadmap)")
phases = [
    ("ตอนนี้ (POC)","ทำงานจริงบน AWS — 5 โรงงาน, 5 AI Agent, เชื่อม SAP จำลอง", GREEN),
    ("ถัดไป","เชื่อม SAP ของจริง (PyRFC/BTP), ส่งอีเมลจริง, รองรับผู้ใช้หลายคนพร้อมกัน", BLUE),
    ("ระยะยาว","ขยายสินค้าทุกหมวด, ดึงราคาตลาดสด, เปิดเป็นบริการ SaaS หลายบริษัท", NAVY),
]
for i,(t,d,col) in enumerate(phases):
    x = Inches(0.8 + i*4.05)
    box(s, x, Inches(2.2), Inches(3.8), Inches(2.8), fill=LIGHT, line=col)
    box(s, x, Inches(2.2), Inches(3.8), Inches(0.65), fill=col)
    text(s, x, Inches(2.23), Inches(3.8), Inches(0.6), [[(t, 15, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x+Inches(0.25), Inches(3.05), Inches(3.3), Inches(1.8), [[(d, 13, SLATE)]], spacing=1.2)
footer(s, 16)
notes(s, "ตอนนี้เราเป็น POC ที่ทำงานได้จริง ก้าวต่อไปคือเชื่อม SAP ของจริงและขยายเป็นบริการให้หลายโรงงาน สถาปัตยกรรมเรารองรับการขยายอยู่แล้ว")

# 17 — Closing
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
text(s, Inches(1.0), Inches(1.6), Inches(11.3), Inches(1.4),
     [[("AutoProcure.AI", 46, WHITE, True)]], align=PP_ALIGN.CENTER)
text(s, Inches(1.0), Inches(2.9), Inches(11.3), Inches(0.8),
     [[("AI ที่เจรจาต่อรองแทนคุณ — ประหยัดจริง ปลอดภัย ตรวจสอบได้", 18, RGBColor(0x93,0xC5,0xFD))]], align=PP_ALIGN.CENTER)
for i,(b,sm) in enumerate([("฿25M","ประหยัด/ปี"),("−14.5%","ลดต้นทุน"),("61 ดีล","อัตโนมัติ")]):
    x = Inches(1.9 + i*3.2)
    text(s, x, Inches(4.2), Inches(3.0), Inches(0.8), [[(b, 36, GREEN if i==0 else WHITE, True)]], align=PP_ALIGN.CENTER)
    text(s, x, Inches(5.0), Inches(3.0), Inches(0.4), [[(sm, 13, RGBColor(0xCB,0xD5,0xE1))]], align=PP_ALIGN.CENTER)
text(s, Inches(1.0), Inches(6.3), Inches(11.3), Inches(0.6),
     [[("ขอบคุณครับ   ·   github.com/teeranon124/NTTdata", 14, RGBColor(0x94,0xA3,0xB8))]], align=PP_ALIGN.CENTER)
notes(s, "สรุปครับ AutoProcure.AI เปลี่ยนเงินที่รั่วไหลจากการซื้ออะไหล่จิปาถะ ให้กลายเป็นเงินที่ประหยัดได้จริง 25 ล้านบาทต่อปี ด้วย AI ที่รับผิดชอบและตรวจสอบได้ ขอบคุณครับ")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AutoProcure_AI_Pitch.pptx")
prs.save(out)
print("SAVED:", out, "| slides:", len(prs.slides._sldIdLst))
