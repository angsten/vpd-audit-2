"""A tiny stand-in for the released decomposition, built from the authors' own classes at 74146b5, for CPU tests.

The target is the authors' `LlamaSimpleMLP` (the released run's target class) with two layers of width 16 and a vocabulary
of 53; the decomposition is the authors' `ComponentModel` over the same six module patterns as the run, with a global
shared-transformer causal importance function, `leaky_hard` sigmoids, and the run's output extraction (index 0). Weights
are random from a fixed seed; the components and the CI function are scaled so that the labels mix zeros, values in
(0, 1), and saturated values, as the real ones do. Nothing here is trained.
"""

from __future__ import annotations

import torch

VOCAB = 53
SEQ = 16
MODULE_C = {"h.*.mlp.c_fc": 6, "h.*.mlp.down_proj": 5, "h.*.attn.q_proj": 4, "h.*.attn.k_proj": 4, "h.*.attn.v_proj": 3, "h.*.attn.o_proj": 4}


def tiny_component_model(seed: int = 0):
    from param_decomp.configs import AttnConfig, GlobalCiConfig, GlobalSharedTransformerCiConfig, ModulePatternInfoConfig
    from param_decomp.models.component_model import ComponentModel
    from param_decomp.pretrain.models.llama_simple_mlp import LlamaSimpleMLP, LlamaSimpleMLPConfig
    from param_decomp.utils.module_utils import expand_module_patterns

    torch.manual_seed(seed)
    cfg = LlamaSimpleMLPConfig(model_type="LlamaSimpleMLP", block_size=SEQ, vocab_size=VOCAB, n_layer=2, n_head=2, n_embd=16, n_intermediate=32,
                               rotary_dim=8, n_ctx=SEQ, n_key_value_heads=2, use_grouped_query_attention=True, flash_attention=False)
    target = LlamaSimpleMLP(cfg)
    with torch.no_grad():
        for p in target.parameters():
            p.mul_(20.0)  # larger logits, so masking matters
    target.eval()
    target.requires_grad_(False)
    info = [ModulePatternInfoConfig(module_pattern=k, C=c) for k, c in MODULE_C.items()]
    ci_cfg = GlobalCiConfig(fn_type="global_shared_transformer",
                            simple_transformer_ci_cfg=GlobalSharedTransformerCiConfig(d_model=8, n_blocks=1, mlp_hidden_dim=[16],
                                                                                      attn_config=AttnConfig(n_heads=2, max_len=SEQ)))
    model = ComponentModel(target, run_batch=lambda m, b: m(b)[0], module_path_info=expand_module_patterns(target, info), ci_config=ci_cfg,
                           sigmoid_type="leaky_hard")
    with torch.no_grad():
        for p in model.ci_fn.parameters():
            p.mul_(1.0)  # about half the pre-sigmoid values at or below 0, a quarter in (0, 1], a quarter above 1
    model.eval()
    return model


def tiny_ids(n: int, seed: int = 1) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    return torch.randint(0, VOCAB, (n, SEQ), generator=g)
