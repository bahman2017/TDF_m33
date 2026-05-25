"""Phase 6D: bibliography verification, LaTeX compile readiness, polish audit."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from tdf_m33.reporting.phase6c_manuscript_draft_audit import (
    REQUIRED_METRIC_SNIPPETS,
    audit_phase6c_draft,
)
from tdf_m33.reporting.phase6b_manuscript_audit import (
    MANUSCRIPT_TEX,
    _affirmative_forbidden,
    _read,
)

BIB_VERIFICATION_MD = "docs/manuscript_bibliography_verification.md"
POLISH_REPORT_MD = "outputs/reports/phase6d_manuscript_polish_audit.md"
PAPER_DIR = "paper"
TEX_BASENAME = "m33_tdf_tau_geometry_draft.tex"

VERIFIED_CITATION_KEYS = ("Corbelli2014", "LopezFune2017")
VERIFIED_DOIS = (
    "10.1051/0004-6361/201424033",
    "10.1093/mnras/stx2742",
)

FORBIDDEN_BIB_MARKERS = (
    "placeholder; verify",
    "placeholder; verify bibliographic",
)


def _extract_bibliography(tex: str) -> str:
    if r"\begin{thebibliography}" not in tex:
        return ""
    return tex.split(r"\begin{thebibliography}")[-1].split(r"\end{thebibliography}")[0]


def _count_open_todos(tex: str) -> int:
    bib = _extract_bibliography(tex)
    return len(re.findall(r"%\s*TODO", bib, flags=re.IGNORECASE))


def _try_latex_compile(repo: Path) -> dict[str, str]:
    paper = repo / PAPER_DIR
    tex = paper / TEX_BASENAME
    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")

    if not tex.is_file():
        return {"status": "fail", "detail": f"missing {tex}"}
    if not latexmk and not pdflatex:
        return {
            "status": "skipped",
            "detail": "latexmk and pdflatex not found on PATH; static LaTeX check only",
        }

    pdf = paper / TEX_BASENAME.replace(".tex", ".pdf")
    log_parts: list[str] = []
    try:
        if latexmk:
            subprocess.run(
                ["latexmk", "-C"],
                cwd=paper,
                capture_output=True,
                text=True,
                timeout=30,
            )
            proc = subprocess.run(
                [
                    "latexmk",
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-f",
                    TEX_BASENAME,
                ],
                cwd=paper,
                capture_output=True,
                text=True,
                timeout=180,
            )
            log_parts.append(proc.stdout + proc.stderr)
        else:
            for _ in range(2):
                proc = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", TEX_BASENAME],
                    cwd=paper,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                log_parts.append(proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        return {"status": "fail", "detail": "LaTeX compile timed out"}

    ok = pdf.is_file() and pdf.stat().st_size > 10_000
    tail = "\n".join(log_parts)[-2000:]
    rc = proc.returncode if "proc" in dir() else -1
    return {
        "status": "pass" if ok else "fail",
        "detail": f"latexmk/pdflatex returncode={rc}; pdf_exists={pdf.is_file()}",
        "pdf": str(pdf.resolve()) if ok else "",
        "log_tail": tail,
    }


def audit_phase6d_polish(repo: Path) -> tuple[list[str], dict[str, str]]:
    errors = list(audit_phase6c_draft(repo))

    if not (repo / BIB_VERIFICATION_MD).is_file():
        errors.append(f"missing {BIB_VERIFICATION_MD}")

    tex_raw = _read(repo, MANUSCRIPT_TEX)
    bib = _extract_bibliography(tex_raw)

    for key in VERIFIED_CITATION_KEYS:
        if key not in tex_raw:
            errors.append(f"missing citation key {key!r}")

    for doi in VERIFIED_DOIS:
        if doi not in tex_raw:
            errors.append(f"missing verified DOI {doi!r}")

    for marker in FORBIDDEN_BIB_MARKERS:
        if marker.lower() in bib.lower():
            errors.append(f"bibliography still contains {marker!r}")

    if _count_open_todos(tex_raw) > 0:
        errors.append("bibliography section still has TODO comments")

    if "verified" not in _read(repo, BIB_VERIFICATION_MD).lower():
        errors.append(f"{BIB_VERIFICATION_MD} missing verified status")

    # No new numerical claims: metrics from Phase 6C must remain
    for metric in REQUIRED_METRIC_SNIPPETS:
        if metric not in tex_raw:
            errors.append(f"metric removed from manuscript (no new science): {metric!r}")

    compile_info = _try_latex_compile(repo)
    if compile_info["status"] == "fail":
        errors.append(f"LaTeX compile failed: {compile_info.get('detail', '')}")

    return errors, compile_info


def write_polish_report(
    repo: Path,
    errors: list[str],
    compile_info: dict[str, str],
) -> None:
    report_path = repo / POLISH_REPORT_MD
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if not errors else "FAIL"
    lines = [
        "# Phase 6D — Manuscript polish audit",
        "",
        f"**Overall:** {status}",
        "",
        "## Bibliography",
        "",
        f"- Verification doc: `{BIB_VERIFICATION_MD}`",
        f"- Keys verified: {', '.join(VERIFIED_CITATION_KEYS)}",
        f"- DOIs in manuscript: {', '.join(VERIFIED_DOIS)}",
        "",
        "## LaTeX compile",
        "",
        f"- Status: **{compile_info.get('status', 'unknown')}**",
        f"- Detail: {compile_info.get('detail', '')}",
    ]
    if compile_info.get("pdf"):
        lines.append(f"- PDF: `{compile_info['pdf']}`")
    if compile_info.get("status") == "skipped":
        lines.append(
            "- Static checks only (install MacTeX/TeX Live for PDF build)."
        )
    if compile_info.get("log_tail") and compile_info.get("status") != "pass":
        lines.append("")
        lines.append("### Log tail")
        lines.append("```")
        lines.append(compile_info["log_tail"][-1500:])
        lines.append("```")

    lines.extend(
        [
            "",
            "## Claim control",
            "",
            "- Phase 6C draft metrics and caveats re-checked.",
            "- Prohibited affirmative claims must remain absent.",
            "",
            "## Issues",
            "",
        ]
    )
    if errors:
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Remaining before submission",
            "",
            "1. Journal template and author/affiliation block.",
            "2. Copy figures into `paper/figures/` if desired (optional; `\\includefig` works).",
            "3. Add further citations only with manifest/verification entries.",
            "4. Uncertainty propagation (not in current pipeline).",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_phase6d_manuscript_polish_audit(repo: Path | None = None) -> tuple[list[str], dict[str, str]]:
    if repo is None:
        repo = Path(__file__).resolve().parents[3]
    errors, compile_info = audit_phase6d_polish(repo)
    write_polish_report(repo, errors, compile_info)
    return errors, compile_info
