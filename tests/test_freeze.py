"""Session 5, plan 1, Part A: the signed rules, Amendment 1, and its three binding specifications, pinned.

`vpd-audit-2/freeze/` holds byte copies of the rules the lead experiment is read under:

  - `part1.md`: the freeze file, Part 1, signed by the PI (`sessions/004/freeze_file_part1_q2.md`);
  - `amendment1.md`: Amendment 1 (`sessions/005/amendment_1_part1_q2.md`);
  - `amendment1_specs/`: the interval specification, the output and reading specification, and the table and run
    specification, with their errata (`sessions/005/notes/{daniel,riku,lena}/`);
  - `amendment2.md`: Amendment 2 (`sessions/005/amendment_2_part1_q2.md`), added in a commit of its own;
  - `amendment3.md`: Amendment 3 (`sessions/005/amendment_3_part1_q2.md`), with the multipliers file that Amendment 1's
    Section 5.6 provides for, `amendment1_multipliers.md`, and its machine-readable copy, `amendment1_multipliers.json`
    (`sessions/005/amendment1_multipliers.{md,json}`), added together in a commit of their own;
  - `amendment4.md`: Amendment 4 (`sessions/005/amendment_4_part1_q2.md`), added in a commit of its own.

Each file's SHA-256 is a constant here, taken when the copies were made. A change to any byte of any of these files
fails this test. The constants are never updated to follow a changed file: a change to the rules is a new dated
file beside these, not an edit.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

FREEZE_DIR = Path(__file__).resolve().parent.parent / "freeze"

PINNED = {
    "part1.md": "27fbb48e5db64ba5f78882ce1a4aed99bf60745369fe60c0169c7560a040ba81",
    "amendment1.md": "9dcfe7dc36a75461ce437f3bc302c10337b3d42ed558e9f47391052863594916",
    "amendment1_specs/interval_spec.md": "67091bb0f84ab5f6584c2336d5ca37ff93e046cd3b91cd923001b5b0768a0da9",
    "amendment1_specs/interval_spec_erratum.md": "efbcec89f2a7626770edf3458bbb76124202406bc049c4e780a7f07896085e10",
    "amendment1_specs/output_and_reading_spec.md": "5f0151f789f5ecb0696e4fb3e57deea6ea94b5a76cb5f2af8ee07547085bd955",
    "amendment1_specs/table_and_run_spec.md": "5ea4d1edfacad8121d4af75fe679ac9ef83e17639622b32e2ac78853684c45dd",
    "amendment1_specs/table_and_run_spec_erratum.md": "ef710617f183f997aa292cc4af67a19012fcefb21ab90f691d77e081b747b49d",
    # Amendment 2 (`sessions/005/amendment_2_part1_q2.md`), committed alone before either version of the made-up-data
    # test of record ran (session 5, plan 3, step 1). The seven pins above are as Part A committed them.
    "amendment2.md": "742ebb7397dc7e58d5d3b18195cb0997dd3bf88627115ce12b8ce871c5221ca5",
    # Amendment 3 and the multipliers file with its machine-readable copy, committed together and alone, after the
    # made-up-data test of record and before any deciding run. The eight pins above are unchanged.
    "amendment3.md": "f13d462ad3adfd1200d1fd14f87f4d1e182fcf8e1a8ce9f4531789b189eff2fa",
    "amendment1_multipliers.md": "2e7e3da766a8f1239545290123a452ce7e7edeacc6cd333a048193be0e1e7962",
    "amendment1_multipliers.json": "f178811ccd2a4b1eff8c5d60f8f2b52533f27186de718703eea57c6fbf8c6f75",
    # Amendment 4 (`sessions/005/amendment_4_part1_q2.md`): the PI's cap of $150 and how spend is counted against it,
    # committed alone, after the first rehearsal and before any deciding run. The eleven pins above are unchanged.
    "amendment4.md": "e408d7a2b674eb1786309c5a1890bee1aa24d203adfea9ea74007dfce8a8a1a2",
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
