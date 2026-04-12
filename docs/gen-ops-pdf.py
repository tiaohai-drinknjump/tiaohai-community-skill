#!/usr/bin/env python3
"""Generate ops-guide.pdf from ops-guide.md with Chinese serif font."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# --- Font Registration ---
SONGTI_PATH = "/System/Library/Fonts/Supplemental/Songti.ttc"
pdfmetrics.registerFont(TTFont("Songti", SONGTI_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont("Songti-Bold", SONGTI_PATH, subfontIndex=1))

# --- Colors ---
DARK = HexColor("#1a1a1a")
GRAY = HexColor("#666666")
LIGHT_BG = HexColor("#f5f5f0")
ACCENT = HexColor("#c17d3a")
TABLE_HEADER_BG = HexColor("#2c2c2c")
TABLE_ALT_BG = HexColor("#f9f9f6")
BORDER_COLOR = HexColor("#d0d0d0")

# --- Base Styles ---
BASE_FONT = "Songti"
BOLD_FONT = "Songti-Bold"
BASE_SIZE = 11  # ~1.1em
LINE_HEIGHT = BASE_SIZE * 1.8

styles = getSampleStyleSheet()

sTitle = ParagraphStyle(
    "CTitle", fontName=BOLD_FONT, fontSize=22, leading=22*1.6,
    textColor=DARK, spaceAfter=6*mm, alignment=TA_CENTER
)
sSubtitle = ParagraphStyle(
    "CSubtitle", fontName=BASE_FONT, fontSize=10, leading=10*1.6,
    textColor=GRAY, spaceAfter=10*mm, alignment=TA_CENTER
)
sH1 = ParagraphStyle(
    "CH1", fontName=BOLD_FONT, fontSize=16, leading=16*1.8,
    textColor=DARK, spaceBefore=10*mm, spaceAfter=4*mm
)
sH2 = ParagraphStyle(
    "CH2", fontName=BOLD_FONT, fontSize=13, leading=13*1.8,
    textColor=DARK, spaceBefore=7*mm, spaceAfter=3*mm
)
sH3 = ParagraphStyle(
    "CH3", fontName=BOLD_FONT, fontSize=BASE_SIZE, leading=LINE_HEIGHT,
    textColor=DARK, spaceBefore=5*mm, spaceAfter=2*mm
)
sBody = ParagraphStyle(
    "CBody", fontName=BASE_FONT, fontSize=BASE_SIZE, leading=LINE_HEIGHT,
    textColor=DARK, spaceAfter=3*mm
)
sBullet = ParagraphStyle(
    "CBullet", fontName=BASE_FONT, fontSize=BASE_SIZE, leading=LINE_HEIGHT,
    textColor=DARK, leftIndent=8*mm, bulletIndent=3*mm, spaceAfter=1.5*mm
)
sCode = ParagraphStyle(
    "CCode", fontName="Courier", fontSize=9, leading=9*1.6,
    textColor=DARK, backColor=LIGHT_BG, leftIndent=5*mm, rightIndent=5*mm,
    spaceBefore=2*mm, spaceAfter=3*mm, borderPadding=(3*mm, 3*mm, 3*mm, 3*mm)
)
sNote = ParagraphStyle(
    "CNote", fontName=BASE_FONT, fontSize=10, leading=10*1.8,
    textColor=GRAY, leftIndent=5*mm, borderColor=ACCENT,
    borderWidth=0, borderPadding=(2*mm, 0, 2*mm, 3*mm),
    spaceBefore=3*mm, spaceAfter=4*mm
)

def bold(text):
    return f'<font name="{BOLD_FONT}">{text}</font>'

def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    if col_widths is None:
        col_widths = [None] * len(headers)

    header_cells = [Paragraph(bold(h), ParagraphStyle("TH", fontName=BOLD_FONT, fontSize=9, leading=9*1.6, textColor=white)) for h in headers]
    body_cells = []
    for row in rows:
        body_cells.append([Paragraph(str(c), ParagraphStyle("TD", fontName=BASE_FONT, fontSize=9.5, leading=9.5*1.7, textColor=DARK)) for c in row])

    table_data = [header_cells] + body_cells
    t = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4*mm),
        ("TOPPADDING", (0, 0), (-1, 0), 3*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
        ("TOPPADDING", (0, 1), (-1, -1), 2.5*mm),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 2.5*mm),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))

    t.setStyle(TableStyle(style_cmds))
    return t

def build_pdf():
    out_path = os.path.join(os.path.dirname(__file__), "ops-guide.pdf")
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    story = []
    W = A4[0] - 40*mm  # usable width

    # === Title ===
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph("跳海社区 Skill", sTitle))
    story.append(Paragraph("运营配合指南", ParagraphStyle(
        "Title2", fontName=BOLD_FONT, fontSize=18, leading=18*1.6,
        textColor=ACCENT, spaceAfter=6*mm, alignment=TA_CENTER
    )))
    story.append(HRFlowable(width="40%", thickness=1, color=ACCENT, spaceAfter=4*mm))
    story.append(Paragraph(
        "本文档面向跳海运营负责人，说明三个需要配合的功能模块。<br/>"
        "本项目由跳海社区成员发起，不是官方项目，但希望得到官方支持。",
        sNote
    ))
    story.append(Spacer(1, 8*mm))

    # === Section 1: 漂流瓶 ===
    story.append(Paragraph("一、漂流瓶功能", sH1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4*mm))

    story.append(Paragraph("这是什么", sH2))
    story.append(Paragraph(
        "一个每日许愿池。用户通过 AI 助手投递匿名或署名留言（如「今晚十点在后海店，"
        "穿格子衬衫坐吧台最左边，想找人聊摇滚乐」），每天晚上 8 点统一揭晓当天所有留言。"
        "看到的人如果感兴趣，可以去对应的店找人。", sBody
    ))
    story.append(Paragraph(f"本质上是{bold('数字版的愿望箱')}——跳海已经在做的事情的线上延伸。", sBody))

    story.append(Paragraph("跳海需要配合什么", sH2))
    story.append(Paragraph(
        f"漂流瓶的数据统一存在跳海飞书的多维表格里，和酒单、活动数据放在一起管理。"
        f"{bold('不需要打酒师做任何额外操作')}，但需要运营在飞书里建一个表。", sBody
    ))
    story.append(make_table(
        ["事项", "说明"],
        [
            ["改变门店运营流程？", "不需要"],
            ["打酒师需要做什么？", "不需要"],
            ["需要在飞书建一个多维表格？", "需要（一次性，5 分钟）"],
            ["需要日常维护？", "不需要（数据由用户通过 AI 写入，自动过期清除）"],
            ["需要审核内容？", "不需要（AI 自动审核，规则已内置）"],
        ],
        col_widths=[W*0.38, W*0.62]
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("飞书多维表格：漂流瓶", sH3))
    story.append(make_table(
        ["字段", "类型", "说明"],
        [
            ["ID", "文本", "自动生成，格式 bottle-YYYYMMDD-001"],
            ["日期", "日期", "自动填充今天"],
            ["城市", "单选", "北京/上海/深圳/..."],
            ["门店", "单选", "后海店/安定门店/...（可不选）"],
            ["身份", "单选", "匿名/留昵称"],
            ["昵称", "文本", "可选"],
            ["留言内容", "长文本", "不超过 200 字"],
            ["想见面的时间", "文本", "如「今晚十点」"],
            ["状态", "单选", "sealed / revealed / expired"],
            ["投递时间", "日期时间", "自动记录"],
        ],
        col_widths=[W*0.2, W*0.15, W*0.65]
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "云函数会在每天 20:00 自动把当天所有 sealed 改为 revealed，"
        "次日自动改为 expired。运营无需手动操作。", sBody
    ))

    story.append(Paragraph("安全设计", sH2))
    for item in [
        "不允许留电话、微信号、社交账号——线下见面靠描述（穿什么、坐哪）",
        "不允许商业推广、色情或骚扰内容",
        "每人每天最多 3 个瓶子",
        "瓶子有效期当天，次日自动清除",
    ]:
        story.append(Paragraph(f"&bull; {item}", sBullet))

    # === Section 2: 实时酒单和活动 ===
    story.append(PageBreak())
    story.append(Paragraph("二、实时酒单和活动数据", sH1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4*mm))

    story.append(Paragraph("这是什么", sH2))
    story.append(Paragraph(
        "让用户问 AI「今天后海店有什么酒？」时能得到真实答案，而不是「建议到店确认」。", sBody
    ))

    story.append(Paragraph("跳海需要配合什么", sH2))
    story.append(Paragraph(
        f"这个{bold('需要配合')}，但设计目标是{bold('让打酒师/店长每天只多花 2 分钟')}。"
        "跳海已经全员使用飞书，所有人都会操作多维表格。", sBody
    ))

    story.append(Paragraph("表 1：每日酒单", sH3))
    story.append(make_table(
        ["字段", "类型", "说明"],
        [
            ["日期", "日期", "自动填充今天"],
            ["城市", "单选", "下拉选"],
            ["门店", "单选", "下拉选"],
            ["酒名", "文本", "如「夕阳小茉莉」"],
            ["厂牌", "文本", "如「气泡实验室」"],
            ["风格", "单选", "IPA/世涛/小麦/酸啤/古斯/其他"],
            ["价格", "数字", "单杯价格"],
            ["备注", "文本", "可选，如「今天新上的」"],
            ["填写人", "人员", "自动关联飞书账号"],
        ],
        col_widths=[W*0.15, W*0.13, W*0.72]
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("表 2：活动日历", sH3))
    story.append(make_table(
        ["字段", "类型", "说明"],
        [
            ["日期", "日期", "活动日期"],
            ["城市", "单选", ""],
            ["门店", "单选", ""],
            ["活动名称", "文本", "如「周五即兴演出之夜」"],
            ["活动类型", "单选", "音乐/市集/展览/读书/播客/运动/其他"],
            ["时间", "文本", "如「20:00」"],
            ["描述", "长文本", "一两句话说明"],
            ["填写人", "人员", ""],
        ],
        col_widths=[W*0.15, W*0.13, W*0.72]
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("谁来填", sH3))
    story.append(make_table(
        ["角色", "填什么", "频率", "耗时"],
        [
            ["当班打酒师/店长", "今日酒单", "每天开店前", "约 2 分钟"],
            ["城市市场负责人/掌群人", "本周活动", "每周一次", "约 5 分钟"],
        ],
        col_widths=[W*0.28, W*0.22, W*0.22, W*0.28]
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("怎么让填写无感", sH3))
    for item in [
        "飞书多维表格可以设为手机端快捷入口——打酒师到店后打开飞书，点「今日酒单」，填几个酒名就完了",
        "可以设置模板——大部分酒头每天变化不大，复制昨天的改一两个就行",
        "后续优化：拍照识别——拍一张酒头照片，AI 自动识别填表",
    ]:
        story.append(Paragraph(f"&bull; {item}", sBullet))

    # === Section 3: 具体步骤 ===
    story.append(PageBreak())
    story.append(Paragraph("三、跳海运营需要做的具体步骤", sH1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4*mm))

    steps = [
        ("步骤 1：创建飞书多维表格（10 分钟）", [
            "在跳海飞书工作区创建三个多维表格：① 每日酒单 ② 活动日历 ③ 漂流瓶",
            "按上文字段设置列",
            "把门店列表设为单选选项（三个表共用同一套城市和门店选项）",
        ]),
        ("步骤 2：设置权限（2 分钟）", [
            "酒单表：各城市打酒师/店长有编辑权限",
            "活动表：市场负责人有编辑权限",
            "漂流瓶表：不需要任何人手动编辑（由云函数通过 API 读写）",
        ]),
        ("步骤 3：创建飞书开放平台应用（10 分钟）", [
            "登录 open.feishu.cn",
            "创建企业自建应用",
            "开通「多维表格」API 权限（读写）",
            "获取 App ID 和 App Secret",
            "把三个表格的 URL 中的 app_token 和 table_id 记下来",
        ]),
        ("步骤 4：把以下信息给到我们", [
            "App ID",
            "App Secret",
            "酒单表的 app_token 和 table_id",
            "活动表的 app_token 和 table_id",
            "漂流瓶表的 app_token 和 table_id",
        ]),
        ("步骤 5：通知打酒师（5 分钟）", [
            "在打酒师群发一条通知：「从今天开始，到店后顺手在飞书里填一下今天的酒头，2 分钟搞定，这样问 AI 助手的人就能知道今天有什么酒了。」",
            "漂流瓶不需要通知任何人——用户自己通过 AI 投递",
        ]),
    ]
    for title, items in steps:
        story.append(Paragraph(bold(title), sH3))
        for item in items:
            story.append(Paragraph(f"&bull; {item}", sBullet))
        story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        f"{bold('不配合也完全不影响使用')}：如果跳海暂时不想接入实时数据，"
        "Skill 照常工作——用户问酒单时会返回通用合作厂牌信息，"
        "并提示「以门店实际酒头为准」。技术上已做好降级处理。", sNote
    ))

    # === Section 4: 打酒师排班 ===
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("四、打酒师排班数据（Phase 3，暂不需要）", sH1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4*mm))
    story.append(Paragraph(
        "这个需要读取跳海飞书的打酒师排班数据（已在飞书里管理的抢单系统）。"
        "只需要给我们一个只读 API 权限即可。目前不急，等前面的功能跑通后再考虑。", sBody
    ))

    # === Section 5: 总结 ===
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("五、总结", sH1))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4*mm))

    story.append(make_table(
        ["功能", "跳海配合度", "优先级"],
        [
            ["漂流瓶", "建一个飞书表（一次性），之后无需日常操作", "最先上线"],
            ["实时酒单", "建飞书表 + 打酒师每天填 2 分钟", "和漂流瓶一起推"],
            ["实时活动", "建飞书表 + 市场负责人每周填 5 分钟", "同上"],
            ["打酒师排班", "开放飞书已有排班系统的 API 只读权限", "后续再做"],
        ],
        col_widths=[W*0.18, W*0.52, W*0.30]
    ))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        f"最小启动方案：{bold('一次性创建三个飞书表 + 一个飞书应用，把凭证给到我们。')}"
        "漂流瓶立即可用，酒单看打酒师配合节奏逐步填充。", sBody
    ))

    doc.build(story)
    print(f"PDF generated: {out_path}")

if __name__ == "__main__":
    build_pdf()
