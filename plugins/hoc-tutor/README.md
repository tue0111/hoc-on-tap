# hoc-tutor — Plugin Claude Code

Nạp giáo trình để **tra cứu và học** trong Claude Code (repo `hoc-on-tap`).

## Cài đặt

```bash
claude plugin marketplace add tue0111/hoc-on-tap
claude plugin install hoc-tutor@hoc-on-tap
```

Local / clone:

```bash
cd /đường/dẫn/hoc-on-tap
claude plugin marketplace add .
claude plugin install hoc-tutor@hoc-on-tap
# hoặc một session:
claude --plugin-dir ./plugins/hoc-tutor
```

Mở Claude Code **trong thư mục repo** (để `CLAUDE_PROJECT_DIR` trỏ đúng `HOC_ROOT`). Cần `python3` và `npx` (Node).

Sau khi sửa plugin: `/reload-plugins`. Kiểm MCP: `/mcp`.

## MCP (tra + học)

Plugin bật 2 server khi enable:

| Server | Việc |
|---|---|
| **hoc-tra-cuu** | `muc_luc`, `danh_sach_mon`, `mo_pack`, `tra_cuu` — mục lục, mở pack môn, tra hybrid index |
| **giao-trinh-files** | Filesystem **read-only** trên `_grok_pack/` |

Luồng học điển hình: `muc_luc` → `mo_pack` (môn) → hỏi bài → `tra_cuu` khi cần bằng chứng index.

## Slash / agent

| Lệnh | Việc |
|---|---|
| `/hoc-tutor:nap-giao-trinh` | Nạp đúng môn (ưu tiên MCP) |
| `/hoc-tutor:tutor-hoc` | Luật tutor |
| `/hoc-tutor:study` | Ôn / nộp bài |
| `@agent-hoc-tutor:learning-director` | Learning Director |

## Cấu trúc

```
plugins/hoc-tutor/
  .claude-plugin/plugin.json
  .mcp.json                 # MCP servers
  mcp/tra_cuu_server.py     # tra_cuu / mo_pack / muc_luc
  agents/learning-director.md
  skills/…
```

## HOC_ROOT

Repo root có `_grok_pack/` và `_learning_system/`. Máy Tuệ thường: `D:\Hoc`.
