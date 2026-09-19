"""Authoritative Qalam release pointer tests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ada_reliability.qalam_release import component_version, load_release, loading_plan


def test_release_json_is_authoritative():
    rel = load_release()
    assert component_version(rel, "qalam-router") == "1.1.0"
    assert component_version(rel, "art-of-writing-bible") == "2.0.0"
    assert component_version(rel, "art-of-writing-bible-evals") == "1.3.0"
    evals = rel["components"]["art-of-writing-bible-evals"]
    assert evals["validates"] == "art-of-writing-bible@2.0.0"
    assert rel["overlays"]["ux-writing-fa-ir"].endswith("fa-ir-overlays/ux-writing-fa-ir.md")


def test_loading_plan_is_deterministic_and_not_single_overlay():
    plan = loading_plan("ux_copy")
    names = [a["name"] for a in plan["assets"]]
    assert "qalam-router" in names
    assert "art-of-writing-bible" in names
    assert "ux-writing-fa-ir" in names
    assert "fa-ir-product-lexicon" in names
    assert "register-atlas.md" in names
    assert plan["router_version"] == "1.1.0"
    assert plan["bible_version"] == "2.0.0"
    assert plan["eval_pack_version"] == "1.3.0"


def test_docs_do_not_claim_1_4_0_is_current():
    root = Path(load_release()["_root"])
    readme = (root / "skills/qalam/AGENTS-WRITING-README.md").read_text(encoding="utf-8")
    runtime = (root / "skills/qalam/router/RUNTIME-INTEGRATION.md").read_text(encoding="utf-8")
    skill = (root / "skills/qalam/router/SKILL.md").read_text(encoding="utf-8")
    assert "RELEASE.json" in readme
    assert "Do not set `QALAM_CANONICAL_VERSION=1.4.0`" in runtime
    assert "- `QALAM_CANONICAL_VERSION=1.4.0`" not in runtime
    stale = "writing/art-of-writing-bible/references/fa-ir-product-lexicon.md"
    assert stale not in skill
    assert "skills/qalam/fa-ir-overlays/fa-ir-product-lexicon.md" in skill
    rel = load_release()
    for path in rel["overlays"].values():
        assert (root / path).is_file(), path

