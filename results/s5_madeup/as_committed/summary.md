# The Made-Up-Data Test of the Interval: Summary of the Generator as Committed in Amendment 1

**Not the test of record: the generator as committed in Amendment 1 (a held-out batch's vulnerability carries its pilot type's factor). Printed beside the test of record; it sets no multiplier, and its multipliers are those each row would have required.**

Every number in this file comes from made-up experiments built on the pilot's own-batch searches. None is a result of the lead experiment.

## Checks With Exact Known Answers

- **G1** (attack-batch effects only): coverage 0.9505 over 2000 experiments; expected 0.95; 0.10 Monte Carlo standard errors from it; V_PB is the classical s^2/K and nu is K - 1 in every experiment: yes. Passes: yes.
- **G2** (independent cell noise only): mean of V_PB over the true variance 2.9316 (expected 2.9375, Monte Carlo standard error 0.0120); coverage 0.9995. Passes: yes.

## The Guard on the Generator

830 comparisons of a plain mean with its true value at search-length rows. The largest is 3.07 Monte Carlo standard errors; the test stops at 5. Comparisons above 3.5: 0.

## Each Core Cell: Pass or Fail

A cell is one core scenario, one row, and one signed reading. Coverage is of the unwidened interval. A cell under 93.5 percent, or with more than 3.25 percent of its intervals wholly on one side of its line, is rerun with 10,000 experiments and judged on the rerun alone.

| Scenario | Row | Reading | Line | Judged on | Coverage | Wholly above | Wholly below | Rerun | Multiplier needed | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | carries | 0.2 | 10000 | 0.8978 | 0.0009 | 0.1013 | yes | 1.811 | FAIL |
| P1 | n20 | depends |  | 10000 | 0.9029 | 0.0919 | 0.0052 | yes | 1.365 | FAIL |
| P1 | n40 | large |  | 2000 | 0.9755 | 0.0145 | 0.0100 | no | 0.881 | pass |
| P1 | n40 | carries | 0.2 | 10000 | 0.9551 | 0.0091 | 0.0358 | yes | 0.985 | pass |
| P1 | n40 | depends |  | 2000 | 0.9540 | 0.0055 | 0.0405 | no | 0.962 | pass |
| P1 | n80 | large |  | 2000 | 0.9590 | 0.0000 | 0.0410 | no | 0.931 | pass |
| P1 | n80 | carries | 0.2 | 10000 | 0.9519 | 0.0029 | 0.0452 | yes | 1.069 | FAIL |
| P1 | n80 | depends |  | 2000 | 0.9480 | 0.0035 | 0.0485 | no | 1.011 | pass |
| P1 | n160 | large |  | 10000 | 0.9328 | 0.0037 | 0.0635 | yes | 1.104 | pass |
| P1 | n160 | carries | 0.2 | 10000 | 0.9079 | 0.0008 | 0.0913 | yes | 1.531 | FAIL |
| P1 | n160 | depends |  | 10000 | 0.9129 | 0.0008 | 0.0863 | yes | 1.341 | FAIL |
| P1 | n320 | large |  | 10000 | 0.9271 | 0.0027 | 0.0702 | yes | 1.152 | pass |
| P1 | n320 | carries | 0.2 | 10000 | 0.9056 | 0.0014 | 0.0930 | yes | 1.588 | FAIL |
| P1 | n320 | depends |  | 10000 | 0.9078 | 0.0013 | 0.0909 | yes | 1.391 | FAIL |
| P1 | h2 | large |  | 10000 | 0.8959 | 0.1031 | 0.0010 | yes | 1.392 | FAIL |
| P1 | h2 | carries | 0.2 | 10000 | 0.8754 | 0.0037 | 0.1209 | yes | 2.339 | FAIL |
| P1 | h2 | depends |  | 2000 | 0.9920 | 0.0015 | 0.0065 | no | 0.716 | pass |
| P1 | h5 | large |  | 10000 | 0.9075 | 0.0020 | 0.0905 | yes | 1.282 | FAIL |
| P1 | h5 | carries | 0.2 | 10000 | 0.8765 | 0.0030 | 0.1205 | yes | 2.488 | FAIL |
| P1 | h5 | depends |  | 10000 | 0.8780 | 0.0022 | 0.1198 | yes | 2.155 | FAIL |
| P1 | h10 | large |  | 10000 | 0.7538 | 0.0000 | 0.2462 | yes | 2.256 | FAIL |
| P1 | h10 | carries | 0.2 | 10000 | 0.7523 | 0.0000 | 0.2477 | yes | 2.819 | FAIL |
| P1 | h10 | depends |  | 10000 | 0.7522 | 0.0000 | 0.2478 | yes | 2.589 | FAIL |
| P2 | n20 | carries |  | 10000 | 0.8958 | 0.0015 | 0.1027 | yes | 1.590 | FAIL |
| P2 | n20 | depends |  | 10000 | 0.8985 | 0.0023 | 0.0992 | yes | 1.361 | FAIL |
| P2 | n40 | large |  | 2000 | 0.9375 | 0.0050 | 0.0575 | no | 1.082 | pass |
| P2 | n40 | carries |  | 2000 | 0.9535 | 0.0100 | 0.0365 | no | 0.982 | pass |
| P2 | n40 | depends |  | 2000 | 0.9520 | 0.0080 | 0.0400 | no | 0.988 | pass |
| P2 | n80 | large |  | 2000 | 0.9530 | 0.0030 | 0.0440 | no | 0.994 | pass |
| P2 | n80 | carries |  | 2000 | 0.9490 | 0.0025 | 0.0485 | no | 1.001 | pass |
| P2 | n80 | depends |  | 2000 | 0.9505 | 0.0020 | 0.0475 | no | 0.995 | pass |
| P2 | n160 | large |  | 10000 | 0.9306 | 0.0033 | 0.0661 | yes | 1.127 | pass |
| P2 | n160 | carries |  | 10000 | 0.9107 | 0.0005 | 0.0888 | yes | 1.369 | FAIL |
| P2 | n160 | depends |  | 10000 | 0.9111 | 0.0004 | 0.0885 | yes | 1.363 | FAIL |
| P2 | n320 | large |  | 10000 | 0.9237 | 0.0034 | 0.0729 | yes | 1.183 | FAIL |
| P2 | n320 | carries |  | 10000 | 0.9083 | 0.0009 | 0.0908 | yes | 1.390 | FAIL |
| P2 | n320 | depends |  | 10000 | 0.9086 | 0.0008 | 0.0906 | yes | 1.386 | FAIL |
| P2 | h2 | large |  | 10000 | 0.8921 | 0.0022 | 0.1057 | yes | 1.430 | FAIL |
| P2 | h2 | carries |  | 10000 | 0.8769 | 0.0029 | 0.1202 | yes | 2.172 | FAIL |
| P2 | h2 | depends |  | 10000 | 0.8764 | 0.0021 | 0.1215 | yes | 2.164 | FAIL |
| P2 | h5 | large |  | 10000 | 0.8779 | 0.0026 | 0.1195 | yes | 1.973 | FAIL |
| P2 | h5 | carries |  | 10000 | 0.8775 | 0.0026 | 0.1199 | yes | 2.299 | FAIL |
| P2 | h5 | depends |  | 10000 | 0.8773 | 0.0023 | 0.1204 | yes | 2.305 | FAIL |
| P2 | h10 | large |  | 10000 | 0.7355 | 0.0000 | 0.2645 | yes | 2.611 | FAIL |
| P2 | h10 | carries |  | 10000 | 0.7362 | 0.0000 | 0.2638 | yes | 2.676 | FAIL |
| P2 | h10 | depends |  | 10000 | 0.7361 | 0.0000 | 0.2639 | yes | 2.674 | FAIL |
| P3 | n20 | carries |  | 10000 | 0.9019 | 0.0019 | 0.0962 | yes | 1.511 | FAIL |
| P3 | n20 | depends |  | 10000 | 0.8951 | 0.0015 | 0.1034 | yes | 1.598 | FAIL |
| P3 | n40 | large |  | 2000 | 0.9460 | 0.0035 | 0.0505 | no | 1.030 | pass |
| P3 | n40 | carries |  | 2000 | 0.9585 | 0.0105 | 0.0310 | no | 0.962 | pass |
| P3 | n40 | depends |  | 2000 | 0.9565 | 0.0105 | 0.0330 | no | 0.962 | pass |
| P3 | n80 | large |  | 2000 | 0.9475 | 0.0025 | 0.0500 | no | 1.018 | pass |
| P3 | n80 | carries |  | 2000 | 0.9535 | 0.0025 | 0.0440 | no | 0.981 | pass |
| P3 | n80 | depends |  | 2000 | 0.9530 | 0.0025 | 0.0445 | no | 0.978 | pass |
| P3 | n160 | large |  | 2000 | 0.9350 | 0.0040 | 0.0610 | no | 1.122 | pass |
| P3 | n160 | carries |  | 10000 | 0.9138 | 0.0015 | 0.0847 | yes | 1.321 | FAIL |
| P3 | n160 | depends |  | 10000 | 0.9140 | 0.0012 | 0.0848 | yes | 1.321 | FAIL |
| P3 | n320 | large |  | 10000 | 0.9241 | 0.0040 | 0.0719 | yes | 1.179 | FAIL |
| P3 | n320 | carries |  | 10000 | 0.9110 | 0.0012 | 0.0878 | yes | 1.379 | FAIL |
| P3 | n320 | depends |  | 10000 | 0.9108 | 0.0010 | 0.0882 | yes | 1.380 | FAIL |
| P3 | h2 | large |  | 10000 | 0.8791 | 0.0034 | 0.1175 | yes | 1.665 | FAIL |
| P3 | h2 | carries |  | 10000 | 0.8754 | 0.0046 | 0.1200 | yes | 2.089 | FAIL |
| P3 | h2 | depends |  | 10000 | 0.8763 | 0.0023 | 0.1214 | yes | 2.140 | FAIL |
| P3 | h5 | large |  | 10000 | 0.8760 | 0.0041 | 0.1199 | yes | 2.043 | FAIL |
| P3 | h5 | carries |  | 10000 | 0.8768 | 0.0036 | 0.1196 | yes | 2.262 | FAIL |
| P3 | h5 | depends |  | 10000 | 0.8773 | 0.0029 | 0.1198 | yes | 2.283 | FAIL |
| P3 | h10 | large |  | 10000 | 0.7427 | 0.0000 | 0.2573 | yes | 2.658 | FAIL |
| P3 | h10 | carries |  | 10000 | 0.7431 | 0.0000 | 0.2569 | yes | 2.682 | FAIL |
| P3 | h10 | depends |  | 10000 | 0.7430 | 0.0000 | 0.2570 | yes | 2.691 | FAIL |
| P4 | n20 | carries | 0.2 | 10000 | 0.9072 | 0.0015 | 0.0913 | yes | 1.648 | FAIL |
| P4 | n20 | depends |  | 10000 | 0.9246 | 0.0727 | 0.0027 | yes | 1.171 | FAIL |
| P4 | n40 | large |  | 2000 | 0.9675 | 0.0215 | 0.0110 | no | 0.890 | pass |
| P4 | n40 | carries | 0.2 | 10000 | 0.9543 | 0.0087 | 0.0370 | yes | 0.996 | pass |
| P4 | n40 | depends |  | 2000 | 0.9525 | 0.0080 | 0.0395 | no | 0.988 | pass |
| P4 | n80 | large |  | 2000 | 0.9430 | 0.0085 | 0.0485 | no | 1.051 | pass |
| P4 | n80 | carries | 0.2 | 10000 | 0.9487 | 0.0032 | 0.0481 | yes | 1.099 | FAIL |
| P4 | n80 | depends |  | 2000 | 0.9515 | 0.0015 | 0.0470 | no | 0.994 | pass |
| P4 | n160 | large |  | 2000 | 0.9370 | 0.0020 | 0.0610 | no | 1.119 | pass |
| P4 | n160 | carries | 0.2 | 10000 | 0.9099 | 0.0004 | 0.0897 | yes | 1.584 | FAIL |
| P4 | n160 | depends |  | 10000 | 0.9136 | 0.0004 | 0.0860 | yes | 1.357 | FAIL |
| P4 | n320 | large |  | 10000 | 0.9277 | 0.0036 | 0.0687 | yes | 1.155 | pass |
| P4 | n320 | carries | 0.2 | 10000 | 0.9075 | 0.0013 | 0.0912 | yes | 1.636 | FAIL |
| P4 | n320 | depends |  | 10000 | 0.9105 | 0.0011 | 0.0884 | yes | 1.417 | FAIL |
| P4 | h2 | large |  | 10000 | 0.9248 | 0.0680 | 0.0072 | yes | 1.213 | FAIL |
| P4 | h2 | carries | 0.2 | 10000 | 0.8770 | 0.0050 | 0.1180 | yes | 2.353 | FAIL |
| P4 | h2 | depends |  | 2000 | 0.9920 | 0.0000 | 0.0080 | no | 0.723 | pass |
| P4 | h5 | large |  | 2000 | 0.9350 | 0.0065 | 0.0585 | no | 1.095 | pass |
| P4 | h5 | carries | 0.2 | 10000 | 0.8787 | 0.0033 | 0.1180 | yes | 2.503 | FAIL |
| P4 | h5 | depends |  | 10000 | 0.8796 | 0.0026 | 0.1178 | yes | 2.134 | FAIL |
| P4 | h10 | large |  | 10000 | 0.7628 | 0.0000 | 0.2372 | yes | 2.138 | FAIL |
| P4 | h10 | carries | 0.2 | 10000 | 0.7599 | 0.0000 | 0.2401 | yes | 2.822 | FAIL |
| P4 | h10 | depends |  | 10000 | 0.7610 | 0.0000 | 0.2390 | yes | 2.581 | FAIL |
| P5 | n20 | carries |  | 10000 | 0.9034 | 0.0021 | 0.0945 | yes | 1.474 | FAIL |
| P5 | n20 | depends |  | 10000 | 0.9061 | 0.0027 | 0.0912 | yes | 1.339 | FAIL |
| P5 | n40 | large |  | 10000 | 0.9420 | 0.0047 | 0.0533 | yes | 1.049 | pass |
| P5 | n40 | carries |  | 2000 | 0.9545 | 0.0115 | 0.0340 | no | 0.980 | pass |
| P5 | n40 | depends |  | 2000 | 0.9480 | 0.0080 | 0.0440 | no | 1.004 | pass |
| P5 | n80 | large |  | 2000 | 0.9370 | 0.0095 | 0.0535 | no | 1.084 | pass |
| P5 | n80 | carries |  | 2000 | 0.9490 | 0.0030 | 0.0480 | no | 1.003 | pass |
| P5 | n80 | depends |  | 2000 | 0.9500 | 0.0025 | 0.0475 | no | 1.000 | pass |
| P5 | n160 | large |  | 10000 | 0.9291 | 0.0035 | 0.0674 | yes | 1.125 | pass |
| P5 | n160 | carries |  | 10000 | 0.9106 | 0.0008 | 0.0886 | yes | 1.362 | FAIL |
| P5 | n160 | depends |  | 10000 | 0.9114 | 0.0007 | 0.0879 | yes | 1.355 | FAIL |
| P5 | n320 | large |  | 10000 | 0.9250 | 0.0030 | 0.0720 | yes | 1.185 | pass |
| P5 | n320 | carries |  | 10000 | 0.9102 | 0.0005 | 0.0893 | yes | 1.422 | FAIL |
| P5 | n320 | depends |  | 10000 | 0.9105 | 0.0005 | 0.0890 | yes | 1.419 | FAIL |
| P5 | h2 | large |  | 10000 | 0.9374 | 0.0040 | 0.0586 | yes | 1.075 | pass |
| P5 | h2 | carries |  | 10000 | 0.8820 | 0.0038 | 0.1142 | yes | 2.056 | FAIL |
| P5 | h2 | depends |  | 10000 | 0.8825 | 0.0021 | 0.1154 | yes | 2.035 | FAIL |
| P5 | h5 | large |  | 10000 | 0.8820 | 0.0029 | 0.1151 | yes | 1.859 | FAIL |
| P5 | h5 | carries |  | 10000 | 0.8803 | 0.0032 | 0.1165 | yes | 2.241 | FAIL |
| P5 | h5 | depends |  | 10000 | 0.8804 | 0.0027 | 0.1169 | yes | 2.244 | FAIL |
| P5 | h10 | large |  | 10000 | 0.7476 | 0.0000 | 0.2524 | yes | 2.611 | FAIL |
| P5 | h10 | carries |  | 10000 | 0.7516 | 0.0000 | 0.2484 | yes | 2.691 | FAIL |
| P5 | h10 | depends |  | 10000 | 0.7512 | 0.0000 | 0.2488 | yes | 2.692 | FAIL |
| P6 | n20 | carries |  | 10000 | 0.8950 | 0.0026 | 0.1024 | yes | 1.538 | FAIL |
| P6 | n20 | depends |  | 10000 | 0.8849 | 0.0023 | 0.1128 | yes | 1.688 | FAIL |
| P6 | n40 | large |  | 10000 | 0.9367 | 0.0049 | 0.0584 | yes | 1.077 | pass |
| P6 | n40 | carries |  | 2000 | 0.9590 | 0.0120 | 0.0290 | no | 0.948 | pass |
| P6 | n40 | depends |  | 2000 | 0.9575 | 0.0115 | 0.0310 | no | 0.950 | pass |
| P6 | n80 | large |  | 2000 | 0.9355 | 0.0055 | 0.0590 | no | 1.101 | pass |
| P6 | n80 | carries |  | 2000 | 0.9535 | 0.0015 | 0.0450 | no | 0.974 | pass |
| P6 | n80 | depends |  | 2000 | 0.9535 | 0.0015 | 0.0450 | no | 0.974 | pass |
| P6 | n160 | large |  | 10000 | 0.9284 | 0.0045 | 0.0671 | yes | 1.153 | pass |
| P6 | n160 | carries |  | 10000 | 0.9078 | 0.0008 | 0.0914 | yes | 1.407 | FAIL |
| P6 | n160 | depends |  | 10000 | 0.9081 | 0.0007 | 0.0912 | yes | 1.409 | FAIL |
| P6 | n320 | large |  | 10000 | 0.9217 | 0.0039 | 0.0744 | yes | 1.201 | FAIL |
| P6 | n320 | carries |  | 10000 | 0.9069 | 0.0012 | 0.0919 | yes | 1.439 | FAIL |
| P6 | n320 | depends |  | 10000 | 0.9069 | 0.0012 | 0.0919 | yes | 1.438 | FAIL |
| P6 | h2 | large |  | 10000 | 0.8871 | 0.0032 | 0.1097 | yes | 1.510 | FAIL |
| P6 | h2 | carries |  | 10000 | 0.8750 | 0.0039 | 0.1211 | yes | 2.144 | FAIL |
| P6 | h2 | depends |  | 10000 | 0.8751 | 0.0023 | 0.1226 | yes | 2.196 | FAIL |
| P6 | h5 | large |  | 10000 | 0.8735 | 0.0034 | 0.1231 | yes | 2.072 | FAIL |
| P6 | h5 | carries |  | 10000 | 0.8749 | 0.0031 | 0.1220 | yes | 2.324 | FAIL |
| P6 | h5 | depends |  | 10000 | 0.8754 | 0.0025 | 0.1221 | yes | 2.344 | FAIL |
| P6 | h10 | large |  | 10000 | 0.7475 | 0.0000 | 0.2525 | yes | 2.590 | FAIL |
| P6 | h10 | carries |  | 10000 | 0.7491 | 0.0000 | 0.2509 | yes | 2.623 | FAIL |
| P6 | h10 | depends |  | 10000 | 0.7485 | 0.0000 | 0.2515 | yes | 2.631 | FAIL |
| P7 | n20 | carries |  | 10000 | 0.8989 | 0.0023 | 0.0988 | yes | 1.559 | FAIL |
| P7 | n20 | depends |  | 10000 | 0.8940 | 0.0015 | 0.1045 | yes | 1.625 | FAIL |
| P7 | n40 | large | 0.0 | 10000 | 0.9569 | 0.0078 | 0.0353 | yes | 0.982 | pass |
| P7 | n40 | carries |  | 2000 | 0.9515 | 0.0105 | 0.0380 | no | 0.987 | pass |
| P7 | n40 | depends |  | 2000 | 0.9510 | 0.0060 | 0.0430 | no | 0.993 | pass |
| P7 | n80 | large | 0.0 | 2000 | 0.9700 | 0.0100 | 0.0200 | no | 0.875 | pass |
| P7 | n80 | carries |  | 2000 | 0.9360 | 0.0035 | 0.0605 | no | 1.115 | pass |
| P7 | n80 | depends |  | 2000 | 0.9585 | 0.0040 | 0.0375 | no | 0.931 | pass |
| P7 | n160 | large | 0.0 | 2000 | 0.9725 | 0.0185 | 0.0090 | no | 0.878 | pass |
| P7 | n160 | carries |  | 10000 | 0.9082 | 0.0004 | 0.0914 | yes | 1.362 | FAIL |
| P7 | n160 | depends |  | 2000 | 0.9540 | 0.0010 | 0.0450 | no | 0.972 | pass |
| P7 | n320 | large | 0.0 | 2000 | 0.9800 | 0.0125 | 0.0075 | no | 0.848 | pass |
| P7 | n320 | carries |  | 10000 | 0.9044 | 0.0004 | 0.0952 | yes | 1.447 | FAIL |
| P7 | n320 | depends |  | 2000 | 0.9500 | 0.0010 | 0.0490 | no | 0.996 | pass |
| P7 | h2 | large | 0.0 | 2000 | 0.9840 | 0.0060 | 0.0100 | no | 0.791 | pass |
| P7 | h2 | carries |  | 10000 | 0.8725 | 0.0040 | 0.1235 | yes | 2.153 | FAIL |
| P7 | h2 | depends |  | 10000 | 0.8839 | 0.0020 | 0.1141 | yes | 1.722 | FAIL |
| P7 | h5 | large | 0.0 | 2000 | 0.9830 | 0.0060 | 0.0110 | no | 0.793 | pass |
| P7 | h5 | carries |  | 10000 | 0.8729 | 0.0041 | 0.1230 | yes | 2.309 | FAIL |
| P7 | h5 | depends |  | 10000 | 0.8832 | 0.0030 | 0.1138 | yes | 1.744 | FAIL |
| P7 | h10 | large | 0.0 | 2000 | 0.9740 | 0.0140 | 0.0120 | no | 0.867 | pass |
| P7 | h10 | carries |  | 10000 | 0.7505 | 0.0000 | 0.2495 | yes | 2.646 | FAIL |
| P7 | h10 | depends |  | 10000 | 0.8068 | 0.0000 | 0.1932 | yes | 1.821 | FAIL |
| P8 | n20 | carries |  | 10000 | 0.9020 | 0.0021 | 0.0959 | yes | 1.488 | FAIL |
| P8 | n20 | depends |  | 10000 | 0.8956 | 0.0010 | 0.1034 | yes | 1.576 | FAIL |
| P8 | n40 | large | 0.0 | 2000 | 0.9630 | 0.0050 | 0.0320 | no | 0.938 | pass |
| P8 | n40 | carries |  | 2000 | 0.9530 | 0.0105 | 0.0365 | no | 0.989 | pass |
| P8 | n40 | depends |  | 2000 | 0.9500 | 0.0090 | 0.0410 | no | 0.998 | pass |
| P8 | n80 | large | 0.0 | 2000 | 0.9630 | 0.0115 | 0.0255 | no | 0.939 | pass |
| P8 | n80 | carries |  | 2000 | 0.9510 | 0.0040 | 0.0450 | no | 0.991 | pass |
| P8 | n80 | depends |  | 2000 | 0.9545 | 0.0055 | 0.0400 | no | 0.983 | pass |
| P8 | n160 | large | 0.0 | 2000 | 0.9590 | 0.0280 | 0.0130 | no | 0.951 | pass |
| P8 | n160 | carries |  | 10000 | 0.9081 | 0.0006 | 0.0913 | yes | 1.419 | FAIL |
| P8 | n160 | depends |  | 2000 | 0.9615 | 0.0025 | 0.0360 | no | 0.933 | pass |
| P8 | n320 | large | 0.0 | 2000 | 0.9535 | 0.0285 | 0.0180 | no | 0.978 | pass |
| P8 | n320 | carries |  | 10000 | 0.9075 | 0.0006 | 0.0919 | yes | 1.423 | FAIL |
| P8 | n320 | depends |  | 2000 | 0.9630 | 0.0015 | 0.0355 | no | 0.929 | pass |
| P8 | h2 | large | 0.0 | 10000 | 0.9309 | 0.0481 | 0.0210 | yes | 1.118 | FAIL |
| P8 | h2 | carries |  | 10000 | 0.8774 | 0.0034 | 0.1192 | yes | 2.093 | FAIL |
| P8 | h2 | depends |  | 10000 | 0.8846 | 0.0021 | 0.1133 | yes | 1.695 | FAIL |
| P8 | h5 | large | 0.0 | 10000 | 0.9262 | 0.0509 | 0.0229 | yes | 1.148 | FAIL |
| P8 | h5 | carries |  | 10000 | 0.8756 | 0.0031 | 0.1213 | yes | 2.300 | FAIL |
| P8 | h5 | depends |  | 10000 | 0.8862 | 0.0019 | 0.1119 | yes | 1.723 | FAIL |
| P8 | h10 | large | 0.0 | 10000 | 0.9196 | 0.0576 | 0.0228 | yes | 1.158 | FAIL |
| P8 | h10 | carries |  | 10000 | 0.7555 | 0.0000 | 0.2445 | yes | 2.615 | FAIL |
| P8 | h10 | depends |  | 10000 | 0.8089 | 0.0000 | 0.1911 | yes | 1.782 | FAIL |
| P9 | n20 | carries |  | 10000 | 0.8995 | 0.0023 | 0.0982 | yes | 1.532 | FAIL |
| P9 | n20 | depends | 0.2 | 10000 | 0.9527 | 0.0082 | 0.0391 | yes | 1.009 | FAIL |
| P9 | n40 | large |  | 2000 | 0.9670 | 0.0075 | 0.0255 | no | 0.898 | pass |
| P9 | n40 | carries |  | 2000 | 0.9565 | 0.0110 | 0.0325 | no | 0.950 | pass |
| P9 | n40 | depends | 0.2 | 10000 | 0.9485 | 0.0069 | 0.0446 | yes | 1.066 | FAIL |
| P9 | n80 | large |  | 2000 | 0.9555 | 0.0040 | 0.0405 | no | 0.951 | pass |
| P9 | n80 | carries |  | 2000 | 0.9510 | 0.0035 | 0.0455 | no | 0.989 | pass |
| P9 | n80 | depends | 0.2 | 10000 | 0.9531 | 0.0042 | 0.0427 | yes | 1.049 | FAIL |
| P9 | n160 | large |  | 2000 | 0.9390 | 0.0030 | 0.0580 | no | 1.073 | pass |
| P9 | n160 | carries |  | 10000 | 0.9103 | 0.0012 | 0.0885 | yes | 1.392 | FAIL |
| P9 | n160 | depends | 0.2 | 10000 | 0.9139 | 0.0010 | 0.0851 | yes | 1.490 | FAIL |
| P9 | n320 | large |  | 10000 | 0.9274 | 0.0045 | 0.0681 | yes | 1.140 | pass |
| P9 | n320 | carries |  | 10000 | 0.9049 | 0.0014 | 0.0937 | yes | 1.432 | FAIL |
| P9 | n320 | depends | 0.2 | 10000 | 0.9080 | 0.0013 | 0.0907 | yes | 1.556 | FAIL |
| P9 | h2 | large |  | 2000 | 0.9685 | 0.0265 | 0.0050 | no | 0.881 | pass |
| P9 | h2 | carries |  | 10000 | 0.8748 | 0.0045 | 0.1207 | yes | 2.181 | FAIL |
| P9 | h2 | depends | 0.2 | 10000 | 0.8927 | 0.0019 | 0.1054 | yes | 1.769 | FAIL |
| P9 | h5 | large |  | 10000 | 0.8929 | 0.0024 | 0.1047 | yes | 1.416 | FAIL |
| P9 | h5 | carries |  | 10000 | 0.8739 | 0.0034 | 0.1227 | yes | 2.354 | FAIL |
| P9 | h5 | depends | 0.2 | 10000 | 0.8744 | 0.0025 | 0.1231 | yes | 2.427 | FAIL |
| P9 | h10 | large |  | 10000 | 0.7531 | 0.0000 | 0.2469 | yes | 2.268 | FAIL |
| P9 | h10 | carries |  | 10000 | 0.7503 | 0.0000 | 0.2497 | yes | 2.655 | FAIL |
| P9 | h10 | depends | 0.2 | 10000 | 0.7509 | 0.0000 | 0.2491 | yes | 2.739 | FAIL |
| P10 | n20 | carries |  | 10000 | 0.8998 | 0.0017 | 0.0985 | yes | 1.502 | FAIL |
| P10 | n20 | depends | 0.2 | 2000 | 0.9645 | 0.0040 | 0.0315 | no | 0.962 | pass |
| P10 | n40 | large |  | 2000 | 0.9655 | 0.0045 | 0.0300 | no | 0.914 | pass |
| P10 | n40 | carries |  | 2000 | 0.9580 | 0.0090 | 0.0330 | no | 0.956 | pass |
| P10 | n40 | depends | 0.2 | 10000 | 0.9508 | 0.0083 | 0.0409 | yes | 1.029 | FAIL |
| P10 | n80 | large |  | 2000 | 0.9375 | 0.0050 | 0.0575 | no | 1.081 | pass |
| P10 | n80 | carries |  | 2000 | 0.9480 | 0.0030 | 0.0490 | no | 1.013 | pass |
| P10 | n80 | depends | 0.2 | 10000 | 0.9494 | 0.0023 | 0.0483 | yes | 1.100 | FAIL |
| P10 | n160 | large |  | 2000 | 0.9400 | 0.0035 | 0.0565 | no | 1.064 | pass |
| P10 | n160 | carries |  | 10000 | 0.9074 | 0.0011 | 0.0915 | yes | 1.393 | FAIL |
| P10 | n160 | depends | 0.2 | 10000 | 0.9112 | 0.0009 | 0.0879 | yes | 1.487 | FAIL |
| P10 | n320 | large |  | 10000 | 0.9303 | 0.0035 | 0.0662 | yes | 1.139 | pass |
| P10 | n320 | carries |  | 10000 | 0.9077 | 0.0007 | 0.0916 | yes | 1.453 | FAIL |
| P10 | n320 | depends | 0.2 | 10000 | 0.9113 | 0.0005 | 0.0882 | yes | 1.566 | FAIL |
| P10 | h2 | large |  | 10000 | 0.9257 | 0.0578 | 0.0165 | yes | 1.174 | pass |
| P10 | h2 | carries |  | 10000 | 0.8747 | 0.0037 | 0.1216 | yes | 2.138 | FAIL |
| P10 | h2 | depends | 0.2 | 10000 | 0.8925 | 0.0020 | 0.1055 | yes | 1.699 | FAIL |
| P10 | h5 | large |  | 10000 | 0.9299 | 0.0042 | 0.0659 | yes | 1.132 | pass |
| P10 | h5 | carries |  | 10000 | 0.8737 | 0.0032 | 0.1231 | yes | 2.292 | FAIL |
| P10 | h5 | depends | 0.2 | 10000 | 0.8746 | 0.0024 | 0.1230 | yes | 2.396 | FAIL |
| P10 | h10 | large |  | 10000 | 0.7510 | 0.0000 | 0.2490 | yes | 2.167 | FAIL |
| P10 | h10 | carries |  | 10000 | 0.7466 | 0.0000 | 0.2534 | yes | 2.618 | FAIL |
| P10 | h10 | depends | 0.2 | 10000 | 0.7479 | 0.0000 | 0.2521 | yes | 2.687 | FAIL |
| P11 | n20 | carries |  | 10000 | 0.8968 | 0.0015 | 0.1017 | yes | 1.553 | FAIL |
| P11 | n20 | depends | 0.0 | 10000 | 0.9425 | 0.0417 | 0.0158 | yes | 1.031 | FAIL |
| P11 | n40 | large |  | 10000 | 0.8948 | 0.1031 | 0.0021 | yes | 1.394 | FAIL |
| P11 | n40 | carries |  | 2000 | 0.9580 | 0.0060 | 0.0360 | no | 0.971 | pass |
| P11 | n40 | depends | 0.0 | 10000 | 0.9487 | 0.0384 | 0.0129 | yes | 1.007 | FAIL |
| P11 | n80 | large |  | 10000 | 0.8805 | 0.1172 | 0.0023 | yes | 1.622 | FAIL |
| P11 | n80 | carries |  | 2000 | 0.9515 | 0.0020 | 0.0465 | no | 0.989 | pass |
| P11 | n80 | depends | 0.0 | 10000 | 0.9336 | 0.0640 | 0.0024 | yes | 1.249 | FAIL |
| P11 | n160 | large |  | 10000 | 0.8675 | 0.1306 | 0.0019 | yes | 1.813 | FAIL |
| P11 | n160 | carries |  | 10000 | 0.9068 | 0.0010 | 0.0922 | yes | 1.384 | FAIL |
| P11 | n160 | depends | 0.0 | 10000 | 0.9039 | 0.0954 | 0.0007 | yes | 1.596 | FAIL |
| P11 | n320 | large |  | 10000 | 0.8643 | 0.1334 | 0.0023 | yes | 1.863 | FAIL |
| P11 | n320 | carries |  | 10000 | 0.9040 | 0.0012 | 0.0948 | yes | 1.462 | FAIL |
| P11 | n320 | depends | 0.0 | 10000 | 0.8998 | 0.0996 | 0.0006 | yes | 1.680 | FAIL |
| P11 | h2 | large |  | 10000 | 0.8510 | 0.1468 | 0.0022 | yes | 2.204 | FAIL |
| P11 | h2 | carries |  | 10000 | 0.8723 | 0.0049 | 0.1228 | yes | 2.242 | FAIL |
| P11 | h2 | depends | 0.0 | 10000 | 0.8726 | 0.1244 | 0.0030 | yes | 2.599 | FAIL |
| P11 | h5 | large |  | 10000 | 0.8495 | 0.1486 | 0.0019 | yes | 2.203 | FAIL |
| P11 | h5 | carries |  | 10000 | 0.8719 | 0.0040 | 0.1241 | yes | 2.376 | FAIL |
| P11 | h5 | depends | 0.0 | 10000 | 0.8733 | 0.1232 | 0.0035 | yes | 2.567 | FAIL |
| P11 | h10 | large |  | 10000 | 0.6891 | 0.3109 | 0.0000 | yes | 2.793 | FAIL |
| P11 | h10 | carries |  | 10000 | 0.7531 | 0.0000 | 0.2469 | yes | 2.687 | FAIL |
| P11 | h10 | depends | 0.0 | 10000 | 0.7522 | 0.2478 | 0.0000 | yes | 2.983 | FAIL |
| P12 | n20 | carries |  | 10000 | 0.8998 | 0.0015 | 0.0987 | yes | 1.525 | FAIL |
| P12 | n20 | depends | 0.0 | 10000 | 0.9581 | 0.0341 | 0.0078 | yes | 0.975 | pass |
| P12 | n40 | large |  | 10000 | 0.9031 | 0.0936 | 0.0033 | yes | 1.348 | FAIL |
| P12 | n40 | carries |  | 2000 | 0.9650 | 0.0105 | 0.0245 | no | 0.911 | pass |
| P12 | n40 | depends | 0.0 | 10000 | 0.9503 | 0.0367 | 0.0130 | yes | 0.998 | pass |
| P12 | n80 | large |  | 10000 | 0.8880 | 0.1102 | 0.0018 | yes | 1.584 | FAIL |
| P12 | n80 | carries |  | 2000 | 0.9565 | 0.0045 | 0.0390 | no | 0.947 | pass |
| P12 | n80 | depends | 0.0 | 10000 | 0.9442 | 0.0521 | 0.0037 | yes | 1.143 | FAIL |
| P12 | n160 | large |  | 10000 | 0.9102 | 0.0863 | 0.0035 | yes | 1.327 | FAIL |
| P12 | n160 | carries |  | 10000 | 0.9125 | 0.0010 | 0.0865 | yes | 1.353 | FAIL |
| P12 | n160 | depends | 0.0 | 10000 | 0.9125 | 0.0865 | 0.0010 | yes | 1.463 | FAIL |
| P12 | n320 | large |  | 10000 | 0.9143 | 0.0814 | 0.0043 | yes | 1.279 | FAIL |
| P12 | n320 | carries |  | 10000 | 0.9087 | 0.0011 | 0.0902 | yes | 1.427 | FAIL |
| P12 | n320 | depends | 0.0 | 10000 | 0.9066 | 0.0924 | 0.0010 | yes | 1.565 | FAIL |
| P12 | h2 | large |  | 10000 | 0.9146 | 0.0815 | 0.0039 | yes | 1.293 | FAIL |
| P12 | h2 | carries |  | 10000 | 0.8835 | 0.0044 | 0.1121 | yes | 2.145 | FAIL |
| P12 | h2 | depends | 0.0 | 10000 | 0.8844 | 0.1134 | 0.0022 | yes | 2.556 | FAIL |
| P12 | h5 | large |  | 10000 | 0.9053 | 0.0905 | 0.0042 | yes | 1.381 | FAIL |
| P12 | h5 | carries |  | 10000 | 0.8831 | 0.0040 | 0.1129 | yes | 2.272 | FAIL |
| P12 | h5 | depends | 0.0 | 10000 | 0.8829 | 0.1143 | 0.0028 | yes | 2.520 | FAIL |
| P12 | h10 | large |  | 10000 | 0.8130 | 0.1867 | 0.0003 | yes | 1.862 | FAIL |
| P12 | h10 | carries |  | 10000 | 0.7503 | 0.0000 | 0.2497 | yes | 2.625 | FAIL |
| P12 | h10 | depends | 0.0 | 10000 | 0.7492 | 0.2508 | 0.0000 | yes | 2.923 | FAIL |
| P13 | n20 | carries |  | 10000 | 0.9032 | 0.0013 | 0.0955 | yes | 1.489 | FAIL |
| P13 | n20 | depends |  | 2000 | 0.9445 | 0.0485 | 0.0070 | no | 1.011 | pass |
| P13 | n40 | large |  | 10000 | 0.9009 | 0.0024 | 0.0967 | yes | 1.484 | FAIL |
| P13 | n40 | carries |  | 10000 | 0.9123 | 0.0030 | 0.0847 | yes | 1.314 | FAIL |
| P13 | n40 | depends |  | 10000 | 0.9043 | 0.0027 | 0.0930 | yes | 1.456 | FAIL |
| P13 | n80 | large |  | 2000 | 0.9415 | 0.0105 | 0.0480 | no | 1.077 | pass |
| P13 | n80 | carries |  | 2000 | 0.9510 | 0.0035 | 0.0455 | no | 0.978 | pass |
| P13 | n80 | depends |  | 2000 | 0.9520 | 0.0025 | 0.0455 | no | 0.982 | pass |
| P13 | n160 | large |  | 10000 | 0.9355 | 0.0038 | 0.0607 | yes | 1.089 | pass |
| P13 | n160 | carries |  | 10000 | 0.9166 | 0.0009 | 0.0825 | yes | 1.323 | FAIL |
| P13 | n160 | depends |  | 10000 | 0.9170 | 0.0008 | 0.0822 | yes | 1.323 | FAIL |
| P13 | n320 | large |  | 10000 | 0.9252 | 0.0036 | 0.0712 | yes | 1.168 | pass |
| P13 | n320 | carries |  | 10000 | 0.9148 | 0.0004 | 0.0848 | yes | 1.357 | FAIL |
| P13 | n320 | depends |  | 10000 | 0.9146 | 0.0004 | 0.0850 | yes | 1.358 | FAIL |
| P13 | h2 | large |  | 10000 | 0.9301 | 0.0506 | 0.0193 | yes | 1.130 | pass |
| P13 | h2 | carries |  | 10000 | 0.8804 | 0.0047 | 0.1149 | yes | 2.074 | FAIL |
| P13 | h2 | depends |  | 10000 | 0.8903 | 0.0021 | 0.1076 | yes | 1.614 | FAIL |
| P13 | h5 | large |  | 10000 | 0.8845 | 0.0038 | 0.1117 | yes | 1.729 | FAIL |
| P13 | h5 | carries |  | 10000 | 0.8820 | 0.0036 | 0.1144 | yes | 1.970 | FAIL |
| P13 | h5 | depends |  | 10000 | 0.8828 | 0.0024 | 0.1148 | yes | 1.980 | FAIL |
| P13 | h10 | large |  | 10000 | 0.7472 | 0.0000 | 0.2528 | yes | 2.612 | FAIL |
| P13 | h10 | carries |  | 10000 | 0.7492 | 0.0000 | 0.2508 | yes | 2.635 | FAIL |
| P13 | h10 | depends |  | 10000 | 0.7491 | 0.0000 | 0.2509 | yes | 2.646 | FAIL |

## The Multiplier Each Row Would Have Required (It Sets None)

| Row | Failing core cells | Largest multiplier needed | Multiplier | Confirmation | Goes to the PI |
|---|---|---|---|---|---|
| n20 | P1 carries, P1 depends, P2 carries, P2 depends, P3 carries, P3 depends, P4 carries, P4 depends, P5 carries, P5 depends, P6 carries, P6 depends, P7 carries, P7 depends, P8 carries, P8 depends, P9 carries, P9 depends, P10 carries, P11 carries, P11 depends, P12 carries, P13 carries | 1.811 | 1.85 | not needed | yes |
| n40 | P9 depends, P10 depends, P11 large, P11 depends, P12 large, P13 large, P13 carries, P13 depends | 1.484 | 1.50 | seed 2 at 1.50: passed (lowest coverage 0.9480) | no |
| n80 | P1 carries, P4 carries, P9 depends, P10 depends, P11 large, P11 depends, P12 large, P12 depends | 1.622 | 1.65 | not needed | yes |
| n160 | P1 carries, P1 depends, P2 carries, P2 depends, P3 carries, P3 depends, P4 carries, P4 depends, P5 carries, P5 depends, P6 carries, P6 depends, P7 carries, P8 carries, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 carries, P13 depends | 1.813 | 1.85 | not needed | yes |
| n320 | P1 carries, P1 depends, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 carries, P4 depends, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P8 carries, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 carries, P13 depends | 1.863 | 1.90 | not needed | yes |
| h2 | P1 large, P1 carries, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 large, P4 carries, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P8 depends, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 carries, P13 depends | 2.599 | 2.60 | not needed | yes |
| h5 | P1 large, P1 carries, P1 depends, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 carries, P4 depends, P5 large, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P8 depends, P9 large, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 large, P13 carries, P13 depends | 2.567 | 2.60 | not needed | yes |
| h10 | P1 large, P1 carries, P1 depends, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 large, P4 carries, P4 depends, P5 large, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P8 depends, P9 large, P9 carries, P9 depends, P10 large, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 large, P13 carries, P13 depends | 2.983 | 3.00 | not needed | yes |

## Harm-Level Core Cells: Coverage Where the Level Is Read, and Over All Experiments

The criterion judges a harm-level row on the experiments in which the count rule lets the level be read (the first three columns of numbers). Beside it, as description, the same intervals over every experiment of the same sample, read or not.

| Scenario | Row | Reading | Share read | Judged on | Coverage, level read | Experiments, all | Coverage, all | Wholly above, all | Wholly below, all |
|---|---|---|---|---|---|---|---|---|---|
| P1 | h2 | large | 1.000 | 10000 | 0.8959 | 10000 | 0.8959 | 0.1031 | 0.0010 |
| P1 | h2 | carries | 1.000 | 10000 | 0.8754 | 10000 | 0.8754 | 0.0037 | 0.1209 |
| P1 | h2 | depends | 1.000 | 2000 | 0.9920 | 2000 | 0.9920 | 0.0015 | 0.0065 |
| P1 | h5 | large | 0.993 | 10000 | 0.9075 | 10000 | 0.9078 | 0.0020 | 0.0902 |
| P1 | h5 | carries | 0.993 | 10000 | 0.8765 | 10000 | 0.8759 | 0.0030 | 0.1211 |
| P1 | h5 | depends | 0.993 | 10000 | 0.8780 | 10000 | 0.8775 | 0.0022 | 0.1203 |
| P1 | h10 | large | 0.193 | 10000 | 0.7538 | 10000 | 0.8784 | 0.0031 | 0.1185 |
| P1 | h10 | carries | 0.193 | 10000 | 0.7523 | 10000 | 0.8770 | 0.0028 | 0.1202 |
| P1 | h10 | depends | 0.193 | 10000 | 0.7522 | 10000 | 0.8777 | 0.0026 | 0.1197 |
| P2 | h2 | large | 1.000 | 10000 | 0.8921 | 10000 | 0.8921 | 0.0022 | 0.1057 |
| P2 | h2 | carries | 1.000 | 10000 | 0.8769 | 10000 | 0.8769 | 0.0029 | 0.1202 |
| P2 | h2 | depends | 1.000 | 10000 | 0.8764 | 10000 | 0.8764 | 0.0021 | 0.1215 |
| P2 | h5 | large | 0.993 | 10000 | 0.8779 | 10000 | 0.8776 | 0.0026 | 0.1198 |
| P2 | h5 | carries | 0.993 | 10000 | 0.8775 | 10000 | 0.8771 | 0.0026 | 0.1203 |
| P2 | h5 | depends | 0.993 | 10000 | 0.8773 | 10000 | 0.8769 | 0.0023 | 0.1208 |
| P2 | h10 | large | 0.195 | 10000 | 0.7355 | 10000 | 0.8763 | 0.0028 | 0.1209 |
| P2 | h10 | carries | 0.195 | 10000 | 0.7362 | 10000 | 0.8773 | 0.0026 | 0.1201 |
| P2 | h10 | depends | 0.195 | 10000 | 0.7361 | 10000 | 0.8770 | 0.0026 | 0.1204 |
| P3 | h2 | large | 1.000 | 10000 | 0.8791 | 10000 | 0.8791 | 0.0034 | 0.1175 |
| P3 | h2 | carries | 1.000 | 10000 | 0.8754 | 10000 | 0.8754 | 0.0046 | 0.1200 |
| P3 | h2 | depends | 1.000 | 10000 | 0.8763 | 10000 | 0.8763 | 0.0023 | 0.1214 |
| P3 | h5 | large | 0.994 | 10000 | 0.8760 | 10000 | 0.8765 | 0.0040 | 0.1195 |
| P3 | h5 | carries | 0.994 | 10000 | 0.8768 | 10000 | 0.8773 | 0.0035 | 0.1192 |
| P3 | h5 | depends | 0.994 | 10000 | 0.8773 | 10000 | 0.8778 | 0.0028 | 0.1194 |
| P3 | h10 | large | 0.194 | 10000 | 0.7427 | 10000 | 0.8770 | 0.0039 | 0.1191 |
| P3 | h10 | carries | 0.194 | 10000 | 0.7431 | 10000 | 0.8779 | 0.0042 | 0.1179 |
| P3 | h10 | depends | 0.194 | 10000 | 0.7430 | 10000 | 0.8783 | 0.0037 | 0.1180 |
| P4 | h2 | large | 1.000 | 10000 | 0.9248 | 10000 | 0.9248 | 0.0680 | 0.0072 |
| P4 | h2 | carries | 1.000 | 10000 | 0.8770 | 10000 | 0.8770 | 0.0050 | 0.1180 |
| P4 | h2 | depends | 1.000 | 2000 | 0.9920 | 2000 | 0.9920 | 0.0000 | 0.0080 |
| P4 | h5 | large | 0.992 | 2000 | 0.9350 | 2000 | 0.9350 | 0.0065 | 0.0585 |
| P4 | h5 | carries | 0.995 | 10000 | 0.8787 | 10000 | 0.8777 | 0.0033 | 0.1190 |
| P4 | h5 | depends | 0.995 | 10000 | 0.8796 | 10000 | 0.8786 | 0.0026 | 0.1188 |
| P4 | h10 | large | 0.193 | 10000 | 0.7628 | 10000 | 0.8802 | 0.0040 | 0.1158 |
| P4 | h10 | carries | 0.193 | 10000 | 0.7599 | 10000 | 0.8792 | 0.0036 | 0.1172 |
| P4 | h10 | depends | 0.193 | 10000 | 0.7610 | 10000 | 0.8809 | 0.0027 | 0.1164 |
| P5 | h2 | large | 1.000 | 10000 | 0.9374 | 10000 | 0.9374 | 0.0040 | 0.0586 |
| P5 | h2 | carries | 1.000 | 10000 | 0.8820 | 10000 | 0.8820 | 0.0038 | 0.1142 |
| P5 | h2 | depends | 1.000 | 10000 | 0.8825 | 10000 | 0.8825 | 0.0021 | 0.1154 |
| P5 | h5 | large | 0.995 | 10000 | 0.8820 | 10000 | 0.8818 | 0.0029 | 0.1153 |
| P5 | h5 | carries | 0.995 | 10000 | 0.8803 | 10000 | 0.8799 | 0.0032 | 0.1169 |
| P5 | h5 | depends | 0.995 | 10000 | 0.8804 | 10000 | 0.8800 | 0.0027 | 0.1173 |
| P5 | h10 | large | 0.192 | 10000 | 0.7476 | 10000 | 0.8823 | 0.0029 | 0.1148 |
| P5 | h10 | carries | 0.192 | 10000 | 0.7516 | 10000 | 0.8830 | 0.0032 | 0.1138 |
| P5 | h10 | depends | 0.192 | 10000 | 0.7512 | 10000 | 0.8831 | 0.0029 | 0.1140 |
| P6 | h2 | large | 1.000 | 10000 | 0.8871 | 10000 | 0.8871 | 0.0032 | 0.1097 |
| P6 | h2 | carries | 1.000 | 10000 | 0.8750 | 10000 | 0.8750 | 0.0039 | 0.1211 |
| P6 | h2 | depends | 1.000 | 10000 | 0.8751 | 10000 | 0.8751 | 0.0023 | 0.1226 |
| P6 | h5 | large | 0.995 | 10000 | 0.8735 | 10000 | 0.8734 | 0.0034 | 0.1232 |
| P6 | h5 | carries | 0.995 | 10000 | 0.8749 | 10000 | 0.8747 | 0.0031 | 0.1222 |
| P6 | h5 | depends | 0.995 | 10000 | 0.8754 | 10000 | 0.8752 | 0.0025 | 0.1223 |
| P6 | h10 | large | 0.198 | 10000 | 0.7475 | 10000 | 0.8772 | 0.0029 | 0.1199 |
| P6 | h10 | carries | 0.198 | 10000 | 0.7491 | 10000 | 0.8780 | 0.0028 | 0.1192 |
| P6 | h10 | depends | 0.198 | 10000 | 0.7485 | 10000 | 0.8778 | 0.0028 | 0.1194 |
| P7 | h2 | large | 1.000 | 2000 | 0.9840 | 2000 | 0.9840 | 0.0060 | 0.0100 |
| P7 | h2 | carries | 1.000 | 10000 | 0.8725 | 10000 | 0.8725 | 0.0040 | 0.1235 |
| P7 | h2 | depends | 1.000 | 10000 | 0.8839 | 10000 | 0.8839 | 0.0020 | 0.1141 |
| P7 | h5 | large | 0.996 | 2000 | 0.9830 | 2000 | 0.9830 | 0.0060 | 0.0110 |
| P7 | h5 | carries | 0.994 | 10000 | 0.8729 | 10000 | 0.8726 | 0.0041 | 0.1233 |
| P7 | h5 | depends | 0.994 | 10000 | 0.8832 | 10000 | 0.8831 | 0.0030 | 0.1139 |
| P7 | h10 | large | 0.197 | 2000 | 0.9740 | 2000 | 0.9845 | 0.0075 | 0.0080 |
| P7 | h10 | carries | 0.191 | 10000 | 0.7505 | 10000 | 0.8761 | 0.0036 | 0.1203 |
| P7 | h10 | depends | 0.191 | 10000 | 0.8068 | 10000 | 0.9082 | 0.0025 | 0.0893 |
| P8 | h2 | large | 1.000 | 10000 | 0.9309 | 10000 | 0.9309 | 0.0481 | 0.0210 |
| P8 | h2 | carries | 1.000 | 10000 | 0.8774 | 10000 | 0.8774 | 0.0034 | 0.1192 |
| P8 | h2 | depends | 1.000 | 10000 | 0.8846 | 10000 | 0.8846 | 0.0021 | 0.1133 |
| P8 | h5 | large | 0.995 | 10000 | 0.9262 | 10000 | 0.9262 | 0.0508 | 0.0230 |
| P8 | h5 | carries | 0.995 | 10000 | 0.8756 | 10000 | 0.8754 | 0.0031 | 0.1215 |
| P8 | h5 | depends | 0.995 | 10000 | 0.8862 | 10000 | 0.8860 | 0.0019 | 0.1121 |
| P8 | h10 | large | 0.196 | 10000 | 0.9196 | 10000 | 0.8970 | 0.0706 | 0.0324 |
| P8 | h10 | carries | 0.196 | 10000 | 0.7555 | 10000 | 0.8774 | 0.0032 | 0.1194 |
| P8 | h10 | depends | 0.196 | 10000 | 0.8089 | 10000 | 0.9106 | 0.0023 | 0.0871 |
| P9 | h2 | large | 1.000 | 2000 | 0.9685 | 2000 | 0.9685 | 0.0265 | 0.0050 |
| P9 | h2 | carries | 1.000 | 10000 | 0.8748 | 10000 | 0.8748 | 0.0045 | 0.1207 |
| P9 | h2 | depends | 1.000 | 10000 | 0.8927 | 10000 | 0.8927 | 0.0019 | 0.1054 |
| P9 | h5 | large | 0.994 | 10000 | 0.8929 | 10000 | 0.8932 | 0.0024 | 0.1044 |
| P9 | h5 | carries | 0.994 | 10000 | 0.8739 | 10000 | 0.8740 | 0.0034 | 0.1226 |
| P9 | h5 | depends | 0.994 | 10000 | 0.8744 | 10000 | 0.8746 | 0.0025 | 0.1229 |
| P9 | h10 | large | 0.196 | 10000 | 0.7531 | 10000 | 0.8753 | 0.0035 | 0.1212 |
| P9 | h10 | carries | 0.196 | 10000 | 0.7503 | 10000 | 0.8747 | 0.0039 | 0.1214 |
| P9 | h10 | depends | 0.196 | 10000 | 0.7509 | 10000 | 0.8749 | 0.0038 | 0.1213 |
| P10 | h2 | large | 1.000 | 10000 | 0.9257 | 10000 | 0.9257 | 0.0578 | 0.0165 |
| P10 | h2 | carries | 1.000 | 10000 | 0.8747 | 10000 | 0.8747 | 0.0037 | 0.1216 |
| P10 | h2 | depends | 1.000 | 10000 | 0.8925 | 10000 | 0.8925 | 0.0020 | 0.1055 |
| P10 | h5 | large | 0.994 | 10000 | 0.9299 | 10000 | 0.9301 | 0.0041 | 0.0658 |
| P10 | h5 | carries | 0.994 | 10000 | 0.8737 | 10000 | 0.8737 | 0.0031 | 0.1232 |
| P10 | h5 | depends | 0.994 | 10000 | 0.8746 | 10000 | 0.8746 | 0.0023 | 0.1231 |
| P10 | h10 | large | 0.197 | 10000 | 0.7510 | 10000 | 0.8755 | 0.0035 | 0.1210 |
| P10 | h10 | carries | 0.197 | 10000 | 0.7466 | 10000 | 0.8755 | 0.0030 | 0.1215 |
| P10 | h10 | depends | 0.197 | 10000 | 0.7479 | 10000 | 0.8764 | 0.0030 | 0.1206 |
| P11 | h2 | large | 1.000 | 10000 | 0.8510 | 10000 | 0.8510 | 0.1468 | 0.0022 |
| P11 | h2 | carries | 1.000 | 10000 | 0.8723 | 10000 | 0.8723 | 0.0049 | 0.1228 |
| P11 | h2 | depends | 1.000 | 10000 | 0.8726 | 10000 | 0.8726 | 0.1244 | 0.0030 |
| P11 | h5 | large | 0.995 | 10000 | 0.8495 | 10000 | 0.8497 | 0.1484 | 0.0019 |
| P11 | h5 | carries | 0.995 | 10000 | 0.8719 | 10000 | 0.8714 | 0.0040 | 0.1246 |
| P11 | h5 | depends | 0.995 | 10000 | 0.8733 | 10000 | 0.8729 | 0.1236 | 0.0035 |
| P11 | h10 | large | 0.193 | 10000 | 0.6891 | 10000 | 0.8449 | 0.1523 | 0.0028 |
| P11 | h10 | carries | 0.193 | 10000 | 0.7531 | 10000 | 0.8727 | 0.0048 | 0.1225 |
| P11 | h10 | depends | 0.193 | 10000 | 0.7522 | 10000 | 0.8717 | 0.1240 | 0.0043 |
| P12 | h2 | large | 1.000 | 10000 | 0.9146 | 10000 | 0.9146 | 0.0815 | 0.0039 |
| P12 | h2 | carries | 1.000 | 10000 | 0.8835 | 10000 | 0.8835 | 0.0044 | 0.1121 |
| P12 | h2 | depends | 1.000 | 10000 | 0.8844 | 10000 | 0.8844 | 0.1134 | 0.0022 |
| P12 | h5 | large | 0.995 | 10000 | 0.9053 | 10000 | 0.9051 | 0.0907 | 0.0042 |
| P12 | h5 | carries | 0.995 | 10000 | 0.8831 | 10000 | 0.8830 | 0.0040 | 0.1130 |
| P12 | h5 | depends | 0.995 | 10000 | 0.8829 | 10000 | 0.8828 | 0.1144 | 0.0028 |
| P12 | h10 | large | 0.192 | 10000 | 0.8130 | 10000 | 0.8862 | 0.1065 | 0.0073 |
| P12 | h10 | carries | 0.192 | 10000 | 0.7503 | 10000 | 0.8842 | 0.0042 | 0.1116 |
| P12 | h10 | depends | 0.192 | 10000 | 0.7492 | 10000 | 0.8835 | 0.1127 | 0.0038 |
| P13 | h2 | large | 1.000 | 10000 | 0.9301 | 10000 | 0.9301 | 0.0506 | 0.0193 |
| P13 | h2 | carries | 1.000 | 10000 | 0.8804 | 10000 | 0.8804 | 0.0047 | 0.1149 |
| P13 | h2 | depends | 1.000 | 10000 | 0.8903 | 10000 | 0.8903 | 0.0021 | 0.1076 |
| P13 | h5 | large | 0.995 | 10000 | 0.8845 | 10000 | 0.8842 | 0.0038 | 0.1120 |
| P13 | h5 | carries | 0.995 | 10000 | 0.8820 | 10000 | 0.8816 | 0.0036 | 0.1148 |
| P13 | h5 | depends | 0.995 | 10000 | 0.8828 | 10000 | 0.8824 | 0.0024 | 0.1152 |
| P13 | h10 | large | 0.194 | 10000 | 0.7472 | 10000 | 0.8794 | 0.0044 | 0.1162 |
| P13 | h10 | carries | 0.194 | 10000 | 0.7492 | 10000 | 0.8810 | 0.0039 | 0.1151 |
| P13 | h10 | depends | 0.194 | 10000 | 0.7491 | 10000 | 0.8814 | 0.0034 | 0.1152 |

## Stress Cells Under 92.5 Percent (Stated, Not Repaired)

| Scenario | Row | Statistic | Coverage | Experiments |
|---|---|---|---|---|
| T1 | n20 | carries | 0.8855 | 2000 |
| T1 | n20 | depends | 0.8995 | 2000 |
| T1 | n20 | carried_margin | 0.9100 | 2000 |
| T1 | n20 | own_margin | 0.9230 | 2000 |
| T1 | n20 | shuffled_vs_yardstick | 0.9230 | 2000 |
| T1 | n20 | carried_added | 0.9050 | 2000 |
| T1 | n20 | pooled_retention | 0.8150 | 2000 |
| T1 | n40 | shuffled_vs_yardstick | 0.9215 | 2000 |
| T1 | n40 | pooled_retention | 0.8110 | 2000 |
| T1 | n80 | own_margin | 0.9190 | 2000 |
| T1 | n80 | shuffled_vs_yardstick | 0.9240 | 2000 |
| T1 | n80 | pooled_retention | 0.8095 | 2000 |
| T1 | n160 | carries | 0.9070 | 2000 |
| T1 | n160 | depends | 0.9075 | 2000 |
| T1 | n160 | kappa | 0.9010 | 2000 |
| T1 | n160 | shuffled_vs_yardstick | 0.9220 | 2000 |
| T1 | n160 | pooled_retention | 0.8115 | 2000 |
| T1 | n320 | carries | 0.9040 | 2000 |
| T1 | n320 | depends | 0.9050 | 2000 |
| T1 | n320 | kappa | 0.8915 | 2000 |
| T1 | n320 | shuffled_vs_yardstick | 0.9230 | 2000 |
| T1 | n320 | carried_added | 0.9230 | 2000 |
| T1 | n320 | pooled_retention | 0.8075 | 2000 |
| T1 | h2 | carries | 0.8215 | 2000 |
| T1 | h2 | depends | 0.8270 | 2000 |
| T1 | h2 | carried_margin | 0.8355 | 2000 |
| T1 | h2 | kappa | 0.8290 | 2000 |
| T1 | h2 | shuffled_vs_yardstick | 0.9240 | 2000 |
| T1 | h2 | carried_added | 0.8130 | 2000 |
| T1 | h2 | pooled_retention | 0.8010 | 2000 |
| T1 | h5 | large | 0.8535 | 2000 |
| T1 | h5 | carries | 0.8110 | 2000 |
| T1 | h5 | depends | 0.8130 | 2000 |
| T1 | h5 | carried_margin | 0.8210 | 2000 |
| T1 | h5 | kappa | 0.8265 | 2000 |
| T1 | h5 | shuffled_vs_yardstick | 0.9160 | 2000 |
| T1 | h5 | carried_added | 0.8150 | 2000 |
| T1 | h5 | pooled_retention | 0.8060 | 2000 |
| T1 | h10 | large | 0.7505 | 2000 |
| T1 | h10 | carries | 0.7415 | 2000 |
| T1 | h10 | depends | 0.7435 | 2000 |
| T1 | h10 | carried_margin | 0.7340 | 2000 |
| T1 | h10 | kappa | 0.7525 | 2000 |
| T1 | h10 | shuffled_vs_yardstick | 0.9070 | 2000 |
| T1 | h10 | carried_added | 0.7295 | 2000 |
| T1 | h10 | pooled_retention | 0.7160 | 2000 |
| T2 | h2 | depends | 0.9245 | 2000 |
| T2 | h10 | large | 0.6149 | 335 |
| T2 | h10 | carries | 0.6269 | 335 |
| T2 | h10 | depends | 0.6239 | 335 |
| T2 | h10 | carried_margin | 0.6179 | 335 |
| T2 | h10 | kappa | 0.7313 | 335 |
| T2 | h10 | shuffled_vs_yardstick | 0.7343 | 335 |
| T2 | h10 | carried_added | 0.6179 | 335 |
| T2 | h10 | pooled_retention | 0.6239 | 335 |
| T3 | n20 | own_margin | 0.9205 | 2000 |
| T3 | n20 | kappa | 0.9140 | 2000 |
| T3 | n20 | shuffled_vs_yardstick | 0.9205 | 2000 |
| T3 | n40 | shuffled_vs_yardstick | 0.9200 | 2000 |
| T3 | n80 | shuffled_vs_yardstick | 0.9220 | 2000 |
| T3 | n80 | pooled_retention | 0.9000 | 2000 |
| T3 | n160 | shuffled_vs_yardstick | 0.9185 | 2000 |
| T3 | n160 | pooled_retention | 0.8920 | 2000 |
| T3 | n320 | kappa | 0.9205 | 2000 |
| T3 | n320 | shuffled_vs_yardstick | 0.9195 | 2000 |
| T3 | n320 | pooled_retention | 0.8920 | 2000 |
| T3 | h2 | carries | 0.9060 | 2000 |
| T3 | h2 | depends | 0.9130 | 2000 |
| T3 | h2 | carried_margin | 0.9235 | 2000 |
| T3 | h2 | own_margin | 0.9145 | 2000 |
| T3 | h2 | kappa | 0.8990 | 2000 |
| T3 | h2 | shuffled_vs_yardstick | 0.9200 | 2000 |
| T3 | h2 | carried_added | 0.9050 | 2000 |
| T3 | h2 | pooled_retention | 0.9070 | 2000 |
| T3 | h5 | large | 0.9245 | 2000 |
| T3 | h5 | carries | 0.9095 | 2000 |
| T3 | h5 | depends | 0.9100 | 2000 |
| T3 | h5 | carried_margin | 0.9180 | 2000 |
| T3 | h5 | kappa | 0.9055 | 2000 |
| T3 | h5 | shuffled_vs_yardstick | 0.9150 | 2000 |
| T3 | h5 | carried_added | 0.9100 | 2000 |
| T3 | h5 | pooled_retention | 0.9055 | 2000 |
| T3 | h10 | large | 0.7895 | 2000 |
| T3 | h10 | carries | 0.7830 | 2000 |
| T3 | h10 | depends | 0.7840 | 2000 |
| T3 | h10 | carried_margin | 0.7825 | 2000 |
| T3 | h10 | kappa | 0.7545 | 2000 |
| T3 | h10 | shuffled_vs_yardstick | 0.8715 | 2000 |
| T3 | h10 | carried_added | 0.7790 | 2000 |
| T3 | h10 | pooled_retention | 0.7760 | 2000 |
| T4 | n20 | large | 0.8945 | 2000 |
| T4 | n20 | carries | 0.9205 | 2000 |
| T4 | n20 | depends | 0.9115 | 2000 |
| T4 | n20 | carried_margin | 0.9065 | 2000 |
| T4 | n20 | own_margin | 0.9070 | 2000 |
| T4 | n20 | shuffled_vs_yardstick | 0.9070 | 2000 |
| T4 | n20 | carried_added | 0.8935 | 2000 |
| T4 | n20 | pooled_retention | 0.8775 | 2000 |
| T4 | n40 | large | 0.8940 | 2000 |
| T4 | n40 | carried_margin | 0.8870 | 2000 |
| T4 | n40 | own_margin | 0.8825 | 2000 |
| T4 | n40 | shuffled_vs_yardstick | 0.9080 | 2000 |
| T4 | n40 | carried_added | 0.8875 | 2000 |
| T4 | n40 | pooled_retention | 0.8780 | 2000 |
| T4 | n80 | large | 0.9230 | 2000 |
| T4 | n80 | carried_margin | 0.9235 | 2000 |
| T4 | n80 | own_margin | 0.9245 | 2000 |
| T4 | n80 | shuffled_vs_yardstick | 0.9075 | 2000 |
| T4 | n80 | carried_added | 0.9245 | 2000 |
| T4 | n80 | pooled_retention | 0.8760 | 2000 |
| T4 | n160 | carries | 0.9115 | 2000 |
| T4 | n160 | depends | 0.9125 | 2000 |
| T4 | n160 | kappa | 0.9220 | 2000 |
| T4 | n160 | shuffled_vs_yardstick | 0.9070 | 2000 |
| T4 | n160 | pooled_retention | 0.8765 | 2000 |
| T4 | n320 | carries | 0.9110 | 2000 |
| T4 | n320 | depends | 0.9110 | 2000 |
| T4 | n320 | carried_margin | 0.9240 | 2000 |
| T4 | n320 | kappa | 0.9085 | 2000 |
| T4 | n320 | shuffled_vs_yardstick | 0.9075 | 2000 |
| T4 | n320 | carried_added | 0.9230 | 2000 |
| T4 | n320 | pooled_retention | 0.8775 | 2000 |
| T4 | h2 | carries | 0.8785 | 2000 |
| T4 | h2 | depends | 0.8790 | 2000 |
| T4 | h2 | carried_margin | 0.8790 | 2000 |
| T4 | h2 | kappa | 0.8750 | 2000 |
| T4 | h2 | shuffled_vs_yardstick | 0.9075 | 2000 |
| T4 | h2 | carried_added | 0.8740 | 2000 |
| T4 | h2 | pooled_retention | 0.8760 | 2000 |
| T4 | h5 | large | 0.9025 | 2000 |
| T4 | h5 | carries | 0.8770 | 2000 |
| T4 | h5 | depends | 0.8790 | 2000 |
| T4 | h5 | carried_margin | 0.8765 | 2000 |
| T4 | h5 | kappa | 0.8715 | 2000 |
| T4 | h5 | shuffled_vs_yardstick | 0.9055 | 2000 |
| T4 | h5 | carried_added | 0.8765 | 2000 |
| T4 | h5 | pooled_retention | 0.8775 | 2000 |
| T4 | h10 | large | 0.7610 | 2000 |
| T4 | h10 | carries | 0.7615 | 2000 |
| T4 | h10 | depends | 0.7615 | 2000 |
| T4 | h10 | carried_margin | 0.7625 | 2000 |
| T4 | h10 | own_margin | 0.9205 | 2000 |
| T4 | h10 | kappa | 0.7720 | 2000 |
| T4 | h10 | shuffled_vs_yardstick | 0.8375 | 2000 |
| T4 | h10 | carried_added | 0.7615 | 2000 |
| T4 | h10 | pooled_retention | 0.7580 | 2000 |
| T5 | n20 | large | 0.7995 | 2000 |
| T5 | n20 | carries | 0.8115 | 2000 |
| T5 | n20 | depends | 0.8130 | 2000 |
| T5 | n20 | carried_margin | 0.8010 | 2000 |
| T5 | n20 | own_margin | 0.9230 | 2000 |
| T5 | n20 | shuffled_vs_yardstick | 0.9230 | 2000 |
| T5 | n20 | carried_added | 0.8010 | 2000 |
| T5 | n20 | pooled_retention | 0.8075 | 2000 |
| T5 | n40 | large | 0.8430 | 2000 |
| T5 | n40 | carries | 0.8695 | 2000 |
| T5 | n40 | depends | 0.8685 | 2000 |
| T5 | n40 | carried_margin | 0.8530 | 2000 |
| T5 | n40 | kappa | 0.9240 | 2000 |
| T5 | n40 | shuffled_vs_yardstick | 0.9230 | 2000 |
| T5 | n40 | carried_added | 0.8600 | 2000 |
| T5 | n40 | pooled_retention | 0.8380 | 2000 |
| T5 | n80 | shuffled_vs_yardstick | 0.9235 | 2000 |
| T5 | n160 | kappa | 0.9110 | 2000 |
| T5 | n160 | shuffled_vs_yardstick | 0.9210 | 2000 |
| T5 | n160 | pooled_retention | 0.9175 | 2000 |
| T5 | n320 | carries | 0.9235 | 2000 |
| T5 | n320 | kappa | 0.9040 | 2000 |
| T5 | n320 | shuffled_vs_yardstick | 0.9240 | 2000 |
| T5 | n320 | pooled_retention | 0.9040 | 2000 |
| T5 | h2 | large | 0.8090 | 2000 |
| T5 | h2 | carries | 0.8130 | 2000 |
| T5 | h2 | depends | 0.8135 | 2000 |
| T5 | h2 | carried_margin | 0.8070 | 2000 |
| T5 | h2 | own_margin | 0.9175 | 2000 |
| T5 | h2 | kappa | 0.9075 | 2000 |
| T5 | h2 | shuffled_vs_yardstick | 0.9220 | 2000 |
| T5 | h2 | carried_added | 0.8170 | 2000 |
| T5 | h2 | pooled_retention | 0.8170 | 2000 |
| T5 | h5 | large | 0.8680 | 2000 |
| T5 | h5 | carries | 0.8920 | 2000 |
| T5 | h5 | depends | 0.8875 | 2000 |
| T5 | h5 | carried_margin | 0.8755 | 2000 |
| T5 | h5 | kappa | 0.9175 | 2000 |
| T5 | h5 | shuffled_vs_yardstick | 0.9180 | 2000 |
| T5 | h5 | carried_added | 0.8890 | 2000 |
| T5 | h5 | pooled_retention | 0.8895 | 2000 |
| T5 | h10 | large | 0.8555 | 2000 |
| T5 | h10 | carries | 0.8580 | 2000 |
| T5 | h10 | depends | 0.8570 | 2000 |
| T5 | h10 | carried_margin | 0.8570 | 2000 |
| T5 | h10 | kappa | 0.8340 | 2000 |
| T5 | h10 | shuffled_vs_yardstick | 0.8565 | 2000 |
| T5 | h10 | carried_added | 0.8560 | 2000 |
| T5 | h10 | pooled_retention | 0.8575 | 2000 |
| T6[0.3] | n20 | carries | 0.8925 | 2000 |
| T6[0.3] | n20 | depends | 0.8960 | 2000 |
| T6[0.3] | n20 | carried_margin | 0.8890 | 2000 |
| T6[0.3] | n20 | own_margin | 0.9090 | 2000 |
| T6[0.3] | n20 | kappa | 0.8815 | 2000 |
| T6[0.3] | n20 | shuffled_vs_yardstick | 0.9090 | 2000 |
| T6[0.3] | n20 | carried_added | 0.9155 | 2000 |
| T6[0.3] | n20 | pooled_retention | 0.8795 | 2000 |
| T6[0.3] | n80 | shuffled_vs_yardstick | 0.8785 | 2000 |
| T6[0.3] | n80 | pooled_retention | 0.8785 | 2000 |
| T6[0.5] | n20 | carries | 0.9120 | 2000 |
| T6[0.5] | n20 | depends | 0.8975 | 2000 |
| T6[0.5] | n20 | carried_margin | 0.9045 | 2000 |
| T6[0.5] | n20 | carried_added | 0.9235 | 2000 |
| T6[0.5] | n20 | pooled_retention | 0.8855 | 2000 |
| T6[0.5] | n80 | shuffled_vs_yardstick | 0.8875 | 2000 |
| T6[0.5] | n80 | pooled_retention | 0.8870 | 2000 |
| T6[0.7] | n20 | carries | 0.9015 | 2000 |
| T6[0.7] | n20 | carried_added | 0.9025 | 2000 |
| T6[0.7] | n20 | pooled_retention | 0.8715 | 2000 |
| T6[0.7] | n80 | shuffled_vs_yardstick | 0.8695 | 2000 |
| T6[0.7] | n80 | pooled_retention | 0.8700 | 2000 |
| T6[0.85] | n20 | carries | 0.9085 | 2000 |
| T6[0.85] | n20 | carried_added | 0.9160 | 2000 |
| T6[0.85] | n20 | pooled_retention | 0.8760 | 2000 |
| T6[0.85] | n80 | depends | 0.8460 | 2000 |
| T6[0.85] | n80 | shuffled_vs_yardstick | 0.8750 | 2000 |
| T6[0.85] | n80 | pooled_retention | 0.8745 | 2000 |
| T6[0.95] | n20 | carries | 0.9030 | 2000 |
| T6[0.95] | n20 | depends | 0.7850 | 2000 |
| T6[0.95] | n20 | kappa | 0.9115 | 2000 |
| T6[0.95] | n20 | carried_added | 0.9075 | 2000 |
| T6[0.95] | n20 | pooled_retention | 0.8740 | 2000 |
| T6[0.95] | n80 | depends | 0.5750 | 2000 |
| T6[0.95] | n80 | shuffled_vs_yardstick | 0.8725 | 2000 |
| T6[0.95] | n80 | pooled_retention | 0.8705 | 2000 |
| T6[1] | n20 | carries | 0.8935 | 2000 |
| T6[1] | n20 | kappa | 0.9170 | 2000 |
| T6[1] | n20 | carried_added | 0.9085 | 2000 |
| T6[1] | n20 | pooled_retention | 0.8750 | 2000 |
| T6[1] | n80 | shuffled_vs_yardstick | 0.8720 | 2000 |
| T6[1] | n80 | pooled_retention | 0.8745 | 2000 |
| T6[1.1] | n20 | carries | 0.8985 | 2000 |
| T6[1.1] | n20 | depends | 0.8895 | 2000 |
| T6[1.1] | n20 | kappa | 0.9175 | 2000 |
| T6[1.1] | n20 | carried_added | 0.9170 | 2000 |
| T6[1.1] | n20 | pooled_retention | 0.8765 | 2000 |
| T6[1.1] | n80 | depends | 0.7305 | 2000 |
| T6[1.1] | n80 | shuffled_vs_yardstick | 0.8765 | 2000 |
| T6[1.1] | n80 | pooled_retention | 0.8770 | 2000 |
| T6[1.25] | n20 | carries | 0.9100 | 2000 |
| T6[1.25] | n20 | carried_added | 0.9060 | 2000 |
| T6[1.25] | n20 | pooled_retention | 0.8695 | 2000 |
| T6[1.25] | n80 | depends | 0.8685 | 2000 |
| T6[1.25] | n80 | shuffled_vs_yardstick | 0.8695 | 2000 |
| T6[1.25] | n80 | pooled_retention | 0.8705 | 2000 |
| T7 | h5 | large | 0.8890 | 2000 |
| T7 | h5 | carries | 0.8920 | 2000 |
| T7 | h5 | depends | 0.8930 | 2000 |
| T7 | h5 | carried_margin | 0.8910 | 2000 |
| T7 | h5 | kappa | 0.8870 | 2000 |
| T7 | h5 | shuffled_vs_yardstick | 0.9095 | 2000 |
| T7 | h5 | carried_added | 0.8910 | 2000 |
| T7 | h5 | pooled_retention | 0.8905 | 2000 |
| T8 | n20 | carries | 0.8450 | 2000 |
| T8 | n20 | depends | 0.8285 | 2000 |
| T8 | n20 | carried_margin | 0.8260 | 2000 |
| T8 | n20 | own_margin | 0.9115 | 2000 |
| T8 | n20 | kappa | 0.9025 | 2000 |
| T8 | n20 | shuffled_vs_yardstick | 0.9115 | 2000 |
| T8 | n20 | carried_added | 0.8735 | 2000 |
| T8 | n20 | pooled_retention | 0.7535 | 2000 |
| T8 | n40 | large | 0.9165 | 2000 |
| T8 | n40 | carried_margin | 0.9235 | 2000 |
| T8 | n40 | kappa | 0.9055 | 2000 |
| T8 | n40 | shuffled_vs_yardstick | 0.9125 | 2000 |
| T8 | n40 | carried_added | 0.9225 | 2000 |
| T8 | n40 | pooled_retention | 0.7590 | 2000 |
| T8 | n80 | kappa | 0.9065 | 2000 |
| T8 | n80 | shuffled_vs_yardstick | 0.9135 | 2000 |
| T8 | n80 | pooled_retention | 0.7590 | 2000 |
| T8 | n160 | carries | 0.8810 | 2000 |
| T8 | n160 | depends | 0.8815 | 2000 |
| T8 | n160 | kappa | 0.8575 | 2000 |
| T8 | n160 | shuffled_vs_yardstick | 0.9130 | 2000 |
| T8 | n160 | pooled_retention | 0.7550 | 2000 |
| T8 | n320 | large | 0.9195 | 2000 |
| T8 | n320 | carries | 0.8775 | 2000 |
| T8 | n320 | depends | 0.8785 | 2000 |
| T8 | n320 | carried_margin | 0.9180 | 2000 |
| T8 | n320 | kappa | 0.8615 | 2000 |
| T8 | n320 | shuffled_vs_yardstick | 0.9145 | 2000 |
| T8 | n320 | carried_added | 0.9130 | 2000 |
| T8 | n320 | pooled_retention | 0.7530 | 2000 |

## The Shuffled Ratio by Its Denominator's Distance From Zero (T6)

Pooled over the eight values of psi. Coverage leaves out psi = 1, where the ratio's truth divides by zero.

| Row | z_D | Experiments | Coverage | a | b | c | d | no reading defined |
|---|---|---|---|---|---|---|---|---|
| n20 | below 2 | 8148 | 0.9180 | 0.290 | 0.000 | 0.000 | 0.710 | 0.000 |
| n20 | 2 to 3 | 966 | 0.8533 | 0.000 | 0.000 | 0.006 | 0.990 | 0.004 |
| n20 | 3 to 5 | 1537 | 0.8862 | 0.069 | 0.000 | 0.046 | 0.865 | 0.020 |
| n20 | 5 to 8 | 2022 | 0.9028 | 0.490 | 0.000 | 0.018 | 0.483 | 0.009 |
| n20 | above 8 | 3327 | 0.9035 | 0.849 | 0.000 | 0.004 | 0.147 | 0.001 |
| n80 | below 2 | 10604 | 0.8116 | 0.081 | 0.000 | 0.000 | 0.919 | 0.000 |
| n80 | 2 to 3 | 1572 | 0.8300 | 0.027 | 0.000 | 0.035 | 0.933 | 0.005 |
| n80 | 3 to 5 | 2272 | 0.9235 | 0.298 | 0.000 | 0.021 | 0.677 | 0.004 |
| n80 | 5 to 8 | 1297 | 0.9306 | 0.598 | 0.000 | 0.007 | 0.394 | 0.001 |
| n80 | above 8 | 255 | 0.9176 | 0.776 | 0.000 | 0.004 | 0.220 | 0.000 |

## The Delta-On Shares When the Delta Components Do Nothing (T8)

Version a: the same searches with fresh cell noise. Version b: every search redrawn from its batch type's pilot starts.

| Row | Share | Version | 2.5th percentile | Median | 97.5th percentile | Interval covers 1 |
|---|---|---|---|---|---|---|
| n20 | carried_share | a | 0.963 | 1.000 | 1.040 | 0.9995 |
| n20 | carried_share | b | 0.875 | 1.002 | 1.137 | 0.9910 |
| n20 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n20 | own_share | b | 0.880 | 1.001 | 1.131 | 0.9765 |
| n40 | carried_share | a | 0.962 | 0.999 | 1.042 | 0.9995 |
| n40 | carried_share | b | 0.858 | 1.004 | 1.162 | 0.9765 |
| n40 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n40 | own_share | b | 0.865 | 1.002 | 1.163 | 0.9680 |
| n80 | carried_share | a | 0.962 | 0.999 | 1.044 | 1.0000 |
| n80 | carried_share | b | 0.795 | 0.996 | 1.231 | 0.9735 |
| n80 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n80 | own_share | b | 0.811 | 0.998 | 1.234 | 0.9695 |
| n160 | carried_share | a | 0.963 | 1.000 | 1.036 | 0.9995 |
| n160 | carried_share | b | 0.865 | 0.996 | 1.149 | 0.9785 |
| n160 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n160 | own_share | b | 0.874 | 0.999 | 1.139 | 0.9770 |
| n320 | carried_share | a | 0.964 | 0.999 | 1.036 | 1.0000 |
| n320 | carried_share | b | 0.881 | 0.997 | 1.128 | 0.9860 |
| n320 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n320 | own_share | b | 0.892 | 0.999 | 1.131 | 0.9675 |

## Batch-Clustered Missing Searches (T7), at 5 Nats

| Statistic | Truth | Convention, mean | Convention, bias | "Both reached", mean | "Both reached", bias |
|---|---|---|---|---|---|
| carries | 0.7000 | 0.7025 | 0.0025 | 0.7209 | 0.0209 |
| large | 2.9822 | 2.9931 | 0.0110 | 3.0839 | 0.1018 |

## Coverage by the Number of Type-C5 Batches (T3)

| Row | Reading | Side | Type-C5 batches | Experiments | Coverage |
|---|---|---|---|---|---|
| n20 | large | attack | 0 | 247 | 0.9555 |
| n20 | large | attack | 1 | 551 | 0.9492 |
| n20 | large | attack | 2 | 556 | 0.9263 |
| n20 | large | attack | 3 or more | 646 | 0.9195 |
| n20 | large | heldout | 0 | 207 | 0.8261 |
| n20 | large | heldout | 1 | 539 | 0.9035 |
| n20 | large | heldout | 2 | 604 | 0.9536 |
| n20 | large | heldout | 3 or more | 650 | 0.9754 |
| n20 | carries | attack | 0 | 247 | 0.9190 |
| n20 | carries | attack | 1 | 551 | 0.9619 |
| n20 | carries | attack | 2 | 556 | 0.9820 |
| n20 | carries | attack | 3 or more | 646 | 0.9752 |
| n20 | carries | heldout | 0 | 207 | 0.9372 |
| n20 | carries | heldout | 1 | 539 | 0.9740 |
| n20 | carries | heldout | 2 | 604 | 0.9652 |
| n20 | carries | heldout | 3 or more | 650 | 0.9708 |
| n20 | depends | attack | 0 | 247 | 0.9474 |
| n20 | depends | attack | 1 | 551 | 0.9800 |
| n20 | depends | attack | 2 | 556 | 0.9892 |
| n20 | depends | attack | 3 or more | 646 | 0.9737 |
| n20 | depends | heldout | 0 | 207 | 0.9614 |
| n20 | depends | heldout | 1 | 539 | 0.9833 |
| n20 | depends | heldout | 2 | 604 | 0.9834 |
| n20 | depends | heldout | 3 or more | 650 | 0.9692 |
| n40 | large | attack | 0 | 247 | 0.9069 |
| n40 | large | attack | 1 | 551 | 0.9401 |
| n40 | large | attack | 2 | 556 | 0.9317 |
| n40 | large | attack | 3 or more | 646 | 0.9272 |
| n40 | large | heldout | 0 | 207 | 0.7923 |
| n40 | large | heldout | 1 | 539 | 0.8924 |
| n40 | large | heldout | 2 | 604 | 0.9487 |
| n40 | large | heldout | 3 or more | 650 | 0.9862 |
| n40 | carries | attack | 0 | 247 | 0.9393 |
| n40 | carries | attack | 1 | 551 | 0.9583 |
| n40 | carries | attack | 2 | 556 | 0.9640 |
| n40 | carries | attack | 3 or more | 646 | 0.9598 |
| n40 | carries | heldout | 0 | 207 | 0.9420 |
| n40 | carries | heldout | 1 | 539 | 0.9425 |
| n40 | carries | heldout | 2 | 604 | 0.9536 |
| n40 | carries | heldout | 3 or more | 650 | 0.9800 |
| n40 | depends | attack | 0 | 247 | 0.9271 |
| n40 | depends | attack | 1 | 551 | 0.9637 |
| n40 | depends | attack | 2 | 556 | 0.9676 |
| n40 | depends | attack | 3 or more | 646 | 0.9505 |
| n40 | depends | heldout | 0 | 207 | 0.9420 |
| n40 | depends | heldout | 1 | 539 | 0.9443 |
| n40 | depends | heldout | 2 | 604 | 0.9520 |
| n40 | depends | heldout | 3 or more | 650 | 0.9738 |
| n80 | large | attack | 0 | 247 | 0.9595 |
| n80 | large | attack | 1 | 551 | 0.9619 |
| n80 | large | attack | 2 | 556 | 0.9568 |
| n80 | large | attack | 3 or more | 646 | 0.9257 |
| n80 | large | heldout | 0 | 207 | 0.8309 |
| n80 | large | heldout | 1 | 539 | 0.9258 |
| n80 | large | heldout | 2 | 604 | 0.9735 |
| n80 | large | heldout | 3 or more | 650 | 0.9815 |
| n80 | carries | attack | 0 | 247 | 0.9595 |
| n80 | carries | attack | 1 | 551 | 0.9601 |
| n80 | carries | attack | 2 | 556 | 0.9676 |
| n80 | carries | attack | 3 or more | 646 | 0.9350 |
| n80 | carries | heldout | 0 | 207 | 0.7101 |
| n80 | carries | heldout | 1 | 539 | 0.9610 |
| n80 | carries | heldout | 2 | 604 | 0.9884 |
| n80 | carries | heldout | 3 or more | 650 | 0.9938 |
| n80 | depends | attack | 0 | 247 | 0.9595 |
| n80 | depends | attack | 1 | 551 | 0.9601 |
| n80 | depends | attack | 2 | 556 | 0.9694 |
| n80 | depends | attack | 3 or more | 646 | 0.9350 |
| n80 | depends | heldout | 0 | 207 | 0.7150 |
| n80 | depends | heldout | 1 | 539 | 0.9592 |
| n80 | depends | heldout | 2 | 604 | 0.9901 |
| n80 | depends | heldout | 3 or more | 650 | 0.9938 |
| n160 | large | attack | 0 | 247 | 0.9433 |
| n160 | large | attack | 1 | 551 | 0.9728 |
| n160 | large | attack | 2 | 556 | 0.9640 |
| n160 | large | attack | 3 or more | 646 | 0.9071 |
| n160 | large | heldout | 0 | 207 | 0.6232 |
| n160 | large | heldout | 1 | 539 | 0.9722 |
| n160 | large | heldout | 2 | 604 | 0.9983 |
| n160 | large | heldout | 3 or more | 650 | 0.9769 |
| n160 | carries | attack | 0 | 247 | 0.9636 |
| n160 | carries | attack | 1 | 551 | 0.9583 |
| n160 | carries | attack | 2 | 556 | 0.9442 |
| n160 | carries | attack | 3 or more | 646 | 0.8885 |
| n160 | carries | heldout | 0 | 207 | 0.4541 |
| n160 | carries | heldout | 1 | 539 | 0.9629 |
| n160 | carries | heldout | 2 | 604 | 1.0000 |
| n160 | carries | heldout | 3 or more | 650 | 0.9969 |
| n160 | depends | attack | 0 | 247 | 0.9636 |
| n160 | depends | attack | 1 | 551 | 0.9601 |
| n160 | depends | attack | 2 | 556 | 0.9460 |
| n160 | depends | attack | 3 or more | 646 | 0.8870 |
| n160 | depends | heldout | 0 | 207 | 0.4589 |
| n160 | depends | heldout | 1 | 539 | 0.9629 |
| n160 | depends | heldout | 2 | 604 | 0.9983 |
| n160 | depends | heldout | 3 or more | 650 | 0.9985 |
| n320 | large | attack | 0 | 247 | 0.9474 |
| n320 | large | attack | 1 | 551 | 0.9728 |
| n320 | large | attack | 2 | 556 | 0.9622 |
| n320 | large | attack | 3 or more | 646 | 0.9040 |
| n320 | large | heldout | 0 | 207 | 0.6087 |
| n320 | large | heldout | 1 | 539 | 0.9685 |
| n320 | large | heldout | 2 | 604 | 0.9983 |
| n320 | large | heldout | 3 or more | 650 | 0.9815 |
| n320 | carries | attack | 0 | 247 | 0.9555 |
| n320 | carries | attack | 1 | 551 | 0.9474 |
| n320 | carries | attack | 2 | 556 | 0.9442 |
| n320 | carries | attack | 3 or more | 646 | 0.8808 |
| n320 | carries | heldout | 0 | 207 | 0.4155 |
| n320 | carries | heldout | 1 | 539 | 0.9555 |
| n320 | carries | heldout | 2 | 604 | 0.9983 |
| n320 | carries | heldout | 3 or more | 650 | 0.9969 |
| n320 | depends | attack | 0 | 247 | 0.9555 |
| n320 | depends | attack | 1 | 551 | 0.9474 |
| n320 | depends | attack | 2 | 556 | 0.9442 |
| n320 | depends | attack | 3 or more | 646 | 0.8808 |
| n320 | depends | heldout | 0 | 207 | 0.4155 |
| n320 | depends | heldout | 1 | 539 | 0.9555 |
| n320 | depends | heldout | 2 | 604 | 0.9983 |
| n320 | depends | heldout | 3 or more | 650 | 0.9969 |
| h2 | large | attack | 0 | 247 | 0.9393 |
| h2 | large | attack | 1 | 551 | 0.9800 |
| h2 | large | attack | 2 | 556 | 0.9694 |
| h2 | large | attack | 3 or more | 646 | 0.8978 |
| h2 | large | heldout | 0 | 207 | 0.6908 |
| h2 | large | heldout | 1 | 539 | 0.9555 |
| h2 | large | heldout | 2 | 604 | 0.9868 |
| h2 | large | heldout | 3 or more | 650 | 0.9800 |
| h2 | carries | attack | 0 | 247 | 0.9109 |
| h2 | carries | attack | 1 | 551 | 0.9165 |
| h2 | carries | attack | 2 | 556 | 0.9245 |
| h2 | carries | attack | 3 or more | 646 | 0.8793 |
| h2 | carries | heldout | 0 | 207 | 0.2126 |
| h2 | carries | heldout | 1 | 539 | 0.9722 |
| h2 | carries | heldout | 2 | 604 | 1.0000 |
| h2 | carries | heldout | 3 or more | 650 | 0.9846 |
| h2 | depends | attack | 0 | 247 | 0.9231 |
| h2 | depends | attack | 1 | 551 | 0.9292 |
| h2 | depends | attack | 2 | 556 | 0.9335 |
| h2 | depends | attack | 3 or more | 646 | 0.8777 |
| h2 | depends | heldout | 0 | 207 | 0.2657 |
| h2 | depends | heldout | 1 | 539 | 0.9703 |
| h2 | depends | heldout | 2 | 604 | 1.0000 |
| h2 | depends | heldout | 3 or more | 650 | 0.9908 |
| h5 | large | attack | 0 | 244 | 0.9098 |
| h5 | large | attack | 1 | 548 | 0.9507 |
| h5 | large | attack | 2 | 557 | 0.9533 |
| h5 | large | attack | 3 or more | 651 | 0.8833 |
| h5 | large | heldout | 0 | 205 | 0.4098 |
| h5 | large | heldout | 1 | 540 | 0.9722 |
| h5 | large | heldout | 2 | 603 | 0.9983 |
| h5 | large | heldout | 3 or more | 652 | 0.9785 |
| h5 | carries | attack | 0 | 244 | 0.9221 |
| h5 | carries | attack | 1 | 548 | 0.9161 |
| h5 | carries | attack | 2 | 557 | 0.9282 |
| h5 | carries | attack | 3 or more | 651 | 0.8833 |
| h5 | carries | heldout | 0 | 205 | 0.2146 |
| h5 | carries | heldout | 1 | 540 | 0.9796 |
| h5 | carries | heldout | 2 | 603 | 1.0000 |
| h5 | carries | heldout | 3 or more | 652 | 0.9862 |
| h5 | depends | attack | 0 | 244 | 0.9221 |
| h5 | depends | attack | 1 | 548 | 0.9215 |
| h5 | depends | attack | 2 | 557 | 0.9282 |
| h5 | depends | attack | 3 or more | 651 | 0.8802 |
| h5 | depends | heldout | 0 | 205 | 0.2195 |
| h5 | depends | heldout | 1 | 540 | 0.9759 |
| h5 | depends | heldout | 2 | 603 | 1.0000 |
| h5 | depends | heldout | 3 or more | 652 | 0.9893 |
| h10 | large | attack | 0 | 515 | 0.8058 |
| h10 | large | attack | 1 | 906 | 0.7826 |
| h10 | large | attack | 2 | 467 | 0.7794 |
| h10 | large | attack | 3 or more | 112 | 0.8125 |
| h10 | large | heldout | 0 | 488 | 0.1475 |
| h10 | large | heldout | 1 | 867 | 0.9942 |
| h10 | large | heldout | 2 | 509 | 1.0000 |
| h10 | large | heldout | 3 or more | 136 | 1.0000 |
| h10 | carries | attack | 0 | 515 | 0.7981 |
| h10 | carries | attack | 1 | 906 | 0.7792 |
| h10 | carries | attack | 2 | 467 | 0.7666 |
| h10 | carries | attack | 3 or more | 112 | 0.8125 |
| h10 | carries | heldout | 0 | 488 | 0.1168 |
| h10 | carries | heldout | 1 | 867 | 0.9965 |
| h10 | carries | heldout | 2 | 509 | 1.0000 |
| h10 | carries | heldout | 3 or more | 136 | 1.0000 |
| h10 | depends | attack | 0 | 515 | 0.7981 |
| h10 | depends | attack | 1 | 906 | 0.7815 |
| h10 | depends | attack | 2 | 467 | 0.7666 |
| h10 | depends | attack | 3 or more | 112 | 0.8125 |
| h10 | depends | heldout | 0 | 488 | 0.1209 |
| h10 | depends | heldout | 1 | 867 | 0.9965 |
| h10 | depends | heldout | 2 | 509 | 1.0000 |
| h10 | depends | heldout | 3 or more | 136 | 1.0000 |

## Every Scenario, Row, and Statistic

Coverage is of the unwidened interval; "above" and "below" are the shares of intervals lying wholly above and wholly below the truth; "variance ratio" is the mean of V_PB + V_c over the Monte Carlo variance of the estimate; the half-width is its median.

| Scenario | Row | Statistic | Truth | Mean | Bias | MC sd | Coverage | Above | Below | Variance ratio | Half-width | V_c = 0 | Start share > 0.5 | Mean nu | Multiplier needed | Percentile coverage | Denominator's distance | Share read | Coverage, all experiments |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | large | -0.4748 | -0.4737 | 0.0011 | 0.0515 | 0.8620 | 0.1370 | 0.0010 | 1.054 | 0.1085 | 0.566 | 0.012 | 14.0 | 2.002 | 0.8365 | n/a | n/a | n/a |
| P1 | n20 | carries | 0.2000 | 0.2004 | 0.0004 | 0.0222 | 0.8970 | 0.0015 | 0.1015 | 1.070 | 0.0476 | 0.576 | 0.025 | 13.8 | 1.738 | 0.8555 | 10.0 | n/a | n/a |
| P1 | n20 | depends | -0.1600 | -0.1577 | 0.0023 | 0.0728 | 0.8960 | 0.0980 | 0.0060 | 0.973 | 0.1482 | 0.592 | 0.000 | 15.3 | 1.448 | 0.8720 | 14.8 | n/a | n/a |
| P1 | n20 | carried_margin | -0.0655 | -0.0651 | 0.0004 | 0.0316 | 0.8830 | 0.1140 | 0.0030 | 0.979 | 0.0655 | 0.577 | 0.000 | 15.2 | 1.605 | 0.8655 | n/a | n/a | n/a |
| P1 | n20 | own_margin | 0.4093 | 0.4086 | -0.0007 | 0.0282 | 0.9030 | 0.0015 | 0.0955 | 1.257 | 0.0626 | 0.566 | 0.131 | 12.0 | 1.410 | 0.8330 | n/a | n/a | n/a |
| P1 | n20 | kappa | -0.5518 | -0.5470 | 0.0048 | 0.2467 | 0.9060 | 0.0725 | 0.0215 | 0.893 | 0.5034 | 0.577 | 0.000 | 15.3 | 1.273 | 0.8870 | 7.2 | n/a | n/a |
| P1 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0282 | 0.9030 | 0.0955 | 0.0015 | 1.257 | 0.0626 | 0.566 | 0.131 | 12.0 | 1.410 | 0.8330 | n/a | n/a | n/a |
| P1 | n20 | carried_added | 0.1187 | 0.1185 | -0.0002 | 0.0169 | 0.9170 | 0.0020 | 0.0810 | 1.043 | 0.0343 | 0.581 | 0.000 | 15.2 | 1.245 | 0.9005 | n/a | n/a | n/a |
| P1 | n20 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0201 | 0.8735 | 0.0030 | 0.1235 | 1.004 | 0.0421 | 0.522 | 0.000 | 15.1 | 2.493 | 0.8650 | 9.9 | n/a | n/a |
| P1 | n40 | large | -0.2038 | -0.2027 | 0.0011 | 0.0506 | 0.9755 | 0.0145 | 0.0100 | 1.139 | 0.1104 | 0.571 | 0.029 | 13.6 | 0.881 | 0.9250 | n/a | n/a | n/a |
| P1 | n40 | carries | 0.2000 | 0.2009 | 0.0009 | 0.0270 | 0.9610 | 0.0055 | 0.0335 | 1.101 | 0.0593 | 0.556 | 0.005 | 14.3 | 0.961 | 0.9255 | 9.4 | n/a | n/a |
| P1 | n40 | depends | 0.1165 | 0.1181 | 0.0016 | 0.0267 | 0.9540 | 0.0055 | 0.0405 | 1.088 | 0.0586 | 0.556 | 0.003 | 14.5 | 0.962 | 0.9245 | 9.6 | n/a | n/a |
| P1 | n40 | carried_margin | 0.2055 | 0.2059 | 0.0003 | 0.0410 | 0.9505 | 0.0055 | 0.0440 | 1.108 | 0.0898 | 0.547 | 0.003 | 14.6 | 0.998 | 0.9230 | n/a | n/a | n/a |
| P1 | n40 | own_margin | 1.7645 | 1.7641 | -0.0004 | 0.1846 | 0.9395 | 0.0105 | 0.0500 | 1.045 | 0.3988 | 0.575 | 0.005 | 14.3 | 1.086 | 0.9040 | n/a | n/a | n/a |
| P1 | n40 | kappa | 0.5274 | 0.5289 | 0.0015 | 0.0762 | 0.9190 | 0.0690 | 0.0120 | 0.962 | 0.1595 | 0.547 | 0.000 | 15.2 | 1.170 | 0.9020 | 6.9 | n/a | n/a |
| P1 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0282 | 0.9035 | 0.0950 | 0.0015 | 1.256 | 0.0627 | 0.568 | 0.132 | 12.0 | 1.389 | 0.8340 | n/a | n/a | n/a |
| P1 | n40 | carried_added | 0.3897 | 0.3895 | -0.0002 | 0.0565 | 0.9390 | 0.0015 | 0.0595 | 1.054 | 0.1198 | 0.548 | 0.000 | 15.2 | 1.082 | 0.9135 | n/a | n/a | n/a |
| P1 | n40 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0201 | 0.8755 | 0.0025 | 0.1220 | 1.008 | 0.0420 | 0.523 | 0.000 | 15.1 | 2.411 | 0.8660 | 9.3 | n/a | n/a |
| P1 | n80 | large | 1.3592 | 1.3557 | -0.0036 | 0.2014 | 0.9590 | 0.0000 | 0.0410 | 1.221 | 0.4661 | 0.587 | 0.051 | 13.0 | 0.931 | 0.9150 | n/a | n/a | n/a |
| P1 | n80 | carries | 0.2000 | 0.2004 | 0.0004 | 0.0313 | 0.9375 | 0.0035 | 0.0590 | 1.161 | 0.0699 | 0.603 | 0.030 | 13.4 | 1.150 | 0.9150 | 12.4 | n/a | n/a |
| P1 | n80 | depends | 0.1846 | 0.1851 | 0.0005 | 0.0287 | 0.9480 | 0.0035 | 0.0485 | 1.188 | 0.0647 | 0.600 | 0.045 | 13.2 | 1.011 | 0.9185 | 12.0 | n/a | n/a |
| P1 | n80 | carried_margin | 1.7685 | 1.7643 | -0.0043 | 0.2107 | 0.9525 | 0.0000 | 0.0475 | 1.190 | 0.4832 | 0.574 | 0.044 | 13.2 | 0.963 | 0.9115 | n/a | n/a | n/a |
| P1 | n80 | own_margin | 9.5794 | 9.6039 | 0.0245 | 0.7305 | 0.9665 | 0.0145 | 0.0190 | 1.336 | 1.7237 | 0.597 | 0.119 | 12.2 | 0.897 | 0.9230 | n/a | n/a | n/a |
| P1 | n80 | kappa | 0.9057 | 0.9063 | 0.0007 | 0.0133 | 0.9240 | 0.0690 | 0.0070 | 1.037 | 0.0289 | 0.575 | 0.012 | 14.1 | 1.199 | 0.8945 | 7.7 | n/a | n/a |
| P1 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0283 | 0.9015 | 0.0965 | 0.0020 | 1.253 | 0.0627 | 0.569 | 0.130 | 12.0 | 1.383 | 0.8325 | n/a | n/a | n/a |
| P1 | n80 | carried_added | 1.9527 | 1.9479 | -0.0048 | 0.2419 | 0.9405 | 0.0000 | 0.0595 | 1.143 | 0.5472 | 0.575 | 0.029 | 13.7 | 1.063 | 0.8985 | n/a | n/a | n/a |
| P1 | n80 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0202 | 0.8745 | 0.0030 | 0.1225 | 0.994 | 0.0420 | 0.474 | 0.000 | 15.1 | 2.421 | 0.8630 | 12.4 | n/a | n/a |
| P1 | n160 | large | 3.8260 | 3.8254 | -0.0006 | 0.4618 | 0.9305 | 0.0025 | 0.0670 | 1.090 | 1.0122 | 0.592 | 0.007 | 14.6 | 1.127 | 0.8945 | n/a | n/a | n/a |
| P1 | n160 | carries | 0.2000 | 0.2013 | 0.0013 | 0.0320 | 0.9060 | 0.0000 | 0.0940 | 1.108 | 0.0672 | 0.588 | 0.005 | 14.7 | 1.575 | 0.8815 | 16.3 | n/a | n/a |
| P1 | n160 | depends | 0.1933 | 0.1945 | 0.0013 | 0.0306 | 0.9100 | 0.0000 | 0.0900 | 1.117 | 0.0642 | 0.589 | 0.005 | 14.6 | 1.345 | 0.8865 | 15.9 | n/a | n/a |
| P1 | n160 | carried_margin | 4.2353 | 4.2340 | -0.0013 | 0.4736 | 0.9285 | 0.0025 | 0.0690 | 1.082 | 1.0343 | 0.592 | 0.006 | 14.6 | 1.158 | 0.8940 | n/a | n/a | n/a |
| P1 | n160 | own_margin | 21.9134 | 21.9300 | 0.0166 | 1.2961 | 0.9570 | 0.0345 | 0.0085 | 1.204 | 2.9755 | 0.593 | 0.074 | 12.7 | 0.962 | 0.9090 | n/a | n/a | n/a |
| P1 | n160 | kappa | 0.9583 | 0.9588 | 0.0005 | 0.0055 | 0.9010 | 0.0915 | 0.0075 | 0.978 | 0.0117 | 0.593 | 0.000 | 15.0 | 1.539 | 0.8830 | 8.5 | n/a | n/a |
| P1 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0282 | 0.9005 | 0.0980 | 0.0015 | 1.257 | 0.0626 | 0.567 | 0.131 | 12.0 | 1.384 | 0.8315 | n/a | n/a | n/a |
| P1 | n160 | carried_added | 4.4195 | 4.4177 | -0.0018 | 0.5084 | 0.9215 | 0.0020 | 0.0765 | 1.070 | 1.1050 | 0.591 | 0.005 | 14.8 | 1.223 | 0.8875 | n/a | n/a | n/a |
| P1 | n160 | pooled_retention | 0.2000 | 0.1998 | -0.0002 | 0.0200 | 0.8770 | 0.0030 | 0.1200 | 1.001 | 0.0420 | 0.506 | 0.000 | 15.1 | 2.482 | 0.8645 | 16.3 | n/a | n/a |
| P1 | n320 | large | 4.4962 | 4.4888 | -0.0075 | 0.5340 | 0.9215 | 0.0030 | 0.0755 | 1.063 | 1.1534 | 0.576 | 0.005 | 14.7 | 1.227 | 0.8925 | n/a | n/a | n/a |
| P1 | n320 | carries | 0.2000 | 0.2008 | 0.0008 | 0.0318 | 0.9000 | 0.0000 | 0.1000 | 1.083 | 0.0661 | 0.588 | 0.005 | 14.8 | 1.716 | 0.8785 | 17.5 | n/a | n/a |
| P1 | n320 | depends | 0.1942 | 0.1950 | 0.0008 | 0.0306 | 0.9010 | 0.0000 | 0.0990 | 1.090 | 0.0636 | 0.590 | 0.006 | 14.7 | 1.396 | 0.8800 | 17.0 | n/a | n/a |
| P1 | n320 | carried_margin | 4.9055 | 4.8974 | -0.0082 | 0.5462 | 0.9185 | 0.0025 | 0.0790 | 1.057 | 1.1798 | 0.587 | 0.006 | 14.8 | 1.255 | 0.8860 | n/a | n/a | n/a |
| P1 | n320 | own_margin | 25.2643 | 25.2985 | 0.0341 | 1.4090 | 0.9545 | 0.0380 | 0.0075 | 1.186 | 3.2445 | 0.590 | 0.077 | 12.7 | 0.973 | 0.9070 | n/a | n/a | n/a |
| P1 | n320 | kappa | 0.9638 | 0.9642 | 0.0004 | 0.0047 | 0.8965 | 0.0945 | 0.0090 | 0.982 | 0.0101 | 0.585 | 0.002 | 15.1 | 1.545 | 0.8780 | 8.6 | n/a | n/a |
| P1 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0282 | 0.9000 | 0.0985 | 0.0015 | 1.256 | 0.0625 | 0.565 | 0.132 | 12.0 | 1.366 | 0.8315 | n/a | n/a | n/a |
| P1 | n320 | carried_added | 5.0897 | 5.0810 | -0.0087 | 0.5818 | 0.9135 | 0.0025 | 0.0840 | 1.048 | 1.2489 | 0.587 | 0.005 | 14.9 | 1.318 | 0.8815 | n/a | n/a | n/a |
| P1 | n320 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0201 | 0.8750 | 0.0030 | 0.1220 | 0.997 | 0.0421 | 0.525 | 0.000 | 15.1 | 2.454 | 0.8645 | 17.2 | n/a | n/a |
| P1 | h2 | large | -0.2116 | -0.2108 | 0.0008 | 0.0298 | 0.8895 | 0.1095 | 0.0010 | 1.242 | 0.0663 | 0.563 | 0.117 | 12.1 | 1.417 | 0.8210 | n/a | 1.000 | 0.8895 |
| P1 | h2 | carries | 0.2000 | 0.1997 | -0.0003 | 0.0189 | 0.8770 | 0.0030 | 0.1200 | 0.994 | 0.0398 | 0.590 | 0.000 | 15.1 | 2.514 | 0.8665 | 121.3 | 1.000 | 0.8770 |
| P1 | h2 | depends | 0.1146 | 0.1146 | 0.0000 | 0.0025 | 0.9920 | 0.0015 | 0.0065 | 1.803 | 0.0068 | 0.577 | 0.006 | 14.3 | 0.716 | 0.9765 | 55.8 | 1.000 | 0.9920 |
| P1 | h2 | carried_margin | 0.1978 | 0.1978 | 0.0001 | 0.0048 | 0.9910 | 0.0065 | 0.0025 | 1.605 | 0.0126 | 0.565 | 0.004 | 14.6 | 0.743 | 0.9760 | n/a | 1.000 | 0.9910 |
| P1 | h2 | own_margin | 1.7255 | 1.7260 | 0.0004 | 0.0315 | 0.8975 | 0.0995 | 0.0030 | 1.019 | 0.0659 | 0.584 | 0.002 | 15.2 | 1.389 | 0.8675 | n/a | 1.000 | 0.8975 |
| P1 | h2 | kappa | 0.5177 | 0.5242 | 0.0065 | 0.0579 | 0.8670 | 0.1180 | 0.0150 | 0.899 | 0.1204 | 0.569 | 0.000 | 15.1 | 2.141 | 0.8635 | 10.1 | 1.000 | 0.8670 |
| P1 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0282 | 0.9020 | 0.0965 | 0.0015 | 1.257 | 0.0627 | 0.565 | 0.128 | 12.0 | 1.390 | 0.8330 | n/a | 1.000 | 0.9020 |
| P1 | h2 | carried_added | 0.3819 | 0.3815 | -0.0005 | 0.0384 | 0.8755 | 0.0030 | 0.1215 | 0.997 | 0.0803 | 0.557 | 0.000 | 15.1 | 2.403 | 0.8650 | n/a | 1.000 | 0.8755 |
| P1 | h2 | pooled_retention | 0.2000 | 0.1998 | -0.0002 | 0.0200 | 0.8750 | 0.0030 | 0.1220 | 0.998 | 0.0420 | 0.574 | 0.000 | 15.0 | 2.487 | 0.8640 | 121.4 | 1.000 | 0.8750 |
| P1 | h5 | large | 0.4283 | 0.4279 | -0.0004 | 0.0539 | 0.9075 | 0.0010 | 0.0915 | 1.140 | 0.1155 | 0.544 | 0.028 | 13.6 | 1.401 | 0.8580 | n/a | 0.995 | 0.9070 |
| P1 | h5 | carries | 0.2000 | 0.1998 | -0.0002 | 0.0208 | 0.8755 | 0.0030 | 0.1215 | 0.991 | 0.0431 | 0.589 | 0.000 | 15.1 | 2.706 | 0.8655 | 157.3 | 0.995 | 0.8745 |
| P1 | h5 | depends | 0.1701 | 0.1700 | -0.0001 | 0.0147 | 0.8770 | 0.0010 | 0.1220 | 1.008 | 0.0304 | 0.595 | 0.000 | 15.2 | 2.364 | 0.8675 | 79.8 | 0.995 | 0.8760 |
| P1 | h5 | carried_margin | 0.8376 | 0.8365 | -0.0011 | 0.0627 | 0.8750 | 0.0030 | 0.1220 | 1.006 | 0.1310 | 0.601 | 0.000 | 15.2 | 2.145 | 0.8650 | n/a | 0.995 | 0.8740 |
| P1 | h5 | own_margin | 4.9248 | 4.9251 | 0.0003 | 0.0617 | 0.9185 | 0.0775 | 0.0040 | 1.064 | 0.1354 | 0.576 | 0.045 | 13.6 | 1.280 | 0.8630 | n/a | 0.995 | 0.9185 |
| P1 | h5 | kappa | 0.8197 | 0.8220 | 0.0023 | 0.0215 | 0.8665 | 0.1165 | 0.0170 | 0.912 | 0.0452 | 0.588 | 0.000 | 15.1 | 2.129 | 0.8645 | 10.1 | 0.995 | 0.8660 |
| P1 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0283 | 0.9015 | 0.0965 | 0.0020 | 1.394 | 0.0636 | 0.564 | 0.168 | 11.6 | 1.390 | 0.8320 | n/a | 0.995 | 0.9020 |
| P1 | h5 | carried_added | 1.0218 | 1.0202 | -0.0016 | 0.1030 | 0.8745 | 0.0035 | 0.1220 | 0.992 | 0.2140 | 0.603 | 0.000 | 15.1 | 2.375 | 0.8665 | n/a | 0.995 | 0.8735 |
| P1 | h5 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0201 | 0.8750 | 0.0040 | 0.1210 | 0.993 | 0.0417 | 0.588 | 0.000 | 15.1 | 2.469 | 0.8650 | 158.5 | 0.995 | 0.8740 |
| P1 | h10 | large | 1.5787 | 1.4723 | -0.1064 | 0.1122 | 0.7470 | 0.0000 | 0.2530 | 1.486 | 0.2777 | 0.592 | 0.000 | 15.1 | 2.235 | 0.7345 | n/a | 0.194 | 0.8755 |
| P1 | h10 | carries | 0.2000 | 0.1863 | -0.0137 | 0.0132 | 0.7425 | 0.0000 | 0.2575 | 1.545 | 0.0344 | 0.588 | 0.000 | 15.1 | 2.725 | 0.7385 | 144.8 | 0.194 | 0.8765 |
| P1 | h10 | depends | 0.1862 | 0.1744 | -0.0118 | 0.0114 | 0.7470 | 0.0000 | 0.2530 | 1.559 | 0.0297 | 0.585 | 0.000 | 15.1 | 2.532 | 0.7390 | 127.7 | 0.194 | 0.8775 |
| P1 | h10 | carried_margin | 1.9880 | 1.8665 | -0.1215 | 0.1156 | 0.7425 | 0.0000 | 0.2575 | 1.566 | 0.3031 | 0.569 | 0.000 | 15.1 | 2.570 | 0.7380 | n/a | 0.194 | 0.8765 |
| P1 | h10 | own_margin | 10.6772 | 10.7054 | 0.0282 | 0.0743 | 0.9595 | 0.0345 | 0.0060 | 1.689 | 0.1814 | 0.579 | 0.226 | 11.1 | 0.950 | 0.9010 | n/a | 0.194 | 0.9670 |
| P1 | h10 | kappa | 0.9152 | 0.9232 | 0.0080 | 0.0076 | 0.7460 | 0.2540 | 0.0000 | 1.363 | 0.0197 | 0.564 | 0.000 | 15.1 | 2.428 | 0.7380 | 11.7 | 0.194 | 0.8660 |
| P1 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3942 | 0.0151 | 0.0196 | 0.8020 | 0.1980 | 0.0000 | 1.408 | 0.0421 | 0.558 | 0.037 | 13.8 | 1.653 | 0.7145 | n/a | 0.194 | 0.8895 |
| P1 | h10 | carried_added | 2.1722 | 2.0229 | -0.1494 | 0.1416 | 0.7410 | 0.0000 | 0.2590 | 1.555 | 0.3696 | 0.572 | 0.000 | 15.1 | 2.664 | 0.7375 | n/a | 0.194 | 0.8750 |
| P1 | h10 | pooled_retention | 0.2000 | 0.1862 | -0.0138 | 0.0130 | 0.7405 | 0.0000 | 0.2595 | 1.551 | 0.0339 | 0.562 | 0.000 | 15.1 | 2.724 | 0.7370 | 145.0 | 0.194 | 0.8735 |
| P2 | n20 | large | -0.2374 | -0.2384 | -0.0010 | 0.0481 | 0.9785 | 0.0070 | 0.0145 | 1.139 | 0.1055 | 0.574 | 0.025 | 13.4 | 0.868 | 0.9005 | n/a | n/a | n/a |
| P2 | n20 | carries | 0.6000 | 0.5996 | -0.0004 | 0.0657 | 0.9015 | 0.0010 | 0.0975 | 1.104 | 0.1443 | 0.589 | 0.020 | 13.6 | 1.576 | 0.8620 | 9.8 | n/a | n/a |
| P2 | n20 | depends | 0.4200 | 0.4208 | 0.0008 | 0.0964 | 0.8980 | 0.0020 | 0.1000 | 1.067 | 0.2037 | 0.583 | 0.004 | 14.3 | 1.354 | 0.8580 | 14.5 | n/a | n/a |
| P2 | n20 | carried_margin | 0.1719 | 0.1716 | -0.0003 | 0.0371 | 0.8635 | 0.0010 | 0.1355 | 1.054 | 0.0775 | 0.570 | 0.001 | 14.8 | 1.739 | 0.8380 | n/a | n/a | n/a |
| P2 | n20 | own_margin | 0.4093 | 0.4100 | 0.0007 | 0.0284 | 0.9025 | 0.0010 | 0.0965 | 1.283 | 0.0650 | 0.549 | 0.136 | 12.0 | 1.322 | 0.8315 | n/a | n/a | n/a |
| P2 | n20 | kappa | 0.4827 | 0.4826 | -0.0002 | 0.0812 | 0.9120 | 0.0635 | 0.0245 | 0.920 | 0.1686 | 0.576 | 0.000 | 15.3 | 1.225 | 0.8880 | 7.2 | n/a | n/a |
| P2 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9025 | 0.0965 | 0.0010 | 1.283 | 0.0650 | 0.549 | 0.136 | 12.0 | 1.322 | 0.8315 | n/a | n/a | n/a |
| P2 | n20 | carried_added | 0.3561 | 0.3562 | 0.0001 | 0.0510 | 0.9085 | 0.0020 | 0.0895 | 1.035 | 0.1049 | 0.570 | 0.000 | 15.2 | 1.339 | 0.8965 | n/a | n/a | n/a |
| P2 | n20 | pooled_retention | 0.6000 | 0.6008 | 0.0008 | 0.0605 | 0.8795 | 0.0025 | 0.1180 | 1.015 | 0.1271 | 0.524 | 0.000 | 15.1 | 2.325 | 0.8675 | 9.9 | n/a | n/a |
| P2 | n40 | large | 0.5757 | 0.5755 | -0.0002 | 0.1403 | 0.9375 | 0.0050 | 0.0575 | 1.096 | 0.3019 | 0.582 | 0.002 | 14.6 | 1.082 | 0.9105 | n/a | n/a | n/a |
| P2 | n40 | carries | 0.6000 | 0.6021 | 0.0021 | 0.0822 | 0.9535 | 0.0100 | 0.0365 | 1.068 | 0.1795 | 0.588 | 0.003 | 14.4 | 0.982 | 0.9255 | 9.4 | n/a | n/a |
| P2 | n40 | depends | 0.5582 | 0.5614 | 0.0031 | 0.0875 | 0.9520 | 0.0080 | 0.0400 | 1.077 | 0.1913 | 0.590 | 0.004 | 14.4 | 0.988 | 0.9245 | 9.6 | n/a | n/a |
| P2 | n40 | carried_margin | 0.9850 | 0.9855 | 0.0005 | 0.1451 | 0.9370 | 0.0030 | 0.0600 | 1.079 | 0.3119 | 0.580 | 0.000 | 14.9 | 1.059 | 0.9140 | n/a | n/a | n/a |
| P2 | n40 | own_margin | 1.7645 | 1.7674 | 0.0030 | 0.1818 | 0.9455 | 0.0075 | 0.0470 | 1.073 | 0.3980 | 0.582 | 0.004 | 14.4 | 1.046 | 0.9200 | n/a | n/a | n/a |
| P2 | n40 | kappa | 0.8425 | 0.8424 | -0.0001 | 0.0252 | 0.9190 | 0.0705 | 0.0105 | 0.988 | 0.0537 | 0.584 | 0.000 | 15.2 | 1.183 | 0.9060 | 6.9 | n/a | n/a |
| P2 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4101 | -0.0008 | 0.0284 | 0.9025 | 0.0965 | 0.0010 | 1.281 | 0.0651 | 0.543 | 0.135 | 12.0 | 1.344 | 0.8315 | n/a | n/a | n/a |
| P2 | n40 | carried_added | 1.1692 | 1.1701 | 0.0009 | 0.1699 | 0.9350 | 0.0015 | 0.0635 | 1.059 | 0.3634 | 0.581 | 0.000 | 15.1 | 1.105 | 0.9135 | n/a | n/a | n/a |
| P2 | n40 | pooled_retention | 0.6000 | 0.6006 | 0.0006 | 0.0603 | 0.8780 | 0.0030 | 0.1190 | 1.021 | 0.1276 | 0.515 | 0.000 | 15.1 | 2.331 | 0.8700 | 9.3 | n/a | n/a |
| P2 | n80 | large | 5.2647 | 5.2738 | 0.0092 | 0.6876 | 0.9530 | 0.0030 | 0.0440 | 1.156 | 1.5529 | 0.581 | 0.027 | 13.6 | 0.994 | 0.9070 | n/a | n/a | n/a |
| P2 | n80 | carries | 0.6000 | 0.6047 | 0.0047 | 0.0934 | 0.9490 | 0.0025 | 0.0485 | 1.191 | 0.2103 | 0.597 | 0.041 | 13.4 | 1.001 | 0.9185 | 12.6 | n/a | n/a |
| P2 | n80 | depends | 0.5923 | 0.5974 | 0.0051 | 0.0938 | 0.9505 | 0.0020 | 0.0475 | 1.198 | 0.2110 | 0.597 | 0.041 | 13.3 | 0.995 | 0.9190 | 12.2 | n/a | n/a |
| P2 | n80 | carried_margin | 5.6740 | 5.6839 | 0.0099 | 0.6985 | 0.9495 | 0.0030 | 0.0475 | 1.152 | 1.5779 | 0.583 | 0.025 | 13.7 | 1.005 | 0.9030 | n/a | n/a | n/a |
| P2 | n80 | own_margin | 9.5794 | 9.5866 | 0.0072 | 0.7268 | 0.9700 | 0.0105 | 0.0195 | 1.333 | 1.7004 | 0.602 | 0.123 | 12.2 | 0.905 | 0.9250 | n/a | n/a | n/a |
| P2 | n80 | kappa | 0.9686 | 0.9687 | 0.0002 | 0.0044 | 0.9185 | 0.0730 | 0.0085 | 1.042 | 0.0097 | 0.584 | 0.013 | 14.2 | 1.249 | 0.8875 | 7.7 | n/a | n/a |
| P2 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9030 | 0.0960 | 0.0010 | 1.281 | 0.0649 | 0.546 | 0.137 | 12.0 | 1.325 | 0.8290 | n/a | n/a | n/a |
| P2 | n80 | carried_added | 5.8582 | 5.8685 | 0.0104 | 0.7306 | 0.9450 | 0.0025 | 0.0525 | 1.139 | 1.6413 | 0.584 | 0.021 | 13.8 | 1.031 | 0.9010 | n/a | n/a | n/a |
| P2 | n80 | pooled_retention | 0.6000 | 0.6007 | 0.0007 | 0.0601 | 0.8785 | 0.0025 | 0.1190 | 1.023 | 0.1278 | 0.464 | 0.000 | 15.1 | 2.240 | 0.8660 | 12.5 | n/a | n/a |
| P2 | n160 | large | 12.6650 | 12.6865 | 0.0215 | 1.4969 | 0.9300 | 0.0035 | 0.0665 | 1.059 | 3.2318 | 0.605 | 0.005 | 14.7 | 1.155 | 0.8945 | n/a | n/a | n/a |
| P2 | n160 | carries | 0.6000 | 0.6051 | 0.0051 | 0.0967 | 0.9145 | 0.0005 | 0.0850 | 1.109 | 0.2050 | 0.587 | 0.010 | 14.6 | 1.368 | 0.8880 | 16.2 | n/a | n/a |
| P2 | n160 | depends | 0.5966 | 0.6020 | 0.0053 | 0.0969 | 0.9145 | 0.0005 | 0.0850 | 1.112 | 0.2049 | 0.586 | 0.010 | 14.6 | 1.362 | 0.8890 | 15.7 | n/a | n/a |
| P2 | n160 | carried_margin | 13.0743 | 13.0965 | 0.0222 | 1.5091 | 0.9265 | 0.0040 | 0.0695 | 1.058 | 3.2476 | 0.603 | 0.005 | 14.7 | 1.158 | 0.8930 | n/a | n/a | n/a |
| P2 | n160 | own_margin | 21.9134 | 21.9237 | 0.0103 | 1.2809 | 0.9605 | 0.0320 | 0.0075 | 1.249 | 2.9829 | 0.590 | 0.073 | 12.8 | 0.944 | 0.9255 | n/a | n/a | n/a |
| P2 | n160 | kappa | 0.9861 | 0.9862 | 0.0001 | 0.0018 | 0.9065 | 0.0875 | 0.0060 | 0.984 | 0.0039 | 0.603 | 0.001 | 15.0 | 1.489 | 0.8855 | 8.5 | n/a | n/a |
| P2 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9040 | 0.0950 | 0.0010 | 1.284 | 0.0652 | 0.545 | 0.140 | 12.0 | 1.311 | 0.8310 | n/a | n/a | n/a |
| P2 | n160 | carried_added | 13.2585 | 13.2812 | 0.0227 | 1.5441 | 0.9260 | 0.0025 | 0.0715 | 1.056 | 3.3176 | 0.603 | 0.005 | 14.7 | 1.172 | 0.8905 | n/a | n/a | n/a |
| P2 | n160 | pooled_retention | 0.6000 | 0.6006 | 0.0006 | 0.0602 | 0.8775 | 0.0030 | 0.1195 | 1.015 | 0.1272 | 0.511 | 0.000 | 15.1 | 2.294 | 0.8680 | 16.4 | n/a | n/a |
| P2 | n320 | large | 14.6756 | 14.7076 | 0.0319 | 1.7056 | 0.9285 | 0.0020 | 0.0695 | 1.052 | 3.6544 | 0.601 | 0.004 | 14.7 | 1.184 | 0.8875 | n/a | n/a | n/a |
| P2 | n320 | carries | 0.6000 | 0.6056 | 0.0056 | 0.0960 | 0.9130 | 0.0010 | 0.0860 | 1.096 | 0.1999 | 0.592 | 0.010 | 14.7 | 1.410 | 0.8835 | 17.4 | n/a | n/a |
| P2 | n320 | depends | 0.5971 | 0.6028 | 0.0058 | 0.0961 | 0.9135 | 0.0005 | 0.0860 | 1.098 | 0.1999 | 0.593 | 0.010 | 14.7 | 1.404 | 0.8835 | 16.9 | n/a | n/a |
| P2 | n320 | carried_margin | 15.0849 | 15.1176 | 0.0327 | 1.7182 | 0.9270 | 0.0020 | 0.0710 | 1.051 | 3.6780 | 0.598 | 0.004 | 14.8 | 1.198 | 0.8880 | n/a | n/a | n/a |
| P2 | n320 | own_margin | 25.2643 | 25.2637 | -0.0006 | 1.3872 | 0.9555 | 0.0365 | 0.0080 | 1.245 | 3.2379 | 0.582 | 0.074 | 12.8 | 0.969 | 0.9070 | n/a | n/a | n/a |
| P2 | n320 | kappa | 0.9879 | 0.9880 | 0.0001 | 0.0016 | 0.9045 | 0.0880 | 0.0075 | 0.970 | 0.0034 | 0.596 | 0.001 | 15.0 | 1.523 | 0.8825 | 8.7 | n/a | n/a |
| P2 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9025 | 0.0965 | 0.0010 | 1.284 | 0.0650 | 0.543 | 0.135 | 12.0 | 1.323 | 0.8310 | n/a | n/a | n/a |
| P2 | n320 | carried_added | 15.2691 | 15.3022 | 0.0331 | 1.7536 | 0.9255 | 0.0020 | 0.0725 | 1.049 | 3.7515 | 0.598 | 0.004 | 14.8 | 1.212 | 0.8845 | n/a | n/a | n/a |
| P2 | n320 | pooled_retention | 0.6000 | 0.6006 | 0.0006 | 0.0603 | 0.8785 | 0.0030 | 0.1185 | 1.013 | 0.1275 | 0.530 | 0.000 | 15.1 | 2.315 | 0.8700 | 17.4 | n/a | n/a |
| P2 | h2 | large | 0.5523 | 0.5524 | 0.0000 | 0.0652 | 0.8970 | 0.0010 | 0.1020 | 1.091 | 0.1367 | 0.557 | 0.004 | 14.6 | 1.366 | 0.8610 | n/a | 1.000 | 0.8970 |
| P2 | h2 | carries | 0.6000 | 0.6002 | 0.0002 | 0.0571 | 0.8775 | 0.0030 | 0.1195 | 1.000 | 0.1198 | 0.594 | 0.000 | 15.1 | 2.219 | 0.8665 | 121.2 | 1.000 | 0.8775 |
| P2 | h2 | depends | 0.5573 | 0.5587 | 0.0014 | 0.0537 | 0.8780 | 0.0020 | 0.1200 | 1.030 | 0.1115 | 0.591 | 0.000 | 15.1 | 2.207 | 0.8680 | 55.6 | 1.000 | 0.8780 |
| P2 | h2 | carried_margin | 0.9616 | 0.9624 | 0.0007 | 0.0752 | 0.8790 | 0.0035 | 0.1175 | 1.018 | 0.1584 | 0.592 | 0.000 | 15.1 | 2.068 | 0.8685 | n/a | 1.000 | 0.8790 |
| P2 | h2 | own_margin | 1.7255 | 1.7255 | -0.0001 | 0.0318 | 0.9035 | 0.0945 | 0.0020 | 1.020 | 0.0662 | 0.589 | 0.001 | 15.2 | 1.381 | 0.8780 | n/a | 1.000 | 0.9035 |
| P2 | h2 | kappa | 0.8392 | 0.8409 | 0.0017 | 0.0192 | 0.8710 | 0.1150 | 0.0140 | 0.917 | 0.0402 | 0.584 | 0.000 | 15.1 | 2.031 | 0.8665 | 10.0 | 1.000 | 0.8710 |
| P2 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9045 | 0.0945 | 0.0010 | 1.282 | 0.0651 | 0.544 | 0.135 | 12.0 | 1.330 | 0.8305 | n/a | 1.000 | 0.9045 |
| P2 | h2 | carried_added | 1.1458 | 1.1470 | 0.0012 | 0.1155 | 0.8770 | 0.0030 | 0.1200 | 1.008 | 0.2432 | 0.585 | 0.000 | 15.1 | 2.283 | 0.8665 | n/a | 1.000 | 0.8770 |
| P2 | h2 | pooled_retention | 0.6000 | 0.6006 | 0.0006 | 0.0603 | 0.8755 | 0.0035 | 0.1210 | 1.007 | 0.1269 | 0.582 | 0.000 | 15.0 | 2.321 | 0.8690 | 121.9 | 1.000 | 0.8755 |
| P2 | h5 | large | 2.4719 | 2.4730 | 0.0011 | 0.2547 | 0.8785 | 0.0025 | 0.1190 | 1.019 | 0.5323 | 0.579 | 0.000 | 15.2 | 1.988 | 0.8630 | n/a | 0.994 | 0.8785 |
| P2 | h5 | carries | 0.6000 | 0.6006 | 0.0006 | 0.0622 | 0.8760 | 0.0015 | 0.1225 | 1.011 | 0.1306 | 0.568 | 0.000 | 15.2 | 2.336 | 0.8675 | 159.4 | 0.994 | 0.8760 |
| P2 | h5 | depends | 0.5850 | 0.5861 | 0.0011 | 0.0613 | 0.8755 | 0.0015 | 0.1230 | 1.022 | 0.1282 | 0.570 | 0.000 | 15.2 | 2.349 | 0.8670 | 79.1 | 0.994 | 0.8755 |
| P2 | h5 | carried_margin | 2.8812 | 2.8830 | 0.0018 | 0.2683 | 0.8770 | 0.0020 | 0.1210 | 1.010 | 0.5633 | 0.576 | 0.000 | 15.1 | 2.212 | 0.8665 | n/a | 0.994 | 0.8770 |
| P2 | h5 | own_margin | 4.9248 | 4.9245 | -0.0003 | 0.0609 | 0.9210 | 0.0770 | 0.0020 | 1.094 | 0.1361 | 0.588 | 0.042 | 13.6 | 1.289 | 0.8695 | n/a | 0.994 | 0.9220 |
| P2 | h5 | kappa | 0.9399 | 0.9405 | 0.0006 | 0.0072 | 0.8700 | 0.1160 | 0.0140 | 0.913 | 0.0150 | 0.580 | 0.000 | 15.1 | 2.040 | 0.8680 | 10.1 | 0.994 | 0.8705 |
| P2 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4100 | -0.0007 | 0.0284 | 0.9060 | 0.0930 | 0.0010 | 1.392 | 0.0656 | 0.553 | 0.157 | 11.6 | 1.283 | 0.8305 | n/a | 0.994 | 0.9065 |
| P2 | h5 | carried_added | 3.0654 | 3.0676 | 0.0022 | 0.3088 | 0.8765 | 0.0020 | 0.1215 | 1.007 | 0.6485 | 0.577 | 0.000 | 15.1 | 2.245 | 0.8660 | n/a | 0.994 | 0.8765 |
| P2 | h5 | pooled_retention | 0.6000 | 0.6004 | 0.0004 | 0.0603 | 0.8775 | 0.0020 | 0.1205 | 1.007 | 0.1267 | 0.573 | 0.000 | 15.1 | 2.305 | 0.8680 | 157.9 | 0.994 | 0.8775 |
| P2 | h10 | large | 5.9232 | 5.5302 | -0.3930 | 0.3995 | 0.7620 | 0.0000 | 0.2380 | 1.519 | 1.0188 | 0.575 | 0.000 | 15.2 | 2.616 | 0.7540 | n/a | 0.198 | 0.8790 |
| P2 | h10 | carries | 0.6000 | 0.5600 | -0.0400 | 0.0400 | 0.7610 | 0.0000 | 0.2390 | 1.539 | 0.1032 | 0.572 | 0.001 | 15.1 | 2.639 | 0.7540 | 147.4 | 0.198 | 0.8765 |
| P2 | h10 | depends | 0.5931 | 0.5537 | -0.0394 | 0.0395 | 0.7605 | 0.0000 | 0.2395 | 1.546 | 0.1020 | 0.573 | 0.001 | 15.1 | 2.648 | 0.7540 | 127.9 | 0.198 | 0.8770 |
| P2 | h10 | carried_margin | 6.3325 | 5.9242 | -0.4083 | 0.4042 | 0.7580 | 0.0000 | 0.2420 | 1.539 | 1.0437 | 0.578 | 0.000 | 15.1 | 2.714 | 0.7535 | n/a | 0.198 | 0.8770 |
| P2 | h10 | own_margin | 10.6772 | 10.7022 | 0.0250 | 0.0732 | 0.9615 | 0.0330 | 0.0055 | 1.744 | 0.1798 | 0.578 | 0.221 | 11.1 | 0.929 | 0.9065 | n/a | 0.198 | 0.9665 |
| P2 | h10 | kappa | 0.9717 | 0.9743 | 0.0026 | 0.0025 | 0.7675 | 0.2325 | 0.0000 | 1.387 | 0.0066 | 0.578 | 0.000 | 15.1 | 2.409 | 0.7515 | 11.6 | 0.198 | 0.8725 |
| P2 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3940 | 0.0153 | 0.0203 | 0.8000 | 0.2000 | 0.0000 | 1.334 | 0.0438 | 0.558 | 0.038 | 13.8 | 1.620 | 0.7100 | n/a | 0.198 | 0.8965 |
| P2 | h10 | carried_added | 6.5167 | 6.0813 | -0.4354 | 0.4304 | 0.7560 | 0.0000 | 0.2440 | 1.537 | 1.1102 | 0.576 | 0.000 | 15.1 | 2.742 | 0.7545 | n/a | 0.198 | 0.8760 |
| P2 | h10 | pooled_retention | 0.6000 | 0.5599 | -0.0401 | 0.0394 | 0.7570 | 0.0000 | 0.2430 | 1.541 | 0.1017 | 0.572 | 0.000 | 15.1 | 2.791 | 0.7535 | 145.4 | 0.198 | 0.8770 |
| P3 | n20 | large | -0.0593 | -0.0585 | 0.0009 | 0.0582 | 0.9235 | 0.0020 | 0.0745 | 1.206 | 0.1320 | 0.561 | 0.027 | 13.6 | 1.242 | 0.8730 | n/a | n/a | n/a |
| P3 | n20 | carries | 0.9000 | 0.9021 | 0.0021 | 0.0965 | 0.9060 | 0.0020 | 0.0920 | 1.172 | 0.2202 | 0.558 | 0.025 | 13.7 | 1.593 | 0.8710 | 9.9 | n/a | n/a |
| P3 | n20 | depends | 0.8550 | 0.8596 | 0.0046 | 0.1394 | 0.8995 | 0.0010 | 0.0995 | 1.183 | 0.3124 | 0.559 | 0.022 | 13.8 | 1.663 | 0.8675 | 14.6 | n/a | n/a |
| P3 | n20 | carried_margin | 0.3500 | 0.3501 | 0.0001 | 0.0547 | 0.8685 | 0.0000 | 0.1315 | 1.144 | 0.1181 | 0.551 | 0.006 | 14.6 | 2.259 | 0.8610 | n/a | n/a | n/a |
| P3 | n20 | own_margin | 0.4093 | 0.4085 | -0.0008 | 0.0276 | 0.9090 | 0.0010 | 0.0900 | 1.316 | 0.0642 | 0.568 | 0.133 | 12.0 | 1.291 | 0.8375 | n/a | n/a | n/a |
| P3 | n20 | kappa | 0.6552 | 0.6562 | 0.0010 | 0.0527 | 0.9170 | 0.0640 | 0.0190 | 0.972 | 0.1122 | 0.552 | 0.000 | 15.2 | 1.140 | 0.9005 | 7.2 | n/a | n/a |
| P3 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4085 | 0.0008 | 0.0276 | 0.9090 | 0.0900 | 0.0010 | 1.316 | 0.0642 | 0.568 | 0.133 | 12.0 | 1.291 | 0.8375 | n/a | n/a | n/a |
| P3 | n20 | carried_added | 0.5341 | 0.5340 | -0.0001 | 0.0750 | 0.9190 | 0.0010 | 0.0800 | 1.080 | 0.1562 | 0.549 | 0.000 | 15.2 | 1.251 | 0.9025 | n/a | n/a | n/a |
| P3 | n20 | pooled_retention | 0.9000 | 0.8996 | -0.0004 | 0.0892 | 0.8785 | 0.0030 | 0.1185 | 1.029 | 0.1909 | 0.538 | 0.000 | 15.1 | 2.227 | 0.8685 | 9.8 | n/a | n/a |
| P3 | n40 | large | 1.1603 | 1.1577 | -0.0026 | 0.2179 | 0.9460 | 0.0035 | 0.0505 | 1.105 | 0.4697 | 0.586 | 0.002 | 14.9 | 1.030 | 0.9245 | n/a | n/a | n/a |
| P3 | n40 | carries | 0.9000 | 0.9030 | 0.0030 | 0.1254 | 0.9585 | 0.0105 | 0.0310 | 1.034 | 0.2681 | 0.562 | 0.004 | 14.3 | 0.962 | 0.9245 | 9.3 | n/a | n/a |
| P3 | n40 | depends | 0.8896 | 0.8941 | 0.0045 | 0.1379 | 0.9565 | 0.0105 | 0.0330 | 1.033 | 0.2937 | 0.562 | 0.004 | 14.3 | 0.962 | 0.9230 | 9.5 | n/a | n/a |
| P3 | n40 | carried_margin | 1.5696 | 1.5662 | -0.0034 | 0.2247 | 0.9475 | 0.0030 | 0.0495 | 1.094 | 0.4831 | 0.586 | 0.001 | 15.0 | 1.009 | 0.9260 | n/a | n/a | n/a |
| P3 | n40 | own_margin | 1.7645 | 1.7639 | -0.0006 | 0.1808 | 0.9440 | 0.0095 | 0.0465 | 1.090 | 0.3992 | 0.548 | 0.004 | 14.2 | 1.053 | 0.9165 | n/a | n/a | n/a |
| P3 | n40 | kappa | 0.8950 | 0.8949 | -0.0001 | 0.0170 | 0.9310 | 0.0595 | 0.0095 | 0.962 | 0.0355 | 0.581 | 0.000 | 15.2 | 1.150 | 0.9170 | 6.9 | n/a | n/a |
| P3 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4085 | 0.0008 | 0.0276 | 0.9100 | 0.0890 | 0.0010 | 1.314 | 0.0640 | 0.571 | 0.132 | 12.0 | 1.283 | 0.8365 | n/a | n/a | n/a |
| P3 | n40 | carried_added | 1.7538 | 1.7502 | -0.0036 | 0.2497 | 0.9430 | 0.0030 | 0.0540 | 1.084 | 0.5354 | 0.587 | 0.001 | 15.1 | 1.030 | 0.9195 | n/a | n/a | n/a |
| P3 | n40 | pooled_retention | 0.9000 | 0.8994 | -0.0006 | 0.0892 | 0.8795 | 0.0030 | 0.1175 | 1.027 | 0.1907 | 0.523 | 0.000 | 15.1 | 2.191 | 0.8675 | 9.4 | n/a | n/a |
| P3 | n80 | large | 8.1937 | 8.1845 | -0.0092 | 1.0217 | 0.9475 | 0.0025 | 0.0500 | 1.196 | 2.3685 | 0.598 | 0.036 | 13.6 | 1.018 | 0.9135 | n/a | n/a | n/a |
| P3 | n80 | carries | 0.9000 | 0.9041 | 0.0041 | 0.1401 | 0.9535 | 0.0025 | 0.0440 | 1.175 | 0.3137 | 0.597 | 0.043 | 13.3 | 0.981 | 0.9205 | 12.4 | n/a | n/a |
| P3 | n80 | depends | 0.8981 | 0.9029 | 0.0048 | 0.1427 | 0.9530 | 0.0025 | 0.0445 | 1.179 | 0.3193 | 0.597 | 0.043 | 13.3 | 0.978 | 0.9205 | 12.1 | n/a | n/a |
| P3 | n80 | carried_margin | 8.6030 | 8.5930 | -0.0100 | 1.0321 | 0.9460 | 0.0030 | 0.0510 | 1.193 | 2.3899 | 0.603 | 0.035 | 13.6 | 1.032 | 0.9120 | n/a | n/a | n/a |
| P3 | n80 | own_margin | 9.5794 | 9.5951 | 0.0157 | 0.7418 | 0.9610 | 0.0160 | 0.0230 | 1.299 | 1.7269 | 0.602 | 0.128 | 12.1 | 0.927 | 0.9190 | n/a | n/a | n/a |
| P3 | n80 | kappa | 0.9790 | 0.9792 | 0.0001 | 0.0030 | 0.9180 | 0.0725 | 0.0095 | 1.006 | 0.0064 | 0.608 | 0.013 | 14.1 | 1.195 | 0.8915 | 7.8 | n/a | n/a |
| P3 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4085 | 0.0008 | 0.0275 | 0.9080 | 0.0910 | 0.0010 | 1.317 | 0.0640 | 0.570 | 0.130 | 12.0 | 1.301 | 0.8380 | n/a | n/a | n/a |
| P3 | n80 | carried_added | 8.7872 | 8.7770 | -0.0102 | 1.0634 | 0.9445 | 0.0030 | 0.0525 | 1.184 | 2.4537 | 0.602 | 0.032 | 13.7 | 1.038 | 0.9115 | n/a | n/a | n/a |
| P3 | n80 | pooled_retention | 0.9000 | 0.8996 | -0.0004 | 0.0894 | 0.8790 | 0.0035 | 0.1175 | 1.025 | 0.1910 | 0.463 | 0.000 | 15.1 | 2.215 | 0.8680 | 12.6 | n/a | n/a |
| P3 | n160 | large | 19.2943 | 19.2662 | -0.0281 | 2.1764 | 0.9350 | 0.0040 | 0.0610 | 1.126 | 4.8533 | 0.608 | 0.004 | 14.7 | 1.122 | 0.9020 | n/a | n/a | n/a |
| P3 | n160 | carries | 0.9000 | 0.9055 | 0.0055 | 0.1416 | 0.9155 | 0.0015 | 0.0830 | 1.138 | 0.3036 | 0.593 | 0.005 | 14.7 | 1.354 | 0.8875 | 16.2 | n/a | n/a |
| P3 | n160 | depends | 0.8992 | 0.9050 | 0.0058 | 0.1428 | 0.9155 | 0.0015 | 0.0830 | 1.140 | 0.3055 | 0.593 | 0.005 | 14.7 | 1.355 | 0.8875 | 15.8 | n/a | n/a |
| P3 | n160 | carried_margin | 19.7036 | 19.6747 | -0.0289 | 2.1882 | 0.9350 | 0.0040 | 0.0610 | 1.125 | 4.8736 | 0.609 | 0.004 | 14.8 | 1.128 | 0.8995 | n/a | n/a | n/a |
| P3 | n160 | own_margin | 21.9134 | 21.9064 | -0.0070 | 1.2917 | 0.9555 | 0.0355 | 0.0090 | 1.219 | 3.0089 | 0.585 | 0.072 | 12.7 | 0.946 | 0.9195 | n/a | n/a | n/a |
| P3 | n160 | kappa | 0.9907 | 0.9908 | 0.0001 | 0.0012 | 0.9055 | 0.0875 | 0.0070 | 0.976 | 0.0026 | 0.610 | 0.000 | 15.0 | 1.446 | 0.8900 | 8.5 | n/a | n/a |
| P3 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4085 | 0.0008 | 0.0275 | 0.9105 | 0.0885 | 0.0010 | 1.317 | 0.0641 | 0.568 | 0.130 | 12.0 | 1.291 | 0.8410 | n/a | n/a | n/a |
| P3 | n160 | carried_added | 19.8878 | 19.8587 | -0.0291 | 2.2227 | 0.9325 | 0.0040 | 0.0635 | 1.122 | 4.9487 | 0.609 | 0.004 | 14.8 | 1.133 | 0.8985 | n/a | n/a | n/a |
| P3 | n160 | pooled_retention | 0.9000 | 0.8999 | -0.0001 | 0.0893 | 0.8785 | 0.0035 | 0.1180 | 1.023 | 0.1904 | 0.524 | 0.000 | 15.1 | 2.157 | 0.8690 | 16.3 | n/a | n/a |
| P3 | n320 | large | 22.3102 | 22.2931 | -0.0171 | 2.5051 | 0.9270 | 0.0030 | 0.0700 | 1.096 | 5.4721 | 0.589 | 0.003 | 14.8 | 1.150 | 0.8885 | n/a | n/a | n/a |
| P3 | n320 | carries | 0.9000 | 0.9054 | 0.0054 | 0.1406 | 0.9095 | 0.0020 | 0.0885 | 1.119 | 0.2991 | 0.592 | 0.004 | 14.7 | 1.343 | 0.8875 | 17.3 | n/a | n/a |
| P3 | n320 | depends | 0.8993 | 0.9050 | 0.0057 | 0.1417 | 0.9095 | 0.0020 | 0.0885 | 1.120 | 0.3008 | 0.592 | 0.004 | 14.7 | 1.344 | 0.8875 | 16.8 | n/a | n/a |
| P3 | n320 | carried_margin | 22.7195 | 22.7016 | -0.0178 | 2.5171 | 0.9265 | 0.0030 | 0.0705 | 1.096 | 5.4995 | 0.590 | 0.003 | 14.8 | 1.161 | 0.8910 | n/a | n/a | n/a |
| P3 | n320 | own_margin | 25.2643 | 25.2677 | 0.0034 | 1.4021 | 0.9530 | 0.0360 | 0.0110 | 1.194 | 3.2419 | 0.591 | 0.072 | 12.9 | 0.973 | 0.9080 | n/a | n/a | n/a |
| P3 | n320 | kappa | 0.9920 | 0.9920 | 0.0001 | 0.0010 | 0.9060 | 0.0890 | 0.0050 | 0.986 | 0.0022 | 0.583 | 0.001 | 15.1 | 1.467 | 0.8890 | 8.7 | n/a | n/a |
| P3 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4085 | 0.0008 | 0.0275 | 0.9075 | 0.0915 | 0.0010 | 1.317 | 0.0642 | 0.567 | 0.131 | 12.1 | 1.288 | 0.8370 | n/a | n/a | n/a |
| P3 | n320 | carried_added | 22.9037 | 22.8856 | -0.0181 | 2.5522 | 0.9225 | 0.0030 | 0.0745 | 1.093 | 5.5747 | 0.591 | 0.003 | 14.9 | 1.176 | 0.8900 | n/a | n/a | n/a |
| P3 | n320 | pooled_retention | 0.9000 | 0.8995 | -0.0005 | 0.0893 | 0.8780 | 0.0040 | 0.1180 | 1.019 | 0.1899 | 0.529 | 0.000 | 15.1 | 2.229 | 0.8675 | 17.2 | n/a | n/a |
| P3 | h2 | large | 1.1253 | 1.1247 | -0.0005 | 0.1197 | 0.8810 | 0.0030 | 0.1160 | 1.030 | 0.2505 | 0.555 | 0.000 | 15.3 | 1.666 | 0.8600 | n/a | 1.000 | 0.8810 |
| P3 | h2 | carries | 0.9000 | 0.8987 | -0.0013 | 0.0844 | 0.8795 | 0.0030 | 0.1175 | 1.007 | 0.1789 | 0.596 | 0.000 | 15.1 | 2.093 | 0.8645 | 121.4 | 1.000 | 0.8795 |
| P3 | h2 | depends | 0.8893 | 0.8900 | 0.0007 | 0.0921 | 0.8785 | 0.0030 | 0.1185 | 1.030 | 0.1929 | 0.596 | 0.000 | 15.1 | 2.142 | 0.8640 | 55.5 | 1.000 | 0.8785 |
| P3 | h2 | carried_margin | 1.5346 | 1.5333 | -0.0013 | 0.1312 | 0.8795 | 0.0025 | 0.1180 | 1.016 | 0.2785 | 0.589 | 0.000 | 15.1 | 2.103 | 0.8660 | n/a | 1.000 | 0.8795 |
| P3 | h2 | own_margin | 1.7255 | 1.7258 | 0.0003 | 0.0312 | 0.9055 | 0.0905 | 0.0040 | 1.035 | 0.0664 | 0.575 | 0.002 | 15.2 | 1.375 | 0.8780 | n/a | 1.000 | 0.9055 |
| P3 | h2 | kappa | 0.8928 | 0.8941 | 0.0013 | 0.0126 | 0.8750 | 0.1110 | 0.0140 | 0.941 | 0.0267 | 0.590 | 0.000 | 15.0 | 1.948 | 0.8700 | 10.1 | 1.000 | 0.8750 |
| P3 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0275 | 0.9105 | 0.0885 | 0.0010 | 1.317 | 0.0643 | 0.572 | 0.130 | 12.0 | 1.286 | 0.8380 | n/a | 1.000 | 0.9105 |
| P3 | h2 | carried_added | 1.7188 | 1.7172 | -0.0015 | 0.1710 | 0.8780 | 0.0030 | 0.1190 | 1.012 | 0.3629 | 0.584 | 0.000 | 15.1 | 2.185 | 0.8655 | n/a | 1.000 | 0.8780 |
| P3 | h2 | pooled_retention | 0.9000 | 0.8992 | -0.0008 | 0.0891 | 0.8790 | 0.0030 | 0.1180 | 1.013 | 0.1892 | 0.560 | 0.000 | 15.0 | 2.241 | 0.8665 | 121.8 | 1.000 | 0.8790 |
| P3 | h5 | large | 4.0046 | 4.0051 | 0.0004 | 0.4037 | 0.8780 | 0.0040 | 0.1180 | 1.026 | 0.8544 | 0.564 | 0.000 | 15.2 | 2.014 | 0.8660 | n/a | 0.995 | 0.8765 |
| P3 | h5 | carries | 0.9000 | 0.9002 | 0.0002 | 0.0918 | 0.8805 | 0.0035 | 0.1160 | 1.028 | 0.1946 | 0.556 | 0.000 | 15.1 | 2.231 | 0.8680 | 157.8 | 0.995 | 0.8790 |
| P3 | h5 | depends | 0.8963 | 0.8972 | 0.0010 | 0.0949 | 0.8815 | 0.0025 | 0.1160 | 1.037 | 0.2000 | 0.556 | 0.000 | 15.1 | 2.253 | 0.8680 | 78.8 | 0.995 | 0.8800 |
| P3 | h5 | carried_margin | 4.4139 | 4.4136 | -0.0003 | 0.4167 | 0.8795 | 0.0040 | 0.1165 | 1.025 | 0.8867 | 0.560 | 0.000 | 15.1 | 2.169 | 0.8665 | n/a | 0.995 | 0.8780 |
| P3 | h5 | own_margin | 4.9248 | 4.9249 | 0.0001 | 0.0592 | 0.9245 | 0.0715 | 0.0040 | 1.159 | 0.1366 | 0.565 | 0.046 | 13.5 | 1.197 | 0.8740 | n/a | 0.995 | 0.9235 |
| P3 | h5 | kappa | 0.9599 | 0.9604 | 0.0005 | 0.0047 | 0.8735 | 0.1110 | 0.0155 | 0.941 | 0.0100 | 0.571 | 0.000 | 15.1 | 1.913 | 0.8700 | 10.1 | 0.995 | 0.8725 |
| P3 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4086 | 0.0007 | 0.0276 | 0.9135 | 0.0855 | 0.0010 | 1.450 | 0.0647 | 0.561 | 0.155 | 11.7 | 1.290 | 0.8415 | n/a | 0.995 | 0.9130 |
| P3 | h5 | carried_added | 4.5981 | 4.5978 | -0.0004 | 0.4566 | 0.8795 | 0.0040 | 0.1165 | 1.023 | 0.9718 | 0.557 | 0.000 | 15.1 | 2.179 | 0.8660 | n/a | 0.995 | 0.8780 |
| P3 | h5 | pooled_retention | 0.9000 | 0.8999 | -0.0001 | 0.0891 | 0.8815 | 0.0030 | 0.1155 | 1.024 | 0.1894 | 0.562 | 0.000 | 15.1 | 2.212 | 0.8670 | 156.9 | 0.995 | 0.8805 |
| P3 | h10 | large | 9.1816 | 8.5529 | -0.6286 | 0.6037 | 0.7475 | 0.0000 | 0.2525 | 1.555 | 1.5729 | 0.586 | 0.000 | 15.1 | 2.610 | 0.7450 | n/a | 0.197 | 0.8825 |
| P3 | h10 | carries | 0.9000 | 0.8383 | -0.0617 | 0.0590 | 0.7485 | 0.0000 | 0.2515 | 1.566 | 0.1543 | 0.565 | 0.001 | 15.1 | 2.607 | 0.7465 | 147.0 | 0.197 | 0.8805 |
| P3 | h10 | depends | 0.8983 | 0.8361 | -0.0622 | 0.0595 | 0.7480 | 0.0000 | 0.2520 | 1.572 | 0.1554 | 0.565 | 0.001 | 15.1 | 2.615 | 0.7465 | 129.0 | 0.197 | 0.8810 |
| P3 | h10 | carried_margin | 9.5909 | 8.9471 | -0.6438 | 0.6076 | 0.7495 | 0.0000 | 0.2505 | 1.574 | 1.5917 | 0.583 | 0.000 | 15.1 | 2.708 | 0.7460 | n/a | 0.197 | 0.8805 |
| P3 | h10 | own_margin | 10.6772 | 10.7037 | 0.0266 | 0.0733 | 0.9595 | 0.0365 | 0.0040 | 1.716 | 0.1796 | 0.567 | 0.210 | 11.2 | 0.947 | 0.8965 | n/a | 0.197 | 0.9745 |
| P3 | h10 | kappa | 0.9812 | 0.9829 | 0.0018 | 0.0017 | 0.7570 | 0.2430 | 0.0000 | 1.387 | 0.0044 | 0.573 | 0.000 | 15.1 | 2.382 | 0.7445 | 11.7 | 0.197 | 0.8700 |
| P3 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3942 | 0.0151 | 0.0202 | 0.8080 | 0.1920 | 0.0000 | 1.341 | 0.0431 | 0.575 | 0.040 | 13.8 | 1.609 | 0.7160 | n/a | 0.197 | 0.9040 |
| P3 | h10 | carried_added | 9.7751 | 9.1036 | -0.6715 | 0.6336 | 0.7490 | 0.0000 | 0.2510 | 1.572 | 1.6591 | 0.581 | 0.000 | 15.1 | 2.716 | 0.7460 | n/a | 0.197 | 0.8805 |
| P3 | h10 | pooled_retention | 0.9000 | 0.8382 | -0.0618 | 0.0581 | 0.7455 | 0.0000 | 0.2545 | 1.570 | 0.1524 | 0.563 | 0.000 | 15.1 | 2.779 | 0.7440 | 146.1 | 0.197 | 0.8770 |
| P4 | n20 | large | -0.4818 | -0.4812 | 0.0006 | 0.0632 | 0.8950 | 0.1030 | 0.0020 | 1.013 | 0.1280 | 0.195 | 0.196 | 10.6 | 1.407 | 0.8080 | n/a | n/a | n/a |
| P4 | n20 | carries | 0.2000 | 0.2006 | 0.0006 | 0.0225 | 0.9000 | 0.0015 | 0.0985 | 1.082 | 0.0488 | 0.605 | 0.029 | 13.7 | 1.654 | 0.8665 | 8.6 | n/a | n/a |
| P4 | n20 | depends | -0.1524 | -0.1536 | -0.0011 | 0.0803 | 0.9200 | 0.0770 | 0.0030 | 1.023 | 0.1598 | 0.069 | 0.034 | 15.0 | 1.223 | 0.8535 | 9.1 | n/a | n/a |
| P4 | n20 | carried_margin | -0.0637 | -0.0631 | 0.0006 | 0.0316 | 0.8975 | 0.0985 | 0.0040 | 1.048 | 0.0681 | 0.124 | 0.005 | 15.7 | 1.329 | 0.8660 | n/a | n/a | n/a |
| P4 | n20 | own_margin | 0.4181 | 0.4181 | -0.0000 | 0.0541 | 0.9275 | 0.0110 | 0.0615 | 0.962 | 0.1324 | 0.116 | 0.666 | 5.9 | 1.203 | 0.6170 | n/a | n/a | n/a |
| P4 | n20 | kappa | -0.5291 | -0.5304 | -0.0013 | 0.2626 | 0.9200 | 0.0595 | 0.0205 | 0.919 | 0.5342 | 0.124 | 0.015 | 14.9 | 1.141 | 0.8705 | 6.6 | n/a | n/a |
| P4 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0541 | 0.9275 | 0.0615 | 0.0110 | 0.962 | 0.1324 | 0.116 | 0.666 | 5.9 | 1.203 | 0.6170 | n/a | n/a | n/a |
| P4 | n20 | carried_added | 0.1205 | 0.1205 | 0.0000 | 0.0189 | 0.9200 | 0.0005 | 0.0795 | 1.068 | 0.0390 | 0.119 | 0.036 | 14.3 | 1.208 | 0.8685 | n/a | n/a | n/a |
| P4 | n20 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0193 | 0.8745 | 0.0010 | 0.1245 | 1.095 | 0.0425 | 0.765 | 0.000 | 15.0 | 2.222 | 0.8690 | 8.6 | n/a | n/a |
| P4 | n40 | large | -0.2046 | -0.2034 | 0.0012 | 0.0559 | 0.9675 | 0.0215 | 0.0110 | 1.053 | 0.1153 | 0.519 | 0.033 | 13.1 | 0.890 | 0.9055 | n/a | n/a | n/a |
| P4 | n40 | carries | 0.2000 | 0.2009 | 0.0009 | 0.0275 | 0.9510 | 0.0105 | 0.0385 | 1.071 | 0.0598 | 0.605 | 0.011 | 14.2 | 1.003 | 0.9200 | 8.1 | n/a | n/a |
| P4 | n40 | depends | 0.1183 | 0.1194 | 0.0011 | 0.0277 | 0.9525 | 0.0080 | 0.0395 | 1.044 | 0.0589 | 0.506 | 0.018 | 14.1 | 0.988 | 0.9175 | 8.1 | n/a | n/a |
| P4 | n40 | carried_margin | 0.2135 | 0.2147 | 0.0012 | 0.0527 | 0.9470 | 0.0085 | 0.0445 | 0.981 | 0.1077 | 0.170 | 0.170 | 11.4 | 1.009 | 0.8560 | n/a | n/a | n/a |
| P4 | n40 | own_margin | 1.8041 | 1.8079 | 0.0038 | 0.2385 | 0.9440 | 0.0080 | 0.0480 | 1.055 | 0.5028 | 0.164 | 0.269 | 10.2 | 1.029 | 0.8345 | n/a | n/a | n/a |
| P4 | n40 | kappa | 0.5368 | 0.5360 | -0.0008 | 0.0836 | 0.9245 | 0.0660 | 0.0095 | 0.935 | 0.1690 | 0.170 | 0.037 | 14.3 | 1.144 | 0.8705 | 6.3 | n/a | n/a |
| P4 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0541 | 0.9280 | 0.0615 | 0.0105 | 0.962 | 0.1329 | 0.117 | 0.668 | 5.9 | 1.216 | 0.6145 | n/a | n/a | n/a |
| P4 | n40 | carried_added | 0.3976 | 0.3983 | 0.0006 | 0.0638 | 0.9405 | 0.0015 | 0.0580 | 1.054 | 0.1351 | 0.171 | 0.054 | 13.8 | 1.062 | 0.8790 | n/a | n/a | n/a |
| P4 | n40 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0193 | 0.8780 | 0.0005 | 0.1215 | 1.096 | 0.0423 | 0.760 | 0.000 | 15.0 | 2.214 | 0.8715 | 8.2 | n/a | n/a |
| P4 | n80 | large | 1.3720 | 1.3688 | -0.0031 | 0.2762 | 0.9430 | 0.0085 | 0.0485 | 1.019 | 0.6170 | 0.218 | 0.320 | 9.1 | 1.051 | 0.8205 | n/a | n/a | n/a |
| P4 | n80 | carries | 0.2000 | 0.2011 | 0.0011 | 0.0313 | 0.9445 | 0.0020 | 0.0535 | 1.208 | 0.0709 | 0.640 | 0.025 | 13.6 | 1.123 | 0.9150 | 8.0 | n/a | n/a |
| P4 | n80 | depends | 0.1848 | 0.1857 | 0.0009 | 0.0289 | 0.9515 | 0.0015 | 0.0470 | 1.225 | 0.0655 | 0.638 | 0.035 | 13.4 | 0.994 | 0.9180 | 7.8 | n/a | n/a |
| P4 | n80 | carried_margin | 1.7901 | 1.7869 | -0.0031 | 0.3134 | 0.9405 | 0.0095 | 0.0500 | 0.992 | 0.6984 | 0.135 | 0.434 | 8.3 | 1.060 | 0.7925 | n/a | n/a | n/a |
| P4 | n80 | own_margin | 9.6872 | 9.6877 | 0.0006 | 1.3645 | 0.9185 | 0.0260 | 0.0555 | 0.973 | 3.5380 | 0.140 | 0.625 | 6.5 | 1.229 | 0.6770 | n/a | n/a | n/a |
| P4 | n80 | kappa | 0.9067 | 0.9060 | -0.0007 | 0.0176 | 0.9280 | 0.0615 | 0.0105 | 0.924 | 0.0356 | 0.135 | 0.257 | 10.3 | 1.133 | 0.8155 | 6.3 | n/a | n/a |
| P4 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0541 | 0.9280 | 0.0605 | 0.0115 | 0.961 | 0.1334 | 0.117 | 0.666 | 5.9 | 1.204 | 0.6160 | n/a | n/a | n/a |
| P4 | n80 | carried_added | 1.9743 | 1.9705 | -0.0037 | 0.3329 | 0.9460 | 0.0070 | 0.0470 | 1.008 | 0.7269 | 0.135 | 0.336 | 9.3 | 1.036 | 0.8195 | n/a | n/a | n/a |
| P4 | n80 | pooled_retention | 0.2000 | 0.1998 | -0.0002 | 0.0193 | 0.8765 | 0.0015 | 0.1220 | 1.099 | 0.0427 | 0.814 | 0.000 | 15.0 | 2.181 | 0.8700 | 7.9 | n/a | n/a |
| P4 | n160 | large | 3.7326 | 3.7245 | -0.0080 | 0.4422 | 0.9370 | 0.0020 | 0.0610 | 1.135 | 0.9920 | 0.560 | 0.011 | 14.3 | 1.119 | 0.8945 | n/a | n/a | n/a |
| P4 | n160 | carries | 0.2000 | 0.2013 | 0.0013 | 0.0311 | 0.9105 | 0.0000 | 0.0895 | 1.169 | 0.0679 | 0.600 | 0.010 | 14.5 | 1.569 | 0.8830 | 16.0 | n/a | n/a |
| P4 | n160 | depends | 0.1931 | 0.1944 | 0.0013 | 0.0297 | 0.9155 | 0.0000 | 0.0845 | 1.174 | 0.0650 | 0.600 | 0.011 | 14.4 | 1.327 | 0.8840 | 15.6 | n/a | n/a |
| P4 | n160 | carried_margin | 4.1507 | 4.1426 | -0.0081 | 0.4610 | 0.9345 | 0.0025 | 0.0630 | 1.114 | 1.0270 | 0.518 | 0.015 | 14.3 | 1.116 | 0.8900 | n/a | n/a | n/a |
| P4 | n160 | own_margin | 21.4901 | 21.4615 | -0.0285 | 1.3054 | 0.9550 | 0.0365 | 0.0085 | 1.203 | 2.9932 | 0.509 | 0.141 | 11.9 | 0.973 | 0.8990 | n/a | n/a | n/a |
| P4 | n160 | kappa | 0.9575 | 0.9579 | 0.0004 | 0.0055 | 0.9035 | 0.0910 | 0.0055 | 1.044 | 0.0121 | 0.521 | 0.003 | 14.9 | 1.375 | 0.8860 | 8.4 | n/a | n/a |
| P4 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0541 | 0.9295 | 0.0605 | 0.0100 | 0.962 | 0.1324 | 0.116 | 0.669 | 5.9 | 1.207 | 0.6160 | n/a | n/a | n/a |
| P4 | n160 | carried_added | 4.3349 | 4.3262 | -0.0086 | 0.4936 | 0.9285 | 0.0025 | 0.0690 | 1.108 | 1.0955 | 0.518 | 0.013 | 14.4 | 1.192 | 0.8865 | n/a | n/a | n/a |
| P4 | n160 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0193 | 0.8775 | 0.0015 | 0.1210 | 1.094 | 0.0424 | 0.551 | 0.000 | 15.1 | 2.210 | 0.8695 | 16.1 | n/a | n/a |
| P4 | n320 | large | 4.4340 | 4.4225 | -0.0115 | 0.5102 | 0.9320 | 0.0030 | 0.0650 | 1.130 | 1.1394 | 0.565 | 0.007 | 14.6 | 1.131 | 0.8920 | n/a | n/a | n/a |
| P4 | n320 | carries | 0.2000 | 0.2011 | 0.0011 | 0.0308 | 0.9060 | 0.0005 | 0.0935 | 1.159 | 0.0669 | 0.578 | 0.009 | 14.7 | 1.631 | 0.8810 | 17.2 | n/a | n/a |
| P4 | n320 | depends | 0.1941 | 0.1952 | 0.0011 | 0.0296 | 0.9110 | 0.0005 | 0.0885 | 1.164 | 0.0644 | 0.577 | 0.009 | 14.6 | 1.425 | 0.8840 | 16.7 | n/a | n/a |
| P4 | n320 | carried_margin | 4.8521 | 4.8405 | -0.0116 | 0.5233 | 0.9255 | 0.0025 | 0.0720 | 1.124 | 1.1622 | 0.565 | 0.007 | 14.7 | 1.212 | 0.8890 | n/a | n/a | n/a |
| P4 | n320 | own_margin | 24.9973 | 24.9730 | -0.0243 | 1.3728 | 0.9580 | 0.0340 | 0.0080 | 1.243 | 3.2285 | 0.572 | 0.093 | 12.4 | 0.956 | 0.9080 | n/a | n/a | n/a |
| P4 | n320 | kappa | 0.9634 | 0.9637 | 0.0003 | 0.0047 | 0.9050 | 0.0905 | 0.0045 | 1.044 | 0.0102 | 0.571 | 0.002 | 15.0 | 1.419 | 0.8860 | 8.7 | n/a | n/a |
| P4 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0541 | 0.9275 | 0.0615 | 0.0110 | 0.962 | 0.1327 | 0.114 | 0.669 | 5.9 | 1.209 | 0.6165 | n/a | n/a | n/a |
| P4 | n320 | carried_added | 5.0363 | 5.0242 | -0.0121 | 0.5570 | 0.9185 | 0.0025 | 0.0790 | 1.118 | 1.2347 | 0.565 | 0.006 | 14.8 | 1.257 | 0.8865 | n/a | n/a | n/a |
| P4 | n320 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0192 | 0.8775 | 0.0010 | 0.1215 | 1.094 | 0.0422 | 0.513 | 0.000 | 15.1 | 2.227 | 0.8700 | 17.4 | n/a | n/a |
| P4 | h2 | large | -0.2198 | -0.2195 | 0.0002 | 0.0542 | 0.9275 | 0.0645 | 0.0080 | 0.966 | 0.1299 | 0.123 | 0.632 | 6.3 | 1.155 | 0.6390 | n/a | 1.000 | 0.9275 |
| P4 | h2 | carries | 0.2000 | 0.1996 | -0.0004 | 0.0182 | 0.8785 | 0.0010 | 0.1205 | 1.086 | 0.0401 | 0.582 | 0.000 | 15.1 | 2.275 | 0.8710 | 115.6 | 1.000 | 0.8785 |
| P4 | h2 | depends | 0.1148 | 0.1148 | -0.0000 | 0.0026 | 0.9920 | 0.0000 | 0.0080 | 1.710 | 0.0070 | 0.568 | 0.011 | 14.1 | 0.723 | 0.9750 | 54.4 | 1.000 | 0.9920 |
| P4 | h2 | carried_margin | 0.1985 | 0.1985 | -0.0000 | 0.0050 | 0.9900 | 0.0065 | 0.0035 | 1.546 | 0.0130 | 0.507 | 0.005 | 14.3 | 0.771 | 0.9605 | n/a | 1.000 | 0.9900 |
| P4 | h2 | own_margin | 1.7295 | 1.7302 | 0.0007 | 0.0316 | 0.9190 | 0.0785 | 0.0025 | 1.079 | 0.0679 | 0.455 | 0.004 | 15.0 | 1.212 | 0.8760 | n/a | 1.000 | 0.9190 |
| P4 | h2 | kappa | 0.5187 | 0.5247 | 0.0060 | 0.0558 | 0.8730 | 0.1190 | 0.0080 | 0.981 | 0.1210 | 0.511 | 0.000 | 15.1 | 1.949 | 0.8685 | 10.0 | 1.000 | 0.8730 |
| P4 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4181 | 0.0003 | 0.0541 | 0.9270 | 0.0625 | 0.0105 | 0.961 | 0.1321 | 0.116 | 0.669 | 5.9 | 1.204 | 0.6140 | n/a | 1.000 | 0.9270 |
| P4 | h2 | carried_added | 0.3827 | 0.3821 | -0.0006 | 0.0369 | 0.8775 | 0.0005 | 0.1220 | 1.092 | 0.0811 | 0.516 | 0.000 | 15.1 | 2.168 | 0.8715 | n/a | 1.000 | 0.8775 |
| P4 | h2 | pooled_retention | 0.2000 | 0.1997 | -0.0003 | 0.0192 | 0.8780 | 0.0010 | 0.1210 | 1.089 | 0.0423 | 0.576 | 0.000 | 15.0 | 2.225 | 0.8710 | 115.0 | 1.000 | 0.8780 |
| P4 | h5 | large | 0.4217 | 0.4212 | -0.0005 | 0.0674 | 0.9350 | 0.0065 | 0.0585 | 1.052 | 0.1497 | 0.197 | 0.280 | 10.0 | 1.095 | 0.7940 | n/a | 0.992 | 0.9350 |
| P4 | h5 | carries | 0.2000 | 0.1998 | -0.0002 | 0.0198 | 0.8755 | 0.0015 | 0.1230 | 1.100 | 0.0435 | 0.608 | 0.000 | 15.1 | 2.362 | 0.8695 | 147.0 | 0.992 | 0.8755 |
| P4 | h5 | depends | 0.1702 | 0.1701 | -0.0000 | 0.0140 | 0.8770 | 0.0005 | 0.1225 | 1.126 | 0.0309 | 0.604 | 0.001 | 15.2 | 2.097 | 0.8675 | 77.6 | 0.992 | 0.8765 |
| P4 | h5 | carried_margin | 0.8400 | 0.8392 | -0.0008 | 0.0601 | 0.8770 | 0.0010 | 0.1220 | 1.115 | 0.1337 | 0.541 | 0.001 | 15.2 | 1.954 | 0.8685 | n/a | 0.992 | 0.8765 |
| P4 | h5 | own_margin | 4.9368 | 4.9373 | 0.0005 | 0.0606 | 0.9365 | 0.0575 | 0.0060 | 1.171 | 0.1391 | 0.537 | 0.067 | 13.1 | 1.081 | 0.8765 | n/a | 0.992 | 0.9360 |
| P4 | h5 | kappa | 0.8202 | 0.8223 | 0.0022 | 0.0208 | 0.8700 | 0.1200 | 0.0100 | 0.981 | 0.0452 | 0.541 | 0.000 | 15.1 | 1.952 | 0.8675 | 10.0 | 0.992 | 0.8705 |
| P4 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4180 | 0.0003 | 0.0539 | 0.9155 | 0.0725 | 0.0120 | 1.011 | 0.1349 | 0.156 | 0.636 | 6.0 | 1.283 | 0.6180 | n/a | 0.992 | 0.9145 |
| P4 | h5 | carried_added | 1.0242 | 1.0230 | -0.0012 | 0.0988 | 0.8770 | 0.0010 | 0.1220 | 1.095 | 0.2173 | 0.546 | 0.000 | 15.1 | 2.175 | 0.8680 | n/a | 0.992 | 0.8765 |
| P4 | h5 | pooled_retention | 0.2000 | 0.1998 | -0.0002 | 0.0192 | 0.8770 | 0.0010 | 0.1220 | 1.095 | 0.0423 | 0.557 | 0.000 | 15.1 | 2.199 | 0.8705 | 146.8 | 0.992 | 0.8765 |
| P4 | h10 | large | 1.5769 | 1.4719 | -0.1050 | 0.1184 | 0.7630 | 0.0000 | 0.2370 | 1.360 | 0.2759 | 0.361 | 0.008 | 15.1 | 2.209 | 0.7390 | n/a | 0.188 | 0.8810 |
| P4 | h10 | carries | 0.2000 | 0.1865 | -0.0135 | 0.0135 | 0.7525 | 0.0000 | 0.2475 | 1.491 | 0.0342 | 0.566 | 0.000 | 15.1 | 2.847 | 0.7455 | 119.6 | 0.188 | 0.8780 |
| P4 | h10 | depends | 0.1862 | 0.1746 | -0.0116 | 0.0117 | 0.7520 | 0.0000 | 0.2480 | 1.502 | 0.0295 | 0.567 | 0.001 | 15.1 | 2.625 | 0.7460 | 108.4 | 0.188 | 0.8785 |
| P4 | h10 | carried_margin | 1.9952 | 1.8750 | -0.1202 | 0.1187 | 0.7535 | 0.0000 | 0.2465 | 1.507 | 0.3026 | 0.526 | 0.001 | 15.1 | 2.652 | 0.7440 | n/a | 0.188 | 0.8795 |
| P4 | h10 | own_margin | 10.7131 | 10.7395 | 0.0264 | 0.0965 | 0.9570 | 0.0310 | 0.0120 | 1.497 | 0.2188 | 0.488 | 0.295 | 10.2 | 0.960 | 0.8755 | n/a | 0.188 | 0.9620 |
| P4 | h10 | kappa | 0.9155 | 0.9234 | 0.0079 | 0.0077 | 0.7590 | 0.2410 | 0.0000 | 1.333 | 0.0196 | 0.538 | 0.000 | 15.2 | 2.434 | 0.7450 | 11.8 | 0.188 | 0.8725 |
| P4 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4031 | 0.0152 | 0.0438 | 0.8600 | 0.1355 | 0.0045 | 0.818 | 0.0869 | 0.040 | 0.608 | 8.0 | 1.573 | 0.5880 | n/a | 0.188 | 0.8840 |
| P4 | h10 | carried_added | 2.1794 | 2.0317 | -0.1477 | 0.1450 | 0.7520 | 0.0000 | 0.2480 | 1.500 | 0.3683 | 0.529 | 0.000 | 15.2 | 2.779 | 0.7455 | n/a | 0.188 | 0.8790 |
| P4 | h10 | pooled_retention | 0.2000 | 0.1864 | -0.0136 | 0.0132 | 0.7505 | 0.0000 | 0.2495 | 1.514 | 0.0335 | 0.552 | 0.000 | 15.1 | 2.876 | 0.7475 | 122.4 | 0.188 | 0.8760 |
| P5 | n20 | large | -0.2409 | -0.2390 | 0.0019 | 0.0546 | 0.9725 | 0.0185 | 0.0090 | 1.063 | 0.1129 | 0.485 | 0.083 | 12.4 | 0.886 | 0.8665 | n/a | n/a | n/a |
| P5 | n20 | carries | 0.6000 | 0.6032 | 0.0032 | 0.0693 | 0.9000 | 0.0030 | 0.0970 | 1.051 | 0.1469 | 0.600 | 0.035 | 13.6 | 1.559 | 0.8595 | 8.7 | n/a | n/a |
| P5 | n20 | depends | 0.4238 | 0.4275 | 0.0037 | 0.1003 | 0.8995 | 0.0025 | 0.0980 | 1.050 | 0.2097 | 0.532 | 0.014 | 14.0 | 1.323 | 0.8515 | 9.2 | n/a | n/a |
| P5 | n20 | carried_margin | 0.1772 | 0.1780 | 0.0008 | 0.0471 | 0.9015 | 0.0045 | 0.0940 | 1.005 | 0.0937 | 0.107 | 0.190 | 11.1 | 1.368 | 0.7995 | n/a | n/a | n/a |
| P5 | n20 | own_margin | 0.4181 | 0.4171 | -0.0010 | 0.0545 | 0.9240 | 0.0060 | 0.0700 | 0.971 | 0.1326 | 0.106 | 0.671 | 5.9 | 1.264 | 0.6205 | n/a | n/a | n/a |
| P5 | n20 | kappa | 0.4903 | 0.4893 | -0.0010 | 0.0880 | 0.9195 | 0.0545 | 0.0260 | 0.914 | 0.1782 | 0.109 | 0.019 | 14.8 | 1.150 | 0.8715 | 6.6 | n/a | n/a |
| P5 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4171 | 0.0010 | 0.0545 | 0.9240 | 0.0700 | 0.0060 | 0.971 | 0.1326 | 0.106 | 0.671 | 5.9 | 1.264 | 0.6205 | n/a | n/a | n/a |
| P5 | n20 | carried_added | 0.3614 | 0.3624 | 0.0010 | 0.0601 | 0.9150 | 0.0005 | 0.0845 | 0.975 | 0.1168 | 0.106 | 0.034 | 14.2 | 1.358 | 0.8570 | n/a | n/a | n/a |
| P5 | n20 | pooled_retention | 0.6000 | 0.6001 | 0.0001 | 0.0610 | 0.8795 | 0.0030 | 0.1175 | 0.986 | 0.1277 | 0.783 | 0.000 | 15.0 | 2.201 | 0.8630 | 8.5 | n/a | n/a |
| P5 | n40 | large | 0.5907 | 0.5913 | 0.0007 | 0.1545 | 0.9305 | 0.0030 | 0.0665 | 1.010 | 0.3194 | 0.426 | 0.026 | 13.7 | 1.141 | 0.8870 | n/a | n/a | n/a |
| P5 | n40 | carries | 0.6000 | 0.6026 | 0.0026 | 0.0825 | 0.9545 | 0.0115 | 0.0340 | 1.076 | 0.1788 | 0.584 | 0.010 | 14.1 | 0.980 | 0.9235 | 8.2 | n/a | n/a |
| P5 | n40 | depends | 0.5592 | 0.5624 | 0.0033 | 0.0878 | 0.9480 | 0.0080 | 0.0440 | 1.080 | 0.1900 | 0.588 | 0.010 | 14.1 | 1.004 | 0.9230 | 8.1 | n/a | n/a |
| P5 | n40 | carried_margin | 1.0088 | 1.0084 | -0.0004 | 0.1776 | 0.9295 | 0.0035 | 0.0670 | 0.974 | 0.3579 | 0.166 | 0.097 | 12.6 | 1.142 | 0.8510 | n/a | n/a | n/a |
| P5 | n40 | own_margin | 1.8041 | 1.8029 | -0.0012 | 0.2410 | 0.9320 | 0.0095 | 0.0585 | 0.999 | 0.5005 | 0.163 | 0.283 | 10.1 | 1.078 | 0.8270 | n/a | n/a | n/a |
| P5 | n40 | kappa | 0.8456 | 0.8446 | -0.0010 | 0.0281 | 0.9270 | 0.0620 | 0.0110 | 0.921 | 0.0564 | 0.168 | 0.036 | 14.3 | 1.119 | 0.8755 | 6.3 | n/a | n/a |
| P5 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4171 | 0.0010 | 0.0546 | 0.9235 | 0.0700 | 0.0065 | 0.970 | 0.1329 | 0.105 | 0.672 | 5.9 | 1.261 | 0.6180 | n/a | n/a | n/a |
| P5 | n40 | carried_added | 1.1929 | 1.1927 | -0.0002 | 0.1995 | 0.9265 | 0.0035 | 0.0700 | 0.973 | 0.4010 | 0.165 | 0.057 | 13.7 | 1.135 | 0.8605 | n/a | n/a | n/a |
| P5 | n40 | pooled_retention | 0.6000 | 0.6003 | 0.0003 | 0.0609 | 0.8770 | 0.0035 | 0.1195 | 0.989 | 0.1280 | 0.737 | 0.000 | 15.0 | 2.204 | 0.8630 | 8.2 | n/a | n/a |
| P5 | n80 | large | 5.3205 | 5.3165 | -0.0040 | 0.9553 | 0.9370 | 0.0095 | 0.0535 | 0.980 | 2.0841 | 0.154 | 0.325 | 9.2 | 1.084 | 0.8090 | n/a | n/a | n/a |
| P5 | n80 | carries | 0.6000 | 0.6038 | 0.0038 | 0.0963 | 0.9490 | 0.0030 | 0.0480 | 1.168 | 0.2150 | 0.601 | 0.043 | 13.4 | 1.003 | 0.9175 | 7.8 | n/a | n/a |
| P5 | n80 | depends | 0.5924 | 0.5965 | 0.0041 | 0.0968 | 0.9500 | 0.0025 | 0.0475 | 1.174 | 0.2158 | 0.605 | 0.044 | 13.4 | 1.000 | 0.9180 | 7.7 | n/a | n/a |
| P5 | n80 | carried_margin | 5.7386 | 5.7336 | -0.0050 | 0.9937 | 0.9360 | 0.0090 | 0.0550 | 0.975 | 2.1740 | 0.133 | 0.367 | 8.9 | 1.084 | 0.8035 | n/a | n/a | n/a |
| P5 | n80 | own_margin | 9.6872 | 9.6879 | 0.0007 | 1.3505 | 0.9325 | 0.0240 | 0.0435 | 1.022 | 3.6393 | 0.131 | 0.654 | 6.2 | 1.130 | 0.6890 | n/a | n/a | n/a |
| P5 | n80 | kappa | 0.9689 | 0.9686 | -0.0003 | 0.0060 | 0.9270 | 0.0615 | 0.0115 | 0.899 | 0.0121 | 0.135 | 0.253 | 10.2 | 1.143 | 0.8140 | 6.3 | n/a | n/a |
| P5 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4171 | 0.0010 | 0.0545 | 0.9230 | 0.0710 | 0.0060 | 0.971 | 0.1328 | 0.105 | 0.670 | 5.9 | 1.253 | 0.6180 | n/a | n/a | n/a |
| P5 | n80 | carried_added | 5.9228 | 5.9179 | -0.0049 | 1.0165 | 0.9345 | 0.0080 | 0.0575 | 0.976 | 2.2115 | 0.133 | 0.332 | 9.3 | 1.072 | 0.8070 | n/a | n/a | n/a |
| P5 | n80 | pooled_retention | 0.6000 | 0.6002 | 0.0002 | 0.0610 | 0.8775 | 0.0030 | 0.1195 | 0.983 | 0.1277 | 0.814 | 0.000 | 15.0 | 2.220 | 0.8610 | 7.9 | n/a | n/a |
| P5 | n160 | large | 12.4023 | 12.3895 | -0.0128 | 1.4591 | 0.9335 | 0.0025 | 0.0640 | 1.067 | 3.1654 | 0.525 | 0.011 | 14.4 | 1.097 | 0.8840 | n/a | n/a | n/a |
| P5 | n160 | carries | 0.6000 | 0.6033 | 0.0033 | 0.0949 | 0.9110 | 0.0015 | 0.0875 | 1.112 | 0.2008 | 0.601 | 0.008 | 14.6 | 1.382 | 0.8880 | 16.3 | n/a | n/a |
| P5 | n160 | depends | 0.5966 | 0.6000 | 0.0035 | 0.0951 | 0.9120 | 0.0015 | 0.0865 | 1.115 | 0.2006 | 0.602 | 0.008 | 14.5 | 1.378 | 0.8885 | 15.9 | n/a | n/a |
| P5 | n160 | carried_margin | 12.8204 | 12.8066 | -0.0138 | 1.4792 | 0.9340 | 0.0025 | 0.0635 | 1.061 | 3.2068 | 0.508 | 0.013 | 14.4 | 1.102 | 0.8820 | n/a | n/a | n/a |
| P5 | n160 | own_margin | 21.4901 | 21.4977 | 0.0076 | 1.2953 | 0.9540 | 0.0375 | 0.0085 | 1.204 | 2.9633 | 0.515 | 0.130 | 11.9 | 0.976 | 0.8985 | n/a | n/a | n/a |
| P5 | n160 | kappa | 0.9858 | 0.9859 | 0.0001 | 0.0019 | 0.9055 | 0.0870 | 0.0075 | 0.939 | 0.0040 | 0.507 | 0.004 | 14.9 | 1.462 | 0.8810 | 8.5 | n/a | n/a |
| P5 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4171 | 0.0010 | 0.0546 | 0.9225 | 0.0710 | 0.0065 | 0.970 | 0.1330 | 0.105 | 0.671 | 5.9 | 1.228 | 0.6190 | n/a | n/a | n/a |
| P5 | n160 | carried_added | 13.0046 | 12.9909 | -0.0136 | 1.5140 | 0.9290 | 0.0025 | 0.0685 | 1.058 | 3.2701 | 0.509 | 0.013 | 14.5 | 1.130 | 0.8800 | n/a | n/a | n/a |
| P5 | n160 | pooled_retention | 0.6000 | 0.6003 | 0.0003 | 0.0609 | 0.8790 | 0.0030 | 0.1180 | 0.983 | 0.1274 | 0.570 | 0.000 | 15.1 | 2.240 | 0.8620 | 16.0 | n/a | n/a |
| P5 | n320 | large | 14.5066 | 14.5006 | -0.0060 | 1.6862 | 0.9225 | 0.0050 | 0.0725 | 1.042 | 3.6096 | 0.562 | 0.004 | 14.7 | 1.211 | 0.8755 | n/a | n/a | n/a |
| P5 | n320 | carries | 0.6000 | 0.6036 | 0.0036 | 0.0962 | 0.9060 | 0.0025 | 0.0915 | 1.061 | 0.1985 | 0.591 | 0.006 | 14.7 | 1.450 | 0.8775 | 17.6 | n/a | n/a |
| P5 | n320 | depends | 0.5971 | 0.6008 | 0.0037 | 0.0963 | 0.9065 | 0.0020 | 0.0915 | 1.064 | 0.1985 | 0.591 | 0.006 | 14.7 | 1.441 | 0.8775 | 17.1 | n/a | n/a |
| P5 | n320 | carried_margin | 14.9247 | 14.9177 | -0.0071 | 1.7009 | 0.9210 | 0.0055 | 0.0735 | 1.040 | 3.6536 | 0.556 | 0.004 | 14.8 | 1.225 | 0.8745 | n/a | n/a | n/a |
| P5 | n320 | own_margin | 24.9973 | 25.0141 | 0.0167 | 1.3764 | 0.9525 | 0.0380 | 0.0095 | 1.215 | 3.1711 | 0.567 | 0.086 | 12.6 | 0.970 | 0.9075 | n/a | n/a | n/a |
| P5 | n320 | kappa | 0.9878 | 0.9879 | 0.0001 | 0.0016 | 0.9030 | 0.0900 | 0.0070 | 0.963 | 0.0034 | 0.557 | 0.002 | 15.0 | 1.447 | 0.8825 | 8.7 | n/a | n/a |
| P5 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4171 | 0.0010 | 0.0546 | 0.9245 | 0.0695 | 0.0060 | 0.970 | 0.1332 | 0.109 | 0.672 | 5.9 | 1.228 | 0.6185 | n/a | n/a | n/a |
| P5 | n320 | carried_added | 15.1089 | 15.1020 | -0.0069 | 1.7370 | 0.9195 | 0.0050 | 0.0755 | 1.037 | 3.7203 | 0.556 | 0.004 | 14.8 | 1.245 | 0.8720 | n/a | n/a | n/a |
| P5 | n320 | pooled_retention | 0.6000 | 0.6002 | 0.0002 | 0.0610 | 0.8765 | 0.0030 | 0.1205 | 0.980 | 0.1276 | 0.538 | 0.000 | 15.1 | 2.249 | 0.8635 | 17.3 | n/a | n/a |
| P5 | h2 | large | 0.5457 | 0.5471 | 0.0014 | 0.0794 | 0.9320 | 0.0060 | 0.0620 | 0.965 | 0.1642 | 0.153 | 0.188 | 11.6 | 1.092 | 0.8100 | n/a | 1.000 | 0.9320 |
| P5 | h2 | carries | 0.6000 | 0.5999 | -0.0001 | 0.0577 | 0.8790 | 0.0035 | 0.1175 | 0.969 | 0.1202 | 0.601 | 0.000 | 15.1 | 2.109 | 0.8660 | 115.6 | 1.000 | 0.8790 |
| P5 | h2 | depends | 0.5574 | 0.5585 | 0.0011 | 0.0545 | 0.8795 | 0.0020 | 0.1185 | 0.993 | 0.1123 | 0.606 | 0.000 | 15.1 | 2.074 | 0.8655 | 54.1 | 1.000 | 0.8795 |
| P5 | h2 | carried_margin | 0.9640 | 0.9642 | 0.0001 | 0.0766 | 0.8790 | 0.0035 | 0.1175 | 0.981 | 0.1596 | 0.523 | 0.000 | 15.2 | 2.008 | 0.8645 | n/a | 1.000 | 0.8790 |
| P5 | h2 | own_margin | 1.7295 | 1.7292 | -0.0003 | 0.0330 | 0.9100 | 0.0835 | 0.0065 | 0.978 | 0.0678 | 0.453 | 0.003 | 15.1 | 1.267 | 0.8720 | n/a | 1.000 | 0.9100 |
| P5 | h2 | kappa | 0.8396 | 0.8414 | 0.0018 | 0.0192 | 0.8670 | 0.1145 | 0.0185 | 0.905 | 0.0399 | 0.543 | 0.000 | 15.1 | 1.942 | 0.8610 | 10.1 | 1.000 | 0.8670 |
| P5 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4171 | 0.0013 | 0.0546 | 0.9245 | 0.0695 | 0.0060 | 0.970 | 0.1328 | 0.105 | 0.669 | 5.9 | 1.259 | 0.6180 | n/a | 1.000 | 0.9245 |
| P5 | h2 | carried_added | 1.1482 | 1.1485 | 0.0003 | 0.1173 | 0.8765 | 0.0035 | 0.1200 | 0.972 | 0.2442 | 0.525 | 0.000 | 15.1 | 2.215 | 0.8625 | n/a | 1.000 | 0.8765 |
| P5 | h2 | pooled_retention | 0.6000 | 0.6002 | 0.0002 | 0.0609 | 0.8770 | 0.0030 | 0.1200 | 0.976 | 0.1272 | 0.582 | 0.000 | 15.0 | 2.253 | 0.8615 | 115.9 | 1.000 | 0.8770 |
| P5 | h5 | large | 2.4701 | 2.4715 | 0.0014 | 0.2592 | 0.8765 | 0.0035 | 0.1200 | 0.994 | 0.5383 | 0.349 | 0.000 | 15.5 | 1.875 | 0.8585 | n/a | 0.997 | 0.8755 |
| P5 | h5 | carries | 0.6000 | 0.6002 | 0.0002 | 0.0624 | 0.8790 | 0.0020 | 0.1190 | 0.992 | 0.1310 | 0.572 | 0.000 | 15.1 | 2.194 | 0.8625 | 148.2 | 0.997 | 0.8780 |
| P5 | h5 | depends | 0.5851 | 0.5858 | 0.0007 | 0.0616 | 0.8790 | 0.0020 | 0.1190 | 1.001 | 0.1289 | 0.574 | 0.000 | 15.2 | 2.188 | 0.8625 | 78.1 | 0.997 | 0.8780 |
| P5 | h5 | carried_margin | 2.8884 | 2.8885 | 0.0001 | 0.2703 | 0.8780 | 0.0025 | 0.1195 | 0.996 | 0.5698 | 0.537 | 0.000 | 15.2 | 2.165 | 0.8645 | n/a | 0.997 | 0.8770 |
| P5 | h5 | own_margin | 4.9368 | 4.9365 | -0.0003 | 0.0632 | 0.9350 | 0.0550 | 0.0100 | 1.058 | 0.1386 | 0.522 | 0.059 | 13.2 | 1.081 | 0.8670 | n/a | 0.997 | 0.9345 |
| P5 | h5 | kappa | 0.9401 | 0.9407 | 0.0007 | 0.0072 | 0.8675 | 0.1130 | 0.0195 | 0.905 | 0.0149 | 0.532 | 0.000 | 15.1 | 1.954 | 0.8645 | 10.0 | 0.997 | 0.8665 |
| P5 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4171 | 0.0013 | 0.0547 | 0.9210 | 0.0710 | 0.0080 | 1.009 | 0.1358 | 0.145 | 0.646 | 5.9 | 1.318 | 0.6215 | n/a | 0.997 | 0.9205 |
| P5 | h5 | carried_added | 3.0726 | 3.0729 | 0.0003 | 0.3111 | 0.8780 | 0.0025 | 0.1195 | 0.991 | 0.6553 | 0.538 | 0.000 | 15.1 | 2.205 | 0.8640 | n/a | 0.997 | 0.8770 |
| P5 | h5 | pooled_retention | 0.6000 | 0.6001 | 0.0001 | 0.0606 | 0.8790 | 0.0025 | 0.1185 | 0.990 | 0.1278 | 0.577 | 0.000 | 15.1 | 2.284 | 0.8645 | 148.3 | 0.997 | 0.8780 |
| P5 | h10 | large | 5.9357 | 5.5321 | -0.4036 | 0.4011 | 0.7485 | 0.0000 | 0.2515 | 1.504 | 1.0227 | 0.575 | 0.001 | 15.1 | 2.557 | 0.7425 | n/a | 0.192 | 0.8790 |
| P5 | h10 | carries | 0.6000 | 0.5590 | -0.0410 | 0.0403 | 0.7515 | 0.0000 | 0.2485 | 1.514 | 0.1033 | 0.585 | 0.000 | 15.1 | 2.625 | 0.7445 | 123.3 | 0.192 | 0.8785 |
| P5 | h10 | depends | 0.5931 | 0.5527 | -0.0404 | 0.0398 | 0.7510 | 0.0000 | 0.2490 | 1.521 | 0.1021 | 0.585 | 0.001 | 15.1 | 2.622 | 0.7445 | 111.0 | 0.192 | 0.8790 |
| P5 | h10 | carried_margin | 6.3541 | 5.9333 | -0.4207 | 0.4077 | 0.7495 | 0.0000 | 0.2505 | 1.517 | 1.0523 | 0.525 | 0.001 | 15.1 | 2.718 | 0.7465 | n/a | 0.192 | 0.8790 |
| P5 | h10 | own_margin | 10.7131 | 10.7381 | 0.0250 | 0.0962 | 0.9595 | 0.0305 | 0.0100 | 1.432 | 0.2150 | 0.507 | 0.278 | 10.4 | 0.962 | 0.8765 | n/a | 0.192 | 0.9565 |
| P5 | h10 | kappa | 0.9718 | 0.9745 | 0.0027 | 0.0026 | 0.7555 | 0.2445 | 0.0000 | 1.314 | 0.0066 | 0.533 | 0.000 | 15.2 | 2.466 | 0.7430 | 11.6 | 0.192 | 0.8675 |
| P5 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4012 | 0.0171 | 0.0431 | 0.8670 | 0.1305 | 0.0025 | 0.818 | 0.0853 | 0.033 | 0.615 | 8.1 | 1.499 | 0.5725 | n/a | 0.192 | 0.8835 |
| P5 | h10 | carried_added | 6.5383 | 6.0898 | -0.4485 | 0.4342 | 0.7495 | 0.0000 | 0.2505 | 1.514 | 1.1183 | 0.526 | 0.001 | 15.1 | 2.747 | 0.7460 | n/a | 0.192 | 0.8790 |
| P5 | h10 | pooled_retention | 0.6000 | 0.5589 | -0.0411 | 0.0396 | 0.7460 | 0.0000 | 0.2540 | 1.513 | 0.1018 | 0.570 | 0.000 | 15.1 | 2.844 | 0.7435 | 122.5 | 0.192 | 0.8785 |
| P6 | n20 | large | -0.0602 | -0.0583 | 0.0020 | 0.0621 | 0.9285 | 0.0025 | 0.0690 | 1.155 | 0.1343 | 0.593 | 0.034 | 13.6 | 1.116 | 0.8745 | n/a | n/a | n/a |
| P6 | n20 | carries | 0.9000 | 0.9036 | 0.0036 | 0.1000 | 0.9025 | 0.0025 | 0.0950 | 1.119 | 0.2189 | 0.619 | 0.021 | 13.9 | 1.473 | 0.8715 | 8.7 | n/a | n/a |
| P6 | n20 | depends | 0.8559 | 0.8625 | 0.0065 | 0.1434 | 0.8925 | 0.0020 | 0.1055 | 1.129 | 0.3110 | 0.630 | 0.017 | 13.9 | 1.597 | 0.8690 | 9.1 | n/a | n/a |
| P6 | n20 | carried_margin | 0.3579 | 0.3581 | 0.0003 | 0.0705 | 0.9050 | 0.0020 | 0.0930 | 1.029 | 0.1396 | 0.129 | 0.200 | 11.1 | 1.343 | 0.8065 | n/a | n/a | n/a |
| P6 | n20 | own_margin | 0.4181 | 0.4164 | -0.0017 | 0.0529 | 0.9275 | 0.0095 | 0.0630 | 1.019 | 0.1342 | 0.109 | 0.688 | 5.8 | 1.146 | 0.6260 | n/a | n/a | n/a |
| P6 | n20 | kappa | 0.6602 | 0.6598 | -0.0004 | 0.0573 | 0.9230 | 0.0565 | 0.0205 | 0.963 | 0.1194 | 0.130 | 0.020 | 14.9 | 1.149 | 0.8730 | 6.6 | n/a | n/a |
| P6 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4164 | 0.0017 | 0.0529 | 0.9275 | 0.0630 | 0.0095 | 1.019 | 0.1342 | 0.109 | 0.688 | 5.8 | 1.146 | 0.6260 | n/a | n/a | n/a |
| P6 | n20 | carried_added | 0.5421 | 0.5418 | -0.0002 | 0.0886 | 0.9090 | 0.0030 | 0.0880 | 1.000 | 0.1755 | 0.130 | 0.045 | 14.3 | 1.248 | 0.8610 | n/a | n/a | n/a |
| P6 | n20 | pooled_retention | 0.9000 | 0.8991 | -0.0009 | 0.0894 | 0.8775 | 0.0015 | 0.1210 | 1.031 | 0.1896 | 0.768 | 0.000 | 15.0 | 2.265 | 0.8705 | 8.6 | n/a | n/a |
| P6 | n40 | large | 1.1871 | 1.1853 | -0.0019 | 0.2487 | 0.9310 | 0.0065 | 0.0625 | 1.005 | 0.5112 | 0.303 | 0.035 | 13.7 | 1.099 | 0.8880 | n/a | n/a | n/a |
| P6 | n40 | carries | 0.9000 | 0.9061 | 0.0061 | 0.1232 | 0.9590 | 0.0120 | 0.0290 | 1.087 | 0.2715 | 0.597 | 0.009 | 14.2 | 0.948 | 0.9265 | 8.2 | n/a | n/a |
| P6 | n40 | depends | 0.8898 | 0.8976 | 0.0078 | 0.1352 | 0.9575 | 0.0115 | 0.0310 | 1.089 | 0.2977 | 0.600 | 0.009 | 14.2 | 0.950 | 0.9270 | 8.1 | n/a | n/a |
| P6 | n40 | carried_margin | 1.6052 | 1.6017 | -0.0036 | 0.2754 | 0.9310 | 0.0050 | 0.0640 | 0.988 | 0.5571 | 0.157 | 0.086 | 13.0 | 1.129 | 0.8645 | n/a | n/a | n/a |
| P6 | n40 | own_margin | 1.8041 | 1.7940 | -0.0100 | 0.2363 | 0.9345 | 0.0110 | 0.0545 | 1.026 | 0.4943 | 0.167 | 0.271 | 10.1 | 1.091 | 0.8315 | n/a | n/a | n/a |
| P6 | n40 | kappa | 0.8971 | 0.8966 | -0.0005 | 0.0180 | 0.9275 | 0.0630 | 0.0095 | 1.007 | 0.0377 | 0.157 | 0.038 | 14.3 | 1.148 | 0.8865 | 6.3 | n/a | n/a |
| P6 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4164 | 0.0017 | 0.0529 | 0.9270 | 0.0635 | 0.0095 | 1.019 | 0.1343 | 0.105 | 0.689 | 5.8 | 1.139 | 0.6295 | n/a | n/a | n/a |
| P6 | n40 | carried_added | 1.7894 | 1.7854 | -0.0040 | 0.2989 | 0.9280 | 0.0040 | 0.0680 | 0.982 | 0.6047 | 0.157 | 0.059 | 13.8 | 1.130 | 0.8715 | n/a | n/a | n/a |
| P6 | n40 | pooled_retention | 0.9000 | 0.8990 | -0.0010 | 0.0895 | 0.8785 | 0.0010 | 0.1205 | 1.029 | 0.1907 | 0.756 | 0.000 | 15.0 | 2.287 | 0.8710 | 8.2 | n/a | n/a |
| P6 | n80 | large | 8.2819 | 8.2608 | -0.0212 | 1.4415 | 0.9355 | 0.0055 | 0.0590 | 1.015 | 3.2085 | 0.138 | 0.359 | 9.1 | 1.101 | 0.8015 | n/a | n/a | n/a |
| P6 | n80 | carries | 0.9000 | 0.9079 | 0.0079 | 0.1432 | 0.9535 | 0.0015 | 0.0450 | 1.180 | 0.3170 | 0.622 | 0.041 | 13.4 | 0.974 | 0.9200 | 7.9 | n/a | n/a |
| P6 | n80 | depends | 0.8981 | 0.9067 | 0.0086 | 0.1460 | 0.9535 | 0.0015 | 0.0450 | 1.184 | 0.3228 | 0.622 | 0.041 | 13.4 | 0.974 | 0.9195 | 7.7 | n/a | n/a |
| P6 | n80 | carried_margin | 8.7000 | 8.6772 | -0.0229 | 1.4788 | 0.9360 | 0.0050 | 0.0590 | 1.013 | 3.2937 | 0.122 | 0.379 | 8.9 | 1.092 | 0.7900 | n/a | n/a | n/a |
| P6 | n80 | own_margin | 9.6872 | 9.6425 | -0.0447 | 1.3100 | 0.9370 | 0.0170 | 0.0460 | 1.073 | 3.5963 | 0.126 | 0.648 | 6.2 | 1.135 | 0.6965 | n/a | n/a | n/a |
| P6 | n80 | kappa | 0.9793 | 0.9791 | -0.0002 | 0.0038 | 0.9280 | 0.0605 | 0.0115 | 0.967 | 0.0080 | 0.124 | 0.279 | 10.1 | 1.127 | 0.8385 | 6.2 | n/a | n/a |
| P6 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4164 | 0.0017 | 0.0529 | 0.9270 | 0.0640 | 0.0090 | 1.020 | 0.1342 | 0.108 | 0.685 | 5.8 | 1.133 | 0.6290 | n/a | n/a | n/a |
| P6 | n80 | carried_added | 8.8842 | 8.8609 | -0.0233 | 1.5023 | 0.9360 | 0.0050 | 0.0590 | 1.013 | 3.3258 | 0.121 | 0.358 | 9.2 | 1.090 | 0.7970 | n/a | n/a | n/a |
| P6 | n80 | pooled_retention | 0.9000 | 0.8987 | -0.0013 | 0.0893 | 0.8775 | 0.0010 | 0.1215 | 1.029 | 0.1900 | 0.811 | 0.000 | 15.0 | 2.282 | 0.8725 | 7.9 | n/a | n/a |
| P6 | n160 | large | 18.9046 | 18.8793 | -0.0252 | 2.2156 | 0.9245 | 0.0040 | 0.0715 | 1.066 | 4.7850 | 0.525 | 0.009 | 14.4 | 1.178 | 0.8800 | n/a | n/a | n/a |
| P6 | n160 | carries | 0.9000 | 0.9051 | 0.0051 | 0.1409 | 0.9080 | 0.0005 | 0.0915 | 1.141 | 0.3019 | 0.576 | 0.011 | 14.5 | 1.380 | 0.8795 | 16.1 | n/a | n/a |
| P6 | n160 | depends | 0.8991 | 0.9046 | 0.0055 | 0.1421 | 0.9080 | 0.0005 | 0.0915 | 1.144 | 0.3041 | 0.576 | 0.011 | 14.5 | 1.379 | 0.8795 | 15.7 | n/a | n/a |
| P6 | n160 | carried_margin | 19.3227 | 19.2957 | -0.0269 | 2.2358 | 0.9255 | 0.0040 | 0.0705 | 1.063 | 4.8193 | 0.510 | 0.010 | 14.4 | 1.174 | 0.8785 | n/a | n/a | n/a |
| P6 | n160 | own_margin | 21.4901 | 21.4840 | -0.0061 | 1.2953 | 0.9505 | 0.0385 | 0.0110 | 1.209 | 2.9915 | 0.494 | 0.133 | 11.8 | 0.989 | 0.8990 | n/a | n/a | n/a |
| P6 | n160 | kappa | 0.9906 | 0.9906 | 0.0001 | 0.0013 | 0.9015 | 0.0960 | 0.0025 | 0.997 | 0.0027 | 0.504 | 0.003 | 14.8 | 1.458 | 0.8820 | 8.5 | n/a | n/a |
| P6 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4164 | 0.0017 | 0.0529 | 0.9270 | 0.0635 | 0.0095 | 1.019 | 0.1343 | 0.106 | 0.684 | 5.8 | 1.130 | 0.6255 | n/a | n/a | n/a |
| P6 | n160 | carried_added | 19.5068 | 19.4794 | -0.0274 | 2.2700 | 0.9240 | 0.0040 | 0.0720 | 1.061 | 4.8914 | 0.511 | 0.009 | 14.5 | 1.191 | 0.8785 | n/a | n/a | n/a |
| P6 | n160 | pooled_retention | 0.9000 | 0.8990 | -0.0010 | 0.0894 | 0.8780 | 0.0015 | 0.1205 | 1.023 | 0.1895 | 0.571 | 0.000 | 15.1 | 2.297 | 0.8710 | 16.2 | n/a | n/a |
| P6 | n320 | large | 22.0611 | 22.0117 | -0.0494 | 2.5313 | 0.9175 | 0.0020 | 0.0805 | 1.059 | 5.4769 | 0.570 | 0.004 | 14.7 | 1.224 | 0.8765 | n/a | n/a | n/a |
| P6 | n320 | carries | 0.9000 | 0.9033 | 0.0033 | 0.1402 | 0.9010 | 0.0005 | 0.0985 | 1.120 | 0.2976 | 0.569 | 0.006 | 14.6 | 1.417 | 0.8770 | 17.7 | n/a | n/a |
| P6 | n320 | depends | 0.8993 | 0.9029 | 0.0036 | 0.1412 | 0.9010 | 0.0005 | 0.0985 | 1.123 | 0.2995 | 0.569 | 0.006 | 14.6 | 1.417 | 0.8770 | 17.2 | n/a | n/a |
| P6 | n320 | carried_margin | 22.4792 | 22.4281 | -0.0511 | 2.5467 | 0.9165 | 0.0020 | 0.0815 | 1.057 | 5.5187 | 0.561 | 0.004 | 14.7 | 1.229 | 0.8755 | n/a | n/a | n/a |
| P6 | n320 | own_margin | 24.9973 | 25.0149 | 0.0176 | 1.3604 | 0.9535 | 0.0410 | 0.0055 | 1.237 | 3.1699 | 0.568 | 0.088 | 12.5 | 0.975 | 0.9095 | n/a | n/a | n/a |
| P6 | n320 | kappa | 0.9919 | 0.9919 | 0.0001 | 0.0011 | 0.9030 | 0.0920 | 0.0050 | 0.996 | 0.0023 | 0.563 | 0.001 | 15.1 | 1.562 | 0.8885 | 8.6 | n/a | n/a |
| P6 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4164 | 0.0017 | 0.0529 | 0.9280 | 0.0630 | 0.0090 | 1.019 | 0.1342 | 0.106 | 0.683 | 5.8 | 1.129 | 0.6290 | n/a | n/a | n/a |
| P6 | n320 | carried_added | 22.6634 | 22.6118 | -0.0516 | 2.5819 | 0.9155 | 0.0020 | 0.0825 | 1.056 | 5.5930 | 0.561 | 0.004 | 14.8 | 1.240 | 0.8750 | n/a | n/a | n/a |
| P6 | n320 | pooled_retention | 0.9000 | 0.8989 | -0.0011 | 0.0895 | 0.8765 | 0.0015 | 0.1220 | 1.020 | 0.1901 | 0.526 | 0.000 | 15.1 | 2.324 | 0.8690 | 17.4 | n/a | n/a |
| P6 | h2 | large | 1.1198 | 1.1197 | -0.0001 | 0.1249 | 0.8855 | 0.0010 | 0.1135 | 1.039 | 0.2632 | 0.183 | 0.021 | 15.1 | 1.567 | 0.8500 | n/a | 1.000 | 0.8855 |
| P6 | h2 | carries | 0.9000 | 0.8985 | -0.0015 | 0.0846 | 0.8800 | 0.0015 | 0.1185 | 1.016 | 0.1803 | 0.586 | 0.000 | 15.1 | 2.203 | 0.8715 | 114.0 | 1.000 | 0.8800 |
| P6 | h2 | depends | 0.8893 | 0.8898 | 0.0005 | 0.0921 | 0.8795 | 0.0010 | 0.1195 | 1.044 | 0.1936 | 0.589 | 0.000 | 15.1 | 2.271 | 0.8715 | 54.7 | 1.000 | 0.8795 |
| P6 | h2 | carried_margin | 1.5381 | 1.5361 | -0.0020 | 0.1319 | 0.8790 | 0.0015 | 0.1195 | 1.024 | 0.2802 | 0.534 | 0.000 | 15.1 | 2.180 | 0.8730 | n/a | 1.000 | 0.8790 |
| P6 | h2 | own_margin | 1.7295 | 1.7294 | -0.0000 | 0.0320 | 0.9160 | 0.0825 | 0.0015 | 1.049 | 0.0677 | 0.449 | 0.005 | 15.1 | 1.301 | 0.8785 | n/a | 1.000 | 0.9160 |
| P6 | h2 | kappa | 0.8931 | 0.8944 | 0.0014 | 0.0127 | 0.8710 | 0.1160 | 0.0130 | 0.926 | 0.0267 | 0.544 | 0.000 | 15.1 | 1.999 | 0.8680 | 10.0 | 1.000 | 0.8710 |
| P6 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4164 | 0.0019 | 0.0529 | 0.9260 | 0.0645 | 0.0095 | 1.019 | 0.1341 | 0.107 | 0.687 | 5.8 | 1.129 | 0.6265 | n/a | 1.000 | 0.9260 |
| P6 | h2 | carried_added | 1.7223 | 1.7198 | -0.0025 | 0.1717 | 0.8785 | 0.0015 | 0.1200 | 1.019 | 0.3656 | 0.528 | 0.000 | 15.1 | 2.312 | 0.8710 | n/a | 1.000 | 0.8785 |
| P6 | h2 | pooled_retention | 0.9000 | 0.8990 | -0.0010 | 0.0892 | 0.8775 | 0.0010 | 0.1215 | 1.025 | 0.1901 | 0.560 | 0.000 | 15.1 | 2.368 | 0.8705 | 115.8 | 1.000 | 0.8775 |
| P6 | h5 | large | 4.0064 | 4.0038 | -0.0025 | 0.4048 | 0.8730 | 0.0010 | 0.1260 | 1.029 | 0.8579 | 0.454 | 0.000 | 15.3 | 2.074 | 0.8675 | n/a | 0.996 | 0.8730 |
| P6 | h5 | carries | 0.9000 | 0.8993 | -0.0007 | 0.0920 | 0.8775 | 0.0015 | 0.1210 | 1.022 | 0.1950 | 0.582 | 0.000 | 15.1 | 2.287 | 0.8680 | 147.1 | 0.996 | 0.8775 |
| P6 | h5 | depends | 0.8963 | 0.8963 | 0.0000 | 0.0949 | 0.8780 | 0.0010 | 0.1210 | 1.032 | 0.2002 | 0.582 | 0.000 | 15.1 | 2.311 | 0.8680 | 78.0 | 0.996 | 0.8780 |
| P6 | h5 | carried_margin | 4.4247 | 4.4200 | -0.0046 | 0.4190 | 0.8790 | 0.0010 | 0.1200 | 1.023 | 0.8914 | 0.526 | 0.000 | 15.2 | 2.216 | 0.8670 | n/a | 0.996 | 0.8790 |
| P6 | h5 | own_margin | 4.9368 | 4.9370 | 0.0003 | 0.0618 | 0.9360 | 0.0595 | 0.0045 | 1.108 | 0.1400 | 0.525 | 0.075 | 13.0 | 1.108 | 0.8740 | n/a | 0.996 | 0.9360 |
| P6 | h5 | kappa | 0.9600 | 0.9605 | 0.0005 | 0.0048 | 0.8715 | 0.1150 | 0.0135 | 0.925 | 0.0100 | 0.526 | 0.000 | 15.1 | 2.022 | 0.8690 | 10.1 | 0.996 | 0.8710 |
| P6 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4162 | 0.0021 | 0.0531 | 0.9180 | 0.0710 | 0.0110 | 1.059 | 0.1391 | 0.153 | 0.661 | 5.8 | 1.227 | 0.6300 | n/a | 0.996 | 0.9180 |
| P6 | h5 | carried_added | 4.6089 | 4.6039 | -0.0050 | 0.4589 | 0.8790 | 0.0010 | 0.1200 | 1.021 | 0.9756 | 0.524 | 0.000 | 15.1 | 2.256 | 0.8690 | n/a | 0.996 | 0.8790 |
| P6 | h5 | pooled_retention | 0.9000 | 0.8992 | -0.0008 | 0.0894 | 0.8790 | 0.0010 | 0.1200 | 1.021 | 0.1899 | 0.579 | 0.000 | 15.1 | 2.347 | 0.8705 | 145.3 | 0.996 | 0.8790 |
| P6 | h10 | large | 9.2049 | 8.5592 | -0.6457 | 0.6066 | 0.7445 | 0.0000 | 0.2555 | 1.545 | 1.5489 | 0.574 | 0.000 | 15.2 | 2.678 | 0.7385 | n/a | 0.199 | 0.8805 |
| P6 | h10 | carries | 0.9000 | 0.8366 | -0.0634 | 0.0593 | 0.7425 | 0.0000 | 0.2575 | 1.553 | 0.1524 | 0.595 | 0.001 | 15.1 | 2.688 | 0.7385 | 122.0 | 0.199 | 0.8810 |
| P6 | h10 | depends | 0.8983 | 0.8344 | -0.0639 | 0.0598 | 0.7425 | 0.0000 | 0.2575 | 1.560 | 0.1537 | 0.596 | 0.001 | 15.1 | 2.700 | 0.7390 | 110.1 | 0.199 | 0.8805 |
| P6 | h10 | carried_margin | 9.6232 | 8.9601 | -0.6631 | 0.6126 | 0.7440 | 0.0000 | 0.2560 | 1.557 | 1.5793 | 0.527 | 0.000 | 15.2 | 2.707 | 0.7420 | n/a | 0.199 | 0.8805 |
| P6 | h10 | own_margin | 10.7131 | 10.7417 | 0.0286 | 0.0962 | 0.9525 | 0.0340 | 0.0135 | 1.434 | 0.2145 | 0.511 | 0.281 | 10.3 | 0.985 | 0.8730 | n/a | 0.199 | 0.9630 |
| P6 | h10 | kappa | 0.9812 | 0.9830 | 0.0018 | 0.0017 | 0.7520 | 0.2480 | 0.0000 | 1.343 | 0.0044 | 0.529 | 0.000 | 15.2 | 2.428 | 0.7375 | 11.8 | 0.199 | 0.8750 |
| P6 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4009 | 0.0174 | 0.0436 | 0.8630 | 0.1345 | 0.0025 | 0.785 | 0.0836 | 0.040 | 0.607 | 8.2 | 1.520 | 0.5600 | n/a | 0.199 | 0.8855 |
| P6 | h10 | carried_added | 9.8074 | 9.1158 | -0.6916 | 0.6385 | 0.7425 | 0.0000 | 0.2575 | 1.556 | 1.6433 | 0.525 | 0.000 | 15.2 | 2.728 | 0.7420 | n/a | 0.199 | 0.8795 |
| P6 | h10 | pooled_retention | 0.9000 | 0.8365 | -0.0635 | 0.0582 | 0.7425 | 0.0000 | 0.2575 | 1.557 | 0.1501 | 0.564 | 0.000 | 15.1 | 2.797 | 0.7410 | 122.2 | 0.199 | 0.8790 |
| P7 | n20 | large | 0.0000 | 0.0005 | 0.0005 | 0.0642 | 0.9195 | 0.0005 | 0.0800 | 1.152 | 0.1426 | 0.569 | 0.026 | 13.7 | 1.448 | 0.8685 | n/a | n/a | n/a |
| P7 | n20 | carries | 1.0000 | 1.0019 | 0.0019 | 0.1085 | 0.9080 | 0.0010 | 0.0910 | 1.124 | 0.2406 | 0.575 | 0.026 | 13.7 | 1.439 | 0.8685 | 10.0 | n/a | n/a |
| P7 | n20 | depends | 1.0000 | 1.0043 | 0.0043 | 0.1575 | 0.9030 | 0.0005 | 0.0965 | 1.140 | 0.3468 | 0.578 | 0.025 | 13.7 | 1.502 | 0.8685 | 15.2 | n/a | n/a |
| P7 | n20 | carried_margin | 0.4093 | 0.4093 | -0.0000 | 0.0624 | 0.8675 | 0.0010 | 0.1315 | 1.105 | 0.1328 | 0.548 | 0.004 | 14.7 | 2.092 | 0.8560 | n/a | n/a | n/a |
| P7 | n20 | own_margin | 0.4093 | 0.4088 | -0.0005 | 0.0282 | 0.9035 | 0.0015 | 0.0950 | 1.231 | 0.0617 | 0.551 | 0.125 | 12.0 | 1.293 | 0.8235 | n/a | n/a | n/a |
| P7 | n20 | kappa | 0.6896 | 0.6926 | 0.0030 | 0.0477 | 0.9145 | 0.0715 | 0.0140 | 0.951 | 0.1010 | 0.552 | 0.000 | 15.3 | 1.197 | 0.8870 | 7.2 | n/a | n/a |
| P7 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9035 | 0.0950 | 0.0015 | 1.231 | 0.0617 | 0.551 | 0.125 | 12.0 | 1.293 | 0.8235 | n/a | n/a | n/a |
| P7 | n20 | carried_added | 0.5935 | 0.5915 | -0.0020 | 0.0837 | 0.9090 | 0.0010 | 0.0900 | 1.056 | 0.1749 | 0.544 | 0.001 | 15.2 | 1.343 | 0.8940 | n/a | n/a | n/a |
| P7 | n20 | pooled_retention | 1.0000 | 0.9949 | -0.0051 | 0.0994 | 0.8640 | 0.0025 | 0.1335 | 1.013 | 0.2106 | 0.535 | 0.000 | 15.1 | 2.296 | 0.8525 | 9.9 | n/a | n/a |
| P7 | n40 | large | 0.0000 | 0.0001 | 0.0001 | 0.0672 | 0.9515 | 0.0060 | 0.0425 | 1.121 | 0.1486 | 0.573 | 0.013 | 13.9 | 1.051 | 0.9170 | n/a | n/a | n/a |
| P7 | n40 | carries | 0.3046 | 0.3057 | 0.0011 | 0.0417 | 0.9515 | 0.0105 | 0.0380 | 1.066 | 0.0908 | 0.580 | 0.004 | 14.3 | 0.987 | 0.9180 | 9.4 | n/a | n/a |
| P7 | n40 | depends | 0.2320 | 0.2343 | 0.0023 | 0.0414 | 0.9510 | 0.0060 | 0.0430 | 1.085 | 0.0910 | 0.577 | 0.005 | 14.4 | 0.993 | 0.9280 | 9.6 | n/a | n/a |
| P7 | n40 | carried_margin | 0.4093 | 0.4089 | -0.0004 | 0.0653 | 0.9395 | 0.0050 | 0.0555 | 1.081 | 0.1419 | 0.562 | 0.002 | 14.7 | 1.062 | 0.9170 | n/a | n/a | n/a |
| P7 | n40 | own_margin | 1.7645 | 1.7595 | -0.0049 | 0.1785 | 0.9450 | 0.0080 | 0.0470 | 1.100 | 0.3946 | 0.566 | 0.005 | 14.3 | 1.027 | 0.9210 | n/a | n/a | n/a |
| P7 | n40 | kappa | 0.6896 | 0.6920 | 0.0023 | 0.0492 | 0.9220 | 0.0710 | 0.0070 | 0.989 | 0.1051 | 0.565 | 0.000 | 15.2 | 1.138 | 0.9075 | 6.9 | n/a | n/a |
| P7 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9030 | 0.0955 | 0.0015 | 1.229 | 0.0617 | 0.550 | 0.123 | 12.0 | 1.300 | 0.8265 | n/a | n/a | n/a |
| P7 | n40 | carried_added | 0.5935 | 0.5911 | -0.0024 | 0.0862 | 0.9330 | 0.0025 | 0.0645 | 1.037 | 0.1808 | 0.562 | 0.000 | 15.1 | 1.097 | 0.9075 | n/a | n/a | n/a |
| P7 | n40 | pooled_retention | 0.3046 | 0.3030 | -0.0016 | 0.0302 | 0.8640 | 0.0015 | 0.1345 | 1.016 | 0.0641 | 0.524 | 0.000 | 15.1 | 2.421 | 0.8530 | 9.4 | n/a | n/a |
| P7 | n80 | large | 0.0000 | -0.0008 | -0.0008 | 0.0510 | 0.9700 | 0.0100 | 0.0200 | 1.315 | 0.1170 | 0.584 | 0.134 | 12.0 | 0.875 | 0.9225 | n/a | n/a | n/a |
| P7 | n80 | carries | 0.0608 | 0.0606 | -0.0002 | 0.0096 | 0.9360 | 0.0035 | 0.0605 | 1.105 | 0.0210 | 0.617 | 0.033 | 13.4 | 1.115 | 0.9040 | 12.4 | n/a | n/a |
| P7 | n80 | depends | 0.0427 | 0.0427 | -0.0000 | 0.0064 | 0.9585 | 0.0040 | 0.0375 | 1.215 | 0.0143 | 0.617 | 0.090 | 12.6 | 0.931 | 0.9225 | 12.1 | n/a | n/a |
| P7 | n80 | carried_margin | 0.4093 | 0.4080 | -0.0013 | 0.0490 | 0.9640 | 0.0050 | 0.0310 | 1.236 | 0.1122 | 0.589 | 0.106 | 12.3 | 0.935 | 0.9145 | n/a | n/a | n/a |
| P7 | n80 | own_margin | 9.5794 | 9.6255 | 0.0461 | 0.7423 | 0.9690 | 0.0155 | 0.0155 | 1.297 | 1.7263 | 0.599 | 0.134 | 12.1 | 0.914 | 0.9160 | n/a | n/a | n/a |
| P7 | n80 | kappa | 0.6896 | 0.6931 | 0.0035 | 0.0437 | 0.9115 | 0.0810 | 0.0075 | 1.037 | 0.0940 | 0.592 | 0.015 | 14.1 | 1.283 | 0.8810 | 7.8 | n/a | n/a |
| P7 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9030 | 0.0955 | 0.0015 | 1.230 | 0.0616 | 0.550 | 0.120 | 12.0 | 1.296 | 0.8225 | n/a | n/a | n/a |
| P7 | n80 | carried_added | 0.5935 | 0.5902 | -0.0033 | 0.0746 | 0.9375 | 0.0020 | 0.0605 | 1.088 | 0.1645 | 0.590 | 0.025 | 13.7 | 1.055 | 0.8915 | n/a | n/a | n/a |
| P7 | n80 | pooled_retention | 0.0608 | 0.0605 | -0.0003 | 0.0060 | 0.8645 | 0.0010 | 0.1345 | 1.016 | 0.0128 | 0.472 | 0.000 | 15.1 | 2.297 | 0.8515 | 12.6 | n/a | n/a |
| P7 | n160 | large | 0.0000 | -0.0003 | -0.0003 | 0.0423 | 0.9725 | 0.0185 | 0.0090 | 1.283 | 0.0971 | 0.584 | 0.102 | 12.3 | 0.878 | 0.9140 | n/a | n/a | n/a |
| P7 | n160 | carries | 0.0269 | 0.0268 | -0.0000 | 0.0043 | 0.8965 | 0.0000 | 0.1035 | 1.064 | 0.0089 | 0.584 | 0.010 | 14.5 | 1.496 | 0.8630 | 16.6 | n/a | n/a |
| P7 | n160 | depends | 0.0187 | 0.0187 | -0.0000 | 0.0025 | 0.9540 | 0.0010 | 0.0450 | 1.129 | 0.0054 | 0.584 | 0.034 | 13.5 | 0.972 | 0.9055 | 16.2 | n/a | n/a |
| P7 | n160 | carried_margin | 0.4093 | 0.4085 | -0.0008 | 0.0396 | 0.9710 | 0.0115 | 0.0175 | 1.169 | 0.0896 | 0.587 | 0.043 | 13.2 | 0.913 | 0.9125 | n/a | n/a | n/a |
| P7 | n160 | own_margin | 21.9134 | 22.0035 | 0.0902 | 1.3123 | 0.9500 | 0.0450 | 0.0050 | 1.152 | 2.9426 | 0.583 | 0.073 | 12.8 | 0.998 | 0.9025 | n/a | n/a | n/a |
| P7 | n160 | kappa | 0.6896 | 0.6941 | 0.0045 | 0.0408 | 0.8945 | 0.0990 | 0.0065 | 1.001 | 0.0872 | 0.583 | 0.001 | 15.0 | 1.478 | 0.8765 | 8.5 | n/a | n/a |
| P7 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9025 | 0.0955 | 0.0020 | 1.229 | 0.0615 | 0.550 | 0.124 | 12.0 | 1.286 | 0.8230 | n/a | n/a | n/a |
| P7 | n160 | carried_added | 0.5935 | 0.5907 | -0.0028 | 0.0689 | 0.9135 | 0.0030 | 0.0835 | 1.038 | 0.1470 | 0.587 | 0.005 | 14.7 | 1.210 | 0.8710 | n/a | n/a | n/a |
| P7 | n160 | pooled_retention | 0.0269 | 0.0267 | -0.0001 | 0.0027 | 0.8640 | 0.0020 | 0.1340 | 1.011 | 0.0056 | 0.526 | 0.000 | 15.1 | 2.346 | 0.8525 | 16.3 | n/a | n/a |
| P7 | n320 | large | 0.0000 | -0.0005 | -0.0005 | 0.0407 | 0.9800 | 0.0125 | 0.0075 | 1.291 | 0.0929 | 0.581 | 0.102 | 12.3 | 0.848 | 0.9220 | n/a | n/a | n/a |
| P7 | n320 | carries | 0.0233 | 0.0233 | -0.0000 | 0.0037 | 0.8950 | 0.0010 | 0.1040 | 1.061 | 0.0077 | 0.588 | 0.007 | 14.6 | 1.523 | 0.8680 | 17.7 | n/a | n/a |
| P7 | n320 | depends | 0.0162 | 0.0162 | -0.0000 | 0.0021 | 0.9500 | 0.0010 | 0.0490 | 1.122 | 0.0045 | 0.589 | 0.025 | 13.6 | 0.996 | 0.9040 | 17.2 | n/a | n/a |
| P7 | n320 | carried_margin | 0.4093 | 0.4083 | -0.0010 | 0.0381 | 0.9670 | 0.0100 | 0.0230 | 1.154 | 0.0855 | 0.589 | 0.043 | 13.3 | 0.921 | 0.9150 | n/a | n/a | n/a |
| P7 | n320 | own_margin | 25.2643 | 25.3521 | 0.0878 | 1.4119 | 0.9570 | 0.0375 | 0.0055 | 1.169 | 3.2200 | 0.582 | 0.080 | 12.8 | 0.961 | 0.8995 | n/a | n/a | n/a |
| P7 | n320 | kappa | 0.6896 | 0.6941 | 0.0045 | 0.0401 | 0.8940 | 0.0985 | 0.0075 | 1.003 | 0.0863 | 0.589 | 0.002 | 15.1 | 1.532 | 0.8700 | 8.7 | n/a | n/a |
| P7 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9010 | 0.0975 | 0.0015 | 1.228 | 0.0616 | 0.551 | 0.122 | 12.0 | 1.296 | 0.8230 | n/a | n/a | n/a |
| P7 | n320 | carried_added | 0.5935 | 0.5905 | -0.0030 | 0.0683 | 0.9015 | 0.0040 | 0.0945 | 1.024 | 0.1452 | 0.591 | 0.004 | 14.8 | 1.283 | 0.8655 | n/a | n/a | n/a |
| P7 | n320 | pooled_retention | 0.0233 | 0.0232 | -0.0001 | 0.0023 | 0.8645 | 0.0020 | 0.1335 | 1.004 | 0.0049 | 0.521 | 0.000 | 15.1 | 2.366 | 0.8525 | 17.5 | n/a | n/a |
| P7 | h2 | large | 0.0000 | -0.0004 | -0.0004 | 0.0244 | 0.9840 | 0.0060 | 0.0100 | 1.456 | 0.0568 | 0.548 | 0.144 | 11.8 | 0.791 | 0.9315 | n/a | 1.000 | 0.9840 |
| P7 | h2 | carries | 0.3108 | 0.3092 | -0.0016 | 0.0292 | 0.8625 | 0.0030 | 0.1345 | 0.997 | 0.0619 | 0.583 | 0.000 | 15.1 | 2.232 | 0.8500 | 121.8 | 1.000 | 0.8625 |
| P7 | h2 | depends | 0.2372 | 0.2368 | -0.0004 | 0.0154 | 0.8700 | 0.0020 | 0.1280 | 1.057 | 0.0324 | 0.590 | 0.000 | 15.2 | 1.870 | 0.8565 | 55.7 | 1.000 | 0.8700 |
| P7 | h2 | carried_margin | 0.4093 | 0.4084 | -0.0009 | 0.0196 | 0.8820 | 0.0020 | 0.1160 | 1.077 | 0.0420 | 0.579 | 0.000 | 15.2 | 1.559 | 0.8640 | n/a | 1.000 | 0.8820 |
| P7 | h2 | own_margin | 1.7255 | 1.7268 | 0.0013 | 0.0316 | 0.8915 | 0.1030 | 0.0055 | 1.010 | 0.0659 | 0.572 | 0.000 | 15.2 | 1.389 | 0.8590 | n/a | 1.000 | 0.8915 |
| P7 | h2 | kappa | 0.6896 | 0.6951 | 0.0054 | 0.0369 | 0.8560 | 0.1295 | 0.0145 | 0.916 | 0.0772 | 0.582 | 0.000 | 15.1 | 2.023 | 0.8535 | 10.1 | 1.000 | 0.8560 |
| P7 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4088 | 0.0005 | 0.0282 | 0.9000 | 0.0985 | 0.0015 | 1.230 | 0.0618 | 0.549 | 0.122 | 12.0 | 1.297 | 0.8245 | n/a | 1.000 | 0.9000 |
| P7 | h2 | carried_added | 0.5935 | 0.5906 | -0.0029 | 0.0592 | 0.8620 | 0.0030 | 0.1350 | 1.002 | 0.1250 | 0.587 | 0.000 | 15.1 | 2.329 | 0.8495 | n/a | 1.000 | 0.8620 |
| P7 | h2 | pooled_retention | 0.3108 | 0.3093 | -0.0015 | 0.0309 | 0.8635 | 0.0025 | 0.1340 | 1.002 | 0.0652 | 0.570 | 0.000 | 15.1 | 2.391 | 0.8515 | 121.7 | 1.000 | 0.8635 |
| P7 | h5 | large | 0.0000 | -0.0003 | -0.0003 | 0.0244 | 0.9830 | 0.0060 | 0.0110 | 1.581 | 0.0580 | 0.554 | 0.179 | 11.4 | 0.793 | 0.9255 | n/a | 0.996 | 0.9830 |
| P7 | h5 | carries | 0.1162 | 0.1156 | -0.0006 | 0.0119 | 0.8620 | 0.0025 | 0.1355 | 1.010 | 0.0250 | 0.581 | 0.000 | 15.1 | 2.347 | 0.8500 | 159.6 | 0.996 | 0.8630 |
| P7 | h5 | depends | 0.0831 | 0.0829 | -0.0002 | 0.0048 | 0.8690 | 0.0015 | 0.1295 | 1.086 | 0.0104 | 0.572 | 0.002 | 15.1 | 1.769 | 0.8550 | 80.4 | 0.996 | 0.8700 |
| P7 | h5 | carried_margin | 0.4093 | 0.4083 | -0.0010 | 0.0194 | 0.8830 | 0.0025 | 0.1145 | 1.109 | 0.0426 | 0.573 | 0.002 | 15.0 | 1.528 | 0.8585 | n/a | 0.996 | 0.8840 |
| P7 | h5 | own_margin | 4.9248 | 4.9276 | 0.0028 | 0.0601 | 0.9215 | 0.0740 | 0.0045 | 1.096 | 0.1347 | 0.593 | 0.048 | 13.6 | 1.252 | 0.8635 | n/a | 0.996 | 0.9220 |
| P7 | h5 | kappa | 0.6896 | 0.6951 | 0.0055 | 0.0370 | 0.8550 | 0.1310 | 0.0140 | 0.911 | 0.0773 | 0.576 | 0.000 | 15.1 | 2.054 | 0.8520 | 10.0 | 0.996 | 0.8560 |
| P7 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4087 | 0.0006 | 0.0283 | 0.9020 | 0.0965 | 0.0015 | 1.322 | 0.0635 | 0.550 | 0.154 | 11.6 | 1.297 | 0.8245 | n/a | 0.996 | 0.9030 |
| P7 | h5 | carried_added | 0.5935 | 0.5905 | -0.0030 | 0.0591 | 0.8620 | 0.0025 | 0.1355 | 1.007 | 0.1247 | 0.576 | 0.000 | 15.1 | 2.347 | 0.8500 | n/a | 0.996 | 0.8630 |
| P7 | h5 | pooled_retention | 0.1162 | 0.1156 | -0.0006 | 0.0115 | 0.8630 | 0.0025 | 0.1345 | 1.006 | 0.0244 | 0.569 | 0.000 | 15.1 | 2.439 | 0.8515 | 156.7 | 0.996 | 0.8640 |
| P7 | h10 | large | 0.0000 | 0.0011 | 0.0011 | 0.0213 | 0.9740 | 0.0140 | 0.0120 | 1.173 | 0.0450 | 0.565 | 0.037 | 13.6 | 0.867 | 0.9245 | n/a | 0.197 | 0.9845 |
| P7 | h10 | carries | 0.0546 | 0.0508 | -0.0038 | 0.0036 | 0.7470 | 0.0000 | 0.2530 | 1.562 | 0.0092 | 0.578 | 0.001 | 15.1 | 2.715 | 0.7415 | 146.8 | 0.197 | 0.8655 |
| P7 | h10 | depends | 0.0383 | 0.0370 | -0.0013 | 0.0013 | 0.8050 | 0.0000 | 0.1950 | 1.677 | 0.0036 | 0.585 | 0.013 | 14.5 | 1.870 | 0.7635 | 128.2 | 0.197 | 0.8980 |
| P7 | h10 | carried_margin | 0.4093 | 0.3962 | -0.0131 | 0.0131 | 0.8005 | 0.0000 | 0.1995 | 1.695 | 0.0353 | 0.586 | 0.011 | 14.6 | 1.800 | 0.7585 | n/a | 0.197 | 0.8955 |
| P7 | h10 | own_margin | 10.6772 | 10.7035 | 0.0264 | 0.0727 | 0.9600 | 0.0355 | 0.0045 | 1.764 | 0.1801 | 0.576 | 0.228 | 11.1 | 0.935 | 0.9095 | n/a | 0.197 | 0.9700 |
| P7 | h10 | kappa | 0.6896 | 0.7195 | 0.0298 | 0.0278 | 0.7565 | 0.2435 | 0.0000 | 1.385 | 0.0723 | 0.586 | 0.000 | 15.1 | 2.474 | 0.7430 | 11.8 | 0.197 | 0.8555 |
| P7 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3951 | 0.0142 | 0.0203 | 0.8170 | 0.1830 | 0.0000 | 1.355 | 0.0437 | 0.558 | 0.043 | 13.7 | 1.645 | 0.7300 | n/a | 0.197 | 0.8900 |
| P7 | h10 | carried_added | 0.5935 | 0.5520 | -0.0415 | 0.0383 | 0.7470 | 0.0000 | 0.2530 | 1.564 | 0.0994 | 0.584 | 0.000 | 15.1 | 2.737 | 0.7405 | n/a | 0.197 | 0.8645 |
| P7 | h10 | pooled_retention | 0.0546 | 0.0508 | -0.0038 | 0.0035 | 0.7470 | 0.0000 | 0.2530 | 1.557 | 0.0091 | 0.560 | 0.000 | 15.1 | 2.799 | 0.7435 | 146.4 | 0.197 | 0.8645 |
| P8 | n20 | large | 0.0000 | -0.0027 | -0.0027 | 0.0685 | 0.9125 | 0.0010 | 0.0865 | 1.136 | 0.1464 | 0.577 | 0.039 | 13.5 | 1.475 | 0.8585 | n/a | n/a | n/a |
| P8 | n20 | carries | 1.0000 | 0.9969 | -0.0031 | 0.1112 | 0.8940 | 0.0010 | 0.1050 | 1.104 | 0.2409 | 0.597 | 0.029 | 13.6 | 1.536 | 0.8585 | 8.5 | n/a | n/a |
| P8 | n20 | depends | 1.0000 | 0.9972 | -0.0028 | 0.1611 | 0.8890 | 0.0010 | 0.1100 | 1.112 | 0.3481 | 0.599 | 0.027 | 13.7 | 1.672 | 0.8585 | 9.1 | n/a | n/a |
| P8 | n20 | carried_margin | 0.4181 | 0.4176 | -0.0005 | 0.0793 | 0.9020 | 0.0015 | 0.0965 | 1.007 | 0.1568 | 0.117 | 0.201 | 11.3 | 1.408 | 0.8075 | n/a | n/a | n/a |
| P8 | n20 | own_margin | 0.4181 | 0.4203 | 0.0022 | 0.0546 | 0.9270 | 0.0130 | 0.0600 | 1.006 | 0.1344 | 0.104 | 0.675 | 5.8 | 1.156 | 0.6310 | n/a | n/a | n/a |
| P8 | n20 | kappa | 0.6942 | 0.6925 | -0.0016 | 0.0523 | 0.9310 | 0.0515 | 0.0175 | 0.924 | 0.1066 | 0.118 | 0.019 | 14.9 | 1.106 | 0.8820 | 6.6 | n/a | n/a |
| P8 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0546 | 0.9270 | 0.0600 | 0.0130 | 1.006 | 0.1344 | 0.104 | 0.675 | 5.8 | 1.156 | 0.6310 | n/a | n/a | n/a |
| P8 | n20 | carried_added | 0.6023 | 0.6020 | -0.0003 | 0.0983 | 0.9065 | 0.0020 | 0.0915 | 0.988 | 0.1925 | 0.118 | 0.043 | 14.3 | 1.331 | 0.8590 | n/a | n/a | n/a |
| P8 | n20 | pooled_retention | 1.0000 | 1.0005 | 0.0005 | 0.1013 | 0.8675 | 0.0065 | 0.1260 | 0.990 | 0.2118 | 0.776 | 0.000 | 15.0 | 2.140 | 0.8555 | 8.7 | n/a | n/a |
| P8 | n40 | large | 0.0000 | -0.0014 | -0.0014 | 0.0680 | 0.9630 | 0.0050 | 0.0320 | 1.192 | 0.1515 | 0.584 | 0.024 | 13.6 | 0.938 | 0.9290 | n/a | n/a | n/a |
| P8 | n40 | carries | 0.3029 | 0.3043 | 0.0013 | 0.0417 | 0.9530 | 0.0105 | 0.0365 | 1.064 | 0.0902 | 0.614 | 0.009 | 14.2 | 0.989 | 0.9235 | 8.1 | n/a | n/a |
| P8 | n40 | depends | 0.2318 | 0.2333 | 0.0015 | 0.0419 | 0.9500 | 0.0090 | 0.0410 | 1.060 | 0.0903 | 0.572 | 0.011 | 14.0 | 0.998 | 0.9250 | 8.0 | n/a | n/a |
| P8 | n40 | carried_margin | 0.4181 | 0.4189 | 0.0008 | 0.0801 | 0.9470 | 0.0065 | 0.0465 | 1.050 | 0.1682 | 0.167 | 0.172 | 11.6 | 1.018 | 0.8740 | n/a | n/a | n/a |
| P8 | n40 | own_margin | 1.8041 | 1.8080 | 0.0039 | 0.2412 | 0.9355 | 0.0095 | 0.0550 | 0.996 | 0.5022 | 0.164 | 0.276 | 10.1 | 1.103 | 0.8275 | n/a | n/a | n/a |
| P8 | n40 | kappa | 0.6942 | 0.6930 | -0.0012 | 0.0539 | 0.9355 | 0.0550 | 0.0095 | 0.977 | 0.1115 | 0.168 | 0.030 | 14.2 | 1.083 | 0.8880 | 6.4 | n/a | n/a |
| P8 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0545 | 0.9290 | 0.0580 | 0.0130 | 1.007 | 0.1345 | 0.104 | 0.675 | 5.8 | 1.162 | 0.6300 | n/a | n/a | n/a |
| P8 | n40 | carried_added | 0.6023 | 0.6033 | 0.0010 | 0.0991 | 0.9415 | 0.0050 | 0.0535 | 1.016 | 0.2041 | 0.166 | 0.053 | 13.6 | 1.072 | 0.8770 | n/a | n/a | n/a |
| P8 | n40 | pooled_retention | 0.3029 | 0.3032 | 0.0003 | 0.0306 | 0.8670 | 0.0070 | 0.1260 | 0.997 | 0.0645 | 0.751 | 0.000 | 15.0 | 2.148 | 0.8575 | 8.2 | n/a | n/a |
| P8 | n80 | large | 0.0000 | 0.0011 | 0.0011 | 0.0586 | 0.9630 | 0.0115 | 0.0255 | 1.281 | 0.1331 | 0.469 | 0.195 | 10.9 | 0.939 | 0.8900 | n/a | n/a | n/a |
| P8 | n80 | carries | 0.0610 | 0.0616 | 0.0006 | 0.0098 | 0.9510 | 0.0040 | 0.0450 | 1.152 | 0.0216 | 0.613 | 0.034 | 13.6 | 0.991 | 0.9205 | 8.1 | n/a | n/a |
| P8 | n80 | depends | 0.0432 | 0.0434 | 0.0003 | 0.0069 | 0.9545 | 0.0055 | 0.0400 | 1.211 | 0.0152 | 0.546 | 0.099 | 12.2 | 0.983 | 0.9160 | 7.9 | n/a | n/a |
| P8 | n80 | carried_margin | 0.4181 | 0.4214 | 0.0033 | 0.0849 | 0.9395 | 0.0145 | 0.0460 | 1.036 | 0.2179 | 0.127 | 0.626 | 6.5 | 1.084 | 0.7145 | n/a | n/a | n/a |
| P8 | n80 | own_margin | 9.6872 | 9.7107 | 0.0235 | 1.2989 | 0.9275 | 0.0250 | 0.0475 | 1.057 | 3.5499 | 0.145 | 0.627 | 6.4 | 1.193 | 0.7065 | n/a | n/a | n/a |
| P8 | n80 | kappa | 0.6942 | 0.6937 | -0.0005 | 0.0545 | 0.9380 | 0.0500 | 0.0120 | 1.025 | 0.1178 | 0.127 | 0.269 | 10.1 | 1.085 | 0.8365 | 6.3 | n/a | n/a |
| P8 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0545 | 0.9280 | 0.0595 | 0.0125 | 1.008 | 0.1345 | 0.104 | 0.673 | 5.8 | 1.161 | 0.6350 | n/a | n/a | n/a |
| P8 | n80 | carried_added | 0.6023 | 0.6058 | 0.0035 | 0.1042 | 0.9395 | 0.0085 | 0.0520 | 0.988 | 0.2258 | 0.128 | 0.361 | 9.1 | 1.075 | 0.7980 | n/a | n/a | n/a |
| P8 | n80 | pooled_retention | 0.0610 | 0.0611 | 0.0000 | 0.0062 | 0.8690 | 0.0065 | 0.1245 | 0.992 | 0.0129 | 0.816 | 0.000 | 15.0 | 2.160 | 0.8575 | 7.9 | n/a | n/a |
| P8 | n160 | large | 0.0000 | -0.0008 | -0.0008 | 0.0540 | 0.9590 | 0.0280 | 0.0130 | 1.132 | 0.1145 | 0.393 | 0.261 | 10.1 | 0.951 | 0.8590 | n/a | n/a | n/a |
| P8 | n160 | carries | 0.0278 | 0.0281 | 0.0003 | 0.0045 | 0.9170 | 0.0015 | 0.0815 | 1.082 | 0.0093 | 0.587 | 0.012 | 14.5 | 1.287 | 0.8880 | 16.2 | n/a | n/a |
| P8 | n160 | depends | 0.0195 | 0.0196 | 0.0002 | 0.0025 | 0.9615 | 0.0025 | 0.0360 | 1.179 | 0.0057 | 0.582 | 0.038 | 13.4 | 0.933 | 0.9180 | 15.8 | n/a | n/a |
| P8 | n160 | carried_margin | 0.4181 | 0.4195 | 0.0014 | 0.0413 | 0.9685 | 0.0095 | 0.0220 | 1.156 | 0.0919 | 0.527 | 0.080 | 12.5 | 0.926 | 0.9110 | n/a | n/a | n/a |
| P8 | n160 | own_margin | 21.4901 | 21.4790 | -0.0111 | 1.2963 | 0.9580 | 0.0320 | 0.0100 | 1.197 | 2.9590 | 0.512 | 0.131 | 11.9 | 0.950 | 0.9000 | n/a | n/a | n/a |
| P8 | n160 | kappa | 0.6942 | 0.6971 | 0.0029 | 0.0404 | 0.9000 | 0.0885 | 0.0115 | 0.993 | 0.0859 | 0.528 | 0.002 | 14.9 | 1.416 | 0.8775 | 8.5 | n/a | n/a |
| P8 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0546 | 0.9300 | 0.0570 | 0.0130 | 1.007 | 0.1345 | 0.104 | 0.675 | 5.8 | 1.161 | 0.6330 | n/a | n/a | n/a |
| P8 | n160 | carried_added | 0.6023 | 0.6040 | 0.0017 | 0.0711 | 0.9265 | 0.0060 | 0.0675 | 1.027 | 0.1515 | 0.525 | 0.011 | 14.5 | 1.150 | 0.8830 | n/a | n/a | n/a |
| P8 | n160 | pooled_retention | 0.0278 | 0.0278 | 0.0000 | 0.0028 | 0.8705 | 0.0060 | 0.1235 | 0.993 | 0.0059 | 0.571 | 0.000 | 15.1 | 2.163 | 0.8595 | 16.3 | n/a | n/a |
| P8 | n320 | large | 0.0000 | -0.0012 | -0.0012 | 0.0586 | 0.9535 | 0.0285 | 0.0180 | 1.092 | 0.1286 | 0.277 | 0.364 | 8.8 | 0.978 | 0.8065 | n/a | n/a | n/a |
| P8 | n320 | carries | 0.0239 | 0.0242 | 0.0003 | 0.0038 | 0.9050 | 0.0010 | 0.0940 | 1.068 | 0.0079 | 0.579 | 0.006 | 14.6 | 1.336 | 0.8790 | 17.6 | n/a | n/a |
| P8 | n320 | depends | 0.0167 | 0.0169 | 0.0002 | 0.0021 | 0.9630 | 0.0015 | 0.0355 | 1.155 | 0.0047 | 0.591 | 0.030 | 13.6 | 0.929 | 0.9160 | 17.1 | n/a | n/a |
| P8 | n320 | carried_margin | 0.4181 | 0.4190 | 0.0009 | 0.0382 | 0.9705 | 0.0110 | 0.0185 | 1.178 | 0.0863 | 0.587 | 0.048 | 13.2 | 0.890 | 0.9220 | n/a | n/a | n/a |
| P8 | n320 | own_margin | 24.9973 | 24.9536 | -0.0438 | 1.3718 | 0.9595 | 0.0305 | 0.0100 | 1.215 | 3.1670 | 0.585 | 0.090 | 12.7 | 0.938 | 0.9120 | n/a | n/a | n/a |
| P8 | n320 | kappa | 0.6942 | 0.6970 | 0.0028 | 0.0398 | 0.8975 | 0.0910 | 0.0115 | 0.985 | 0.0849 | 0.583 | 0.002 | 15.0 | 1.506 | 0.8780 | 8.7 | n/a | n/a |
| P8 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4202 | -0.0021 | 0.0545 | 0.9275 | 0.0600 | 0.0125 | 1.008 | 0.1344 | 0.105 | 0.675 | 5.8 | 1.158 | 0.6335 | n/a | n/a | n/a |
| P8 | n320 | carried_added | 0.6023 | 0.6035 | 0.0012 | 0.0693 | 0.9195 | 0.0040 | 0.0765 | 1.027 | 0.1473 | 0.588 | 0.004 | 14.8 | 1.188 | 0.8815 | n/a | n/a | n/a |
| P8 | n320 | pooled_retention | 0.0239 | 0.0239 | 0.0000 | 0.0024 | 0.8695 | 0.0060 | 0.1245 | 0.986 | 0.0051 | 0.529 | 0.000 | 15.1 | 2.176 | 0.8580 | 17.5 | n/a | n/a |
| P8 | h2 | large | 0.0000 | -0.0019 | -0.0019 | 0.0505 | 0.9425 | 0.0365 | 0.0210 | 1.056 | 0.1303 | 0.121 | 0.660 | 6.0 | 1.030 | 0.6495 | n/a | 1.000 | 0.9425 |
| P8 | h2 | carries | 0.3149 | 0.3148 | -0.0001 | 0.0300 | 0.8680 | 0.0070 | 0.1250 | 0.986 | 0.0628 | 0.581 | 0.000 | 15.1 | 2.077 | 0.8580 | 115.0 | 1.000 | 0.8680 |
| P8 | h2 | depends | 0.2419 | 0.2422 | 0.0003 | 0.0163 | 0.8790 | 0.0060 | 0.1150 | 1.044 | 0.0339 | 0.571 | 0.000 | 15.2 | 1.696 | 0.8630 | 55.1 | 1.000 | 0.8790 |
| P8 | h2 | carried_margin | 0.4183 | 0.4184 | 0.0001 | 0.0209 | 0.8900 | 0.0065 | 0.1035 | 1.059 | 0.0447 | 0.526 | 0.000 | 15.3 | 1.450 | 0.8695 | n/a | 1.000 | 0.8900 |
| P8 | h2 | own_margin | 1.7295 | 1.7296 | 0.0001 | 0.0324 | 0.9195 | 0.0730 | 0.0075 | 1.023 | 0.0671 | 0.451 | 0.005 | 15.0 | 1.188 | 0.8675 | n/a | 1.000 | 0.9195 |
| P8 | h2 | kappa | 0.6943 | 0.6976 | 0.0033 | 0.0365 | 0.8635 | 0.1200 | 0.0165 | 0.911 | 0.0765 | 0.524 | 0.000 | 15.1 | 1.891 | 0.8590 | 10.1 | 1.000 | 0.8635 |
| P8 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4203 | -0.0019 | 0.0545 | 0.9270 | 0.0600 | 0.0130 | 1.007 | 0.1348 | 0.105 | 0.675 | 5.8 | 1.159 | 0.6310 | n/a | 1.000 | 0.9270 |
| P8 | h2 | carried_added | 0.6025 | 0.6029 | 0.0003 | 0.0611 | 0.8675 | 0.0060 | 0.1265 | 0.985 | 0.1275 | 0.530 | 0.000 | 15.1 | 2.166 | 0.8560 | n/a | 1.000 | 0.8675 |
| P8 | h2 | pooled_retention | 0.3149 | 0.3151 | 0.0003 | 0.0319 | 0.8680 | 0.0065 | 0.1255 | 0.982 | 0.0664 | 0.561 | 0.000 | 15.1 | 2.213 | 0.8570 | 116.5 | 1.000 | 0.8680 |
| P8 | h5 | large | 0.0000 | -0.0017 | -0.0017 | 0.0506 | 0.9385 | 0.0375 | 0.0240 | 1.094 | 0.1319 | 0.166 | 0.629 | 6.1 | 1.069 | 0.6470 | n/a | 0.996 | 0.9385 |
| P8 | h5 | carries | 0.1177 | 0.1178 | 0.0001 | 0.0122 | 0.8695 | 0.0065 | 0.1240 | 0.990 | 0.0257 | 0.590 | 0.000 | 15.2 | 2.216 | 0.8585 | 148.8 | 0.996 | 0.8685 |
| P8 | h5 | depends | 0.0847 | 0.0848 | 0.0001 | 0.0051 | 0.8810 | 0.0045 | 0.1145 | 1.051 | 0.0109 | 0.581 | 0.001 | 15.1 | 1.744 | 0.8640 | 78.3 | 0.996 | 0.8800 |
| P8 | h5 | carried_margin | 0.4183 | 0.4186 | 0.0002 | 0.0209 | 0.8915 | 0.0060 | 0.1025 | 1.058 | 0.0451 | 0.541 | 0.001 | 15.1 | 1.472 | 0.8685 | n/a | 0.996 | 0.8905 |
| P8 | h5 | own_margin | 4.9368 | 4.9365 | -0.0002 | 0.0615 | 0.9375 | 0.0560 | 0.0065 | 1.126 | 0.1377 | 0.536 | 0.066 | 13.2 | 1.084 | 0.8770 | n/a | 0.996 | 0.9370 |
| P8 | h5 | kappa | 0.6943 | 0.6976 | 0.0033 | 0.0363 | 0.8675 | 0.1180 | 0.0145 | 0.922 | 0.0763 | 0.551 | 0.000 | 15.1 | 1.893 | 0.8595 | 10.0 | 0.996 | 0.8665 |
| P8 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4202 | -0.0019 | 0.0548 | 0.9150 | 0.0745 | 0.0105 | 1.051 | 0.1404 | 0.145 | 0.655 | 5.9 | 1.309 | 0.6300 | n/a | 0.996 | 0.9145 |
| P8 | h5 | carried_added | 0.6025 | 0.6031 | 0.0005 | 0.0612 | 0.8710 | 0.0065 | 0.1225 | 0.983 | 0.1277 | 0.540 | 0.000 | 15.1 | 2.148 | 0.8585 | n/a | 0.996 | 0.8700 |
| P8 | h5 | pooled_retention | 0.1177 | 0.1177 | 0.0001 | 0.0119 | 0.8695 | 0.0070 | 0.1235 | 0.990 | 0.0249 | 0.555 | 0.000 | 15.1 | 2.204 | 0.8575 | 146.3 | 0.996 | 0.8685 |
| P8 | h10 | large | 0.0000 | 0.0014 | 0.0014 | 0.0433 | 0.9155 | 0.0605 | 0.0240 | 0.731 | 0.0806 | 0.083 | 0.488 | 8.5 | 1.168 | 0.6600 | n/a | 0.201 | 0.9070 |
| P8 | h10 | carries | 0.0553 | 0.0516 | -0.0037 | 0.0037 | 0.7465 | 0.0000 | 0.2535 | 1.561 | 0.0095 | 0.590 | 0.001 | 15.1 | 2.593 | 0.7405 | 123.8 | 0.201 | 0.8705 |
| P8 | h10 | depends | 0.0390 | 0.0377 | -0.0013 | 0.0014 | 0.8100 | 0.0000 | 0.1900 | 1.654 | 0.0039 | 0.585 | 0.018 | 14.4 | 1.798 | 0.7690 | 111.5 | 0.201 | 0.9080 |
| P8 | h10 | carried_margin | 0.4183 | 0.4052 | -0.0132 | 0.0143 | 0.8050 | 0.0000 | 0.1950 | 1.617 | 0.0379 | 0.528 | 0.017 | 14.5 | 1.779 | 0.7610 | n/a | 0.201 | 0.9085 |
| P8 | h10 | own_margin | 10.7131 | 10.7408 | 0.0277 | 0.0977 | 0.9605 | 0.0300 | 0.0095 | 1.391 | 0.2132 | 0.516 | 0.267 | 10.5 | 0.950 | 0.8760 | n/a | 0.201 | 0.9600 |
| P8 | h10 | kappa | 0.6943 | 0.7224 | 0.0281 | 0.0277 | 0.7510 | 0.2490 | 0.0000 | 1.372 | 0.0715 | 0.531 | 0.000 | 15.2 | 2.384 | 0.7395 | 11.6 | 0.201 | 0.8625 |
| P8 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4037 | 0.0146 | 0.0450 | 0.8710 | 0.1245 | 0.0045 | 0.763 | 0.0847 | 0.041 | 0.585 | 8.3 | 1.538 | 0.5630 | n/a | 0.201 | 0.8955 |
| P8 | h10 | carried_added | 0.6025 | 0.5623 | -0.0402 | 0.0397 | 0.7410 | 0.0000 | 0.2590 | 1.549 | 0.1029 | 0.516 | 0.001 | 15.2 | 2.648 | 0.7380 | n/a | 0.201 | 0.8700 |
| P8 | h10 | pooled_retention | 0.0553 | 0.0516 | -0.0037 | 0.0036 | 0.7415 | 0.0000 | 0.2585 | 1.563 | 0.0093 | 0.547 | 0.000 | 15.2 | 2.784 | 0.7355 | 124.5 | 0.201 | 0.8680 |
| P9 | n20 | large | -0.3274 | -0.3272 | 0.0003 | 0.0463 | 0.9545 | 0.0445 | 0.0010 | 1.117 | 0.1007 | 0.571 | 0.019 | 13.6 | 0.977 | 0.8755 | n/a | n/a | n/a |
| P9 | n20 | carries | 0.4483 | 0.4493 | 0.0010 | 0.0498 | 0.8925 | 0.0025 | 0.1050 | 1.081 | 0.1079 | 0.589 | 0.018 | 13.9 | 1.636 | 0.8635 | 9.9 | n/a | n/a |
| P9 | n20 | depends | 0.2000 | 0.2030 | 0.0030 | 0.0778 | 0.9520 | 0.0080 | 0.0400 | 1.079 | 0.1668 | 0.577 | 0.001 | 15.0 | 1.010 | 0.9030 | 14.8 | n/a | n/a |
| P9 | n20 | carried_margin | 0.0819 | 0.0822 | 0.0004 | 0.0302 | 0.9455 | 0.0055 | 0.0490 | 1.111 | 0.0650 | 0.557 | 0.001 | 15.0 | 1.018 | 0.8860 | n/a | n/a | n/a |
| P9 | n20 | own_margin | 0.4093 | 0.4094 | 0.0001 | 0.0289 | 0.8960 | 0.0030 | 0.1010 | 1.190 | 0.0623 | 0.562 | 0.129 | 12.0 | 1.363 | 0.8200 | n/a | n/a | n/a |
| P9 | n20 | kappa | 0.3077 | 0.3098 | 0.0022 | 0.1053 | 0.9235 | 0.0575 | 0.0190 | 0.984 | 0.2262 | 0.554 | 0.000 | 15.3 | 1.134 | 0.8980 | 7.2 | n/a | n/a |
| P9 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0289 | 0.8960 | 0.1010 | 0.0030 | 1.190 | 0.0623 | 0.562 | 0.129 | 12.0 | 1.363 | 0.8200 | n/a | n/a | n/a |
| P9 | n20 | carried_added | 0.2661 | 0.2666 | 0.0006 | 0.0394 | 0.9125 | 0.0015 | 0.0860 | 0.984 | 0.0783 | 0.555 | 0.000 | 15.2 | 1.399 | 0.8965 | n/a | n/a | n/a |
| P9 | n20 | pooled_retention | 0.4483 | 0.4485 | 0.0002 | 0.0452 | 0.8750 | 0.0045 | 0.1205 | 1.007 | 0.0950 | 0.538 | 0.000 | 15.1 | 2.275 | 0.8635 | 9.8 | n/a | n/a |
| P9 | n40 | large | -0.0564 | -0.0554 | 0.0010 | 0.0616 | 0.9670 | 0.0075 | 0.0255 | 1.146 | 0.1372 | 0.588 | 0.015 | 13.8 | 0.898 | 0.9340 | n/a | n/a | n/a |
| P9 | n40 | carries | 0.2756 | 0.2767 | 0.0011 | 0.0375 | 0.9565 | 0.0110 | 0.0325 | 1.084 | 0.0822 | 0.595 | 0.003 | 14.4 | 0.950 | 0.9255 | 9.3 | n/a | n/a |
| P9 | n40 | depends | 0.2000 | 0.2018 | 0.0018 | 0.0366 | 0.9515 | 0.0100 | 0.0385 | 1.121 | 0.0816 | 0.590 | 0.003 | 14.5 | 1.013 | 0.9305 | 9.5 | n/a | n/a |
| P9 | n40 | carried_margin | 0.3529 | 0.3540 | 0.0011 | 0.0587 | 0.9465 | 0.0060 | 0.0475 | 1.085 | 0.1275 | 0.572 | 0.003 | 14.7 | 1.021 | 0.9185 | n/a | n/a | n/a |
| P9 | n40 | own_margin | 1.7645 | 1.7689 | 0.0044 | 0.1843 | 0.9375 | 0.0105 | 0.0520 | 1.060 | 0.4036 | 0.564 | 0.005 | 14.3 | 1.084 | 0.9060 | n/a | n/a | n/a |
| P9 | n40 | kappa | 0.6571 | 0.6580 | 0.0009 | 0.0536 | 0.9305 | 0.0615 | 0.0080 | 1.023 | 0.1161 | 0.573 | 0.000 | 15.2 | 1.097 | 0.9165 | 6.8 | n/a | n/a |
| P9 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0289 | 0.8965 | 0.1010 | 0.0025 | 1.192 | 0.0621 | 0.559 | 0.129 | 12.0 | 1.363 | 0.8220 | n/a | n/a | n/a |
| P9 | n40 | carried_added | 0.5371 | 0.5384 | 0.0013 | 0.0802 | 0.9355 | 0.0040 | 0.0605 | 1.005 | 0.1672 | 0.575 | 0.000 | 15.1 | 1.100 | 0.9035 | n/a | n/a | n/a |
| P9 | n40 | pooled_retention | 0.2756 | 0.2758 | 0.0002 | 0.0278 | 0.8765 | 0.0045 | 0.1190 | 1.012 | 0.0585 | 0.514 | 0.000 | 15.1 | 2.253 | 0.8640 | 9.3 | n/a | n/a |
| P9 | n80 | large | 1.5066 | 1.5054 | -0.0011 | 0.2240 | 0.9555 | 0.0040 | 0.0405 | 1.156 | 0.5020 | 0.580 | 0.044 | 13.1 | 0.951 | 0.9135 | n/a | n/a | n/a |
| P9 | n80 | carries | 0.2151 | 0.2165 | 0.0014 | 0.0337 | 0.9510 | 0.0035 | 0.0455 | 1.170 | 0.0760 | 0.583 | 0.041 | 13.2 | 0.989 | 0.9250 | 12.4 | n/a | n/a |
| P9 | n80 | depends | 0.2000 | 0.2014 | 0.0014 | 0.0313 | 0.9535 | 0.0035 | 0.0430 | 1.192 | 0.0711 | 0.581 | 0.051 | 13.0 | 1.084 | 0.9250 | 12.1 | n/a | n/a |
| P9 | n80 | carried_margin | 1.9159 | 1.9149 | -0.0010 | 0.2335 | 0.9560 | 0.0030 | 0.0410 | 1.134 | 0.5235 | 0.586 | 0.035 | 13.3 | 0.967 | 0.9080 | n/a | n/a | n/a |
| P9 | n80 | own_margin | 9.5794 | 9.5805 | 0.0011 | 0.7445 | 0.9630 | 0.0150 | 0.0220 | 1.301 | 1.7190 | 0.597 | 0.139 | 12.0 | 0.901 | 0.9195 | n/a | n/a | n/a |
| P9 | n80 | kappa | 0.9123 | 0.9127 | 0.0004 | 0.0125 | 0.9200 | 0.0735 | 0.0065 | 1.026 | 0.0269 | 0.589 | 0.009 | 14.1 | 1.251 | 0.8930 | 7.7 | n/a | n/a |
| P9 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0290 | 0.8990 | 0.0980 | 0.0030 | 1.191 | 0.0626 | 0.564 | 0.129 | 12.0 | 1.368 | 0.8205 | n/a | n/a | n/a |
| P9 | n80 | carried_added | 2.1001 | 2.0992 | -0.0009 | 0.2648 | 0.9470 | 0.0025 | 0.0505 | 1.100 | 0.5888 | 0.584 | 0.023 | 13.7 | 1.024 | 0.9030 | n/a | n/a | n/a |
| P9 | n80 | pooled_retention | 0.2151 | 0.2152 | 0.0001 | 0.0217 | 0.8755 | 0.0040 | 0.1205 | 1.007 | 0.0456 | 0.480 | 0.000 | 15.1 | 2.291 | 0.8635 | 12.5 | n/a | n/a |
| P9 | n160 | large | 3.9734 | 3.9803 | 0.0069 | 0.4726 | 0.9390 | 0.0030 | 0.0580 | 1.130 | 1.0514 | 0.563 | 0.007 | 14.5 | 1.073 | 0.9030 | n/a | n/a | n/a |
| P9 | n160 | carries | 0.2067 | 0.2084 | 0.0018 | 0.0328 | 0.9090 | 0.0000 | 0.0910 | 1.138 | 0.0706 | 0.578 | 0.006 | 14.6 | 1.387 | 0.8830 | 16.2 | n/a | n/a |
| P9 | n160 | depends | 0.2000 | 0.2018 | 0.0018 | 0.0315 | 0.9150 | 0.0000 | 0.0850 | 1.147 | 0.0679 | 0.574 | 0.006 | 14.5 | 1.478 | 0.8870 | 15.7 | n/a | n/a |
| P9 | n160 | carried_margin | 4.3827 | 4.3897 | 0.0070 | 0.4852 | 0.9350 | 0.0030 | 0.0620 | 1.118 | 1.0765 | 0.567 | 0.006 | 14.6 | 1.091 | 0.8950 | n/a | n/a | n/a |
| P9 | n160 | own_margin | 21.9134 | 21.9222 | 0.0088 | 1.3042 | 0.9610 | 0.0315 | 0.0075 | 1.200 | 2.9965 | 0.583 | 0.075 | 12.7 | 0.932 | 0.9160 | n/a | n/a | n/a |
| P9 | n160 | kappa | 0.9597 | 0.9600 | 0.0004 | 0.0054 | 0.8985 | 0.0935 | 0.0080 | 0.975 | 0.0114 | 0.574 | 0.001 | 15.0 | 1.525 | 0.8780 | 8.5 | n/a | n/a |
| P9 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0290 | 0.8950 | 0.1025 | 0.0025 | 1.190 | 0.0623 | 0.565 | 0.130 | 12.0 | 1.370 | 0.8225 | n/a | n/a | n/a |
| P9 | n160 | carried_added | 4.5669 | 4.5741 | 0.0072 | 0.5203 | 0.9245 | 0.0035 | 0.0720 | 1.103 | 1.1468 | 0.566 | 0.005 | 14.7 | 1.140 | 0.8885 | n/a | n/a | n/a |
| P9 | n160 | pooled_retention | 0.2067 | 0.2068 | 0.0001 | 0.0209 | 0.8745 | 0.0040 | 0.1215 | 0.997 | 0.0439 | 0.529 | 0.000 | 15.1 | 2.305 | 0.8645 | 16.2 | n/a | n/a |
| P9 | n320 | large | 4.6436 | 4.6469 | 0.0034 | 0.5375 | 0.9290 | 0.0025 | 0.0685 | 1.123 | 1.1906 | 0.569 | 0.004 | 14.7 | 1.135 | 0.8920 | n/a | n/a | n/a |
| P9 | n320 | carries | 0.2058 | 0.2072 | 0.0014 | 0.0323 | 0.9025 | 0.0000 | 0.0975 | 1.127 | 0.0688 | 0.585 | 0.005 | 14.8 | 1.414 | 0.8810 | 17.4 | n/a | n/a |
| P9 | n320 | depends | 0.2000 | 0.2014 | 0.0014 | 0.0311 | 0.9055 | 0.0000 | 0.0945 | 1.135 | 0.0663 | 0.587 | 0.005 | 14.7 | 1.543 | 0.8850 | 16.9 | n/a | n/a |
| P9 | n320 | carried_margin | 5.0529 | 5.0563 | 0.0035 | 0.5503 | 0.9225 | 0.0030 | 0.0745 | 1.113 | 1.2136 | 0.566 | 0.004 | 14.7 | 1.173 | 0.8910 | n/a | n/a | n/a |
| P9 | n320 | own_margin | 25.2643 | 25.2838 | 0.0195 | 1.4090 | 0.9555 | 0.0365 | 0.0080 | 1.196 | 3.2463 | 0.580 | 0.070 | 12.7 | 0.976 | 0.9010 | n/a | n/a | n/a |
| P9 | n320 | kappa | 0.9648 | 0.9651 | 0.0003 | 0.0047 | 0.8965 | 0.0930 | 0.0105 | 0.953 | 0.0098 | 0.569 | 0.000 | 15.1 | 1.569 | 0.8775 | 8.6 | n/a | n/a |
| P9 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0289 | 0.8990 | 0.0985 | 0.0025 | 1.190 | 0.0622 | 0.563 | 0.130 | 12.0 | 1.375 | 0.8220 | n/a | n/a | n/a |
| P9 | n320 | carried_added | 5.2371 | 5.2407 | 0.0036 | 0.5859 | 0.9155 | 0.0030 | 0.0815 | 1.101 | 1.2861 | 0.566 | 0.003 | 14.8 | 1.234 | 0.8865 | n/a | n/a | n/a |
| P9 | n320 | pooled_retention | 0.2058 | 0.2059 | 0.0001 | 0.0207 | 0.8760 | 0.0050 | 0.1190 | 1.003 | 0.0434 | 0.529 | 0.000 | 15.1 | 2.297 | 0.8640 | 17.3 | n/a | n/a |
| P9 | h2 | large | -0.0642 | -0.0641 | 0.0001 | 0.0254 | 0.9685 | 0.0265 | 0.0050 | 1.313 | 0.0565 | 0.569 | 0.148 | 11.8 | 0.881 | 0.9090 | n/a | 1.000 | 0.9685 |
| P9 | h2 | carries | 0.2772 | 0.2772 | 0.0001 | 0.0264 | 0.8720 | 0.0055 | 0.1225 | 0.994 | 0.0555 | 0.586 | 0.000 | 15.1 | 2.147 | 0.8620 | 122.2 | 1.000 | 0.8720 |
| P9 | h2 | depends | 0.2000 | 0.2003 | 0.0003 | 0.0113 | 0.8860 | 0.0025 | 0.1115 | 1.082 | 0.0240 | 0.587 | 0.000 | 15.2 | 1.680 | 0.8720 | 55.3 | 1.000 | 0.8860 |
| P9 | h2 | carried_margin | 0.3451 | 0.3453 | 0.0002 | 0.0136 | 0.9175 | 0.0025 | 0.0800 | 1.127 | 0.0301 | 0.577 | 0.000 | 15.3 | 1.257 | 0.8975 | n/a | 1.000 | 0.9175 |
| P9 | h2 | own_margin | 1.7255 | 1.7255 | -0.0001 | 0.0316 | 0.8990 | 0.0940 | 0.0070 | 1.033 | 0.0663 | 0.591 | 0.001 | 15.2 | 1.389 | 0.8770 | n/a | 1.000 | 0.8990 |
| P9 | h2 | kappa | 0.6520 | 0.6560 | 0.0040 | 0.0417 | 0.8680 | 0.1160 | 0.0160 | 0.909 | 0.0870 | 0.571 | 0.000 | 15.1 | 1.982 | 0.8620 | 10.1 | 1.000 | 0.8680 |
| P9 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0289 | 0.8970 | 0.1000 | 0.0030 | 1.192 | 0.0622 | 0.561 | 0.130 | 12.0 | 1.358 | 0.8215 | n/a | 1.000 | 0.8970 |
| P9 | h2 | carried_added | 0.5293 | 0.5297 | 0.0004 | 0.0536 | 0.8745 | 0.0040 | 0.1215 | 0.994 | 0.1121 | 0.584 | 0.000 | 15.1 | 2.272 | 0.8625 | n/a | 1.000 | 0.8745 |
| P9 | h2 | pooled_retention | 0.2772 | 0.2773 | 0.0002 | 0.0279 | 0.8760 | 0.0035 | 0.1205 | 0.999 | 0.0585 | 0.572 | 0.000 | 15.0 | 2.298 | 0.8635 | 120.9 | 1.000 | 0.8760 |
| P9 | h5 | large | 0.5757 | 0.5761 | 0.0004 | 0.0670 | 0.8955 | 0.0025 | 0.1020 | 1.115 | 0.1425 | 0.554 | 0.009 | 14.3 | 1.427 | 0.8690 | n/a | 0.997 | 0.8955 |
| P9 | h5 | carries | 0.2288 | 0.2291 | 0.0002 | 0.0238 | 0.8750 | 0.0030 | 0.1220 | 1.003 | 0.0498 | 0.580 | 0.000 | 15.1 | 2.317 | 0.8640 | 157.8 | 0.997 | 0.8750 |
| P9 | h5 | depends | 0.2000 | 0.2003 | 0.0003 | 0.0180 | 0.8760 | 0.0030 | 0.1210 | 1.022 | 0.0377 | 0.575 | 0.000 | 15.2 | 2.448 | 0.8635 | 78.4 | 0.997 | 0.8760 |
| P9 | h5 | carried_margin | 0.9850 | 0.9854 | 0.0004 | 0.0774 | 0.8795 | 0.0035 | 0.1170 | 1.013 | 0.1630 | 0.586 | 0.000 | 15.2 | 2.136 | 0.8670 | n/a | 0.997 | 0.8795 |
| P9 | h5 | own_margin | 4.9248 | 4.9241 | -0.0007 | 0.0605 | 0.9185 | 0.0745 | 0.0070 | 1.120 | 0.1366 | 0.590 | 0.046 | 13.6 | 1.280 | 0.8700 | n/a | 0.997 | 0.9185 |
| P9 | h5 | kappa | 0.8425 | 0.8442 | 0.0018 | 0.0189 | 0.8675 | 0.1175 | 0.0150 | 0.908 | 0.0394 | 0.574 | 0.000 | 15.1 | 2.008 | 0.8625 | 10.1 | 0.997 | 0.8670 |
| P9 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4093 | -0.0000 | 0.0290 | 0.8965 | 0.1015 | 0.0020 | 1.308 | 0.0646 | 0.555 | 0.169 | 11.5 | 1.353 | 0.8235 | n/a | 0.997 | 0.8965 |
| P9 | h5 | carried_added | 1.1692 | 1.1698 | 0.0006 | 0.1180 | 0.8770 | 0.0035 | 0.1195 | 0.998 | 0.2472 | 0.596 | 0.000 | 15.1 | 2.304 | 0.8630 | n/a | 0.997 | 0.8770 |
| P9 | h5 | pooled_retention | 0.2288 | 0.2290 | 0.0001 | 0.0231 | 0.8765 | 0.0035 | 0.1200 | 0.993 | 0.0483 | 0.577 | 0.000 | 15.1 | 2.332 | 0.8635 | 157.2 | 0.997 | 0.8760 |
| P9 | h10 | large | 1.7261 | 1.6043 | -0.1218 | 0.1250 | 0.7330 | 0.0000 | 0.2670 | 1.369 | 0.2958 | 0.574 | 0.002 | 15.1 | 2.446 | 0.7190 | n/a | 0.196 | 0.8765 |
| P9 | h10 | carries | 0.2136 | 0.1984 | -0.0152 | 0.0145 | 0.7340 | 0.0000 | 0.2660 | 1.423 | 0.0357 | 0.579 | 0.001 | 15.1 | 2.774 | 0.7285 | 144.8 | 0.196 | 0.8780 |
| P9 | h10 | depends | 0.2000 | 0.1867 | -0.0133 | 0.0127 | 0.7355 | 0.0000 | 0.2645 | 1.435 | 0.0312 | 0.579 | 0.001 | 15.0 | 2.904 | 0.7300 | 126.6 | 0.196 | 0.8785 |
| P9 | h10 | carried_margin | 2.1354 | 1.9988 | -0.1366 | 0.1287 | 0.7325 | 0.0000 | 0.2675 | 1.441 | 0.3193 | 0.575 | 0.002 | 15.1 | 2.796 | 0.7275 | n/a | 0.196 | 0.8765 |
| P9 | h10 | own_margin | 10.6772 | 10.7062 | 0.0290 | 0.0753 | 0.9580 | 0.0375 | 0.0045 | 1.659 | 0.1831 | 0.548 | 0.236 | 10.8 | 0.943 | 0.8905 | n/a | 0.196 | 0.9650 |
| P9 | h10 | kappa | 0.9206 | 0.9284 | 0.0078 | 0.0074 | 0.7395 | 0.2605 | 0.0000 | 1.254 | 0.0182 | 0.566 | 0.000 | 15.2 | 2.547 | 0.7280 | 11.9 | 0.196 | 0.8665 |
| P9 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3946 | 0.0147 | 0.0200 | 0.8065 | 0.1935 | 0.0000 | 1.350 | 0.0432 | 0.554 | 0.045 | 13.6 | 1.574 | 0.7100 | n/a | 0.196 | 0.8925 |
| P9 | h10 | carried_added | 2.3196 | 2.1543 | -0.1654 | 0.1555 | 0.7305 | 0.0000 | 0.2695 | 1.430 | 0.3846 | 0.575 | 0.000 | 15.1 | 2.893 | 0.7270 | n/a | 0.196 | 0.8755 |
| P9 | h10 | pooled_retention | 0.2136 | 0.1984 | -0.0152 | 0.0143 | 0.7310 | 0.0000 | 0.2690 | 1.430 | 0.0353 | 0.548 | 0.000 | 15.1 | 2.927 | 0.7275 | 145.1 | 0.196 | 0.8755 |
| P10 | n20 | large | -0.3345 | -0.3336 | 0.0009 | 0.0544 | 0.9235 | 0.0720 | 0.0045 | 1.052 | 0.1098 | 0.381 | 0.108 | 11.8 | 1.132 | 0.8285 | n/a | n/a | n/a |
| P10 | n20 | carries | 0.4447 | 0.4460 | 0.0013 | 0.0480 | 0.9070 | 0.0010 | 0.0920 | 1.187 | 0.1095 | 0.605 | 0.025 | 13.8 | 1.523 | 0.8745 | 8.6 | n/a | n/a |
| P10 | n20 | depends | 0.2000 | 0.2012 | 0.0012 | 0.0788 | 0.9645 | 0.0040 | 0.0315 | 1.129 | 0.1731 | 0.366 | 0.008 | 14.4 | 0.962 | 0.8945 | 9.3 | n/a | n/a |
| P10 | n20 | carried_margin | 0.0836 | 0.0842 | 0.0005 | 0.0347 | 0.9580 | 0.0010 | 0.0410 | 1.144 | 0.0751 | 0.129 | 0.086 | 12.8 | 0.959 | 0.8450 | n/a | n/a | n/a |
| P10 | n20 | own_margin | 0.4181 | 0.4178 | -0.0003 | 0.0543 | 0.9135 | 0.0145 | 0.0720 | 0.982 | 0.1292 | 0.121 | 0.674 | 6.0 | 1.224 | 0.6020 | n/a | n/a | n/a |
| P10 | n20 | kappa | 0.3122 | 0.3122 | -0.0000 | 0.1122 | 0.9340 | 0.0505 | 0.0155 | 1.025 | 0.2421 | 0.128 | 0.019 | 14.9 | 1.085 | 0.8935 | 6.5 | n/a | n/a |
| P10 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4178 | 0.0003 | 0.0543 | 0.9135 | 0.0720 | 0.0145 | 0.982 | 0.1292 | 0.121 | 0.674 | 6.0 | 1.224 | 0.6020 | n/a | n/a | n/a |
| P10 | n20 | carried_added | 0.2678 | 0.2679 | 0.0001 | 0.0423 | 0.9060 | 0.0005 | 0.0935 | 1.064 | 0.0867 | 0.128 | 0.033 | 14.3 | 1.376 | 0.8675 | n/a | n/a | n/a |
| P10 | n20 | pooled_retention | 0.4447 | 0.4442 | -0.0004 | 0.0434 | 0.8840 | 0.0015 | 0.1145 | 1.071 | 0.0949 | 0.765 | 0.000 | 15.0 | 2.254 | 0.8750 | 8.6 | n/a | n/a |
| P10 | n40 | large | -0.0573 | -0.0581 | -0.0008 | 0.0633 | 0.9655 | 0.0045 | 0.0300 | 1.138 | 0.1395 | 0.563 | 0.022 | 13.6 | 0.914 | 0.9195 | n/a | n/a | n/a |
| P10 | n40 | carries | 0.2741 | 0.2753 | 0.0012 | 0.0377 | 0.9580 | 0.0090 | 0.0330 | 1.066 | 0.0819 | 0.596 | 0.007 | 14.2 | 0.956 | 0.9260 | 8.1 | n/a | n/a |
| P10 | n40 | depends | 0.2000 | 0.2012 | 0.0012 | 0.0373 | 0.9515 | 0.0075 | 0.0410 | 1.087 | 0.0815 | 0.556 | 0.008 | 14.1 | 1.015 | 0.9260 | 8.1 | n/a | n/a |
| P10 | n40 | carried_margin | 0.3608 | 0.3596 | -0.0012 | 0.0710 | 0.9370 | 0.0025 | 0.0605 | 1.056 | 0.1488 | 0.162 | 0.166 | 11.5 | 1.094 | 0.8585 | n/a | n/a | n/a |
| P10 | n40 | own_margin | 1.8041 | 1.7998 | -0.0043 | 0.2436 | 0.9310 | 0.0090 | 0.0600 | 0.981 | 0.4938 | 0.164 | 0.260 | 10.2 | 1.142 | 0.8320 | n/a | n/a | n/a |
| P10 | n40 | kappa | 0.6620 | 0.6601 | -0.0019 | 0.0585 | 0.9450 | 0.0475 | 0.0075 | 1.020 | 0.1234 | 0.165 | 0.040 | 14.3 | 1.028 | 0.8950 | 6.4 | n/a | n/a |
| P10 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4177 | 0.0004 | 0.0543 | 0.9165 | 0.0695 | 0.0140 | 0.983 | 0.1293 | 0.122 | 0.669 | 6.0 | 1.196 | 0.6040 | n/a | n/a | n/a |
| P10 | n40 | carried_added | 0.5450 | 0.5434 | -0.0016 | 0.0884 | 0.9230 | 0.0030 | 0.0740 | 1.035 | 0.1839 | 0.164 | 0.066 | 13.7 | 1.178 | 0.8735 | n/a | n/a | n/a |
| P10 | n40 | pooled_retention | 0.2741 | 0.2738 | -0.0003 | 0.0268 | 0.8820 | 0.0020 | 0.1160 | 1.068 | 0.0585 | 0.735 | 0.000 | 15.0 | 2.326 | 0.8730 | 8.2 | n/a | n/a |
| P10 | n80 | large | 1.5193 | 1.5147 | -0.0047 | 0.3006 | 0.9375 | 0.0050 | 0.0575 | 1.021 | 0.6770 | 0.217 | 0.327 | 9.3 | 1.081 | 0.8145 | n/a | n/a | n/a |
| P10 | n80 | carries | 0.2149 | 0.2162 | 0.0012 | 0.0337 | 0.9480 | 0.0030 | 0.0490 | 1.192 | 0.0760 | 0.643 | 0.031 | 13.7 | 1.013 | 0.9205 | 8.1 | n/a | n/a |
| P10 | n80 | depends | 0.2000 | 0.2011 | 0.0011 | 0.0314 | 0.9515 | 0.0035 | 0.0450 | 1.209 | 0.0708 | 0.639 | 0.035 | 13.5 | 1.082 | 0.9255 | 7.9 | n/a | n/a |
| P10 | n80 | carried_margin | 1.9374 | 1.9324 | -0.0050 | 0.3378 | 0.9370 | 0.0065 | 0.0565 | 1.002 | 0.7632 | 0.138 | 0.426 | 8.5 | 1.084 | 0.7870 | n/a | n/a | n/a |
| P10 | n80 | own_margin | 9.6872 | 9.6751 | -0.0121 | 1.3483 | 0.9205 | 0.0240 | 0.0555 | 0.989 | 3.5041 | 0.137 | 0.621 | 6.5 | 1.176 | 0.6925 | n/a | n/a | n/a |
| P10 | n80 | kappa | 0.9132 | 0.9125 | -0.0006 | 0.0156 | 0.9340 | 0.0575 | 0.0085 | 1.024 | 0.0334 | 0.140 | 0.257 | 10.3 | 1.123 | 0.8425 | 6.2 | n/a | n/a |
| P10 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4178 | 0.0003 | 0.0543 | 0.9140 | 0.0720 | 0.0140 | 0.980 | 0.1292 | 0.125 | 0.670 | 6.0 | 1.210 | 0.6025 | n/a | n/a | n/a |
| P10 | n80 | carried_added | 2.1216 | 2.1162 | -0.0054 | 0.3600 | 0.9370 | 0.0055 | 0.0575 | 1.002 | 0.7850 | 0.138 | 0.345 | 9.4 | 1.085 | 0.8105 | n/a | n/a | n/a |
| P10 | n80 | pooled_retention | 0.2149 | 0.2147 | -0.0002 | 0.0210 | 0.8830 | 0.0025 | 0.1145 | 1.067 | 0.0459 | 0.816 | 0.000 | 15.0 | 2.309 | 0.8745 | 8.0 | n/a | n/a |
| P10 | n160 | large | 3.8799 | 3.8789 | -0.0010 | 0.4604 | 0.9400 | 0.0035 | 0.0565 | 1.125 | 1.0250 | 0.567 | 0.009 | 14.4 | 1.064 | 0.9010 | n/a | n/a | n/a |
| P10 | n160 | carries | 0.2068 | 0.2079 | 0.0011 | 0.0320 | 0.9135 | 0.0010 | 0.0855 | 1.164 | 0.0699 | 0.590 | 0.009 | 14.6 | 1.422 | 0.8855 | 16.2 | n/a | n/a |
| P10 | n160 | depends | 0.2000 | 0.2011 | 0.0011 | 0.0307 | 0.9170 | 0.0010 | 0.0820 | 1.171 | 0.0669 | 0.594 | 0.010 | 14.5 | 1.526 | 0.8890 | 15.7 | n/a | n/a |
| P10 | n160 | carried_margin | 4.2980 | 4.2967 | -0.0014 | 0.4806 | 0.9330 | 0.0040 | 0.0630 | 1.099 | 1.0592 | 0.521 | 0.012 | 14.4 | 1.110 | 0.8930 | n/a | n/a | n/a |
| P10 | n160 | own_margin | 21.4901 | 21.5116 | 0.0215 | 1.2750 | 0.9565 | 0.0365 | 0.0070 | 1.251 | 3.0042 | 0.514 | 0.131 | 11.8 | 0.977 | 0.9040 | n/a | n/a | n/a |
| P10 | n160 | kappa | 0.9589 | 0.9593 | 0.0004 | 0.0053 | 0.9075 | 0.0845 | 0.0080 | 1.053 | 0.0117 | 0.526 | 0.003 | 14.9 | 1.398 | 0.8890 | 8.5 | n/a | n/a |
| P10 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4177 | 0.0004 | 0.0543 | 0.9145 | 0.0715 | 0.0140 | 0.982 | 0.1290 | 0.123 | 0.672 | 6.0 | 1.226 | 0.6035 | n/a | n/a | n/a |
| P10 | n160 | carried_added | 4.4822 | 4.4804 | -0.0018 | 0.5143 | 0.9300 | 0.0030 | 0.0670 | 1.091 | 1.1302 | 0.522 | 0.011 | 14.5 | 1.153 | 0.8870 | n/a | n/a | n/a |
| P10 | n160 | pooled_retention | 0.2068 | 0.2066 | -0.0002 | 0.0202 | 0.8820 | 0.0025 | 0.1155 | 1.069 | 0.0439 | 0.551 | 0.000 | 15.1 | 2.302 | 0.8755 | 16.2 | n/a | n/a |
| P10 | n320 | large | 4.5814 | 4.5739 | -0.0075 | 0.5257 | 0.9320 | 0.0040 | 0.0640 | 1.140 | 1.1834 | 0.572 | 0.005 | 14.6 | 1.156 | 0.9020 | n/a | n/a | n/a |
| P10 | n320 | carries | 0.2059 | 0.2067 | 0.0008 | 0.0316 | 0.9070 | 0.0010 | 0.0920 | 1.154 | 0.0690 | 0.591 | 0.010 | 14.7 | 1.421 | 0.8870 | 17.5 | n/a | n/a |
| P10 | n320 | depends | 0.2000 | 0.2008 | 0.0008 | 0.0305 | 0.9090 | 0.0010 | 0.0900 | 1.160 | 0.0665 | 0.588 | 0.011 | 14.7 | 1.576 | 0.8885 | 17.0 | n/a | n/a |
| P10 | n320 | carried_margin | 4.9995 | 4.9916 | -0.0079 | 0.5412 | 0.9300 | 0.0035 | 0.0665 | 1.123 | 1.2142 | 0.581 | 0.004 | 14.7 | 1.182 | 0.8980 | n/a | n/a | n/a |
| P10 | n320 | own_margin | 24.9973 | 25.0212 | 0.0239 | 1.3371 | 0.9520 | 0.0400 | 0.0080 | 1.291 | 3.1984 | 0.569 | 0.089 | 12.6 | 0.987 | 0.9115 | n/a | n/a | n/a |
| P10 | n320 | kappa | 0.9645 | 0.9648 | 0.0003 | 0.0045 | 0.9040 | 0.0890 | 0.0070 | 1.062 | 0.0100 | 0.577 | 0.001 | 15.0 | 1.515 | 0.8890 | 8.6 | n/a | n/a |
| P10 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4177 | 0.0004 | 0.0543 | 0.9165 | 0.0695 | 0.0140 | 0.982 | 0.1288 | 0.123 | 0.674 | 6.0 | 1.203 | 0.6025 | n/a | n/a | n/a |
| P10 | n320 | carried_added | 5.1837 | 5.1754 | -0.0083 | 0.5760 | 0.9220 | 0.0035 | 0.0745 | 1.113 | 1.2848 | 0.580 | 0.003 | 14.8 | 1.237 | 0.8935 | n/a | n/a | n/a |
| P10 | n320 | pooled_retention | 0.2059 | 0.2056 | -0.0002 | 0.0201 | 0.8835 | 0.0025 | 0.1140 | 1.068 | 0.0436 | 0.536 | 0.000 | 15.1 | 2.284 | 0.8755 | 17.3 | n/a | n/a |
| P10 | h2 | large | -0.0724 | -0.0722 | 0.0002 | 0.0508 | 0.9150 | 0.0595 | 0.0255 | 1.003 | 0.1265 | 0.139 | 0.660 | 6.1 | 1.185 | 0.6095 | n/a | 1.000 | 0.9150 |
| P10 | h2 | carries | 0.2770 | 0.2765 | -0.0005 | 0.0256 | 0.8810 | 0.0035 | 0.1155 | 1.051 | 0.0555 | 0.568 | 0.000 | 15.1 | 2.180 | 0.8720 | 115.4 | 1.000 | 0.8810 |
| P10 | h2 | depends | 0.2000 | 0.2000 | -0.0000 | 0.0110 | 0.8970 | 0.0005 | 0.1025 | 1.134 | 0.0240 | 0.569 | 0.000 | 15.2 | 1.740 | 0.8825 | 53.8 | 1.000 | 0.8970 |
| P10 | h2 | carried_margin | 0.3459 | 0.3455 | -0.0004 | 0.0134 | 0.9160 | 0.0010 | 0.0830 | 1.194 | 0.0305 | 0.496 | 0.000 | 15.3 | 1.315 | 0.8965 | n/a | 1.000 | 0.9160 |
| P10 | h2 | own_margin | 1.7295 | 1.7293 | -0.0002 | 0.0321 | 0.9160 | 0.0790 | 0.0050 | 1.045 | 0.0684 | 0.442 | 0.004 | 15.1 | 1.274 | 0.8775 | n/a | 1.000 | 0.9160 |
| P10 | h2 | kappa | 0.6525 | 0.6566 | 0.0041 | 0.0405 | 0.8720 | 0.1130 | 0.0150 | 0.973 | 0.0873 | 0.508 | 0.000 | 15.1 | 1.964 | 0.8740 | 10.0 | 1.000 | 0.8720 |
| P10 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4177 | 0.0006 | 0.0543 | 0.9145 | 0.0710 | 0.0145 | 0.981 | 0.1288 | 0.121 | 0.673 | 6.0 | 1.203 | 0.6005 | n/a | 1.000 | 0.9145 |
| P10 | h2 | carried_added | 0.5301 | 0.5293 | -0.0008 | 0.0519 | 0.8825 | 0.0020 | 0.1155 | 1.059 | 0.1124 | 0.501 | 0.000 | 15.1 | 2.315 | 0.8740 | n/a | 1.000 | 0.8825 |
| P10 | h2 | pooled_retention | 0.2770 | 0.2767 | -0.0003 | 0.0270 | 0.8825 | 0.0020 | 0.1155 | 1.059 | 0.0585 | 0.556 | 0.000 | 15.1 | 2.344 | 0.8755 | 114.8 | 1.000 | 0.8825 |
| P10 | h5 | large | 0.5690 | 0.5688 | -0.0002 | 0.0752 | 0.9295 | 0.0040 | 0.0665 | 1.145 | 0.1700 | 0.219 | 0.177 | 11.4 | 1.161 | 0.8335 | n/a | 0.991 | 0.9290 |
| P10 | h5 | carries | 0.2288 | 0.2285 | -0.0002 | 0.0229 | 0.8830 | 0.0020 | 0.1150 | 1.073 | 0.0498 | 0.597 | 0.000 | 15.1 | 2.322 | 0.8755 | 147.8 | 0.991 | 0.8815 |
| P10 | h5 | depends | 0.2000 | 0.2000 | -0.0000 | 0.0174 | 0.8835 | 0.0015 | 0.1150 | 1.093 | 0.0378 | 0.599 | 0.000 | 15.1 | 2.379 | 0.8765 | 77.5 | 0.991 | 0.8820 |
| P10 | h5 | carried_margin | 0.9874 | 0.9863 | -0.0010 | 0.0751 | 0.8860 | 0.0010 | 0.1130 | 1.083 | 0.1637 | 0.561 | 0.000 | 15.2 | 2.089 | 0.8775 | n/a | 0.991 | 0.8850 |
| P10 | h5 | own_margin | 4.9368 | 4.9369 | 0.0002 | 0.0602 | 0.9380 | 0.0555 | 0.0065 | 1.165 | 0.1386 | 0.539 | 0.060 | 13.2 | 1.075 | 0.8790 | n/a | 0.991 | 0.9370 |
| P10 | h5 | kappa | 0.8428 | 0.8447 | 0.0020 | 0.0183 | 0.8760 | 0.1110 | 0.0130 | 0.973 | 0.0396 | 0.560 | 0.000 | 15.1 | 1.990 | 0.8745 | 10.0 | 0.991 | 0.8745 |
| P10 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4175 | 0.0008 | 0.0542 | 0.9020 | 0.0835 | 0.0145 | 1.035 | 0.1355 | 0.163 | 0.648 | 6.0 | 1.317 | 0.6055 | n/a | 0.991 | 0.9020 |
| P10 | h5 | carried_added | 1.1715 | 1.1700 | -0.0015 | 0.1143 | 0.8840 | 0.0020 | 0.1140 | 1.068 | 0.2486 | 0.569 | 0.000 | 15.1 | 2.303 | 0.8770 | n/a | 0.991 | 0.8825 |
| P10 | h5 | pooled_retention | 0.2288 | 0.2285 | -0.0003 | 0.0223 | 0.8830 | 0.0025 | 0.1145 | 1.066 | 0.0485 | 0.567 | 0.000 | 15.1 | 2.344 | 0.8775 | 149.3 | 0.991 | 0.8815 |
| P10 | h10 | large | 1.7243 | 1.6112 | -0.1131 | 0.1253 | 0.7555 | 0.0000 | 0.2445 | 1.429 | 0.3030 | 0.387 | 0.006 | 15.1 | 2.220 | 0.7360 | n/a | 0.197 | 0.8895 |
| P10 | h10 | carries | 0.2135 | 0.1992 | -0.0144 | 0.0141 | 0.7550 | 0.0000 | 0.2450 | 1.561 | 0.0367 | 0.577 | 0.001 | 15.1 | 2.687 | 0.7510 | 121.7 | 0.197 | 0.8845 |
| P10 | h10 | depends | 0.2000 | 0.1875 | -0.0125 | 0.0123 | 0.7555 | 0.0000 | 0.2445 | 1.572 | 0.0322 | 0.582 | 0.002 | 15.1 | 2.793 | 0.7520 | 111.2 | 0.197 | 0.8860 |
| P10 | h10 | carried_margin | 2.1426 | 2.0128 | -0.1298 | 0.1257 | 0.7555 | 0.0000 | 0.2445 | 1.571 | 0.3275 | 0.539 | 0.000 | 15.1 | 2.629 | 0.7495 | n/a | 0.197 | 0.8850 |
| P10 | h10 | own_margin | 10.7131 | 10.7386 | 0.0255 | 0.0965 | 0.9620 | 0.0255 | 0.0125 | 1.461 | 0.2157 | 0.497 | 0.283 | 10.3 | 0.938 | 0.8750 | n/a | 0.197 | 0.9555 |
| P10 | h10 | kappa | 0.9208 | 0.9282 | 0.0073 | 0.0071 | 0.7585 | 0.2415 | 0.0000 | 1.381 | 0.0184 | 0.550 | 0.000 | 15.2 | 2.380 | 0.7520 | 11.7 | 0.197 | 0.8765 |
| P10 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4016 | 0.0167 | 0.0438 | 0.8560 | 0.1395 | 0.0045 | 0.783 | 0.0842 | 0.030 | 0.609 | 8.1 | 1.512 | 0.5730 | n/a | 0.197 | 0.8880 |
| P10 | h10 | carried_added | 2.3268 | 2.1697 | -0.1571 | 0.1513 | 0.7535 | 0.0000 | 0.2465 | 1.567 | 0.3945 | 0.539 | 0.000 | 15.2 | 2.733 | 0.7495 | n/a | 0.197 | 0.8830 |
| P10 | h10 | pooled_retention | 0.2135 | 0.1991 | -0.0145 | 0.0137 | 0.7530 | 0.0000 | 0.2470 | 1.586 | 0.0361 | 0.544 | 0.000 | 15.1 | 2.776 | 0.7490 | 123.9 | 0.197 | 0.8825 |
| P11 | n20 | large | -0.4093 | -0.4116 | -0.0022 | 0.0490 | 0.8945 | 0.1035 | 0.0020 | 1.082 | 0.1056 | 0.580 | 0.019 | 13.8 | 1.342 | 0.8470 | n/a | n/a | n/a |
| P11 | n20 | carries | 0.3104 | 0.3097 | -0.0006 | 0.0330 | 0.8940 | 0.0010 | 0.1050 | 1.154 | 0.0740 | 0.595 | 0.025 | 13.7 | 1.542 | 0.8645 | 9.7 | n/a | n/a |
| P11 | n20 | depends | 0.0000 | -0.0000 | -0.0000 | 0.0709 | 0.9430 | 0.0420 | 0.0150 | 1.006 | 0.1492 | 0.550 | 0.000 | 15.2 | 1.025 | 0.8940 | 14.3 | n/a | n/a |
| P11 | n20 | carried_margin | 0.0000 | -0.0008 | -0.0008 | 0.0294 | 0.9485 | 0.0425 | 0.0090 | 1.016 | 0.0623 | 0.551 | 0.000 | 15.2 | 1.011 | 0.8940 | n/a | n/a | n/a |
| P11 | n20 | own_margin | 0.4093 | 0.4107 | 0.0014 | 0.0286 | 0.9100 | 0.0010 | 0.0890 | 1.287 | 0.0645 | 0.549 | 0.122 | 12.0 | 1.268 | 0.8380 | n/a | n/a | n/a |
| P11 | n20 | kappa | 0.0000 | -0.0019 | -0.0019 | 0.1568 | 0.9115 | 0.0645 | 0.0240 | 0.922 | 0.3248 | 0.551 | 0.000 | 15.3 | 1.227 | 0.8940 | 7.2 | n/a | n/a |
| P11 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9100 | 0.0890 | 0.0010 | 1.287 | 0.0645 | 0.549 | 0.122 | 12.0 | 1.268 | 0.8380 | n/a | n/a | n/a |
| P11 | n20 | carried_added | 0.1842 | 0.1843 | 0.0001 | 0.0256 | 0.9190 | 0.0010 | 0.0800 | 1.088 | 0.0544 | 0.549 | 0.000 | 15.2 | 1.271 | 0.9045 | n/a | n/a | n/a |
| P11 | n20 | pooled_retention | 0.3104 | 0.3112 | 0.0008 | 0.0315 | 0.8780 | 0.0030 | 0.1190 | 0.995 | 0.0660 | 0.538 | 0.000 | 15.1 | 2.262 | 0.8690 | 10.0 | n/a | n/a |
| P11 | n40 | large | -0.4093 | -0.4115 | -0.0022 | 0.0487 | 0.9010 | 0.0965 | 0.0025 | 1.111 | 0.1067 | 0.562 | 0.018 | 13.8 | 1.330 | 0.8580 | n/a | n/a | n/a |
| P11 | n40 | carries | 0.0945 | 0.0949 | 0.0004 | 0.0127 | 0.9580 | 0.0060 | 0.0360 | 1.099 | 0.0279 | 0.594 | 0.003 | 14.4 | 0.971 | 0.9270 | 9.4 | n/a | n/a |
| P11 | n40 | depends | 0.0000 | 0.0003 | 0.0003 | 0.0168 | 0.9525 | 0.0360 | 0.0115 | 1.016 | 0.0359 | 0.585 | 0.000 | 15.2 | 0.983 | 0.9065 | 9.6 | n/a | n/a |
| P11 | n40 | carried_margin | 0.0000 | -0.0008 | -0.0008 | 0.0297 | 0.9515 | 0.0435 | 0.0050 | 1.036 | 0.0634 | 0.579 | 0.001 | 15.2 | 0.995 | 0.9065 | n/a | n/a | n/a |
| P11 | n40 | own_margin | 1.7645 | 1.7667 | 0.0022 | 0.1846 | 0.9410 | 0.0080 | 0.0510 | 1.043 | 0.3993 | 0.604 | 0.005 | 14.4 | 1.065 | 0.9130 | n/a | n/a | n/a |
| P11 | n40 | kappa | 0.0000 | -0.0029 | -0.0029 | 0.1615 | 0.9245 | 0.0630 | 0.0125 | 0.970 | 0.3386 | 0.578 | 0.000 | 15.2 | 1.151 | 0.9065 | 6.9 | n/a | n/a |
| P11 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9105 | 0.0885 | 0.0010 | 1.287 | 0.0646 | 0.549 | 0.120 | 12.0 | 1.285 | 0.8380 | n/a | n/a | n/a |
| P11 | n40 | carried_added | 0.1842 | 0.1844 | 0.0002 | 0.0266 | 0.9435 | 0.0030 | 0.0535 | 1.069 | 0.0566 | 0.581 | 0.001 | 15.1 | 1.038 | 0.9245 | n/a | n/a | n/a |
| P11 | n40 | pooled_retention | 0.0945 | 0.0948 | 0.0002 | 0.0096 | 0.8765 | 0.0035 | 0.1200 | 0.991 | 0.0201 | 0.526 | 0.000 | 15.1 | 2.198 | 0.8675 | 9.3 | n/a | n/a |
| P11 | n80 | large | -0.4093 | -0.4112 | -0.0019 | 0.0470 | 0.8920 | 0.1075 | 0.0005 | 1.123 | 0.1036 | 0.569 | 0.044 | 13.3 | 1.558 | 0.8425 | n/a | n/a | n/a |
| P11 | n80 | carries | 0.0189 | 0.0190 | 0.0002 | 0.0029 | 0.9515 | 0.0020 | 0.0465 | 1.221 | 0.0067 | 0.592 | 0.048 | 13.3 | 0.989 | 0.9195 | 12.5 | n/a | n/a |
| P11 | n80 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0028 | 0.9385 | 0.0600 | 0.0015 | 1.094 | 0.0061 | 0.582 | 0.018 | 14.1 | 1.196 | 0.8940 | 12.1 | n/a | n/a |
| P11 | n80 | carried_margin | 0.0000 | -0.0005 | -0.0005 | 0.0265 | 0.9345 | 0.0625 | 0.0030 | 1.077 | 0.0581 | 0.585 | 0.018 | 14.1 | 1.141 | 0.8940 | n/a | n/a | n/a |
| P11 | n80 | own_margin | 9.5794 | 9.5796 | 0.0002 | 0.7563 | 0.9635 | 0.0150 | 0.0215 | 1.258 | 1.7226 | 0.586 | 0.124 | 12.0 | 0.938 | 0.9130 | n/a | n/a | n/a |
| P11 | n80 | kappa | 0.0000 | 0.0041 | 0.0041 | 0.1420 | 0.9235 | 0.0715 | 0.0050 | 1.027 | 0.3063 | 0.585 | 0.013 | 14.1 | 1.242 | 0.8940 | 7.8 | n/a | n/a |
| P11 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9125 | 0.0865 | 0.0010 | 1.287 | 0.0647 | 0.545 | 0.120 | 12.0 | 1.254 | 0.8355 | n/a | n/a | n/a |
| P11 | n80 | carried_added | 0.1842 | 0.1847 | 0.0005 | 0.0231 | 0.9410 | 0.0020 | 0.0570 | 1.126 | 0.0517 | 0.583 | 0.026 | 13.8 | 1.074 | 0.9030 | n/a | n/a | n/a |
| P11 | n80 | pooled_retention | 0.0189 | 0.0189 | 0.0000 | 0.0019 | 0.8780 | 0.0035 | 0.1185 | 0.995 | 0.0040 | 0.479 | 0.000 | 15.1 | 2.207 | 0.8690 | 12.6 | n/a | n/a |
| P11 | n160 | large | -0.4093 | -0.4113 | -0.0020 | 0.0458 | 0.8795 | 0.1205 | 0.0000 | 1.125 | 0.1004 | 0.557 | 0.035 | 13.4 | 1.677 | 0.8390 | n/a | n/a | n/a |
| P11 | n160 | carries | 0.0083 | 0.0084 | 0.0001 | 0.0013 | 0.9190 | 0.0010 | 0.0800 | 1.131 | 0.0028 | 0.591 | 0.010 | 14.5 | 1.277 | 0.8850 | 16.2 | n/a | n/a |
| P11 | n160 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0012 | 0.9135 | 0.0860 | 0.0005 | 1.094 | 0.0024 | 0.584 | 0.003 | 14.9 | 1.449 | 0.8905 | 15.8 | n/a | n/a |
| P11 | n160 | carried_margin | 0.0000 | -0.0006 | -0.0006 | 0.0248 | 0.9140 | 0.0830 | 0.0030 | 1.044 | 0.0528 | 0.587 | 0.003 | 14.9 | 1.310 | 0.8905 | n/a | n/a | n/a |
| P11 | n160 | own_margin | 21.9134 | 21.8705 | -0.0428 | 1.2813 | 0.9630 | 0.0320 | 0.0050 | 1.244 | 2.9780 | 0.581 | 0.076 | 12.8 | 0.935 | 0.9175 | n/a | n/a | n/a |
| P11 | n160 | kappa | 0.0000 | 0.0056 | 0.0056 | 0.1328 | 0.9080 | 0.0850 | 0.0070 | 0.989 | 0.2831 | 0.585 | 0.002 | 15.0 | 1.416 | 0.8905 | 8.5 | n/a | n/a |
| P11 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9105 | 0.0885 | 0.0010 | 1.287 | 0.0646 | 0.550 | 0.123 | 12.0 | 1.258 | 0.8360 | n/a | n/a | n/a |
| P11 | n160 | carried_added | 0.1842 | 0.1846 | 0.0004 | 0.0215 | 0.9275 | 0.0040 | 0.0685 | 1.054 | 0.0461 | 0.576 | 0.005 | 14.7 | 1.179 | 0.8865 | n/a | n/a | n/a |
| P11 | n160 | pooled_retention | 0.0083 | 0.0084 | 0.0000 | 0.0008 | 0.8775 | 0.0035 | 0.1190 | 0.994 | 0.0018 | 0.529 | 0.000 | 15.1 | 2.257 | 0.8695 | 16.2 | n/a | n/a |
| P11 | n320 | large | -0.4093 | -0.4113 | -0.0020 | 0.0457 | 0.8785 | 0.1210 | 0.0005 | 1.126 | 0.1002 | 0.554 | 0.033 | 13.4 | 1.698 | 0.8400 | n/a | n/a | n/a |
| P11 | n320 | carries | 0.0072 | 0.0073 | 0.0001 | 0.0012 | 0.9140 | 0.0020 | 0.0840 | 1.097 | 0.0024 | 0.586 | 0.010 | 14.7 | 1.331 | 0.8840 | 17.2 | n/a | n/a |
| P11 | n320 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0010 | 0.9090 | 0.0910 | 0.0000 | 1.091 | 0.0021 | 0.577 | 0.002 | 15.0 | 1.551 | 0.8855 | 16.7 | n/a | n/a |
| P11 | n320 | carried_margin | 0.0000 | -0.0005 | -0.0005 | 0.0245 | 0.9110 | 0.0860 | 0.0030 | 1.042 | 0.0525 | 0.578 | 0.002 | 15.0 | 1.392 | 0.8855 | n/a | n/a | n/a |
| P11 | n320 | own_margin | 25.2643 | 25.2177 | -0.0467 | 1.3945 | 0.9590 | 0.0320 | 0.0090 | 1.231 | 3.2829 | 0.584 | 0.083 | 12.7 | 0.945 | 0.9030 | n/a | n/a | n/a |
| P11 | n320 | kappa | 0.0000 | 0.0062 | 0.0062 | 0.1311 | 0.9065 | 0.0855 | 0.0080 | 0.982 | 0.2783 | 0.580 | 0.001 | 15.1 | 1.488 | 0.8855 | 8.6 | n/a | n/a |
| P11 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9090 | 0.0900 | 0.0010 | 1.286 | 0.0645 | 0.548 | 0.124 | 12.0 | 1.253 | 0.8350 | n/a | n/a | n/a |
| P11 | n320 | carried_added | 0.1842 | 0.1846 | 0.0004 | 0.0213 | 0.9215 | 0.0050 | 0.0735 | 1.038 | 0.0449 | 0.578 | 0.003 | 14.8 | 1.163 | 0.8870 | n/a | n/a | n/a |
| P11 | n320 | pooled_retention | 0.0072 | 0.0073 | 0.0000 | 0.0007 | 0.8765 | 0.0035 | 0.1200 | 0.986 | 0.0015 | 0.513 | 0.000 | 15.1 | 2.294 | 0.8675 | 17.3 | n/a | n/a |
| P11 | h2 | large | -0.4093 | -0.4112 | -0.0019 | 0.0449 | 0.8645 | 0.1350 | 0.0005 | 1.103 | 0.0973 | 0.553 | 0.040 | 13.5 | 2.047 | 0.8275 | n/a | 1.000 | 0.8645 |
| P11 | h2 | carries | 0.0965 | 0.0966 | 0.0002 | 0.0093 | 0.8760 | 0.0045 | 0.1195 | 0.980 | 0.0192 | 0.577 | 0.000 | 15.1 | 2.136 | 0.8665 | 121.3 | 1.000 | 0.8760 |
| P11 | h2 | depends | 0.0000 | -0.0005 | -0.0005 | 0.0133 | 0.8790 | 0.1185 | 0.0025 | 0.999 | 0.0271 | 0.580 | 0.000 | 15.1 | 2.482 | 0.8695 | 55.4 | 1.000 | 0.8790 |
| P11 | h2 | carried_margin | 0.0000 | -0.0005 | -0.0005 | 0.0226 | 0.8780 | 0.1185 | 0.0035 | 0.981 | 0.0468 | 0.583 | 0.000 | 15.1 | 2.211 | 0.8695 | n/a | 1.000 | 0.8780 |
| P11 | h2 | own_margin | 1.7255 | 1.7249 | -0.0006 | 0.0321 | 0.9070 | 0.0850 | 0.0080 | 0.997 | 0.0664 | 0.570 | 0.001 | 15.2 | 1.300 | 0.8755 | n/a | 1.000 | 0.9070 |
| P11 | h2 | kappa | 0.0000 | 0.0092 | 0.0092 | 0.1202 | 0.8715 | 0.1140 | 0.0145 | 0.901 | 0.2494 | 0.581 | 0.000 | 15.1 | 1.946 | 0.8695 | 10.0 | 1.000 | 0.8715 |
| P11 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9090 | 0.0900 | 0.0010 | 1.284 | 0.0647 | 0.549 | 0.122 | 12.0 | 1.262 | 0.8350 | n/a | 1.000 | 0.9090 |
| P11 | h2 | carried_added | 0.1842 | 0.1847 | 0.0005 | 0.0188 | 0.8775 | 0.0035 | 0.1190 | 0.986 | 0.0389 | 0.582 | 0.000 | 15.1 | 2.229 | 0.8695 | n/a | 1.000 | 0.8775 |
| P11 | h2 | pooled_retention | 0.0965 | 0.0967 | 0.0002 | 0.0098 | 0.8765 | 0.0035 | 0.1200 | 0.982 | 0.0203 | 0.583 | 0.000 | 15.1 | 2.301 | 0.8680 | 122.5 | 1.000 | 0.8765 |
| P11 | h5 | large | -0.4093 | -0.4112 | -0.0019 | 0.0448 | 0.8650 | 0.1345 | 0.0005 | 1.150 | 0.0990 | 0.557 | 0.047 | 13.1 | 2.079 | 0.8305 | n/a | 0.996 | 0.8640 |
| P11 | h5 | carries | 0.0361 | 0.0362 | 0.0001 | 0.0038 | 0.8760 | 0.0040 | 0.1200 | 0.988 | 0.0078 | 0.593 | 0.000 | 15.1 | 2.292 | 0.8685 | 159.3 | 0.996 | 0.8755 |
| P11 | h5 | depends | 0.0000 | -0.0002 | -0.0002 | 0.0046 | 0.8795 | 0.1175 | 0.0030 | 0.996 | 0.0096 | 0.574 | 0.000 | 15.1 | 2.414 | 0.8710 | 78.1 | 0.996 | 0.8790 |
| P11 | h5 | carried_margin | 0.0000 | -0.0006 | -0.0006 | 0.0226 | 0.8785 | 0.1175 | 0.0040 | 0.985 | 0.0472 | 0.573 | 0.000 | 15.1 | 2.223 | 0.8710 | n/a | 0.996 | 0.8780 |
| P11 | h5 | own_margin | 4.9248 | 4.9235 | -0.0013 | 0.0623 | 0.9215 | 0.0730 | 0.0055 | 1.052 | 0.1367 | 0.599 | 0.042 | 13.7 | 1.318 | 0.8650 | n/a | 0.996 | 0.9210 |
| P11 | h5 | kappa | 0.0000 | 0.0088 | 0.0088 | 0.1202 | 0.8720 | 0.1145 | 0.0135 | 0.905 | 0.2492 | 0.575 | 0.000 | 15.1 | 1.934 | 0.8710 | 10.1 | 0.996 | 0.8715 |
| P11 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4107 | -0.0014 | 0.0286 | 0.9145 | 0.0850 | 0.0005 | 1.396 | 0.0656 | 0.553 | 0.150 | 11.6 | 1.242 | 0.8375 | n/a | 0.996 | 0.9135 |
| P11 | h5 | carried_added | 0.1842 | 0.1847 | 0.0005 | 0.0187 | 0.8765 | 0.0040 | 0.1195 | 0.989 | 0.0389 | 0.581 | 0.000 | 15.1 | 2.228 | 0.8675 | n/a | 0.996 | 0.8760 |
| P11 | h5 | pooled_retention | 0.0361 | 0.0361 | 0.0001 | 0.0037 | 0.8765 | 0.0040 | 0.1195 | 0.987 | 0.0076 | 0.578 | 0.000 | 15.1 | 2.298 | 0.8695 | 158.3 | 0.996 | 0.8760 |
| P11 | h10 | large | -0.4093 | -0.3802 | 0.0291 | 0.0278 | 0.7025 | 0.2975 | 0.0000 | 1.600 | 0.0699 | 0.573 | 0.024 | 14.4 | 2.879 | 0.6690 | n/a | 0.193 | 0.8530 |
| P11 | h10 | carries | 0.0170 | 0.0159 | -0.0011 | 0.0012 | 0.7605 | 0.0000 | 0.2395 | 1.518 | 0.0029 | 0.552 | 0.000 | 15.2 | 2.674 | 0.7550 | 148.7 | 0.193 | 0.8770 |
| P11 | h10 | depends | 0.0000 | 0.0013 | 0.0013 | 0.0014 | 0.7615 | 0.2385 | 0.0000 | 1.511 | 0.0035 | 0.540 | 0.000 | 15.2 | 2.884 | 0.7590 | 129.1 | 0.193 | 0.8780 |
| P11 | h10 | carried_margin | 0.0000 | 0.0145 | 0.0145 | 0.0150 | 0.7620 | 0.2380 | 0.0000 | 1.504 | 0.0376 | 0.541 | 0.000 | 15.2 | 2.724 | 0.7590 | n/a | 0.193 | 0.8775 |
| P11 | h10 | own_margin | 10.6772 | 10.7021 | 0.0249 | 0.0735 | 0.9640 | 0.0320 | 0.0040 | 1.711 | 0.1801 | 0.592 | 0.218 | 11.2 | 0.929 | 0.9020 | n/a | 0.193 | 0.9715 |
| P11 | h10 | kappa | 0.0000 | 0.0904 | 0.0904 | 0.0919 | 0.7710 | 0.2290 | 0.0000 | 1.353 | 0.2338 | 0.543 | 0.000 | 15.2 | 2.361 | 0.7590 | 11.6 | 0.193 | 0.8715 |
| P11 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3947 | 0.0146 | 0.0203 | 0.7990 | 0.2010 | 0.0000 | 1.341 | 0.0440 | 0.576 | 0.039 | 13.8 | 1.578 | 0.7145 | n/a | 0.193 | 0.9045 |
| P11 | h10 | carried_added | 0.1842 | 0.1721 | -0.0121 | 0.0124 | 0.7610 | 0.0000 | 0.2390 | 1.526 | 0.0313 | 0.553 | 0.000 | 15.2 | 2.711 | 0.7575 | n/a | 0.193 | 0.8780 |
| P11 | h10 | pooled_retention | 0.0170 | 0.0158 | -0.0011 | 0.0011 | 0.7580 | 0.0000 | 0.2420 | 1.532 | 0.0029 | 0.566 | 0.000 | 15.1 | 2.808 | 0.7550 | 146.3 | 0.193 | 0.8755 |
| P12 | n20 | large | -0.4181 | -0.4205 | -0.0024 | 0.0582 | 0.9185 | 0.0790 | 0.0025 | 1.089 | 0.1226 | 0.276 | 0.145 | 11.1 | 1.232 | 0.8290 | n/a | n/a | n/a |
| P12 | n20 | carries | 0.3058 | 0.3060 | 0.0001 | 0.0338 | 0.8980 | 0.0005 | 0.1015 | 1.120 | 0.0745 | 0.621 | 0.025 | 13.8 | 1.547 | 0.8550 | 8.4 | n/a | n/a |
| P12 | n20 | depends | 0.0000 | -0.0051 | -0.0051 | 0.0788 | 0.9580 | 0.0330 | 0.0090 | 1.004 | 0.1601 | 0.141 | 0.017 | 15.0 | 0.942 | 0.8850 | 9.0 | n/a | n/a |
| P12 | n20 | carried_margin | 0.0000 | -0.0014 | -0.0014 | 0.0325 | 0.9665 | 0.0240 | 0.0095 | 1.019 | 0.0677 | 0.118 | 0.018 | 14.9 | 0.913 | 0.8850 | n/a | n/a | n/a |
| P12 | n20 | own_margin | 0.4181 | 0.4191 | 0.0010 | 0.0532 | 0.9335 | 0.0095 | 0.0570 | 1.069 | 0.1361 | 0.118 | 0.681 | 5.9 | 1.136 | 0.6430 | n/a | n/a | n/a |
| P12 | n20 | kappa | 0.0000 | -0.0119 | -0.0119 | 0.1722 | 0.9285 | 0.0500 | 0.0215 | 0.938 | 0.3538 | 0.117 | 0.017 | 15.0 | 1.104 | 0.8850 | 6.6 | n/a | n/a |
| P12 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4191 | -0.0010 | 0.0532 | 0.9335 | 0.0570 | 0.0095 | 1.069 | 0.1361 | 0.118 | 0.681 | 5.9 | 1.136 | 0.6430 | n/a | n/a | n/a |
| P12 | n20 | carried_added | 0.1842 | 0.1851 | 0.0009 | 0.0296 | 0.9155 | 0.0015 | 0.0830 | 1.044 | 0.0599 | 0.119 | 0.031 | 14.4 | 1.240 | 0.8745 | n/a | n/a | n/a |
| P12 | n20 | pooled_retention | 0.3058 | 0.3074 | 0.0016 | 0.0303 | 0.9030 | 0.0030 | 0.0940 | 1.073 | 0.0658 | 0.772 | 0.000 | 15.0 | 2.131 | 0.8875 | 8.6 | n/a | n/a |
| P12 | n40 | large | -0.4181 | -0.4203 | -0.0022 | 0.0575 | 0.9155 | 0.0825 | 0.0020 | 1.108 | 0.1229 | 0.277 | 0.131 | 11.2 | 1.250 | 0.8445 | n/a | n/a | n/a |
| P12 | n40 | carries | 0.0926 | 0.0934 | 0.0008 | 0.0125 | 0.9650 | 0.0105 | 0.0245 | 1.110 | 0.0277 | 0.603 | 0.006 | 14.2 | 0.911 | 0.9405 | 8.2 | n/a | n/a |
| P12 | n40 | depends | 0.0000 | -0.0007 | -0.0007 | 0.0181 | 0.9520 | 0.0350 | 0.0130 | 1.025 | 0.0381 | 0.185 | 0.026 | 14.5 | 0.988 | 0.8895 | 8.1 | n/a | n/a |
| P12 | n40 | carried_margin | 0.0000 | -0.0011 | -0.0011 | 0.0326 | 0.9590 | 0.0325 | 0.0085 | 1.044 | 0.0687 | 0.159 | 0.045 | 14.3 | 0.945 | 0.8895 | n/a | n/a | n/a |
| P12 | n40 | own_margin | 1.8041 | 1.8058 | 0.0018 | 0.2358 | 0.9420 | 0.0070 | 0.0510 | 1.041 | 0.4964 | 0.160 | 0.270 | 10.2 | 1.044 | 0.8355 | n/a | n/a | n/a |
| P12 | n40 | kappa | 0.0000 | -0.0117 | -0.0117 | 0.1778 | 0.9395 | 0.0505 | 0.0100 | 0.985 | 0.3678 | 0.159 | 0.037 | 14.3 | 1.065 | 0.8895 | 6.3 | n/a | n/a |
| P12 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4192 | -0.0011 | 0.0532 | 0.9320 | 0.0585 | 0.0095 | 1.069 | 0.1357 | 0.117 | 0.680 | 5.9 | 1.139 | 0.6455 | n/a | n/a | n/a |
| P12 | n40 | carried_added | 0.1842 | 0.1854 | 0.0012 | 0.0304 | 0.9420 | 0.0050 | 0.0530 | 1.029 | 0.0625 | 0.162 | 0.062 | 13.8 | 1.048 | 0.8915 | n/a | n/a | n/a |
| P12 | n40 | pooled_retention | 0.0926 | 0.0932 | 0.0005 | 0.0092 | 0.9015 | 0.0040 | 0.0945 | 1.068 | 0.0200 | 0.759 | 0.000 | 15.0 | 2.131 | 0.8880 | 8.2 | n/a | n/a |
| P12 | n80 | large | -0.4181 | -0.4205 | -0.0024 | 0.0532 | 0.8985 | 0.0995 | 0.0020 | 1.132 | 0.1131 | 0.390 | 0.102 | 11.9 | 1.427 | 0.8360 | n/a | n/a | n/a |
| P12 | n80 | carries | 0.0187 | 0.0190 | 0.0003 | 0.0031 | 0.9565 | 0.0045 | 0.0390 | 1.108 | 0.0067 | 0.632 | 0.030 | 13.6 | 0.947 | 0.9255 | 8.0 | n/a | n/a |
| P12 | n80 | depends | 0.0000 | -0.0004 | -0.0004 | 0.0036 | 0.9515 | 0.0460 | 0.0025 | 1.120 | 0.0077 | 0.144 | 0.247 | 10.6 | 1.085 | 0.8505 | 7.7 | n/a | n/a |
| P12 | n80 | carried_margin | 0.0000 | -0.0014 | -0.0014 | 0.0327 | 0.9690 | 0.0255 | 0.0055 | 1.091 | 0.0739 | 0.141 | 0.265 | 10.5 | 0.907 | 0.8505 | n/a | n/a | n/a |
| P12 | n80 | own_margin | 9.6872 | 9.6432 | -0.0440 | 1.3432 | 0.9250 | 0.0195 | 0.0555 | 0.980 | 3.5808 | 0.130 | 0.641 | 6.4 | 1.217 | 0.6960 | n/a | n/a | n/a |
| P12 | n80 | kappa | 0.0000 | -0.0143 | -0.0143 | 0.1787 | 0.9470 | 0.0435 | 0.0095 | 1.059 | 0.3883 | 0.140 | 0.268 | 10.3 | 1.017 | 0.8505 | 6.2 | n/a | n/a |
| P12 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4191 | -0.0010 | 0.0532 | 0.9325 | 0.0575 | 0.0100 | 1.068 | 0.1359 | 0.116 | 0.679 | 5.9 | 1.138 | 0.6445 | n/a | n/a | n/a |
| P12 | n80 | carried_added | 0.1842 | 0.1851 | 0.0009 | 0.0312 | 0.9405 | 0.0080 | 0.0515 | 1.036 | 0.0691 | 0.138 | 0.355 | 9.4 | 1.054 | 0.8190 | n/a | n/a | n/a |
| P12 | n80 | pooled_retention | 0.0187 | 0.0188 | 0.0001 | 0.0019 | 0.9005 | 0.0050 | 0.0945 | 1.068 | 0.0040 | 0.821 | 0.000 | 15.0 | 2.115 | 0.8880 | 7.9 | n/a | n/a |
| P12 | n160 | large | -0.4181 | -0.4204 | -0.0023 | 0.0619 | 0.9295 | 0.0680 | 0.0025 | 1.073 | 0.1330 | 0.158 | 0.341 | 8.8 | 1.132 | 0.7830 | n/a | n/a | n/a |
| P12 | n160 | carries | 0.0085 | 0.0086 | 0.0001 | 0.0014 | 0.9225 | 0.0005 | 0.0770 | 1.104 | 0.0029 | 0.603 | 0.009 | 14.6 | 1.281 | 0.8940 | 16.1 | n/a | n/a |
| P12 | n160 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0012 | 0.9335 | 0.0665 | 0.0000 | 1.165 | 0.0025 | 0.512 | 0.004 | 14.9 | 1.363 | 0.8975 | 15.6 | n/a | n/a |
| P12 | n160 | carried_margin | 0.0000 | -0.0013 | -0.0013 | 0.0242 | 0.9335 | 0.0650 | 0.0015 | 1.126 | 0.0534 | 0.518 | 0.004 | 14.9 | 1.113 | 0.8975 | n/a | n/a | n/a |
| P12 | n160 | own_margin | 21.4901 | 21.4718 | -0.0183 | 1.3290 | 0.9490 | 0.0380 | 0.0130 | 1.158 | 2.9838 | 0.522 | 0.129 | 11.9 | 1.007 | 0.8970 | n/a | n/a | n/a |
| P12 | n160 | kappa | 0.0000 | 0.0009 | 0.0009 | 0.1293 | 0.9235 | 0.0665 | 0.0100 | 1.074 | 0.2853 | 0.518 | 0.002 | 14.9 | 1.188 | 0.8975 | 8.4 | n/a | n/a |
| P12 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4191 | -0.0010 | 0.0532 | 0.9320 | 0.0580 | 0.0100 | 1.068 | 0.1351 | 0.118 | 0.677 | 5.9 | 1.157 | 0.6445 | n/a | n/a | n/a |
| P12 | n160 | carried_added | 0.1842 | 0.1852 | 0.0010 | 0.0216 | 0.9350 | 0.0045 | 0.0605 | 1.074 | 0.0468 | 0.517 | 0.007 | 14.6 | 1.126 | 0.8970 | n/a | n/a | n/a |
| P12 | n160 | pooled_retention | 0.0085 | 0.0085 | 0.0000 | 0.0008 | 0.9015 | 0.0040 | 0.0945 | 1.067 | 0.0018 | 0.547 | 0.000 | 15.1 | 2.118 | 0.8870 | 16.3 | n/a | n/a |
| P12 | n320 | large | -0.4181 | -0.4203 | -0.0022 | 0.0634 | 0.9320 | 0.0645 | 0.0035 | 1.074 | 0.1385 | 0.135 | 0.394 | 8.4 | 1.153 | 0.7750 | n/a | n/a | n/a |
| P12 | n320 | carries | 0.0073 | 0.0074 | 0.0001 | 0.0012 | 0.9240 | 0.0005 | 0.0755 | 1.128 | 0.0025 | 0.606 | 0.005 | 14.8 | 1.304 | 0.8965 | 17.3 | n/a | n/a |
| P12 | n320 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0010 | 0.9275 | 0.0720 | 0.0005 | 1.150 | 0.0021 | 0.585 | 0.003 | 15.0 | 1.473 | 0.9010 | 16.8 | n/a | n/a |
| P12 | n320 | carried_margin | 0.0000 | -0.0012 | -0.0012 | 0.0238 | 0.9290 | 0.0675 | 0.0035 | 1.117 | 0.0523 | 0.589 | 0.002 | 15.0 | 1.264 | 0.9010 | n/a | n/a | n/a |
| P12 | n320 | own_margin | 24.9973 | 24.9616 | -0.0357 | 1.3692 | 0.9645 | 0.0320 | 0.0035 | 1.247 | 3.2077 | 0.584 | 0.074 | 12.7 | 0.908 | 0.9145 | n/a | n/a | n/a |
| P12 | n320 | kappa | 0.0000 | 0.0022 | 0.0022 | 0.1269 | 0.9215 | 0.0685 | 0.0100 | 1.062 | 0.2780 | 0.589 | 0.002 | 15.1 | 1.373 | 0.9010 | 8.7 | n/a | n/a |
| P12 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4192 | -0.0011 | 0.0532 | 0.9335 | 0.0565 | 0.0100 | 1.068 | 0.1360 | 0.116 | 0.679 | 5.9 | 1.132 | 0.6455 | n/a | n/a | n/a |
| P12 | n320 | carried_added | 0.1842 | 0.1853 | 0.0011 | 0.0210 | 0.9315 | 0.0045 | 0.0640 | 1.084 | 0.0458 | 0.590 | 0.002 | 14.8 | 1.175 | 0.9040 | n/a | n/a | n/a |
| P12 | n320 | pooled_retention | 0.0073 | 0.0074 | 0.0000 | 0.0007 | 0.9035 | 0.0030 | 0.0935 | 1.066 | 0.0016 | 0.526 | 0.000 | 15.1 | 2.153 | 0.8890 | 17.7 | n/a | n/a |
| P12 | h2 | large | -0.4183 | -0.4204 | -0.0021 | 0.0629 | 0.9265 | 0.0715 | 0.0020 | 1.069 | 0.1372 | 0.123 | 0.418 | 8.3 | 1.138 | 0.7635 | n/a | 1.000 | 0.9265 |
| P12 | h2 | carries | 0.0963 | 0.0968 | 0.0005 | 0.0090 | 0.9020 | 0.0045 | 0.0935 | 1.065 | 0.0195 | 0.573 | 0.000 | 15.1 | 1.938 | 0.8870 | 115.4 | 1.000 | 0.9020 |
| P12 | h2 | depends | 0.0000 | -0.0010 | -0.0010 | 0.0129 | 0.9015 | 0.0955 | 0.0030 | 1.079 | 0.0277 | 0.497 | 0.000 | 15.1 | 2.406 | 0.8885 | 53.4 | 1.000 | 0.9015 |
| P12 | h2 | carried_margin | 0.0000 | -0.0013 | -0.0013 | 0.0220 | 0.9010 | 0.0945 | 0.0045 | 1.063 | 0.0478 | 0.498 | 0.000 | 15.1 | 2.142 | 0.8885 | n/a | 1.000 | 0.9010 |
| P12 | h2 | own_margin | 1.7295 | 1.7270 | -0.0024 | 0.0324 | 0.9315 | 0.0645 | 0.0040 | 1.061 | 0.0688 | 0.454 | 0.004 | 15.1 | 1.134 | 0.8905 | n/a | 1.000 | 0.9315 |
| P12 | h2 | kappa | 0.0000 | 0.0042 | 0.0042 | 0.1164 | 0.8925 | 0.0890 | 0.0185 | 0.987 | 0.2513 | 0.504 | 0.000 | 15.1 | 1.861 | 0.8885 | 10.0 | 1.000 | 0.8925 |
| P12 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4191 | -0.0008 | 0.0532 | 0.9335 | 0.0575 | 0.0090 | 1.068 | 0.1359 | 0.116 | 0.677 | 5.9 | 1.141 | 0.6450 | n/a | 1.000 | 0.9335 |
| P12 | h2 | carried_added | 0.1842 | 0.1852 | 0.0010 | 0.0183 | 0.9005 | 0.0040 | 0.0955 | 1.067 | 0.0394 | 0.510 | 0.000 | 15.1 | 2.037 | 0.8880 | n/a | 1.000 | 0.9005 |
| P12 | h2 | pooled_retention | 0.0963 | 0.0968 | 0.0005 | 0.0095 | 0.9005 | 0.0030 | 0.0965 | 1.065 | 0.0206 | 0.574 | 0.000 | 15.0 | 2.139 | 0.8880 | 114.6 | 1.000 | 0.9005 |
| P12 | h5 | large | -0.4183 | -0.4203 | -0.0020 | 0.0629 | 0.9230 | 0.0750 | 0.0020 | 1.109 | 0.1414 | 0.167 | 0.424 | 8.0 | 1.178 | 0.7635 | n/a | 0.994 | 0.9240 |
| P12 | h5 | carries | 0.0360 | 0.0362 | 0.0002 | 0.0037 | 0.8975 | 0.0040 | 0.0985 | 1.069 | 0.0079 | 0.580 | 0.000 | 15.1 | 2.117 | 0.8835 | 147.3 | 0.994 | 0.8990 |
| P12 | h5 | depends | 0.0000 | -0.0003 | -0.0003 | 0.0045 | 0.9010 | 0.0955 | 0.0035 | 1.081 | 0.0096 | 0.525 | 0.000 | 15.1 | 2.321 | 0.8870 | 77.0 | 0.994 | 0.9025 |
| P12 | h5 | carried_margin | 0.0000 | -0.0012 | -0.0012 | 0.0219 | 0.9005 | 0.0955 | 0.0040 | 1.071 | 0.0476 | 0.528 | 0.000 | 15.1 | 2.087 | 0.8870 | n/a | 0.994 | 0.9020 |
| P12 | h5 | own_margin | 4.9368 | 4.9334 | -0.0034 | 0.0611 | 0.9485 | 0.0420 | 0.0095 | 1.164 | 0.1399 | 0.512 | 0.057 | 13.2 | 1.009 | 0.8890 | n/a | 0.994 | 0.9485 |
| P12 | h5 | kappa | 0.0000 | 0.0046 | 0.0046 | 0.1160 | 0.8890 | 0.0930 | 0.0180 | 0.991 | 0.2516 | 0.527 | 0.000 | 15.1 | 1.848 | 0.8870 | 9.9 | 0.994 | 0.8900 |
| P12 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4191 | -0.0008 | 0.0531 | 0.9255 | 0.0650 | 0.0095 | 1.125 | 0.1450 | 0.157 | 0.660 | 6.0 | 1.242 | 0.6410 | n/a | 0.994 | 0.9245 |
| P12 | h5 | carried_added | 0.1842 | 0.1852 | 0.0010 | 0.0183 | 0.9005 | 0.0040 | 0.0955 | 1.063 | 0.0395 | 0.541 | 0.000 | 15.1 | 2.078 | 0.8865 | n/a | 0.994 | 0.9020 |
| P12 | h5 | pooled_retention | 0.0360 | 0.0362 | 0.0002 | 0.0036 | 0.9000 | 0.0040 | 0.0960 | 1.065 | 0.0077 | 0.559 | 0.000 | 15.1 | 2.123 | 0.8840 | 147.9 | 0.994 | 0.9010 |
| P12 | h10 | large | -0.4183 | -0.3882 | 0.0301 | 0.0487 | 0.8085 | 0.1910 | 0.0005 | 0.943 | 0.0980 | 0.044 | 0.373 | 11.0 | 1.835 | 0.6210 | n/a | 0.194 | 0.8990 |
| P12 | h10 | carries | 0.0169 | 0.0158 | -0.0011 | 0.0011 | 0.7565 | 0.0000 | 0.2435 | 1.525 | 0.0029 | 0.571 | 0.001 | 15.1 | 2.622 | 0.7535 | 121.7 | 0.194 | 0.9035 |
| P12 | h10 | depends | 0.0000 | 0.0013 | 0.0013 | 0.0014 | 0.7545 | 0.2455 | 0.0000 | 1.503 | 0.0035 | 0.543 | 0.000 | 15.2 | 2.849 | 0.7515 | 110.2 | 0.194 | 0.9010 |
| P12 | h10 | carried_margin | 0.0000 | 0.0145 | 0.0145 | 0.0150 | 0.7545 | 0.2455 | 0.0000 | 1.494 | 0.0379 | 0.538 | 0.000 | 15.2 | 2.672 | 0.7515 | n/a | 0.194 | 0.9010 |
| P12 | h10 | own_margin | 10.7131 | 10.7410 | 0.0278 | 0.0979 | 0.9560 | 0.0320 | 0.0120 | 1.402 | 0.2154 | 0.497 | 0.283 | 10.3 | 0.967 | 0.8765 | n/a | 0.194 | 0.9630 |
| P12 | h10 | kappa | 0.0000 | 0.0905 | 0.0905 | 0.0923 | 0.7630 | 0.2370 | 0.0000 | 1.335 | 0.2347 | 0.537 | 0.000 | 15.2 | 2.349 | 0.7515 | 11.6 | 0.194 | 0.8930 |
| P12 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4027 | 0.0156 | 0.0447 | 0.8590 | 0.1380 | 0.0030 | 0.775 | 0.0845 | 0.037 | 0.598 | 8.3 | 1.567 | 0.5685 | n/a | 0.194 | 0.8880 |
| P12 | h10 | carried_added | 0.1842 | 0.1721 | -0.0121 | 0.0124 | 0.7570 | 0.0000 | 0.2430 | 1.513 | 0.0315 | 0.528 | 0.001 | 15.2 | 2.689 | 0.7545 | n/a | 0.194 | 0.9020 |
| P12 | h10 | pooled_retention | 0.0169 | 0.0158 | -0.0011 | 0.0011 | 0.7555 | 0.0000 | 0.2445 | 1.519 | 0.0029 | 0.565 | 0.000 | 15.1 | 2.773 | 0.7535 | 122.6 | 0.194 | 0.9035 |
| P13 | n20 | large | -0.4216 | -0.4212 | 0.0004 | 0.0586 | 0.8995 | 0.0985 | 0.0020 | 1.027 | 0.1190 | 0.269 | 0.146 | 11.0 | 1.358 | 0.8115 | n/a | n/a | n/a |
| P13 | n20 | carries | 0.3000 | 0.3007 | 0.0007 | 0.0336 | 0.9025 | 0.0020 | 0.0955 | 1.098 | 0.0739 | 0.603 | 0.025 | 13.8 | 1.438 | 0.8690 | 8.6 | n/a | n/a |
| P13 | n20 | depends | -0.0084 | -0.0092 | -0.0008 | 0.0793 | 0.9445 | 0.0485 | 0.0070 | 0.982 | 0.1579 | 0.137 | 0.018 | 14.9 | 1.011 | 0.8685 | 9.1 | n/a | n/a |
| P13 | n20 | carried_margin | -0.0035 | -0.0031 | 0.0004 | 0.0327 | 0.9525 | 0.0395 | 0.0080 | 0.982 | 0.0674 | 0.117 | 0.019 | 14.8 | 0.989 | 0.8675 | n/a | n/a | n/a |
| P13 | n20 | own_margin | 0.4181 | 0.4181 | -0.0000 | 0.0532 | 0.9340 | 0.0075 | 0.0585 | 1.008 | 0.1320 | 0.108 | 0.687 | 5.8 | 1.157 | 0.6290 | n/a | n/a | n/a |
| P13 | n20 | kappa | -0.0194 | -0.0206 | -0.0012 | 0.1776 | 0.9020 | 0.0710 | 0.0270 | 0.895 | 0.3579 | 0.117 | 0.016 | 14.8 | 1.196 | 0.8680 | 6.6 | n/a | n/a |
| P13 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0532 | 0.9340 | 0.0585 | 0.0075 | 1.008 | 0.1320 | 0.108 | 0.687 | 5.8 | 1.157 | 0.6290 | n/a | n/a | n/a |
| P13 | n20 | carried_added | 0.1807 | 0.1808 | 0.0001 | 0.0292 | 0.9140 | 0.0010 | 0.0850 | 1.017 | 0.0584 | 0.117 | 0.036 | 14.2 | 1.286 | 0.8675 | n/a | n/a | n/a |
| P13 | n20 | pooled_retention | 0.3000 | 0.2999 | -0.0001 | 0.0304 | 0.8670 | 0.0040 | 0.1290 | 0.988 | 0.0635 | 0.757 | 0.000 | 15.0 | 2.281 | 0.8560 | 8.5 | n/a | n/a |
| P13 | n40 | large | 0.1394 | 0.1469 | 0.0075 | 0.1527 | 0.9105 | 0.0015 | 0.0880 | 1.121 | 0.3079 | 0.509 | 0.064 | 12.8 | 1.395 | 0.8795 | n/a | n/a | n/a |
| P13 | n40 | carries | 0.3730 | 0.3770 | 0.0040 | 0.0785 | 0.9275 | 0.0030 | 0.0695 | 1.105 | 0.1635 | 0.582 | 0.034 | 13.5 | 1.257 | 0.9060 | 8.2 | n/a | n/a |
| P13 | n40 | depends | 0.3090 | 0.3134 | 0.0044 | 0.0851 | 0.9195 | 0.0040 | 0.0765 | 1.099 | 0.1747 | 0.552 | 0.038 | 13.3 | 1.396 | 0.9000 | 8.1 | n/a | n/a |
| P13 | n40 | carried_margin | 0.5575 | 0.5650 | 0.0075 | 0.1717 | 0.8955 | 0.0030 | 0.1015 | 1.068 | 0.3345 | 0.291 | 0.150 | 11.1 | 1.562 | 0.8465 | n/a | n/a | n/a |
| P13 | n40 | own_margin | 1.8041 | 1.8030 | -0.0010 | 0.2382 | 0.9430 | 0.0095 | 0.0475 | 1.039 | 0.4933 | 0.169 | 0.259 | 10.3 | 1.034 | 0.8450 | n/a | n/a | n/a |
| P13 | n40 | kappa | 0.7517 | 0.7452 | -0.0064 | 0.0649 | 0.9230 | 0.0430 | 0.0340 | 0.871 | 0.1269 | 0.292 | 0.090 | 12.1 | 1.159 | 0.8650 | 4.5 | n/a | n/a |
| P13 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4180 | 0.0001 | 0.0532 | 0.9340 | 0.0585 | 0.0075 | 1.009 | 0.1319 | 0.109 | 0.684 | 5.8 | 1.155 | 0.6300 | n/a | n/a | n/a |
| P13 | n40 | carried_added | 0.7417 | 0.7490 | 0.0073 | 0.1843 | 0.9010 | 0.0020 | 0.0970 | 1.056 | 0.3619 | 0.291 | 0.104 | 11.8 | 1.458 | 0.8585 | n/a | n/a | n/a |
| P13 | n40 | pooled_retention | 0.3730 | 0.3710 | -0.0020 | 0.0560 | 0.8955 | 0.0010 | 0.1035 | 1.037 | 0.1142 | 0.519 | 0.045 | 13.4 | 1.478 | 0.8620 | 8.2 | n/a | n/a |
| P13 | n80 | large | 7.5438 | 7.5628 | 0.0190 | 1.4855 | 0.9415 | 0.0105 | 0.0480 | 1.010 | 3.3580 | 0.175 | 0.374 | 8.9 | 1.077 | 0.7995 | n/a | n/a | n/a |
| P13 | n80 | carries | 0.8252 | 0.8332 | 0.0080 | 0.1407 | 0.9510 | 0.0035 | 0.0455 | 1.169 | 0.3111 | 0.621 | 0.044 | 13.4 | 0.978 | 0.9205 | 7.9 | n/a | n/a |
| P13 | n80 | depends | 0.8219 | 0.8305 | 0.0086 | 0.1431 | 0.9520 | 0.0025 | 0.0455 | 1.173 | 0.3163 | 0.622 | 0.044 | 13.4 | 0.982 | 0.9210 | 7.8 | n/a | n/a |
| P13 | n80 | carried_margin | 7.9619 | 7.9809 | 0.0190 | 1.5226 | 0.9400 | 0.0100 | 0.0500 | 1.008 | 3.4576 | 0.158 | 0.394 | 8.7 | 1.069 | 0.7920 | n/a | n/a | n/a |
| P13 | n80 | own_margin | 9.6872 | 9.6712 | -0.0160 | 1.3702 | 0.9250 | 0.0225 | 0.0525 | 0.972 | 3.5839 | 0.131 | 0.645 | 6.3 | 1.198 | 0.6855 | n/a | n/a | n/a |
| P13 | n80 | kappa | 0.9774 | 0.9771 | -0.0003 | 0.0049 | 0.9255 | 0.0640 | 0.0105 | 0.921 | 0.0096 | 0.159 | 0.317 | 9.6 | 1.164 | 0.8055 | 5.7 | n/a | n/a |
| P13 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0532 | 0.9310 | 0.0610 | 0.0080 | 1.009 | 0.1322 | 0.109 | 0.683 | 5.8 | 1.153 | 0.6275 | n/a | n/a | n/a |
| P13 | n80 | carried_added | 8.1461 | 8.1648 | 0.0188 | 1.5434 | 0.9405 | 0.0100 | 0.0495 | 1.008 | 3.4712 | 0.158 | 0.374 | 8.9 | 1.074 | 0.7925 | n/a | n/a | n/a |
| P13 | n80 | pooled_retention | 0.8252 | 0.8226 | -0.0027 | 0.0860 | 0.8705 | 0.0040 | 0.1255 | 0.997 | 0.1805 | 0.459 | 0.005 | 15.1 | 1.835 | 0.8520 | 8.0 | n/a | n/a |
| P13 | n160 | large | 18.7263 | 18.7283 | 0.0021 | 2.2891 | 0.9250 | 0.0060 | 0.0690 | 1.011 | 4.8397 | 0.543 | 0.007 | 14.4 | 1.161 | 0.8790 | n/a | n/a | n/a |
| P13 | n160 | carries | 0.8918 | 0.8996 | 0.0078 | 0.1469 | 0.9070 | 0.0015 | 0.0915 | 1.064 | 0.2998 | 0.597 | 0.011 | 14.4 | 1.325 | 0.8760 | 16.1 | n/a | n/a |
| P13 | n160 | depends | 0.8908 | 0.8990 | 0.0082 | 0.1482 | 0.9085 | 0.0000 | 0.0915 | 1.066 | 0.3017 | 0.597 | 0.011 | 14.4 | 1.324 | 0.8760 | 15.7 | n/a | n/a |
| P13 | n160 | carried_margin | 19.1444 | 19.1464 | 0.0020 | 2.3080 | 0.9250 | 0.0050 | 0.0700 | 1.009 | 4.8811 | 0.529 | 0.009 | 14.4 | 1.178 | 0.8790 | n/a | n/a | n/a |
| P13 | n160 | own_margin | 21.4901 | 21.4633 | -0.0267 | 1.3268 | 0.9540 | 0.0350 | 0.0110 | 1.155 | 3.0080 | 0.510 | 0.127 | 11.8 | 0.974 | 0.8950 | n/a | n/a | n/a |
| P13 | n160 | kappa | 0.9905 | 0.9906 | 0.0001 | 0.0013 | 0.9005 | 0.0915 | 0.0080 | 0.978 | 0.0027 | 0.540 | 0.003 | 14.8 | 1.495 | 0.8800 | 8.4 | n/a | n/a |
| P13 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4181 | 0.0000 | 0.0532 | 0.9320 | 0.0605 | 0.0075 | 1.009 | 0.1323 | 0.108 | 0.686 | 5.8 | 1.153 | 0.6300 | n/a | n/a | n/a |
| P13 | n160 | carried_added | 19.3286 | 19.3304 | 0.0018 | 2.3428 | 0.9225 | 0.0045 | 0.0730 | 1.008 | 4.9431 | 0.528 | 0.008 | 14.5 | 1.192 | 0.8785 | n/a | n/a | n/a |
| P13 | n160 | pooled_retention | 0.8918 | 0.8912 | -0.0005 | 0.0908 | 0.8665 | 0.0045 | 0.1290 | 0.977 | 0.1885 | 0.562 | 0.000 | 15.1 | 2.268 | 0.8565 | 16.4 | n/a | n/a |
| P13 | n320 | large | 21.9357 | 21.9211 | -0.0146 | 2.5841 | 0.9180 | 0.0040 | 0.0780 | 1.014 | 5.4621 | 0.585 | 0.004 | 14.7 | 1.234 | 0.8820 | n/a | n/a | n/a |
| P13 | n320 | carries | 0.8950 | 0.9007 | 0.0056 | 0.1439 | 0.9045 | 0.0010 | 0.0945 | 1.071 | 0.2954 | 0.596 | 0.011 | 14.6 | 1.414 | 0.8755 | 17.5 | n/a | n/a |
| P13 | n320 | depends | 0.8942 | 0.9002 | 0.0059 | 0.1450 | 0.9045 | 0.0010 | 0.0945 | 1.073 | 0.2971 | 0.596 | 0.011 | 14.6 | 1.414 | 0.8755 | 17.0 | n/a | n/a |
| P13 | n320 | carried_margin | 22.3538 | 22.3391 | -0.0147 | 2.5981 | 0.9155 | 0.0040 | 0.0805 | 1.014 | 5.4857 | 0.580 | 0.004 | 14.8 | 1.242 | 0.8820 | n/a | n/a | n/a |
| P13 | n320 | own_margin | 24.9973 | 24.9992 | 0.0018 | 1.3740 | 0.9540 | 0.0365 | 0.0095 | 1.218 | 3.1924 | 0.567 | 0.083 | 12.5 | 0.955 | 0.9035 | n/a | n/a | n/a |
| P13 | n320 | kappa | 0.9918 | 0.9919 | 0.0001 | 0.0011 | 0.8980 | 0.0960 | 0.0060 | 0.974 | 0.0023 | 0.586 | 0.001 | 15.0 | 1.529 | 0.8775 | 8.6 | n/a | n/a |
| P13 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4180 | 0.0001 | 0.0532 | 0.9340 | 0.0585 | 0.0075 | 1.010 | 0.1326 | 0.110 | 0.687 | 5.8 | 1.152 | 0.6285 | n/a | n/a | n/a |
| P13 | n320 | carried_added | 22.5380 | 22.5231 | -0.0149 | 2.6342 | 0.9140 | 0.0040 | 0.0820 | 1.013 | 5.5603 | 0.580 | 0.004 | 14.8 | 1.257 | 0.8775 | n/a | n/a | n/a |
| P13 | n320 | pooled_retention | 0.8950 | 0.8945 | -0.0005 | 0.0910 | 0.8685 | 0.0045 | 0.1270 | 0.975 | 0.1894 | 0.545 | 0.000 | 15.1 | 2.362 | 0.8585 | 17.7 | n/a | n/a |
| P13 | h2 | large | -0.0284 | -0.0281 | 0.0004 | 0.0503 | 0.9320 | 0.0460 | 0.0220 | 1.008 | 0.1256 | 0.123 | 0.663 | 5.9 | 1.088 | 0.6255 | n/a | 1.000 | 0.9320 |
| P13 | h2 | carries | 0.3000 | 0.2997 | -0.0003 | 0.0288 | 0.8675 | 0.0040 | 0.1285 | 0.976 | 0.0600 | 0.584 | 0.000 | 15.1 | 2.187 | 0.8565 | 115.8 | 1.000 | 0.8675 |
| P13 | h2 | depends | 0.2254 | 0.2257 | 0.0002 | 0.0144 | 0.8795 | 0.0025 | 0.1180 | 1.047 | 0.0300 | 0.582 | 0.000 | 15.2 | 1.632 | 0.8625 | 54.6 | 1.000 | 0.8795 |
| P13 | h2 | carried_margin | 0.3899 | 0.3900 | 0.0001 | 0.0181 | 0.8975 | 0.0020 | 0.1005 | 1.079 | 0.0390 | 0.516 | 0.000 | 15.3 | 1.368 | 0.8730 | n/a | 1.000 | 0.8975 |
| P13 | h2 | own_margin | 1.7295 | 1.7299 | 0.0004 | 0.0332 | 0.9035 | 0.0920 | 0.0045 | 0.971 | 0.0675 | 0.461 | 0.004 | 15.0 | 1.360 | 0.8590 | n/a | 1.000 | 0.9035 |
| P13 | h2 | kappa | 0.6792 | 0.6833 | 0.0041 | 0.0388 | 0.8645 | 0.1215 | 0.0140 | 0.882 | 0.0802 | 0.541 | 0.000 | 15.1 | 2.059 | 0.8540 | 10.0 | 1.000 | 0.8645 |
| P13 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4181 | 0.0003 | 0.0532 | 0.9325 | 0.0600 | 0.0075 | 1.009 | 0.1320 | 0.109 | 0.687 | 5.8 | 1.159 | 0.6295 | n/a | 1.000 | 0.9325 |
| P13 | h2 | carried_added | 0.5741 | 0.5740 | -0.0001 | 0.0583 | 0.8655 | 0.0035 | 0.1310 | 0.983 | 0.1215 | 0.510 | 0.000 | 15.1 | 2.278 | 0.8560 | n/a | 1.000 | 0.8655 |
| P13 | h2 | pooled_retention | 0.3000 | 0.2998 | -0.0002 | 0.0304 | 0.8655 | 0.0040 | 0.1305 | 0.978 | 0.0631 | 0.567 | 0.000 | 15.1 | 2.313 | 0.8580 | 116.3 | 1.000 | 0.8655 |
| P13 | h5 | large | 3.9236 | 3.9222 | -0.0014 | 0.4141 | 0.8730 | 0.0040 | 0.1230 | 0.989 | 0.8575 | 0.498 | 0.000 | 15.3 | 1.814 | 0.8575 | n/a | 0.993 | 0.8730 |
| P13 | h5 | carries | 0.8838 | 0.8838 | -0.0001 | 0.0935 | 0.8695 | 0.0035 | 0.1270 | 0.991 | 0.1935 | 0.562 | 0.000 | 15.2 | 2.056 | 0.8565 | 145.0 | 0.993 | 0.8685 |
| P13 | h5 | depends | 0.8795 | 0.8802 | 0.0007 | 0.0964 | 0.8690 | 0.0035 | 0.1275 | 1.000 | 0.1989 | 0.562 | 0.000 | 15.2 | 2.066 | 0.8565 | 77.9 | 0.993 | 0.8680 |
| P13 | h5 | carried_margin | 4.3419 | 4.3404 | -0.0015 | 0.4265 | 0.8695 | 0.0035 | 0.1270 | 0.992 | 0.8879 | 0.542 | 0.000 | 15.2 | 1.944 | 0.8555 | n/a | 0.993 | 0.8685 |
| P13 | h5 | own_margin | 4.9368 | 4.9369 | 0.0001 | 0.0637 | 0.9350 | 0.0580 | 0.0070 | 1.042 | 0.1401 | 0.509 | 0.059 | 13.2 | 1.084 | 0.8705 | n/a | 0.993 | 0.9350 |
| P13 | h5 | kappa | 0.9593 | 0.9598 | 0.0005 | 0.0050 | 0.8640 | 0.1205 | 0.0155 | 0.892 | 0.0103 | 0.534 | 0.000 | 15.2 | 1.966 | 0.8585 | 9.9 | 0.993 | 0.8635 |
| P13 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4182 | 0.0001 | 0.0532 | 0.9155 | 0.0730 | 0.0115 | 1.070 | 0.1357 | 0.151 | 0.655 | 6.0 | 1.262 | 0.6330 | n/a | 0.993 | 0.9160 |
| P13 | h5 | carried_added | 4.5261 | 4.5244 | -0.0017 | 0.4667 | 0.8690 | 0.0035 | 0.1275 | 0.989 | 0.9710 | 0.539 | 0.000 | 15.2 | 2.010 | 0.8540 | n/a | 0.993 | 0.8680 |
| P13 | h5 | pooled_retention | 0.8838 | 0.8834 | -0.0004 | 0.0907 | 0.8670 | 0.0035 | 0.1295 | 0.985 | 0.1879 | 0.524 | 0.000 | 15.2 | 2.142 | 0.8555 | 147.7 | 0.993 | 0.8660 |
| P13 | h10 | large | 9.2049 | 8.5846 | -0.6203 | 0.6344 | 0.7310 | 0.0000 | 0.2690 | 1.421 | 1.5465 | 0.554 | 0.001 | 15.2 | 2.634 | 0.7230 | n/a | 0.191 | 0.8675 |
| P13 | h10 | carries | 0.9000 | 0.8392 | -0.0608 | 0.0622 | 0.7340 | 0.0000 | 0.2660 | 1.416 | 0.1514 | 0.580 | 0.002 | 15.1 | 2.659 | 0.7285 | 122.4 | 0.191 | 0.8670 |
| P13 | h10 | depends | 0.8983 | 0.8370 | -0.0613 | 0.0628 | 0.7340 | 0.0000 | 0.2660 | 1.422 | 0.1526 | 0.580 | 0.002 | 15.1 | 2.672 | 0.7285 | 110.1 | 0.191 | 0.8685 |
| P13 | h10 | carried_margin | 9.6232 | 8.9867 | -0.6366 | 0.6416 | 0.7305 | 0.0000 | 0.2695 | 1.428 | 1.5682 | 0.528 | 0.001 | 15.2 | 2.695 | 0.7245 | n/a | 0.191 | 0.8665 |
| P13 | h10 | own_margin | 10.7131 | 10.7405 | 0.0274 | 0.0993 | 0.9530 | 0.0375 | 0.0095 | 1.362 | 0.2148 | 0.521 | 0.273 | 10.4 | 0.969 | 0.8675 | n/a | 0.191 | 0.9570 |
| P13 | h10 | kappa | 0.9812 | 0.9830 | 0.0017 | 0.0018 | 0.7415 | 0.2585 | 0.0000 | 1.248 | 0.0043 | 0.533 | 0.000 | 15.2 | 2.405 | 0.7255 | 11.9 | 0.191 | 0.8640 |
| P13 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4021 | 0.0163 | 0.0439 | 0.8650 | 0.1325 | 0.0025 | 0.788 | 0.0837 | 0.037 | 0.598 | 8.2 | 1.513 | 0.5740 | n/a | 0.191 | 0.8900 |
| P13 | h10 | carried_added | 9.8074 | 9.1435 | -0.6639 | 0.6687 | 0.7315 | 0.0000 | 0.2685 | 1.427 | 1.6350 | 0.530 | 0.001 | 15.2 | 2.717 | 0.7250 | n/a | 0.191 | 0.8675 |
| P13 | h10 | pooled_retention | 0.9000 | 0.8389 | -0.0611 | 0.0608 | 0.7275 | 0.0000 | 0.2725 | 1.434 | 0.1494 | 0.547 | 0.000 | 15.1 | 2.780 | 0.7235 | 121.7 | 0.191 | 0.8660 |
| T1 | n20 | large | -0.2236 | -0.2227 | 0.0009 | 0.0420 | 0.9675 | 0.0220 | 0.0105 | 1.091 | 0.0873 | 0.440 | 0.114 | 11.9 | 0.891 | n/a | n/a | n/a | n/a |
| T1 | n20 | carries | 0.6000 | 0.6018 | 0.0018 | 0.0557 | 0.8855 | 0.0010 | 0.1135 | 1.108 | 0.1175 | 0.594 | 0.046 | 13.4 | 1.375 | n/a | 10.3 | n/a | n/a |
| T1 | n20 | depends | 0.4041 | 0.4051 | 0.0010 | 0.0847 | 0.8995 | 0.0010 | 0.0995 | 1.064 | 0.1691 | 0.493 | 0.031 | 13.5 | 1.205 | n/a | 9.9 | n/a | n/a |
| T1 | n20 | carried_margin | 0.1517 | 0.1517 | 0.0000 | 0.0370 | 0.9100 | 0.0020 | 0.0880 | 1.014 | 0.0746 | 0.074 | 0.342 | 9.9 | 1.236 | n/a | n/a | n/a | n/a |
| T1 | n20 | own_margin | 0.3753 | 0.3744 | -0.0009 | 0.0453 | 0.9230 | 0.0135 | 0.0635 | 0.986 | 0.1099 | 0.071 | 0.761 | 5.3 | 1.228 | n/a | n/a | n/a | n/a |
| T1 | n20 | kappa | 0.4521 | 0.4499 | -0.0022 | 0.0766 | 0.9410 | 0.0400 | 0.0190 | 0.944 | 0.1575 | 0.077 | 0.072 | 14.0 | 1.034 | n/a | 8.0 | n/a | n/a |
| T1 | n20 | shuffled_vs_yardstick | -0.3753 | -0.3744 | 0.0009 | 0.0453 | 0.9230 | 0.0635 | 0.0135 | 0.986 | 0.1099 | 0.071 | 0.761 | 5.3 | 1.228 | n/a | n/a | n/a | n/a |
| T1 | n20 | carried_added | 0.3354 | 0.3357 | 0.0003 | 0.0457 | 0.9050 | 0.0035 | 0.0915 | 1.010 | 0.0902 | 0.074 | 0.112 | 13.2 | 1.377 | n/a | n/a | n/a | n/a |
| T1 | n20 | pooled_retention | 0.6000 | 0.6004 | 0.0004 | 0.0482 | 0.8150 | 0.0005 | 0.1845 | 1.065 | 0.1022 | 0.742 | 0.000 | 15.1 | 1.748 | n/a | 10.5 | n/a | n/a |
| T1 | n40 | large | 0.5777 | 0.5776 | -0.0002 | 0.1397 | 0.9340 | 0.0035 | 0.0625 | 1.073 | 0.2950 | 0.339 | 0.048 | 13.0 | 1.116 | n/a | n/a | n/a | n/a |
| T1 | n40 | carries | 0.6000 | 0.6042 | 0.0042 | 0.0791 | 0.9620 | 0.0060 | 0.0320 | 1.176 | 0.1791 | 0.612 | 0.013 | 14.1 | 0.914 | n/a | 8.1 | n/a | n/a |
| T1 | n40 | depends | 0.5570 | 0.5617 | 0.0046 | 0.0847 | 0.9605 | 0.0040 | 0.0355 | 1.178 | 0.1915 | 0.609 | 0.016 | 14.1 | 0.925 | n/a | 7.8 | n/a | n/a |
| T1 | n40 | carried_margin | 0.9530 | 0.9519 | -0.0011 | 0.1616 | 0.9360 | 0.0045 | 0.0595 | 1.017 | 0.3375 | 0.144 | 0.177 | 11.3 | 1.089 | n/a | n/a | n/a | n/a |
| T1 | n40 | own_margin | 1.7109 | 1.7066 | -0.0043 | 0.2420 | 0.9270 | 0.0100 | 0.0630 | 0.986 | 0.5024 | 0.137 | 0.321 | 9.5 | 1.111 | n/a | n/a | n/a | n/a |
| T1 | n40 | kappa | 0.8384 | 0.8364 | -0.0019 | 0.0267 | 0.9430 | 0.0420 | 0.0150 | 0.949 | 0.0543 | 0.145 | 0.089 | 12.9 | 1.038 | n/a | 6.7 | n/a | n/a |
| T1 | n40 | shuffled_vs_yardstick | -0.3753 | -0.3744 | 0.0009 | 0.0452 | 0.9215 | 0.0650 | 0.0135 | 0.988 | 0.1095 | 0.072 | 0.762 | 5.2 | 1.205 | n/a | n/a | n/a | n/a |
| T1 | n40 | carried_added | 1.1368 | 1.1359 | -0.0008 | 0.1760 | 0.9345 | 0.0025 | 0.0630 | 1.021 | 0.3660 | 0.143 | 0.117 | 12.4 | 1.121 | n/a | n/a | n/a | n/a |
| T1 | n40 | pooled_retention | 0.6000 | 0.6004 | 0.0004 | 0.0480 | 0.8110 | 0.0015 | 0.1875 | 1.079 | 0.1021 | 0.739 | 0.000 | 15.1 | 1.765 | n/a | 8.1 | n/a | n/a |
| T1 | n80 | large | 5.4462 | 5.4215 | -0.0246 | 0.9351 | 0.9375 | 0.0130 | 0.0495 | 0.971 | 2.1413 | 0.137 | 0.454 | 8.1 | 1.130 | n/a | n/a | n/a | n/a |
| T1 | n80 | carries | 0.6000 | 0.6025 | 0.0025 | 0.0839 | 0.9555 | 0.0015 | 0.0430 | 1.233 | 0.1911 | 0.632 | 0.048 | 13.3 | 0.962 | n/a | 7.8 | n/a | n/a |
| T1 | n80 | depends | 0.5925 | 0.5952 | 0.0027 | 0.0844 | 0.9540 | 0.0015 | 0.0445 | 1.238 | 0.1923 | 0.632 | 0.049 | 13.3 | 0.960 | n/a | 7.7 | n/a | n/a |
| T1 | n80 | carried_margin | 5.8214 | 5.7959 | -0.0255 | 0.9673 | 0.9340 | 0.0130 | 0.0530 | 0.967 | 2.2168 | 0.123 | 0.495 | 7.9 | 1.111 | n/a | n/a | n/a | n/a |
| T1 | n80 | own_margin | 9.8249 | 9.7970 | -0.0279 | 1.3732 | 0.9190 | 0.0230 | 0.0580 | 1.010 | 3.6976 | 0.126 | 0.666 | 6.1 | 1.216 | n/a | n/a | n/a | n/a |
| T1 | n80 | kappa | 0.9694 | 0.9688 | -0.0006 | 0.0054 | 0.9445 | 0.0425 | 0.0130 | 0.959 | 0.0115 | 0.124 | 0.422 | 8.6 | 1.042 | n/a | 6.6 | n/a | n/a |
| T1 | n80 | shuffled_vs_yardstick | -0.3753 | -0.3744 | 0.0009 | 0.0453 | 0.9240 | 0.0625 | 0.0135 | 0.986 | 0.1101 | 0.075 | 0.766 | 5.3 | 1.211 | n/a | n/a | n/a | n/a |
| T1 | n80 | carried_added | 6.0052 | 5.9799 | -0.0253 | 0.9830 | 0.9345 | 0.0130 | 0.0525 | 0.969 | 2.2251 | 0.123 | 0.470 | 8.1 | 1.105 | n/a | n/a | n/a | n/a |
| T1 | n80 | pooled_retention | 0.6000 | 0.6003 | 0.0003 | 0.0480 | 0.8095 | 0.0010 | 0.1895 | 1.080 | 0.1028 | 0.794 | 0.000 | 15.1 | 1.719 | n/a | 7.7 | n/a | n/a |
| T1 | n160 | large | 12.8347 | 12.8149 | -0.0198 | 1.2576 | 0.9335 | 0.0020 | 0.0645 | 1.093 | 2.7495 | 0.530 | 0.041 | 13.7 | 1.084 | n/a | n/a | n/a | n/a |
| T1 | n160 | carries | 0.6000 | 0.6020 | 0.0020 | 0.0770 | 0.9070 | 0.0005 | 0.0925 | 1.134 | 0.1645 | 0.583 | 0.029 | 13.9 | 1.278 | n/a | 18.8 | n/a | n/a |
| T1 | n160 | depends | 0.5967 | 0.5988 | 0.0021 | 0.0771 | 0.9075 | 0.0005 | 0.0920 | 1.137 | 0.1646 | 0.582 | 0.030 | 13.9 | 1.273 | n/a | 18.3 | n/a | n/a |
| T1 | n160 | carried_margin | 13.2100 | 13.1893 | -0.0207 | 1.2722 | 0.9310 | 0.0020 | 0.0670 | 1.086 | 2.7713 | 0.513 | 0.041 | 13.6 | 1.109 | n/a | n/a | n/a | n/a |
| T1 | n160 | own_margin | 22.1392 | 22.1336 | -0.0056 | 1.1889 | 0.9555 | 0.0305 | 0.0140 | 1.184 | 2.6459 | 0.508 | 0.177 | 11.3 | 0.971 | n/a | n/a | n/a | n/a |
| T1 | n160 | kappa | 0.9863 | 0.9863 | 0.0000 | 0.0015 | 0.9010 | 0.0945 | 0.0045 | 1.034 | 0.0032 | 0.515 | 0.018 | 14.1 | 1.281 | n/a | 10.3 | n/a | n/a |
| T1 | n160 | shuffled_vs_yardstick | -0.3753 | -0.3744 | 0.0009 | 0.0453 | 0.9220 | 0.0645 | 0.0135 | 0.985 | 0.1101 | 0.073 | 0.763 | 5.3 | 1.224 | n/a | n/a | n/a | n/a |
| T1 | n160 | carried_added | 13.3937 | 13.3733 | -0.0205 | 1.2990 | 0.9270 | 0.0020 | 0.0710 | 1.084 | 2.8293 | 0.512 | 0.041 | 13.7 | 1.121 | n/a | n/a | n/a | n/a |
| T1 | n160 | pooled_retention | 0.6000 | 0.6003 | 0.0003 | 0.0479 | 0.8115 | 0.0015 | 0.1870 | 1.072 | 0.1022 | 0.551 | 0.000 | 15.1 | 1.765 | n/a | 18.6 | n/a | n/a |
| T1 | n320 | large | 14.9997 | 14.9897 | -0.0099 | 1.4052 | 0.9275 | 0.0020 | 0.0705 | 1.111 | 3.0704 | 0.581 | 0.021 | 14.2 | 1.123 | n/a | n/a | n/a | n/a |
| T1 | n320 | carries | 0.6000 | 0.6028 | 0.0028 | 0.0755 | 0.9040 | 0.0005 | 0.0955 | 1.150 | 0.1632 | 0.604 | 0.026 | 14.1 | 1.245 | n/a | 20.6 | n/a | n/a |
| T1 | n320 | depends | 0.5971 | 0.6001 | 0.0029 | 0.0756 | 0.9050 | 0.0005 | 0.0945 | 1.152 | 0.1632 | 0.604 | 0.026 | 14.0 | 1.245 | n/a | 20.1 | n/a | n/a |
| T1 | n320 | carried_margin | 15.3749 | 15.3641 | -0.0108 | 1.4147 | 0.9275 | 0.0020 | 0.0705 | 1.108 | 3.0942 | 0.580 | 0.022 | 14.2 | 1.140 | n/a | n/a | n/a | n/a |
| T1 | n320 | own_margin | 25.7474 | 25.7227 | -0.0247 | 1.2105 | 0.9535 | 0.0365 | 0.0100 | 1.237 | 2.7978 | 0.585 | 0.120 | 12.1 | 0.966 | n/a | n/a | n/a | n/a |
| T1 | n320 | kappa | 0.9882 | 0.9882 | 0.0000 | 0.0012 | 0.8915 | 0.1035 | 0.0050 | 1.023 | 0.0027 | 0.581 | 0.005 | 14.6 | 1.324 | n/a | 10.6 | n/a | n/a |
| T1 | n320 | shuffled_vs_yardstick | -0.3753 | -0.3744 | 0.0009 | 0.0452 | 0.9230 | 0.0635 | 0.0135 | 0.987 | 0.1098 | 0.075 | 0.764 | 5.3 | 1.204 | n/a | n/a | n/a | n/a |
| T1 | n320 | carried_added | 15.5587 | 15.5481 | -0.0106 | 1.4425 | 0.9230 | 0.0020 | 0.0750 | 1.105 | 3.1511 | 0.580 | 0.021 | 14.2 | 1.152 | n/a | n/a | n/a | n/a |
| T1 | n320 | pooled_retention | 0.6000 | 0.6004 | 0.0004 | 0.0478 | 0.8075 | 0.0005 | 0.1920 | 1.077 | 0.1024 | 0.543 | 0.000 | 15.1 | 1.757 | n/a | 20.3 | n/a | n/a |
| T1 | h2 | large | 0.5840 | 0.5850 | 0.0010 | 0.0653 | 0.9515 | 0.0025 | 0.0460 | 1.090 | 0.1389 | 0.110 | 0.183 | 11.9 | 0.989 | n/a | n/a | 1.000 | 0.9515 |
| T1 | h2 | carries | 0.6000 | 0.5999 | -0.0001 | 0.0455 | 0.8215 | 0.0005 | 0.1780 | 1.070 | 0.0971 | 0.598 | 0.000 | 15.2 | 1.683 | n/a | 130.0 | 1.000 | 0.8215 |
| T1 | h2 | depends | 0.5573 | 0.5579 | 0.0006 | 0.0428 | 0.8270 | 0.0005 | 0.1725 | 1.108 | 0.0905 | 0.594 | 0.000 | 15.2 | 1.670 | n/a | 64.2 | 1.000 | 0.8270 |
| T1 | h2 | carried_margin | 0.9595 | 0.9594 | -0.0001 | 0.0597 | 0.8355 | 0.0010 | 0.1635 | 1.089 | 0.1283 | 0.530 | 0.000 | 15.2 | 1.584 | n/a | n/a | 1.000 | 0.8355 |
| T1 | h2 | own_margin | 1.7216 | 1.7215 | -0.0001 | 0.0276 | 0.9335 | 0.0635 | 0.0030 | 1.081 | 0.0574 | 0.440 | 0.011 | 14.6 | 1.102 | n/a | n/a | 1.000 | 0.9335 |
| T1 | h2 | kappa | 0.8393 | 0.8403 | 0.0010 | 0.0152 | 0.8290 | 0.1640 | 0.0070 | 0.945 | 0.0326 | 0.538 | 0.000 | 15.1 | 1.605 | n/a | 12.5 | 1.000 | 0.8290 |
| T1 | h2 | shuffled_vs_yardstick | -0.3755 | -0.3744 | 0.0011 | 0.0452 | 0.9240 | 0.0630 | 0.0130 | 0.987 | 0.1103 | 0.074 | 0.765 | 5.3 | 1.211 | n/a | n/a | 1.000 | 0.9240 |
| T1 | h2 | carried_added | 1.1432 | 1.1434 | 0.0002 | 0.0916 | 0.8130 | 0.0005 | 0.1865 | 1.069 | 0.1955 | 0.532 | 0.000 | 15.2 | 1.709 | n/a | n/a | 1.000 | 0.8130 |
| T1 | h2 | pooled_retention | 0.6000 | 0.6001 | 0.0001 | 0.0480 | 0.8010 | 0.0005 | 0.1985 | 1.063 | 0.1020 | 0.584 | 0.000 | 15.1 | 1.769 | n/a | 130.5 | 1.000 | 0.8010 |
| T1 | h5 | large | 2.5194 | 2.5191 | -0.0003 | 0.2079 | 0.8535 | 0.0010 | 0.1455 | 1.087 | 0.4315 | 0.390 | 0.000 | 15.4 | 1.497 | n/a | n/a | 0.992 | 0.8545 |
| T1 | h5 | carries | 0.6000 | 0.5998 | -0.0002 | 0.0490 | 0.8110 | 0.0005 | 0.1885 | 1.078 | 0.1039 | 0.577 | 0.000 | 15.2 | 1.741 | n/a | 151.3 | 0.992 | 0.8125 |
| T1 | h5 | depends | 0.5851 | 0.5853 | 0.0001 | 0.0484 | 0.8130 | 0.0005 | 0.1865 | 1.091 | 0.1021 | 0.576 | 0.000 | 15.2 | 1.752 | n/a | 91.7 | 0.992 | 0.8145 |
| T1 | h5 | carried_margin | 2.8948 | 2.8936 | -0.0012 | 0.2144 | 0.8210 | 0.0005 | 0.1785 | 1.074 | 0.4540 | 0.533 | 0.000 | 15.2 | 1.699 | n/a | n/a | 0.992 | 0.8225 |
| T1 | h5 | own_margin | 4.9472 | 4.9474 | 0.0001 | 0.0515 | 0.9540 | 0.0410 | 0.0050 | 1.231 | 0.1224 | 0.509 | 0.117 | 12.2 | 0.982 | n/a | n/a | 0.992 | 0.9560 |
| T1 | h5 | kappa | 0.9403 | 0.9407 | 0.0004 | 0.0057 | 0.8265 | 0.1675 | 0.0060 | 0.947 | 0.0121 | 0.546 | 0.000 | 15.2 | 1.607 | n/a | 12.6 | 0.992 | 0.8280 |
| T1 | h5 | shuffled_vs_yardstick | -0.3755 | -0.3745 | 0.0010 | 0.0452 | 0.9160 | 0.0700 | 0.0140 | 0.989 | 0.1092 | 0.103 | 0.724 | 5.4 | 1.360 | n/a | n/a | 0.992 | 0.9160 |
| T1 | h5 | carried_added | 3.0786 | 3.0774 | -0.0012 | 0.2465 | 0.8150 | 0.0005 | 0.1845 | 1.068 | 0.5210 | 0.534 | 0.000 | 15.2 | 1.745 | n/a | n/a | 0.992 | 0.8165 |
| T1 | h5 | pooled_retention | 0.6000 | 0.5999 | -0.0001 | 0.0480 | 0.8060 | 0.0010 | 0.1930 | 1.062 | 0.1010 | 0.564 | 0.000 | 15.1 | 1.770 | n/a | 154.2 | 0.992 | 0.8070 |
| T1 | h10 | large | 5.9817 | 5.7967 | -0.1850 | 0.3839 | 0.7505 | 0.0000 | 0.2495 | 1.286 | 0.8226 | 0.576 | 0.000 | 15.1 | 1.741 | n/a | n/a | 0.452 | 0.8355 |
| T1 | h10 | carries | 0.6000 | 0.5813 | -0.0187 | 0.0383 | 0.7415 | 0.0000 | 0.2585 | 1.290 | 0.0854 | 0.562 | 0.000 | 15.0 | 1.810 | n/a | 121.8 | 0.452 | 0.8310 |
| T1 | h10 | depends | 0.5931 | 0.5747 | -0.0185 | 0.0380 | 0.7435 | 0.0000 | 0.2565 | 1.298 | 0.0846 | 0.564 | 0.001 | 15.0 | 1.806 | n/a | 111.9 | 0.452 | 0.8330 |
| T1 | h10 | carried_margin | 6.3571 | 6.1648 | -0.1923 | 0.3880 | 0.7340 | 0.0000 | 0.2660 | 1.289 | 0.8619 | 0.544 | 0.000 | 15.1 | 1.821 | n/a | n/a | 0.452 | 0.8265 |
| T1 | h10 | own_margin | 10.7177 | 10.7298 | 0.0121 | 0.0984 | 0.9525 | 0.0280 | 0.0195 | 1.355 | 0.2110 | 0.490 | 0.284 | 10.3 | 0.972 | n/a | n/a | 0.452 | 0.9480 |
| T1 | h10 | kappa | 0.9719 | 0.9731 | 0.0012 | 0.0022 | 0.7525 | 0.2475 | 0.0000 | 1.134 | 0.0049 | 0.538 | 0.000 | 15.2 | 1.716 | n/a | 14.9 | 0.452 | 0.8275 |
| T1 | h10 | shuffled_vs_yardstick | -0.3755 | -0.3681 | 0.0073 | 0.0387 | 0.9070 | 0.0845 | 0.0085 | 0.872 | 0.0802 | 0.034 | 0.707 | 6.8 | 1.302 | n/a | n/a | 0.452 | 0.9015 |
| T1 | h10 | carried_added | 6.5409 | 6.3360 | -0.2049 | 0.4128 | 0.7295 | 0.0000 | 0.2705 | 1.286 | 0.9177 | 0.542 | 0.000 | 15.1 | 1.846 | n/a | n/a | 0.452 | 0.8255 |
| T1 | h10 | pooled_retention | 0.6000 | 0.5812 | -0.0188 | 0.0375 | 0.7160 | 0.0000 | 0.2840 | 1.287 | 0.0833 | 0.561 | 0.000 | 15.2 | 1.900 | n/a | 123.8 | 0.452 | 0.8105 |
| T2 | n20 | large | -0.2755 | -0.2763 | -0.0007 | 0.0686 | 0.9715 | 0.0245 | 0.0040 | 1.153 | 0.1492 | 0.495 | 0.062 | 12.6 | 0.898 | n/a | n/a | n/a | n/a |
| T2 | n20 | carries | 0.6000 | 0.6014 | 0.0014 | 0.0737 | 0.9430 | 0.0035 | 0.0535 | 1.195 | 0.1693 | 0.621 | 0.018 | 13.8 | 1.057 | n/a | 7.4 | n/a | n/a |
| T2 | n20 | depends | 0.4531 | 0.4540 | 0.0009 | 0.1020 | 0.9430 | 0.0045 | 0.0525 | 1.158 | 0.2276 | 0.581 | 0.010 | 14.1 | 1.045 | n/a | 8.0 | n/a | n/a |
| T2 | n20 | carried_margin | 0.2282 | 0.2284 | 0.0001 | 0.0582 | 0.9290 | 0.0030 | 0.0680 | 1.100 | 0.1237 | 0.129 | 0.116 | 11.5 | 1.113 | n/a | n/a | n/a | n/a |
| T2 | n20 | own_margin | 0.5038 | 0.5046 | 0.0009 | 0.0709 | 0.9295 | 0.0055 | 0.0650 | 1.039 | 0.1779 | 0.132 | 0.604 | 6.5 | 1.185 | n/a | n/a | n/a | n/a |
| T2 | n20 | kappa | 0.5522 | 0.5485 | -0.0037 | 0.0884 | 0.9370 | 0.0445 | 0.0185 | 0.977 | 0.1846 | 0.128 | 0.007 | 15.0 | 1.062 | n/a | 5.7 | n/a | n/a |
| T2 | n20 | shuffled_vs_yardstick | -0.5038 | -0.5046 | -0.0009 | 0.0709 | 0.9295 | 0.0650 | 0.0055 | 1.039 | 0.1779 | 0.132 | 0.604 | 6.5 | 1.185 | n/a | n/a | n/a | n/a |
| T2 | n20 | carried_added | 0.4133 | 0.4151 | 0.0018 | 0.0738 | 0.9360 | 0.0015 | 0.0625 | 1.082 | 0.1558 | 0.126 | 0.020 | 14.4 | 1.121 | n/a | n/a | n/a | n/a |
| T2 | n20 | pooled_retention | 0.6000 | 0.6024 | 0.0024 | 0.0681 | 0.9290 | 0.0100 | 0.0610 | 1.012 | 0.1471 | 0.811 | 0.000 | 15.0 | 1.154 | n/a | 7.4 | n/a | n/a |
| T2 | n40 | large | 0.6165 | 0.6152 | -0.0013 | 0.1554 | 0.9555 | 0.0035 | 0.0410 | 1.170 | 0.3502 | 0.528 | 0.009 | 14.4 | 0.953 | n/a | n/a | n/a | n/a |
| T2 | n40 | carries | 0.6000 | 0.6009 | 0.0009 | 0.0776 | 0.9570 | 0.0095 | 0.0335 | 1.110 | 0.1720 | 0.630 | 0.005 | 14.4 | 0.957 | n/a | 8.4 | n/a | n/a |
| T2 | n40 | depends | 0.5628 | 0.5642 | 0.0014 | 0.0815 | 0.9560 | 0.0095 | 0.0345 | 1.128 | 0.1817 | 0.627 | 0.005 | 14.4 | 0.962 | n/a | 8.7 | n/a | n/a |
| T2 | n40 | carried_margin | 1.1202 | 1.1198 | -0.0004 | 0.1838 | 0.9520 | 0.0025 | 0.0455 | 1.103 | 0.4018 | 0.196 | 0.038 | 13.8 | 0.995 | n/a | n/a | n/a | n/a |
| T2 | n40 | own_margin | 1.9905 | 1.9933 | 0.0029 | 0.2379 | 0.9500 | 0.0140 | 0.0360 | 1.042 | 0.5019 | 0.188 | 0.196 | 10.9 | 0.999 | n/a | n/a | n/a | n/a |
| T2 | n40 | kappa | 0.8582 | 0.8573 | -0.0009 | 0.0262 | 0.9500 | 0.0405 | 0.0095 | 1.026 | 0.0550 | 0.198 | 0.009 | 15.3 | 0.996 | n/a | 6.1 | n/a | n/a |
| T2 | n40 | shuffled_vs_yardstick | -0.5038 | -0.5046 | -0.0009 | 0.0709 | 0.9300 | 0.0645 | 0.0055 | 1.038 | 0.1775 | 0.132 | 0.605 | 6.5 | 1.179 | n/a | n/a | n/a | n/a |
| T2 | n40 | carried_added | 1.3053 | 1.3065 | 0.0012 | 0.2123 | 0.9480 | 0.0030 | 0.0490 | 1.078 | 0.4595 | 0.197 | 0.013 | 14.8 | 1.010 | n/a | n/a | n/a | n/a |
| T2 | n40 | pooled_retention | 0.6000 | 0.6025 | 0.0025 | 0.0682 | 0.9310 | 0.0095 | 0.0595 | 1.008 | 0.1472 | 0.760 | 0.000 | 15.0 | 1.158 | n/a | 8.4 | n/a | n/a |
| T2 | n80 | large | 5.0693 | 5.1115 | 0.0422 | 0.9030 | 0.9490 | 0.0055 | 0.0455 | 1.076 | 1.9924 | 0.181 | 0.220 | 10.4 | 1.003 | n/a | n/a | n/a | n/a |
| T2 | n80 | carries | 0.6000 | 0.6070 | 0.0070 | 0.1048 | 0.9580 | 0.0030 | 0.0390 | 1.145 | 0.2310 | 0.637 | 0.022 | 13.9 | 0.963 | n/a | 8.3 | n/a | n/a |
| T2 | n80 | depends | 0.5921 | 0.5996 | 0.0075 | 0.1052 | 0.9590 | 0.0025 | 0.0385 | 1.153 | 0.2318 | 0.636 | 0.022 | 13.8 | 0.954 | n/a | 8.1 | n/a | n/a |
| T2 | n80 | carried_margin | 5.5730 | 5.6162 | 0.0431 | 0.9529 | 0.9470 | 0.0060 | 0.0470 | 1.070 | 2.1144 | 0.149 | 0.251 | 10.0 | 1.023 | n/a | n/a | n/a | n/a |
| T2 | n80 | own_margin | 9.4118 | 9.4564 | 0.0447 | 1.2392 | 0.9400 | 0.0220 | 0.0380 | 1.050 | 3.3857 | 0.144 | 0.607 | 6.5 | 1.067 | n/a | n/a | n/a | n/a |
| T2 | n80 | kappa | 0.9679 | 0.9678 | -0.0001 | 0.0061 | 0.9460 | 0.0440 | 0.0100 | 0.997 | 0.0129 | 0.149 | 0.140 | 11.7 | 1.020 | n/a | 6.0 | n/a | n/a |
| T2 | n80 | shuffled_vs_yardstick | -0.5038 | -0.5047 | -0.0009 | 0.0709 | 0.9300 | 0.0645 | 0.0055 | 1.039 | 0.1776 | 0.133 | 0.603 | 6.5 | 1.174 | n/a | n/a | n/a | n/a |
| T2 | n80 | carried_added | 5.7581 | 5.8029 | 0.0448 | 0.9826 | 0.9460 | 0.0060 | 0.0480 | 1.066 | 2.1653 | 0.149 | 0.217 | 10.5 | 1.013 | n/a | n/a | n/a | n/a |
| T2 | n80 | pooled_retention | 0.6000 | 0.6026 | 0.0026 | 0.0682 | 0.9285 | 0.0120 | 0.0595 | 1.008 | 0.1470 | 0.814 | 0.000 | 15.0 | 1.128 | n/a | 8.3 | n/a | n/a |
| T2 | n160 | large | 11.5374 | 11.5829 | 0.0455 | 1.5713 | 0.9495 | 0.0115 | 0.0390 | 1.058 | 3.4317 | 0.567 | 0.002 | 14.9 | 1.001 | n/a | n/a | n/a | n/a |
| T2 | n160 | carries | 0.6000 | 0.6097 | 0.0097 | 0.1174 | 0.9410 | 0.0040 | 0.0550 | 1.047 | 0.2444 | 0.611 | 0.001 | 14.9 | 1.076 | n/a | 13.4 | n/a | n/a |
| T2 | n160 | depends | 0.5963 | 0.6063 | 0.0100 | 0.1177 | 0.9415 | 0.0035 | 0.0550 | 1.049 | 0.2444 | 0.611 | 0.001 | 14.9 | 1.075 | n/a | 12.9 | n/a | n/a |
| T2 | n160 | carried_margin | 12.0411 | 12.0875 | 0.0464 | 1.6001 | 0.9500 | 0.0110 | 0.0390 | 1.053 | 3.4920 | 0.539 | 0.002 | 14.9 | 0.999 | n/a | n/a | n/a | n/a |
| T2 | n160 | own_margin | 20.1919 | 20.1827 | -0.0093 | 1.5340 | 0.9550 | 0.0265 | 0.0185 | 1.079 | 3.3321 | 0.530 | 0.081 | 12.7 | 0.978 | n/a | n/a | n/a | n/a |
| T2 | n160 | kappa | 0.9849 | 0.9849 | 0.0001 | 0.0024 | 0.9505 | 0.0385 | 0.0110 | 0.995 | 0.0050 | 0.540 | 0.001 | 15.1 | 0.998 | n/a | 7.4 | n/a | n/a |
| T2 | n160 | shuffled_vs_yardstick | -0.5038 | -0.5047 | -0.0009 | 0.0709 | 0.9305 | 0.0635 | 0.0060 | 1.039 | 0.1775 | 0.132 | 0.603 | 6.5 | 1.182 | n/a | n/a | n/a | n/a |
| T2 | n160 | carried_added | 12.2262 | 12.2742 | 0.0480 | 1.6387 | 0.9495 | 0.0110 | 0.0395 | 1.051 | 3.5677 | 0.539 | 0.002 | 14.9 | 1.006 | n/a | n/a | n/a | n/a |
| T2 | n160 | pooled_retention | 0.6000 | 0.6024 | 0.0024 | 0.0681 | 0.9275 | 0.0100 | 0.0625 | 1.006 | 0.1464 | 0.517 | 0.000 | 15.0 | 1.146 | n/a | 13.4 | n/a | n/a |
| T2 | n320 | large | 13.5205 | 13.5793 | 0.0587 | 1.7887 | 0.9495 | 0.0090 | 0.0415 | 1.075 | 3.9270 | 0.573 | 0.000 | 15.1 | 1.001 | n/a | n/a | n/a | n/a |
| T2 | n320 | carries | 0.6000 | 0.6103 | 0.0103 | 0.1147 | 0.9410 | 0.0035 | 0.0555 | 1.070 | 0.2412 | 0.603 | 0.000 | 15.1 | 1.098 | n/a | 14.1 | n/a | n/a |
| T2 | n320 | depends | 0.5968 | 0.6074 | 0.0105 | 0.1149 | 0.9405 | 0.0035 | 0.0560 | 1.072 | 0.2412 | 0.603 | 0.000 | 15.1 | 1.097 | n/a | 13.7 | n/a | n/a |
| T2 | n320 | carried_margin | 14.0243 | 14.0839 | 0.0596 | 1.8122 | 0.9490 | 0.0100 | 0.0410 | 1.074 | 3.9771 | 0.572 | 0.000 | 15.1 | 1.004 | n/a | n/a | n/a | n/a |
| T2 | n320 | own_margin | 23.4972 | 23.4572 | -0.0400 | 1.6387 | 0.9545 | 0.0315 | 0.0140 | 1.121 | 3.6535 | 0.585 | 0.045 | 13.2 | 0.969 | n/a | n/a | n/a | n/a |
| T2 | n320 | kappa | 0.9870 | 0.9871 | 0.0001 | 0.0020 | 0.9510 | 0.0380 | 0.0110 | 0.998 | 0.0042 | 0.573 | 0.000 | 15.2 | 0.993 | n/a | 7.5 | n/a | n/a |
| T2 | n320 | shuffled_vs_yardstick | -0.5038 | -0.5047 | -0.0009 | 0.0709 | 0.9305 | 0.0640 | 0.0055 | 1.039 | 0.1777 | 0.131 | 0.606 | 6.5 | 1.175 | n/a | n/a | n/a | n/a |
| T2 | n320 | carried_added | 14.2094 | 14.2706 | 0.0612 | 1.8518 | 0.9480 | 0.0095 | 0.0425 | 1.070 | 4.0600 | 0.572 | 0.000 | 15.1 | 1.010 | n/a | n/a | n/a | n/a |
| T2 | n320 | pooled_retention | 0.6000 | 0.6024 | 0.0024 | 0.0679 | 0.9275 | 0.0095 | 0.0630 | 1.010 | 0.1468 | 0.527 | 0.000 | 15.0 | 1.147 | n/a | 14.2 | n/a | n/a |
| T2 | h2 | large | 0.4690 | 0.4712 | 0.0022 | 0.0855 | 0.9485 | 0.0095 | 0.0420 | 1.044 | 0.1913 | 0.163 | 0.286 | 10.1 | 1.006 | n/a | n/a | 1.000 | 0.9485 |
| T2 | h2 | carries | 0.6000 | 0.6016 | 0.0016 | 0.0637 | 0.9275 | 0.0105 | 0.0620 | 1.000 | 0.1370 | 0.606 | 0.000 | 15.1 | 1.132 | n/a | 100.9 | 1.000 | 0.9275 |
| T2 | h2 | depends | 0.5576 | 0.5605 | 0.0029 | 0.0599 | 0.9245 | 0.0065 | 0.0690 | 1.018 | 0.1282 | 0.605 | 0.000 | 15.1 | 1.155 | n/a | 50.7 | 1.000 | 0.9245 |
| T2 | h2 | carried_margin | 0.9731 | 0.9758 | 0.0027 | 0.0861 | 0.9265 | 0.0080 | 0.0655 | 1.012 | 0.1859 | 0.534 | 0.000 | 15.1 | 1.155 | n/a | n/a | 1.000 | 0.9265 |
| T2 | h2 | own_margin | 1.7452 | 1.7443 | -0.0009 | 0.0344 | 0.9335 | 0.0515 | 0.0150 | 1.023 | 0.0730 | 0.438 | 0.002 | 15.3 | 1.089 | n/a | n/a | 1.000 | 0.9335 |
| T2 | h2 | kappa | 0.8402 | 0.8418 | 0.0016 | 0.0219 | 0.9315 | 0.0400 | 0.0285 | 0.956 | 0.0455 | 0.538 | 0.000 | 15.0 | 1.102 | n/a | 8.9 | 1.000 | 0.9315 |
| T2 | h2 | shuffled_vs_yardstick | -0.5041 | -0.5046 | -0.0005 | 0.0709 | 0.9310 | 0.0630 | 0.0060 | 1.039 | 0.1776 | 0.132 | 0.608 | 6.5 | 1.177 | n/a | n/a | 1.000 | 0.9310 |
| T2 | h2 | carried_added | 1.1582 | 1.1625 | 0.0044 | 0.1316 | 0.9270 | 0.0090 | 0.0640 | 1.002 | 0.2831 | 0.528 | 0.000 | 15.1 | 1.158 | n/a | n/a | 1.000 | 0.9270 |
| T2 | h2 | pooled_retention | 0.6000 | 0.6025 | 0.0025 | 0.0679 | 0.9265 | 0.0095 | 0.0640 | 1.002 | 0.1461 | 0.583 | 0.000 | 15.0 | 1.144 | n/a | 101.5 | 1.000 | 0.9265 |
| T2 | h5 | large | 2.3716 | 2.3818 | 0.0102 | 0.2803 | 0.9320 | 0.0095 | 0.0585 | 1.013 | 0.5996 | 0.317 | 0.001 | 15.6 | 1.130 | n/a | n/a | 0.998 | 0.9325 |
| T2 | h5 | carries | 0.6000 | 0.6026 | 0.0026 | 0.0703 | 0.9275 | 0.0090 | 0.0635 | 0.999 | 0.1507 | 0.576 | 0.000 | 15.1 | 1.181 | n/a | 139.8 | 0.998 | 0.9280 |
| T2 | h5 | depends | 0.5849 | 0.5881 | 0.0032 | 0.0693 | 0.9250 | 0.0085 | 0.0665 | 1.005 | 0.1479 | 0.577 | 0.000 | 15.1 | 1.196 | n/a | 68.6 | 0.998 | 0.9255 |
| T2 | h5 | carried_margin | 2.8757 | 2.8864 | 0.0108 | 0.3021 | 0.9290 | 0.0105 | 0.0605 | 1.002 | 0.6486 | 0.543 | 0.000 | 15.1 | 1.175 | n/a | n/a | 0.998 | 0.9295 |
| T2 | h5 | own_margin | 4.9161 | 4.9156 | -0.0005 | 0.0713 | 0.9445 | 0.0430 | 0.0125 | 1.049 | 0.1550 | 0.528 | 0.032 | 13.8 | 1.024 | n/a | n/a | 0.998 | 0.9450 |
| T2 | h5 | kappa | 0.9395 | 0.9402 | 0.0006 | 0.0083 | 0.9340 | 0.0385 | 0.0275 | 0.952 | 0.0172 | 0.546 | 0.000 | 15.1 | 1.111 | n/a | 8.9 | 0.998 | 0.9345 |
| T2 | h5 | shuffled_vs_yardstick | -0.5041 | -0.5047 | -0.0006 | 0.0711 | 0.9250 | 0.0690 | 0.0060 | 1.117 | 0.1895 | 0.166 | 0.603 | 6.4 | 1.270 | n/a | n/a | 0.998 | 0.9255 |
| T2 | h5 | carried_added | 3.0607 | 3.0732 | 0.0124 | 0.3480 | 0.9280 | 0.0105 | 0.0615 | 0.999 | 0.7464 | 0.543 | 0.000 | 15.1 | 1.179 | n/a | n/a | 0.998 | 0.9285 |
| T2 | h5 | pooled_retention | 0.6000 | 0.6025 | 0.0025 | 0.0680 | 0.9270 | 0.0105 | 0.0625 | 0.999 | 0.1461 | 0.564 | 0.000 | 15.0 | 1.170 | n/a | 139.2 | 0.998 | 0.9275 |
| T2 | h10 | large | 5.8435 | 5.0093 | -0.8341 | 0.3835 | 0.6149 | 0.0000 | 0.3851 | 1.754 | 1.0600 | 0.558 | 0.000 | 15.1 | 3.533 | n/a | n/a | 0.017 | 0.9250 |
| T2 | h10 | carries | 0.6000 | 0.5135 | -0.0865 | 0.0390 | 0.6269 | 0.0000 | 0.3731 | 1.788 | 0.1102 | 0.561 | 0.000 | 15.1 | 3.796 | n/a | 118.0 | 0.017 | 0.9245 |
| T2 | h10 | depends | 0.5931 | 0.5079 | -0.0852 | 0.0382 | 0.6239 | 0.0000 | 0.3761 | 1.795 | 0.1084 | 0.555 | 0.000 | 15.1 | 3.770 | n/a | 106.8 | 0.017 | 0.9245 |
| T2 | h10 | carried_margin | 6.3475 | 5.4681 | -0.8794 | 0.3938 | 0.6179 | 0.0000 | 0.3821 | 1.792 | 1.1161 | 0.567 | 0.000 | 15.1 | 3.942 | n/a | n/a | 0.017 | 0.9255 |
| T2 | h10 | own_margin | 10.7031 | 10.7697 | 0.0666 | 0.0909 | 0.9343 | 0.0657 | 0.0000 | 1.668 | 0.2246 | 0.463 | 0.293 | 9.9 | 1.049 | n/a | n/a | 0.017 | 0.9640 |
| T2 | h10 | kappa | 0.9717 | 0.9775 | 0.0058 | 0.0030 | 0.7313 | 0.2687 | 0.0000 | 1.559 | 0.0082 | 0.543 | 0.000 | 15.1 | 3.260 | n/a | 10.2 | 0.017 | 0.9340 |
| T2 | h10 | shuffled_vs_yardstick | -0.5041 | -0.4588 | 0.0453 | 0.0473 | 0.7343 | 0.2657 | 0.0000 | 0.851 | 0.0905 | 0.039 | 0.403 | 10.5 | 2.083 | n/a | n/a | 0.017 | 0.8630 |
| T2 | h10 | carried_added | 6.5326 | 5.5952 | -0.9374 | 0.4196 | 0.6179 | 0.0000 | 0.3821 | 1.790 | 1.1872 | 0.567 | 0.000 | 15.1 | 4.004 | n/a | n/a | 0.017 | 0.9255 |
| T2 | h10 | pooled_retention | 0.6000 | 0.5137 | -0.0863 | 0.0383 | 0.6239 | 0.0000 | 0.3761 | 1.796 | 0.1088 | 0.543 | 0.000 | 15.1 | 3.984 | n/a | 126.4 | 0.017 | 0.9270 |
| T3 | n20 | large | -0.1809 | -0.1816 | -0.0007 | 0.0378 | 0.9340 | 0.0615 | 0.0045 | 1.210 | 0.0801 | 0.488 | 0.184 | 11.1 | 1.118 | n/a | n/a | n/a | n/a |
| T3 | n20 | carries | 0.6997 | 0.7003 | 0.0006 | 0.0398 | 0.9665 | 0.0070 | 0.0265 | 1.328 | 0.0911 | 0.577 | 0.152 | 11.8 | 0.898 | n/a | 8.5 | n/a | n/a |
| T3 | n20 | depends | 0.5674 | 0.5680 | 0.0006 | 0.0552 | 0.9765 | 0.0085 | 0.0150 | 1.254 | 0.1231 | 0.579 | 0.137 | 12.0 | 0.829 | n/a | 9.1 | n/a | n/a |
| T3 | n20 | carried_margin | 0.2372 | 0.2370 | -0.0002 | 0.0334 | 0.9310 | 0.0140 | 0.0550 | 0.995 | 0.0818 | 0.073 | 0.773 | 5.5 | 1.135 | n/a | n/a | n/a | n/a |
| T3 | n20 | own_margin | 0.4181 | 0.4186 | 0.0005 | 0.0548 | 0.9205 | 0.0130 | 0.0665 | 1.001 | 0.1342 | 0.114 | 0.683 | 5.9 | 1.265 | n/a | n/a | n/a | n/a |
| T3 | n20 | kappa | 0.5629 | 0.5640 | 0.0010 | 0.0617 | 0.9140 | 0.0720 | 0.0140 | 0.952 | 0.1287 | 0.075 | 0.069 | 14.5 | 1.264 | n/a | 8.2 | n/a | n/a |
| T3 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4186 | -0.0005 | 0.0548 | 0.9205 | 0.0665 | 0.0130 | 1.001 | 0.1342 | 0.114 | 0.683 | 5.9 | 1.265 | n/a | n/a | n/a | n/a |
| T3 | n20 | carried_added | 0.4214 | 0.4220 | 0.0006 | 0.0529 | 0.9335 | 0.0055 | 0.0610 | 1.031 | 0.1108 | 0.073 | 0.144 | 13.3 | 1.121 | n/a | n/a | n/a | n/a |
| T3 | n20 | pooled_retention | 0.6997 | 0.7074 | 0.0077 | 0.0900 | 0.9390 | 0.0135 | 0.0475 | 0.982 | 0.1876 | 0.698 | 0.000 | 15.1 | 1.065 | n/a | 8.6 | n/a | n/a |
| T3 | n40 | large | 0.8233 | 0.8242 | 0.0009 | 0.1749 | 0.9295 | 0.0010 | 0.0695 | 1.093 | 0.3659 | 0.329 | 0.066 | 12.6 | 1.162 | n/a | n/a | n/a | n/a |
| T3 | n40 | carries | 0.7170 | 0.7178 | 0.0008 | 0.0889 | 0.9580 | 0.0065 | 0.0355 | 1.159 | 0.1984 | 0.616 | 0.018 | 13.8 | 0.953 | n/a | 8.1 | n/a | n/a |
| T3 | n40 | depends | 0.6881 | 0.6897 | 0.0015 | 0.0955 | 0.9560 | 0.0050 | 0.0390 | 1.166 | 0.2128 | 0.613 | 0.018 | 13.8 | 0.972 | n/a | 8.0 | n/a | n/a |
| T3 | n40 | carried_margin | 1.2414 | 1.2428 | 0.0014 | 0.2030 | 0.9340 | 0.0010 | 0.0650 | 1.059 | 0.4170 | 0.147 | 0.175 | 11.4 | 1.175 | n/a | n/a | n/a | n/a |
| T3 | n40 | own_margin | 1.8041 | 1.8116 | 0.0075 | 0.2412 | 0.9335 | 0.0130 | 0.0535 | 1.013 | 0.5018 | 0.164 | 0.265 | 10.2 | 1.078 | n/a | n/a | n/a | n/a |
| T3 | n40 | kappa | 0.8708 | 0.8700 | -0.0008 | 0.0218 | 0.9380 | 0.0485 | 0.0135 | 0.987 | 0.0459 | 0.146 | 0.070 | 13.5 | 1.063 | n/a | 6.6 | n/a | n/a |
| T3 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4186 | -0.0005 | 0.0547 | 0.9200 | 0.0665 | 0.0135 | 1.001 | 0.1344 | 0.116 | 0.683 | 5.9 | 1.259 | n/a | n/a | n/a | n/a |
| T3 | n40 | carried_added | 1.4256 | 1.4278 | 0.0022 | 0.2253 | 0.9290 | 0.0015 | 0.0695 | 1.056 | 0.4654 | 0.148 | 0.103 | 12.7 | 1.125 | n/a | n/a | n/a | n/a |
| T3 | n40 | pooled_retention | 0.7170 | 0.7212 | 0.0042 | 0.0870 | 0.9340 | 0.0085 | 0.0575 | 1.013 | 0.1844 | 0.651 | 0.000 | 15.1 | 1.114 | n/a | 8.1 | n/a | n/a |
| T3 | n80 | large | 6.8973 | 6.9049 | 0.0076 | 1.2744 | 0.9485 | 0.0065 | 0.0450 | 1.053 | 2.7996 | 0.146 | 0.283 | 9.8 | 1.006 | n/a | n/a | n/a | n/a |
| T3 | n80 | carries | 0.7597 | 0.7632 | 0.0035 | 0.1275 | 0.9540 | 0.0025 | 0.0435 | 1.173 | 0.2815 | 0.620 | 0.025 | 13.7 | 0.985 | n/a | 7.9 | n/a | n/a |
| T3 | n80 | depends | 0.7552 | 0.7591 | 0.0039 | 0.1293 | 0.9545 | 0.0020 | 0.0435 | 1.178 | 0.2853 | 0.623 | 0.025 | 13.7 | 0.975 | n/a | 7.7 | n/a | n/a |
| T3 | n80 | carried_margin | 7.3154 | 7.3235 | 0.0081 | 1.3107 | 0.9480 | 0.0070 | 0.0450 | 1.050 | 2.8878 | 0.133 | 0.306 | 9.6 | 1.011 | n/a | n/a | n/a | n/a |
| T3 | n80 | own_margin | 9.6872 | 9.7245 | 0.0373 | 1.3358 | 0.9300 | 0.0195 | 0.0505 | 1.038 | 3.6543 | 0.141 | 0.650 | 6.3 | 1.154 | n/a | n/a | n/a | n/a |
| T3 | n80 | kappa | 0.9754 | 0.9751 | -0.0003 | 0.0047 | 0.9470 | 0.0470 | 0.0060 | 1.053 | 0.0101 | 0.132 | 0.224 | 10.7 | 1.021 | n/a | 5.8 | n/a | n/a |
| T3 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4186 | -0.0005 | 0.0547 | 0.9220 | 0.0645 | 0.0135 | 1.001 | 0.1343 | 0.113 | 0.684 | 5.9 | 1.274 | n/a | n/a | n/a | n/a |
| T3 | n80 | carried_added | 7.4996 | 7.5085 | 0.0089 | 1.3326 | 0.9495 | 0.0065 | 0.0440 | 1.049 | 2.9220 | 0.133 | 0.289 | 9.9 | 1.001 | n/a | n/a | n/a | n/a |
| T3 | n80 | pooled_retention | 0.7597 | 0.7605 | 0.0007 | 0.0805 | 0.9000 | 0.0050 | 0.0950 | 1.053 | 0.1732 | 0.744 | 0.000 | 15.1 | 1.499 | n/a | 7.9 | n/a | n/a |
| T3 | n160 | large | 16.1075 | 16.1473 | 0.0398 | 2.0840 | 0.9455 | 0.0075 | 0.0470 | 1.068 | 4.5288 | 0.522 | 0.005 | 14.8 | 1.035 | n/a | n/a | n/a | n/a |
| T3 | n160 | carries | 0.7709 | 0.7786 | 0.0077 | 0.1288 | 0.9325 | 0.0010 | 0.0665 | 1.122 | 0.2741 | 0.600 | 0.005 | 14.7 | 1.182 | n/a | 16.2 | n/a | n/a |
| T3 | n160 | depends | 0.7690 | 0.7770 | 0.0080 | 0.1296 | 0.9330 | 0.0005 | 0.0665 | 1.125 | 0.2753 | 0.600 | 0.005 | 14.7 | 1.179 | n/a | 15.7 | n/a | n/a |
| T3 | n160 | carried_margin | 16.5256 | 16.5659 | 0.0403 | 2.1014 | 0.9440 | 0.0075 | 0.0485 | 1.066 | 4.5600 | 0.508 | 0.005 | 14.8 | 1.032 | n/a | n/a | n/a | n/a |
| T3 | n160 | own_margin | 21.4901 | 21.4794 | -0.0107 | 1.3082 | 0.9575 | 0.0300 | 0.0125 | 1.192 | 2.9990 | 0.505 | 0.132 | 11.7 | 0.963 | n/a | n/a | n/a | n/a |
| T3 | n160 | kappa | 0.9890 | 0.9890 | 0.0000 | 0.0016 | 0.9270 | 0.0695 | 0.0035 | 1.039 | 0.0033 | 0.510 | 0.001 | 15.1 | 1.259 | n/a | 7.7 | n/a | n/a |
| T3 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4186 | -0.0005 | 0.0548 | 0.9185 | 0.0680 | 0.0135 | 1.001 | 0.1348 | 0.115 | 0.683 | 5.9 | 1.274 | n/a | n/a | n/a | n/a |
| T3 | n160 | carried_added | 16.7098 | 16.7509 | 0.0411 | 2.1320 | 0.9440 | 0.0075 | 0.0485 | 1.065 | 4.6226 | 0.508 | 0.005 | 14.8 | 1.040 | n/a | n/a | n/a | n/a |
| T3 | n160 | pooled_retention | 0.7709 | 0.7717 | 0.0008 | 0.0787 | 0.8920 | 0.0045 | 0.1035 | 1.064 | 0.1705 | 0.577 | 0.000 | 15.1 | 1.726 | n/a | 16.1 | n/a | n/a |
| T3 | n320 | large | 18.8086 | 18.8668 | 0.0583 | 2.3949 | 0.9445 | 0.0060 | 0.0495 | 1.061 | 5.1922 | 0.579 | 0.003 | 15.0 | 1.036 | n/a | n/a | n/a | n/a |
| T3 | n320 | carries | 0.7708 | 0.7795 | 0.0086 | 0.1281 | 0.9260 | 0.0010 | 0.0730 | 1.110 | 0.2716 | 0.586 | 0.004 | 14.9 | 1.180 | n/a | 17.5 | n/a | n/a |
| T3 | n320 | depends | 0.7691 | 0.7780 | 0.0089 | 0.1288 | 0.9260 | 0.0010 | 0.0730 | 1.111 | 0.2727 | 0.586 | 0.004 | 14.9 | 1.177 | n/a | 17.0 | n/a | n/a |
| T3 | n320 | carried_margin | 19.2267 | 19.2854 | 0.0588 | 2.4077 | 0.9425 | 0.0065 | 0.0510 | 1.061 | 5.2245 | 0.574 | 0.003 | 15.0 | 1.033 | n/a | n/a | n/a | n/a |
| T3 | n320 | own_margin | 24.9973 | 24.9618 | -0.0355 | 1.3501 | 0.9640 | 0.0285 | 0.0075 | 1.251 | 3.2114 | 0.577 | 0.088 | 12.6 | 0.933 | n/a | n/a | n/a | n/a |
| T3 | n320 | kappa | 0.9905 | 0.9905 | 0.0000 | 0.0013 | 0.9205 | 0.0745 | 0.0050 | 1.022 | 0.0028 | 0.577 | 0.001 | 15.2 | 1.250 | n/a | 7.9 | n/a | n/a |
| T3 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4186 | -0.0005 | 0.0547 | 0.9195 | 0.0680 | 0.0125 | 1.002 | 0.1343 | 0.115 | 0.682 | 5.9 | 1.250 | n/a | n/a | n/a | n/a |
| T3 | n320 | carried_added | 19.4109 | 19.4705 | 0.0596 | 2.4387 | 0.9410 | 0.0065 | 0.0525 | 1.060 | 5.2807 | 0.573 | 0.003 | 15.0 | 1.044 | n/a | n/a | n/a | n/a |
| T3 | n320 | pooled_retention | 0.7708 | 0.7718 | 0.0010 | 0.0787 | 0.8920 | 0.0040 | 0.1040 | 1.065 | 0.1706 | 0.555 | 0.000 | 15.1 | 1.747 | n/a | 17.3 | n/a | n/a |
| T3 | h2 | large | 0.8269 | 0.8290 | 0.0021 | 0.1157 | 0.9455 | 0.0070 | 0.0475 | 1.027 | 0.2406 | 0.162 | 0.014 | 15.1 | 1.022 | n/a | n/a | 1.000 | 0.9455 |
| T3 | h2 | carries | 0.7470 | 0.7480 | 0.0011 | 0.0761 | 0.9060 | 0.0050 | 0.0890 | 1.036 | 0.1624 | 0.599 | 0.000 | 15.1 | 1.374 | n/a | 115.3 | 1.000 | 0.9060 |
| T3 | h2 | depends | 0.7200 | 0.7227 | 0.0027 | 0.0795 | 0.9130 | 0.0030 | 0.0840 | 1.055 | 0.1677 | 0.598 | 0.000 | 15.1 | 1.321 | n/a | 53.8 | 1.000 | 0.9130 |
| T3 | h2 | carried_margin | 1.2453 | 1.2476 | 0.0024 | 0.1175 | 0.9235 | 0.0060 | 0.0705 | 1.041 | 0.2517 | 0.510 | 0.000 | 15.1 | 1.200 | n/a | n/a | 1.000 | 0.9235 |
| T3 | h2 | own_margin | 1.7295 | 1.7293 | -0.0001 | 0.0323 | 0.9145 | 0.0825 | 0.0030 | 1.041 | 0.0685 | 0.444 | 0.002 | 15.1 | 1.249 | n/a | n/a | 1.000 | 0.9145 |
| T3 | h2 | kappa | 0.8711 | 0.8721 | 0.0009 | 0.0160 | 0.8990 | 0.0900 | 0.0110 | 0.976 | 0.0341 | 0.510 | 0.000 | 15.1 | 1.623 | n/a | 9.3 | 1.000 | 0.8990 |
| T3 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4186 | -0.0003 | 0.0548 | 0.9200 | 0.0665 | 0.0135 | 1.001 | 0.1344 | 0.114 | 0.684 | 5.9 | 1.251 | n/a | n/a | 1.000 | 0.9200 |
| T3 | h2 | carried_added | 1.4295 | 1.4327 | 0.0032 | 0.1528 | 0.9050 | 0.0050 | 0.0900 | 1.043 | 0.3266 | 0.509 | 0.000 | 15.1 | 1.455 | n/a | n/a | 1.000 | 0.9050 |
| T3 | h2 | pooled_retention | 0.7470 | 0.7489 | 0.0019 | 0.0815 | 0.9070 | 0.0060 | 0.0870 | 1.038 | 0.1738 | 0.569 | 0.000 | 15.0 | 1.331 | n/a | 115.6 | 1.000 | 0.9070 |
| T3 | h5 | large | 3.2326 | 3.2404 | 0.0078 | 0.3742 | 0.9245 | 0.0070 | 0.0685 | 1.048 | 0.7991 | 0.409 | 0.000 | 15.3 | 1.181 | n/a | n/a | 0.996 | 0.9245 |
| T3 | h5 | carries | 0.7489 | 0.7509 | 0.0020 | 0.0839 | 0.9095 | 0.0045 | 0.0860 | 1.052 | 0.1793 | 0.575 | 0.000 | 15.1 | 1.357 | n/a | 148.0 | 0.996 | 0.9095 |
| T3 | h5 | depends | 0.7395 | 0.7421 | 0.0026 | 0.0855 | 0.9100 | 0.0035 | 0.0865 | 1.059 | 0.1821 | 0.575 | 0.000 | 15.1 | 1.332 | n/a | 77.3 | 0.996 | 0.9100 |
| T3 | h5 | carried_margin | 3.6509 | 3.6589 | 0.0080 | 0.3852 | 0.9180 | 0.0065 | 0.0755 | 1.048 | 0.8265 | 0.536 | 0.000 | 15.1 | 1.228 | n/a | n/a | 0.996 | 0.9180 |
| T3 | h5 | own_margin | 4.9368 | 4.9358 | -0.0010 | 0.0614 | 0.9445 | 0.0515 | 0.0040 | 1.142 | 0.1404 | 0.525 | 0.065 | 13.1 | 1.037 | n/a | n/a | 0.996 | 0.9435 |
| T3 | h5 | kappa | 0.9520 | 0.9523 | 0.0003 | 0.0061 | 0.9055 | 0.0865 | 0.0080 | 0.986 | 0.0129 | 0.537 | 0.000 | 15.1 | 1.513 | n/a | 9.0 | 0.996 | 0.9045 |
| T3 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4185 | -0.0002 | 0.0546 | 0.9150 | 0.0710 | 0.0140 | 1.057 | 0.1403 | 0.154 | 0.662 | 5.9 | 1.345 | n/a | n/a | 0.996 | 0.9140 |
| T3 | h5 | carried_added | 3.8351 | 3.8440 | 0.0089 | 0.4203 | 0.9100 | 0.0060 | 0.0840 | 1.049 | 0.9005 | 0.537 | 0.000 | 15.1 | 1.307 | n/a | n/a | 0.996 | 0.9100 |
| T3 | h5 | pooled_retention | 0.7489 | 0.7507 | 0.0018 | 0.0813 | 0.9055 | 0.0060 | 0.0885 | 1.046 | 0.1740 | 0.570 | 0.000 | 15.1 | 1.353 | n/a | 149.5 | 0.996 | 0.9055 |
| T3 | h10 | large | 7.8013 | 7.4173 | -0.3840 | 0.5639 | 0.7895 | 0.0000 | 0.2105 | 1.468 | 1.4033 | 0.561 | 0.000 | 15.2 | 2.017 | n/a | n/a | 0.197 | 0.8980 |
| T3 | h10 | carries | 0.7712 | 0.7321 | -0.0391 | 0.0552 | 0.7830 | 0.0000 | 0.2170 | 1.482 | 0.1385 | 0.570 | 0.001 | 15.1 | 2.098 | n/a | 121.9 | 0.197 | 0.8960 |
| T3 | h10 | depends | 0.7672 | 0.7283 | -0.0390 | 0.0554 | 0.7840 | 0.0000 | 0.2160 | 1.488 | 0.1389 | 0.569 | 0.001 | 15.1 | 2.088 | n/a | 109.3 | 0.197 | 0.8960 |
| T3 | h10 | carried_margin | 8.2196 | 7.8202 | -0.3995 | 0.5707 | 0.7825 | 0.0000 | 0.2175 | 1.478 | 1.4304 | 0.536 | 0.001 | 15.2 | 2.076 | n/a | n/a | 0.197 | 0.8960 |
| T3 | h10 | own_margin | 10.7131 | 10.7410 | 0.0279 | 0.0995 | 0.9505 | 0.0385 | 0.0110 | 1.362 | 0.2187 | 0.494 | 0.275 | 10.3 | 0.989 | n/a | n/a | 0.197 | 0.9605 |
| T3 | h10 | kappa | 0.9781 | 0.9804 | 0.0023 | 0.0020 | 0.7545 | 0.2455 | 0.0000 | 1.304 | 0.0051 | 0.544 | 0.000 | 15.2 | 2.531 | n/a | 11.3 | 0.197 | 0.8885 |
| T3 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4029 | 0.0155 | 0.0440 | 0.8715 | 0.1270 | 0.0015 | 0.787 | 0.0853 | 0.032 | 0.613 | 8.1 | 1.510 | n/a | n/a | 0.197 | 0.8790 |
| T3 | h10 | carried_added | 8.4038 | 7.9777 | -0.4261 | 0.5967 | 0.7790 | 0.0000 | 0.2210 | 1.477 | 1.4959 | 0.535 | 0.000 | 15.2 | 2.129 | n/a | n/a | 0.197 | 0.8950 |
| T3 | h10 | pooled_retention | 0.7712 | 0.7318 | -0.0394 | 0.0543 | 0.7760 | 0.0000 | 0.2240 | 1.482 | 0.1366 | 0.568 | 0.000 | 15.1 | 2.167 | n/a | 121.7 | 0.197 | 0.8935 |
| T4 | n20 | large | -0.2628 | -0.2591 | 0.0037 | 0.0809 | 0.8945 | 0.1035 | 0.0020 | 1.020 | 0.1560 | 0.314 | 0.273 | 10.1 | 1.344 | n/a | n/a | n/a | n/a |
| T4 | n20 | carries | 0.6000 | 0.6050 | 0.0050 | 0.0720 | 0.9205 | 0.0025 | 0.0770 | 1.107 | 0.1565 | 0.689 | 0.029 | 13.9 | 1.233 | n/a | 5.2 | n/a | n/a |
| T4 | n20 | depends | 0.4441 | 0.4404 | -0.0037 | 0.1094 | 0.9115 | 0.0055 | 0.0830 | 1.015 | 0.2275 | 0.424 | 0.067 | 12.9 | 1.254 | n/a | 4.2 | n/a | n/a |
| T4 | n20 | carried_margin | 0.2100 | 0.2116 | 0.0016 | 0.0901 | 0.9065 | 0.0030 | 0.0905 | 1.023 | 0.1840 | 0.004 | 0.840 | 6.5 | 1.401 | n/a | n/a | n/a | n/a |
| T4 | n20 | own_margin | 0.4727 | 0.4707 | -0.0021 | 0.1376 | 0.9070 | 0.0045 | 0.0885 | 0.980 | 0.3036 | 0.007 | 0.971 | 4.2 | 1.306 | n/a | n/a | n/a | n/a |
| T4 | n20 | kappa | 0.5327 | 0.5181 | -0.0146 | 0.1167 | 0.9350 | 0.0390 | 0.0260 | 0.925 | 0.2378 | 0.005 | 0.555 | 10.0 | 1.078 | n/a | 4.6 | n/a | n/a |
| T4 | n20 | shuffled_vs_yardstick | -0.4727 | -0.4707 | 0.0021 | 0.1376 | 0.9070 | 0.0885 | 0.0045 | 0.980 | 0.3036 | 0.007 | 0.971 | 4.2 | 1.306 | n/a | n/a | n/a | n/a |
| T4 | n20 | carried_added | 0.3941 | 0.3951 | 0.0010 | 0.1003 | 0.8935 | 0.0020 | 0.1045 | 0.982 | 0.1917 | 0.005 | 0.654 | 9.0 | 1.429 | n/a | n/a | n/a | n/a |
| T4 | n20 | pooled_retention | 0.6000 | 0.5992 | -0.0008 | 0.0588 | 0.8775 | 0.0045 | 0.1180 | 1.064 | 0.1279 | 0.964 | 0.000 | 15.0 | 2.173 | n/a | 5.1 | n/a | n/a |
| T4 | n40 | large | 0.7084 | 0.7127 | 0.0043 | 0.2753 | 0.8940 | 0.0020 | 0.1040 | 0.993 | 0.4504 | 0.114 | 0.374 | 9.2 | 1.414 | n/a | n/a | n/a | n/a |
| T4 | n40 | carries | 0.6000 | 0.6080 | 0.0080 | 0.0860 | 0.9610 | 0.0085 | 0.0305 | 1.165 | 0.1893 | 0.680 | 0.035 | 13.8 | 0.923 | n/a | 4.8 | n/a | n/a |
| T4 | n40 | depends | 0.5648 | 0.5717 | 0.0070 | 0.0914 | 0.9575 | 0.0060 | 0.0365 | 1.161 | 0.1999 | 0.680 | 0.039 | 13.7 | 0.939 | n/a | 4.5 | n/a | n/a |
| T4 | n40 | carried_margin | 1.1811 | 1.1834 | 0.0023 | 0.3875 | 0.8870 | 0.0015 | 0.1115 | 0.987 | 0.6867 | 0.009 | 0.797 | 6.9 | 1.495 | n/a | n/a | n/a | n/a |
| T4 | n40 | own_margin | 2.0914 | 2.0725 | -0.0189 | 0.5941 | 0.8825 | 0.0050 | 0.1125 | 0.996 | 1.1476 | 0.010 | 0.890 | 5.3 | 1.518 | n/a | n/a | n/a | n/a |
| T4 | n40 | kappa | 0.8651 | 0.8582 | -0.0069 | 0.0392 | 0.9465 | 0.0355 | 0.0180 | 0.872 | 0.0775 | 0.008 | 0.644 | 8.7 | 1.019 | n/a | 4.4 | n/a | n/a |
| T4 | n40 | shuffled_vs_yardstick | -0.4727 | -0.4707 | 0.0021 | 0.1376 | 0.9080 | 0.0875 | 0.0045 | 0.980 | 0.3038 | 0.006 | 0.971 | 4.2 | 1.305 | n/a | n/a | n/a | n/a |
| T4 | n40 | carried_added | 1.3653 | 1.3669 | 0.0016 | 0.4016 | 0.8875 | 0.0020 | 0.1105 | 0.977 | 0.6992 | 0.009 | 0.710 | 7.9 | 1.473 | n/a | n/a | n/a | n/a |
| T4 | n40 | pooled_retention | 0.6000 | 0.5989 | -0.0011 | 0.0589 | 0.8780 | 0.0045 | 0.1175 | 1.058 | 0.1277 | 0.961 | 0.000 | 15.0 | 2.173 | n/a | 4.8 | n/a | n/a |
| T4 | n80 | large | 5.5237 | 5.4915 | -0.0323 | 1.4343 | 0.9230 | 0.0145 | 0.0625 | 0.977 | 3.3916 | 0.014 | 0.844 | 5.9 | 1.204 | n/a | n/a | n/a | n/a |
| T4 | n80 | carries | 0.6000 | 0.6015 | 0.0015 | 0.0963 | 0.9380 | 0.0030 | 0.0590 | 1.157 | 0.2108 | 0.670 | 0.029 | 13.7 | 1.090 | n/a | 4.5 | n/a | n/a |
| T4 | n80 | depends | 0.5927 | 0.5941 | 0.0014 | 0.0969 | 0.9365 | 0.0030 | 0.0605 | 1.160 | 0.2116 | 0.671 | 0.030 | 13.7 | 1.083 | n/a | 4.4 | n/a | n/a |
| T4 | n80 | carried_margin | 5.9964 | 5.9621 | -0.0343 | 1.5508 | 0.9235 | 0.0130 | 0.0635 | 0.974 | 3.6938 | 0.011 | 0.878 | 5.7 | 1.193 | n/a | n/a | n/a | n/a |
| T4 | n80 | own_margin | 10.1169 | 10.1011 | -0.0158 | 2.3568 | 0.9245 | 0.0200 | 0.0555 | 0.998 | 6.3368 | 0.011 | 0.956 | 4.2 | 1.188 | n/a | n/a | n/a | n/a |
| T4 | n80 | kappa | 0.9702 | 0.9687 | -0.0015 | 0.0087 | 0.9340 | 0.0520 | 0.0140 | 0.969 | 0.0183 | 0.011 | 0.818 | 6.6 | 1.121 | n/a | 4.2 | n/a | n/a |
| T4 | n80 | shuffled_vs_yardstick | -0.4727 | -0.4707 | 0.0021 | 0.1376 | 0.9075 | 0.0880 | 0.0045 | 0.980 | 0.3035 | 0.007 | 0.971 | 4.2 | 1.311 | n/a | n/a | n/a | n/a |
| T4 | n80 | carried_added | 6.1806 | 6.1456 | -0.0350 | 1.5675 | 0.9245 | 0.0125 | 0.0630 | 0.973 | 3.6970 | 0.011 | 0.862 | 5.9 | 1.182 | n/a | n/a | n/a | n/a |
| T4 | n80 | pooled_retention | 0.6000 | 0.5990 | -0.0010 | 0.0587 | 0.8760 | 0.0045 | 0.1195 | 1.064 | 0.1277 | 0.968 | 0.000 | 15.0 | 2.178 | n/a | 4.6 | n/a | n/a |
| T4 | n160 | large | 12.1058 | 12.0533 | -0.0525 | 1.5232 | 0.9375 | 0.0050 | 0.0575 | 1.029 | 3.2638 | 0.357 | 0.051 | 13.5 | 1.103 | n/a | n/a | n/a | n/a |
| T4 | n160 | carries | 0.6000 | 0.6013 | 0.0013 | 0.0940 | 0.9115 | 0.0020 | 0.0865 | 1.124 | 0.2013 | 0.597 | 0.011 | 14.5 | 1.350 | n/a | 13.9 | n/a | n/a |
| T4 | n160 | depends | 0.5965 | 0.5980 | 0.0015 | 0.0941 | 0.9125 | 0.0015 | 0.0860 | 1.126 | 0.2012 | 0.596 | 0.011 | 14.5 | 1.341 | n/a | 13.5 | n/a | n/a |
| T4 | n160 | carried_margin | 12.5785 | 12.5240 | -0.0545 | 1.5878 | 0.9340 | 0.0065 | 0.0595 | 1.010 | 3.3637 | 0.293 | 0.069 | 13.1 | 1.095 | n/a | n/a | n/a | n/a |
| T4 | n160 | own_margin | 21.0870 | 21.0890 | 0.0020 | 1.6392 | 0.9410 | 0.0415 | 0.0175 | 1.081 | 3.8099 | 0.281 | 0.373 | 8.9 | 1.078 | n/a | n/a | n/a | n/a |
| T4 | n160 | kappa | 0.9856 | 0.9856 | 0.0001 | 0.0020 | 0.9220 | 0.0700 | 0.0080 | 1.055 | 0.0043 | 0.301 | 0.036 | 14.1 | 1.198 | n/a | 8.0 | n/a | n/a |
| T4 | n160 | shuffled_vs_yardstick | -0.4727 | -0.4707 | 0.0021 | 0.1376 | 0.9070 | 0.0885 | 0.0045 | 0.980 | 0.3033 | 0.006 | 0.971 | 4.2 | 1.301 | n/a | n/a | n/a | n/a |
| T4 | n160 | carried_added | 12.7627 | 12.7075 | -0.0552 | 1.6190 | 0.9325 | 0.0060 | 0.0615 | 1.010 | 3.4308 | 0.294 | 0.066 | 13.3 | 1.098 | n/a | n/a | n/a | n/a |
| T4 | n160 | pooled_retention | 0.6000 | 0.5990 | -0.0010 | 0.0587 | 0.8765 | 0.0050 | 0.1185 | 1.055 | 0.1274 | 0.675 | 0.000 | 15.0 | 2.254 | n/a | 13.9 | n/a | n/a |
| T4 | n320 | large | 14.3285 | 14.2637 | -0.0648 | 1.6079 | 0.9250 | 0.0035 | 0.0715 | 1.114 | 3.5765 | 0.561 | 0.008 | 14.7 | 1.180 | n/a | n/a | n/a | n/a |
| T4 | n320 | carries | 0.6000 | 0.6014 | 0.0014 | 0.0926 | 0.9110 | 0.0015 | 0.0875 | 1.137 | 0.1992 | 0.589 | 0.005 | 14.7 | 1.400 | n/a | 17.4 | n/a | n/a |
| T4 | n320 | depends | 0.5970 | 0.5985 | 0.0015 | 0.0927 | 0.9110 | 0.0010 | 0.0880 | 1.140 | 0.1991 | 0.589 | 0.005 | 14.7 | 1.395 | n/a | 16.9 | n/a | n/a |
| T4 | n320 | carried_margin | 14.8012 | 14.7344 | -0.0669 | 1.6371 | 0.9240 | 0.0040 | 0.0720 | 1.100 | 3.6155 | 0.554 | 0.007 | 14.7 | 1.200 | n/a | n/a | n/a | n/a |
| T4 | n320 | own_margin | 24.7915 | 24.7884 | -0.0031 | 1.3629 | 0.9605 | 0.0345 | 0.0050 | 1.239 | 3.2057 | 0.548 | 0.100 | 12.3 | 0.923 | n/a | n/a | n/a | n/a |
| T4 | n320 | kappa | 0.9877 | 0.9878 | 0.0001 | 0.0016 | 0.9085 | 0.0825 | 0.0090 | 1.027 | 0.0034 | 0.558 | 0.002 | 15.1 | 1.389 | n/a | 8.7 | n/a | n/a |
| T4 | n320 | shuffled_vs_yardstick | -0.4727 | -0.4706 | 0.0021 | 0.1376 | 0.9075 | 0.0880 | 0.0045 | 0.980 | 0.3035 | 0.006 | 0.971 | 4.2 | 1.317 | n/a | n/a | n/a | n/a |
| T4 | n320 | carried_added | 14.9854 | 14.9179 | -0.0675 | 1.6715 | 0.9230 | 0.0040 | 0.0730 | 1.098 | 3.6883 | 0.554 | 0.007 | 14.8 | 1.223 | n/a | n/a | n/a | n/a |
| T4 | n320 | pooled_retention | 0.6000 | 0.5990 | -0.0010 | 0.0587 | 0.8775 | 0.0045 | 0.1180 | 1.058 | 0.1273 | 0.536 | 0.000 | 15.1 | 2.257 | n/a | 17.3 | n/a | n/a |
| T4 | h2 | large | 0.4942 | 0.4959 | 0.0017 | 0.1351 | 0.9555 | 0.0345 | 0.0100 | 1.043 | 0.2883 | 0.011 | 0.738 | 7.3 | 0.970 | n/a | n/a | 1.000 | 0.9555 |
| T4 | h2 | carries | 0.6000 | 0.5992 | -0.0008 | 0.0559 | 0.8785 | 0.0045 | 0.1170 | 1.044 | 0.1206 | 0.577 | 0.000 | 15.1 | 2.047 | n/a | 97.2 | 1.000 | 0.8785 |
| T4 | h2 | depends | 0.5575 | 0.5580 | 0.0005 | 0.0528 | 0.8790 | 0.0030 | 0.1180 | 1.066 | 0.1123 | 0.569 | 0.000 | 15.1 | 2.046 | n/a | 50.9 | 1.000 | 0.8790 |
| T4 | h2 | carried_margin | 0.9671 | 0.9666 | -0.0005 | 0.0755 | 0.8790 | 0.0055 | 0.1155 | 1.036 | 0.1617 | 0.306 | 0.000 | 15.4 | 1.911 | n/a | n/a | 1.000 | 0.8790 |
| T4 | h2 | own_margin | 1.7346 | 1.7348 | 0.0002 | 0.0339 | 0.9400 | 0.0515 | 0.0085 | 1.096 | 0.0729 | 0.172 | 0.045 | 14.4 | 1.032 | n/a | n/a | 1.000 | 0.9400 |
| T4 | h2 | kappa | 0.8400 | 0.8422 | 0.0022 | 0.0185 | 0.8750 | 0.1130 | 0.0120 | 0.988 | 0.0401 | 0.340 | 0.000 | 15.2 | 1.921 | n/a | 10.0 | 1.000 | 0.8750 |
| T4 | h2 | shuffled_vs_yardstick | -0.4729 | -0.4706 | 0.0022 | 0.1376 | 0.9075 | 0.0880 | 0.0045 | 0.980 | 0.3036 | 0.006 | 0.971 | 4.2 | 1.309 | n/a | n/a | 1.000 | 0.9075 |
| T4 | h2 | carried_added | 1.1513 | 1.1501 | -0.0012 | 0.1145 | 0.8740 | 0.0055 | 0.1205 | 1.034 | 0.2466 | 0.307 | 0.000 | 15.2 | 2.122 | n/a | n/a | 1.000 | 0.8740 |
| T4 | h2 | pooled_retention | 0.6000 | 0.5992 | -0.0008 | 0.0588 | 0.8760 | 0.0050 | 0.1190 | 1.050 | 0.1272 | 0.577 | 0.000 | 15.1 | 2.242 | n/a | 95.7 | 1.000 | 0.8760 |
| T4 | h5 | large | 2.4230 | 2.4201 | -0.0029 | 0.2624 | 0.9025 | 0.0045 | 0.0930 | 1.105 | 0.5677 | 0.076 | 0.062 | 15.1 | 1.336 | n/a | n/a | 0.995 | 0.9015 |
| T4 | h5 | carries | 0.6000 | 0.5992 | -0.0008 | 0.0606 | 0.8770 | 0.0050 | 0.1180 | 1.057 | 0.1308 | 0.588 | 0.000 | 15.1 | 2.174 | n/a | 114.3 | 0.995 | 0.8765 |
| T4 | h5 | depends | 0.5851 | 0.5848 | -0.0003 | 0.0598 | 0.8790 | 0.0030 | 0.1180 | 1.066 | 0.1283 | 0.589 | 0.000 | 15.1 | 2.188 | n/a | 70.3 | 0.995 | 0.8785 |
| T4 | h5 | carried_margin | 2.8959 | 2.8910 | -0.0049 | 0.2655 | 0.8765 | 0.0055 | 0.1180 | 1.045 | 0.5713 | 0.417 | 0.001 | 15.3 | 2.100 | n/a | n/a | 0.995 | 0.8760 |
| T4 | h5 | own_margin | 4.9493 | 4.9485 | -0.0008 | 0.0703 | 0.9600 | 0.0275 | 0.0125 | 1.119 | 0.1580 | 0.307 | 0.175 | 11.2 | 0.923 | n/a | n/a | 0.995 | 0.9600 |
| T4 | h5 | kappa | 0.9402 | 0.9410 | 0.0008 | 0.0069 | 0.8715 | 0.1145 | 0.0140 | 0.983 | 0.0150 | 0.430 | 0.000 | 15.2 | 1.888 | n/a | 10.0 | 0.995 | 0.8705 |
| T4 | h5 | shuffled_vs_yardstick | -0.4729 | -0.4709 | 0.0021 | 0.1379 | 0.9055 | 0.0895 | 0.0050 | 1.051 | 0.3211 | 0.009 | 0.965 | 3.9 | 1.323 | n/a | n/a | 0.995 | 0.9065 |
| T4 | h5 | carried_added | 3.0801 | 3.0745 | -0.0056 | 0.3048 | 0.8765 | 0.0055 | 0.1180 | 1.044 | 0.6553 | 0.417 | 0.000 | 15.3 | 2.168 | n/a | n/a | 0.995 | 0.8760 |
| T4 | h5 | pooled_retention | 0.6000 | 0.5990 | -0.0010 | 0.0587 | 0.8775 | 0.0050 | 0.1175 | 1.055 | 0.1272 | 0.570 | 0.000 | 15.1 | 2.217 | n/a | 118.7 | 0.995 | 0.8770 |
| T4 | h10 | large | 5.9093 | 5.5147 | -0.3946 | 0.3999 | 0.7610 | 0.0000 | 0.2390 | 1.558 | 1.0377 | 0.485 | 0.006 | 15.1 | 2.308 | n/a | n/a | 0.183 | 0.8775 |
| T4 | h10 | carries | 0.6000 | 0.5595 | -0.0405 | 0.0400 | 0.7615 | 0.0000 | 0.2385 | 1.582 | 0.1048 | 0.591 | 0.001 | 15.1 | 2.475 | n/a | 85.9 | 0.183 | 0.8805 |
| T4 | h10 | depends | 0.5931 | 0.5532 | -0.0399 | 0.0395 | 0.7615 | 0.0000 | 0.2385 | 1.588 | 0.1036 | 0.594 | 0.001 | 15.1 | 2.473 | n/a | 80.3 | 0.183 | 0.8810 |
| T4 | h10 | carried_margin | 6.3826 | 5.9706 | -0.4120 | 0.4119 | 0.7625 | 0.0000 | 0.2375 | 1.555 | 1.0647 | 0.375 | 0.002 | 15.2 | 2.522 | n/a | n/a | 0.183 | 0.8765 |
| T4 | h10 | own_margin | 10.7607 | 10.7954 | 0.0347 | 0.1585 | 0.9205 | 0.0390 | 0.0405 | 1.164 | 0.3623 | 0.309 | 0.477 | 7.9 | 1.175 | n/a | n/a | 0.183 | 0.9185 |
| T4 | h10 | kappa | 0.9720 | 0.9746 | 0.0026 | 0.0025 | 0.7720 | 0.2280 | 0.0000 | 1.431 | 0.0066 | 0.383 | 0.000 | 15.3 | 2.298 | n/a | 11.4 | 0.183 | 0.8720 |
| T4 | h10 | shuffled_vs_yardstick | -0.4734 | -0.4559 | 0.0174 | 0.1254 | 0.8375 | 0.1575 | 0.0050 | 0.848 | 0.2094 | 0.001 | 0.947 | 5.3 | 1.844 | n/a | n/a | 0.183 | 0.8340 |
| T4 | h10 | carried_added | 6.5668 | 6.1275 | -0.4394 | 0.4373 | 0.7615 | 0.0000 | 0.2385 | 1.558 | 1.1311 | 0.375 | 0.001 | 15.3 | 2.536 | n/a | n/a | 0.183 | 0.8760 |
| T4 | h10 | pooled_retention | 0.6000 | 0.5593 | -0.0407 | 0.0389 | 0.7580 | 0.0000 | 0.2420 | 1.604 | 0.1024 | 0.531 | 0.000 | 15.1 | 2.663 | n/a | 87.8 | 0.183 | 0.8760 |
| T5 | n20 | large | 0.9339 | 0.9322 | -0.0017 | 0.6234 | 0.7995 | 0.0010 | 0.1995 | 1.238 | 1.3807 | 0.614 | 0.036 | 13.5 | 2.139 | n/a | n/a | n/a | n/a |
| T5 | n20 | carries | 2.5505 | 2.5730 | 0.0225 | 1.0849 | 0.8115 | 0.0010 | 0.1875 | 1.226 | 2.2682 | 0.587 | 0.041 | 13.4 | 2.199 | n/a | 8.6 | n/a | n/a |
| T5 | n20 | depends | 3.2336 | 3.2712 | 0.0375 | 1.5719 | 0.8130 | 0.0010 | 0.1860 | 1.224 | 3.3057 | 0.570 | 0.047 | 13.2 | 2.194 | n/a | 9.3 | n/a | n/a |
| T5 | n20 | carried_margin | 1.3520 | 1.3516 | -0.0003 | 0.6217 | 0.8010 | 0.0000 | 0.1990 | 1.241 | 1.3646 | 0.603 | 0.036 | 13.5 | 2.158 | n/a | n/a | n/a | n/a |
| T5 | n20 | own_margin | 0.4181 | 0.4195 | 0.0014 | 0.0538 | 0.9230 | 0.0100 | 0.0670 | 1.012 | 0.1310 | 0.123 | 0.665 | 6.0 | 1.194 | n/a | n/a | n/a | n/a |
| T5 | n20 | kappa | 0.8801 | 0.8579 | -0.0222 | 0.0673 | 0.9320 | 0.0500 | 0.0180 | 0.880 | 0.1261 | 0.604 | 0.018 | 13.9 | 1.115 | n/a | 2.5 | n/a | n/a |
| T5 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4195 | -0.0014 | 0.0538 | 0.9230 | 0.0670 | 0.0100 | 1.012 | 0.1310 | 0.123 | 0.665 | 6.0 | 1.194 | n/a | n/a | n/a | n/a |
| T5 | n20 | carried_added | 1.5362 | 1.5369 | 0.0007 | 0.6229 | 0.8010 | 0.0005 | 0.1985 | 1.239 | 1.3653 | 0.602 | 0.036 | 13.5 | 2.134 | n/a | n/a | n/a | n/a |
| T5 | n20 | pooled_retention | 2.5505 | 2.5802 | 0.0297 | 1.0933 | 0.8075 | 0.0005 | 0.1920 | 1.209 | 2.2521 | 0.572 | 0.041 | 13.5 | 2.203 | n/a | 8.6 | n/a | n/a |
| T5 | n40 | large | 1.7407 | 1.7590 | 0.0183 | 0.6264 | 0.8430 | 0.0010 | 0.1560 | 1.257 | 1.3707 | 0.587 | 0.036 | 13.4 | 1.825 | n/a | n/a | n/a | n/a |
| T5 | n40 | carries | 1.1784 | 1.2004 | 0.0220 | 0.3391 | 0.8695 | 0.0000 | 0.1305 | 1.254 | 0.7150 | 0.567 | 0.037 | 13.3 | 1.621 | n/a | 8.2 | n/a | n/a |
| T5 | n40 | depends | 1.1966 | 1.2220 | 0.0254 | 0.3745 | 0.8685 | 0.0000 | 0.1315 | 1.256 | 0.7901 | 0.565 | 0.037 | 13.3 | 1.662 | n/a | 8.2 | n/a | n/a |
| T5 | n40 | carried_margin | 2.1588 | 2.1785 | 0.0197 | 0.6320 | 0.8530 | 0.0010 | 0.1460 | 1.249 | 1.3850 | 0.548 | 0.042 | 13.2 | 1.763 | n/a | n/a | n/a | n/a |
| T5 | n40 | own_margin | 1.8041 | 1.8047 | 0.0006 | 0.2386 | 0.9375 | 0.0155 | 0.0470 | 0.999 | 0.4952 | 0.162 | 0.260 | 10.2 | 1.061 | n/a | n/a | n/a | n/a |
| T5 | n40 | kappa | 0.9214 | 0.9169 | -0.0045 | 0.0254 | 0.9240 | 0.0430 | 0.0330 | 1.022 | 0.0525 | 0.549 | 0.012 | 13.9 | 1.111 | n/a | 3.7 | n/a | n/a |
| T5 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4195 | -0.0014 | 0.0538 | 0.9230 | 0.0665 | 0.0105 | 1.013 | 0.1316 | 0.123 | 0.662 | 6.0 | 1.200 | n/a | n/a | n/a | n/a |
| T5 | n40 | carried_added | 2.3430 | 2.3637 | 0.0208 | 0.6391 | 0.8600 | 0.0010 | 0.1390 | 1.241 | 1.3963 | 0.549 | 0.041 | 13.3 | 1.713 | n/a | n/a | n/a | n/a |
| T5 | n40 | pooled_retention | 1.1784 | 1.1985 | 0.0201 | 0.3331 | 0.8380 | 0.0020 | 0.1600 | 1.237 | 0.6912 | 0.577 | 0.043 | 13.5 | 1.950 | n/a | 8.2 | n/a | n/a |
| T5 | n80 | large | 6.3296 | 6.3766 | 0.0470 | 1.0527 | 0.9570 | 0.0065 | 0.0365 | 1.106 | 2.3510 | 0.288 | 0.223 | 10.2 | 0.970 | n/a | n/a | n/a | n/a |
| T5 | n80 | carries | 0.7022 | 0.7119 | 0.0097 | 0.1160 | 0.9540 | 0.0065 | 0.0395 | 1.185 | 0.2560 | 0.585 | 0.043 | 13.2 | 0.965 | n/a | 8.0 | n/a | n/a |
| T5 | n80 | depends | 0.6966 | 0.7068 | 0.0102 | 0.1174 | 0.9550 | 0.0055 | 0.0395 | 1.190 | 0.2588 | 0.586 | 0.044 | 13.2 | 0.964 | n/a | 7.8 | n/a | n/a |
| T5 | n80 | carried_margin | 6.7477 | 6.7961 | 0.0484 | 1.0852 | 0.9580 | 0.0070 | 0.0350 | 1.096 | 2.4293 | 0.266 | 0.247 | 10.0 | 0.958 | n/a | n/a | n/a | n/a |
| T5 | n80 | own_margin | 9.6872 | 9.7148 | 0.0276 | 1.3343 | 0.9300 | 0.0220 | 0.0480 | 1.038 | 3.6469 | 0.113 | 0.661 | 6.1 | 1.180 | n/a | n/a | n/a | n/a |
| T5 | n80 | kappa | 0.9734 | 0.9733 | -0.0001 | 0.0052 | 0.9355 | 0.0545 | 0.0100 | 1.022 | 0.0110 | 0.268 | 0.117 | 11.8 | 1.076 | n/a | 6.5 | n/a | n/a |
| T5 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4195 | -0.0014 | 0.0538 | 0.9235 | 0.0660 | 0.0105 | 1.012 | 0.1312 | 0.121 | 0.660 | 6.0 | 1.202 | n/a | n/a | n/a | n/a |
| T5 | n80 | carried_added | 6.9319 | 6.9813 | 0.0494 | 1.1062 | 0.9570 | 0.0070 | 0.0360 | 1.092 | 2.4690 | 0.266 | 0.231 | 10.2 | 0.959 | n/a | n/a | n/a | n/a |
| T5 | n80 | pooled_retention | 0.7022 | 0.7069 | 0.0047 | 0.0823 | 0.9395 | 0.0045 | 0.0560 | 1.156 | 0.1782 | 0.582 | 0.016 | 14.0 | 1.085 | n/a | 7.9 | n/a | n/a |
| T5 | n160 | large | 13.2003 | 13.2282 | 0.0279 | 1.4784 | 0.9460 | 0.0060 | 0.0480 | 1.107 | 3.2872 | 0.517 | 0.016 | 14.1 | 1.024 | n/a | n/a | n/a | n/a |
| T5 | n160 | carries | 0.6368 | 0.6431 | 0.0063 | 0.0971 | 0.9255 | 0.0010 | 0.0735 | 1.140 | 0.2099 | 0.573 | 0.013 | 14.3 | 1.193 | n/a | 16.0 | n/a | n/a |
| T5 | n160 | depends | 0.6337 | 0.6402 | 0.0065 | 0.0973 | 0.9270 | 0.0010 | 0.0720 | 1.143 | 0.2103 | 0.572 | 0.013 | 14.3 | 1.184 | n/a | 15.6 | n/a | n/a |
| T5 | n160 | carried_margin | 13.6184 | 13.6477 | 0.0293 | 1.4972 | 0.9470 | 0.0055 | 0.0475 | 1.102 | 3.3252 | 0.501 | 0.017 | 14.1 | 1.024 | n/a | n/a | n/a | n/a |
| T5 | n160 | own_margin | 21.4901 | 21.4692 | -0.0208 | 1.3067 | 0.9530 | 0.0365 | 0.0105 | 1.202 | 2.9971 | 0.490 | 0.146 | 11.8 | 0.969 | n/a | n/a | n/a | n/a |
| T5 | n160 | kappa | 0.9867 | 0.9867 | 0.0001 | 0.0019 | 0.9110 | 0.0770 | 0.0120 | 0.974 | 0.0040 | 0.504 | 0.004 | 14.8 | 1.327 | n/a | 8.8 | n/a | n/a |
| T5 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4195 | -0.0014 | 0.0538 | 0.9210 | 0.0685 | 0.0105 | 1.012 | 0.1315 | 0.123 | 0.662 | 6.0 | 1.205 | n/a | n/a | n/a | n/a |
| T5 | n160 | carried_added | 13.8026 | 13.8329 | 0.0303 | 1.5302 | 0.9460 | 0.0055 | 0.0485 | 1.098 | 3.3953 | 0.501 | 0.015 | 14.1 | 1.041 | n/a | n/a | n/a | n/a |
| T5 | n160 | pooled_retention | 0.6368 | 0.6389 | 0.0020 | 0.0614 | 0.9175 | 0.0030 | 0.0795 | 1.062 | 0.1335 | 0.585 | 0.002 | 14.9 | 1.361 | n/a | 16.0 | n/a | n/a |
| T5 | n320 | large | 15.2419 | 15.2719 | 0.0300 | 1.6548 | 0.9390 | 0.0030 | 0.0580 | 1.102 | 3.6601 | 0.573 | 0.007 | 14.5 | 1.073 | n/a | n/a | n/a | n/a |
| T5 | n320 | carries | 0.6292 | 0.6357 | 0.0065 | 0.0938 | 0.9235 | 0.0010 | 0.0755 | 1.159 | 0.2049 | 0.583 | 0.009 | 14.6 | 1.236 | n/a | 17.3 | n/a | n/a |
| T5 | n320 | depends | 0.6265 | 0.6332 | 0.0067 | 0.0940 | 0.9250 | 0.0010 | 0.0740 | 1.162 | 0.2051 | 0.583 | 0.009 | 14.6 | 1.228 | n/a | 16.8 | n/a | n/a |
| T5 | n320 | carried_margin | 15.6600 | 15.6914 | 0.0314 | 1.6694 | 0.9370 | 0.0030 | 0.0600 | 1.100 | 3.6929 | 0.571 | 0.007 | 14.5 | 1.074 | n/a | n/a | n/a | n/a |
| T5 | n320 | own_margin | 24.9973 | 24.9459 | -0.0514 | 1.3386 | 0.9590 | 0.0360 | 0.0050 | 1.305 | 3.2320 | 0.568 | 0.096 | 12.5 | 0.940 | n/a | n/a | n/a | n/a |
| T5 | n320 | kappa | 0.9884 | 0.9884 | 0.0001 | 0.0016 | 0.9040 | 0.0860 | 0.0100 | 0.979 | 0.0034 | 0.574 | 0.002 | 15.0 | 1.406 | n/a | 9.0 | n/a | n/a |
| T5 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4195 | -0.0014 | 0.0538 | 0.9240 | 0.0655 | 0.0105 | 1.013 | 0.1309 | 0.122 | 0.661 | 6.0 | 1.195 | n/a | n/a | n/a | n/a |
| T5 | n320 | carried_added | 15.8442 | 15.8767 | 0.0324 | 1.7040 | 0.9365 | 0.0030 | 0.0605 | 1.096 | 3.7635 | 0.571 | 0.007 | 14.6 | 1.092 | n/a | n/a | n/a | n/a |
| T5 | n320 | pooled_retention | 0.6292 | 0.6309 | 0.0017 | 0.0605 | 0.9040 | 0.0050 | 0.0910 | 1.037 | 0.1296 | 0.576 | 0.002 | 15.1 | 1.534 | n/a | 17.5 | n/a | n/a |
| T5 | h2 | large | 1.6970 | 1.6987 | 0.0016 | 0.5999 | 0.8090 | 0.0005 | 0.1905 | 1.294 | 1.3774 | 0.600 | 0.037 | 13.6 | 2.187 | n/a | n/a | 1.000 | 0.8090 |
| T5 | h2 | carries | 1.2016 | 1.2032 | 0.0015 | 0.3161 | 0.8130 | 0.0005 | 0.1865 | 1.285 | 0.7185 | 0.622 | 0.037 | 13.8 | 2.065 | n/a | 115.1 | 1.000 | 0.8130 |
| T5 | h2 | depends | 1.2231 | 1.2264 | 0.0033 | 0.3508 | 0.8135 | 0.0005 | 0.1860 | 1.287 | 0.7901 | 0.621 | 0.036 | 13.8 | 2.111 | n/a | 54.3 | 1.000 | 0.8135 |
| T5 | h2 | carried_margin | 2.1154 | 2.1181 | 0.0028 | 0.6009 | 0.8070 | 0.0005 | 0.1925 | 1.288 | 1.3760 | 0.617 | 0.036 | 13.8 | 2.176 | n/a | n/a | 1.000 | 0.8070 |
| T5 | h2 | own_margin | 1.7295 | 1.7286 | -0.0008 | 0.0320 | 0.9175 | 0.0775 | 0.0050 | 1.049 | 0.0678 | 0.462 | 0.005 | 15.1 | 1.278 | n/a | n/a | 1.000 | 0.9175 |
| T5 | h2 | kappa | 0.9199 | 0.9149 | -0.0050 | 0.0256 | 0.9075 | 0.0340 | 0.0585 | 0.947 | 0.0519 | 0.615 | 0.018 | 14.2 | 1.213 | n/a | 3.7 | 1.000 | 0.9075 |
| T5 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4195 | -0.0011 | 0.0538 | 0.9220 | 0.0675 | 0.0105 | 1.011 | 0.1313 | 0.122 | 0.660 | 6.0 | 1.200 | n/a | n/a | 1.000 | 0.9220 |
| T5 | h2 | carried_added | 2.2996 | 2.3034 | 0.0038 | 0.6076 | 0.8170 | 0.0005 | 0.1825 | 1.280 | 1.3857 | 0.618 | 0.036 | 13.8 | 2.040 | n/a | n/a | 1.000 | 0.8170 |
| T5 | h2 | pooled_retention | 1.2016 | 1.2035 | 0.0019 | 0.3179 | 0.8170 | 0.0005 | 0.1825 | 1.278 | 0.7192 | 0.612 | 0.037 | 13.8 | 2.053 | n/a | 115.0 | 1.000 | 0.8170 |
| T5 | h5 | large | 3.5641 | 3.5543 | -0.0098 | 0.6439 | 0.8680 | 0.0020 | 0.1300 | 1.232 | 1.3628 | 0.578 | 0.049 | 13.7 | 1.605 | n/a | n/a | 0.992 | 0.8690 |
| T5 | h5 | carries | 0.8136 | 0.8123 | -0.0013 | 0.1305 | 0.8920 | 0.0020 | 0.1060 | 1.225 | 0.2785 | 0.597 | 0.042 | 13.8 | 1.518 | n/a | 146.4 | 0.992 | 0.8930 |
| T5 | h5 | depends | 0.8067 | 0.8058 | -0.0009 | 0.1348 | 0.8875 | 0.0015 | 0.1110 | 1.227 | 0.2879 | 0.598 | 0.042 | 13.8 | 1.556 | n/a | 77.5 | 0.992 | 0.8885 |
| T5 | h5 | carried_margin | 3.9824 | 3.9736 | -0.0088 | 0.6457 | 0.8755 | 0.0015 | 0.1230 | 1.237 | 1.3685 | 0.602 | 0.046 | 13.8 | 1.631 | n/a | n/a | 0.992 | 0.8765 |
| T5 | h5 | own_margin | 4.9368 | 4.9355 | -0.0013 | 0.0624 | 0.9470 | 0.0480 | 0.0050 | 1.104 | 0.1402 | 0.503 | 0.060 | 13.0 | 1.021 | n/a | n/a | 0.992 | 0.9470 |
| T5 | h5 | kappa | 0.9558 | 0.9550 | -0.0008 | 0.0090 | 0.9175 | 0.0445 | 0.0380 | 0.956 | 0.0187 | 0.598 | 0.018 | 14.3 | 1.139 | n/a | 6.3 | 0.992 | 0.9170 |
| T5 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4194 | -0.0010 | 0.0538 | 0.9180 | 0.0700 | 0.0120 | 1.060 | 0.1359 | 0.167 | 0.651 | 6.1 | 1.271 | n/a | n/a | 0.992 | 0.9185 |
| T5 | h5 | carried_added | 4.1666 | 4.1589 | -0.0077 | 0.6623 | 0.8890 | 0.0015 | 0.1095 | 1.228 | 1.4148 | 0.602 | 0.043 | 13.8 | 1.526 | n/a | n/a | 0.992 | 0.8900 |
| T5 | h5 | pooled_retention | 0.8136 | 0.8120 | -0.0016 | 0.1292 | 0.8895 | 0.0020 | 0.1085 | 1.229 | 0.2751 | 0.601 | 0.044 | 13.8 | 1.508 | n/a | 148.3 | 0.992 | 0.8905 |
| T5 | h10 | large | 6.9265 | 6.5226 | -0.4039 | 0.6824 | 0.8555 | 0.0000 | 0.1445 | 1.352 | 1.5687 | 0.596 | 0.037 | 14.0 | 1.795 | n/a | n/a | 0.195 | 0.9290 |
| T5 | h10 | carries | 0.6909 | 0.6497 | -0.0412 | 0.0646 | 0.8580 | 0.0000 | 0.1420 | 1.375 | 0.1510 | 0.601 | 0.033 | 14.0 | 1.897 | n/a | 120.5 | 0.195 | 0.9320 |
| T5 | h10 | depends | 0.6856 | 0.6447 | -0.0409 | 0.0650 | 0.8570 | 0.0000 | 0.1430 | 1.375 | 0.1516 | 0.601 | 0.034 | 14.0 | 1.895 | n/a | 109.1 | 0.195 | 0.9320 |
| T5 | h10 | carried_margin | 7.3448 | 6.9252 | -0.4197 | 0.6847 | 0.8570 | 0.0000 | 0.1430 | 1.365 | 1.5820 | 0.600 | 0.038 | 14.0 | 1.820 | n/a | n/a | 0.195 | 0.9300 |
| T5 | h10 | own_margin | 10.7131 | 10.7445 | 0.0314 | 0.0968 | 0.9575 | 0.0355 | 0.0070 | 1.458 | 0.2175 | 0.491 | 0.283 | 10.2 | 0.941 | n/a | n/a | 0.195 | 0.9580 |
| T5 | h10 | kappa | 0.9755 | 0.9779 | 0.0023 | 0.0030 | 0.8340 | 0.1660 | 0.0000 | 1.260 | 0.0073 | 0.597 | 0.011 | 14.6 | 1.587 | n/a | 9.2 | 0.195 | 0.9115 |
| T5 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4026 | 0.0157 | 0.0433 | 0.8565 | 0.1400 | 0.0035 | 0.811 | 0.0845 | 0.044 | 0.621 | 8.1 | 1.575 | n/a | n/a | 0.195 | 0.8840 |
| T5 | h10 | carried_added | 7.5290 | 7.0819 | -0.4471 | 0.7003 | 0.8560 | 0.0000 | 0.1440 | 1.371 | 1.6289 | 0.600 | 0.035 | 14.0 | 1.847 | n/a | n/a | 0.195 | 0.9305 |
| T5 | h10 | pooled_retention | 0.6909 | 0.6499 | -0.0410 | 0.0643 | 0.8575 | 0.0000 | 0.1425 | 1.364 | 0.1496 | 0.611 | 0.034 | 14.1 | 1.840 | n/a | 123.3 | 0.195 | 0.9305 |
| T6[0.3] | n20 | large | -0.1807 | -0.1806 | 0.0001 | 0.0549 | 0.9770 | 0.0080 | 0.0150 | 1.145 | 0.1187 | 0.533 | 0.059 | 12.9 | 0.853 | n/a | n/a | n/a | n/a |
| T6[0.3] | n20 | carries | 0.7000 | 0.7010 | 0.0010 | 0.0786 | 0.8925 | 0.0035 | 0.1040 | 1.096 | 0.1695 | 0.612 | 0.026 | 13.8 | 1.495 | n/a | 8.6 | n/a | n/a |
| T6[0.3] | n20 | depends | 0.6845 | 0.6862 | 0.0017 | 0.0827 | 0.8960 | 0.0030 | 0.1010 | 1.092 | 0.1781 | 0.617 | 0.023 | 13.8 | 1.447 | n/a | 10.9 | n/a | n/a |
| T6[0.3] | n20 | carried_margin | 0.3920 | 0.3923 | 0.0004 | 0.0583 | 0.8890 | 0.0025 | 0.1085 | 0.976 | 0.1125 | 0.115 | 0.176 | 11.5 | 1.565 | n/a | n/a | n/a | n/a |
| T6[0.3] | n20 | own_margin | 0.5727 | 0.5729 | 0.0003 | 0.0615 | 0.9090 | 0.0070 | 0.0840 | 0.968 | 0.1328 | 0.122 | 0.526 | 7.4 | 1.355 | n/a | n/a | n/a | n/a |
| T6[0.3] | n20 | kappa | 0.9297 | 0.9334 | 0.0037 | 0.0537 | 0.8815 | 0.1085 | 0.0100 | 0.921 | 0.1099 | 0.175 | 0.000 | 15.3 | 1.978 | n/a | 6.6 | n/a | n/a |
| T6[0.3] | n20 | shuffled_vs_yardstick | -0.5727 | -0.5729 | -0.0003 | 0.0615 | 0.9090 | 0.0840 | 0.0070 | 0.968 | 0.1328 | 0.122 | 0.526 | 7.4 | 1.355 | n/a | n/a | n/a | n/a |
| T6[0.3] | n20 | carried_added | 0.4216 | 0.4222 | 0.0006 | 0.0698 | 0.9155 | 0.0010 | 0.0835 | 0.983 | 0.1355 | 0.116 | 0.034 | 14.3 | 1.372 | n/a | n/a | n/a | n/a |
| T6[0.3] | n20 | pooled_retention | 0.7000 | 0.7003 | 0.0003 | 0.0701 | 0.8795 | 0.0060 | 0.1145 | 1.015 | 0.1489 | 0.763 | 0.000 | 15.0 | 2.291 | n/a | 8.6 | n/a | n/a |
| T6[0.3] | n80 | large | 6.3077 | 6.3135 | 0.0059 | 1.1653 | 0.9345 | 0.0105 | 0.0550 | 0.937 | 2.4522 | 0.141 | 0.350 | 9.2 | 1.129 | n/a | n/a | n/a | n/a |
| T6[0.3] | n80 | carries | 0.7000 | 0.7083 | 0.0083 | 0.1133 | 0.9535 | 0.0040 | 0.0425 | 1.151 | 0.2499 | 0.608 | 0.041 | 13.5 | 0.974 | n/a | 7.9 | n/a | n/a |
| T6[0.3] | n80 | depends | 0.5806 | 0.5940 | 0.0134 | 0.1470 | 0.9510 | 0.0000 | 0.0490 | 1.196 | 0.3074 | 0.591 | 0.053 | 13.2 | 0.990 | n/a | 5.3 | n/a | n/a |
| T6[0.3] | n80 | carried_margin | 4.0996 | 4.1043 | 0.0046 | 1.0726 | 0.9310 | 0.0140 | 0.0550 | 0.941 | 2.4310 | 0.125 | 0.542 | 7.3 | 1.103 | n/a | n/a | n/a | n/a |
| T6[0.3] | n80 | own_margin | 7.0610 | 7.0169 | -0.0441 | 1.4051 | 0.9320 | 0.0160 | 0.0520 | 1.021 | 3.5695 | 0.135 | 0.580 | 6.9 | 1.121 | n/a | n/a | n/a | n/a |
| T6[0.3] | n80 | kappa | 0.5933 | 0.5854 | -0.0079 | 0.0585 | 0.9315 | 0.0400 | 0.0285 | 0.974 | 0.1484 | 0.125 | 0.649 | 6.2 | 1.119 | n/a | 6.2 | n/a | n/a |
| T6[0.3] | n80 | shuffled_vs_yardstick | 2.2081 | 2.2093 | 0.0012 | 0.2504 | 0.8785 | 0.0060 | 0.1155 | 1.007 | 0.5250 | 0.131 | 0.001 | 15.9 | 1.918 | n/a | n/a | n/a | n/a |
| T6[0.3] | n80 | carried_added | 6.9100 | 6.9163 | 0.0064 | 1.2291 | 0.9355 | 0.0100 | 0.0545 | 0.934 | 2.5778 | 0.126 | 0.350 | 9.3 | 1.138 | n/a | n/a | n/a | n/a |
| T6[0.3] | n80 | pooled_retention | 0.7000 | 0.7005 | 0.0005 | 0.0702 | 0.8785 | 0.0060 | 0.1155 | 1.013 | 0.1488 | 0.834 | 0.000 | 15.0 | 2.275 | n/a | 7.9 | n/a | n/a |
| T6[0.5] | n20 | large | -0.1807 | -0.1821 | -0.0014 | 0.0546 | 0.9725 | 0.0060 | 0.0215 | 1.162 | 0.1200 | 0.514 | 0.068 | 12.7 | 0.869 | n/a | n/a | n/a | n/a |
| T6[0.5] | n20 | carries | 0.7000 | 0.7002 | 0.0002 | 0.0768 | 0.9120 | 0.0015 | 0.0865 | 1.144 | 0.1707 | 0.581 | 0.035 | 13.6 | 1.415 | n/a | 8.5 | n/a | n/a |
| T6[0.5] | n20 | depends | 0.5583 | 0.5574 | -0.0009 | 0.1129 | 0.8975 | 0.0015 | 0.1010 | 1.129 | 0.2424 | 0.557 | 0.015 | 13.9 | 1.459 | n/a | 9.0 | n/a | n/a |
| T6[0.5] | n20 | carried_margin | 0.2284 | 0.2281 | -0.0003 | 0.0529 | 0.9045 | 0.0010 | 0.0945 | 1.058 | 0.1087 | 0.125 | 0.199 | 11.0 | 1.440 | n/a | n/a | n/a | n/a |
| T6[0.5] | n20 | own_margin | 0.4091 | 0.4101 | 0.0011 | 0.0536 | 0.9350 | 0.0105 | 0.0545 | 1.004 | 0.1326 | 0.118 | 0.676 | 5.8 | 1.144 | n/a | n/a | n/a | n/a |
| T6[0.5] | n20 | kappa | 0.5416 | 0.5369 | -0.0048 | 0.0768 | 0.9305 | 0.0460 | 0.0235 | 0.936 | 0.1576 | 0.123 | 0.016 | 14.8 | 1.095 | n/a | 6.6 | n/a | n/a |
| T6[0.5] | n20 | shuffled_vs_yardstick | -0.4091 | -0.4101 | -0.0011 | 0.0536 | 0.9350 | 0.0545 | 0.0105 | 1.004 | 0.1326 | 0.118 | 0.676 | 5.8 | 1.144 | n/a | n/a | n/a | n/a |
| T6[0.5] | n20 | carried_added | 0.4216 | 0.4234 | 0.0018 | 0.0672 | 0.9235 | 0.0020 | 0.0745 | 1.053 | 0.1361 | 0.124 | 0.032 | 14.3 | 1.179 | n/a | n/a | n/a | n/a |
| T6[0.5] | n20 | pooled_retention | 0.7000 | 0.7034 | 0.0034 | 0.0700 | 0.8855 | 0.0025 | 0.1120 | 1.042 | 0.1507 | 0.764 | 0.000 | 15.0 | 2.189 | n/a | 8.6 | n/a | n/a |
| T6[0.5] | n80 | large | 6.3077 | 6.3327 | 0.0250 | 1.0978 | 0.9400 | 0.0060 | 0.0540 | 1.036 | 2.4477 | 0.149 | 0.330 | 9.3 | 1.040 | n/a | n/a | n/a | n/a |
| T6[0.5] | n80 | carries | 0.7000 | 0.7083 | 0.0083 | 0.1129 | 0.9510 | 0.0035 | 0.0455 | 1.163 | 0.2517 | 0.637 | 0.037 | 13.6 | 0.991 | n/a | 8.0 | n/a | n/a |
| T6[0.5] | n80 | depends | 0.4128 | 0.4256 | 0.0127 | 0.1968 | 0.9555 | 0.0005 | 0.0440 | 1.431 | 0.3917 | 0.489 | 0.118 | 12.0 | 0.974 | n/a | 3.5 | n/a | n/a |
| T6[0.5] | n80 | carried_margin | 2.0822 | 2.0848 | 0.0026 | 0.9530 | 0.9290 | 0.0185 | 0.0525 | 1.031 | 2.4414 | 0.126 | 0.602 | 6.6 | 1.113 | n/a | n/a | n/a | n/a |
| T6[0.5] | n80 | own_margin | 5.0436 | 5.0138 | -0.0298 | 1.4596 | 0.9400 | 0.0195 | 0.0405 | 1.044 | 3.4989 | 0.144 | 0.480 | 8.0 | 1.070 | n/a | n/a | n/a | n/a |
| T6[0.5] | n80 | kappa | 0.3013 | 0.2880 | -0.0133 | 0.0972 | 0.9325 | 0.0390 | 0.0285 | 1.006 | 0.2515 | 0.124 | 0.632 | 6.4 | 1.125 | n/a | 6.3 | n/a | n/a |
| T6[0.5] | n80 | shuffled_vs_yardstick | 4.2255 | 4.2479 | 0.0224 | 0.4530 | 0.8875 | 0.0025 | 0.1100 | 1.010 | 0.9511 | 0.128 | 0.000 | 15.4 | 2.153 | n/a | n/a | n/a | n/a |
| T6[0.5] | n80 | carried_added | 6.9100 | 6.9382 | 0.0282 | 1.1591 | 0.9400 | 0.0055 | 0.0545 | 1.031 | 2.5678 | 0.128 | 0.330 | 9.4 | 1.041 | n/a | n/a | n/a | n/a |
| T6[0.5] | n80 | pooled_retention | 0.7000 | 0.7034 | 0.0034 | 0.0704 | 0.8870 | 0.0025 | 0.1105 | 1.026 | 0.1505 | 0.825 | 0.000 | 15.0 | 2.171 | n/a | 8.1 | n/a | n/a |
| T6[0.7] | n20 | large | -0.1807 | -0.1815 | -0.0008 | 0.0543 | 0.9720 | 0.0060 | 0.0220 | 1.145 | 0.1196 | 0.516 | 0.062 | 12.8 | 0.861 | n/a | n/a | n/a | n/a |
| T6[0.7] | n20 | carries | 0.7000 | 0.6988 | -0.0012 | 0.0775 | 0.9015 | 0.0020 | 0.0965 | 1.115 | 0.1714 | 0.605 | 0.031 | 13.6 | 1.592 | n/a | 8.6 | n/a | n/a |
| T6[0.7] | n20 | depends | 0.2638 | 0.2467 | -0.0171 | 0.2165 | 0.9520 | 0.0040 | 0.0440 | 1.092 | 0.4353 | 0.289 | 0.050 | 13.4 | 0.993 | n/a | 5.6 | n/a | n/a |
| T6[0.7] | n20 | carried_margin | 0.0647 | 0.0639 | -0.0008 | 0.0553 | 0.9285 | 0.0050 | 0.0665 | 1.024 | 0.1111 | 0.122 | 0.121 | 12.2 | 1.097 | n/a | n/a | n/a | n/a |
| T6[0.7] | n20 | own_margin | 0.2454 | 0.2455 | 0.0001 | 0.0511 | 0.9270 | 0.0210 | 0.0520 | 0.998 | 0.1301 | 0.102 | 0.707 | 5.7 | 1.188 | n/a | n/a | n/a | n/a |
| T6[0.7] | n20 | kappa | 0.1536 | 0.1447 | -0.0088 | 0.1163 | 0.9290 | 0.0300 | 0.0410 | 0.917 | 0.2350 | 0.122 | 0.094 | 12.8 | 1.109 | n/a | 6.6 | n/a | n/a |
| T6[0.7] | n20 | shuffled_vs_yardstick | -0.2454 | -0.2455 | -0.0001 | 0.0511 | 0.9270 | 0.0520 | 0.0210 | 0.998 | 0.1301 | 0.102 | 0.707 | 5.7 | 1.188 | n/a | n/a | n/a | n/a |
| T6[0.7] | n20 | carried_added | 0.4216 | 0.4195 | -0.0021 | 0.0674 | 0.9025 | 0.0015 | 0.0960 | 1.017 | 0.1345 | 0.124 | 0.038 | 14.3 | 1.310 | n/a | n/a | n/a | n/a |
| T6[0.7] | n20 | pooled_retention | 0.7000 | 0.6984 | -0.0016 | 0.0702 | 0.8715 | 0.0020 | 0.1265 | 1.001 | 0.1472 | 0.788 | 0.000 | 15.0 | 2.260 | n/a | 8.6 | n/a | n/a |
| T6[0.7] | n80 | large | 6.3077 | 6.2706 | -0.0371 | 1.1105 | 0.9335 | 0.0045 | 0.0620 | 1.007 | 2.4640 | 0.149 | 0.357 | 9.1 | 1.128 | n/a | n/a | n/a | n/a |
| T6[0.7] | n80 | carries | 0.7000 | 0.7004 | 0.0004 | 0.1163 | 0.9340 | 0.0040 | 0.0620 | 1.058 | 0.2455 | 0.625 | 0.037 | 13.6 | 1.097 | n/a | 8.0 | n/a | n/a |
| T6[0.7] | n80 | depends | 0.0214 | -0.6231 | -0.6445 | 24.5550 | 0.9850 | 0.0120 | 0.0030 | 622852.845 | 0.8281 | 0.176 | 0.529 | 7.6 | 0.763 | n/a | 1.9 | n/a | n/a |
| T6[0.7] | n80 | carried_margin | 0.0647 | 0.0429 | -0.0219 | 0.9392 | 0.9265 | 0.0165 | 0.0570 | 1.031 | 2.5199 | 0.127 | 0.635 | 6.3 | 1.185 | n/a | n/a | n/a | n/a |
| T6[0.7] | n80 | own_margin | 3.0262 | 3.0611 | 0.0349 | 1.5942 | 0.9425 | 0.0215 | 0.0360 | 1.006 | 3.6531 | 0.131 | 0.408 | 8.9 | 1.047 | n/a | n/a | n/a | n/a |
| T6[0.7] | n80 | kappa | 0.0094 | -0.0126 | -0.0220 | 0.1421 | 0.9370 | 0.0330 | 0.0300 | 0.974 | 0.3627 | 0.127 | 0.647 | 6.2 | 1.084 | n/a | 6.2 | n/a | n/a |
| T6[0.7] | n80 | shuffled_vs_yardstick | 6.2429 | 6.2277 | -0.0152 | 0.6513 | 0.8695 | 0.0020 | 0.1285 | 0.987 | 1.3491 | 0.137 | 0.000 | 15.2 | 2.278 | n/a | n/a | n/a | n/a |
| T6[0.7] | n80 | carried_added | 6.9100 | 6.8716 | -0.0383 | 1.1716 | 0.9320 | 0.0045 | 0.0635 | 1.003 | 2.5876 | 0.127 | 0.360 | 9.2 | 1.118 | n/a | n/a | n/a | n/a |
| T6[0.7] | n80 | pooled_retention | 0.7000 | 0.6985 | -0.0015 | 0.0700 | 0.8700 | 0.0020 | 0.1280 | 1.004 | 0.1463 | 0.825 | 0.000 | 15.0 | 2.200 | n/a | 7.9 | n/a | n/a |
| T6[0.85] | n20 | large | -0.1807 | -0.1804 | 0.0003 | 0.0554 | 0.9720 | 0.0065 | 0.0215 | 1.125 | 0.1194 | 0.531 | 0.058 | 12.9 | 0.887 | n/a | n/a | n/a | n/a |
| T6[0.85] | n20 | carries | 0.7000 | 0.7020 | 0.0020 | 0.0788 | 0.9085 | 0.0010 | 0.0905 | 1.105 | 0.1701 | 0.598 | 0.032 | 13.6 | 1.448 | n/a | 8.5 | n/a | n/a |
| T6[0.85] | n20 | depends | -0.4724 | -1.0794 | -0.6069 | 13.7731 | 0.9675 | 0.0325 | 0.0000 | 88436.508 | 1.2763 | 0.107 | 0.286 | 10.5 | 0.911 | n/a | 2.7 | n/a | n/a |
| T6[0.85] | n20 | carried_margin | -0.0580 | -0.0562 | 0.0017 | 0.0598 | 0.9635 | 0.0065 | 0.0300 | 1.056 | 0.1231 | 0.117 | 0.074 | 13.2 | 0.916 | n/a | n/a | n/a | n/a |
| T6[0.85] | n20 | own_margin | 0.1227 | 0.1242 | 0.0015 | 0.0523 | 0.9520 | 0.0215 | 0.0265 | 1.024 | 0.1304 | 0.100 | 0.647 | 6.1 | 0.986 | n/a | n/a | n/a | n/a |
| T6[0.85] | n20 | kappa | -0.1375 | -0.1450 | -0.0075 | 0.1472 | 0.9290 | 0.0230 | 0.0480 | 0.952 | 0.3064 | 0.117 | 0.141 | 12.0 | 1.114 | n/a | 6.5 | n/a | n/a |
| T6[0.85] | n20 | shuffled_vs_yardstick | -0.1227 | -0.1242 | -0.0015 | 0.0523 | 0.9520 | 0.0265 | 0.0215 | 1.024 | 0.1304 | 0.100 | 0.647 | 6.1 | 0.986 | n/a | n/a | n/a | n/a |
| T6[0.85] | n20 | carried_added | 0.4216 | 0.4235 | 0.0019 | 0.0689 | 0.9160 | 0.0005 | 0.0835 | 1.013 | 0.1367 | 0.116 | 0.043 | 14.2 | 1.273 | n/a | n/a | n/a | n/a |
| T6[0.85] | n20 | pooled_retention | 0.7000 | 0.7003 | 0.0003 | 0.0705 | 0.8760 | 0.0030 | 0.1210 | 1.009 | 0.1497 | 0.773 | 0.000 | 15.0 | 2.213 | n/a | 8.5 | n/a | n/a |
| T6[0.85] | n80 | large | 6.3077 | 6.3554 | 0.0477 | 1.1160 | 0.9360 | 0.0085 | 0.0555 | 1.009 | 2.4613 | 0.163 | 0.340 | 9.3 | 1.066 | n/a | n/a | n/a | n/a |
| T6[0.85] | n80 | carries | 0.7000 | 0.7082 | 0.0082 | 0.1142 | 0.9455 | 0.0025 | 0.0520 | 1.139 | 0.2503 | 0.610 | 0.032 | 13.4 | 1.029 | n/a | 7.9 | n/a | n/a |
| T6[0.85] | n80 | depends | -0.9572 | -0.7123 | 0.2449 | 34.1420 | 0.8460 | 0.1540 | 0.0000 | 851076.098 | 2.8415 | 0.128 | 0.515 | 8.2 | 1.937 | n/a | 0.9 | n/a | n/a |
| T6[0.85] | n80 | carried_margin | -1.4483 | -1.4011 | 0.0472 | 0.9487 | 0.9400 | 0.0235 | 0.0365 | 1.038 | 2.4247 | 0.143 | 0.602 | 6.6 | 1.080 | n/a | n/a | n/a | n/a |
| T6[0.85] | n80 | own_margin | 1.5131 | 1.5422 | 0.0292 | 1.6940 | 0.9535 | 0.0185 | 0.0280 | 0.998 | 3.7848 | 0.129 | 0.339 | 9.5 | 0.988 | n/a | n/a | n/a | n/a |
| T6[0.85] | n80 | kappa | -0.2096 | -0.2235 | -0.0139 | 0.1694 | 0.9340 | 0.0395 | 0.0265 | 0.980 | 0.4341 | 0.142 | 0.637 | 6.3 | 1.095 | n/a | 6.3 | n/a | n/a |
| T6[0.85] | n80 | shuffled_vs_yardstick | 7.7560 | 7.7565 | 0.0005 | 0.8049 | 0.8750 | 0.0020 | 0.1230 | 0.997 | 1.6947 | 0.135 | 0.000 | 15.1 | 2.255 | n/a | n/a | n/a | n/a |
| T6[0.85] | n80 | carried_added | 6.9100 | 6.9592 | 0.0493 | 1.1780 | 0.9360 | 0.0085 | 0.0555 | 1.004 | 2.5868 | 0.141 | 0.341 | 9.3 | 1.076 | n/a | n/a | n/a | n/a |
| T6[0.85] | n80 | pooled_retention | 0.7000 | 0.7000 | -0.0000 | 0.0704 | 0.8745 | 0.0020 | 0.1235 | 1.009 | 0.1487 | 0.806 | 0.000 | 15.0 | 2.222 | n/a | 7.9 | n/a | n/a |
| T6[0.95] | n20 | large | -0.1807 | -0.1806 | 0.0001 | 0.0535 | 0.9720 | 0.0065 | 0.0215 | 1.192 | 0.1177 | 0.539 | 0.061 | 12.9 | 0.889 | n/a | n/a | n/a | n/a |
| T6[0.95] | n20 | carries | 0.7000 | 0.7005 | 0.0005 | 0.0764 | 0.9030 | 0.0020 | 0.0950 | 1.152 | 0.1706 | 0.607 | 0.026 | 13.7 | 1.528 | n/a | 8.7 | n/a | n/a |
| T6[0.95] | n20 | depends | -3.4173 | -13.6323 | -10.2150 | 239.0143 | 0.7850 | 0.2150 | 0.0000 | 3707396.274 | 8.2428 | 0.104 | 0.469 | 8.3 | 2.430 | n/a | 0.9 | n/a | n/a |
| T6[0.95] | n20 | carried_margin | -0.1398 | -0.1402 | -0.0004 | 0.0653 | 0.9615 | 0.0150 | 0.0235 | 0.986 | 0.1337 | 0.110 | 0.044 | 13.9 | 0.960 | n/a | n/a | n/a | n/a |
| T6[0.95] | n20 | own_margin | 0.0409 | 0.0404 | -0.0005 | 0.0553 | 0.9530 | 0.0280 | 0.0190 | 1.020 | 0.1290 | 0.117 | 0.559 | 7.2 | 0.984 | n/a | n/a | n/a | n/a |
| T6[0.95] | n20 | kappa | -0.3315 | -0.3484 | -0.0169 | 0.1746 | 0.9115 | 0.0205 | 0.0680 | 0.885 | 0.3558 | 0.108 | 0.150 | 11.6 | 1.273 | n/a | 6.6 | n/a | n/a |
| T6[0.95] | n20 | shuffled_vs_yardstick | -0.0409 | -0.0404 | 0.0005 | 0.0553 | 0.9530 | 0.0190 | 0.0280 | 1.020 | 0.1290 | 0.117 | 0.559 | 7.2 | 0.984 | n/a | n/a | n/a | n/a |
| T6[0.95] | n20 | carried_added | 0.4216 | 0.4212 | -0.0004 | 0.0679 | 0.9075 | 0.0020 | 0.0905 | 1.010 | 0.1369 | 0.108 | 0.035 | 14.2 | 1.307 | n/a | n/a | n/a | n/a |
| T6[0.95] | n20 | pooled_retention | 0.7000 | 0.7001 | 0.0001 | 0.0703 | 0.8740 | 0.0030 | 0.1230 | 1.003 | 0.1475 | 0.766 | 0.000 | 15.0 | 2.191 | n/a | 8.6 | n/a | n/a |
| T6[0.95] | n80 | large | 6.3077 | 6.2947 | -0.0130 | 1.1108 | 0.9400 | 0.0055 | 0.0545 | 1.002 | 2.4426 | 0.149 | 0.347 | 9.2 | 1.084 | n/a | n/a | n/a | n/a |
| T6[0.95] | n80 | carries | 0.7000 | 0.7069 | 0.0069 | 0.1139 | 0.9515 | 0.0030 | 0.0455 | 1.117 | 0.2479 | 0.617 | 0.029 | 13.4 | 0.981 | n/a | 8.0 | n/a | n/a |
| T6[0.95] | n80 | depends | -4.8716 | 4.4044 | 9.2760 | 167.4496 | 0.5750 | 0.4250 | 0.0000 | 10237307.952 | 6.6771 | 0.164 | 0.389 | 9.5 | 5.383 | n/a | 0.3 | n/a | n/a |
| T6[0.95] | n80 | carried_margin | -2.4571 | -2.4715 | -0.0144 | 0.9840 | 0.9340 | 0.0240 | 0.0420 | 1.006 | 2.4289 | 0.131 | 0.569 | 7.0 | 1.104 | n/a | n/a | n/a | n/a |
| T6[0.95] | n80 | own_margin | 0.5044 | 0.4617 | -0.0427 | 1.7416 | 0.9535 | 0.0195 | 0.0270 | 0.995 | 3.8722 | 0.126 | 0.301 | 10.0 | 0.984 | n/a | n/a | n/a | n/a |
| T6[0.95] | n80 | kappa | -0.3556 | -0.3841 | -0.0285 | 0.1945 | 0.9350 | 0.0335 | 0.0315 | 0.961 | 0.4916 | 0.132 | 0.635 | 6.3 | 1.125 | n/a | 6.3 | n/a | n/a |
| T6[0.95] | n80 | shuffled_vs_yardstick | 8.7647 | 8.7661 | 0.0014 | 0.9061 | 0.8725 | 0.0045 | 0.1230 | 0.982 | 1.8744 | 0.153 | 0.000 | 15.1 | 2.231 | n/a | n/a | n/a | n/a |
| T6[0.95] | n80 | carried_added | 6.9100 | 6.8965 | -0.0134 | 1.1716 | 0.9405 | 0.0060 | 0.0535 | 0.999 | 2.5567 | 0.133 | 0.350 | 9.3 | 1.090 | n/a | n/a | n/a | n/a |
| T6[0.95] | n80 | pooled_retention | 0.7000 | 0.6999 | -0.0001 | 0.0704 | 0.8705 | 0.0045 | 0.1250 | 0.997 | 0.1466 | 0.814 | 0.000 | 15.0 | 2.130 | n/a | 8.0 | n/a | n/a |
| T6[1] | n20 | large | -0.1807 | -0.1811 | -0.0004 | 0.0549 | 0.9785 | 0.0055 | 0.0160 | 1.120 | 0.1178 | 0.530 | 0.061 | 12.9 | 0.871 | n/a | n/a | n/a | n/a |
| T6[1] | n20 | carries | 0.7000 | 0.6998 | -0.0002 | 0.0793 | 0.8935 | 0.0005 | 0.1060 | 1.068 | 0.1694 | 0.605 | 0.029 | 13.7 | 1.504 | n/a | 8.6 | n/a | n/a |
| T6[1] | n20 | depends | n/a | -6.5602 | n/a | 165.1243 | n/a | n/a | n/a | 602150.739 | 16.6170 | 0.128 | 0.517 | 7.8 | n/a | n/a | 0.0 | n/a | n/a |
| T6[1] | n20 | carried_margin | -0.1807 | -0.1811 | -0.0004 | 0.0665 | 0.9715 | 0.0125 | 0.0160 | 1.023 | 0.1376 | 0.124 | 0.036 | 14.2 | 0.898 | n/a | n/a | n/a | n/a |
| T6[1] | n20 | own_margin | 0.0000 | -0.0000 | -0.0000 | 0.0573 | 0.9515 | 0.0310 | 0.0175 | 0.997 | 0.1351 | 0.104 | 0.534 | 7.4 | 0.971 | n/a | n/a | n/a | n/a |
| T6[1] | n20 | kappa | -0.4286 | -0.4475 | -0.0189 | 0.1828 | 0.9170 | 0.0205 | 0.0625 | 0.919 | 0.3784 | 0.123 | 0.169 | 11.6 | 1.145 | n/a | 6.6 | n/a | n/a |
| T6[1] | n20 | shuffled_vs_yardstick | 0.0000 | 0.0000 | 0.0000 | 0.0573 | 0.9515 | 0.0175 | 0.0310 | 0.997 | 0.1351 | 0.104 | 0.534 | 7.4 | 0.971 | n/a | n/a | n/a | n/a |
| T6[1] | n20 | carried_added | 0.4216 | 0.4206 | -0.0010 | 0.0688 | 0.9085 | 0.0020 | 0.0895 | 0.990 | 0.1345 | 0.121 | 0.037 | 14.3 | 1.296 | n/a | n/a | n/a | n/a |
| T6[1] | n20 | pooled_retention | 0.7000 | 0.6996 | -0.0004 | 0.0702 | 0.8750 | 0.0010 | 0.1240 | 1.011 | 0.1494 | 0.763 | 0.000 | 15.0 | 2.314 | n/a | 8.7 | n/a | n/a |
| T6[1] | n80 | large | 6.3077 | 6.3165 | 0.0089 | 1.1072 | 0.9425 | 0.0070 | 0.0505 | 1.003 | 2.4452 | 0.165 | 0.328 | 9.3 | 1.042 | n/a | n/a | n/a | n/a |
| T6[1] | n80 | carries | 0.7000 | 0.7046 | 0.0046 | 0.1135 | 0.9400 | 0.0030 | 0.0570 | 1.119 | 0.2451 | 0.645 | 0.027 | 13.7 | 1.052 | n/a | 8.0 | n/a | n/a |
| T6[1] | n80 | depends | n/a | -1.2158 | n/a | 75.1012 | n/a | n/a | n/a | 3359769.108 | 7.5385 | 0.200 | 0.342 | 10.0 | n/a | n/a | 0.0 | n/a | n/a |
| T6[1] | n80 | carried_margin | -2.9614 | -2.9449 | 0.0165 | 0.9981 | 0.9460 | 0.0210 | 0.0330 | 0.991 | 2.4190 | 0.145 | 0.545 | 7.2 | 1.020 | n/a | n/a | n/a | n/a |
| T6[1] | n80 | own_margin | 0.0000 | 0.0288 | 0.0288 | 1.7756 | 0.9525 | 0.0235 | 0.0240 | 1.004 | 3.9587 | 0.130 | 0.284 | 10.3 | 0.988 | n/a | n/a | n/a | n/a |
| T6[1] | n80 | kappa | -0.4286 | -0.4521 | -0.0235 | 0.2013 | 0.9315 | 0.0340 | 0.0345 | 0.954 | 0.5145 | 0.145 | 0.636 | 6.3 | 1.090 | n/a | 6.3 | n/a | n/a |
| T6[1] | n80 | shuffled_vs_yardstick | 9.2691 | 9.2614 | -0.0076 | 0.9553 | 0.8720 | 0.0005 | 0.1275 | 0.990 | 1.9855 | 0.150 | 0.000 | 15.1 | 2.351 | n/a | n/a | n/a | n/a |
| T6[1] | n80 | carried_added | 6.9100 | 6.9182 | 0.0082 | 1.1675 | 0.9420 | 0.0070 | 0.0510 | 1.000 | 2.5601 | 0.144 | 0.335 | 9.3 | 1.056 | n/a | n/a | n/a | n/a |
| T6[1] | n80 | pooled_retention | 0.7000 | 0.6995 | -0.0005 | 0.0705 | 0.8745 | 0.0010 | 0.1245 | 0.999 | 0.1480 | 0.806 | 0.000 | 15.0 | 2.312 | n/a | 8.0 | n/a | n/a |
| T6[1.1] | n20 | large | -0.1807 | -0.1801 | 0.0006 | 0.0551 | 0.9740 | 0.0065 | 0.0195 | 1.150 | 0.1187 | 0.535 | 0.053 | 12.9 | 0.898 | n/a | n/a | n/a | n/a |
| T6[1.1] | n20 | carries | 0.7000 | 0.7025 | 0.0025 | 0.0791 | 0.8985 | 0.0020 | 0.0995 | 1.103 | 0.1719 | 0.613 | 0.025 | 13.7 | 1.514 | n/a | 8.6 | n/a | n/a |
| T6[1.1] | n20 | depends | 3.2086 | 3.3306 | 0.1219 | 64.4510 | 0.8895 | 0.0000 | 0.1105 | 170165.757 | 4.6528 | 0.231 | 0.423 | 8.5 | 1.480 | n/a | -1.5 | n/a | n/a |
| T6[1.1] | n20 | carried_margin | -0.2625 | -0.2594 | 0.0031 | 0.0735 | 0.9635 | 0.0275 | 0.0090 | 0.980 | 0.1503 | 0.117 | 0.021 | 14.7 | 0.934 | n/a | n/a | n/a | n/a |
| T6[1.1] | n20 | own_margin | -0.0818 | -0.0793 | 0.0025 | 0.0615 | 0.9465 | 0.0440 | 0.0095 | 0.978 | 0.1361 | 0.125 | 0.461 | 8.3 | 1.029 | n/a | n/a | n/a | n/a |
| T6[1.1] | n20 | kappa | -0.6226 | -0.6326 | -0.0100 | 0.2098 | 0.9175 | 0.0215 | 0.0610 | 0.884 | 0.4240 | 0.117 | 0.168 | 11.4 | 1.191 | n/a | 6.6 | n/a | n/a |
| T6[1.1] | n20 | shuffled_vs_yardstick | 0.0818 | 0.0793 | -0.0025 | 0.0615 | 0.9465 | 0.0095 | 0.0440 | 0.978 | 0.1361 | 0.125 | 0.461 | 8.3 | 1.029 | n/a | n/a | n/a | n/a |
| T6[1.1] | n20 | carried_added | 0.4216 | 0.4241 | 0.0025 | 0.0702 | 0.9170 | 0.0010 | 0.0820 | 0.974 | 0.1370 | 0.117 | 0.033 | 14.3 | 1.240 | n/a | n/a | n/a | n/a |
| T6[1.1] | n20 | pooled_retention | 0.7000 | 0.6996 | -0.0004 | 0.0708 | 0.8765 | 0.0025 | 0.1210 | 0.982 | 0.1474 | 0.754 | 0.000 | 15.0 | 2.336 | n/a | 8.5 | n/a | n/a |
| T6[1.1] | n80 | large | 6.3077 | 6.3120 | 0.0043 | 1.1041 | 0.9430 | 0.0085 | 0.0485 | 1.021 | 2.4422 | 0.149 | 0.353 | 9.2 | 1.048 | n/a | n/a | n/a | n/a |
| T6[1.1] | n80 | carries | 0.7000 | 0.6995 | -0.0005 | 0.1099 | 0.9440 | 0.0040 | 0.0520 | 1.181 | 0.2467 | 0.621 | 0.035 | 13.5 | 1.028 | n/a | 8.0 | n/a | n/a |
| T6[1.1] | n80 | depends | 3.9358 | 2.1036 | -1.8322 | 31.7421 | 0.7305 | 0.0000 | 0.2695 | 257470.515 | 7.0066 | 0.246 | 0.245 | 10.9 | 3.006 | n/a | -0.5 | n/a | n/a |
| T6[1.1] | n80 | carried_margin | -3.9701 | -3.9564 | 0.0138 | 1.0326 | 0.9495 | 0.0240 | 0.0265 | 1.016 | 2.4431 | 0.128 | 0.509 | 7.7 | 1.000 | n/a | n/a | n/a | n/a |
| T6[1.1] | n80 | own_margin | -1.0087 | -0.9190 | 0.0897 | 1.8104 | 0.9590 | 0.0235 | 0.0175 | 1.041 | 4.0518 | 0.133 | 0.256 | 10.8 | 0.952 | n/a | n/a | n/a | n/a |
| T6[1.1] | n80 | kappa | -0.5746 | -0.6008 | -0.0262 | 0.2205 | 0.9330 | 0.0375 | 0.0295 | 0.997 | 0.5725 | 0.127 | 0.638 | 6.3 | 1.146 | n/a | 6.3 | n/a | n/a |
| T6[1.1] | n80 | shuffled_vs_yardstick | 10.2778 | 10.2684 | -0.0094 | 1.0603 | 0.8765 | 0.0025 | 0.1210 | 0.970 | 2.1794 | 0.176 | 0.000 | 15.1 | 2.335 | n/a | n/a | n/a | n/a |
| T6[1.1] | n80 | carried_added | 6.9100 | 6.9162 | 0.0062 | 1.1654 | 0.9420 | 0.0080 | 0.0500 | 1.016 | 2.5581 | 0.129 | 0.356 | 9.2 | 1.065 | n/a | n/a | n/a | n/a |
| T6[1.1] | n80 | pooled_retention | 0.7000 | 0.6994 | -0.0006 | 0.0708 | 0.8770 | 0.0025 | 0.1205 | 0.980 | 0.1457 | 0.812 | 0.000 | 15.0 | 2.259 | n/a | 8.0 | n/a | n/a |
| T6[1.25] | n20 | large | -0.1807 | -0.1821 | -0.0014 | 0.0551 | 0.9740 | 0.0050 | 0.0210 | 1.168 | 0.1199 | 0.524 | 0.068 | 12.9 | 0.873 | n/a | n/a | n/a | n/a |
| T6[1.25] | n20 | carries | 0.7000 | 0.7000 | -0.0000 | 0.0777 | 0.9100 | 0.0015 | 0.0885 | 1.126 | 0.1709 | 0.605 | 0.033 | 13.7 | 1.465 | n/a | 8.4 | n/a | n/a |
| T6[1.25] | n20 | depends | 1.8835 | 1.8546 | -0.0289 | 9.1743 | 0.9460 | 0.0030 | 0.0510 | 20198.216 | 0.9710 | 0.321 | 0.289 | 9.8 | 1.024 | n/a | -3.2 | n/a | n/a |
| T6[1.25] | n20 | carried_margin | -0.3852 | -0.3846 | 0.0006 | 0.0803 | 0.9515 | 0.0425 | 0.0060 | 1.034 | 0.1722 | 0.117 | 0.015 | 15.1 | 0.995 | n/a | n/a | n/a | n/a |
| T6[1.25] | n20 | own_margin | -0.2045 | -0.2025 | 0.0021 | 0.0695 | 0.9505 | 0.0430 | 0.0065 | 1.007 | 0.1515 | 0.107 | 0.355 | 9.7 | 0.999 | n/a | n/a | n/a | n/a |
| T6[1.25] | n20 | kappa | -0.9137 | -0.9327 | -0.0190 | 0.2386 | 0.9280 | 0.0155 | 0.0565 | 0.944 | 0.4992 | 0.115 | 0.191 | 11.3 | 1.123 | n/a | 6.5 | n/a | n/a |
| T6[1.25] | n20 | shuffled_vs_yardstick | 0.2045 | 0.2025 | -0.0021 | 0.0695 | 0.9505 | 0.0065 | 0.0430 | 1.007 | 0.1515 | 0.107 | 0.355 | 9.7 | 0.999 | n/a | n/a | n/a | n/a |
| T6[1.25] | n20 | carried_added | 0.4216 | 0.4236 | 0.0020 | 0.0714 | 0.9060 | 0.0020 | 0.0920 | 0.941 | 0.1373 | 0.117 | 0.042 | 14.2 | 1.344 | n/a | n/a | n/a | n/a |
| T6[1.25] | n20 | pooled_retention | 0.7000 | 0.7010 | 0.0010 | 0.0728 | 0.8695 | 0.0025 | 0.1280 | 0.949 | 0.1485 | 0.769 | 0.000 | 15.0 | 2.370 | n/a | 8.6 | n/a | n/a |
| T6[1.25] | n80 | large | 6.3077 | 6.3308 | 0.0232 | 1.1489 | 0.9375 | 0.0075 | 0.0550 | 0.951 | 2.4687 | 0.157 | 0.344 | 9.2 | 1.070 | n/a | n/a | n/a | n/a |
| T6[1.25] | n80 | carries | 0.7000 | 0.7076 | 0.0076 | 0.1168 | 0.9420 | 0.0035 | 0.0545 | 1.082 | 0.2482 | 0.623 | 0.027 | 13.6 | 1.050 | n/a | 8.0 | n/a | n/a |
| T6[1.25] | n80 | depends | 2.1743 | -0.4781 | -2.6524 | 85.4060 | 0.8685 | 0.0000 | 0.1315 | 1019591.044 | 2.8213 | 0.311 | 0.183 | 11.5 | 1.672 | n/a | -1.4 | n/a | n/a |
| T6[1.25] | n80 | carried_margin | -5.4832 | -5.4721 | 0.0111 | 1.1126 | 0.9535 | 0.0300 | 0.0165 | 0.999 | 2.5007 | 0.141 | 0.413 | 8.6 | 0.979 | n/a | n/a | n/a | n/a |
| T6[1.25] | n80 | own_margin | -2.5218 | -2.5336 | -0.0118 | 1.9736 | 0.9515 | 0.0300 | 0.0185 | 0.995 | 4.3055 | 0.139 | 0.221 | 11.4 | 0.991 | n/a | n/a | n/a | n/a |
| T6[1.25] | n80 | kappa | -0.7935 | -0.8237 | -0.0302 | 0.2556 | 0.9285 | 0.0380 | 0.0335 | 0.960 | 0.6511 | 0.142 | 0.630 | 6.3 | 1.094 | n/a | 6.3 | n/a | n/a |
| T6[1.25] | n80 | shuffled_vs_yardstick | 11.7909 | 11.8030 | 0.0121 | 1.2465 | 0.8695 | 0.0025 | 0.1280 | 0.938 | 2.5168 | 0.176 | 0.000 | 15.1 | 2.460 | n/a | n/a | n/a | n/a |
| T6[1.25] | n80 | carried_added | 6.9100 | 6.9365 | 0.0265 | 1.2141 | 0.9380 | 0.0070 | 0.0550 | 0.946 | 2.5827 | 0.144 | 0.349 | 9.3 | 1.057 | n/a | n/a | n/a | n/a |
| T6[1.25] | n80 | pooled_retention | 0.7000 | 0.7008 | 0.0008 | 0.0727 | 0.8705 | 0.0025 | 0.1270 | 0.950 | 0.1487 | 0.831 | 0.000 | 15.0 | 2.316 | n/a | 7.9 | n/a | n/a |
| T7 | h5 | large | 2.9822 | 2.9931 | 0.0110 | 0.2984 | 0.8890 | 0.0030 | 0.1080 | 1.116 | 0.6587 | 0.440 | 0.000 | 15.4 | 1.920 | n/a | n/a | 0.701 | 0.8795 |
| T7 | h5 | carries | 0.7000 | 0.7025 | 0.0025 | 0.0706 | 0.8920 | 0.0020 | 0.1060 | 1.097 | 0.1562 | 0.603 | 0.000 | 15.1 | 2.248 | n/a | 141.2 | 0.701 | 0.8795 |
| T7 | h5 | depends | 0.6888 | 0.6919 | 0.0031 | 0.0711 | 0.8930 | 0.0010 | 0.1060 | 1.108 | 0.1565 | 0.600 | 0.000 | 15.1 | 2.261 | n/a | 75.3 | 0.701 | 0.8805 |
| T7 | h5 | carried_margin | 3.4005 | 3.4109 | 0.0104 | 0.3121 | 0.8910 | 0.0015 | 0.1075 | 1.101 | 0.6897 | 0.560 | 0.000 | 15.2 | 2.133 | n/a | n/a | 0.701 | 0.8795 |
| T7 | h5 | own_margin | 4.9368 | 4.9356 | -0.0012 | 0.0636 | 0.9415 | 0.0530 | 0.0055 | 1.124 | 0.1427 | 0.538 | 0.057 | 13.1 | 1.046 | n/a | n/a | 0.701 | 0.9415 |
| T7 | h5 | kappa | 0.9486 | 0.9490 | 0.0004 | 0.0060 | 0.8870 | 0.1015 | 0.0115 | 0.980 | 0.0130 | 0.549 | 0.000 | 15.1 | 1.971 | n/a | 9.9 | 0.701 | 0.8775 |
| T7 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4178 | 0.0006 | 0.0554 | 0.9095 | 0.0750 | 0.0155 | 1.069 | 0.1480 | 0.197 | 0.639 | 6.1 | 1.398 | n/a | n/a | 0.701 | 0.9095 |
| T7 | h5 | carried_added | 3.5847 | 3.5963 | 0.0116 | 0.3515 | 0.8910 | 0.0020 | 0.1070 | 1.098 | 0.7766 | 0.562 | 0.000 | 15.1 | 2.169 | n/a | n/a | 0.701 | 0.8785 |
| T7 | h5 | pooled_retention | 0.7000 | 0.7022 | 0.0022 | 0.0684 | 0.8905 | 0.0020 | 0.1075 | 1.098 | 0.1513 | 0.594 | 0.000 | 15.1 | 2.246 | n/a | 143.3 | 0.701 | 0.8785 |
| T8 | n20 | large | -0.1807 | -0.1820 | -0.0013 | 0.0751 | 0.9790 | 0.0030 | 0.0180 | 1.176 | 0.1746 | 0.532 | 0.067 | 6.7 | 0.837 | n/a | n/a | n/a | n/a |
| T8 | n20 | carries | 0.7000 | 0.6995 | -0.0005 | 0.1086 | 0.8450 | 0.0010 | 0.1540 | 1.108 | 0.2482 | 0.584 | 0.042 | 6.9 | 1.674 | n/a | 7.0 | n/a | n/a |
| T8 | n20 | depends | 0.5678 | 0.5686 | 0.0008 | 0.1558 | 0.8285 | 0.0010 | 0.1705 | 1.099 | 0.3367 | 0.579 | 0.022 | 7.0 | 1.521 | n/a | 8.7 | n/a | n/a |
| T8 | n20 | carried_margin | 0.2374 | 0.2364 | -0.0010 | 0.0686 | 0.8260 | 0.0010 | 0.1730 | 1.059 | 0.1399 | 0.190 | 0.182 | 6.8 | 1.820 | n/a | n/a | n/a | n/a |
| T8 | n20 | own_margin | 0.4181 | 0.4184 | 0.0003 | 0.0602 | 0.9115 | 0.0035 | 0.0850 | 1.090 | 0.1374 | 0.188 | 0.523 | 4.8 | 1.248 | n/a | n/a | n/a | n/a |
| T8 | n20 | kappa | 0.5631 | 0.5615 | -0.0016 | 0.1000 | 0.9025 | 0.0750 | 0.0225 | 0.837 | 0.2145 | 0.192 | 0.012 | 7.8 | 1.163 | n/a | 5.1 | n/a | n/a |
| T8 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4184 | -0.0003 | 0.0602 | 0.9115 | 0.0850 | 0.0035 | 1.090 | 0.1374 | 0.188 | 0.523 | 4.8 | 1.248 | n/a | n/a | n/a | n/a |
| T8 | n20 | carried_added | 0.4216 | 0.4207 | -0.0009 | 0.0891 | 0.8735 | 0.0000 | 0.1265 | 1.067 | 0.1879 | 0.189 | 0.040 | 7.6 | 1.996 | n/a | n/a | n/a | n/a |
| T8 | n20 | pooled_retention | 0.7000 | 0.7001 | 0.0001 | 0.0992 | 0.7535 | 0.0015 | 0.2450 | 1.035 | 0.2362 | 0.663 | 0.000 | 7.1 | 2.112 | n/a | 7.0 | n/a | n/a |
| T8 | n40 | large | 0.7895 | 0.7852 | -0.0042 | 0.2462 | 0.9165 | 0.0010 | 0.0825 | 1.097 | 0.5584 | 0.451 | 0.019 | 7.3 | 1.297 | n/a | n/a | n/a | n/a |
| T8 | n40 | carries | 0.7000 | 0.7039 | 0.0039 | 0.1301 | 0.9490 | 0.0030 | 0.0480 | 1.146 | 0.3200 | 0.587 | 0.008 | 7.2 | 1.003 | n/a | 6.2 | n/a | n/a |
| T8 | n40 | depends | 0.6694 | 0.6750 | 0.0056 | 0.1405 | 0.9445 | 0.0030 | 0.0525 | 1.153 | 0.3454 | 0.578 | 0.009 | 7.2 | 1.051 | n/a | 6.3 | n/a | n/a |
| T8 | n40 | carried_margin | 1.2076 | 1.2037 | -0.0039 | 0.2677 | 0.9235 | 0.0010 | 0.0755 | 1.071 | 0.5993 | 0.275 | 0.051 | 7.4 | 1.196 | n/a | n/a | n/a | n/a |
| T8 | n40 | own_margin | 1.8041 | 1.8026 | -0.0015 | 0.2923 | 0.9300 | 0.0060 | 0.0640 | 1.079 | 0.6770 | 0.286 | 0.128 | 6.8 | 1.190 | n/a | n/a | n/a | n/a |
| T8 | n40 | kappa | 0.8677 | 0.8666 | -0.0011 | 0.0323 | 0.9055 | 0.0815 | 0.0130 | 0.886 | 0.0693 | 0.276 | 0.022 | 7.6 | 1.207 | n/a | 4.8 | n/a | n/a |
| T8 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4185 | -0.0004 | 0.0602 | 0.9125 | 0.0845 | 0.0030 | 1.089 | 0.1379 | 0.191 | 0.523 | 4.8 | 1.246 | n/a | n/a | n/a | n/a |
| T8 | n40 | carried_added | 1.3918 | 1.3879 | -0.0038 | 0.2996 | 0.9225 | 0.0005 | 0.0770 | 1.066 | 0.6649 | 0.277 | 0.035 | 7.5 | 1.219 | n/a | n/a | n/a | n/a |
| T8 | n40 | pooled_retention | 0.7000 | 0.7000 | -0.0000 | 0.0987 | 0.7590 | 0.0015 | 0.2395 | 1.042 | 0.2347 | 0.637 | 0.000 | 7.1 | 2.090 | n/a | 6.2 | n/a | n/a |
| T8 | n80 | large | 6.3077 | 6.3354 | 0.0277 | 1.3905 | 0.9370 | 0.0040 | 0.0590 | 1.039 | 3.2449 | 0.294 | 0.190 | 6.5 | 1.139 | n/a | n/a | n/a | n/a |
| T8 | n80 | carries | 0.7000 | 0.7126 | 0.0126 | 0.1626 | 0.9375 | 0.0020 | 0.0605 | 1.157 | 0.3812 | 0.637 | 0.041 | 6.9 | 1.105 | n/a | 6.8 | n/a | n/a |
| T8 | n80 | depends | 0.6943 | 0.7079 | 0.0136 | 0.1649 | 0.9380 | 0.0020 | 0.0600 | 1.166 | 0.3840 | 0.636 | 0.043 | 6.9 | 1.102 | n/a | 6.7 | n/a | n/a |
| T8 | n80 | carried_margin | 6.7258 | 6.7538 | 0.0280 | 1.4266 | 0.9340 | 0.0035 | 0.0625 | 1.035 | 3.3230 | 0.276 | 0.203 | 6.5 | 1.113 | n/a | n/a | n/a | n/a |
| T8 | n80 | own_margin | 9.6872 | 9.7037 | 0.0165 | 1.5521 | 0.9350 | 0.0155 | 0.0495 | 1.036 | 3.9110 | 0.271 | 0.433 | 5.2 | 1.098 | n/a | n/a | n/a | n/a |
| T8 | n80 | kappa | 0.9733 | 0.9734 | 0.0000 | 0.0063 | 0.9065 | 0.0875 | 0.0060 | 0.911 | 0.0136 | 0.277 | 0.148 | 6.8 | 1.332 | n/a | 5.0 | n/a | n/a |
| T8 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4184 | -0.0003 | 0.0602 | 0.9135 | 0.0830 | 0.0035 | 1.091 | 0.1384 | 0.191 | 0.522 | 4.8 | 1.248 | n/a | n/a | n/a | n/a |
| T8 | n80 | carried_added | 6.9100 | 6.9381 | 0.0281 | 1.4628 | 0.9325 | 0.0035 | 0.0640 | 1.034 | 3.3963 | 0.277 | 0.191 | 6.6 | 1.121 | n/a | n/a | n/a | n/a |
| T8 | n80 | pooled_retention | 0.7000 | 0.6996 | -0.0004 | 0.0985 | 0.7590 | 0.0015 | 0.2395 | 1.042 | 0.2358 | 0.659 | 0.000 | 7.1 | 2.055 | n/a | 6.9 | n/a | n/a |
| T8 | n160 | large | 14.5697 | 14.5960 | 0.0263 | 2.4453 | 0.9360 | 0.0025 | 0.0615 | 1.045 | 5.7414 | 0.567 | 0.029 | 7.1 | 1.074 | n/a | n/a | n/a | n/a |
| T8 | n160 | carries | 0.7000 | 0.7110 | 0.0110 | 0.1639 | 0.8810 | 0.0000 | 0.1190 | 1.130 | 0.3652 | 0.591 | 0.032 | 7.0 | 1.353 | n/a | 11.5 | n/a | n/a |
| T8 | n160 | depends | 0.6974 | 0.7090 | 0.0116 | 0.1651 | 0.8815 | 0.0000 | 0.1185 | 1.135 | 0.3661 | 0.590 | 0.032 | 7.0 | 1.348 | n/a | 11.2 | n/a | n/a |
| T8 | n160 | carried_margin | 14.9878 | 15.0144 | 0.0266 | 2.4669 | 0.9330 | 0.0030 | 0.0640 | 1.045 | 5.7953 | 0.553 | 0.030 | 7.1 | 1.078 | n/a | n/a | n/a | n/a |
| T8 | n160 | own_margin | 21.4901 | 21.5055 | 0.0154 | 1.8006 | 0.9480 | 0.0455 | 0.0065 | 1.240 | 4.7185 | 0.534 | 0.139 | 6.4 | 1.012 | n/a | n/a | n/a | n/a |
| T8 | n160 | kappa | 0.9879 | 0.9881 | 0.0002 | 0.0022 | 0.8575 | 0.1395 | 0.0030 | 0.963 | 0.0050 | 0.555 | 0.011 | 7.2 | 1.585 | n/a | 6.1 | n/a | n/a |
| T8 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4184 | -0.0003 | 0.0602 | 0.9130 | 0.0840 | 0.0030 | 1.089 | 0.1372 | 0.188 | 0.521 | 4.8 | 1.231 | n/a | n/a | n/a | n/a |
| T8 | n160 | carried_added | 15.1720 | 15.1987 | 0.0267 | 2.5157 | 0.9275 | 0.0030 | 0.0695 | 1.043 | 5.9127 | 0.553 | 0.029 | 7.1 | 1.098 | n/a | n/a | n/a | n/a |
| T8 | n160 | pooled_retention | 0.7000 | 0.7001 | 0.0001 | 0.0989 | 0.7550 | 0.0015 | 0.2435 | 1.029 | 0.2340 | 0.522 | 0.000 | 7.1 | 2.120 | n/a | 11.9 | n/a | n/a |
| T8 | n320 | large | 17.0248 | 17.0441 | 0.0193 | 2.7886 | 0.9195 | 0.0020 | 0.0785 | 1.053 | 6.5969 | 0.574 | 0.019 | 7.1 | 1.131 | n/a | n/a | n/a | n/a |
| T8 | n320 | carries | 0.7000 | 0.7106 | 0.0106 | 0.1633 | 0.8775 | 0.0000 | 0.1225 | 1.107 | 0.3639 | 0.594 | 0.026 | 7.1 | 1.410 | n/a | 12.2 | n/a | n/a |
| T8 | n320 | depends | 0.6978 | 0.7088 | 0.0110 | 0.1643 | 0.8785 | 0.0000 | 0.1215 | 1.111 | 0.3645 | 0.595 | 0.026 | 7.1 | 1.408 | n/a | 11.9 | n/a | n/a |
| T8 | n320 | carried_margin | 17.4429 | 17.4625 | 0.0196 | 2.8068 | 0.9180 | 0.0020 | 0.0800 | 1.054 | 6.6485 | 0.572 | 0.019 | 7.1 | 1.146 | n/a | n/a | n/a | n/a |
| T8 | n320 | own_margin | 24.9973 | 25.0131 | 0.0158 | 1.9523 | 0.9460 | 0.0455 | 0.0085 | 1.225 | 5.1155 | 0.577 | 0.117 | 6.4 | 1.011 | n/a | n/a | n/a | n/a |
| T8 | n320 | kappa | 0.9896 | 0.9897 | 0.0002 | 0.0019 | 0.8615 | 0.1335 | 0.0050 | 0.956 | 0.0043 | 0.576 | 0.005 | 7.3 | 1.668 | n/a | 6.2 | n/a | n/a |
| T8 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4184 | -0.0003 | 0.0602 | 0.9145 | 0.0830 | 0.0025 | 1.089 | 0.1381 | 0.190 | 0.521 | 4.8 | 1.263 | n/a | n/a | n/a | n/a |
| T8 | n320 | carried_added | 17.6271 | 17.6468 | 0.0197 | 2.8570 | 0.9130 | 0.0020 | 0.0850 | 1.051 | 6.7641 | 0.572 | 0.019 | 7.2 | 1.160 | n/a | n/a | n/a | n/a |
| T8 | n320 | pooled_retention | 0.7000 | 0.7001 | 0.0001 | 0.0991 | 0.7530 | 0.0015 | 0.2455 | 1.024 | 0.2350 | 0.521 | 0.000 | 7.1 | 2.096 | n/a | 12.6 | n/a | n/a |

## Verdict and Reading Frequencies

Where a signed reading's truth sits on a line, how often each verdict is printed; for the shuffled ratio always, how often each reading.

| Scenario | Row | Statistic | Line | yes | no | undetermined | a | b | c | d | no reading defined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | carries | 0.2 | 0.002 | 0.102 | 0.897 | n/a | n/a | n/a | n/a | n/a |
| P1 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.439 | 0.000 | 0.561 |
| P1 | n40 | carries | 0.2 | 0.005 | 0.034 | 0.961 | n/a | n/a | n/a | n/a | n/a |
| P1 | n40 | depends |  | n/a | n/a | n/a | 0.000 | 0.747 | 0.000 | 0.254 | 0.000 |
| P1 | n80 | carries | 0.2 | 0.004 | 0.059 | 0.938 | n/a | n/a | n/a | n/a | n/a |
| P1 | n80 | depends |  | n/a | n/a | n/a | 0.001 | 0.114 | 0.000 | 0.885 | 0.000 |
| P1 | n160 | carries | 0.2 | 0.000 | 0.094 | 0.906 | n/a | n/a | n/a | n/a | n/a |
| P1 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 0.110 | 0.000 | 0.890 | 0.000 |
| P1 | n320 | carries | 0.2 | 0.000 | 0.100 | 0.900 | n/a | n/a | n/a | n/a | n/a |
| P1 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 0.114 | 0.000 | 0.886 | 0.000 |
| P1 | h2 | carries | 0.2 | 0.003 | 0.120 | 0.877 | n/a | n/a | n/a | n/a | n/a |
| P1 | h2 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P1 | h5 | carries | 0.2 | 0.003 | 0.121 | 0.875 | n/a | n/a | n/a | n/a | n/a |
| P1 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 0.513 | 0.000 | 0.486 | 0.000 |
| P1 | h10 | carries | 0.2 | 0.000 | 0.258 | 0.743 | n/a | n/a | n/a | n/a | n/a |
| P1 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 0.435 | 0.000 | 0.565 | 0.000 |
| P2 | n20 | depends |  | n/a | n/a | n/a | 0.602 | 0.000 | 0.000 | 0.399 | 0.000 |
| P2 | n40 | depends |  | n/a | n/a | n/a | 0.999 | 0.000 | 0.000 | 0.001 | 0.000 |
| P2 | n80 | depends |  | n/a | n/a | n/a | 0.995 | 0.000 | 0.000 | 0.005 | 0.000 |
| P2 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P2 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P2 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P2 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P2 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P3 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P4 | n20 | carries | 0.2 | 0.002 | 0.099 | 0.900 | n/a | n/a | n/a | n/a | n/a |
| P4 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.595 | 0.001 | 0.405 |
| P4 | n40 | carries | 0.2 | 0.011 | 0.038 | 0.951 | n/a | n/a | n/a | n/a | n/a |
| P4 | n40 | depends |  | n/a | n/a | n/a | 0.000 | 0.723 | 0.003 | 0.274 | 0.000 |
| P4 | n80 | carries | 0.2 | 0.002 | 0.053 | 0.945 | n/a | n/a | n/a | n/a | n/a |
| P4 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.119 | 0.000 | 0.880 | 0.000 |
| P4 | n160 | carries | 0.2 | 0.000 | 0.089 | 0.910 | n/a | n/a | n/a | n/a | n/a |
| P4 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 0.104 | 0.000 | 0.896 | 0.000 |
| P4 | n320 | carries | 0.2 | 0.001 | 0.093 | 0.906 | n/a | n/a | n/a | n/a | n/a |
| P4 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 0.115 | 0.000 | 0.885 | 0.000 |
| P4 | h2 | carries | 0.2 | 0.001 | 0.120 | 0.878 | n/a | n/a | n/a | n/a | n/a |
| P4 | h2 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P4 | h5 | carries | 0.2 | 0.002 | 0.123 | 0.875 | n/a | n/a | n/a | n/a | n/a |
| P4 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 0.490 | 0.000 | 0.509 | 0.000 |
| P4 | h10 | carries | 0.2 | 0.000 | 0.247 | 0.752 | n/a | n/a | n/a | n/a | n/a |
| P4 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 0.427 | 0.000 | 0.573 | 0.000 |
| P5 | n20 | depends |  | n/a | n/a | n/a | 0.607 | 0.000 | 0.000 | 0.394 | 0.000 |
| P5 | n40 | depends |  | n/a | n/a | n/a | 0.999 | 0.000 | 0.000 | 0.002 | 0.000 |
| P5 | n80 | depends |  | n/a | n/a | n/a | 0.994 | 0.000 | 0.000 | 0.006 | 0.000 |
| P5 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| P6 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P7 | n20 | large | 0.0 | 0.001 | 0.080 | 0.919 | n/a | n/a | n/a | n/a | n/a |
| P7 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P7 | n40 | large | 0.0 | 0.006 | 0.043 | 0.952 | n/a | n/a | n/a | n/a | n/a |
| P7 | n40 | depends |  | n/a | n/a | n/a | 0.049 | 0.007 | 0.000 | 0.944 | 0.000 |
| P7 | n80 | large | 0.0 | 0.010 | 0.020 | 0.970 | n/a | n/a | n/a | n/a | n/a |
| P7 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.001 | 0.000 | 0.000 |
| P7 | n160 | large | 0.0 | 0.018 | 0.009 | 0.973 | n/a | n/a | n/a | n/a | n/a |
| P7 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | n320 | large | 0.0 | 0.013 | 0.007 | 0.980 | n/a | n/a | n/a | n/a | n/a |
| P7 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | h2 | large | 0.0 | 0.006 | 0.010 | 0.984 | n/a | n/a | n/a | n/a | n/a |
| P7 | h2 | depends |  | n/a | n/a | n/a | 0.749 | 0.000 | 0.000 | 0.251 | 0.000 |
| P7 | h5 | large | 0.0 | 0.006 | 0.011 | 0.983 | n/a | n/a | n/a | n/a | n/a |
| P7 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | h10 | large | 0.0 | 0.014 | 0.012 | 0.974 | n/a | n/a | n/a | n/a | n/a |
| P7 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | n20 | large | 0.0 | 0.001 | 0.086 | 0.912 | n/a | n/a | n/a | n/a | n/a |
| P8 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P8 | n40 | large | 0.0 | 0.005 | 0.032 | 0.963 | n/a | n/a | n/a | n/a | n/a |
| P8 | n40 | depends |  | n/a | n/a | n/a | 0.051 | 0.005 | 0.000 | 0.945 | 0.000 |
| P8 | n80 | large | 0.0 | 0.011 | 0.025 | 0.963 | n/a | n/a | n/a | n/a | n/a |
| P8 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.001 | 0.000 | 0.000 |
| P8 | n160 | large | 0.0 | 0.028 | 0.013 | 0.959 | n/a | n/a | n/a | n/a | n/a |
| P8 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | n320 | large | 0.0 | 0.029 | 0.018 | 0.954 | n/a | n/a | n/a | n/a | n/a |
| P8 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | h2 | large | 0.0 | 0.036 | 0.021 | 0.943 | n/a | n/a | n/a | n/a | n/a |
| P8 | h2 | depends |  | n/a | n/a | n/a | 0.876 | 0.000 | 0.000 | 0.123 | 0.000 |
| P8 | h5 | large | 0.0 | 0.037 | 0.024 | 0.939 | n/a | n/a | n/a | n/a | n/a |
| P8 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | h10 | large | 0.0 | 0.060 | 0.024 | 0.915 | n/a | n/a | n/a | n/a | n/a |
| P8 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P9 | n20 | depends | 0.2 | 0.008 | 0.040 | 0.952 | 0.008 | 0.004 | 0.036 | 0.952 | 0.000 |
| P9 | n40 | depends | 0.2 | 0.010 | 0.038 | 0.952 | 0.010 | 0.038 | 0.000 | 0.952 | 0.000 |
| P9 | n80 | depends | 0.2 | 0.004 | 0.043 | 0.954 | 0.004 | 0.043 | 0.000 | 0.954 | 0.000 |
| P9 | n160 | depends | 0.2 | 0.000 | 0.085 | 0.915 | 0.000 | 0.085 | 0.000 | 0.915 | 0.000 |
| P9 | n320 | depends | 0.2 | 0.000 | 0.095 | 0.905 | 0.000 | 0.095 | 0.000 | 0.905 | 0.000 |
| P9 | h2 | depends | 0.2 | 0.003 | 0.112 | 0.886 | 0.003 | 0.112 | 0.000 | 0.886 | 0.000 |
| P9 | h5 | depends | 0.2 | 0.003 | 0.121 | 0.876 | 0.003 | 0.121 | 0.000 | 0.876 | 0.000 |
| P9 | h10 | depends | 0.2 | 0.000 | 0.265 | 0.736 | 0.000 | 0.265 | 0.000 | 0.736 | 0.000 |
| P10 | n20 | depends | 0.2 | 0.004 | 0.032 | 0.965 | 0.004 | 0.004 | 0.028 | 0.965 | 0.000 |
| P10 | n40 | depends | 0.2 | 0.007 | 0.041 | 0.952 | 0.007 | 0.041 | 0.000 | 0.952 | 0.000 |
| P10 | n80 | depends | 0.2 | 0.004 | 0.045 | 0.952 | 0.004 | 0.045 | 0.000 | 0.952 | 0.000 |
| P10 | n160 | depends | 0.2 | 0.001 | 0.082 | 0.917 | 0.001 | 0.082 | 0.000 | 0.917 | 0.000 |
| P10 | n320 | depends | 0.2 | 0.001 | 0.090 | 0.909 | 0.001 | 0.090 | 0.000 | 0.909 | 0.000 |
| P10 | h2 | depends | 0.2 | 0.001 | 0.102 | 0.897 | 0.001 | 0.102 | 0.000 | 0.897 | 0.000 |
| P10 | h5 | depends | 0.2 | 0.002 | 0.115 | 0.883 | 0.002 | 0.115 | 0.000 | 0.883 | 0.000 |
| P10 | h10 | depends | 0.2 | 0.000 | 0.244 | 0.755 | 0.000 | 0.244 | 0.000 | 0.755 | 0.000 |
| P11 | n20 | depends | 0.0 | 0.000 | 0.768 | 0.232 | 0.000 | 0.011 | 0.743 | 0.232 | 0.015 |
| P11 | n40 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.036 | 0.953 | 0.000 | 0.011 |
| P11 | n80 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.060 | 0.939 | 0.000 | 0.002 |
| P11 | n160 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.086 | 0.913 | 0.000 | 0.001 |
| P11 | n320 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.091 | 0.909 | 0.000 | 0.000 |
| P11 | h2 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.118 | 0.879 | 0.000 | 0.003 |
| P11 | h5 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.117 | 0.879 | 0.000 | 0.003 |
| P11 | h10 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.238 | 0.761 | 0.000 | 0.000 |
| P12 | n20 | depends | 0.0 | 0.000 | 0.728 | 0.273 | 0.000 | 0.005 | 0.714 | 0.273 | 0.009 |
| P12 | n40 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.035 | 0.952 | 0.000 | 0.013 |
| P12 | n80 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.046 | 0.952 | 0.000 | 0.003 |
| P12 | n160 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.067 | 0.933 | 0.000 | 0.000 |
| P12 | n320 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.072 | 0.927 | 0.000 | 0.001 |
| P12 | h2 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.096 | 0.901 | 0.000 | 0.003 |
| P12 | h5 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.096 | 0.901 | 0.000 | 0.004 |
| P12 | h10 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.245 | 0.754 | 0.000 | 0.000 |
| P13 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.011 | 0.727 | 0.252 | 0.010 |
| P13 | n40 | depends |  | n/a | n/a | n/a | 0.087 | 0.007 | 0.000 | 0.905 | 0.000 |
| P13 | n80 | depends |  | n/a | n/a | n/a | 0.995 | 0.000 | 0.000 | 0.005 | 0.000 |
| P13 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | h2 | depends |  | n/a | n/a | n/a | 0.251 | 0.001 | 0.000 | 0.749 | 0.000 |
| P13 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | n20 | depends |  | n/a | n/a | n/a | 0.692 | 0.000 | 0.000 | 0.308 | 0.000 |
| T1 | n40 | depends |  | n/a | n/a | n/a | 0.998 | 0.000 | 0.000 | 0.002 | 0.000 |
| T1 | n80 | depends |  | n/a | n/a | n/a | 0.994 | 0.000 | 0.000 | 0.006 | 0.000 |
| T1 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n20 | depends |  | n/a | n/a | n/a | 0.600 | 0.000 | 0.000 | 0.400 | 0.000 |
| T2 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| T2 | n80 | depends |  | n/a | n/a | n/a | 0.994 | 0.000 | 0.000 | 0.006 | 0.000 |
| T2 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n20 | depends |  | n/a | n/a | n/a | 0.995 | 0.000 | 0.000 | 0.005 | 0.000 |
| T3 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n80 | depends |  | n/a | n/a | n/a | 0.999 | 0.000 | 0.000 | 0.002 | 0.000 |
| T3 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | n20 | depends |  | n/a | n/a | n/a | 0.595 | 0.000 | 0.000 | 0.405 | 0.000 |
| T4 | n40 | depends |  | n/a | n/a | n/a | 0.983 | 0.000 | 0.000 | 0.018 | 0.000 |
| T4 | n80 | depends |  | n/a | n/a | n/a | 0.993 | 0.000 | 0.000 | 0.007 | 0.000 |
| T4 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | n20 | depends |  | n/a | n/a | n/a | 0.355 | 0.000 | 0.000 | 0.645 | 0.000 |
| T5 | n40 | depends |  | n/a | n/a | n/a | 0.846 | 0.000 | 0.000 | 0.154 | 0.000 |
| T5 | n80 | depends |  | n/a | n/a | n/a | 0.989 | 0.000 | 0.000 | 0.011 | 0.000 |
| T5 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | h2 | depends |  | n/a | n/a | n/a | 0.909 | 0.000 | 0.000 | 0.091 | 0.000 |
| T5 | h5 | depends |  | n/a | n/a | n/a | 0.972 | 0.000 | 0.000 | 0.029 | 0.000 |
| T5 | h10 | depends |  | n/a | n/a | n/a | 0.994 | 0.000 | 0.000 | 0.006 | 0.000 |
| T6[0.3] | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T6[0.3] | n80 | depends |  | n/a | n/a | n/a | 0.789 | 0.000 | 0.000 | 0.210 | 0.000 |
| T6[0.5] | n20 | depends |  | n/a | n/a | n/a | 0.952 | 0.000 | 0.000 | 0.048 | 0.000 |
| T6[0.5] | n80 | depends |  | n/a | n/a | n/a | 0.057 | 0.000 | 0.001 | 0.943 | 0.000 |
| T6[0.7] | n20 | depends |  | n/a | n/a | n/a | 0.009 | 0.000 | 0.012 | 0.980 | 0.000 |
| T6[0.7] | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.021 | 0.977 | 0.003 |
| T6[0.85] | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.037 | 0.951 | 0.012 |
| T6[0.85] | n80 | depends |  | n/a | n/a | n/a | 0.005 | 0.000 | 0.022 | 0.971 | 0.002 |
| T6[0.95] | n20 | depends |  | n/a | n/a | n/a | 0.007 | 0.000 | 0.009 | 0.970 | 0.013 |
| T6[0.95] | n80 | depends |  | n/a | n/a | n/a | 0.015 | 0.000 | 0.007 | 0.975 | 0.002 |
| T6[1] | n20 | depends |  | n/a | n/a | n/a | 0.049 | 0.000 | 0.004 | 0.945 | 0.003 |
| T6[1] | n80 | depends |  | n/a | n/a | n/a | 0.032 | 0.000 | 0.006 | 0.960 | 0.003 |
| T6[1.1] | n20 | depends |  | n/a | n/a | n/a | 0.310 | 0.000 | 0.000 | 0.690 | 0.000 |
| T6[1.1] | n80 | depends |  | n/a | n/a | n/a | 0.091 | 0.000 | 0.001 | 0.907 | 0.001 |
| T6[1.25] | n20 | depends |  | n/a | n/a | n/a | 0.816 | 0.000 | 0.000 | 0.184 | 0.000 |
| T6[1.25] | n80 | depends |  | n/a | n/a | n/a | 0.284 | 0.000 | 0.000 | 0.716 | 0.000 |
| T7 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T8 | n20 | depends |  | n/a | n/a | n/a | 0.606 | 0.000 | 0.000 | 0.395 | 0.000 |
| T8 | n40 | depends |  | n/a | n/a | n/a | 0.941 | 0.000 | 0.000 | 0.059 | 0.000 |
| T8 | n80 | depends |  | n/a | n/a | n/a | 0.883 | 0.000 | 0.000 | 0.117 | 0.000 |
| T8 | n160 | depends |  | n/a | n/a | n/a | 0.968 | 0.000 | 0.000 | 0.032 | 0.000 |
| T8 | n320 | depends |  | n/a | n/a | n/a | 0.981 | 0.000 | 0.000 | 0.019 | 0.000 |

## In Words

- **Core cells:** 299 judged, 200 failing: P1 n20 carries, P1 n20 depends, P1 n80 carries, P1 n160 carries, P1 n160 depends, P1 n320 carries, P1 n320 depends, P1 h2 large, P1 h2 carries, P1 h5 large, P1 h5 carries, P1 h5 depends, P1 h10 large, P1 h10 carries, P1 h10 depends, P2 n20 carries, P2 n20 depends, P2 n160 carries, P2 n160 depends, P2 n320 large, P2 n320 carries, P2 n320 depends, P2 h2 large, P2 h2 carries, P2 h2 depends, P2 h5 large, P2 h5 carries, P2 h5 depends, P2 h10 large, P2 h10 carries, P2 h10 depends, P3 n20 carries, P3 n20 depends, P3 n160 carries, P3 n160 depends, P3 n320 large, P3 n320 carries, P3 n320 depends, P3 h2 large, P3 h2 carries, P3 h2 depends, P3 h5 large, P3 h5 carries, P3 h5 depends, P3 h10 large, P3 h10 carries, P3 h10 depends, P4 n20 carries, P4 n20 depends, P4 n80 carries, P4 n160 carries, P4 n160 depends, P4 n320 carries, P4 n320 depends, P4 h2 large, P4 h2 carries, P4 h5 carries, P4 h5 depends, P4 h10 large, P4 h10 carries, P4 h10 depends, P5 n20 carries, P5 n20 depends, P5 n160 carries, P5 n160 depends, P5 n320 carries, P5 n320 depends, P5 h2 carries, P5 h2 depends, P5 h5 large, P5 h5 carries, P5 h5 depends, P5 h10 large, P5 h10 carries, P5 h10 depends, P6 n20 carries, P6 n20 depends, P6 n160 carries, P6 n160 depends, P6 n320 large, P6 n320 carries, P6 n320 depends, P6 h2 large, P6 h2 carries, P6 h2 depends, P6 h5 large, P6 h5 carries, P6 h5 depends, P6 h10 large, P6 h10 carries, P6 h10 depends, P7 n20 carries, P7 n20 depends, P7 n160 carries, P7 n320 carries, P7 h2 carries, P7 h2 depends, P7 h5 carries, P7 h5 depends, P7 h10 carries, P7 h10 depends, P8 n20 carries, P8 n20 depends, P8 n160 carries, P8 n320 carries, P8 h2 large, P8 h2 carries, P8 h2 depends, P8 h5 large, P8 h5 carries, P8 h5 depends, P8 h10 large, P8 h10 carries, P8 h10 depends, P9 n20 carries, P9 n20 depends, P9 n40 depends, P9 n80 depends, P9 n160 carries, P9 n160 depends, P9 n320 carries, P9 n320 depends, P9 h2 carries, P9 h2 depends, P9 h5 large, P9 h5 carries, P9 h5 depends, P9 h10 large, P9 h10 carries, P9 h10 depends, P10 n20 carries, P10 n40 depends, P10 n80 depends, P10 n160 carries, P10 n160 depends, P10 n320 carries, P10 n320 depends, P10 h2 carries, P10 h2 depends, P10 h5 carries, P10 h5 depends, P10 h10 large, P10 h10 carries, P10 h10 depends, P11 n20 carries, P11 n20 depends, P11 n40 large, P11 n40 depends, P11 n80 large, P11 n80 depends, P11 n160 large, P11 n160 carries, P11 n160 depends, P11 n320 large, P11 n320 carries, P11 n320 depends, P11 h2 large, P11 h2 carries, P11 h2 depends, P11 h5 large, P11 h5 carries, P11 h5 depends, P11 h10 large, P11 h10 carries, P11 h10 depends, P12 n20 carries, P12 n40 large, P12 n80 large, P12 n80 depends, P12 n160 large, P12 n160 carries, P12 n160 depends, P12 n320 large, P12 n320 carries, P12 n320 depends, P12 h2 large, P12 h2 carries, P12 h2 depends, P12 h5 large, P12 h5 carries, P12 h5 depends, P12 h10 large, P12 h10 carries, P12 h10 depends, P13 n20 carries, P13 n40 large, P13 n40 carries, P13 n40 depends, P13 n160 carries, P13 n160 depends, P13 n320 carries, P13 n320 depends, P13 h2 carries, P13 h2 depends, P13 h5 large, P13 h5 carries, P13 h5 depends, P13 h10 large, P13 h10 carries, P13 h10 depends.
- **This version sets no multiplier.** What follows is what each row would have required under the generator as committed.
- **n20:** needs more than 1.5; the row goes to the PI.
- **n40:** multiplier 1.50, confirmed on seed 2 (lowest coverage 0.9480).
- **n80:** needs more than 1.5; the row goes to the PI.
- **n160:** needs more than 1.5; the row goes to the PI.
- **n320:** needs more than 1.5; the row goes to the PI.
- **h2:** needs more than 1.5; the row goes to the PI.
- **h5:** needs more than 1.5; the row goes to the PI.
- **h10:** needs more than 1.5; the row goes to the PI.
- **Stress cells under 92.5 percent:** 289, listed above.
- **G1:** yes. **G2:** yes.
- **Seeds:** master 20261006. **Commit:** 7c301015d6318fc1dc353fa83e2a0f4d3f22e80e (code as committed: yes).
