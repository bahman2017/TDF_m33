"""Scan text files for hidden/bidirectional Unicode control characters."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Explicit bidi / invisible controls (not normal punctuation or symbols).
FORBIDDEN_CODEPOINTS: frozenset[int] = frozenset(
    list(range(0x202A, 0x202F))  # U+202A..U+202E
    + list(range(0x2066, 0x206A))  # U+2066..U+2069
    + [
        0x200E,  # LEFT-TO-RIGHT MARK
        0x200F,  # RIGHT-TO-LEFT MARK
        0x200B,  # ZERO WIDTH SPACE
        0x200C,  # ZERO WIDTH NON-JOINER
        0x200D,  # ZERO WIDTH JOINER
        0xFEFF,  # BOM / ZWNBSP
    ]
)

SCAN_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".md", ".yaml", ".yml", ".csv", ".txt", ".sha256"}
)

SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"}
)


@dataclass(frozen=True)
class UnicodeIssue:
    path: Path
    line: int
    column: int
    codepoint: int

    @property
    def name(self) -> str:
        return unicodedata.name(chr(self.codepoint), "UNKNOWN")


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        files.append(path)
    return sorted(files)


def scan_text_file(path: Path) -> list[UnicodeIssue]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return [
            UnicodeIssue(path=path, line=1, column=1, codepoint=0xFEFF),
        ]
    text = raw.decode("utf-8")
    issues: list[UnicodeIssue] = []
    line_no = 1
    col = 1
    for ch in text:
        if ch == "\n":
            line_no += 1
            col = 1
            continue
        cp = ord(ch)
        if cp in FORBIDDEN_CODEPOINTS:
            issues.append(
                UnicodeIssue(path=path, line=line_no, column=col, codepoint=cp)
            )
        col += 1
    return issues


def scan_repository(root: Path) -> list[UnicodeIssue]:
    issues: list[UnicodeIssue] = []
    for path in iter_text_files(root):
        issues.extend(scan_text_file(path))
    return issues


def normalize_text_content(text: str) -> str:
    """Remove forbidden controls; normalize CRLF to LF."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(ch for ch in text if ord(ch) not in FORBIDDEN_CODEPOINTS)


def normalize_text_file(path: Path) -> bool:
    """Normalize a file in place. Returns True if modified."""
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8")
    normalized = normalize_text_content(text.lstrip("\ufeff"))
    if not had_bom and normalized == text and b"\r" not in raw:
        return False
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return True
