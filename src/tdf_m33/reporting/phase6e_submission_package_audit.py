"""Phase 6E: journal-neutral submission package audit."""

from __future__ import annotations

from pathlib import Path

from tdf_m33.reporting.phase6b_manuscript_audit import (
    MANUSCRIPT_TEX,
    REQUIRED_CAVEAT_GROUPS,
    _affirmative_forbidden,
    _read,
)
from tdf_m33.reporting.phase6c_manuscript_draft_audit import (
    REQUIRED_METRIC_SNIPPETS,
    audit_phase6c_draft,
)
from tdf_m33.reporting.phase6d_manuscript_polish_audit import (
    BIB_VERIFICATION_MD,
    POLISH_REPORT_MD,
    _try_latex_compile,
)

SUBMISSION_CHECKLIST_MD = "docs/manuscript_submission_checklist.md"
SUBMISSION_REPORT_MD = "outputs/reports/phase6e_submission_package_audit.md"
PREPARE_FIGURES_SCRIPT = "scripts/prepare_paper_figures.py"

REQUIRED_PACKAGED_FIGURES = (
    "fig1_rotation_baryonic.png",
    "fig2_model_comparison.png",
    "fig3_tau_gradient.png",
    "fig4_tau_map_disk.png",
    "fig4_tau_map_sky.png",
    "fig5_deflection_proxy.png",
)
OPTIONAL_PACKAGED_FIGURES = ("fig4_tau_map.png",)

REQUIRED_TEX_SECTIONS = (
    "acknowledgments",
    "data and code availability",
    "conflict of interest",
    "funding",
)


def audit_submission_package(repo: Path) -> tuple[list[str], dict]:
    errors = list(audit_phase6c_draft(repo))

    for rel in (
        MANUSCRIPT_TEX,
        BIB_VERIFICATION_MD,
        SUBMISSION_CHECKLIST_MD,
        PREPARE_FIGURES_SCRIPT,
    ):
        if not (repo / rel).is_file():
            errors.append(f"missing required file: {rel}")

    tex_raw = _read(repo, MANUSCRIPT_TEX)
    tex = tex_raw.lower()

    for sec in REQUIRED_TEX_SECTIONS:
        if sec not in tex:
            errors.append(f"manuscript missing section: {sec!r}")

    if "[author" not in tex_raw.lower() and "todo" not in tex:
        errors.append("manuscript missing author TODO block")

    for metric in REQUIRED_METRIC_SNIPPETS:
        if metric not in tex_raw:
            errors.append(f"metric missing: {metric!r}")

    for group in REQUIRED_CAVEAT_GROUPS:
        if not any(alt.lower() in tex for alt in group):
            errors.append(f"missing caveat group: {group!r}")

    for phrase in (
        "tdf replaces dark matter",
        "lensing is confirmed",
        "m33 proves tdf",
    ):
        if _affirmative_forbidden(tex_raw, phrase):
            errors.append(f"prohibited phrase: {phrase!r}")

    figures_dir = repo / "paper" / "figures"
    figure_status: dict[str, str] = {}
    readme = figures_dir / "README.md"
    if readme.is_file():
        for name in REQUIRED_PACKAGED_FIGURES:
            figure_status[name] = "present" if (figures_dir / name).is_file() else "missing"
            if figure_status[name] == "missing":
                errors.append(f"packaged figure missing: {name}")
        for name in OPTIONAL_PACKAGED_FIGURES:
            figure_status[name] = (
                "present" if (figures_dir / name).is_file() else "optional (not packaged)"
            )
    elif figures_dir.is_dir():
        figure_status["packaging"] = "incomplete — missing paper/figures/README.md"
    else:
        figure_status["packaging"] = "optional — run prepare_paper_figures.py"

    compile_info = _try_latex_compile(repo)
    if compile_info["status"] == "fail":
        errors.append(f"LaTeX compile failed: {compile_info.get('detail', '')}")

    meta = {
        "compile": compile_info,
        "latex_documented_in": POLISH_REPORT_MD if (repo / POLISH_REPORT_MD).is_file() else "",
        "figure_status": figure_status,
    }
    return errors, meta


def write_submission_report(repo: Path, errors: list[str], meta: dict) -> None:
    path = repo / SUBMISSION_REPORT_MD
    path.parent.mkdir(parents=True, exist_ok=True)
    compile_info = meta.get("compile", {})
    if not isinstance(compile_info, dict):
        compile_info = {}

    lines = [
        "# Phase 6E — Submission package audit",
        "",
        f"**Overall:** {'PASS' if not errors else 'FAIL'}",
        "",
        "## Packaging artifacts",
        "",
        f"- `{MANUSCRIPT_TEX}`",
        f"- `{SUBMISSION_CHECKLIST_MD}`",
        f"- `{PREPARE_FIGURES_SCRIPT}`",
        "",
        "## LaTeX compile",
        "",
        f"- Status: **{compile_info.get('status', 'unknown')}**",
        f"- Detail: {compile_info.get('detail', '')}",
        f"- Phase 6D report: `{meta.get('latex_documented_in', POLISH_REPORT_MD)}`",
    ]
    if compile_info.get("pdf"):
        lines.append(f"- PDF (local): `{compile_info['pdf']}`")

    fig_status = meta.get("figure_status", {})
    if fig_status:
        lines.append("")
        lines.append("## Figure packaging")
        for k, v in sorted(fig_status.items()):
            lines.append(f"- `{k}`: {v}")

    lines.extend(["", "## Issues", ""])
    lines.extend(f"- {e}" for e in errors) if errors else lines.append("- None.")

    lines.extend(
        [
            "",
            "## Journal TODOs",
            "",
            "Template selection, author block, funding/COI, overfull boxes.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_phase6e_submission_package_audit(repo: Path | None = None) -> tuple[list[str], dict]:
    if repo is None:
        repo = Path(__file__).resolve().parents[3]
    errors, meta = audit_submission_package(repo)
    write_submission_report(repo, errors, meta)
    return errors, meta
