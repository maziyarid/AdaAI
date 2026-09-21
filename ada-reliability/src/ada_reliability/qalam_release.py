"""Single authoritative Qalam/Bible/eval release pointer.

Runtime behaviour, documentation, eval selection and receipt generation
must read this module (backed by skills/qalam/RELEASE.json). Do not
hard-code a "current" version in worker docs.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


WRITING_TASK_TYPES = {
    "academic_content", "content_refresh", "writing", "ux_copy",
    "metadata_refresh", "service_page", "medical_copy",
}

PROFILE_OVERLAYS = {
    "academic_content": [],
    "content_refresh": [],
    "writing": [],
    "metadata_refresh": [],
    "ux_copy": ["ux-writing-fa-ir", "fa-ir-product-lexicon", "tool-routing"],
    "service_page": ["ux-writing-fa-ir", "fa-ir-product-lexicon"],
    "medical_copy": ["persian-medical-human-writing"],
}


def repo_root(start: Optional[Path] = None) -> Optional[Path]:
    here = (start or Path(__file__)).resolve()
    for p in [here, *here.parents]:
        if (p / "skills" / "qalam" / "REGISTRY.json").exists():
            return p
    return None


def load_release(root: Optional[Path] = None) -> dict[str, Any]:
    base = root or repo_root()
    if base is None:
        raise FileNotFoundError("Ada repo root with skills/qalam/REGISTRY.json not found")
    release_path = base / "skills" / "qalam" / "RELEASE.json"
    if not release_path.is_file():
        raise FileNotFoundError(f"missing authoritative release pointer: {release_path}")
    data = json.loads(release_path.read_text(encoding="utf-8"))
    data["_path"] = str(release_path)
    data["_root"] = str(base)
    return data


def component_version(release: dict[str, Any], component: str) -> str:
    rec = (release.get("components") or {}).get(component) or {}
    version = rec.get("version")
    if not version:
        raise KeyError(f"RELEASE.json has no version for {component}")
    return version


def loading_plan(task_type: str, *, locale: str = "fa-IR",
                 release: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Deterministic load list.

    'Load only the needed overlay' means: do not load unrelated *profiles*.
    It does not authorize skipping the router, the Bible, or overlays listed
    for the selected profile. Bible companion files listed in the Bible
    skill remain mandatory whenever the Bible is loaded.
    """
    rel = release or load_release()
    always = ["qalam-router", "art-of-writing-bible"] if task_type in WRITING_TASK_TYPES else ["qalam-router"]
    overlays = list(PROFILE_OVERLAYS.get(task_type, []))
    if locale == "fa-IR" and task_type in ("ux_copy", "service_page"):
        if "ux-writing-fa-ir" not in overlays:
            overlays.append("ux-writing-fa-ir")
    bible_companions = list((rel.get("loading") or {}).get("bible_companions") or [])
    assets = []
    components = rel.get("components") or {}
    overlay_paths = rel.get("overlays") or {}
    for name in always:
        rec = components.get(name) or {}
        assets.append({
            "name": name,
            "role": rec.get("role", name),
            "version": rec.get("version"),
            "path": rec.get("path"),
            "required": True,
        })
    if "art-of-writing-bible" in always:
        for path in bible_companions:
            assets.append({
                "name": Path(path).name,
                "role": "bible-companion",
                "version": component_version(rel, "art-of-writing-bible"),
                "path": path,
                "required": True,
            })
    for name in overlays:
        path = overlay_paths.get(name) or ((components.get(name) or {}).get("path"))
        assets.append({
            "name": name,
            "role": "overlay",
            "version": (components.get(name) or {}).get("version") or component_version(rel, "art-of-writing-bible"),
            "path": path,
            "required": True,
        })
    return {
        "task_type": task_type,
        "locale": locale,
        "router_version": component_version(rel, "qalam-router"),
        "bible_version": component_version(rel, "art-of-writing-bible"),
        "eval_pack_version": component_version(rel, "art-of-writing-bible-evals"),
        "eval_pack_validates": ((rel.get("components") or {}).get("art-of-writing-bible-evals") or {}).get("validates"),
        "assets": assets,
        "rule": (rel.get("loading") or {}).get("rule"),
    }
