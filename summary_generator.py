"""
Summary text for one prediction.

1. template_summary(): always works, built only from the model outputs (never invents anything).
   Fixed structure with four headings: Result / What influenced the result / What to do next / Reducing your risk.
   It reports the habit factors (smoking, alcohol, betel quid) that moved the model's score, adds a note when a
   direction contradicts medical knowledge, and adds fixed, checked guidance (next steps and risk reduction).
   It does NOT show "x% from the photo / y% from patient details": that SHAP-based relative attribution is not a
   percentage of the prediction and can be misread by patients (it is shown only under Technical details).
2. LLMRewriter: optional. A small local LLM (Qwen2.5-Instruct) rewrites the report in friendlier language, guided by
   two prompt-based examples (few-shot) or a fine-tuned LoRA adapter. A safety check rejects any rewrite that changes
   the result, adds numbers, drops a habit factor, a risk-factor note, any next step, any risk-reduction point,
   the quitline number or a heading, or makes a diagnosis; then the template report is shown instead.
   The disclaimer is always appended by the code, never left to the LLM.
"""
import re

DISCLAIMER = "This is an AI screening aid, not a diagnosis. Please consult a dentist or oral medicine specialist."
DEFAULT_LLM = "Qwen/Qwen2.5-1.5B-Instruct"     # ~3 GB download the first time; "Qwen/Qwen2.5-0.5B-Instruct" is ~1 GB
HEADINGS = ["**Result**", "**What influenced the result**", "**What to do next**", "**Reducing your risk**"]

FACTOR_KEYS = {"age": "Age", "sex": "Sex", "smoking": "Smoking", "alcohol": "Alcohol", "betel": "Betel quid"}
HABITS = ["Smoking", "Alcohol", "Betel quid"]                    # the only factors described in the summary
HABIT_KEY = {"Smoking": "smoking", "Alcohol": "alcohol", "Betel quid": "betel"}
HABIT_TEXT = {"Smoking": ("not smoking", "smoking"), "Alcohol": ("not drinking alcohol", "drinking alcohol"),
              "Betel quid": ("not chewing betel quid", "chewing betel quid")}
SYNONYMS = {"Smoking": ["smok"], "Alcohol": ["alcohol", "drink"], "Betel quid": ["betel", "quid", "paan", "areca"]}

# Fixed, checked guidance: (sentence, words that must survive any rewrite).
NEXT_STEPS_SUSPICIOUS = [
    ("See a dentist, oral medicine specialist or ENT (ear, nose and throat) doctor as soon as possible, ideally within "
     "2 weeks. Take this report and the photo with you.", ["2 weeks"]),
    ("The specialist will examine your mouth and, if needed, take a small tissue sample (biopsy). Only this can "
     "confirm what the patch is.", ["biopsy"]),
    ("Many suspicious patches turn out to be treatable or not cancer, and problems found early are much easier to "
     "treat. Do not delay the visit.", ["early"]),
    ("Tell the doctor if you notice a sore or patch that has not healed in 3 weeks, a lump, bleeding, pain, numbness, "
     "or difficulty chewing or swallowing.", ["3 weeks"]),
]
NEXT_STEPS_CLEAR = [
    ("This result does not rule out oral disease; a screening model can miss problems.", ["rule out"]),
    ("Keep having regular dental check-ups, and look inside your mouth once a month in good light.", ["check-up"]),
    ("See a dentist if any sore, white or red patch, or lump does not heal in 3 weeks, or if you have pain, bleeding "
     "or numbness.", ["3 weeks"]),
]
HABIT_ADVICE = {
    "Smoking": ("Stopping smoking lowers the risk of oral cancer.", ["smok"]),
    "Betel quid": ("Stopping betel quid, areca nut, gutkha and other chewing tobacco lowers the risk of oral cancer.",
                   ["betel"]),
    "Alcohol": ("Cutting down or stopping alcohol lowers the risk, especially together with tobacco.", ["alcohol"]),
}
QUITLINE = ("Free help to quit tobacco in India: National Tobacco Quitline, 1800-11-2356.", ["1800-11-2356"])
GENERAL_ADVICE = ("Avoiding tobacco in any form, betel quid and alcohol helps keep the risk of oral cancer low.",
                  ["tobacco"])


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def build_facts(res, patient):
    """Plain facts for the template and the LLM. res comes from Classifier.classify()."""
    given = [h for h in HABITS if patient.get(HABIT_KEY[h]) is not None]
    sh = {h: res["shap_factors"].get(h, 0.0) for h in given}
    up = [h for h, v in sorted(sh.items(), key=lambda kv: -kv[1]) if v > 0.05]
    down = [h for h, v in sorted(sh.items(), key=lambda kv: kv[1]) if v < -0.05]
    yes = [h for h in HABITS if patient.get(HABIT_KEY[h]) == "yes"]
    text = lambda h: HABIT_TEXT[h][h in yes]
    notes = [f"{HABIT_TEXT[h][1].capitalize()} is still a well-known risk factor for oral cancer. It lowered the score "
             f"here only because of patterns in the data the model learned from; it does not mean it is safe."
             for h in down if h in yes]
    if any(h not in yes for h in up):
        notes.append("Some directions reflect patterns in the data the model learned from, not medical causes.")
    steps = NEXT_STEPS_SUSPICIOUS if res["pred"] else NEXT_STEPS_CLEAR
    life = [HABIT_ADVICE[h] for h in yes]
    if any(h in yes for h in ("Smoking", "Betel quid")):
        life.append(QUITLINE)
    if not life:
        life = [GENERAL_ADVICE]
    return dict(
        suspicious=bool(res["pred"]),
        result_word="suspicious" if res["pred"] else "not suspicious",
        result_detail="possible OPMD or oral cancer" if res["pred"] else "healthy or benign",
        probability=round(res["p_final"] * 100),
        habits_given=given, factors_up=up, factors_down=down,
        up_text=[text(h) for h in up], down_text=[text(h) for h in down], notes=notes,
        next_steps=[s for s, _ in steps], next_keys=[k for _, k in steps],
        lifestyle=[s for s, _ in life], life_keys=[k for _, k in life],
    )


