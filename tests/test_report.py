"""The technical report's and the README's citations open.

Every citation of the forms `` `path`, line N ``, `` `path`, lines N to M ``, `` `path`, lines N, M, and K `` (and the same
with the line numbers in parentheses after the path, or after "docstring") must name a file of this repository with at
least the largest line it cites. A name given without its folder (`lead_tables.txt`, `rehearsal_2/rehearsal.json`) is
the file at the root if one has that name, else the nearest earlier full path in the same document that ends with it,
else the one tracked file that does. Every
backticked path under results/, freeze/, provenance/, data/, vpd_audit_2/, tests/ and third_party/ must exist; the
third_party/ ones need the submodule checked out (clone with --recurse-submodules). Line references with no file
before them, such as "(line 22)", are not checked here.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = ("REPORT.md", "README.md")
ROOTS = ("results/", "freeze/", "provenance/", "data/", "vpd_audit_2/", "tests/", "third_party/")
NUMBERS = r"\d+(?:(?:,\s*and|,|\s+and|\s+to)\s+\d+)*"
CITATION = re.compile(r"`([^`\s]+)`(?: docstring)?(?:, | \()lines? (" + NUMBERS + ")")
FULL_PATH = re.compile(r"`((?:results|freeze|provenance|data|vpd_audit_2|tests|third_party)/[^`\s]*)`")
SUBMODULE = ROOT / "third_party" / "vpd-audit"


def _tracked() -> list[str]:
    """The repository's tracked files, relative to its root (this folder)."""
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout
    return out.split("\n")[:-1]


def _resolve(name: str, before: str, tracked: list[str]) -> str | None:
    """The file a cited name stands for, or None if no single file does. A tracked file at the root (`README.md`) is
    itself."""
    if name.startswith(ROOTS) or name in tracked:
        return name
    earlier = [p for p in FULL_PATH.findall(before) if p.endswith("/" + name)]
    if earlier:
        return earlier[-1]
    candidates = [f for f in tracked if f == name or f.endswith("/" + name)]
    return candidates[0] if len(candidates) == 1 else None


def _citations(doc: str) -> list[tuple[str, str | None, int, int]]:
    """(cited name, resolved path, largest line cited, the document's line) for every citation in `doc`."""
    text = (ROOT / doc).read_text()
    tracked = _tracked()
    return [(m.group(1), _resolve(m.group(1), text[: m.start()], tracked), max(int(n) for n in re.findall(r"\d+", m.group(2))),
             text.count("\n", 0, m.start()) + 1) for m in CITATION.finditer(text)]


def _submodule_checked_out() -> bool:
    return SUBMODULE.is_dir() and any(SUBMODULE.iterdir())


@pytest.mark.parametrize("doc", DOCS)
def test_every_line_citation_opens(doc):
    citations = _citations(doc)
    failures = []
    for name, path, largest, at in citations:
        if path is None:
            failures.append(f"{doc}, line {at}: `{name}` names no single file")
            continue
        if path.startswith("third_party/") and not _submodule_checked_out():
            continue
        file = ROOT / path
        if not file.is_file():
            failures.append(f"{doc}, line {at}: `{name}` ({path}) is not a file")
            continue
        n = len(file.read_text(errors="replace").splitlines())
        if n < largest:
            failures.append(f"{doc}, line {at}: `{name}` ({path}) has {n} lines; line {largest} is cited")
    print(f"{doc}: {len(citations)} line citations checked")
    assert citations and not failures, "\n".join(failures)


@pytest.mark.parametrize("doc", DOCS)
def test_every_backticked_path_exists(doc):
    paths = sorted({p for p in FULL_PATH.findall((ROOT / doc).read_text())
                    if not p.startswith("third_party/") and "<" not in p and "*" not in p})
    missing = [p for p in paths if not (ROOT / p).exists()]
    print(f"{doc}: {len(paths)} backticked paths checked")
    assert paths and not missing, f"{doc}: missing {missing}"


@pytest.mark.parametrize("doc", DOCS)
def test_every_backticked_third_party_path_exists(doc):
    if not _submodule_checked_out():
        pytest.skip("the submodule third_party/vpd-audit is not checked out (clone with --recurse-submodules)")
    paths = sorted({p for p in FULL_PATH.findall((ROOT / doc).read_text()) if p.startswith("third_party/")})
    missing = [p for p in paths if not (ROOT / p).exists()]
    print(f"{doc}: {len(paths)} backticked third_party paths checked")
    assert not missing, f"{doc}: missing {missing}"
