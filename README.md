# OralScreen AI (online demo)

AI-assisted oral cancer screening prototype (M.Tech project).
Oral-cavity segmentation (Mobile-UNet) → EfficientNet-B0 screening → XGBoost fusion with patient habits →
Grad-CAM and SHAP explanations → plain-language report.

This is the lightweight online version for Streamlit Community Cloud: the AI-written report (fine-tuned
Qwen2.5) is only in the offline version; here the standard report is shown.

**Screening aid only, not a diagnosis.**

## One deployment, two pages

| URL | Page | File |
|---|---|---|
| `/` | Project website (objectives, methodology, results, progress, team) | `website/site.py` |
| `/screening` | Screening app | `screening.py` |

`app.py` only routes between the two pages.
Demo videos: put `.mp4` files in `website/assets/videos/` and they appear in the Demonstration section.

Run locally: `pip install -r requirements.txt` then `streamlit run app.py`.

Full code, notebooks and documentation: <https://github.com/annapoorna-a-k/Oral-Cancer-Detection-and-Multiclass-Classification>
