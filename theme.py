"""
Look and feel for the Streamlit app: colours (light / dark), fonts, page sections and small HTML helpers.
Everything visual lives here so app.py stays about the screening logic.
"""
import textwrap

LIGHT = dict(
    bg="#F3F6F9", surface="#FFFFFF", surface2="#EAF0F5", border="#DCE4EB", text="#0E2A3B", muted="#5A7184",
    primary="#0B3C5D", primary_text="#FFFFFF", accent="#3E7CB1", accent_soft="#DCEAF5",
    hero1="#6F96B3", hero2="#4C7896", hero_text="#FFFFFF", hero_muted="#E3EDF5",
    ok="#1B7A57", ok_soft="#E2F3EC", bad="#B42318", bad_soft="#FDECEA", warn_soft="#FFF6E0", warn="#8A5A00",
    shadow="0 10px 30px rgba(14, 42, 59, .08)",
)
DARK = dict(
    bg="#0A141D", surface="#102030", surface2="#15293B", border="#22394C", text="#E4EDF4", muted="#98AFC1",
    primary="#7DB3E0", primary_text="#06131D", accent="#7DB3E0", accent_soft="#173550",
    hero1="#163A55", hero2="#0E2536", hero_text="#F1F6FA", hero_muted="#B5CADB",
    ok="#4CC79A", ok_soft="#10362A", bad="#FF8A7A", bad_soft="#3A1A18", warn_soft="#3A2E12", warn="#F2C66D",
    shadow="0 10px 30px rgba(0, 0, 0, .35)",
)


def H(s):
    """Clean HTML for st.markdown: no indentation (would become a code block) and no blank lines."""
    return "\n".join(l.strip() for l in textwrap.dedent(s).splitlines() if l.strip())


