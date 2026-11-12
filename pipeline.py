"""
Oral screening pipeline used by the Streamlit app.

photo -> Mobile-UNet lw_adapters (oral cavity mask) -> segmented crop
      -> EfficientNet-B0 384 px (image probability) + Grad-CAM
      -> L4 XGBoost stacker [image probability + patient details] -> final probability
      -> SHAP (metadata XGBoost + L4 stacker) for the explanation

No PyTorch is loaded in this process: on Apple Silicon Macs, PyTorch's OpenMP library and the one XGBoost
uses clash and crash Python. The classifier therefore runs as ONNX (exported from the trained PyTorch model,
identical output) and the optional LLM runs in a separate process (llm_worker.py).
"""
import os

import json
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
import xgboost as xgb
from PIL import Image, ImageOps

MODELS_DIR = Path(__file__).resolve().parent / "models"
SEG_SIZE = 256
SEG_THRESHOLD = 0.5
MIN_MASK_AREA = 0.05          # mask smaller than 5% of the photo -> probably not an intraoral photo
WORK_MAX_SIDE = 1600          # big phone photos are scaled down to this before processing
FACTOR_NAMES = {"age": "Age", "sex": "Sex", "smoking": "Smoking", "alcohol": "Alcohol", "betel": "Betel quid"}


def _find(pattern):
    hits = sorted(MODELS_DIR.rglob(pattern))
    if not hits:
        raise FileNotFoundError(f"Could not find '{pattern}' inside {MODELS_DIR}")
    return hits[0]


# ----------------------------------------------------------------------------- image reading
def read_image(file_or_path):
    """Read a photo the same way as training (EXIF rotation applied), RGB uint8, scaled to WORK_MAX_SIDE."""
    img = np.asarray(ImageOps.exif_transpose(Image.open(file_or_path)).convert("RGB"))
    s = WORK_MAX_SIDE / max(img.shape[:2])
    if s < 1:
        img = cv2.resize(img, (int(img.shape[1] * s), int(img.shape[0] * s)), interpolation=cv2.INTER_AREA)
    return img


