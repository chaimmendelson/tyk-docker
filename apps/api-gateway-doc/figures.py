"""Diagram generator for the API Gateway standard.

Draws the figures used by build_docx.py with Pillow (no other dependencies).
Everything is drawn at 2x and downsampled for smooth edges.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(HERE, "figures")
OUT_DIR = BASE_DIR
LANG = "en"          # "en", or "he" (right-to-left: text is shaped RTL and the layout is mirrored)

S = 2  # supersampling factor
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (31, 56, 100)
BLUE = (47, 84, 150)
LIGHT = (217, 226, 243)
LIGHTER = (237, 242, 250)
MID = (143, 170, 220)
GRAY = (89, 89, 89)
LGRAY = (242, 242, 242)
GRAY_LINE = (166, 166, 166)
WARM = (255, 242, 204)
WARM_LINE = (191, 144, 0)
WHITE = (255, 255, 255)


def configure(lang):
    """Select the language of the figures. Hebrew figures go to figures/he/."""
    global LANG, OUT_DIR
    LANG = lang
    OUT_DIR = BASE_DIR if lang == "en" else os.path.join(BASE_DIR, lang)


class Canvas:
    """Drawing surface. With rtl=True every x coordinate is mirrored (callers keep working in
    left-to-right coordinates) and text is shaped right-to-left."""

    def __init__(self, w, h, rtl=None):
        self.w, self.h = w, h
        self.rtl = (LANG != "en") if rtl is None else rtl
        self.img = Image.new("RGB", (w * S, h * S), WHITE)
        self.d = ImageDraw.Draw(self.img)
        self._fonts = {}

    # ---- text -----------------------------------------------------------
    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(FONT_B if bold else FONT_R, size * S)
        return self._fonts[key]

    def _len(self, font, text):
        if self.rtl:
            return font.getlength(text, direction="rtl", language=LANG)
        return font.getlength(text)

    def _mx(self, x):
        return self.w - x if self.rtl else x

    def wrap(self, text, font, max_w):
        lines = []
        for para in text.split("\n"):
            cur = ""
            for word in para.split():
                trial = (cur + " " + word).strip()
                if not cur or self._len(font, trial) <= max_w * S:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            lines.append(cur)
        return lines

    def text(self, x, y, text, size=24, bold=False, color=NAVY, max_w=None,
             anchor="c", gap=1.28, bg=None):
        """Draw a text block. (x, y) is the block centre; for anchor 'l' / 'r',
        x is the left / right edge and y is still the vertical centre.
        Returns the block height."""
        f = self.font(size, bold)
        lines = self.wrap(text, f, max_w) if max_w else text.split("\n")
        lh = size * gap
        cy = y - lh * len(lines) / 2
        if self.rtl:
            x = self._mx(x)
            anchor = {"l": "r", "r": "l"}.get(anchor, anchor)
        for ln in lines:
            wpx = self._len(f, ln) / S
            if anchor == "c":
                lx = x - wpx / 2
            elif anchor == "l":
                lx = x
            else:
                lx = x - wpx
            if bg:
                self.d.rectangle([(lx - 6) * S, cy * S, (lx + wpx + 6) * S, (cy + lh) * S], fill=bg)
            if self.rtl:
                self.d.text((lx * S, (cy + lh / 2) * S), ln, font=f, fill=color, anchor="lm",
                            direction="rtl", language=LANG)
            else:
                self.d.text((lx * S, (cy + lh / 2) * S), ln, font=f, fill=color, anchor="lm")
            cy += lh
        return lh * len(lines)

    # ---- shapes ---------------------------------------------------------
    def box(self, x, y, w, h, text="", fill=LIGHT, outline=BLUE, size=24, bold=False,
            color=NAVY, radius=14, width=3, pad=14, dash=False):
        bx = self._mx(x) - w if self.rtl else x
        self.d.rounded_rectangle([bx * S, y * S, (bx + w) * S, (y + h) * S],
                                 radius=radius * S, fill=fill, outline=outline, width=width * S)
        if text:
            self.text(x + w / 2, y + h / 2, text, size, bold, color, max_w=w - 2 * pad)

    def panel(self, x, y, w, h, title, body, fill, outline, tsize=26, bsize=22, color=NAVY):
        """Box with a bold title block and a wrapped body underneath."""
        self.box(x, y, w, h, fill=fill, outline=outline)
        th = self.text(x + w / 2, y + 16 + tsize * 0.64, title, tsize, True, color, max_w=w - 30)
        if body:
            top = y + 16 + th + 6
            self.text(x + w / 2, top + (y + h - top) / 2, body, bsize, False, color, max_w=w - 50)

    def line(self, p0, p1, color=NAVY, width=3, dash=None):
        (x0, y0), (x1, y1) = p0, p1
        self._line((self._mx(x0), y0), (self._mx(x1), y1), color, width, dash)

    def _line(self, p0, p1, color, width, dash):
        (x0, y0), (x1, y1) = p0, p1
        if not dash:
            self.d.line([x0 * S, y0 * S, x1 * S, y1 * S], fill=color, width=width * S)
            return
        length = math.hypot(x1 - x0, y1 - y0)
        on, off = dash
        pos = 0.0
        while pos < length:
            end = min(pos + on, length)
            a = (x0 + (x1 - x0) * pos / length, y0 + (y1 - y0) * pos / length)
            b = (x0 + (x1 - x0) * end / length, y0 + (y1 - y0) * end / length)
            self.d.line([a[0] * S, a[1] * S, b[0] * S, b[1] * S], fill=color, width=width * S)
            pos += on + off

    def arrow(self, p0, p1, color=NAVY, width=3, head=17, dash=None):
        (x0, y0), (x1, y1) = p0, p1
        x0, x1 = self._mx(x0), self._mx(x1)
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.7 * math.cos(ang), y1 - head * 0.7 * math.sin(ang)
        self._line((x0, y0), (bx, by), color, width, dash)
        pts = [(x1, y1),
               (x1 - head * math.cos(ang - 0.42), y1 - head * math.sin(ang - 0.42)),
               (x1 - head * math.cos(ang + 0.42), y1 - head * math.sin(ang + 0.42))]
        self.d.polygon([(px * S, py * S) for px, py in pts], fill=color)

    def save(self, name):
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, name)
        self.img.resize((self.w, self.h), Image.LANCZOS).save(path, optimize=True)
        return path


# ---------------------------------------------------------------------------
# Text of the figures, per language. Keys are shared; only the wording differs.
# ---------------------------------------------------------------------------

STRINGS = {
    "en": {
        "c2b.actors": ["User", "Identity Provider", "API Gateway", "Backend"],
        "b2b.actors": ["B2B Client", "Identity Provider / Token Service", "API Gateway", "Backend"],
        "c2b.steps": ["1. Authenticate", "2. Short-lived access token", "3. API request with access token",
                      "4. Validate token and claims; enforce authorization and policies",
                      "5. Authorized request with trusted identity attributes"],
        "b2b.steps": ["1. Client authentication (client credential)", "2. Short-lived access token",
                      "3. API request with access token",
                      "4. Validate token and claims; enforce authorization and policies",
                      "5. Authorized request with trusted identity attributes"],
        "lifecycle.stages": ["Design", "Development", "Exposure", "Operation", "Change / Version",
                             "Deprecation", "Retirement"],
        "lifecycle.note": "Lifecycle owned by the Application Team; technical capabilities provided by the Gateway",
        "gitops.steps": ["1. Change defined in Git (pull request)", "2. Review", "3. Automated validation",
                         "4. Approval", "5. Automated deployment"],
        "gitops.gateway": "API Gateway\n(runtime configuration)",
        "gitops.gitcfg": "Git-managed configuration",
        "gitops.secrets": "Secrets management",
        "gitops.supplied": "secrets supplied\nat deployment",
        "gitops.note": "Git records what was requested and approved; Gateway audit records what was executed.",
        "dist.mgmt": "Management Plane\n(central management)",
        "dist.sites": [("Site A", "API Gateway A", "Application A"), ("Site B", "API Gateway B", "Application B")],
        "dist.local": "{site} (local Data Plane)",
        "dist.config": "configuration",
        "dist.note": "If the Management Plane becomes unavailable, each Gateway continues to serve traffic\n"
                     "using its last known valid configuration.",
        "op.app.title": "Application Team (owns the APIs)",
        "op.app.body": "API definition · Consumers · Authorization policy · Rate limits · Versioning · "
                       "Documentation · Lifecycle",
        "op.as_code": "API definitions and policies as code",
        "op.git.title": "Git / GitOps",
        "op.git.body": "Pull request → review → validation → approval → automated deployment",
        "op.deployed": "approved configuration deployed",
        "op.platform": "API Gateway Platform (owned by the Infrastructure Team)",
        "op.caps.title": "Gateway capabilities",
        "op.caps.body": "Authentication · Authorization · Routing · Health checks · Timeouts · Rate limiting · "
                        "Transformation · Caching · Schema validation · Logging · Audit",
        "op.dataplane": "Distributed Data Plane",
        "op.site": "{site}\nAPI Gateway",
        "op.backend": "{site} Backend services",
        "op.sites": ["Site A", "Site B"],
        "op.org.title": "Organization",
        "op.org.body": "Governance and standards",
        "op.guardrails": "standards implemented as guardrails",
        "op.mgmt.title": "Central Management",
        "op.mgmt.body": "Management Plane",
        "op.legend": ["Application team", "Infrastructure team", "Organization"],
    },
    "he": {
        "c2b.actors": ["משתמש", "ספק זהויות (IdP)", "API Gateway", "Backend"],
        "b2b.actors": ["לקוח B2B", "ספק זהויות / שירות tokens", "API Gateway", "Backend"],
        "c2b.steps": ["1. אימות זהות", "2. access token קצר מועד", "3. בקשת API עם ה-access token",
                      "4. אימות ה-token וה-claims; אכיפת הרשאות ומדיניות",
                      "5. בקשה מורשית עם מאפייני זהות מהימנים"],
        "b2b.steps": ["1. אימות הלקוח באמצעות אישור הזיהוי", "2. access token קצר מועד",
                      "3. בקשת API עם ה-access token",
                      "4. אימות ה-token וה-claims; אכיפת הרשאות ומדיניות",
                      "5. בקשה מורשית עם מאפייני זהות מהימנים"],
        "lifecycle.stages": ["תכנון", "פיתוח", "חשיפה", "תפעול", "שינוי / גרסה", "הוצאה משימוש",
                             "הפסקת שירות"],
        "lifecycle.note": "מחזור החיים בבעלות צוות האפליקציה; היכולות הטכניות ניתנות על ידי ה-Gateway",
        "gitops.steps": ["1. השינוי מוגדר ב-Git כ-pull request", "2. סקירה", "3. אימות אוטומטי",
                         "4. אישור", "5. פריסה אוטומטית"],
        "gitops.gateway": "API Gateway\nתצורת זמן ריצה",
        "gitops.gitcfg": "תצורה המנוהלת ב-Git",
        "gitops.secrets": "ניהול secrets",
        "gitops.supplied": "ה-secrets מסופקים\nבזמן הפריסה",
        "gitops.note": "Git מתעד מה התבקש ואושר; יומן ה-audit של ה-Gateway מתעד מה בוצע.",
        "dist.mgmt": "Management Plane\n(ניהול מרכזי)",
        "dist.sites": [("אתר A", "API Gateway A", "אפליקציה A"), ("אתר B", "API Gateway B", "אפליקציה B")],
        "dist.local": "{site} (Data Plane מקומי)",
        "dist.config": "תצורה",
        "dist.note": "אם ה-Management Plane אינו זמין, כל Gateway ממשיך לשרת תעבורה\n"
                     "בהתאם לתצורה התקפה האחרונה הידועה לו.",
        "op.app.title": "צוות האפליקציה (הבעלים של ה-API)",
        "op.app.body": "הגדרת API · צרכנים · מדיניות הרשאות · הגבלות קצב · ניהול גרסאות · תיעוד · "
                       "מחזור חיים",
        "op.as_code": "הגדרות API ומדיניות כקוד",
        "op.git.title": "Git / GitOps",
        "op.git.body": "Pull request ← סקירה ← אימות ← אישור ← פריסה אוטומטית",
        "op.deployed": "התצורה המאושרת נפרסת",
        "op.platform": "פלטפורמת API Gateway (בבעלות צוות התשתיות)",
        "op.caps.title": "יכולות ה-Gateway",
        "op.caps.body": "אימות זהות · הרשאה · ניתוב · בדיקות תקינות · זמני קצוב · הגבלת קצב · "
                        "המרה · מטמון · אימות סכמה · רישום יומנים · audit",
        "op.dataplane": "Data Plane מבוזר",
        "op.site": "{site}\nAPI Gateway",
        "op.backend": "שירותי Backend של {site}",
        "op.sites": ["אתר A", "אתר B"],
        "op.org.title": "הארגון",
        "op.org.body": "governance ותקנים",
        "op.guardrails": "תקנים הממומשים כ-guardrails",
        "op.mgmt.title": "ניהול מרכזי",
        "op.mgmt.body": "Management Plane",
        "op.legend": ["צוות האפליקציה", "צוות התשתיות", "הארגון"],
    },
}


def tr(key):
    return STRINGS[LANG][key]


# ---------------------------------------------------------------------------
# Sequence diagram (C2B / B2B flows)
# ---------------------------------------------------------------------------

def sequence(name, actors, steps, width=1400):
    """actors: [(label, x)]; steps: ('msg', from, to, label) | ('note', actor, text)."""
    probe = Canvas(width, 10)
    lab_size = 24
    top, head_h, head_w = 30, 112, 250

    layout, y = [], top + head_h + 40
    for st in steps:
        if st[0] == "msg":
            _, a, b, label = st
            span = abs(actors[b][1] - actors[a][1]) - 36
            lines = probe.wrap(label, probe.font(lab_size), max(span, 200))
            ph = len(lines) * lab_size * 1.28
            layout.append((st, y, ph))
            y += ph + 16 + 44
        else:
            _, a, text = st
            lines = probe.wrap(text, probe.font(lab_size), 400)
            bh = len(lines) * lab_size * 1.28 + 30
            layout.append((st, y, bh))
            y += bh + 40
    height = int(y + 10)

    c = Canvas(width, height)
    for label, ax in actors:                       # lifelines then heads
        c.line((ax, top + head_h), (ax, height - 10), GRAY_LINE, 2, dash=(12, 9))
    for label, ax in actors:
        c.box(ax - head_w / 2, top, head_w, head_h, label, fill=NAVY, outline=NAVY,
              size=25, bold=True, color=WHITE)

    for st, y0, h in layout:
        if st[0] == "msg":
            _, a, b, label = st
            xa, xb = actors[a][1], actors[b][1]
            ya = y0 + h + 16
            c.arrow((xa, ya), (xb, ya), BLUE, 3)
            c.text((xa + xb) / 2, y0 + h / 2, label, lab_size, False, NAVY,
                   max_w=max(abs(xb - xa) - 36, 200), bg=WHITE)
        else:
            _, a, text = st
            ax = actors[a][1]
            c.box(ax - 215, y0, 430, h, text, fill=LIGHTER, outline=MID, size=lab_size, pad=12)
    return c.save(name)


# ---------------------------------------------------------------------------
# Individual figures
# ---------------------------------------------------------------------------

def fig_c2b():
    a, s = tr("c2b.actors"), tr("c2b.steps")
    actors = [(a[0], 150), (a[1], 500), (a[2], 880), (a[3], 1245)]
    steps = [
        ("msg", 0, 1, s[0]),
        ("msg", 1, 0, s[1]),
        ("msg", 0, 2, s[2]),
        ("note", 2, s[3]),
        ("msg", 2, 3, s[4]),
    ]
    return sequence("fig_c2b.png", actors, steps)


def fig_b2b():
    a, s = tr("b2b.actors"), tr("b2b.steps")
    actors = [(a[0], 150), (a[1], 520), (a[2], 890), (a[3], 1250)]
    steps = [
        ("msg", 0, 1, s[0]),
        ("msg", 1, 0, s[1]),
        ("msg", 0, 2, s[2]),
        ("note", 2, s[3]),
        ("msg", 2, 3, s[4]),
    ]
    return sequence("fig_b2b.png", actors, steps)


def fig_lifecycle():
    stages = tr("lifecycle.stages")
    w, gap, x0, y0, h = 172, 30, 8, 40, 120
    c = Canvas(1400, 250)
    for i, s in enumerate(stages):
        x = x0 + i * (w + gap)
        c.box(x, y0, w, h, s, fill=LIGHT, outline=BLUE, size=21, pad=8)
        if i < len(stages) - 1:
            c.arrow((x + w + 3, y0 + h / 2), (x + w + gap - 3, y0 + h / 2), NAVY, 3, head=13)
    c.line((8, 200), (1392, 200), MID, 2)
    c.text(700, 228, tr("lifecycle.note"), 22, False, GRAY)
    return c.save("fig_lifecycle.png")


def fig_gitops():
    c = Canvas(1400, 610)
    w, gap, x0, y0, h = 224, 55, 30, 40, 150
    labels = tr("gitops.steps")
    xs = [x0 + i * (w + gap) for i in range(5)]
    for i, (x, t) in enumerate(zip(xs, labels)):
        c.box(x, y0, w, h, t, fill=LIGHT, outline=BLUE, size=24, pad=12)
        if i < 4:
            c.arrow((x + w + 3, y0 + h / 2), (x + w + gap - 3, y0 + h / 2), NAVY, 3, head=13)
    gx, gy, gw, gh = xs[4], 370, w, 130
    c.box(gx, gy, gw, gh, tr("gitops.gateway"), fill=NAVY, outline=NAVY, size=24, bold=True, color=WHITE)
    c.arrow((gx + w / 2, y0 + h + 3), (gx + w / 2, gy - 3), NAVY, 3)
    c.text(gx + w / 2 - 22, 285, tr("gitops.gitcfg"), 22, False, NAVY, max_w=210, anchor="r", bg=WHITE)
    sx, sw = 560, 360
    c.box(sx, gy, sw, gh, tr("gitops.secrets"), fill=WARM, outline=WARM_LINE, size=24, bold=True)
    c.arrow((sx + sw + 3, gy + gh / 2), (gx - 3, gy + gh / 2), NAVY, 3)
    c.text((sx + sw + gx) / 2, gy + gh / 2 - 38, tr("gitops.supplied"), 21, False, NAVY, bg=WHITE)
    c.line((30, 545), (1370, 545), MID, 2)
    c.text(700, 580, tr("gitops.note"), 22, False, GRAY)
    return c.save("fig_gitops.png")


def fig_distributed():
    c = Canvas(1400, 730)
    c.box(300, 30, 800, 110, tr("dist.mgmt"), fill=NAVY, outline=NAVY,
          size=27, bold=True, color=WHITE)
    for cx, (site, gw, app) in zip((360, 1040), tr("dist.sites")):
        c.box(cx - 300, 250, 600, 370, fill=LIGHTER, outline=MID, radius=18)
        c.box(cx - 220, 300, 440, 100, gw, fill=LIGHT, outline=BLUE, size=26, bold=True)
        c.arrow((cx, 403), (cx, 447), NAVY, 3)
        c.box(cx - 220, 450, 440, 90, app, fill=WARM, outline=WARM_LINE, size=26)
        c.text(cx, 585, tr("dist.local").format(site=site), 24, True, GRAY)
        c.arrow((cx, 142), (cx, 297), BLUE, 3, dash=(14, 9))
        c.text(cx + 14, 222, tr("dist.config"), 22, False, BLUE, anchor="l", bg=WHITE)
    c.text(700, 680, tr("dist.note"), 23, False, GRAY)
    return c.save("fig_distributed.png")


def fig_operating_model():
    c = Canvas(1400, 1110)
    LW, LX = 970, 30
    cx = LX + LW / 2

    c.panel(LX, 30, LW, 190, tr("op.app.title"), tr("op.app.body"), WARM, WARM_LINE)
    c.arrow((cx, 223), (cx, 297), NAVY, 3)
    c.text(cx + 16, 260, tr("op.as_code"), 22, False, NAVY, anchor="l")

    c.panel(LX, 300, LW, 120, tr("op.git.title"), tr("op.git.body"), LIGHT, BLUE)
    c.arrow((cx, 423), (cx, 497), NAVY, 3)
    c.text(cx + 16, 460, tr("op.deployed"), 22, False, NAVY, anchor="l")

    # platform container
    c.box(LX, 500, LW, 470, fill=LIGHTER, outline=BLUE, radius=18)
    c.text(LX + 24, 532, tr("op.platform"), 26, True, NAVY, anchor="l")
    c.panel(LX + 30, 565, LW - 60, 150, tr("op.caps.title"), tr("op.caps.body"), WHITE, MID)
    c.text(cx, 748, tr("op.dataplane"), 24, True, GRAY)
    bw = (LW - 60 - 30) / 2
    for i, site in enumerate(tr("op.sites")):
        bx = LX + 30 + i * (bw + 30)
        c.box(bx, 775, bw, 110, tr("op.site").format(site=site), fill=LIGHT, outline=BLUE, size=25, bold=True)
        c.arrow((bx + bw / 2, 888), (bx + bw / 2, 1013), NAVY, 3)
        c.box(bx, 1015, bw, 80, tr("op.backend").format(site=site), fill=WARM, outline=WARM_LINE, size=24)

    # right column
    RX, RW = 1090, 280
    c.panel(RX, 30, RW, 190, tr("op.org.title"), tr("op.org.body"), LGRAY, GRAY_LINE)
    c.arrow((RX + RW / 2, 223), (RX + RW / 2, 607), NAVY, 3)
    c.text(RX + RW / 2 - 16, 420, tr("op.guardrails"), 21, False, NAVY, max_w=190, anchor="r")
    c.panel(RX, 610, RW, 170, tr("op.mgmt.title"), tr("op.mgmt.body"), LIGHT, BLUE)
    c.arrow((RX - 3, 695), (LX + LW + 3, 695), BLUE, 3, head=15)

    # legend
    ly = 830
    for i, ((fill, line), label) in enumerate(zip(((WARM, WARM_LINE), (LIGHT, BLUE), (LGRAY, GRAY_LINE)),
                                                  tr("op.legend"))):
        yy = ly + i * 56
        c.box(RX, yy, 34, 34, fill=fill, outline=line, radius=6, width=2)
        c.text(RX + 48, yy + 17, label, 21, False, NAVY, anchor="l")
    return c.save("fig_operating_model.png")


ALL = {
    "c2b": fig_c2b,
    "b2b": fig_b2b,
    "lifecycle": fig_lifecycle,
    "gitops": fig_gitops,
    "distributed": fig_distributed,
    "operating_model": fig_operating_model,
}


def generate_all():
    return {key: fn() for key, fn in ALL.items()}


if __name__ == "__main__":
    import sys
    configure(sys.argv[1] if len(sys.argv) > 1 else "en")
    for k, p in generate_all().items():
        print(k, p)
