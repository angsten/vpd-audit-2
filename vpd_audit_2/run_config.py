"""The released decomposition's configuration, read from the raw text of its `final_config.yaml`.

The file is `provenance/runs/s-55ea3f9b/final_config.yaml`, byte for byte as WandB serves it (its SHA-256 is
checked on load). Values are read from the parsed YAML text, never from the authors' `Config` class, whose
validators and defaults could fill or change fields silently. Importing this module asserts every value that
`provenance/provenance.md` records from that file, so later code that imports it fails loudly on a mismatch:

    from vpd_audit_2.run_config import RAW, loss_entry, eval_entry

`RAW` is the parsed dictionary; `loss_entry(classname)` and `eval_entry(classname)` return the single entry of
that class in `loss_metric_configs` or `eval_metric_configs`.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from vpd_audit_2.env import PROVENANCE_DIR

RUN_ID = "s-55ea3f9b"
CONFIG_PATH: Path = PROVENANCE_DIR / "runs" / RUN_ID / "final_config.yaml"
CONFIG_SHA256 = "75af17e6813ad0e939c18221fa188a757911e292141323cd375b8aa5d06a4ffc"


def load_raw(path: Path = CONFIG_PATH, sha256: str = CONFIG_SHA256) -> dict[str, Any]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == sha256, f"{path}: SHA-256 {digest}, expected {sha256}"
    raw = yaml.safe_load(data)
    assert isinstance(raw, dict)
    return raw


def _entries(raw: dict[str, Any], section: str, classname: str) -> list[dict[str, Any]]:
    return [e for e in raw[section] if e.get("classname") == classname]


def loss_entry(classname: str, raw: dict[str, Any] | None = None) -> dict[str, Any]:
    found = _entries(raw if raw is not None else RAW, "loss_metric_configs", classname)
    assert len(found) == 1, f"{len(found)} loss entries of class {classname}"
    return found[0]


def eval_entry(classname: str, raw: dict[str, Any] | None = None) -> dict[str, Any]:
    found = _entries(raw if raw is not None else RAW, "eval_metric_configs", classname)
    assert len(found) == 1, f"{len(found)} eval entries of class {classname}"
    return found[0]


# Every top-level value recorded in provenance.md, as it appears in the raw text.
TOP_LEVEL: dict[str, Any] = {
    "seed": 0,
    "autocast_bf16": True,
    "n_mask_samples": 1,
    "sampling": "continuous",
    "sigmoid_type": "leaky_hard",
    "identity_module_info": None,
    "init_spd_checkpoint": None,
    "use_delta_component": True,
    "output_loss_type": "kl",
    "lr_schedule": {"start_val": 5.0e-05, "warmup_pct": 0.0, "final_val_frac": 0.1, "fn_type": "cosine"},
    "steps": 400000,
    "batch_size": 64,
    "grad_clip_norm_components": 0.01,
    "grad_clip_norm_ci_fns": None,
    "faithfulness_warmup_steps": 400,
    "faithfulness_warmup_lr": 0.001,
    "faithfulness_warmup_weight_decay": 0.0,
    "train_log_freq": 200,
    "eval_freq": 1000,
    "eval_batch_size": 128,
    "slow_eval_freq": 10000,
    "n_eval_steps": 1,
    "slow_eval_on_first_step": True,
    "save_freq": None,
    "ci_alive_threshold": 0.0,
    "pretrained_model_class": "spd.pretrain.models.llama_simple_mlp.LlamaSimpleMLP",
    "pretrained_model_path": None,
    "pretrained_model_name": "goodfire/spd/runs/t-9d2b8f02",
    "pretrained_model_output_attr": "idx_0",
    "tokenizer_name": "EleutherAI/gpt-neox-20b",
}

CI_CONFIG: dict[str, Any] = {
    "mode": "global",
    "fn_type": "global_shared_transformer",
    "hidden_dims": None,
    "reader_hidden_dims": None,
    "d_resid_ci_fn": None,
    "block_groups": None,
    "transition_attn_config": None,
    "transition_hidden_dim": None,
    "simple_transformer_ci_cfg": {"d_model": 2048, "n_blocks": 8, "mlp_hidden_dim": [8192],
                                  "attn_config": {"n_heads": 16, "max_len": 512, "rope_base": 10000.0}},
}

MODULE_INFO: list[dict[str, Any]] = [
    {"module_pattern": "h.*.mlp.c_fc", "C": 3072},
    {"module_pattern": "h.*.mlp.down_proj", "C": 3584},
    {"module_pattern": "h.*.attn.q_proj", "C": 512},
    {"module_pattern": "h.*.attn.k_proj", "C": 512},
    {"module_pattern": "h.*.attn.v_proj", "C": 1024},
    {"module_pattern": "h.*.attn.o_proj", "C": 1024},
]

# The four training terms, in the raw text's order, each complete (no field absent from these dicts is present).
LOSS_METRIC_CONFIGS: list[dict[str, Any]] = [
    {"coeff": 0.0002, "classname": "ImportanceMinimalityLoss", "pnorm": 2.0, "beta": 0.5, "p_anneal_start_frac": 0.0,
     "p_anneal_final_p": 0.4, "p_anneal_end_frac": 1.0, "eps": 1.0e-12},
    {"coeff": 0.5, "classname": "StochasticReconSubsetLoss", "routing": {"type": "uniform_k_subset"}},
    {"coeff": 0.5, "optimizer": {"type": "adam", "beta1": 0.5, "beta2": 0.99, "eps": 1.0e-08,
                                 "lr_schedule": {"start_val": 0.01, "warmup_pct": 0.025, "final_val_frac": 1.0, "fn_type": "constant"}},
     "scope": {"type": "per_batch_per_position"}, "use_sigmoid_parameterization": False, "n_warmup_steps": 2,
     "classname": "PersistentPGDReconLoss"},
    {"coeff": 10000000.0, "classname": "FaithfulnessLoss"},
]

# The evaluation metrics, in the raw text's order, each complete.
EVAL_METRIC_CONFIGS: list[dict[str, Any]] = [
    {"classname": "CIHistograms", "n_batches_accum": 1},
    {"classname": "ComponentActivationDensity"},
    {"classname": "CI_L0", "groups": {"layer_0": ["h.0.*"], "layer_1": ["h.1.*"], "layer_2": ["h.2.*"], "layer_3": ["h.3.*"], "total": ["*"]}},
    {"classname": "CEandKLLosses", "rounding_threshold": 0.0},
    {"classname": "CIMeanPerComponent"},
    {"coeff": None, "classname": "StochasticHiddenActsReconLoss"},
    {"classname": "CIHiddenActsReconLoss"},
    {"coeff": None, "init": "random", "step_size": 0.1, "n_steps": 20, "mask_scope": "shared_across_batch", "classname": "PGDReconLoss"},
]

TASK_CONFIG: dict[str, Any] = {
    "task_name": "lm",
    "max_seq_len": 512,
    "buffer_size": 1000,
    "dataset_name": "danbraunai/pile-uncopyrighted-tok-shuffled",
    "column_name": "input_ids",
    "train_data_split": "train",
    "eval_data_split": "val",
    "shuffle_each_epoch": True,
    "is_tokenized": True,
    "streaming": True,
}

TOP_LEVEL_KEYS = (set(TOP_LEVEL) | {"wandb_project", "wandb_run_name", "wandb_run_name_prefix", "ci_config", "module_info",
                                    "loss_metric_configs", "eval_metric_configs", "task_config"})


def assert_run_config(raw: dict[str, Any]) -> None:
    """Every value provenance.md records from the raw text, including the absences it relies on."""
    assert set(raw) == TOP_LEVEL_KEYS, f"top-level keys differ: extra {sorted(set(raw) - TOP_LEVEL_KEYS)}, missing {sorted(TOP_LEVEL_KEYS - set(raw))}"
    for k, v in TOP_LEVEL.items():
        assert raw[k] == v, f"{k}: raw {raw[k]!r}, recorded {v!r}"
    assert raw["ci_config"] == CI_CONFIG, raw["ci_config"]
    assert raw["module_info"] == MODULE_INFO, raw["module_info"]
    assert raw["loss_metric_configs"] == LOSS_METRIC_CONFIGS, raw["loss_metric_configs"]
    assert raw["eval_metric_configs"] == EVAL_METRIC_CONFIGS, raw["eval_metric_configs"]
    assert raw["task_config"] == TASK_CONFIG, raw["task_config"]
    # the absences the provenance answers rest on
    pgd_eval = [e for e in raw["eval_metric_configs"] if "PGD" in e["classname"]]
    assert len(pgd_eval) == 1 and pgd_eval[0]["n_steps"] == 20, "exactly one adversary metric in evaluation, of 20 steps"
    assert "routing" not in eval_entry("PGDReconLoss", raw), "the evaluation adversary's entry has no routing field"
    assert "routing" not in loss_entry("PersistentPGDReconLoss", raw), "the training adversary's entry has no routing field"
    assert not any("MultiBatch" in e["classname"] for e in raw["eval_metric_configs"] + raw["loss_metric_configs"]), "no multi-batch adversary"
    assert "dataset_seed" not in raw["task_config"], "no dataset_seed field: the loaders use the global seed"
    assert sum(raw["module_info"][i]["C"] for i in range(6)) * 4 == 38912


RAW: dict[str, Any] = load_raw()
assert_run_config(RAW)


if __name__ == "__main__":
    print(f"{CONFIG_PATH.relative_to(PROVENANCE_DIR.parent)}: SHA-256 {CONFIG_SHA256}; every recorded value asserted")
