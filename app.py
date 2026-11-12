"""
OralScreen AI -- oral cancer screening research prototype (M.Tech project)
Run:  streamlit run app.py
"""
import hashlib
import importlib.util
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components

import pipeline as P
import summary_generator as S
import theme as T

# Online mode: set automatically when the language-model libraries are not installed (the free cloud version),
# or force it with the environment variable ORALSCREEN_ONLINE=1. Online mode hides the AI report and
# changes the privacy wording; screening, Grad-CAM, SHAP and the standard report work the same.
LLM_INSTALLED = all(importlib.util.find_spec(m) is not None for m in ("torch", "transformers"))
ONLINE = os.environ.get("ORALSCREEN_ONLINE") == "1" or not LLM_INSTALLED
LLM_ENABLED = LLM_INSTALLED and not ONLINE

st.set_page_config(page_title="OralScreen AI", page_icon="🦷", layout="wide", initial_sidebar_state="collapsed")


# ----------------------------------------------------------------------------- models (loaded once)
@st.cache_resource(show_spinner="Loading the segmentation and classification models...")
def load_models():
    return P.Segmenter(), P.Classifier()


@st.cache_resource(show_spinner="Loading the language model (the first time this downloads it, ~3 GB)...")
def load_llm(model_id):
    return S.LLMRewriter(model_id)


# ----------------------------------------------------------------------------- theme + navigation
dark = st.session_state.get("dark", False)
C = T.DARK if dark else T.LIGHT
st.markdown(T.css(C), unsafe_allow_html=True)

with st.container(key="nav"):
    n1, n2 = st.columns([6, 1.1], vertical_alignment="center")
    n1.markdown(T.nav_html(), unsafe_allow_html=True)
    n2.toggle("🌙 Dark mode", key="dark")

try:
    segmenter, classifier = load_models()
except Exception as e:
    st.error(f"Could not load the models: {e}\n\nCheck that the `models/` folder is next to app.py (see HOW_TO_RUN.md).")
    st.stop()

# ----------------------------------------------------------------------------- landing sections
st.markdown(T.hero_html(ONLINE), unsafe_allow_html=True)
st.markdown(T.features_html(ONLINE), unsafe_allow_html=True)
st.markdown(T.steps_html(ONLINE), unsafe_allow_html=True)
st.markdown(T.info_html(ONLINE), unsafe_allow_html=True)

# ----------------------------------------------------------------------------- screening form
st.markdown(T.section_head("screen", "Screening", "Start a screening",
                           "Upload one intraoral photo and fill in what you know. Unknown details can be left as "
                           "“Not known”."), unsafe_allow_html=True)

