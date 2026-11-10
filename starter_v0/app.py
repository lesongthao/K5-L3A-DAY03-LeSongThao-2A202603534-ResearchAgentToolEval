from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    execute_tool_call,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


st.set_page_config(page_title="Research Desk", page_icon="R", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      :root {
        --ink: #17231f;
        --muted: #64716b;
        --paper: #f5f7f3;
        --line: #dce4dc;
        --green: #176b4a;
        --mint: #dcefe4;
        --coral: #b94b35;
      }
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
      .stApp {
        background-color: var(--paper);
        background-image: linear-gradient(rgba(23, 107, 74, .035) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(23, 107, 74, .035) 1px, transparent 1px);
        background-size: 32px 32px;
      }
      [data-testid="stSidebar"] { background: #eaf0e9; border-right: 1px solid var(--line); }
      h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: 0; }
      h1 { font-size: 2rem; font-weight: 800; }
      [data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 8px; background: rgba(255,255,255,.82); }
      [data-testid="stChatMessage"] p { line-height: 1.65; }
      [data-testid="stChatInput"] { border-color: #b9c9bd; }
      .desk-kicker { color: var(--green); font-size: .75rem; font-weight: 700; text-transform: uppercase; }
      .desk-subtitle { color: var(--muted); margin-top: -.6rem; }
      div.stButton > button, div.stDownloadButton > button { border-radius: 6px; }
      div.stButton > button[kind="primary"] { background: var(--green); border-color: var(--green); }
      [data-testid="stMetric"] { background: rgba(255,255,255,.72); padding: .8rem; border: 1px solid var(--line); border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_conversation() -> None:
    for key in ("turns", "history", "transcript", "transcript_path", "conversation_config"):
        st.session_state.pop(key, None)


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        return
    with st.expander(f"Hoạt động công cụ · {len(events)}", expanded=False):
        for event in events:
            st.markdown(f"**{event.get('tool', 'tool')}**")
            st.caption("Tham số")
            st.json(event.get("args", {}), expanded=False)
            st.caption("Kết quả")
            st.json(event.get("result", {}), expanded=False)


def render_turns() -> None:
    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("status") == "provider_error":
                st.error(turn.get("error", "Provider error"))
            else:
                st.markdown(turn.get("assistant_text") or "Agent không trả về nội dung.")
            render_tool_events(turn.get("tool_events", []))


def save_turn(user_text: str, allow_telegram: bool) -> None:
    config = st.session_state.get("conversation_config")
    if config is None:
        config = {
            "provider": st.session_state.provider,
            "model": st.session_state.model.strip() or None,
            "version": st.session_state.version.strip() or "v0",
        }
        st.session_state.conversation_config = config

        prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        version = build_artifact_version(config["version"], prompt_path, tools_path)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([
            safe_slug(config["version"]),
            safe_slug(config["provider"]),
            timestamp,
        ])
        model_provider = make_provider(config["provider"])
        selected_model = config["model"] or getattr(model_provider, "default_model", None)
        st.session_state.transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(version),
            "provider": config["provider"],
            "model": selected_model,
            "system_prompt": str(prompt_path.relative_to(ROOT)),
            "tools": str(tools_path.relative_to(ROOT)),
            "history_window": 5,
            "max_tool_rounds": 4,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        st.session_state.transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"

    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    provider = make_provider(config["provider"])
    model = config["model"]
    history = st.session_state.history
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, 5),
        {"role": "user", "content": user_text},
    ]

    def guarded_executor(call: Any) -> dict[str, Any]:
        if call.name == "send":
            if not allow_telegram:
                return {
                    "tool": call.name,
                    "args": call.args,
                    "result": {
                        "status": "blocked",
                        "message": "Telegram đang bị khóa. Bật xác nhận trong thanh bên trước khi yêu cầu gửi.",
                    },
                }
            if call.args.get("confirmed") is not True:
                return {
                    "tool": call.name,
                    "args": call.args,
                    "result": {
                        "status": "needs_confirmation",
                        "message": "Tool yêu cầu confirmed=true; chưa gửi tin.",
                    },
                }
        return execute_tool_call(call)

    turn = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=4,
            tool_executor=guarded_executor,
        )
        turn.update(result)
        history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": result["assistant_text"]},
        ])
    except Exception as exc:
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn["ended_at"] = now_iso()
    st.session_state.turns.append(turn)
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


st.session_state.setdefault("turns", [])
st.session_state.setdefault("history", [])

with st.sidebar:
    st.markdown("### Phiên làm việc")
    st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini", "ollama"], key="provider")
    st.text_input("Model override", placeholder="Để trống dùng model mặc định", key="model")
    st.text_input("Nhãn phiên bản", value="v0", key="version")
    allow_telegram = st.checkbox("Cho phép gửi Telegram trong phiên này", value=False)
    if allow_telegram:
        st.warning("Tin nhắn Telegram có thể được gửi thật. Chỉ bật khi bạn chủ động xác nhận yêu cầu gửi.")
    if st.session_state.get("conversation_config"):
        current = st.session_state.conversation_config
        st.caption(f"Phiên hiện tại: {current['provider']} · {current['version']}")
    if st.button("Cuộc trò chuyện mới", use_container_width=True):
        reset_conversation()
        st.rerun()

    transcript = st.session_state.get("transcript")
    if transcript:
        st.download_button(
            "Tải transcript JSON",
            data=json.dumps(transcript, ensure_ascii=False, indent=2),
            file_name=Path(st.session_state.transcript_path).name,
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"Đã lưu: {Path(st.session_state.transcript_path).relative_to(ROOT)}")

st.markdown('<div class="desk-kicker">Research Desk / Live Agent</div>', unsafe_allow_html=True)
st.title("Research, có bằng chứng.")
if st.session_state.get("conversation_config"):
    config = st.session_state.conversation_config
    st.caption(f"Đang dùng {config['provider']} · {config['version']}")
else:
    st.caption("Sẵn sàng cho phiên demo")

if not st.session_state.turns:
    st.markdown("#### Bắt đầu phiên nghiên cứu")
    st.caption("Ví dụ: tìm tin AI mới nhất; đọc URL và tóm tắt; hoặc hỏi về bài đăng của một tài khoản cụ thể.")

render_turns()

user_text = st.chat_input("Bạn muốn nghiên cứu điều gì?")
if user_text:
    with st.spinner("Agent đang xử lý yêu cầu và công cụ..."):
        save_turn(user_text, allow_telegram)
    st.rerun()