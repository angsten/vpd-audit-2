"""The removal-effect harness for B2 and B3 (plan 6, Section 4, item 8), on G3's machinery.

A batch is a list of rows, each a text with a list of changes (position, module, component, new mask value); a row with no
change is that text's base. One forward per batch. A change's effect is G3's
    e = log1p(sum_i Q_i expm1(d_i)) - sum_i P_i d_i
in float64 (`g3.effect`), d the logit difference between the changed row and the base row, summed over the change's
position and every later one.

Backgrounds (G3's, with plan 6's precisions): all on in float32 (masks 1, delta masks 1); at labels in float64 (masks at
the labels, delta masks 0); stochastic in float64 (masks g + (1 - g) u, delta masks u_delta, from (master, "stoch", 1,
text_id, 0), all 24 matrices). The float64 passes run the model cast to float64 with the float32 labels and draws cast to
float64, never recomputed (Ruth), and the target recomputed in float64, as G3's diagnostic did. The authors'
`LlamaRMSNorm` still computes in float32 inside a float64 model (D5); it is left as it is.

B2's removals put a label-zero component's mask to 0 in all on and stochastic, and to 1 at labels, where its mask already
sits at 0 (session 1's label-zero reference). In the pilot's B2 every batch carries its own base row, so a change and its
base share one forward and one grouping.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from vpd_audit_2 import g3

BACKGROUNDS = ("all_on", "at_labels", "stochastic")
PRECISION = {"all_on": "fp32", "at_labels": "fp64", "stochastic": "fp64"}


class Harness:
    def __init__(self, model: Any, ids: np.ndarray, labels32: dict[str, Any], draw: dict[str, Any] | None, device: str):
        import torch

        self.model, self.device = model, device
        self.ids = torch.from_numpy(np.asarray(ids).astype(np.int64)).to(device)
        self.labels32 = {k: v.to(device) for k, v in labels32.items()}
        self.draw = draw
        self.dtype = None
        self.set_precision("fp32")

    def set_precision(self, precision: str) -> None:
        import torch

        dtype = torch.float64 if precision == "fp64" else torch.float32
        if dtype == self.dtype:
            return
        self.model.to(dtype)
        self.dtype = dtype
        with torch.no_grad():
            self.wd = self.model.calc_weight_deltas()
            self.target = self.model(self.ids)
        self.labels = {k: v.to(dtype) for k, v in self.labels32.items()}  # cast, never recomputed
        if self.draw is not None:
            self.u = {k: v.to(self.device, dtype) for k, v in self.draw["u"].items()}
            self.ud = {k: v.to(self.device, dtype) for k, v in self.draw["delta"].items()}

    def release(self) -> None:
        import torch

        self.model.to(torch.float32)
        self.dtype = None

    def _row(self, background: str, i: int, changes: list[tuple[int, str, int, float]]) -> tuple[dict[str, Any], dict[str, Any]]:
        import torch

        T = int(self.ids.shape[1])
        if background == "all_on":
            comp = {k: torch.ones_like(v[i : i + 1]) for k, v in self.labels.items()}
            dm = {k: torch.ones((1, T), dtype=self.dtype, device=self.device) for k in self.labels}
        elif background == "at_labels":
            comp = {k: v[i : i + 1].clone() for k, v in self.labels.items()}
            dm = {k: torch.zeros((1, T), dtype=self.dtype, device=self.device) for k in self.labels}
        elif background == "stochastic":
            comp = {k: v[i : i + 1] + (1 - v[i : i + 1]) * self.u[k][i : i + 1] for k, v in self.labels.items()}
            dm = {k: self.ud[k][i : i + 1] for k in self.labels}
        else:
            raise ValueError(background)
        for t, k, c, val in changes:
            comp[k][0, t, c] = val
        return comp, dm

    def logits(self, background: str, rows: list[tuple[int, list[tuple[int, str, int, float]]]]) -> Any:
        import torch

        from param_decomp.models.components import make_mask_infos

        parts = [self._row(background, i, ch) for i, ch in rows]
        comp = {k: torch.cat([p[0][k] for p in parts]) for k in self.labels}
        dm = {k: torch.cat([p[1][k] for p in parts]) for k in self.labels}
        wdm = {k: (self.wd[k], dm[k]) for k in self.labels}
        with torch.no_grad():
            return self.model(self.ids[[i for i, _ in rows]], mask_infos=make_mask_infos(component_masks=comp, weight_deltas_and_masks=wdm,
                                                                                       routing_masks="all"))

    def effect(self, test: Any, base: Any, i: int, t: int) -> float:
        """Per-position effects over all positions, then the numpy sum from t to the end, as G3 summed them."""
        e = g3.effect(test, base, self.target[i]).cpu().numpy()
        return float(e[t:].sum())

    def effects_with_base(self, background: str, i: int, changes: list[tuple[int, str, int, float]], rows_per_batch: int) -> list[float]:
        """Each single change on text i, in batches whose first row is the text's base."""
        out = []
        for a in range(0, len(changes), rows_per_batch - 1):
            chunk = changes[a : a + rows_per_batch - 1]
            lg = self.logits(background, [(i, [])] + [(i, [ch]) for ch in chunk])
            out += [self.effect(lg[r + 1], lg[0], i, ch[0]) for r, ch in enumerate(chunk)]
            del lg
        return out


def reproduce_g3_controls(h: Harness, controls: list[dict[str, Any]], stored: dict[str, Any]) -> dict[str, Any]:
    """Plan 6, item 8's test: G3's positive controls through this harness, at G3's grouping (one batch of all 32 texts for
    the base, one with each text's control), in float32, against `g3.json`'s effects, for all on and stochastic."""
    h.set_precision("fp32")
    out = {}
    n = int(h.ids.shape[0])
    for bg in ("all_on", "stochastic"):
        base = h.logits(bg, [(i, []) for i in range(n)])
        test = h.logits(bg, [(c["row"], [(c["position"], c["module"], c["c"], 0.0)]) for c in controls])
        got = [h.effect(test[c["row"]], base[c["row"]], c["row"], c["position"]) for c in controls]
        want = [r["effect_grouping_32"] for r in stored[bg]["rows"]]
        out[bg] = {"bitwise_equal": got == want, "max_abs_difference": float(max(abs(a - b) for a, b in zip(got, want)))}
        del base, test
    out["passes"] = all(v["bitwise_equal"] for v in out.values())
    return out
