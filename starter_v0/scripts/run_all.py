"""One command to produce every piece of REAL evidence the lab asks for.

Run from starter_v0/ (needs real keys in .env):

    python scripts/run_all.py --provider openrouter --author "Nhóm X"

What it does (each step can be skipped, see --help):
  1. preflight the provider
  2. base eval for every snapshot in artifacts/versions/v0..v4 (prompt + tools of that version)
  3. group eval + extension eval on the final version (v4)
  4. optional: local small models (--local-models qwen2.5:7b llama3.2:3b)
  5. scripted live chat (scripts/run_chat_demo.py) -> transcripts/*.transcript.json
  6. writes artifacts/version_log.csv from the run JSON (real hashes, real metrics)
  7. parses runs into analysis/all_runs.csv and fills the evidence tables in artifacts/REPORT.md

Nothing here invents numbers: every metric comes from runs/*.json written by run_eval.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = ROOT / "artifacts" / "versions"
PY = sys.executable

# One hypothesis per version. Written BEFORE running, confirmed/refuted by the run JSON.
VERSION_META: dict[str, dict[str, str]] = {
    "v0": {
        "changed_artifact": "baseline",
        "reason": "Baseline starter: prompt khuyến khích đoán / tự gửi / một bước; tools.yaml mô tả mơ hồ",
        "hypothesis": "Đo hành vi chưa tối ưu: dự đoán FAIL ở clarify (R10,R11), confirm (R12), parallel (R13) và args (R03,R06,R07)",
    },
    "v1": {
        "changed_artifact": "system_prompt.md",
        "reason": "Bỏ 3 chỉ dẫn xấu (đoán thay vì hỏi, gửi không cần xác nhận, ép một tool) + thêm 4 rule boundary",
        "hypothesis": "Lỗi missing_info / wrong_boundary / parallel do prompt ra lệnh sai, không phải do model: sửa prompt sẽ PASS R10,R11,R12,R13 mà không cần đổi tools.yaml",
    },
    "v2": {
        "changed_artifact": "tools.yaml",
        "reason": "Viết lại description mọi tool (làm gì / khi nào dùng / khi nào KHÔNG dùng) + convention args",
        "hypothesis": "Lỗi wrong_arg_value còn lại (handle sama/elonmusk/karpathy, topic=news, timeframe, search_type=Top, query chỉ là keyword) do model không biết convention; ghi convention vào parameter description sẽ sửa chúng",
    },
    "v3": {
        "changed_artifact": "system_prompt.md",
        "reason": "Thêm bảng routing + quy ước args + rule multi-turn (chỉ trả lời lượt cuối, carry-over slot, correction ghi đè)",
        "hypothesis": "Lỗi còn lại tập trung ở multi-turn (M01–M06): model không biết carry-over/ghi đè giá trị giữa các lượt; rule hội thoại tường minh sẽ tăng multiturn_accuracy",
    },
    "v4": {
        "changed_artifact": "tools.yaml + system_prompt.md",
        "reason": "Thêm 4 tool mới (wikipedia, hackernews, github_repos, hf_models) có ranh giới khi-nào-KHÔNG-dùng + routing rows + rule gửi sau khi user nói Có",
        "hypothesis": "Mở rộng scope bằng tool có ranh giới rõ sẽ KHÔNG làm giảm base eval (không cướp routing của lookup/social_search, không gọi tool cho câu out-of-scope) và cho phép PASS group eval",
    },
}


def run(cmd: list[str]) -> str:
    print("\n$ " + " ".join(cmd), flush=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}  # Vietnamese/emoji safe on Windows
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, env=env, encoding="utf-8", errors="replace")
    print(proc.stdout[-4000:])
    if proc.returncode != 0:
        print(proc.stderr[-4000:], file=sys.stderr)
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.stdout


def run_eval(version: str, suite: str, eval_file: str, provider: str, model: str | None,
             prompt: Path, tools: Path) -> Path:
    cmd = [PY, "run_eval.py", "--provider", provider, "--version", version, "--suite", suite,
           "--eval-cases", eval_file, "--system-prompt", str(prompt.relative_to(ROOT)),
           "--tools", str(tools.relative_to(ROOT))]
    if model:
        cmd += ["--model", model]
    out = run(cmd)
    match = re.search(r"Saved: (.+\.json)", out)
    if not match:
        raise SystemExit("Could not find the saved run file in run_eval.py output")
    return Path(match.group(1).strip())


def load_run(path: Path) -> dict:
    path = path if path.is_absolute() else ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    path = path if path.is_absolute() else ROOT / path
    return str(path.resolve().relative_to(ROOT))


def write_version_log(rows: list[dict[str, str]], author: str) -> Path:
    out = ROOT / "artifacts" / "version_log.csv"
    fields = ["version", "author", "changed_artifact", "artifact_version", "prompt_hash", "tools_hash",
              "reason", "hypothesis", "metric_before", "metric_after", "run_file"]
    with out.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"author": author, **row})
    print(f"Wrote {out}")
    return out


def log_row(version: str, run_path: Path, before: float | None, meta: dict[str, str]) -> dict[str, str]:
    data = load_run(run_path)
    summary = data["summary"]
    return {
        "version": version,
        "changed_artifact": meta["changed_artifact"],
        "artifact_version": data["artifact_version"],
        "prompt_hash": data["prompt_hash"][:12],
        "tools_hash": data["tools_hash"][:12],
        "reason": meta["reason"],
        "hypothesis": meta["hypothesis"],
        "metric_before": "" if before is None else f"{before:.4f}",
        "metric_after": f"{summary['case_accuracy']:.4f}",
        "run_file": rel(run_path),
    }


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except AttributeError:
            pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", default="openrouter", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--author", default="team")
    parser.add_argument("--versions", nargs="+", default=["v0", "v1", "v2", "v3", "v4"])
    parser.add_argument("--final", default="v4", help="Version used for group/extension eval, chat demo and local check.")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--skip-base", action="store_true")
    parser.add_argument("--skip-group", action="store_true")
    parser.add_argument("--skip-extension", action="store_true")
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--local-models", nargs="*", default=[], help="Ollama models for Step 7, e.g. qwen2.5:7b llama3.2:3b")
    args = parser.parse_args()

    if not args.skip_preflight:
        cmd = [PY, "scripts/preflight_provider.py", "--provider", args.provider]
        run(cmd + (["--model", args.model] if args.model else []))

    rows: list[dict[str, str]] = []
    previous: float | None = None
    final_dir = VERSIONS_DIR / args.final

    if not args.skip_base:
        for version in args.versions:
            vdir = VERSIONS_DIR / version
            path = run_eval(version, "base", "data/eval_base.json", args.provider, args.model,
                            vdir / "system_prompt.md", vdir / "tools.yaml")
            row = log_row(version, path, previous, VERSION_META.get(version, {
                "changed_artifact": "?", "reason": "?", "hypothesis": "?"}))
            rows.append(row)
            previous = float(row["metric_after"])

    if not args.skip_group:
        path = run_eval(args.final, "group", "data/eval_group.json", args.provider, args.model,
                        final_dir / "system_prompt.md", final_dir / "tools.yaml")
        rows.append(log_row(f"{args.final}-group", path, None, {
            "changed_artifact": "data/eval_group.json",
            "reason": "Chạy 10 team case (5 single + 5 multi) trên bản cuối",
            "hypothesis": "Tool mới được route đúng lúc; boundary send (Có → gửi, huỷ → không gửi) đúng",
        }))

    if not args.skip_extension:
        path = run_eval(args.final, "extension", "data/eval_research_extension.json", args.provider, args.model,
                        final_dir / "system_prompt.md", final_dir / "tools.yaml")
        rows.append(log_row(f"{args.final}-extension", path, None, {
            "changed_artifact": "data/eval_research_extension.json",
            "reason": "Extension eval: policy + arXiv",
            "hypothesis": "Mô tả policy_area và papers/paper_text đủ để route đúng các câu policy/arXiv",
        }))

    cloud_best = previous
    local_dir_v4 = ROOT / "artifacts" / "local" / "v4-local"
    local_dir_v5 = ROOT / "artifacts" / "local" / "v5-local"
    for local_model in args.local_models:
        slug = re.sub(r"[^a-z0-9]+", "", local_model.lower())
        base_prev = None
        for label, vdir, meta in [
            (f"{args.final}-{slug}", final_dir, {"changed_artifact": "none (cloud prompt)",
             "reason": f"Local baseline {local_model} với prompt/tools cloud {args.final}",
             "hypothesis": "Prompt tối ưu cho cloud có còn đúng trên model nhỏ không"}),
            (f"v4-local-{slug}", local_dir_v4, {"changed_artifact": "artifacts/local/v4-local",
             "reason": f"{local_model}: rút gọn prompt + description ngắn có ví dụ args, bỏ tool không dùng trong base",
             "hypothesis": "Model nhỏ bị lạc vì prompt dài và 14 tool; prompt ngắn + ít tool giảm wrong_tool"}),
            (f"v5-local-{slug}", local_dir_v5, {"changed_artifact": "artifacts/local/v5-local",
             "reason": f"{local_model}: thêm few-shot routing examples vào prompt ngắn",
             "hypothesis": "Few-shot cụ thể giúp model nhỏ gọi clarify và điền args đúng hơn"}),
        ]:
            path = run_eval(label, "base", "data/eval_base.json", "ollama", local_model,
                            vdir / "system_prompt.md", vdir / "tools.yaml")
            row = log_row(label, path, base_prev, meta)
            row["reason"] += f" [model={local_model}]"
            rows.append(row)
            base_prev = float(row["metric_after"])
    if args.local_models:
        path = run_eval("v5-local-on-cloud", "base", "data/eval_base.json", args.provider, args.model,
                        local_dir_v5 / "system_prompt.md", local_dir_v5 / "tools.yaml")
        rows.append(log_row("v5-local-on-cloud", path, cloud_best, {
            "changed_artifact": "artifacts/local/v5-local",
            "reason": "Kiểm tra ngược: prompt local v5 chạy trên model cloud",
            "hypothesis": "Prompt ngắn + few-shot không làm giảm điểm cloud",
        }))

    if rows:
        existing = ROOT / "artifacts" / "version_log.csv"
        if args.skip_base and existing.exists():  # keep earlier rows when re-running only part
            with existing.open(encoding="utf-8") as file:
                old = [r for r in csv.DictReader(file) if r["version"] not in {row["version"] for row in rows}]
            rows = old + rows  # old rows keep their own author column
        write_version_log(rows, args.author)

    if not args.skip_chat:
        cmd = [PY, "scripts/run_chat_demo.py", "--provider", args.provider, "--version", args.final,
               "--system-prompt", str((final_dir / "system_prompt.md").relative_to(ROOT)),
               "--tools", str((final_dir / "tools.yaml").relative_to(ROOT))]
        run(cmd + (["--model", args.model] if args.model else []))

    run([PY, "scripts/parse_runs.py", "runs/", "--output", "analysis/all_runs.csv"])
    run([PY, "scripts/fill_report.py"])
    print("\nDONE. Đọc artifacts/REPORT.md (các bảng AUTO đã được điền từ log thật) rồi viết nhận xét của nhóm.")


if __name__ == "__main__":
    main()
