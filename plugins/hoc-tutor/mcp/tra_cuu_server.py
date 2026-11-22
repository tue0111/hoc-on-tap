#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP stdio server: tra cứu giáo trình (retrieval + _grok_pack).

Zero third-party deps. Protocol: JSON-RPC over stdin/stdout, one message per line.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SERVER_NAME = "hoc-tra-cuu"
SERVER_VERSION = "1.0.0"

COURSE_PACK = {
    "ke-toan-tai-chinh-1": "01_ke-toan-tai-chinh-1.md",
    "kttc1": "01_ke-toan-tai-chinh-1.md",
    "nguyen-ly-ke-toan": "02_nguyen-ly-ke-toan.md",
    "nlkt": "02_nguyen-ly-ke-toan.md",
    "ke-toan-tai-chinh-2": "03_ke-toan-tai-chinh-2.md",
    "kttc2": "03_ke-toan-tai-chinh-2.md",
    "ke-toan-chi-phi": "04_ke-toan-chi-phi.md",
    "ktcp": "04_ke-toan-chi-phi.md",
    "kiem-toan-1": "05_kiem-toan-1.md",
    "ke-toan-ngan-hang": "06_ke-toan-ngan-hang_p1.md",
    "ktnh": "06_ke-toan-ngan-hang_p1.md",
    "kinh-doanh-va-nghiep-vu": "07_kinh-doanh-va-nghiep-vu_p1.md",
    "luat-kinh-doanh": "08_luat-kinh-doanh.md",
    "ngan-hang-thuong-mai": "09_ngan-hang-thuong-mai.md",
    "nhtm": "09_ngan-hang-thuong-mai.md",
    "thi-truong-tai-chinh": "10_thi-truong-tai-chinh.md",
    "tttc": "10_thi-truong-tai-chinh.md",
    "tai-chinh-hanh-chinh-su-nghiep": "11_tai-chinh-hanh-chinh-su-nghiep_p1.md",
    "tchcsn": "11_tai-chinh-hanh-chinh-su-nghiep_p1.md",
    "tai-chinh-doanh-nghiep-1": "12_tai-chinh-doanh-nghiep-1.md",
    "tcdn1": "12_tai-chinh-doanh-nghiep-1.md",
    "van-ban-phap-quy": "17_van-ban-phap-quy.md",
    "he-thong-thong-tin-ke-toan-1": "18_he-thong-thong-tin-ke-toan-1.md",
    "htttkt1": "18_he-thong-thong-tin-ke-toan-1.md",
    "ke-toan-thue-1": "19_ke-toan-thue-1.md",
    "ktthue1": "19_ke-toan-thue-1.md",
    "ke-toan-tai-chinh-3": "20_ke-toan-tai-chinh-3.md",
    "kttc3": "20_ke-toan-tai-chinh-3.md",
    "ke-toan-hanh-chinh-su-nghiep": "21_ke-toan-hanh-chinh-su-nghiep_p1.md",
    "kthcsn": "21_ke-toan-hanh-chinh-su-nghiep_p1.md",
}


def hoc_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("HOC_ROOT")
    if env:
        return Path(env).resolve()
    # plugin lives at HOC_ROOT/plugins/hoc-tutor/mcp/this_file
    return Path(__file__).resolve().parents[3]


def pack_dir() -> Path:
    return hoc_root() / "_grok_pack"


def learning_dir() -> Path:
    return hoc_root() / "_learning_system"


