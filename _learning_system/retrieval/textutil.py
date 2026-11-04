# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
import re
import unicodedata

STOP = frozenset(
    """
    và của các là được trong với cho một những này đó từ về đến khi hoặc như trên
    để có không phải thì sẽ đã tại vào ra lên xuống cũng hơn rất nữa sau trước
    theo bằng bị do nên vì nếu mà còn đang được những kẻ người anh chị học
    môn bài chúng ta tôi xin chào nội dung slide chương chủ đề phần
    """.split()
)

TOKEN_RE = re.compile(r"[0-9a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", re.I)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def fold(s: str) -> str:
    s = nfc(s).lower()
    return s


def tokenize(text: str) -> list[str]:
    toks = TOKEN_RE.findall(fold(text))
    out = []
    for t in toks:
        if len(t) <= 1:
            continue
        if t in STOP:
            continue
        out.append(t)
    return out


def content_hash(text: str) -> str:
    return hashlib.sha256(nfc(text).encode("utf-8")).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