def template_summary(f):
    """Markdown report with the same four headings every time."""
    res = (f"The screening model classified the photo as **{f['result_word']}** ({f['result_detail']}), with a model "
           f"score of {f['probability']}%. The coloured area on the photo shows where the model looked most closely"
           + (" and may point to the area that needs checking." if f["suspicious"] else "."))
    if not f["habits_given"]:
        infl = ("No habit details (smoking, alcohol, betel quid) were given, so the result is based on the photo "
                "and any other details entered.")
    else:
        parts = []
        if f["up_text"]:
            parts.append(f"Habits that raised the score: {_join(f['up_text'])}.")
        if f["down_text"]:
            parts.append(f"Habits that lowered the score: {_join(f['down_text'])}.")
        if not parts:
            parts.append("The habit details given had little effect on the score; the result is based mainly on the photo.")
        infl = " ".join(parts + f["notes"])
    out = [HEADINGS[0], res, HEADINGS[1], infl,
           HEADINGS[2], "\n".join(f"- {s}" for s in f["next_steps"]),
           HEADINGS[3], "\n".join(f"- {s}" for s in f["lifestyle"]),
           f"_{DISCLAIMER}_"]
    return "\n\n".join(out)


# ----------------------------------------------------------------------------- few-shot examples
# Two hand-written, prompt-based examples that guide the LLM's rewriting style (not training data).
FEW_SHOT_CASES = [
    (dict(pred=1, p_final=.78, image_share=.62,
          shap_factors={"Age": .3, "Sex": .1, "Smoking": .0, "Alcohol": -.12, "Betel quid": .5}),
     dict(age=58.0, sex="m", smoking="no", alcohol="yes", betel="yes"),
     """**Result**

The screening model classified the photo as **suspicious** (possible OPMD or oral cancer), with a model score of 78%. The coloured area on the photo shows where the model looked most closely, and it may point to the area that needs checking.

**What influenced the result**

Chewing betel quid raised the score. Drinking alcohol lowered it. Please note that drinking alcohol is still a well-known risk factor for oral cancer. It lowered the score here only because of patterns in the data the model learned from, so it does not mean drinking is safe.

**What to do next**

- Please see a dentist, oral medicine specialist or ENT (ear, nose and throat) doctor as soon as possible, ideally within 2 weeks, and take this report and the photo with you.
- The specialist will examine your mouth and, if needed, take a small tissue sample (biopsy). Only this test can confirm what the patch is.
- Many suspicious patches turn out to be treatable or not cancer, and anything found early is much easier to treat, so please do not delay the visit.
- Tell the doctor if you notice a sore or patch that has not healed in 3 weeks, a lump, bleeding, pain, numbness, or difficulty chewing or swallowing.

**Reducing your risk**

- Cutting down or stopping alcohol lowers your risk, especially if you also use tobacco.
- Stopping betel quid, areca nut, gutkha and other chewing tobacco lowers your risk of oral cancer.
- For free help to quit tobacco, call the National Tobacco Quitline on 1800-11-2356."""),
    (dict(pred=0, p_final=.18, image_share=.55,
          shap_factors={"Age": -.3, "Sex": -.1, "Smoking": .2, "Alcohol": .0, "Betel quid": -.2}),
     dict(age=27.0, sex="f", smoking="yes", alcohol=None, betel="no"),
     """**Result**

The screening model classified the photo as **not suspicious** (healthy or benign), with a model score of 18%. The coloured area on the photo shows where the model looked most closely.

**What influenced the result**

Smoking raised the score, and not chewing betel quid lowered it.

**What to do next**

- This result does not rule out oral disease, because a screening model can miss problems.
- Keep having regular dental check-ups, and look inside your mouth once a month in good light.
- See a dentist if any sore, white or red patch, or lump does not heal in 3 weeks, or if you have pain, bleeding or numbness.

**Reducing your risk**

- Smoking is a risk factor for oral cancer, and stopping smoking lowers your risk.
- For free help to quit tobacco, call the National Tobacco Quitline on 1800-11-2356."""),
]