left, right = st.columns([1.15, 1], gap="large")
with left:
    with st.container(key="card_upload"):
        st.markdown('<div class="subhead" style="margin-top:0">1 · Photo of the mouth</div>', unsafe_allow_html=True)
        up = st.file_uploader("Upload a clear, close-up photo of the inside of the mouth",
                              type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if up is not None:
            img = P.read_image(up)
            st.image(img, caption="Uploaded photo", width="stretch")
        else:
            img = None
            st.markdown('<p class="note">Tips: good light, mouth open, the area of concern in focus. '
                        'JPG or PNG.</p>', unsafe_allow_html=True)
with right:
    with st.container(key="card_details"):
        st.markdown('<div class="subhead" style="margin-top:0">2 · Patient details</div>', unsafe_allow_html=True)
        a1, a2 = st.columns([1, 1.3])
        age_known = a2.checkbox("Age known", value=True)
        age = a1.number_input("Age (years)", min_value=1, max_value=110, value=45, disabled=not age_known)
        sex = st.selectbox("Sex", ["Not known", "Female", "Male"])
        yn = ["Not known", "No", "Yes"]
        h1, h2, h3 = st.columns(3)
        smoking = h1.selectbox("Smoking", yn)
        alcohol = h2.selectbox("Alcohol", yn)
        betel = h3.selectbox("Betel quid", yn)
        st.markdown('<div class="subhead">3 · Report</div>', unsafe_allow_html=True)
        if LLM_ENABLED:
            use_llm = st.checkbox("Write the report with AI (local language model)", value=False,
                                  help="Rewrites the standard report in friendlier language. Slower; downloads a model once.")
            llm_id = st.selectbox("Language model", [S.DEFAULT_LLM, "Qwen/Qwen2.5-0.5B-Instruct"], disabled=not use_llm)
        else:
            use_llm, llm_id = False, S.DEFAULT_LLM
            st.markdown('<p class="note">This online demo gives the standard report. The AI-written report '
                        '(fine-tuned Qwen2.5) is available in the offline version that runs on a laptop.</p>',
                        unsafe_allow_html=True)
        run = st.button("Analyse photo", type="primary", width="stretch", disabled=img is None)

to_cat = lambda v, m: None if v == "Not known" else m[v]
patient = dict(age=float(age) if age_known else None,
               sex=to_cat(sex, {"Female": "f", "Male": "m"}),
               smoking=to_cat(smoking, {"No": "no", "Yes": "yes"}),
               alcohol=to_cat(alcohol, {"No": "no", "Yes": "yes"}),
               betel=to_cat(betel, {"No": "no", "Yes": "yes"}))
key = hashlib.md5((up.getvalue() if up else b"") + repr(patient).encode() + repr((use_llm, llm_id)).encode()).hexdigest()

# ----------------------------------------------------------------------------- analysis (kept in session_state so a
# theme switch or any other rerun does not erase the results)
if run and img is not None:
    with st.spinner("Finding the oral cavity..."):
        seg = segmenter(img)
    out = dict(key=key, seg=seg, img=img, patient=patient)
    if seg["ok"]:
        with st.spinner("Screening the photo and preparing the explanation..."):
            res = classifier.classify(seg["crop"], patient)
            over, full_cam = P.heatmap_on_original(img, seg["mask"], seg["box"], res["cam"])
            focus = P.focus_region(full_cam) if res["pred"] else None
            if focus is not None and focus.any():
                over = P.outline(over, focus, (255, 255, 255))
        facts = S.build_facts(res, patient)
        text, note, rejected, source = S.template_summary(facts), "", "", "template"
        if use_llm:
            try:
                with st.spinner("Writing the report with the language model..."):
                    llm = load_llm(llm_id)
                    text, note, rejected = llm.rewrite(text, facts)
                if not note or note.startswith("(accepted"):
                    source = f"{llm_id.split('/')[-1]}" + (" + fine-tuned adapter" if llm.fine_tuned else " (few-shot)")
            except Exception as e:
                note = f"Language model not available ({type(e).__name__}: {e}); showing the standard report."
        out.update(res=res, over=over, text=text, note=note, rejected=rejected, source=source)
    st.session_state["out"] = out
    st.session_state["scroll"] = True

out = st.session_state.get("out")
if out is not None and out["key"] != key:
    st.markdown('<p class="note" style="margin-top:1rem">The photo or details changed. Press <b>Analyse photo</b> '
                'again to update the results below.</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------- results
if out is not None:
    st.markdown(T.section_head("results", "Results", "Screening result"), unsafe_allow_html=True)
    seg, img = out["seg"], out["img"]
    if not seg["ok"]:
        st.markdown(T.H(f"""<div class="info warn"><h4>{T.icon('alert', 20)} The oral cavity could not be found clearly</h4>
<ul><li>It covers only {seg['mask_area']:.0%} of the photo. Please upload a closer photo of the inside of the mouth.</li></ul></div>"""),
                    unsafe_allow_html=True)
        st.image(P.outline(img, seg["mask"] > 0, (0, 255, 0)), caption="What was detected", width=420)
    else:
        res, pat = out["res"], out["patient"]
        hab = {h: res["shap_factors"].get(h, 0.0) for h in S.HABITS if pat.get(S.HABIT_KEY[h]) is not None}
        main = max(hab, key=lambda h: abs(hab[h])) if hab and max(abs(v) for v in hab.values()) > 0.05 else None
        r1, r2, r3 = st.columns([1.5, 1, 1], gap="medium")
        r1.markdown(T.result_html(res["pred"]), unsafe_allow_html=True)
        r2.markdown(T.tile_html("Model score (suspicious)", f"{res['p_final']:.0%}", "Decision line at 50%",
                                meter=res["p_final"], color="var(--bad)" if res["pred"] else "var(--ok)"),
                    unsafe_allow_html=True)
        r3.markdown(T.tile_html("Main habit factor", "—" if main is None else main,
                                "No habit had a clear effect" if main is None else
                                ("raised the score" if hab[main] > 0 else "lowered the score")), unsafe_allow_html=True)

        st.markdown('<div class="subhead">Where the model looked</div>', unsafe_allow_html=True)
        i1, i2, i3 = st.columns(3, gap="medium")
        for col, k, im, cap in [(i1, "imgcard1", P.outline(img, seg["mask"] > 0, (0, 255, 0)), "Oral cavity found (green outline)"),
                                (i2, "imgcard2", seg["crop"], "Region given to the classifier"),
                                (i3, "imgcard3", out["over"], "Grad-CAM: red = strongest focus" +
                                 ("; white = possible area of concern" if res["pred"] else ""))]:
            with col, st.container(key=k):
                st.image(im, caption=cap, width="stretch")
        st.markdown('<p class="note">The heatmap shows which part of the photo influenced the model most. '
                    'It is a hint, not an exact lesion boundary.</p>', unsafe_allow_html=True)

        g1, g2 = st.columns([1, 1.5], gap="large")
        with g1:
            st.markdown('<div class="subhead">How the details affected the score</div>', unsafe_allow_html=True)
            known = {S.FACTOR_KEYS[k] for k, v in pat.items() if v is not None}
            fac = {k: v for k, v in res["shap_factors"].items() if k in known}
            with st.container(key="card_chart"):
                if fac:
                    names = sorted(fac, key=lambda k: abs(fac[k]))
                    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})
                    fig, ax = plt.subplots(figsize=(5, 0.8 + 0.42 * len(names)))
                    fig.patch.set_facecolor(C["surface"]); ax.set_facecolor(C["surface"])
                    ax.barh(names, [fac[n] for n in names], height=.55,
                            color=[C["bad"] if fac[n] > 0 else C["accent"] for n in names])
                    ax.axvline(0, color=C["muted"], lw=0.8)
                    ax.set_xlabel("← lowers the score      raises the score →", color=C["muted"])
                    ax.tick_params(colors=C["text"])
                    for sp in ax.spines.values():
                        sp.set_visible(False)
                    ax.grid(axis="x", color=C["border"], lw=.6); ax.set_axisbelow(True)
                    plt.tight_layout()
                    st.pyplot(fig, width="stretch")
                    plt.close(fig)
                    st.markdown('<p class="note">SHAP values of the metadata model. Directions reflect patterns '
                                'in the training data, not medical causes.</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="note">No patient details were given.</p>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="subhead">Report</div>', unsafe_allow_html=True)
            src = ("✍️ Written by the language model " + out["source"] + " · passed the safety check"
                   if out["source"] != "template" else "📋 Standard report (template)")
            st.markdown(f'<span class="badge">{src}</span>', unsafe_allow_html=True)
            with st.container(key="report"):
                st.markdown(out["text"])
            if out["note"] and not out["note"].startswith("(accepted"):
                st.markdown(f'<p class="note">{out["note"]}</p>', unsafe_allow_html=True)
            if out["rejected"]:
                with st.expander("See the rejected AI text"):
                    st.text(out["rejected"])

        with st.expander("Technical details"):
            rows = [("Image model probability (EfficientNet-B0, 384 px)", f"{res['p_image']:.3f}"),
                    ("Metadata-only probability (XGBoost)", f"{res['p_meta']:.3f}"),
                    ("Final probability (XGBoost stacking)", f"{res['p_final']:.3f}"),
                    ("Relative attribution to the photo (|SHAP| share; not a % of the prediction)", f"{res['image_share']:.2f}"),
                    ("Oral cavity area in the photo", f"{seg['mask_area']:.1%}"),
                    ("Test-set performance of this model", "accuracy 0.785 · MCC 0.585 · AUC 0.854 · sensitivity 0.714 · specificity 0.870")]
            st.markdown("\n".join(["| Item | Value |", "|---|---|"] + [f"| {a} | {b} |" for a, b in rows]))

    if st.session_state.pop("scroll", False):
        components.html("<script>const e=window.parent.document.getElementById('results');"
                        "if(e){e.scrollIntoView({behavior:'smooth'});}</script>", height=0)

st.markdown(T.footer_html(), unsafe_allow_html=True)
