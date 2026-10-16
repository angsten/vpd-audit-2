"""Plan 1 of the research log, Part A: the signed rules, Amendment 1, and its three binding specifications, pinned.

`freeze/` holds copies of the rules the lead experiment is read under:

  - `part1.md`: the freeze file, Part 1, signed by the author (`freeze/part1.md`);
  - `amendment1.md`: Amendment 1 (`freeze/amendment1.md`);
  - `amendment1_specs/`: the interval specification, the output and reading specification, and the table and run
    specification, with their errata (`freeze/amendment1_specs/`);
  - `amendment2.md`: Amendment 2 (`freeze/amendment2.md`), added in a commit of its own;
  - `amendment3.md`: Amendment 3 (`freeze/amendment3.md`), with the multipliers file that Amendment 1's
    Section 5.6 provides for, `amendment1_multipliers.md`, and its machine-readable copy, `amendment1_multipliers.json`
    (`freeze/amendment1_multipliers.{md,json}`), added together in a commit of their own;
  - `amendment4.md`: Amendment 4 (`freeze/amendment4.md`), added in a commit of its own.

Each file's SHA-256 is a constant here, taken when the copies were made. A change to any byte of any of these files
fails this test. The constants were regenerated once, on 15 October 2026, for a wording-only change made on its own
branch: the freeze files were reworded for publication after the runs, and only wording changed, which the reviewed
diff shows. Apart from that, a change to the rules is a new dated file beside these, not an edit.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

FREEZE_DIR = Path(__file__).resolve().parent.parent / "freeze"

PINNED = {
    "part1.md": "42cceb14044a71e3938b8038a003b14a33444bfcc6e7133904200d8e839924d3",
    "amendment1.md": "0d6273d87aebf011828d15805b1711b223d89b328f7b3eec72576e18158006e6",
    "amendment1_specs/interval_spec.md": "f58f543b6d7b8db9a9ee0441f0af16bf758db79a8f5d1cccb60527b4d5a7255c",
    "amendment1_specs/interval_spec_erratum.md": "474d753720c7956edc2ca7a4277f7aeb614c916a199692b3916c8c51d4243fd6",
    "amendment1_specs/output_and_reading_spec.md": "1f9d6c0eb24974865e5774e0f1612106022c7e603c1dbd681f22bc0af393b4be",
    "amendment1_specs/table_and_run_spec.md": "780eda5bbad5af5e1bca758d0eb9c01934f2cd450bdf11078961c39030e2c035",
    "amendment1_specs/table_and_run_spec_erratum.md": "6794afc27617a41eb7ec77eb7e891cc146d5e2ea119ded57898ef3628a505aad",
    # Amendment 2 (`freeze/amendment2.md`), committed alone before either version of the made-up-data
    # test of record ran (plan 3 of the research log, step 1). The seven pins above were as Part A committed them.
    "amendment2.md": "c00aa684a85ae99b31cc03078ded9c838f62a9f51852bc3bd57e90daf09c4ff4",
    # Amendment 3 and the multipliers file with its machine-readable copy, committed together and alone, after the
    # made-up-data test of record and before any deciding run. The eight pins above were unchanged.
    "amendment3.md": "df1debf599735d1060bd259cc1fa7a32150476275bcb32cb1c14459c4e50c8e3",
    "amendment1_multipliers.md": "145e918f310f08563177614352f7942e7040e71ae8556a71e0503f526635b5de",
    "amendment1_multipliers.json": "f178811ccd2a4b1eff8c5d60f8f2b52533f27186de718703eea57c6fbf8c6f75",
    # Amendment 4 (`freeze/amendment4.md`): the author's cap of $150 and how spend is counted against it,
    # committed alone, after the first rehearsal and before any deciding run. The eleven pins above were unchanged.
    "amendment4.md": "ab1ac58a931f7dcf6e43599274522cd95fd351c70ffe6a8d6d223d852f80879b",
}


@pytest.mark.parametrize("name", sorted(PINNED))
def test_frozen_file_is_unchanged(name: str) -> None:
    path = FREEZE_DIR / name
    assert path.is_file(), f"the frozen file {name} is missing"
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    assert got == PINNED[name], f"the frozen file {name} has changed"


def test_twelve_files_are_pinned() -> None:
    assert len(PINNED) == 12  # Part A's seven, Amendment 2, Amendment 3 with the multipliers file and its copy, Amendment 4


def test_the_multipliers_copy_is_in_the_form_the_entry_point_reads_and_is_one_in_every_row() -> None:
    """Amendment 3: no row is widened. The entry point's own parser accepts the committed copy, and every row is 1."""
    from vpd_audit_2 import lead_analysis as LA

    assert LA.MULTIPLIERS_MD == "freeze/amendment1_multipliers.md" and LA.MULTIPLIERS_JSON == "freeze/amendment1_multipliers.json"
    assert LA.parse_multipliers(FREEZE_DIR / "amendment1_multipliers.json") == {row: 1.0 for row in LA.ROWS}
    assert LA.ROWS == ("n20", "n40", "n80", "n160", "n320", "h2", "h5", "h10")


def test_sha256sums_lists_every_pinned_file_with_its_pinned_hash() -> None:
    """`SHA256SUMS` may gain lines for files added later (the multipliers); the seven pinned lines must stay as they are."""
    listed: dict[str, str] = {}
    for line in (FREEZE_DIR / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert name not in listed, f"SHA256SUMS lists {name} twice"
        listed[name] = digest
    for name, digest in PINNED.items():
        assert listed.get(name) == digest, f"SHA256SUMS does not carry the pinned hash of {name}"


def test_every_file_sha256sums_lists_matches_it() -> None:
    for line in (FREEZE_DIR / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = FREEZE_DIR / name
        assert path.is_file(), f"SHA256SUMS lists {name}, which is missing"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"{name} does not match SHA256SUMS"