def build_messages(draft, system, few_shot=True):
    """Chat messages for the LLM: system rules, optional worked examples, then the real draft."""
    msgs = [{"role": "system", "content": system}]
    if few_shot:
        for res, patient, answer in FEW_SHOT_CASES:
            ex = template_summary(build_facts(res, patient)).replace(f"_{DISCLAIMER}_", "").strip()
            msgs += [{"role": "user", "content": f"Draft report:\n\n{ex}"}, {"role": "assistant", "content": answer}]
    msgs.append({"role": "user", "content": f"Draft report:\n\n{draft}"})
    return msgs


# ----------------------------------------------------------------------------- safety check
# Phrases that would make a diagnosis, promise an outcome, reassure falsely or mention treatment. Precise patterns,
# so ordinary sentences like "you don't have to worry" or "definitely see a dentist" are not caught.
BANNED = [
    r"\byou (?:\w+ ){0,2}have (?:oral |mouth )?cancer", r"\byou (?:do not|don't|dont) have (?:oral |mouth )?cancer",
    r"\b(?:is|are|it's) (?:definitely|certainly|surely) (?:not )?(?:cancer|malignant|benign)",
    r"\bdiagnosed with\b", r"\bthe diagnosis is\b", r"\bguarantee", r"\bgood news\b", r"\bnothing to worry",
    r"\bno need to (?:see|consult|visit|worry)", r"\bchemotherapy\b", r"\bradiotherapy\b",
    r"\bradiation therapy\b", r"\bsurgery\b", r"\bmalignant tumou?r", r"\bterminal\b", r"\bfatal\b", r"\bdeadly\b",
]


def is_safe(text, facts):
    """True if an LLM rewrite keeps every fact, step and warning of the template and adds nothing unsupported."""
    t = text.lower()
    for pat in BANNED:
        m = re.search(pat, t)
        if m:
            return False, f"contains a diagnostic, reassuring or alarming phrase: '{m.group(0)}'"
    if "%" in text.replace(f"{facts['probability']}%", ""):
        return False, "added a percentage that is not the model score"
    allowed = {str(facts["probability"])} | set(re.findall(r"\d+", " ".join(facts["next_steps"] + facts["lifestyle"])))
    nums = set(re.findall(r"\d+", text))
    if not nums <= allowed:
        return False, f"added numbers not in the results: {sorted(nums - allowed)}"
    says_not = bool(re.search(r"\bnot (?:appear |look |seem )?(?:to be )?suspicious|\bnon-suspicious", t))
    if facts["suspicious"] and (says_not or "suspicious" not in t):
        return False, "changed the result"
    if not facts["suspicious"] and not says_not:
        return False, "changed the result"
    if "screening" not in t:
        return False, "did not say the result comes from a screening model"
    for h in HEADINGS:
        if h.strip("*").lower() not in t:
            return False, f"left out the heading {h.strip('*')}"
    for h in facts["factors_up"] + facts["factors_down"]:
        if not any(w in t for w in SYNONYMS[h]):
            return False, f"left out the habit '{h}'"
    if any("risk factor" in n for n in facts["notes"]) and "risk factor" not in t:
        return False, "left out the note that a habit is still a risk factor"
    if facts["notes"] and "pattern" not in t:
        return False, "left out the note that directions come from patterns in the data"
    for step, keys in zip(facts["next_steps"], facts["next_keys"]):
        if not all(k.lower() in t for k in keys):
            return False, f"left out the next step '{step[:45]}...'"
    for tip, keys in zip(facts["lifestyle"], facts["life_keys"]):
        if not all(k.lower() in t for k in keys):
            return False, f"left out the risk-reduction point '{tip[:45]}...'"
    if len(text.split()) > 330:
        return False, "is too long"
    return True, ""