def css(c):
    return H(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {{ --bg:{c['bg']}; --surface:{c['surface']}; --surface2:{c['surface2']}; --border:{c['border']};
  --text:{c['text']}; --muted:{c['muted']}; --primary:{c['primary']}; --primary-text:{c['primary_text']};
  --accent:{c['accent']}; --accent-soft:{c['accent_soft']}; --ok:{c['ok']}; --ok-soft:{c['ok_soft']};
  --bad:{c['bad']}; --bad-soft:{c['bad_soft']}; --warn:{c['warn']}; --warn-soft:{c['warn_soft']}; --shadow:{c['shadow']}; }}
html {{ scroll-behavior: smooth; }}
html, body, .stApp, [class*="st-"], button, input, textarea, select {{ font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif !important; }}
.stApp {{ background: var(--bg) !important; color: var(--text); }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; }}
.block-container {{ max-width: 1180px !important; padding: 1.1rem 1.5rem 3rem !important; }}
/* text */
.stApp p, .stApp li, .stApp label, .stApp span, .stMarkdown, [data-testid="stWidgetLabel"] p {{ color: var(--text); }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stApp small {{ color: var(--muted) !important; }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: var(--text) !important; letter-spacing: -.02em; }}
a {{ color: var(--accent); }}
/* widgets */
[data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-testid="stNumberInputContainer"],
[data-baseweb="base-input"], .stNumberInput input, .stTextInput input {{ background: var(--surface) !important; color: var(--text) !important; border-color: var(--border) !important; border-radius: 10px !important; }}
[data-baseweb="select"] svg, [data-testid="stNumberInputContainer"] svg {{ fill: var(--muted) !important; color: var(--muted) !important; }}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{ background: var(--surface2) !important; color: var(--text) !important; }}
[data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] {{ background: var(--surface) !important; color: var(--text) !important; }}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {{ background: var(--surface2) !important; }}
[data-testid="stFileUploaderDropzone"] {{ background: var(--surface2) !important; border: 2px dashed var(--border) !important; border-radius: 16px !important; padding: 1.4rem !important; }}
[data-testid="stFileUploaderDropzone"] * {{ color: var(--muted) !important; }}
[data-testid="stFileUploaderDropzone"] button {{ background: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }}
[data-testid="stFileUploaderFile"] *, [data-testid="stFileUploaderFileName"] {{ color: var(--text) !important; }}
[data-testid="stFileUploaderFile"], [data-testid="stFileChip"], [data-testid="stFileUploaderFile"] > div {{ background: var(--surface) !important; border-color: var(--border) !important; }}
.stButton > button, .stDownloadButton > button {{ border-radius: 999px !important; padding: .55rem 1.4rem !important; font-weight: 600 !important; border: 1px solid var(--border) !important; background: var(--surface) !important; color: var(--text) !important; }}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {{ background: var(--primary) !important; color: var(--primary-text) !important; border: none !important; box-shadow: var(--shadow); }}
.stButton > button[kind="primary"] * {{ color: var(--primary-text) !important; }}
.stButton > button:hover {{ filter: brightness(1.08); }}
[data-testid="stExpander"] details {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 14px !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: var(--text) !important; }}
[data-testid="stCheckbox"] label span, [data-baseweb="checkbox"] div {{ border-color: var(--border); }}
[data-testid="stImageCaption"], [data-testid="caption"] {{ color: var(--muted) !important; }}
[data-testid="stSpinner"] * {{ color: var(--muted) !important; }}
[data-testid="stTooltipIcon"] svg {{ color: var(--muted) !important; stroke: var(--muted) !important; }}
hr {{ border-color: var(--border) !important; }}
/* keep Streamlit's icon font (otherwise icons show as words like "upload") */
[data-testid="stIconMaterial"], .material-symbols-rounded {{ font-family: 'Material Symbols Rounded' !important; }}
/* select boxes (react-aria ComboBox in Streamlit >= 1.6x) and their dropdown list */
.stSelectbox .react-aria-ComboBox > div {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }}
.stSelectbox input, .stSelectbox button, .stSelectbox svg {{ color: var(--text) !important; }}
.react-aria-Popover, .react-aria-ListBox, [role="listbox"] {{ background: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }}
.react-aria-ListBoxItem, [role="option"] {{ color: var(--text) !important; background: transparent !important; }}
.react-aria-ListBoxItem[data-focused], .react-aria-ListBoxItem[data-hovered], .react-aria-ListBoxItem[data-selected], [role="option"]:hover, [role="option"][aria-selected="true"] {{ background: var(--surface2) !important; }}
/* checkboxes */
.stCheckbox label > div:not([data-testid]) {{ border-color: var(--muted) !important; }}
.stCheckbox label:has(input:not(:checked)) > div:not([data-testid]) {{ background: var(--surface) !important; }}
.stCheckbox label:has(input:checked) > div:not([data-testid]) {{ background: var(--primary) !important; border-color: var(--primary) !important; }}
.stCheckbox label:has(input:checked) > div:not([data-testid]) > div {{ background: var(--primary-text) !important; }}
/* nav bar: even padding, everything centred, theme switch with a visible track */
.st-key-nav {{ padding: .75rem 1.1rem .75rem 1.2rem !important; }}
.st-key-nav [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
.st-key-nav .stMarkdown > div {{ height: auto !important; }}
.st-key-nav [data-testid="stColumn"] {{ display: flex; align-items: center; }}
.st-key-nav [data-testid="stColumn"]:last-child > div {{ align-items: flex-end; }}
.st-key-nav .stCheckbox label {{ align-items: center; gap: .55rem; }}
.st-key-nav .stCheckbox label > div:not([data-testid]) {{ width: 38px !important; height: 22px !important; border-radius: 999px !important;
  background: var(--border) !important; border: none !important; position: relative; flex: 0 0 38px; }}
.st-key-nav .stCheckbox label > div:not([data-testid]) > div {{ width: 16px !important; height: 16px !important; border-radius: 50% !important;
  background: #FFFFFF !important; box-shadow: 0 1px 3px rgba(0,0,0,.25); }}
.st-key-nav .stCheckbox label:has(input:not(:checked)) > div:not([data-testid]) {{ background: #B9C7D3 !important; }}
.st-key-nav .stCheckbox label:has(input:checked) > div:not([data-testid]) {{ background: var(--primary) !important; }}
.st-key-nav .stCheckbox label:has(input:checked) > div:not([data-testid]) > div {{ background: var(--primary-text) !important; }}
.st-key-nav [data-testid="stWidgetLabel"] p {{ font-weight: 600; font-size: .9rem; white-space: nowrap; }}
/* keyed containers become cards */
.st-key-nav {{ background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: .55rem 1rem .55rem 1.2rem; box-shadow: var(--shadow); }}
.st-key-nav [data-testid="stHorizontalBlock"] {{ align-items: center; }}
[class*="st-key-card"] {{ background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 1.5rem 1.6rem; box-shadow: var(--shadow); }}
[class*="st-key-imgcard"] {{ background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: .8rem; }}
[class*="st-key-imgcard"] img {{ border-radius: 12px; }}
.st-key-report {{ background: var(--surface); border: 1px solid var(--border); border-left: 5px solid var(--accent); border-radius: 18px; padding: 1.4rem 1.7rem; box-shadow: var(--shadow); }}
.st-key-report p strong {{ color: var(--primary); }}
.st-key-report ul {{ margin-top: -.3rem; }}
/* sections */
.sec {{ padding: 4.2rem 0 1.6rem; scroll-margin-top: 1rem; }}
.eyebrow {{ display:inline-block; font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color: var(--accent); margin-bottom:.5rem; }}
.sec h2 {{ font-size: 2.3rem; line-height:1.15; margin: 0 0 .8rem; font-weight: 700; }}
.lead {{ color: var(--muted) !important; font-size: 1.05rem; max-width: 720px; line-height: 1.65; }}
/* nav */
.brand {{ display:flex; align-items:center; gap:.6rem; font-weight:800; font-size:1.15rem; color: var(--text); }}
.brand .mark {{ width:34px; height:34px; border-radius:10px; background: var(--primary); display:grid; place-items:center; }}
.brand small {{ font-weight:500; color: var(--muted); font-size:.75rem; margin-left:.2rem; }}
.navlinks {{ display:flex; gap:1.6rem; justify-content:center; }}
.navlinks a {{ color: var(--text) !important; text-decoration:none; font-weight:500; font-size:.92rem; opacity:.85; }}
.navlinks a:hover {{ opacity:1; color: var(--accent) !important; }}
/* hero */
.hero {{ position:relative; overflow:hidden; margin-top: 1rem; border-radius: 28px; padding: 3.6rem 3.2rem; min-height: 520px;
  background: radial-gradient(1200px 500px at 85% -10%, rgba(255,255,255,.18), transparent 60%), linear-gradient(135deg, {c['hero1']}, {c['hero2']});
  display:grid; grid-template-columns: 1.15fr .85fr; gap: 2.5rem; align-items:center; }}
.hero * {{ color: {c['hero_text']} !important; }}
.hero .pill {{ display:inline-flex; align-items:center; gap:.5rem; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25); padding:.35rem .8rem; border-radius:999px; font-size:.8rem; font-weight:600; }}
.hero h1 {{ font-size: 3.7rem; line-height: 1.04; font-weight: 800; margin: 1.1rem 0 1rem; letter-spacing: -.035em; }}
.hero p.sub {{ color: {c['hero_muted']} !important; font-size: 1.08rem; line-height: 1.65; max-width: 560px; }}
.btnrow {{ display:flex; gap:.8rem; margin-top: 1.6rem; flex-wrap: wrap; }}
.btn {{ display:inline-block; padding:.75rem 1.4rem; border-radius:999px; font-weight:700; font-size:.95rem; text-decoration:none !important; }}
.btn.solid {{ background:#FFFFFF; color:#0B3C5D !important; }}
.btn.solid * {{ color:#0B3C5D !important; }}
.btn.ghost {{ border:1px solid rgba(255,255,255,.45); }}
.mock {{ background: rgba(255,255,255,.96); border-radius: 22px; padding: 1.3rem; box-shadow: 0 30px 60px rgba(4, 22, 35, .35); }}
.mock * {{ color:#0E2A3B !important; }}
.mock .row {{ display:flex; justify-content:space-between; align-items:center; }}
.mock .tag {{ font-size:.72rem; font-weight:700; padding:.25rem .6rem; border-radius:999px; background:#FDECEA; color:#B42318 !important; }}
.mock .mouth {{ margin: .9rem 0; height: 170px; border-radius: 50% / 45%; background: radial-gradient(circle at 62% 46%, #ffe14d 0 7%, #ff8a3d 13%, rgba(255,60,60,.55) 22%, rgba(255,60,60,0) 34%), radial-gradient(ellipse at 50% 50%, #c96d79, #a8505d 70%, #5b2a33 100%); border: 6px solid #2b1418; }}
.mock .bar {{ height:8px; border-radius:99px; background:#E6EDF3; overflow:hidden; margin:.35rem 0 .9rem; }}
.mock .bar span {{ display:block; height:100%; width:78%; background: linear-gradient(90deg,#3E7CB1,#B42318); }}
.mock .chips {{ display:flex; gap:.4rem; flex-wrap:wrap; }}
.mock .chip {{ font-size:.72rem; padding:.25rem .55rem; border-radius:8px; background:#EAF0F5; font-weight:600; }}
.mock small {{ color:#5A7184 !important; }}
.heroimg {{ background: #F4F4F4; border-radius: 24px; padding: .6rem; box-shadow: 0 30px 60px rgba(4, 22, 35, .30); }}
.heroimg img {{ width: 100%; display: block; border-radius: 18px; }}
.floatcard {{ position:absolute; left: 3.2rem; bottom: 1.6rem; display:none; }}
/* stats */
.stats {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.4rem; }}
.stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 1.2rem 1.3rem; }}
.stat b {{ display:block; font-size: 2rem; font-weight: 800; color: var(--primary); letter-spacing:-.03em; }}
.stat span {{ color: var(--muted) !important; font-size: .85rem; line-height:1.4; }}
/* feature cards */
.grid4 {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 1.1rem; margin-top: 1.8rem; }}
.grid3 {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 1.1rem; margin-top: 1.8rem; }}
.feat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 1.5rem; box-shadow: var(--shadow); }}
.feat .ic {{ width:46px; height:46px; border-radius:14px; background: var(--accent-soft); display:grid; place-items:center; margin-bottom: 1rem; }}
.feat .ic svg {{ stroke: var(--accent); }}
.feat h4 {{ margin:0 0 .45rem; font-size:1.05rem; font-weight:700; }}
.feat p {{ color: var(--muted) !important; font-size:.9rem; line-height:1.55; margin:0; }}
.feat .tech {{ display:inline-block; margin-top:.8rem; font-size:.72rem; font-weight:700; color: var(--accent) !important; background: var(--accent-soft); padding:.2rem .55rem; border-radius:8px; }}
/* steps */
.steps {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 1.1rem; margin-top: 1.8rem; counter-reset: s; }}
.step {{ position:relative; padding: 1.4rem 1.3rem; border-radius: 20px; background: var(--surface2); border: 1px solid var(--border); }}
.step .n {{ width:38px; height:38px; border-radius:50%; background: var(--primary); color: var(--primary-text) !important; display:grid; place-items:center; font-weight:800; margin-bottom:.9rem; }}
.step h4 {{ margin:0 0 .35rem; font-size:1rem; font-weight:700; }}
.step p {{ margin:0; color: var(--muted) !important; font-size:.88rem; line-height:1.55; }}
/* info */
.info {{ background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 1.5rem 1.6rem; }}
.info h4 {{ margin:0 0 .7rem; font-weight:700; display:flex; gap:.5rem; align-items:center; }}
.info ul {{ margin:0; padding-left: 1.1rem; }}
.info li {{ color: var(--muted) !important; margin:.35rem 0; font-size:.92rem; line-height:1.5; }}
.info.warn {{ background: var(--warn-soft); border-color: transparent; }}
.info.warn h4, .info.warn li {{ color: var(--warn) !important; }}
/* results */
.result {{ border-radius: 22px; padding: 1.5rem 1.7rem; display:flex; gap:1.2rem; align-items:center; height: 100%; }}
.result.bad {{ background: var(--bad-soft); }}
.result.ok {{ background: var(--ok-soft); }}
.result .dot {{ width:54px; height:54px; border-radius:16px; display:grid; place-items:center; flex: 0 0 54px; }}
.result.bad .dot {{ background: var(--bad); }}
.result.ok .dot {{ background: var(--ok); }}
.result h3 {{ margin:0; font-size:1.55rem; font-weight:800; }}
.result.bad h3 {{ color: var(--bad) !important; }}
.result.ok h3 {{ color: var(--ok) !important; }}
.result p {{ margin:.15rem 0 0; color: var(--text); font-size:.92rem; }}
.tile {{ background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 1.2rem 1.4rem; height:100%; }}
.tile .k {{ color: var(--muted) !important; font-size:.82rem; font-weight:600; }}
.tile .v {{ font-size: 2rem; font-weight: 800; color: var(--text); letter-spacing: -.03em; line-height:1.2; margin-top:.2rem; }}
.tile .s {{ color: var(--muted) !important; font-size:.82rem; }}
.meter {{ height:8px; border-radius:99px; background: var(--surface2); overflow:hidden; margin-top:.55rem; position:relative; }}
.meter span {{ display:block; height:100%; border-radius:99px; }}
.meter i {{ position:absolute; left:50%; top:-3px; width:2px; height:14px; background: var(--muted); }}
.subhead {{ font-size: 1.25rem; font-weight: 700; margin: 2rem 0 .8rem; color: var(--text); }}
.note {{ font-size:.85rem; color: var(--muted) !important; }}
.badge {{ display:inline-block; font-size:.75rem; font-weight:600; padding:.25rem .65rem; border-radius:999px; background: var(--accent-soft); color: var(--accent) !important; }}
/* footer */
.foot {{ margin-top: 4rem; padding: 2rem 2.2rem; border-radius: 24px; background: var(--surface); border: 1px solid var(--border); display:grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 2rem; }}
.foot h5 {{ margin: 0 0 .6rem; font-size: .95rem; font-weight:700; color: var(--text); }}
.foot p {{ color: var(--muted) !important; font-size: .85rem; line-height: 1.6; margin: 0; }}
@media (max-width: 900px) {{
  .hero {{ grid-template-columns: 1fr; padding: 2.2rem 1.6rem; }} .hero h1 {{ font-size: 2.5rem; }}
  .stats, .grid4, .steps {{ grid-template-columns: 1fr 1fr; }} .grid3, .foot {{ grid-template-columns: 1fr; }}
  .navlinks {{ display:none; }}
}}
</style>
""")


# ----------------------------------------------------------------------------- icons (stroke icons, no images)
def icon(name, size=22, color="currentColor"):
    paths = {
        "logo": '<path d="M12 3c-3 0-5 1.6-6 3.5C5 8.6 5.6 12 7 14.5c.8 1.4 1.1 3 1.4 4.6.2 1 .8 1.9 1.6 1.9.9 0 1.2-1 1.4-2.2l.6-3.3.6 3.3c.2 1.2.5 2.2 1.4 2.2.8 0 1.4-.9 1.6-1.9.3-1.6.6-3.2 1.4-4.6C18.4 12 19 8.6 18 6.5 17 4.6 15 3 12 3z"/><path d="M12 7v5M9.5 9.5h5"/>',
        "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><ellipse cx="12" cy="12" rx="5.5" ry="4"/>',
        "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3h1V4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3h-1V4z"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
        "doc": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
        "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
        "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "check": '<path d="M5 12l5 5L20 7"/>',
        "cross": '<path d="M12 5v14M5 12h14"/>',
        "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c1-3.5 3.5-5 6.5-5s5.5 1.5 6.5 5"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.5c2.5 0 4.5 1.3 5.5 4"/>',
    }
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{paths[name]}</svg>')


BRAND = "OralScreen AI"


def nav_html():
    return H(f"""
<div style="display:flex;align-items:center;justify-content:space-between;gap:1rem">
<div class="brand"><div class="mark">{icon('logo', 20, '#FFFFFF')}</div>{BRAND}<small>research prototype</small></div>
<div class="navlinks"><a href="#overview">Overview</a><a href="#how">How it works</a><a href="#info">Important information</a><a href="#screen">Screening</a></div>
</div>
""")


def _img_uri(path):
    import base64, pathlib
    p = pathlib.Path(__file__).resolve().parent / path
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


def hero_html(online=False):
    hero_img = _img_uri("assets/hero_illustration.jpg")
    privacy_stat = ('<div class="stat"><b>0</b><span>photos saved: images are processed in memory for your session only</span></div>'
                    if online else
                    '<div class="stat"><b>100%</b><span>on this computer: photos and details never leave the device</span></div>')
    return H(f"""
<div class="hero" id="overview">
<div>
<span class="pill">{icon('shield', 16, '#FFFFFF')} AI-assisted oral cancer screening</span>
<h1>Early signs,<br>found sooner.</h1>
<p class="sub">Upload a photo of the inside of the mouth and add a few lifestyle details. The system finds the oral cavity,
checks it for signs of potentially malignant disorders (OPMD) or oral cancer, shows where it looked, and writes a
plain-language report with clear next steps.</p>
<div class="btnrow"><a class="btn solid" href="#screen">Start screening &nbsp;→</a><a class="btn ghost" href="#how">How it works</a></div>
</div>
<div class="heroimg"><img src="{hero_img}" alt="Illustration: doctors examining an open mouth with magnifying glasses"></div></div>
<div class="stats">
<div class="stat"><b>3,000</b><span>annotated photos from 714 patients used to build the models</span></div>
<div class="stat"><b>0.94</b><span>Dice overlap of the oral-cavity segmentation (validation)</span></div>
<div class="stat"><b>95%</b><span>of oral cancer images flagged as suspicious on the held-out test set</span></div>
{privacy_stat}
</div>
""")


def features_html(online=False):
    where = "runs in the browser on a free server (or fully offline on a laptop)" if online else "runs entirely on a laptop"
    f = [("scan", "Finds the mouth", "A lightweight Mobile-UNet outlines the oral cavity and removes the face, lips and background, so only the mouth is analysed.", "Mobile-UNet · adapters"),
         ("brain", "Screens the photo", "An EfficientNet-B0 network looks for visual signs of OPMD and oral cancer in the segmented mouth.", "EfficientNet-B0 · 384 px"),
         ("user", "Adds risk habits", "Age, sex, smoking, alcohol and betel-quid chewing are combined with the photo by a gradient-boosted model for the final decision.", "XGBoost stacking"),
         ("doc", "Explains and reports", "A heatmap shows where the model looked, a chart shows which habits mattered, and a plain-language report lists the next steps.", "Grad-CAM · SHAP · local LLM")]
    cards = "".join(f'<div class="feat"><div class="ic">{icon(i, 22)}</div><h4>{t}</h4><p>{d}</p><span class="tech">{k}</span></div>' for i, t, d, k in f)
    return H(f"""
<div class="sec" id="what">
<span class="eyebrow">What it does</span>
<h2>One photo. Four careful steps.</h2>
<p class="lead">Built for quick screening in clinics and community camps, the system {where} and explains every result instead of giving a bare yes or no.</p>
<div class="grid4">{cards}</div>
</div>
""")


def steps_html(online=False):
    noacc = "No account needed." if online else "No account, no upload to the cloud."
    s = [("Upload a photo", "A clear, close-up photo of the inside of the mouth, taken in good light (phone photos work)."),
         ("Add patient details", "Age, sex and habits: smoking, alcohol and betel quid. Every detail is optional; unknowns are fine."),
         ("Run the analysis", "Segmentation, screening and explanation take a few seconds on a normal laptop."),
         ("Read the report", "See the result, where the model looked, which habits mattered, and what to do next.")]
    cards = "".join(f'<div class="step"><div class="n">{k + 1}</div><h4>{t}</h4><p>{d}</p></div>' for k, (t, d) in enumerate(s))
    return H(f"""
<div class="sec" id="how">
<span class="eyebrow">How it works</span>
<h2>From photo to report in under a minute</h2>
<p class="lead">{noacc} Follow the four steps below, then scroll to the screening section to begin.</p>
<div class="steps">{cards}</div>
</div>
""")


def info_html(online=False):
    privacy_items = ("<li>This online demo runs on a Streamlit Community Cloud server: photos are sent to it for analysis.</li>"
                     "<li>Photos and details are processed in memory for your session and are not saved by the app.</li>"
                     "<li>Do not upload identifiable patient photos without consent.</li>") if online else (
                     "<li>All models, including the report writer, run on this computer.</li>"
                     "<li>Photos and patient details are not stored or sent anywhere.</li>"
                     "<li>Close the page to clear everything.</li>")
    return H(f"""
<div class="sec" id="info">
<span class="eyebrow">Important information</span>
<h2>Please read before screening</h2>
<div class="grid3">
<div class="info"><h4>{icon('people', 20)} Who it is for</h4><ul>
<li>Dentists and doctors who want a second look at a lesion.</li>
<li>Health workers running oral screening camps.</li>
<li>Patients, together with a health professional.</li></ul></div>
<div class="info warn"><h4>{icon('alert', 20)} What it is not</h4><ul>
<li>It is <b>not a diagnosis</b>. Only a clinical examination and biopsy can confirm disease.</li>
<li>It can miss problems. A "not suspicious" result does not rule out disease.</li>
<li>Any patch or sore that has not healed in 3 weeks should be seen by a dentist.</li></ul></div>
<div class="info"><h4>{icon('lock', 20)} Privacy</h4><ul>
{privacy_items}</ul></div>
</div>
</div>
""")


def section_head(id_, eyebrow, title, lead=""):
    return H(f"""
<div class="sec" id="{id_}" style="padding-bottom:1rem">
<span class="eyebrow">{eyebrow}</span>
<h2>{title}</h2>
{f'<p class="lead">{lead}</p>' if lead else ''}
</div>
""")


def result_html(pred):
    if pred:
        return H(f"""<div class="result bad"><div class="dot">{icon('alert', 26, '#FFFFFF')}</div>
<div><h3>Suspicious</h3><p>Possible OPMD or oral cancer. Please see a specialist soon.</p></div></div>""")
    return H(f"""<div class="result ok"><div class="dot">{icon('check', 26, '#FFFFFF')}</div>
<div><h3>Not suspicious</h3><p>Likely healthy or benign. This does not rule out disease.</p></div></div>""")


def tile_html(k, v, s="", meter=None, color="var(--accent)"):
    m = (f'<div class="meter"><span style="width:{meter * 100:.0f}%;background:{color}"></span><i></i></div>'
         if meter is not None else "")
    return H(f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div>{m}<div class="s">{s}</div></div>')


def footer_html():
    return H(f"""
<div class="foot">
<div><div class="brand" style="margin-bottom:.7rem"><div class="mark">{icon('logo', 20, '#FFFFFF')}</div>{BRAND}</div>
<p>An M.Tech research prototype for AI-assisted oral cancer screening. Results are a screening aid, not a diagnosis.
Please consult a dentist or oral medicine specialist.</p></div>
<div><h5>Quit tobacco</h5><p>National Tobacco Quitline (India)<br><b style="color:var(--text)">1800-11-2356</b> · free</p></div>
<div><h5>How it was built</h5><p>Mobile-UNet segmentation · EfficientNet-B0 · XGBoost fusion · Grad-CAM & SHAP · Qwen2.5 report writer</p></div>
</div>
""")
