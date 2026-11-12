"""
Runs the local LLM in its own process (PyTorch must not share a process with XGBoost on macOS).
Usage: python llm_worker.py <model_id> [<lora_adapter_dir>]
Protocol: one JSON object per line on stdin {"messages": [...]} (or {"system": ..., "user": ...});
one JSON line back {"text": ...} or {"error": ...}.
"""
import json
import sys


def main():
    model_id = sys.argv[1]
    adapter = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if torch.backends.mps.is_available():
            device, dtype = "mps", torch.float16          # Apple Silicon GPU
        elif torch.cuda.is_available():
            device, dtype = "cuda", torch.float16
        else:
            device, dtype = "cpu", torch.float32
        tok = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype)
        if adapter:
            from peft import PeftModel                      # fine-tuned LoRA adapter from the Kaggle notebook
            model = PeftModel.from_pretrained(model, adapter).merge_and_unload()
        model = model.to(device).eval()
        print(json.dumps({"ready": True, "device": device, "adapter": bool(adapter)}), flush=True)
    except Exception as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}), flush=True)
        return

    for line in sys.stdin:
        try:
            req = json.loads(line)
            msgs = req.get("messages") or [{"role": "system", "content": req["system"]},
                                           {"role": "user", "content": req["user"]}]
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=450, do_sample=False, repetition_penalty=1.05,
                                     pad_token_id=tok.eos_token_id)
            text = tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            print(json.dumps({"text": text}), flush=True)
        except Exception as e:
            print(json.dumps({"error": f"{type(e).__name__}: {e}"}), flush=True)


if __name__ == "__main__":
    main()