# ----------------------------------------------------------------------------- LLM
class LLMRewriter:
    """Talks to llm_worker.py, which loads a small instruction-tuned model with Hugging Face transformers
    (downloaded once, then offline). It runs in a separate process so PyTorch never shares a process with XGBoost."""

    SYSTEM = ("You write short, kind, easy-to-read oral screening reports for patients in India. "
              "You are given a draft report made from an AI screening model's results and checked medical guidance. "
              "Rewrite it in calm, neutral, simple English that a non-medical person understands. Rules: "
              "use ONLY the facts and advice in the draft; do not add new numbers, percentages, diseases, tests, "
              "treatments or causes; make clear the result comes from an AI screening model, not a diagnosis; "
              "never say the person has or does not have cancer; do not say 'good news' or give false reassurance; "
              "keep the result word exactly as given ('suspicious' or 'not suspicious'); mention every habit that is "
              "named and whether it raised or lowered the score; keep every note about risk factors and data "
              "patterns; keep every next step, every risk-reduction point and the quitline number; always use exactly "
              "these four bold headings in this order: **Result**, **What influenced the result**, **What to do next**, "
              "**Reducing your risk**, with short bullet points under the last two; at most 250 words.")

    def __init__(self, model_id=DEFAULT_LLM, adapter_dir=None):
        """adapter_dir: folder with a fine-tuned LoRA adapter (from the Kaggle notebook); None = auto-detect
        models/llm/qwen_report_lora next to this file. With an adapter, few-shot examples are not needed."""
        import subprocess, sys, json
        from pathlib import Path
        self.json = json
        here = Path(__file__).resolve().parent
        if adapter_dir is None:
            cand = here / "models" / "llm" / "qwen_report_lora"
            adapter_dir = cand if (cand / "adapter_config.json").exists() else None
        if adapter_dir is not None:
            # the adapter only fits the model it was trained on (e.g. 1.5B); with another model use few-shot instead
            try:
                base = json.load(open(Path(adapter_dir) / "adapter_config.json")).get("base_model_name_or_path", "")
            except Exception:
                base = ""
            if base and base.rstrip("/").split("/")[-1].lower() != model_id.rstrip("/").split("/")[-1].lower():
                adapter_dir = None
        worker = here / "llm_worker.py"
        cmd = [sys.executable, str(worker), model_id] + ([str(adapter_dir)] if adapter_dir else [])
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        first = self._read()
        if "error" in first:
            raise RuntimeError(first["error"])
        self.fine_tuned = bool(first.get("adapter"))

    def _read(self):
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("the language model process stopped (see the Terminal for details)")
            line = line.strip()
            if line.startswith("{"):
                try:
                    return self.json.loads(line)
                except ValueError:
                    pass

    def _ask(self, messages):
        self.proc.stdin.write(self.json.dumps({"messages": messages}) + "\n")
        self.proc.stdin.flush()
        return self._read()

    def rewrite(self, template, facts, attempts=2):
        """Returns (text_to_show, note, rejected_llm_text). Retries once with feedback if the safety check fails."""
        draft = template.replace(f"_{DISCLAIMER}_", "").strip()
        msgs = build_messages(draft, self.SYSTEM, few_shot=not self.fine_tuned)
        rejected, why = "", ""
        for i in range(attempts):
            reply = self._ask(msgs)
            if "error" in reply:
                return template, f"Language model error ({reply['error']}); showing the standard summary.", rejected
            text = reply["text"].replace(DISCLAIMER, "").strip()
            ok, why = is_safe(text, facts)
            if ok:
                return f"{text}\n\n_{DISCLAIMER}_", ("" if i == 0 else "(accepted on the second try)"), ""
            rejected = text
            msgs = msgs + [{"role": "assistant", "content": text},
                           {"role": "user", "content": f"That version was rejected because it {why}. "
                                                       f"Write the report again from the draft and follow every rule exactly."}]
        return template, f"LLM text rejected ({why}); showing the standard summary.", rejected
