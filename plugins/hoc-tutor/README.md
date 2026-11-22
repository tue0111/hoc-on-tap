# hoc-tutor — Plugin Claude Code

Nạp giáo trình kế toán / tài chính / ngân hàng từ repo `hoc-on-tap` vào Claude Code.

## Cài đặt (từ GitHub)

Trong terminal (đã cài Claude Code và đang đứng ngoài hoặc trong repo):

```bash
claude plugin marketplace add tue0111/hoc-on-tap
claude plugin install hoc-tutor@hoc-on-tap
```

## Cài đặt (local / đang clone repo)

```bash
cd /đường/dẫn/hoc-on-tap
claude plugin marketplace add .
claude plugin install hoc-tutor@hoc-on-tap
```

Hoặc chỉ load tạm một session, không cần marketplace:

```bash
claude --plugin-dir ./plugins/hoc-tutor
```

Sau khi sửa skill trong plugin, trong session chạy `/reload-plugins`.

## Dùng nhanh

| Lệnh | Việc |
|---|---|
| `/hoc-tutor:nap-giao-trinh` | Nạp đúng file `_grok_pack` theo môn |
| `/hoc-tutor:tutor-hoc` | Bật luật tutor (giáo trình trước, trích nguồn) |
| `/hoc-tutor:study` | Ôn / nộp bài (NLKT, KTTC1 ưu tiên CLI) |
| `@agent-hoc-tutor:learning-director` | Ủy thác Learning Director |

Ví dụ: `/hoc-tutor:nap-giao-trinh Kế toán thuế 1` rồi hỏi bài.

## Cấu trúc

```
plugins/hoc-tutor/
  .claude-plugin/plugin.json
  agents/learning-director.md
  skills/
    nap-giao-trinh/     # nạp _grok_pack
    tutor-hoc/          # persona + luật trả lời
    study/ …            # port từ _learning_system/.grok/skills
```

Marketplace của repo: `.claude-plugin/marketplace.json`.

## HOC_ROOT

Mọi skill dùng `HOC_ROOT` = thư mục gốc repo (có `_grok_pack/`, `_learning_system/`). Trên máy Tuệ thường là `D:\Hoc`.