def text_result(text: str, is_error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def tool_muc_luc() -> dict:
    path = pack_dir() / "00_MUC_LUC.md"
    if not path.exists():
        return text_result(f"Không thấy {path}", is_error=True)
    # Keep response bounded; full file is long
    lines = path.read_text(encoding="utf-8").splitlines()
    head = "\n".join(lines[:220])
    more = len(lines) - 220
    suffix = f"\n\n… còn {more} dòng. Đọc tiếp file: {path}" if more > 0 else ""
    return text_result(head + suffix)


def tool_danh_sach_mon() -> dict:
    rows = [
        "Alias course_id → file _grok_pack (dùng với tra_cuu / mo_pack):",
        "",
    ]
    seen = set()
    for alias, fname in COURSE_PACK.items():
        if fname in seen:
            continue
        seen.add(fname)
        rows.append(f"- {fname}  (vd. course=`{alias}`)")
    rows.append("")
    rows.append(f"HOC_ROOT={hoc_root()}")
    rows.append(f"_grok_pack={pack_dir()}")
    return text_result("\n".join(rows))


def tool_mo_pack(course: str, max_chars: int = 12000) -> dict:
    key = (course or "").strip().lower().replace(" ", "-")
    fname = COURSE_PACK.get(key)
    if not fname:
        # accept raw filename
        if course.endswith(".md"):
            fname = Path(course).name
        else:
            return text_result(
                f"Không map được môn `{course}`. Gọi danh_sach_mon hoặc muc_luc.",
                is_error=True,
            )
    path = pack_dir() / fname
    if not path.exists():
        # try p2 sibling note
        return text_result(f"Không thấy file pack: {path}", is_error=True)
    raw = path.read_text(encoding="utf-8")
    truncated = len(raw) > max_chars
    body = raw[:max_chars]
    note = f"\n\n[Đã cắt còn {max_chars}/{len(raw)} ký tự. File: {path}]" if truncated else f"\n\n[File: {path}]"
    return text_result(body + note)


def tool_tra_cuu(question: str, course: str | None = None, chapter: int | None = None) -> dict:
    ls = learning_dir()
    if not (ls / "retrieval").exists():
        return text_result(
            f"Không thấy learning system tại {ls}. Hãy mở repo hoc-on-tap làm project root.",
            is_error=True,
        )
    cmd = [sys.executable, "-m", "retrieval.cli", "retrieve", question, "--json"]
    if course:
        cmd.extend(["--course", course])
    if chapter is not None:
        cmd.extend(["--chapter", str(chapter)])
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ls),
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONPATH": str(ls)},
        )
    except Exception as exc:  # noqa: BLE001
        return text_result(f"Lỗi chạy retrieval: {exc}", is_error=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
        return text_result(f"Retrieval thất bại:\n{err}", is_error=True)
    out = (proc.stdout or "").strip()
    if not out:
        return text_result("Retrieval không trả về dữ liệu.", is_error=True)
    return text_result(out)


TOOLS = [
    {
        "name": "muc_luc",
        "description": "Đọc mục lục _grok_pack (00_MUC_LUC.md) để biết môn → file nào.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "danh_sach_mon",
        "description": "Liệt kê alias course_id và file pack tương ứng để tra/học.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "mo_pack",
        "description": "Mở (đọc) file _grok_pack của một môn để học/tra cứu trong session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "course": {
                    "type": "string",
                    "description": "course_id hoặc alias (vd. kttc1, ke-toan-thue-1) hoặc tên file .md",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Giới hạn ký tự trả về (mặc định 12000)",
                    "default": 12000,
                },
            },
            "required": ["course"],
            "additionalProperties": False,
        },
    },
    {
        "name": "tra_cuu",
        "description": "Tra cứu hybrid trong _learning_system (giáo trình đã index). Ưu tiên khi hỏi khái niệm / hạch toán / tìm chương.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Câu hỏi cần tra"},
                "course": {
                    "type": "string",
                    "description": "course_id (vd. ke-toan-tai-chinh-1, nguyen-ly-ke-toan)",
                },
                "chapter": {"type": "integer", "description": "Số chương nếu biết"},
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
]


def call_tool(name: str, arguments: dict | None) -> dict:
    args = arguments or {}
    if name == "muc_luc":
        return tool_muc_luc()
    if name == "danh_sach_mon":
        return tool_danh_sach_mon()
    if name == "mo_pack":
        return tool_mo_pack(str(args.get("course") or ""), int(args.get("max_chars") or 12000))
    if name == "tra_cuu":
        chapter = args.get("chapter")
        return tool_tra_cuu(
            str(args.get("question") or ""),
            course=(str(args["course"]) if args.get("course") else None),
            chapter=(int(chapter) if chapter is not None else None),
        )
    return text_result(f"Unknown tool: {name}", is_error=True)


def respond(msg_id, result=None, error=None) -> None:
    payload: dict = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg: dict) -> None:
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params") or {}

    # Notifications (no id)
    if msg_id is None:
        return

    if method == "initialize":
        respond(
            msg_id,
            {
                "protocolVersion": params.get("protocolVersion") or "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
        return

    if method == "ping":
        respond(msg_id, {})
        return

    if method == "tools/list":
        respond(msg_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        name = params.get("name") or ""
        arguments = params.get("arguments") or {}
        respond(msg_id, call_tool(name, arguments))
        return

    respond(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        handle(msg)


if __name__ == "__main__":
    main()