# ----------------------------------------------------------------------------- segmentation
class Segmenter:
    def __init__(self):
        onnx = next(iter(sorted(MODELS_DIR.rglob("lw_adapters*.onnx"))), None)
        if onnx is None:
            raise FileNotFoundError("lw_adapters.onnx not found in models/segmentation/")
        self.sess = ort.InferenceSession(str(onnx), providers=["CPUExecutionProvider"])
        self.inp = self.sess.get_inputs()[0].name

    def __call__(self, img):
        h, w = img.shape[:2]
        x = cv2.resize(img, (SEG_SIZE, SEG_SIZE), interpolation=cv2.INTER_AREA).astype(np.float32)[None] / 255.0
        prob = self.sess.run(None, {self.inp: x})[0][0, ..., 0]
        prob = cv2.resize(prob, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = _clean_mask((prob > SEG_THRESHOLD).astype(np.uint8) * 255)
        crop, box = segmented_crop(img, mask)
        area = float((mask > 0).mean())
        return dict(mask=mask, mask_area=area, crop=crop, box=box, ok=crop is not None and area >= MIN_MASK_AREA)


def _clean_mask(mask):
    """Keep the largest region and fill holes (same as the segmentation notebook)."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n <= 1:
        return mask
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    out = np.where(lab == largest, 255, 0).astype(np.uint8)
    contours, _ = cv2.findContours(out, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, contours, -1, 255, thickness=cv2.FILLED)
    return out


def segmented_crop(img, mask):
    """Black out everything outside the mask and crop to its box (the format the classifier was trained on)."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None, None
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    crop = (img * (mask[..., None] > 0))[y0:y1, x0:x1]
    return crop, (int(x0), int(y0), int(x1), int(y1))


# ----------------------------------------------------------------------------- classifier
class Classifier:
    def __init__(self):
        cfg_path = _find("EfficientNet-B0/Image_only/config.json")
        d = cfg_path.parent
        self.cfg = json.load(open(cfg_path))
        self.img_size = self.cfg["img_size"]
        self.pre = max(256, self.img_size + 32)
        self.mean, self.std = np.array(self.cfg["mean"], np.float32), np.array(self.cfg["std"], np.float32)
        self.sess = ort.InferenceSession(str(d / "effb0_384.onnx"), providers=["CPUExecutionProvider"])
        self.head_w = np.load(d / "effb0_384_head.npz")["W"]          # final linear layer, used for Grad-CAM
        self.enc = json.load(open(_find("metadata_encoding.json")))
        self.meta_xgb = xgb.XGBClassifier(); self.meta_xgb.load_model(str(_find("Metadata_only/xgboost.json")))
        self.l4 = xgb.XGBClassifier(); self.l4.load_model(str(_find("EfficientNet-B0/late_fusion/L4_xgboost.json")))
        self.threshold = float(self.cfg.get("threshold", 0.5))

    # ---- metadata
    def encode(self, patient):
        """patient: dict with keys age (number or None), sex ('m'/'f'/None), smoking/alcohol/betel ('yes'/'no'/None)."""
        v = {}
        for col, st in self.enc["encoding"]["numeric"].items():
            key = next(k for k, c in self.enc["columns"].items() if c == col)
            a = patient.get(key)
            a = st["median"] if a is None else float(a)
            v[f"m_{key}"] = float(np.clip((a - st["min"]) / max(st["max"] - st["min"], 1e-6), 0, 1))
        for col, cats in self.enc["encoding"]["categorical"].items():
            key = next(k for k, c in self.enc["columns"].items() if c == col)
            val = (patient.get(key) or "unknown").strip().lower()
            for ct in cats:
                v[f"m_{key}={ct}"] = float(val == ct)
        return np.array([[v[f] for f in self.enc["features"]]], dtype=np.float32)

    # ---- image + Grad-CAM
    def image_prob_and_cam(self, crop, target=None):
        """Same preprocessing as training: resize to PRE (bicubic) -> IMG_SIZE (bilinear) -> ImageNet normalisation.
        Grad-CAM: the network ends with global average pooling + one linear layer, so the Grad-CAM channel weights
        are exactly that layer's weights for the target class (checked against PyTorch autograd: correlation 1.0)."""
        im = Image.fromarray(crop).resize((self.pre, self.pre), Image.BICUBIC).resize((self.img_size, self.img_size), Image.BILINEAR)
        x = ((np.asarray(im, np.float32) / 255.0 - self.mean) / self.std).transpose(2, 0, 1)[None].astype(np.float32)
        logits, feats = self.sess.run(None, {"image": x})
        e = np.exp(logits[0] - logits[0].max()); p = float(e[1] / e.sum())
        target = int(p >= self.threshold) if target is None else target
        cam = np.maximum(np.tensordot(self.head_w[target], feats[0], axes=1), 0)
        cam = cam / cam.max() if cam.max() > 0 else cam
        return p, cam.astype(np.float32)

    def classify(self, crop, patient):
        M = self.encode(patient)
        p_img, _ = self.image_prob_and_cam(crop)
        X4 = np.column_stack([[p_img], M]).astype(np.float32)
        p_final = float(self.l4.predict_proba(X4)[0, 1])
        pred = int(p_final >= self.threshold)
        _, cam = self.image_prob_and_cam(crop, target=pred)      # heatmap for the final decision
        # SHAP (exact TreeSHAP from xgboost), log-odds units, > 0 pushes towards "suspicious"
        c_meta = self.meta_xgb.get_booster().predict(xgb.DMatrix(M), pred_contribs=True)[0, :-1]
        c_l4 = self.l4.get_booster().predict(xgb.DMatrix(X4.astype(np.float32)), pred_contribs=True)[0, :-1]
        factors = {}
        for f, val in zip(self.enc["features"], c_meta):
            k = FACTOR_NAMES.get(f[2:].split("=")[0], f)
            factors[k] = factors.get(k, 0.0) + float(val)
        s_img, s_meta = abs(float(c_l4[0])), abs(float(c_l4[1:].sum()))
        return dict(p_image=p_img, p_meta=float(self.meta_xgb.predict_proba(M)[0, 1]), p_final=p_final, pred=pred,
                    cam=cam, shap_factors=factors, image_share=s_img / (s_img + s_meta + 1e-9))


# ----------------------------------------------------------------------------- drawing
def heatmap_on_original(img, mask, box, cam, alpha=0.45):
    """Paste the crop's Grad-CAM back onto the full photo (only inside the oral-cavity mask)."""
    x0, y0, x1, y1 = box
    full = np.zeros(img.shape[:2], np.float32)
    full[y0:y1, x0:x1] = cv2.resize(cam, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    full *= (mask > 0)
    heat = cv2.applyColorMap((np.clip(full, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    w = (alpha * (full > 0.05))[..., None]
    return (img * (1 - w) + heat * w).astype(np.uint8), full


def outline(img, binary, color, thickness=None):
    out = img.copy()
    t = thickness or max(2, img.shape[1] // 300)
    contours, _ = cv2.findContours(binary.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, contours, -1, color, t)
    return out


def focus_region(full_cam, level=0.6, min_frac=0.002):
    """The strongest-attention region (top of the heatmap) -- shown as 'where the model focused'."""
    reg = (full_cam >= level).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(reg, connectivity=8)
    keep = np.zeros_like(reg)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_frac * reg.size:
            keep[lab == i] = 1
    return keep
