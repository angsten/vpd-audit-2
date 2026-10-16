# Erratum to `interval_spec.md`

The specification as filed cannot be edited, so three corrections to `interval_spec.md` are recorded here and should be read with it. None changes a formula of the interval itself.

## 1. Check Scenario G1 Should Have Attack-Batch Effects Only

Section 7 gives G1 Gaussian effects of both attack and held-out batches and promises 95 percent coverage. That is slightly wrong. With both effects, the variance estimate rests on about 30 degrees of freedom while the rule uses $K - 1 = 15$, so the interval is a little wide and coverage is about 95.9 percent.

**Corrected G1:** Gaussian attack-batch effects only, with no held-out effect, no start effect, and no cell noise. Then $V_{\mathrm{PB}}$ equals the classical $s^2/K$ exactly, $V_c = 0$, $\nu = 15$, and the interval is the textbook $t$ interval, whose coverage is exactly 95 percent. A second version with both effects may be run beside it; its expected coverage is about 95.9 percent.

## 2. The Truth at Harm-Level Rows When There Is a Start Effect

Section 6 writes each true value from population means and says "large" is $\mu_k + \mu_C - \mu_q$. At a harm-level row with $\sigma_\delta > 0$ this needs care. Whether an attack search reaches the level depends on the start's shift $\delta_s$, and so does the held-out batch's 20-step harm $q$, because both sides share the start. The estimator averages $q$ over cells whose attack search is present, so starts under which more attack searches are present weigh more.

**The rule that is always right:** every true mean is the expected total divided by the expected count, with the dependence on $\delta$ kept inside both expectations. For a mean of kind $M_A$,

$$
\text{truth} = \frac{\mathbb{E}\left[\sum_{i,j,s} a_{is}\, f_{ijs}\right]}{\mathbb{E}\left[K\sum_{i,s} a_{is}\right]},
$$

and likewise for $M_H$ with $b_{js}$. In practice: at each point of the $\delta$ grid compute the share of searches present and the present searches' mean of each quantity, then combine grid points weighted by the normal density times the share present. For "large" this means $\mu_q$ is averaged with the attack side's presence share as an extra weight. Scenarios P7 and P8, which set $\rho$ so that the true "large" difference is zero, must use that same weighted $\mu_q$.

At search-length rows nothing is missing and the simple formulas of Section 6 are exact. At harm-level rows with $\sigma_\delta = 0$ they are exact too.

## 3. Three Symbols That Look Alike

The specification uses $z_{ijs}$ for a cell's shuffled harm, $Z_{ij}$ for the table of linearized values in Section 5.2, and the draft's $z_D$ for the shuffled denominator's distance from zero. It also uses $w_c$ for a batch type's probability, $W_{ijs}$ for a linearized cell, and $w$ for an unwidened half-width. They are different things. In code we suggest names that cannot be confused, for example `shuf` for $z_{ijs}$, `lin_table` for $Z_{ij}$, `denom_z` for $z_D$, `type_weight` for $w_c$, `lin_cell` for $W_{ijs}$, and `half_width` for $w$.
