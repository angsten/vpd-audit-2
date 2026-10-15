# The Made-Up-Data Test of the Interval: Summary

Every number in this file comes from made-up experiments built on the pilot's own-batch searches. None is a result of the lead experiment.

## Checks With Exact Known Answers

- **G1** (attack-batch effects only): coverage 0.9500 over 100 experiments; expected 0.95; 0.00 Monte Carlo standard errors from it; V_PB is the classical s^2/K and nu is K - 1 in every experiment: yes. Passes: yes.
- **G2** (independent cell noise only): mean of V_PB over the true variance 3.0050 (expected 2.9375, Monte Carlo standard error 0.0539); coverage 1.0000. Passes: yes.

## The Guard on the Generator

800 comparisons of a plain mean with its true value at search-length rows. The largest is 4.03 Monte Carlo standard errors; the test stops at 5. Comparisons above 3.5: 7.

| Scenario | Experiments | Row | Statistic | Truth | Mean | Standard errors |
|---|---|---|---|---|---|---|
| T2 | first | n40 | carried_margin | 1.1202 | 1.0625 | -3.80 |
| T2 | first | n40 | carried_added | 1.3053 | 1.2381 | -3.83 |
| T2 | first | n80 | large | 5.0693 | 4.7438 | -4.03 |
| T2 | first | n80 | carried_margin | 5.5730 | 5.2316 | -3.99 |
| T2 | first | n80 | carried_added | 5.7581 | 5.4072 | -3.99 |
| T6[0.95] | first | n80 | large | 6.3077 | 5.9825 | -3.55 |
| T6[0.95] | first | n80 | carried_added | 6.9100 | 6.5624 | -3.59 |

## Each Core Cell: Pass or Fail

A cell is one core scenario, one row, and one signed reading. Coverage is of the unwidened interval. A cell under 93.5 percent, or with more than 3.25 percent of its intervals wholly on one side of its line, is rerun with 10,000 experiments and judged on the rerun alone.

| Scenario | Row | Reading | Line | Judged on | Coverage | Wholly above | Wholly below | Rerun | Multiplier needed | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | carries | 0.2 | 200 | 0.8900 | 0.0000 | 0.1100 | yes | 1.838 | FAIL |
| P1 | n20 | depends |  | 100 | 0.9400 | 0.0600 | 0.0000 | no | 1.060 | pass |
| P1 | n40 | large |  | 100 | 0.9800 | 0.0100 | 0.0100 | no | 0.769 | pass |
| P1 | n40 | carries | 0.2 | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.891 | pass |
| P1 | n40 | depends |  | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.739 | pass |
| P1 | n80 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.904 | pass |
| P1 | n80 | carries | 0.2 | 200 | 0.9400 | 0.0000 | 0.0600 | yes | 1.137 | FAIL |
| P1 | n80 | depends |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.999 | pass |
| P1 | n160 | large |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.816 | pass |
| P1 | n160 | carries | 0.2 | 200 | 0.9250 | 0.0000 | 0.0750 | yes | 1.447 | FAIL |
| P1 | n160 | depends |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.843 | pass |
| P1 | n320 | large |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.738 | pass |
| P1 | n320 | carries | 0.2 | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.412 | FAIL |
| P1 | n320 | depends |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.921 | pass |
| P1 | h2 | large |  | 100 | 0.9400 | 0.0600 | 0.0000 | no | 1.042 | pass |
| P1 | h2 | carries | 0.2 | 200 | 0.8700 | 0.0000 | 0.1300 | yes | 2.572 | FAIL |
| P1 | h2 | depends |  | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.611 | pass |
| P1 | h5 | large |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.011 | pass |
| P1 | h5 | carries | 0.2 | 200 | 0.8750 | 0.0000 | 0.1250 | yes | 2.719 | FAIL |
| P1 | h5 | depends |  | 200 | 0.8750 | 0.0000 | 0.1250 | yes | 2.339 | FAIL |
| P1 | h10 | large |  | 200 | 0.7850 | 0.0000 | 0.2150 | yes | 2.303 | FAIL |
| P1 | h10 | carries | 0.2 | 200 | 0.8000 | 0.0000 | 0.2000 | yes | 2.566 | FAIL |
| P1 | h10 | depends |  | 200 | 0.8000 | 0.0000 | 0.2000 | yes | 2.389 | FAIL |
| P2 | n20 | carries |  | 200 | 0.9150 | 0.0000 | 0.0850 | yes | 1.307 | FAIL |
| P2 | n20 | depends |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.160 | FAIL |
| P2 | n40 | large |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.847 | pass |
| P2 | n40 | carries |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.003 | pass |
| P2 | n40 | depends |  | 100 | 0.9500 | 0.0100 | 0.0400 | no | 0.990 | pass |
| P2 | n80 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.989 | pass |
| P2 | n80 | carries |  | 200 | 0.9500 | 0.0000 | 0.0500 | yes | 0.973 | pass |
| P2 | n80 | depends |  | 200 | 0.9500 | 0.0000 | 0.0500 | yes | 0.982 | pass |
| P2 | n160 | large |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.843 | pass |
| P2 | n160 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.074 | pass |
| P2 | n160 | depends |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.067 | pass |
| P2 | n320 | large |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.896 | pass |
| P2 | n320 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.091 | pass |
| P2 | n320 | depends |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.087 | pass |
| P2 | h2 | large |  | 200 | 0.9400 | 0.0000 | 0.0600 | yes | 1.041 | pass |
| P2 | h2 | carries |  | 200 | 0.9050 | 0.0050 | 0.0900 | yes | 1.981 | FAIL |
| P2 | h2 | depends |  | 200 | 0.9050 | 0.0050 | 0.0900 | yes | 1.981 | FAIL |
| P2 | h5 | large |  | 200 | 0.9000 | 0.0100 | 0.0900 | yes | 1.622 | FAIL |
| P2 | h5 | carries |  | 200 | 0.9000 | 0.0100 | 0.0900 | yes | 2.105 | FAIL |
| P2 | h5 | depends |  | 200 | 0.9050 | 0.0050 | 0.0900 | yes | 2.109 | FAIL |
| P2 | h10 | large |  | 200 | 0.8050 | 0.0000 | 0.1950 | yes | 2.165 | FAIL |
| P2 | h10 | carries |  | 200 | 0.7950 | 0.0000 | 0.2050 | yes | 2.323 | FAIL |
| P2 | h10 | depends |  | 200 | 0.7900 | 0.0000 | 0.2100 | yes | 2.323 | FAIL |
| P3 | n20 | carries |  | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.462 | FAIL |
| P3 | n20 | depends |  | 200 | 0.9150 | 0.0000 | 0.0850 | yes | 1.494 | FAIL |
| P3 | n40 | large |  | 200 | 0.9450 | 0.0000 | 0.0550 | yes | 1.015 | pass |
| P3 | n40 | carries |  | 100 | 0.9500 | 0.0100 | 0.0400 | no | 1.001 | pass |
| P3 | n40 | depends |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.022 | pass |
| P3 | n80 | large |  | 200 | 0.9500 | 0.0050 | 0.0450 | yes | 0.994 | pass |
| P3 | n80 | carries |  | 200 | 0.9600 | 0.0050 | 0.0350 | yes | 0.913 | pass |
| P3 | n80 | depends |  | 200 | 0.9650 | 0.0000 | 0.0350 | yes | 0.901 | pass |
| P3 | n160 | large |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.179 | FAIL |
| P3 | n160 | carries |  | 200 | 0.8950 | 0.0000 | 0.1050 | yes | 1.418 | FAIL |
| P3 | n160 | depends |  | 200 | 0.8950 | 0.0000 | 0.1050 | yes | 1.419 | FAIL |
| P3 | n320 | large |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.213 | pass |
| P3 | n320 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.245 | pass |
| P3 | n320 | depends |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.249 | pass |
| P3 | h2 | large |  | 200 | 0.8550 | 0.0050 | 0.1400 | yes | 1.598 | FAIL |
| P3 | h2 | carries |  | 200 | 0.8550 | 0.0050 | 0.1400 | yes | 2.183 | FAIL |
| P3 | h2 | depends |  | 200 | 0.8600 | 0.0000 | 0.1400 | yes | 2.239 | FAIL |
| P3 | h5 | large |  | 200 | 0.8600 | 0.0050 | 0.1350 | yes | 2.105 | FAIL |
| P3 | h5 | carries |  | 200 | 0.8650 | 0.0000 | 0.1350 | yes | 2.345 | FAIL |
| P3 | h5 | depends |  | 200 | 0.8650 | 0.0000 | 0.1350 | yes | 2.364 | FAIL |
| P3 | h10 | large |  | 200 | 0.7300 | 0.0000 | 0.2700 | yes | 2.718 | FAIL |
| P3 | h10 | carries |  | 200 | 0.7300 | 0.0000 | 0.2700 | yes | 2.828 | FAIL |
| P3 | h10 | depends |  | 200 | 0.7300 | 0.0000 | 0.2700 | yes | 2.842 | FAIL |
| P4 | n20 | carries | 0.2 | 200 | 0.9000 | 0.0050 | 0.0950 | yes | 1.626 | FAIL |
| P4 | n20 | depends |  | 100 | 0.9500 | 0.0500 | 0.0000 | no | 0.959 | pass |
| P4 | n40 | large |  | 100 | 0.9500 | 0.0300 | 0.0200 | no | 0.905 | pass |
| P4 | n40 | carries | 0.2 | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.877 | pass |
| P4 | n40 | depends |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.951 | pass |
| P4 | n80 | large |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.075 | pass |
| P4 | n80 | carries | 0.2 | 200 | 0.9350 | 0.0000 | 0.0650 | yes | 1.229 | FAIL |
| P4 | n80 | depends |  | 100 | 0.9500 | 0.0100 | 0.0400 | no | 0.935 | pass |
| P4 | n160 | large |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.910 | pass |
| P4 | n160 | carries | 0.2 | 200 | 0.9250 | 0.0000 | 0.0750 | yes | 1.578 | FAIL |
| P4 | n160 | depends |  | 200 | 0.9250 | 0.0000 | 0.0750 | yes | 1.372 | pass |
| P4 | n320 | large |  | 200 | 0.9150 | 0.0050 | 0.0800 | yes | 1.123 | FAIL |
| P4 | n320 | carries | 0.2 | 200 | 0.9050 | 0.0000 | 0.0950 | yes | 1.656 | FAIL |
| P4 | n320 | depends |  | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.546 | FAIL |
| P4 | h2 | large |  | 100 | 0.9500 | 0.0400 | 0.0100 | no | 0.873 | pass |
| P4 | h2 | carries | 0.2 | 200 | 0.8650 | 0.0000 | 0.1350 | yes | 2.280 | FAIL |
| P4 | h2 | depends |  | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.648 | pass |
| P4 | h5 | large |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.909 | pass |
| P4 | h5 | carries | 0.2 | 200 | 0.8650 | 0.0000 | 0.1350 | yes | 2.480 | FAIL |
| P4 | h5 | depends |  | 200 | 0.8600 | 0.0000 | 0.1400 | yes | 2.078 | FAIL |
| P4 | h10 | large |  | 200 | 0.7600 | 0.0000 | 0.2400 | yes | 2.154 | FAIL |
| P4 | h10 | carries | 0.2 | 200 | 0.7800 | 0.0000 | 0.2200 | yes | 2.808 | FAIL |
| P4 | h10 | depends |  | 200 | 0.7850 | 0.0000 | 0.2150 | yes | 2.557 | FAIL |
| P5 | n20 | carries |  | 200 | 0.9300 | 0.0000 | 0.0700 | yes | 1.306 | pass |
| P5 | n20 | depends |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.228 | FAIL |
| P5 | n40 | large |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.900 | pass |
| P5 | n40 | carries |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.730 | pass |
| P5 | n40 | depends |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.714 | pass |
| P5 | n80 | large |  | 200 | 0.9450 | 0.0100 | 0.0450 | yes | 1.031 | pass |
| P5 | n80 | carries |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.892 | pass |
| P5 | n80 | depends |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.885 | pass |
| P5 | n160 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.936 | pass |
| P5 | n160 | carries |  | 200 | 0.9200 | 0.0050 | 0.0750 | yes | 1.215 | FAIL |
| P5 | n160 | depends |  | 200 | 0.9250 | 0.0050 | 0.0700 | yes | 1.198 | pass |
| P5 | n320 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.944 | pass |
| P5 | n320 | carries |  | 200 | 0.9150 | 0.0050 | 0.0800 | yes | 1.378 | FAIL |
| P5 | n320 | depends |  | 200 | 0.9150 | 0.0050 | 0.0800 | yes | 1.373 | FAIL |
| P5 | h2 | large |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.019 | pass |
| P5 | h2 | carries |  | 200 | 0.8800 | 0.0100 | 0.1100 | yes | 1.871 | FAIL |
| P5 | h2 | depends |  | 200 | 0.8900 | 0.0000 | 0.1100 | yes | 1.842 | FAIL |
| P5 | h5 | large |  | 200 | 0.8900 | 0.0050 | 0.1050 | yes | 1.620 | FAIL |
| P5 | h5 | carries |  | 200 | 0.8850 | 0.0050 | 0.1100 | yes | 2.001 | FAIL |
| P5 | h5 | depends |  | 200 | 0.8900 | 0.0000 | 0.1100 | yes | 1.963 | FAIL |
| P5 | h10 | large |  | 200 | 0.7500 | 0.0000 | 0.2500 | yes | 2.863 | FAIL |
| P5 | h10 | carries |  | 200 | 0.7500 | 0.0000 | 0.2500 | yes | 2.932 | FAIL |
| P5 | h10 | depends |  | 200 | 0.7500 | 0.0000 | 0.2500 | yes | 2.930 | FAIL |
| P6 | n20 | carries |  | 200 | 0.9050 | 0.0050 | 0.0900 | yes | 1.338 | FAIL |
| P6 | n20 | depends |  | 200 | 0.9050 | 0.0000 | 0.0950 | yes | 1.375 | FAIL |
| P6 | n40 | large |  | 200 | 0.9600 | 0.0000 | 0.0400 | yes | 0.944 | pass |
| P6 | n40 | carries |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.966 | pass |
| P6 | n40 | depends |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.990 | pass |
| P6 | n80 | large |  | 200 | 0.9450 | 0.0050 | 0.0500 | yes | 1.012 | pass |
| P6 | n80 | carries |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.948 | pass |
| P6 | n80 | depends |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.942 | pass |
| P6 | n160 | large |  | 200 | 0.9400 | 0.0050 | 0.0550 | yes | 1.143 | pass |
| P6 | n160 | carries |  | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.264 | FAIL |
| P6 | n160 | depends |  | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.263 | FAIL |
| P6 | n320 | large |  | 200 | 0.9400 | 0.0050 | 0.0550 | yes | 1.095 | pass |
| P6 | n320 | carries |  | 200 | 0.9150 | 0.0000 | 0.0850 | yes | 1.403 | FAIL |
| P6 | n320 | depends |  | 200 | 0.9150 | 0.0000 | 0.0850 | yes | 1.403 | FAIL |
| P6 | h2 | large |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.104 | pass |
| P6 | h2 | carries |  | 200 | 0.8950 | 0.0100 | 0.0950 | yes | 2.015 | FAIL |
| P6 | h2 | depends |  | 200 | 0.9050 | 0.0000 | 0.0950 | yes | 2.085 | FAIL |
| P6 | h5 | large |  | 200 | 0.8900 | 0.0100 | 0.1000 | yes | 1.938 | FAIL |
| P6 | h5 | carries |  | 200 | 0.8900 | 0.0100 | 0.1000 | yes | 2.097 | FAIL |
| P6 | h5 | depends |  | 200 | 0.8900 | 0.0100 | 0.1000 | yes | 2.118 | FAIL |
| P6 | h10 | large |  | 200 | 0.7550 | 0.0000 | 0.2450 | yes | 2.543 | FAIL |
| P6 | h10 | carries |  | 200 | 0.7550 | 0.0000 | 0.2450 | yes | 2.604 | FAIL |
| P6 | h10 | depends |  | 200 | 0.7550 | 0.0000 | 0.2450 | yes | 2.613 | FAIL |
| P7 | n20 | carries |  | 200 | 0.9000 | 0.0050 | 0.0950 | yes | 1.334 | FAIL |
| P7 | n20 | depends |  | 200 | 0.8950 | 0.0000 | 0.1050 | yes | 1.353 | FAIL |
| P7 | n40 | large | 0.0 | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.754 | pass |
| P7 | n40 | carries |  | 100 | 0.9700 | 0.0100 | 0.0200 | no | 0.815 | pass |
| P7 | n40 | depends |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.876 | pass |
| P7 | n80 | large | 0.0 | 200 | 0.9650 | 0.0100 | 0.0250 | yes | 0.801 | pass |
| P7 | n80 | carries |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.830 | pass |
| P7 | n80 | depends |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.802 | pass |
| P7 | n160 | large | 0.0 | 100 | 0.9700 | 0.0100 | 0.0200 | no | 0.908 | pass |
| P7 | n160 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.028 | pass |
| P7 | n160 | depends |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.828 | pass |
| P7 | n320 | large | 0.0 | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.977 | pass |
| P7 | n320 | carries |  | 200 | 0.9250 | 0.0000 | 0.0750 | yes | 1.169 | pass |
| P7 | n320 | depends |  | 100 | 0.9800 | 0.0100 | 0.0100 | no | 0.806 | pass |
| P7 | h2 | large | 0.0 | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.835 | pass |
| P7 | h2 | carries |  | 200 | 0.8800 | 0.0000 | 0.1200 | yes | 2.223 | FAIL |
| P7 | h2 | depends |  | 200 | 0.8850 | 0.0000 | 0.1150 | yes | 1.977 | FAIL |
| P7 | h5 | large | 0.0 | 100 | 0.9900 | 0.0000 | 0.0100 | no | 0.779 | pass |
| P7 | h5 | carries |  | 200 | 0.8800 | 0.0000 | 0.1200 | yes | 2.101 | FAIL |
| P7 | h5 | depends |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.580 | FAIL |
| P7 | h10 | large | 0.0 | 100 | 0.9600 | 0.0300 | 0.0100 | no | 0.939 | pass |
| P7 | h10 | carries |  | 200 | 0.7400 | 0.0000 | 0.2600 | yes | 2.659 | FAIL |
| P7 | h10 | depends |  | 200 | 0.7750 | 0.0000 | 0.2250 | yes | 1.704 | FAIL |
| P8 | n20 | carries |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.350 | FAIL |
| P8 | n20 | depends |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.425 | FAIL |
| P8 | n40 | large | 0.0 | 100 | 0.9600 | 0.0200 | 0.0200 | no | 0.827 | pass |
| P8 | n40 | carries |  | 100 | 1.0000 | 0.0000 | 0.0000 | no | 0.770 | pass |
| P8 | n40 | depends |  | 100 | 0.9800 | 0.0100 | 0.0100 | no | 0.795 | pass |
| P8 | n80 | large | 0.0 | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.802 | pass |
| P8 | n80 | carries |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.771 | pass |
| P8 | n80 | depends |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.924 | pass |
| P8 | n160 | large | 0.0 | 200 | 0.9800 | 0.0150 | 0.0050 | yes | 0.881 | pass |
| P8 | n160 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.062 | pass |
| P8 | n160 | depends |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.803 | pass |
| P8 | n320 | large | 0.0 | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.933 | pass |
| P8 | n320 | carries |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.816 | pass |
| P8 | n320 | depends |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.704 | pass |
| P8 | h2 | large | 0.0 | 200 | 0.8950 | 0.0750 | 0.0300 | yes | 1.157 | FAIL |
| P8 | h2 | carries |  | 200 | 0.8950 | 0.0000 | 0.1050 | yes | 2.093 | FAIL |
| P8 | h2 | depends |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.157 | pass |
| P8 | h5 | large | 0.0 | 200 | 0.9100 | 0.0650 | 0.0250 | yes | 1.098 | FAIL |
| P8 | h5 | carries |  | 200 | 0.8900 | 0.0000 | 0.1100 | yes | 2.113 | FAIL |
| P8 | h5 | depends |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.597 | FAIL |
| P8 | h10 | large | 0.0 | 200 | 0.9250 | 0.0600 | 0.0150 | yes | 1.139 | FAIL |
| P8 | h10 | carries |  | 200 | 0.7700 | 0.0000 | 0.2300 | yes | 2.701 | FAIL |
| P8 | h10 | depends |  | 200 | 0.8450 | 0.0000 | 0.1550 | yes | 1.815 | FAIL |
| P9 | n20 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.011 | pass |
| P9 | n20 | depends | 0.2 | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.854 | pass |
| P9 | n40 | large |  | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.706 | pass |
| P9 | n40 | carries |  | 100 | 1.0000 | 0.0000 | 0.0000 | no | 0.713 | pass |
| P9 | n40 | depends | 0.2 | 100 | 0.9800 | 0.0000 | 0.0200 | no | 0.859 | pass |
| P9 | n80 | large |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.806 | pass |
| P9 | n80 | carries |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.026 | pass |
| P9 | n80 | depends | 0.2 | 200 | 0.9700 | 0.0050 | 0.0250 | yes | 0.903 | pass |
| P9 | n160 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.965 | pass |
| P9 | n160 | carries |  | 200 | 0.9200 | 0.0050 | 0.0750 | yes | 1.269 | FAIL |
| P9 | n160 | depends | 0.2 | 200 | 0.9200 | 0.0050 | 0.0750 | yes | 1.323 | FAIL |
| P9 | n320 | large |  | 200 | 0.9350 | 0.0050 | 0.0600 | yes | 1.184 | pass |
| P9 | n320 | carries |  | 200 | 0.8950 | 0.0050 | 0.1000 | yes | 1.222 | FAIL |
| P9 | n320 | depends | 0.2 | 200 | 0.9000 | 0.0050 | 0.0950 | yes | 1.327 | FAIL |
| P9 | h2 | large |  | 100 | 0.9800 | 0.0200 | 0.0000 | no | 0.902 | pass |
| P9 | h2 | carries |  | 200 | 0.8800 | 0.0100 | 0.1100 | yes | 1.960 | FAIL |
| P9 | h2 | depends | 0.2 | 200 | 0.8850 | 0.0100 | 0.1050 | yes | 1.517 | FAIL |
| P9 | h5 | large |  | 200 | 0.8850 | 0.0100 | 0.1050 | yes | 1.346 | FAIL |
| P9 | h5 | carries |  | 200 | 0.8700 | 0.0150 | 0.1150 | yes | 2.157 | FAIL |
| P9 | h5 | depends | 0.2 | 200 | 0.8650 | 0.0150 | 0.1200 | yes | 2.292 | FAIL |
| P9 | h10 | large |  | 200 | 0.7450 | 0.0000 | 0.2550 | yes | 2.395 | FAIL |
| P9 | h10 | carries |  | 200 | 0.7400 | 0.0000 | 0.2600 | yes | 2.745 | FAIL |
| P9 | h10 | depends | 0.2 | 200 | 0.7450 | 0.0000 | 0.2550 | yes | 2.804 | FAIL |
| P10 | n20 | carries |  | 200 | 0.9300 | 0.0050 | 0.0650 | yes | 1.151 | pass |
| P10 | n20 | depends | 0.2 | 200 | 0.9500 | 0.0000 | 0.0500 | yes | 1.038 | FAIL |
| P10 | n40 | large |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.807 | pass |
| P10 | n40 | carries |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.026 | pass |
| P10 | n40 | depends | 0.2 | 200 | 0.9550 | 0.0050 | 0.0400 | yes | 1.004 | FAIL |
| P10 | n80 | large |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.863 | pass |
| P10 | n80 | carries |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.916 | pass |
| P10 | n80 | depends | 0.2 | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.949 | pass |
| P10 | n160 | large |  | 100 | 0.9700 | 0.0100 | 0.0200 | no | 0.860 | pass |
| P10 | n160 | carries |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.323 | FAIL |
| P10 | n160 | depends | 0.2 | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.397 | FAIL |
| P10 | n320 | large |  | 200 | 0.9300 | 0.0000 | 0.0700 | yes | 1.146 | pass |
| P10 | n320 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.122 | pass |
| P10 | n320 | depends | 0.2 | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.339 | FAIL |
| P10 | h2 | large |  | 200 | 0.9300 | 0.0600 | 0.0100 | yes | 1.167 | pass |
| P10 | h2 | carries |  | 200 | 0.8750 | 0.0000 | 0.1250 | yes | 2.317 | FAIL |
| P10 | h2 | depends | 0.2 | 200 | 0.8900 | 0.0000 | 0.1100 | yes | 1.810 | FAIL |
| P10 | h5 | large |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.933 | pass |
| P10 | h5 | carries |  | 200 | 0.8800 | 0.0000 | 0.1200 | yes | 2.374 | FAIL |
| P10 | h5 | depends | 0.2 | 200 | 0.8850 | 0.0000 | 0.1150 | yes | 2.490 | FAIL |
| P10 | h10 | large |  | 200 | 0.7850 | 0.0000 | 0.2150 | yes | 2.091 | FAIL |
| P10 | h10 | carries |  | 200 | 0.7600 | 0.0000 | 0.2400 | yes | 2.381 | FAIL |
| P10 | h10 | depends | 0.2 | 200 | 0.7650 | 0.0000 | 0.2350 | yes | 2.419 | FAIL |
| P11 | n20 | carries |  | 100 | 0.9600 | 0.0000 | 0.0400 | no | 0.922 | pass |
| P11 | n20 | depends | 0.0 | 200 | 0.9450 | 0.0250 | 0.0300 | yes | 1.038 | pass |
| P11 | n40 | large |  | 200 | 0.9050 | 0.0950 | 0.0000 | yes | 1.230 | FAIL |
| P11 | n40 | carries |  | 100 | 0.9700 | 0.0100 | 0.0200 | no | 0.844 | pass |
| P11 | n40 | depends | 0.0 | 200 | 0.9500 | 0.0400 | 0.0100 | yes | 1.002 | FAIL |
| P11 | n80 | large |  | 200 | 0.8850 | 0.1150 | 0.0000 | yes | 1.362 | FAIL |
| P11 | n80 | carries |  | 100 | 0.9500 | 0.0100 | 0.0400 | no | 0.943 | pass |
| P11 | n80 | depends | 0.0 | 200 | 0.9500 | 0.0500 | 0.0000 | yes | 1.036 | FAIL |
| P11 | n160 | large |  | 200 | 0.8700 | 0.1250 | 0.0050 | yes | 1.843 | FAIL |
| P11 | n160 | carries |  | 200 | 0.9100 | 0.0000 | 0.0900 | yes | 1.290 | FAIL |
| P11 | n160 | depends | 0.0 | 200 | 0.8850 | 0.1150 | 0.0000 | yes | 1.588 | FAIL |
| P11 | n320 | large |  | 200 | 0.8700 | 0.1250 | 0.0050 | yes | 1.800 | FAIL |
| P11 | n320 | carries |  | 200 | 0.8850 | 0.0000 | 0.1150 | yes | 1.220 | FAIL |
| P11 | n320 | depends | 0.0 | 200 | 0.8900 | 0.1100 | 0.0000 | yes | 1.504 | FAIL |
| P11 | h2 | large |  | 200 | 0.8500 | 0.1500 | 0.0000 | yes | 2.037 | FAIL |
| P11 | h2 | carries |  | 200 | 0.8550 | 0.0100 | 0.1350 | yes | 2.005 | FAIL |
| P11 | h2 | depends | 0.0 | 200 | 0.8650 | 0.1250 | 0.0100 | yes | 2.384 | FAIL |
| P11 | h5 | large |  | 200 | 0.8500 | 0.1500 | 0.0000 | yes | 2.043 | FAIL |
| P11 | h5 | carries |  | 200 | 0.8700 | 0.0100 | 0.1200 | yes | 2.083 | FAIL |
| P11 | h5 | depends | 0.0 | 200 | 0.8700 | 0.1250 | 0.0050 | yes | 2.341 | FAIL |
| P11 | h10 | large |  | 200 | 0.6800 | 0.3200 | 0.0000 | yes | 2.855 | FAIL |
| P11 | h10 | carries |  | 200 | 0.7150 | 0.0000 | 0.2850 | yes | 2.461 | FAIL |
| P11 | h10 | depends | 0.0 | 200 | 0.7150 | 0.2850 | 0.0000 | yes | 2.753 | FAIL |
| P12 | n20 | carries |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.396 | FAIL |
| P12 | n20 | depends | 0.0 | 200 | 0.9650 | 0.0250 | 0.0100 | yes | 0.923 | pass |
| P12 | n40 | large |  | 200 | 0.9200 | 0.0800 | 0.0000 | yes | 1.356 | FAIL |
| P12 | n40 | carries |  | 100 | 0.9700 | 0.0000 | 0.0300 | no | 0.972 | pass |
| P12 | n40 | depends | 0.0 | 200 | 0.9250 | 0.0550 | 0.0200 | yes | 1.107 | FAIL |
| P12 | n80 | large |  | 200 | 0.8950 | 0.1050 | 0.0000 | yes | 1.604 | FAIL |
| P12 | n80 | carries |  | 200 | 0.9800 | 0.0000 | 0.0200 | yes | 0.897 | pass |
| P12 | n80 | depends | 0.0 | 200 | 0.9200 | 0.0700 | 0.0100 | yes | 1.156 | FAIL |
| P12 | n160 | large |  | 200 | 0.9550 | 0.0450 | 0.0000 | yes | 0.926 | pass |
| P12 | n160 | carries |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.546 | FAIL |
| P12 | n160 | depends | 0.0 | 200 | 0.9050 | 0.0950 | 0.0000 | yes | 1.481 | FAIL |
| P12 | n320 | large |  | 200 | 0.9500 | 0.0500 | 0.0000 | yes | 0.994 | pass |
| P12 | n320 | carries |  | 200 | 0.8750 | 0.0000 | 0.1250 | yes | 1.496 | FAIL |
| P12 | n320 | depends | 0.0 | 200 | 0.8850 | 0.1100 | 0.0050 | yes | 1.572 | FAIL |
| P12 | h2 | large |  | 100 | 0.9500 | 0.0500 | 0.0000 | no | 0.936 | pass |
| P12 | h2 | carries |  | 200 | 0.8700 | 0.0000 | 0.1300 | yes | 2.386 | FAIL |
| P12 | h2 | depends | 0.0 | 200 | 0.8650 | 0.1350 | 0.0000 | yes | 2.724 | FAIL |
| P12 | h5 | large |  | 100 | 0.9500 | 0.0500 | 0.0000 | no | 0.971 | pass |
| P12 | h5 | carries |  | 200 | 0.8750 | 0.0000 | 0.1250 | yes | 2.591 | FAIL |
| P12 | h5 | depends | 0.0 | 200 | 0.8650 | 0.1350 | 0.0000 | yes | 2.698 | FAIL |
| P12 | h10 | large |  | 200 | 0.8750 | 0.1250 | 0.0000 | yes | 1.805 | FAIL |
| P12 | h10 | carries |  | 200 | 0.7700 | 0.0000 | 0.2300 | yes | 2.722 | FAIL |
| P12 | h10 | depends | 0.0 | 200 | 0.7650 | 0.2350 | 0.0000 | yes | 2.749 | FAIL |
| P13 | n20 | carries |  | 200 | 0.8750 | 0.0100 | 0.1150 | yes | 1.578 | FAIL |
| P13 | n20 | depends |  | 100 | 0.9700 | 0.0200 | 0.0100 | no | 0.832 | pass |
| P13 | n40 | large |  | 200 | 0.9050 | 0.0000 | 0.0950 | yes | 1.333 | FAIL |
| P13 | n40 | carries |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.192 | FAIL |
| P13 | n40 | depends |  | 200 | 0.9000 | 0.0000 | 0.1000 | yes | 1.223 | FAIL |
| P13 | n80 | large |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.023 | pass |
| P13 | n80 | carries |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.875 | pass |
| P13 | n80 | depends |  | 100 | 0.9600 | 0.0100 | 0.0300 | no | 0.869 | pass |
| P13 | n160 | large |  | 100 | 0.9400 | 0.0100 | 0.0500 | no | 1.019 | pass |
| P13 | n160 | carries |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.537 | FAIL |
| P13 | n160 | depends |  | 200 | 0.9200 | 0.0000 | 0.0800 | yes | 1.536 | FAIL |
| P13 | n320 | large |  | 200 | 0.9000 | 0.0050 | 0.0950 | yes | 1.360 | FAIL |
| P13 | n320 | carries |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.137 | pass |
| P13 | n320 | depends |  | 100 | 0.9400 | 0.0000 | 0.0600 | no | 1.140 | pass |
| P13 | h2 | large |  | 100 | 0.9600 | 0.0300 | 0.0100 | no | 0.945 | pass |
| P13 | h2 | carries |  | 200 | 0.8600 | 0.0050 | 0.1350 | yes | 2.165 | FAIL |
| P13 | h2 | depends |  | 100 | 0.9500 | 0.0000 | 0.0500 | no | 0.988 | pass |
| P13 | h5 | large |  | 200 | 0.8550 | 0.0100 | 0.1350 | yes | 1.743 | FAIL |
| P13 | h5 | carries |  | 200 | 0.8550 | 0.0100 | 0.1350 | yes | 2.051 | FAIL |
| P13 | h5 | depends |  | 200 | 0.8600 | 0.0050 | 0.1350 | yes | 2.070 | FAIL |
| P13 | h10 | large |  | 200 | 0.7900 | 0.0000 | 0.2100 | yes | 2.315 | FAIL |
| P13 | h10 | carries |  | 200 | 0.7950 | 0.0000 | 0.2050 | yes | 2.189 | FAIL |
| P13 | h10 | depends |  | 200 | 0.7900 | 0.0000 | 0.2100 | yes | 2.192 | FAIL |

## Each Row's Multiplier

| Row | Failing core cells | Largest multiplier needed | Multiplier | Confirmation | Goes to the PI |
|---|---|---|---|---|---|
| n20 | P1 carries, P2 carries, P2 depends, P3 carries, P3 depends, P4 carries, P5 depends, P6 carries, P6 depends, P7 carries, P7 depends, P8 carries, P8 depends, P10 depends, P12 carries, P13 carries | 1.838 | 1.85 | not needed | yes |
| n40 | P10 depends, P11 large, P11 depends, P12 large, P12 depends, P13 large, P13 carries, P13 depends | 1.356 | 1.40 | seed 2 at 1.40: passed (lowest coverage 0.9650) | no |
| n80 | P1 carries, P4 carries, P11 large, P11 depends, P12 large, P12 depends | 1.604 | 1.65 | not needed | yes |
| n160 | P1 carries, P3 large, P3 carries, P3 depends, P4 carries, P5 carries, P6 carries, P6 depends, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 carries, P12 depends, P13 carries, P13 depends | 1.843 | 1.85 | not needed | yes |
| n320 | P1 carries, P4 large, P4 carries, P4 depends, P5 carries, P5 depends, P6 carries, P6 depends, P9 carries, P9 depends, P10 depends, P11 large, P11 carries, P11 depends, P12 carries, P12 depends, P13 large | 1.800 | 1.85 | not needed | yes |
| h2 | P1 carries, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 carries, P5 carries, P5 depends, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 carries, P12 depends, P13 carries | 2.724 | 2.75 | not needed | yes |
| h5 | P1 carries, P1 depends, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 carries, P4 depends, P5 large, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P8 depends, P9 large, P9 carries, P9 depends, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 carries, P12 depends, P13 large, P13 carries, P13 depends | 2.719 | 2.75 | not needed | yes |
| h10 | P1 large, P1 carries, P1 depends, P2 large, P2 carries, P2 depends, P3 large, P3 carries, P3 depends, P4 large, P4 carries, P4 depends, P5 large, P5 carries, P5 depends, P6 large, P6 carries, P6 depends, P7 carries, P7 depends, P8 large, P8 carries, P8 depends, P9 large, P9 carries, P9 depends, P10 large, P10 carries, P10 depends, P11 large, P11 carries, P11 depends, P12 large, P12 carries, P12 depends, P13 large, P13 carries, P13 depends | 2.932 | 2.95 | not needed | yes |

## Stress Cells Under 92.5 Percent (Stated, Not Repaired)

| Scenario | Row | Statistic | Coverage | Experiments |
|---|---|---|---|---|
| T1 | n20 | carries | 0.8700 | 100 |
| T1 | n20 | carried_added | 0.8800 | 100 |
| T1 | n20 | pooled_retention | 0.7600 | 100 |
| T1 | n40 | large | 0.9200 | 100 |
| T1 | n40 | carries | 0.9200 | 100 |
| T1 | n40 | own_margin | 0.9200 | 100 |
| T1 | n40 | pooled_retention | 0.7700 | 100 |
| T1 | n80 | own_margin | 0.9000 | 100 |
| T1 | n80 | pooled_retention | 0.7700 | 100 |
| T1 | n160 | carries | 0.9100 | 100 |
| T1 | n160 | depends | 0.9100 | 100 |
| T1 | n160 | kappa | 0.8400 | 100 |
| T1 | n160 | pooled_retention | 0.7900 | 100 |
| T1 | n320 | large | 0.9100 | 100 |
| T1 | n320 | carries | 0.9200 | 100 |
| T1 | n320 | depends | 0.9200 | 100 |
| T1 | n320 | carried_margin | 0.9100 | 100 |
| T1 | n320 | kappa | 0.8600 | 100 |
| T1 | n320 | carried_added | 0.9000 | 100 |
| T1 | n320 | pooled_retention | 0.7800 | 100 |
| T1 | h2 | large | 0.9200 | 100 |
| T1 | h2 | carries | 0.8000 | 100 |
| T1 | h2 | depends | 0.8000 | 100 |
| T1 | h2 | carried_margin | 0.7900 | 100 |
| T1 | h2 | own_margin | 0.9200 | 100 |
| T1 | h2 | kappa | 0.7900 | 100 |
| T1 | h2 | carried_added | 0.7800 | 100 |
| T1 | h2 | pooled_retention | 0.7700 | 100 |
| T1 | h5 | large | 0.8200 | 100 |
| T1 | h5 | carries | 0.7900 | 100 |
| T1 | h5 | depends | 0.7900 | 100 |
| T1 | h5 | carried_margin | 0.7900 | 100 |
| T1 | h5 | kappa | 0.7800 | 100 |
| T1 | h5 | shuffled_vs_yardstick | 0.9200 | 100 |
| T1 | h5 | carried_added | 0.7900 | 100 |
| T1 | h5 | pooled_retention | 0.7800 | 100 |
| T1 | h10 | large | 0.7900 | 100 |
| T1 | h10 | carries | 0.7700 | 100 |
| T1 | h10 | depends | 0.7700 | 100 |
| T1 | h10 | carried_margin | 0.7800 | 100 |
| T1 | h10 | kappa | 0.7600 | 100 |
| T1 | h10 | carried_added | 0.7600 | 100 |
| T1 | h10 | pooled_retention | 0.7600 | 100 |
| T2 | n20 | carried_margin | 0.9000 | 100 |
| T2 | n20 | own_margin | 0.8800 | 100 |
| T2 | n20 | shuffled_vs_yardstick | 0.8800 | 100 |
| T2 | n20 | carried_added | 0.8900 | 100 |
| T2 | n40 | shuffled_vs_yardstick | 0.8800 | 100 |
| T2 | n80 | large | 0.9100 | 100 |
| T2 | n80 | carried_margin | 0.9200 | 100 |
| T2 | n80 | own_margin | 0.8900 | 100 |
| T2 | n80 | shuffled_vs_yardstick | 0.8800 | 100 |
| T2 | n80 | carried_added | 0.9000 | 100 |
| T2 | n160 | carries | 0.9000 | 100 |
| T2 | n160 | depends | 0.9000 | 100 |
| T2 | n160 | shuffled_vs_yardstick | 0.8800 | 100 |
| T2 | n320 | carries | 0.9100 | 100 |
| T2 | n320 | depends | 0.9200 | 100 |
| T2 | n320 | shuffled_vs_yardstick | 0.8900 | 100 |
| T2 | h2 | shuffled_vs_yardstick | 0.8800 | 100 |
| T2 | h5 | shuffled_vs_yardstick | 0.8900 | 100 |
| T2 | h10 | large | 0.7222 | 18 |
| T2 | h10 | carries | 0.6667 | 18 |
| T2 | h10 | depends | 0.6667 | 18 |
| T2 | h10 | carried_margin | 0.6667 | 18 |
| T2 | h10 | kappa | 0.7222 | 18 |
| T2 | h10 | shuffled_vs_yardstick | 0.6111 | 18 |
| T2 | h10 | carried_added | 0.6667 | 18 |
| T2 | h10 | pooled_retention | 0.6667 | 18 |
| T3 | n20 | own_margin | 0.9000 | 100 |
| T3 | n20 | kappa | 0.9000 | 100 |
| T3 | n20 | shuffled_vs_yardstick | 0.9000 | 100 |
| T3 | n20 | pooled_retention | 0.9100 | 100 |
| T3 | n40 | kappa | 0.9200 | 100 |
| T3 | n40 | shuffled_vs_yardstick | 0.9000 | 100 |
| T3 | n40 | pooled_retention | 0.9000 | 100 |
| T3 | n80 | own_margin | 0.9200 | 100 |
| T3 | n80 | shuffled_vs_yardstick | 0.9000 | 100 |
| T3 | n80 | pooled_retention | 0.9000 | 100 |
| T3 | n160 | shuffled_vs_yardstick | 0.9100 | 100 |
| T3 | n160 | pooled_retention | 0.8800 | 100 |
| T3 | n320 | carries | 0.9200 | 100 |
| T3 | n320 | depends | 0.9200 | 100 |
| T3 | n320 | shuffled_vs_yardstick | 0.9000 | 100 |
| T3 | n320 | pooled_retention | 0.8800 | 100 |
| T3 | h2 | carries | 0.9000 | 100 |
| T3 | h2 | depends | 0.9000 | 100 |
| T3 | h2 | carried_margin | 0.9200 | 100 |
| T3 | h2 | own_margin | 0.9200 | 100 |
| T3 | h2 | kappa | 0.9200 | 100 |
| T3 | h2 | shuffled_vs_yardstick | 0.9000 | 100 |
| T3 | h2 | carried_added | 0.9000 | 100 |
| T3 | h2 | pooled_retention | 0.9000 | 100 |
| T3 | h5 | large | 0.9200 | 100 |
| T3 | h5 | carries | 0.8900 | 100 |
| T3 | h5 | depends | 0.8900 | 100 |
| T3 | h5 | carried_margin | 0.9100 | 100 |
| T3 | h5 | kappa | 0.9200 | 100 |
| T3 | h5 | shuffled_vs_yardstick | 0.8900 | 100 |
| T3 | h5 | carried_added | 0.9000 | 100 |
| T3 | h5 | pooled_retention | 0.8900 | 100 |
| T3 | h10 | large | 0.8500 | 100 |
| T3 | h10 | carries | 0.8400 | 100 |
| T3 | h10 | depends | 0.8400 | 100 |
| T3 | h10 | carried_margin | 0.8500 | 100 |
| T3 | h10 | kappa | 0.8400 | 100 |
| T3 | h10 | shuffled_vs_yardstick | 0.9200 | 100 |
| T3 | h10 | carried_added | 0.8500 | 100 |
| T3 | h10 | pooled_retention | 0.8500 | 100 |
| T4 | n20 | depends | 0.9100 | 100 |
| T4 | n20 | carried_margin | 0.9200 | 100 |
| T4 | n20 | pooled_retention | 0.8100 | 100 |
| T4 | n40 | own_margin | 0.9100 | 100 |
| T4 | n40 | carried_added | 0.9100 | 100 |
| T4 | n40 | pooled_retention | 0.8100 | 100 |
| T4 | n80 | pooled_retention | 0.8100 | 100 |
| T4 | n160 | large | 0.9200 | 100 |
| T4 | n160 | carries | 0.8800 | 100 |
| T4 | n160 | depends | 0.8800 | 100 |
| T4 | n160 | kappa | 0.8700 | 100 |
| T4 | n160 | pooled_retention | 0.8100 | 100 |
| T4 | n320 | large | 0.8800 | 100 |
| T4 | n320 | carries | 0.8700 | 100 |
| T4 | n320 | depends | 0.8700 | 100 |
| T4 | n320 | carried_margin | 0.8800 | 100 |
| T4 | n320 | kappa | 0.8500 | 100 |
| T4 | n320 | carried_added | 0.8800 | 100 |
| T4 | n320 | pooled_retention | 0.8100 | 100 |
| T4 | h2 | carries | 0.8200 | 100 |
| T4 | h2 | depends | 0.8200 | 100 |
| T4 | h2 | carried_margin | 0.8200 | 100 |
| T4 | h2 | own_margin | 0.9100 | 100 |
| T4 | h2 | kappa | 0.8000 | 100 |
| T4 | h2 | carried_added | 0.8100 | 100 |
| T4 | h2 | pooled_retention | 0.8100 | 100 |
| T4 | h5 | large | 0.8500 | 100 |
| T4 | h5 | carries | 0.8100 | 100 |
| T4 | h5 | depends | 0.8100 | 100 |
| T4 | h5 | carried_margin | 0.8100 | 100 |
| T4 | h5 | kappa | 0.8100 | 100 |
| T4 | h5 | carried_added | 0.8100 | 100 |
| T4 | h5 | pooled_retention | 0.8100 | 100 |
| T4 | h10 | large | 0.7500 | 100 |
| T4 | h10 | carries | 0.7500 | 100 |
| T4 | h10 | depends | 0.7500 | 100 |
| T4 | h10 | carried_margin | 0.7500 | 100 |
| T4 | h10 | kappa | 0.7500 | 100 |
| T4 | h10 | shuffled_vs_yardstick | 0.8600 | 100 |
| T4 | h10 | carried_added | 0.7500 | 100 |
| T4 | h10 | pooled_retention | 0.7500 | 100 |
| T5 | n20 | large | 0.7900 | 100 |
| T5 | n20 | carries | 0.7900 | 100 |
| T5 | n20 | depends | 0.7900 | 100 |
| T5 | n20 | carried_margin | 0.7900 | 100 |
| T5 | n20 | kappa | 0.9100 | 100 |
| T5 | n20 | carried_added | 0.7900 | 100 |
| T5 | n20 | pooled_retention | 0.7900 | 100 |
| T5 | n40 | large | 0.8200 | 100 |
| T5 | n40 | carries | 0.8500 | 100 |
| T5 | n40 | depends | 0.8500 | 100 |
| T5 | n40 | carried_margin | 0.8500 | 100 |
| T5 | n40 | carried_added | 0.8500 | 100 |
| T5 | n40 | pooled_retention | 0.8100 | 100 |
| T5 | n160 | large | 0.9200 | 100 |
| T5 | n160 | carries | 0.8900 | 100 |
| T5 | n160 | depends | 0.8900 | 100 |
| T5 | n160 | carried_margin | 0.9100 | 100 |
| T5 | n160 | carried_added | 0.9100 | 100 |
| T5 | n160 | pooled_retention | 0.9000 | 100 |
| T5 | n320 | carries | 0.9100 | 100 |
| T5 | n320 | depends | 0.9100 | 100 |
| T5 | n320 | kappa | 0.8900 | 100 |
| T5 | n320 | pooled_retention | 0.8900 | 100 |
| T5 | h2 | large | 0.8400 | 100 |
| T5 | h2 | carries | 0.8500 | 100 |
| T5 | h2 | depends | 0.8500 | 100 |
| T5 | h2 | carried_margin | 0.8400 | 100 |
| T5 | h2 | carried_added | 0.8500 | 100 |
| T5 | h2 | pooled_retention | 0.8500 | 100 |
| T5 | h5 | large | 0.8700 | 100 |
| T5 | h5 | carries | 0.8800 | 100 |
| T5 | h5 | depends | 0.8800 | 100 |
| T5 | h5 | carried_margin | 0.8800 | 100 |
| T5 | h5 | carried_added | 0.8800 | 100 |
| T5 | h5 | pooled_retention | 0.8800 | 100 |
| T5 | h10 | large | 0.8300 | 100 |
| T5 | h10 | carries | 0.8100 | 100 |
| T5 | h10 | depends | 0.8200 | 100 |
| T5 | h10 | carried_margin | 0.8300 | 100 |
| T5 | h10 | kappa | 0.8500 | 100 |
| T5 | h10 | shuffled_vs_yardstick | 0.8700 | 100 |
| T5 | h10 | carried_added | 0.8400 | 100 |
| T5 | h10 | pooled_retention | 0.8200 | 100 |
| T6[0.3] | n20 | carries | 0.8700 | 100 |
| T6[0.3] | n20 | depends | 0.8600 | 100 |
| T6[0.3] | n20 | carried_margin | 0.8700 | 100 |
| T6[0.3] | n20 | kappa | 0.9100 | 100 |
| T6[0.3] | n20 | carried_added | 0.9200 | 100 |
| T6[0.3] | n20 | pooled_retention | 0.9200 | 100 |
| T6[0.3] | n80 | shuffled_vs_yardstick | 0.9000 | 100 |
| T6[0.3] | n80 | pooled_retention | 0.9100 | 100 |
| T6[0.5] | n20 | carries | 0.9200 | 100 |
| T6[0.5] | n20 | depends | 0.9100 | 100 |
| T6[0.5] | n20 | carried_margin | 0.9100 | 100 |
| T6[0.5] | n20 | kappa | 0.9200 | 100 |
| T6[0.5] | n20 | pooled_retention | 0.8500 | 100 |
| T6[0.5] | n80 | shuffled_vs_yardstick | 0.8500 | 100 |
| T6[0.5] | n80 | pooled_retention | 0.8500 | 100 |
| T6[0.7] | n20 | carries | 0.8900 | 100 |
| T6[0.7] | n20 | carried_margin | 0.9100 | 100 |
| T6[0.7] | n20 | kappa | 0.9200 | 100 |
| T6[0.7] | n20 | carried_added | 0.9200 | 100 |
| T6[0.7] | n80 | large | 0.9100 | 100 |
| T6[0.7] | n80 | carried_margin | 0.8900 | 100 |
| T6[0.7] | n80 | own_margin | 0.9200 | 100 |
| T6[0.7] | n80 | kappa | 0.8700 | 100 |
| T6[0.7] | n80 | carried_added | 0.9100 | 100 |
| T6[0.85] | n20 | carries | 0.9000 | 100 |
| T6[0.85] | n20 | kappa | 0.8900 | 100 |
| T6[0.85] | n20 | carried_added | 0.8600 | 100 |
| T6[0.85] | n20 | pooled_retention | 0.8900 | 100 |
| T6[0.85] | n80 | large | 0.9100 | 100 |
| T6[0.85] | n80 | depends | 0.8600 | 100 |
| T6[0.85] | n80 | kappa | 0.9100 | 100 |
| T6[0.85] | n80 | shuffled_vs_yardstick | 0.9000 | 100 |
| T6[0.85] | n80 | carried_added | 0.9000 | 100 |
| T6[0.85] | n80 | pooled_retention | 0.9000 | 100 |
| T6[0.95] | n20 | depends | 0.6600 | 100 |
| T6[0.95] | n20 | own_margin | 0.9200 | 100 |
| T6[0.95] | n20 | kappa | 0.8600 | 100 |
| T6[0.95] | n20 | shuffled_vs_yardstick | 0.9200 | 100 |
| T6[0.95] | n20 | carried_added | 0.8700 | 100 |
| T6[0.95] | n20 | pooled_retention | 0.7800 | 100 |
| T6[0.95] | n80 | large | 0.9200 | 100 |
| T6[0.95] | n80 | depends | 0.5200 | 100 |
| T6[0.95] | n80 | shuffled_vs_yardstick | 0.7700 | 100 |
| T6[0.95] | n80 | carried_added | 0.9200 | 100 |
| T6[0.95] | n80 | pooled_retention | 0.7800 | 100 |
| T6[1] | n20 | carries | 0.9200 | 100 |
| T6[1] | n20 | kappa | 0.8900 | 100 |
| T6[1] | n20 | pooled_retention | 0.8600 | 100 |
| T6[1] | n80 | carried_margin | 0.9200 | 100 |
| T6[1] | n80 | shuffled_vs_yardstick | 0.8600 | 100 |
| T6[1] | n80 | pooled_retention | 0.8600 | 100 |
| T6[1.1] | n20 | carries | 0.8900 | 100 |
| T6[1.1] | n20 | carried_added | 0.9200 | 100 |
| T6[1.1] | n20 | pooled_retention | 0.8500 | 100 |
| T6[1.1] | n80 | carries | 0.9100 | 100 |
| T6[1.1] | n80 | depends | 0.7900 | 100 |
| T6[1.1] | n80 | shuffled_vs_yardstick | 0.8500 | 100 |
| T6[1.1] | n80 | pooled_retention | 0.8500 | 100 |
| T6[1.25] | n20 | carries | 0.8900 | 100 |
| T6[1.25] | n20 | carried_added | 0.9000 | 100 |
| T6[1.25] | n20 | pooled_retention | 0.8800 | 100 |
| T6[1.25] | n80 | depends | 0.9000 | 100 |
| T6[1.25] | n80 | shuffled_vs_yardstick | 0.8600 | 100 |
| T6[1.25] | n80 | pooled_retention | 0.8500 | 100 |
| T7 | h5 | shuffled_vs_yardstick | 0.9100 | 100 |
| T8 | n20 | carries | 0.8700 | 100 |
| T8 | n20 | depends | 0.8700 | 100 |
| T8 | n20 | carried_margin | 0.9000 | 100 |
| T8 | n20 | kappa | 0.8800 | 100 |
| T8 | n20 | pooled_retention | 0.8200 | 100 |
| T8 | n40 | kappa | 0.9200 | 100 |
| T8 | n40 | pooled_retention | 0.7900 | 100 |
| T8 | n80 | own_margin | 0.9200 | 100 |
| T8 | n80 | pooled_retention | 0.7800 | 100 |
| T8 | n160 | large | 0.9100 | 100 |
| T8 | n160 | carries | 0.8700 | 100 |
| T8 | n160 | depends | 0.8700 | 100 |
| T8 | n160 | carried_margin | 0.9200 | 100 |
| T8 | n160 | own_margin | 0.9200 | 100 |
| T8 | n160 | carried_added | 0.9100 | 100 |
| T8 | n160 | pooled_retention | 0.8100 | 100 |
| T8 | n320 | carries | 0.8700 | 100 |
| T8 | n320 | depends | 0.8700 | 100 |
| T8 | n320 | pooled_retention | 0.7900 | 100 |

## The Shuffled Ratio by Its Denominator's Distance From Zero (T6)

Pooled over the eight values of psi. Coverage leaves out psi = 1, where the ratio's truth divides by zero.

| Row | z_D | Experiments | Coverage | a | b | c | d | no reading defined |
|---|---|---|---|---|---|---|---|---|
| n20 | below 2 | 402 | 0.9353 | 0.271 | 0.000 | 0.000 | 0.729 | 0.000 |
| n20 | 2 to 3 | 47 | 0.8333 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| n20 | 3 to 5 | 89 | 0.7841 | 0.056 | 0.000 | 0.045 | 0.888 | 0.011 |
| n20 | 5 to 8 | 87 | 0.8837 | 0.471 | 0.000 | 0.000 | 0.506 | 0.023 |
| n20 | above 8 | 175 | 0.8971 | 0.851 | 0.000 | 0.006 | 0.143 | 0.000 |
| n80 | below 2 | 527 | 0.8426 | 0.076 | 0.000 | 0.002 | 0.922 | 0.000 |
| n80 | 2 to 3 | 82 | 0.7722 | 0.012 | 0.000 | 0.037 | 0.951 | 0.000 |
| n80 | 3 to 5 | 107 | 0.8868 | 0.308 | 0.000 | 0.028 | 0.636 | 0.028 |
| n80 | 5 to 8 | 76 | 0.9600 | 0.605 | 0.000 | 0.013 | 0.368 | 0.013 |
| n80 | above 8 | 8 | 0.8750 | 0.625 | 0.000 | 0.000 | 0.375 | 0.000 |

## The Delta-On Shares When the Delta Components Do Nothing (T8)

Version a: the same searches with fresh cell noise. Version b: every search redrawn from its batch type's pilot starts.

| Row | Share | Version | 2.5th percentile | Median | 97.5th percentile | Interval covers 1 |
|---|---|---|---|---|---|---|
| n20 | carried_share | a | 0.960 | 0.997 | 1.039 | 1.0000 |
| n20 | carried_share | b | 0.850 | 0.996 | 1.133 | 1.0000 |
| n20 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n20 | own_share | b | 0.881 | 0.990 | 1.124 | 0.9700 |
| n40 | carried_share | a | 0.962 | 1.001 | 1.040 | 1.0000 |
| n40 | carried_share | b | 0.867 | 1.002 | 1.183 | 0.9800 |
| n40 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n40 | own_share | b | 0.830 | 0.995 | 1.142 | 0.9500 |
| n80 | carried_share | a | 0.962 | 1.003 | 1.036 | 1.0000 |
| n80 | carried_share | b | 0.750 | 0.981 | 1.237 | 0.9600 |
| n80 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n80 | own_share | b | 0.813 | 0.976 | 1.283 | 0.9700 |
| n160 | carried_share | a | 0.968 | 1.000 | 1.038 | 1.0000 |
| n160 | carried_share | b | 0.865 | 1.001 | 1.151 | 0.9800 |
| n160 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n160 | own_share | b | 0.851 | 1.012 | 1.141 | 0.9700 |
| n320 | carried_share | a | 0.968 | 1.001 | 1.036 | 1.0000 |
| n320 | carried_share | b | 0.880 | 1.001 | 1.122 | 0.9900 |
| n320 | own_share | a | 1.000 | 1.000 | 1.000 | 1.0000 |
| n320 | own_share | b | 0.872 | 1.002 | 1.128 | 0.9600 |

## Batch-Clustered Missing Searches (T7), at 5 Nats

| Statistic | Truth | Convention, mean | Convention, bias | "Both reached", mean | "Both reached", bias |
|---|---|---|---|---|---|
| carries | 0.7000 | 0.7110 | 0.0110 | 0.7305 | 0.0305 |
| large | 2.9822 | 3.0215 | 0.0393 | 3.1180 | 0.1358 |

## Coverage by the Number of Type-C5 Batches (T3)

| Row | Reading | Side | Type-C5 batches | Experiments | Coverage |
|---|---|---|---|---|---|
| n20 | large | attack | 0 | 18 | 0.9444 |
| n20 | large | attack | 1 | 25 | 0.9200 |
| n20 | large | attack | 2 | 19 | 0.8947 |
| n20 | large | attack | 3 or more | 38 | 0.9474 |
| n20 | large | heldout | 0 | 11 | 1.0000 |
| n20 | large | heldout | 1 | 22 | 0.8182 |
| n20 | large | heldout | 2 | 26 | 1.0000 |
| n20 | large | heldout | 3 or more | 41 | 0.9268 |
| n20 | carries | attack | 0 | 18 | 0.9444 |
| n20 | carries | attack | 1 | 25 | 0.9600 |
| n20 | carries | attack | 2 | 19 | 1.0000 |
| n20 | carries | attack | 3 or more | 38 | 0.9737 |
| n20 | carries | heldout | 0 | 11 | 1.0000 |
| n20 | carries | heldout | 1 | 22 | 0.9545 |
| n20 | carries | heldout | 2 | 26 | 1.0000 |
| n20 | carries | heldout | 3 or more | 41 | 0.9512 |
| n20 | depends | attack | 0 | 18 | 0.9444 |
| n20 | depends | attack | 1 | 25 | 0.9600 |
| n20 | depends | attack | 2 | 19 | 0.9474 |
| n20 | depends | attack | 3 or more | 38 | 1.0000 |
| n20 | depends | heldout | 0 | 11 | 1.0000 |
| n20 | depends | heldout | 1 | 22 | 0.9545 |
| n20 | depends | heldout | 2 | 26 | 1.0000 |
| n20 | depends | heldout | 3 or more | 41 | 0.9512 |
| n40 | large | attack | 0 | 18 | 0.9444 |
| n40 | large | attack | 1 | 25 | 1.0000 |
| n40 | large | attack | 2 | 19 | 0.9474 |
| n40 | large | attack | 3 or more | 38 | 0.9737 |
| n40 | large | heldout | 0 | 11 | 0.9091 |
| n40 | large | heldout | 1 | 22 | 0.9545 |
| n40 | large | heldout | 2 | 26 | 1.0000 |
| n40 | large | heldout | 3 or more | 41 | 0.9756 |
| n40 | carries | attack | 0 | 18 | 1.0000 |
| n40 | carries | attack | 1 | 25 | 1.0000 |
| n40 | carries | attack | 2 | 19 | 1.0000 |
| n40 | carries | attack | 3 or more | 38 | 0.9737 |
| n40 | carries | heldout | 0 | 11 | 1.0000 |
| n40 | carries | heldout | 1 | 22 | 1.0000 |
| n40 | carries | heldout | 2 | 26 | 1.0000 |
| n40 | carries | heldout | 3 or more | 41 | 0.9756 |
| n40 | depends | attack | 0 | 18 | 1.0000 |
| n40 | depends | attack | 1 | 25 | 1.0000 |
| n40 | depends | attack | 2 | 19 | 1.0000 |
| n40 | depends | attack | 3 or more | 38 | 0.9737 |
| n40 | depends | heldout | 0 | 11 | 1.0000 |
| n40 | depends | heldout | 1 | 22 | 1.0000 |
| n40 | depends | heldout | 2 | 26 | 1.0000 |
| n40 | depends | heldout | 3 or more | 41 | 0.9756 |
| n80 | large | attack | 0 | 18 | 0.9444 |
| n80 | large | attack | 1 | 25 | 1.0000 |
| n80 | large | attack | 2 | 19 | 1.0000 |
| n80 | large | attack | 3 or more | 38 | 0.9737 |
| n80 | large | heldout | 0 | 11 | 1.0000 |
| n80 | large | heldout | 1 | 22 | 1.0000 |
| n80 | large | heldout | 2 | 26 | 0.9615 |
| n80 | large | heldout | 3 or more | 41 | 0.9756 |
| n80 | carries | attack | 0 | 18 | 1.0000 |
| n80 | carries | attack | 1 | 25 | 0.9600 |
| n80 | carries | attack | 2 | 19 | 1.0000 |
| n80 | carries | attack | 3 or more | 38 | 1.0000 |
| n80 | carries | heldout | 0 | 11 | 0.9091 |
| n80 | carries | heldout | 1 | 22 | 1.0000 |
| n80 | carries | heldout | 2 | 26 | 1.0000 |
| n80 | carries | heldout | 3 or more | 41 | 1.0000 |
| n80 | depends | attack | 0 | 18 | 1.0000 |
| n80 | depends | attack | 1 | 25 | 0.9600 |
| n80 | depends | attack | 2 | 19 | 1.0000 |
| n80 | depends | attack | 3 or more | 38 | 1.0000 |
| n80 | depends | heldout | 0 | 11 | 0.9091 |
| n80 | depends | heldout | 1 | 22 | 1.0000 |
| n80 | depends | heldout | 2 | 26 | 1.0000 |
| n80 | depends | heldout | 3 or more | 41 | 1.0000 |
| n160 | large | attack | 0 | 18 | 0.8889 |
| n160 | large | attack | 1 | 25 | 1.0000 |
| n160 | large | attack | 2 | 19 | 1.0000 |
| n160 | large | attack | 3 or more | 38 | 0.8947 |
| n160 | large | heldout | 0 | 11 | 0.7273 |
| n160 | large | heldout | 1 | 22 | 0.9545 |
| n160 | large | heldout | 2 | 26 | 1.0000 |
| n160 | large | heldout | 3 or more | 41 | 0.9512 |
| n160 | carries | attack | 0 | 18 | 1.0000 |
| n160 | carries | attack | 1 | 25 | 0.9600 |
| n160 | carries | attack | 2 | 19 | 0.9474 |
| n160 | carries | attack | 3 or more | 38 | 0.8684 |
| n160 | carries | heldout | 0 | 11 | 0.4545 |
| n160 | carries | heldout | 1 | 22 | 0.9545 |
| n160 | carries | heldout | 2 | 26 | 1.0000 |
| n160 | carries | heldout | 3 or more | 41 | 1.0000 |
| n160 | depends | attack | 0 | 18 | 1.0000 |
| n160 | depends | attack | 1 | 25 | 0.9600 |
| n160 | depends | attack | 2 | 19 | 0.9474 |
| n160 | depends | attack | 3 or more | 38 | 0.8684 |
| n160 | depends | heldout | 0 | 11 | 0.4545 |
| n160 | depends | heldout | 1 | 22 | 0.9545 |
| n160 | depends | heldout | 2 | 26 | 1.0000 |
| n160 | depends | heldout | 3 or more | 41 | 1.0000 |
| n320 | large | attack | 0 | 18 | 0.8889 |
| n320 | large | attack | 1 | 25 | 1.0000 |
| n320 | large | attack | 2 | 19 | 0.9474 |
| n320 | large | attack | 3 or more | 38 | 0.8947 |
| n320 | large | heldout | 0 | 11 | 0.6364 |
| n320 | large | heldout | 1 | 22 | 0.9545 |
| n320 | large | heldout | 2 | 26 | 1.0000 |
| n320 | large | heldout | 3 or more | 41 | 0.9512 |
| n320 | carries | attack | 0 | 18 | 1.0000 |
| n320 | carries | attack | 1 | 25 | 0.9600 |
| n320 | carries | attack | 2 | 19 | 0.9474 |
| n320 | carries | attack | 3 or more | 38 | 0.8421 |
| n320 | carries | heldout | 0 | 11 | 0.3636 |
| n320 | carries | heldout | 1 | 22 | 0.9545 |
| n320 | carries | heldout | 2 | 26 | 1.0000 |
| n320 | carries | heldout | 3 or more | 41 | 1.0000 |
| n320 | depends | attack | 0 | 18 | 1.0000 |
| n320 | depends | attack | 1 | 25 | 0.9600 |
| n320 | depends | attack | 2 | 19 | 0.9474 |
| n320 | depends | attack | 3 or more | 38 | 0.8421 |
| n320 | depends | heldout | 0 | 11 | 0.3636 |
| n320 | depends | heldout | 1 | 22 | 0.9545 |
| n320 | depends | heldout | 2 | 26 | 1.0000 |
| n320 | depends | heldout | 3 or more | 41 | 1.0000 |
| h2 | large | attack | 0 | 18 | 1.0000 |
| h2 | large | attack | 1 | 25 | 0.9600 |
| h2 | large | attack | 2 | 19 | 0.9474 |
| h2 | large | attack | 3 or more | 38 | 0.9211 |
| h2 | large | heldout | 0 | 11 | 0.7273 |
| h2 | large | heldout | 1 | 22 | 0.9091 |
| h2 | large | heldout | 2 | 26 | 1.0000 |
| h2 | large | heldout | 3 or more | 41 | 1.0000 |
| h2 | carries | attack | 0 | 18 | 0.9444 |
| h2 | carries | attack | 1 | 25 | 0.9600 |
| h2 | carries | attack | 2 | 19 | 0.8947 |
| h2 | carries | attack | 3 or more | 38 | 0.8421 |
| h2 | carries | heldout | 0 | 11 | 0.1818 |
| h2 | carries | heldout | 1 | 22 | 0.9545 |
| h2 | carries | heldout | 2 | 26 | 1.0000 |
| h2 | carries | heldout | 3 or more | 41 | 1.0000 |
| h2 | depends | attack | 0 | 18 | 0.9444 |
| h2 | depends | attack | 1 | 25 | 0.9600 |
| h2 | depends | attack | 2 | 19 | 0.8947 |
| h2 | depends | attack | 3 or more | 38 | 0.8421 |
| h2 | depends | heldout | 0 | 11 | 0.1818 |
| h2 | depends | heldout | 1 | 22 | 0.9545 |
| h2 | depends | heldout | 2 | 26 | 1.0000 |
| h2 | depends | heldout | 3 or more | 41 | 1.0000 |
| h5 | large | attack | 0 | 18 | 0.9444 |
| h5 | large | attack | 1 | 25 | 0.9600 |
| h5 | large | attack | 2 | 19 | 0.9474 |
| h5 | large | attack | 3 or more | 38 | 0.8684 |
| h5 | large | heldout | 0 | 11 | 0.3636 |
| h5 | large | heldout | 1 | 22 | 0.9545 |
| h5 | large | heldout | 2 | 26 | 1.0000 |
| h5 | large | heldout | 3 or more | 41 | 1.0000 |
| h5 | carries | attack | 0 | 18 | 0.9444 |
| h5 | carries | attack | 1 | 25 | 0.9200 |
| h5 | carries | attack | 2 | 19 | 0.8947 |
| h5 | carries | attack | 3 or more | 38 | 0.8421 |
| h5 | carries | heldout | 0 | 11 | 0.0909 |
| h5 | carries | heldout | 1 | 22 | 0.9545 |
| h5 | carries | heldout | 2 | 26 | 1.0000 |
| h5 | carries | heldout | 3 or more | 41 | 1.0000 |
| h5 | depends | attack | 0 | 18 | 0.9444 |
| h5 | depends | attack | 1 | 25 | 0.9200 |
| h5 | depends | attack | 2 | 19 | 0.8947 |
| h5 | depends | attack | 3 or more | 38 | 0.8421 |
| h5 | depends | heldout | 0 | 11 | 0.0909 |
| h5 | depends | heldout | 1 | 22 | 0.9545 |
| h5 | depends | heldout | 2 | 26 | 1.0000 |
| h5 | depends | heldout | 3 or more | 41 | 1.0000 |
| h10 | large | attack | 0 | 24 | 0.7917 |
| h10 | large | attack | 1 | 50 | 0.8600 |
| h10 | large | attack | 2 | 21 | 0.8571 |
| h10 | large | attack | 3 or more | 5 | 1.0000 |
| h10 | large | heldout | 0 | 16 | 0.0625 |
| h10 | large | heldout | 1 | 51 | 1.0000 |
| h10 | large | heldout | 2 | 25 | 1.0000 |
| h10 | large | heldout | 3 or more | 8 | 1.0000 |
| h10 | carries | attack | 0 | 24 | 0.7917 |
| h10 | carries | attack | 1 | 50 | 0.8400 |
| h10 | carries | attack | 2 | 21 | 0.8571 |
| h10 | carries | attack | 3 or more | 5 | 1.0000 |
| h10 | carries | heldout | 0 | 16 | 0.0000 |
| h10 | carries | heldout | 1 | 51 | 1.0000 |
| h10 | carries | heldout | 2 | 25 | 1.0000 |
| h10 | carries | heldout | 3 or more | 8 | 1.0000 |
| h10 | depends | attack | 0 | 24 | 0.7917 |
| h10 | depends | attack | 1 | 50 | 0.8400 |
| h10 | depends | attack | 2 | 21 | 0.8571 |
| h10 | depends | attack | 3 or more | 5 | 1.0000 |
| h10 | depends | heldout | 0 | 16 | 0.0000 |
| h10 | depends | heldout | 1 | 51 | 1.0000 |
| h10 | depends | heldout | 2 | 25 | 1.0000 |
| h10 | depends | heldout | 3 or more | 8 | 1.0000 |

## Every Scenario, Row, and Statistic

Coverage is of the unwidened interval; "above" and "below" are the shares of intervals lying wholly above and wholly below the truth; "variance ratio" is the mean of V_PB + V_c over the Monte Carlo variance of the estimate; the half-width is its median.

| Scenario | Row | Statistic | Truth | Mean | Bias | MC sd | Coverage | Above | Below | Variance ratio | Half-width | V_c = 0 | Start share > 0.5 | Mean nu | Multiplier needed | Percentile coverage | Denominator's distance | Share read |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | large | -0.4748 | -0.4794 | -0.0046 | 0.0486 | 0.9200 | 0.0800 | 0.0000 | 1.262 | 0.1101 | 0.530 | 0.000 | 13.9 | 1.823 | 0.8800 | n/a | n/a |
| P1 | n20 | carries | 0.2000 | 0.1999 | -0.0001 | 0.0217 | 0.9000 | 0.0000 | 0.1000 | 1.150 | 0.0514 | 0.550 | 0.030 | 13.3 | 1.681 | 0.8400 | 9.7 | n/a |
| P1 | n20 | depends | -0.1600 | -0.1691 | -0.0091 | 0.0706 | 0.9400 | 0.0600 | 0.0000 | 1.112 | 0.1542 | 0.570 | 0.000 | 15.3 | 1.060 | 0.9200 | 13.3 | n/a |
| P1 | n20 | carried_margin | -0.0655 | -0.0698 | -0.0043 | 0.0304 | 0.9300 | 0.0700 | 0.0000 | 1.129 | 0.0669 | 0.530 | 0.000 | 15.2 | 1.134 | 0.9200 | n/a | n/a |
| P1 | n20 | own_margin | 0.4093 | 0.4097 | 0.0003 | 0.0268 | 0.9400 | 0.0000 | 0.0600 | 1.524 | 0.0686 | 0.510 | 0.160 | 11.5 | 1.039 | 0.8700 | n/a | n/a |
| P1 | n20 | kappa | -0.5518 | -0.5778 | -0.0261 | 0.2297 | 0.9600 | 0.0400 | 0.0000 | 1.083 | 0.5129 | 0.520 | 0.000 | 15.3 | 0.889 | 0.9500 | 7.0 | n/a |
| P1 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4097 | -0.0003 | 0.0268 | 0.9400 | 0.0600 | 0.0000 | 1.524 | 0.0686 | 0.510 | 0.160 | 11.5 | 1.039 | 0.8700 | n/a | n/a |
| P1 | n20 | carried_added | 0.1187 | 0.1199 | 0.0012 | 0.0187 | 0.8900 | 0.0100 | 0.1000 | 0.894 | 0.0349 | 0.540 | 0.000 | 15.3 | 1.476 | 0.8700 | n/a | n/a |
| P1 | n20 | pooled_retention | 0.2000 | 0.2029 | 0.0029 | 0.0208 | 0.9100 | 0.0000 | 0.0900 | 1.001 | 0.0425 | 0.580 | 0.000 | 15.0 | 1.566 | 0.8900 | 10.0 | n/a |
| P1 | n40 | large | -0.2038 | -0.2052 | -0.0015 | 0.0477 | 0.9800 | 0.0100 | 0.0100 | 1.323 | 0.1133 | 0.620 | 0.020 | 13.7 | 0.769 | 0.9500 | n/a | n/a |
| P1 | n40 | carries | 0.2000 | 0.2032 | 0.0032 | 0.0243 | 0.9800 | 0.0000 | 0.0200 | 1.369 | 0.0602 | 0.670 | 0.010 | 14.3 | 0.891 | 0.9600 | 9.3 | n/a |
| P1 | n40 | depends | 0.1165 | 0.1175 | 0.0011 | 0.0241 | 0.9900 | 0.0000 | 0.0100 | 1.353 | 0.0601 | 0.680 | 0.010 | 14.5 | 0.739 | 0.9800 | 9.5 | n/a |
| P1 | n40 | carried_margin | 0.2055 | 0.2044 | -0.0011 | 0.0372 | 0.9800 | 0.0000 | 0.0200 | 1.346 | 0.0913 | 0.680 | 0.000 | 14.8 | 0.818 | 0.9600 | n/a | n/a |
| P1 | n40 | own_margin | 1.7645 | 1.7557 | -0.0087 | 0.1765 | 0.9300 | 0.0100 | 0.0600 | 1.113 | 0.3969 | 0.630 | 0.010 | 14.6 | 1.158 | 0.9200 | n/a | n/a |
| P1 | n40 | kappa | 0.5274 | 0.5202 | -0.0072 | 0.0733 | 0.9500 | 0.0500 | 0.0000 | 1.074 | 0.1594 | 0.690 | 0.000 | 15.2 | 0.998 | 0.9400 | 6.8 | n/a |
| P1 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4096 | -0.0003 | 0.0267 | 0.9400 | 0.0600 | 0.0000 | 1.525 | 0.0688 | 0.510 | 0.170 | 11.6 | 1.047 | 0.8700 | n/a | n/a |
| P1 | n40 | carried_added | 0.3897 | 0.3941 | 0.0044 | 0.0550 | 0.9400 | 0.0100 | 0.0500 | 1.144 | 0.1244 | 0.680 | 0.000 | 15.1 | 1.006 | 0.9300 | n/a | n/a |
| P1 | n40 | pooled_retention | 0.2000 | 0.2027 | 0.0027 | 0.0208 | 0.9100 | 0.0000 | 0.0900 | 1.006 | 0.0429 | 0.540 | 0.000 | 15.1 | 1.537 | 0.8800 | 9.4 | n/a |
| P1 | n80 | large | 1.3592 | 1.3803 | 0.0211 | 0.2215 | 0.9500 | 0.0000 | 0.0500 | 1.049 | 0.4627 | 0.600 | 0.030 | 13.4 | 0.904 | 0.9100 | n/a | n/a |
| P1 | n80 | carries | 0.2000 | 0.2062 | 0.0062 | 0.0329 | 0.9400 | 0.0100 | 0.0500 | 1.187 | 0.0720 | 0.580 | 0.050 | 13.5 | 1.180 | 0.9400 | 12.6 | n/a |
| P1 | n80 | depends | 0.1846 | 0.1903 | 0.0057 | 0.0303 | 0.9500 | 0.0000 | 0.0500 | 1.212 | 0.0675 | 0.590 | 0.050 | 13.2 | 0.999 | 0.9400 | 12.3 | n/a |
| P1 | n80 | carried_margin | 1.7685 | 1.7901 | 0.0216 | 0.2257 | 0.9600 | 0.0000 | 0.0400 | 1.078 | 0.4739 | 0.600 | 0.030 | 13.5 | 0.887 | 0.9000 | n/a | n/a |
| P1 | n80 | own_margin | 9.5794 | 9.4810 | -0.0984 | 0.7285 | 0.9700 | 0.0100 | 0.0200 | 1.262 | 1.7010 | 0.640 | 0.140 | 12.4 | 0.870 | 0.9100 | n/a | n/a |
| P1 | n80 | kappa | 0.9057 | 0.9047 | -0.0010 | 0.0142 | 0.9300 | 0.0600 | 0.0100 | 0.937 | 0.0295 | 0.610 | 0.000 | 14.2 | 1.062 | 0.9100 | 7.8 | n/a |
| P1 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4098 | -0.0005 | 0.0269 | 0.9400 | 0.0600 | 0.0000 | 1.515 | 0.0682 | 0.530 | 0.160 | 11.5 | 1.028 | 0.8700 | n/a | n/a |
| P1 | n80 | carried_added | 1.9527 | 1.9797 | 0.0270 | 0.2562 | 0.9300 | 0.0000 | 0.0700 | 1.066 | 0.5499 | 0.600 | 0.020 | 13.9 | 1.065 | 0.8900 | n/a | n/a |
| P1 | n80 | pooled_retention | 0.2000 | 0.2030 | 0.0030 | 0.0211 | 0.9100 | 0.0000 | 0.0900 | 0.989 | 0.0424 | 0.480 | 0.000 | 15.1 | 1.609 | 0.8800 | 12.4 | n/a |
| P1 | n160 | large | 3.8260 | 3.9004 | 0.0744 | 0.4543 | 0.9700 | 0.0000 | 0.0300 | 1.190 | 1.0296 | 0.560 | 0.020 | 14.3 | 0.816 | 0.9400 | n/a | n/a |
| P1 | n160 | carries | 0.2000 | 0.2074 | 0.0074 | 0.0327 | 0.9600 | 0.0000 | 0.0400 | 1.152 | 0.0691 | 0.610 | 0.010 | 14.5 | 0.963 | 0.9400 | 16.5 | n/a |
| P1 | n160 | depends | 0.1933 | 0.2005 | 0.0072 | 0.0313 | 0.9600 | 0.0000 | 0.0400 | 1.161 | 0.0664 | 0.610 | 0.010 | 14.4 | 0.843 | 0.9400 | 16.1 | n/a |
| P1 | n160 | carried_margin | 4.2353 | 4.3102 | 0.0749 | 0.4618 | 0.9700 | 0.0000 | 0.0300 | 1.195 | 1.0454 | 0.580 | 0.010 | 14.4 | 0.850 | 0.9500 | n/a | n/a |
| P1 | n160 | own_margin | 21.9134 | 21.6776 | -0.2358 | 1.4149 | 0.9500 | 0.0200 | 0.0300 | 0.999 | 2.9520 | 0.690 | 0.050 | 13.4 | 0.988 | 0.8900 | n/a | n/a |
| P1 | n160 | kappa | 0.9583 | 0.9582 | -0.0001 | 0.0061 | 0.9300 | 0.0600 | 0.0100 | 0.816 | 0.0118 | 0.570 | 0.000 | 15.0 | 1.385 | 0.8800 | 8.4 | n/a |
| P1 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4097 | -0.0004 | 0.0267 | 0.9400 | 0.0600 | 0.0000 | 1.527 | 0.0683 | 0.520 | 0.150 | 11.6 | 1.007 | 0.8700 | n/a | n/a |
| P1 | n160 | carried_added | 4.4195 | 4.4998 | 0.0803 | 0.4955 | 0.9700 | 0.0000 | 0.0300 | 1.187 | 1.1088 | 0.580 | 0.000 | 14.6 | 0.900 | 0.9500 | n/a | n/a |
| P1 | n160 | pooled_retention | 0.2000 | 0.2028 | 0.0028 | 0.0207 | 0.9100 | 0.0000 | 0.0900 | 1.004 | 0.0425 | 0.530 | 0.000 | 15.1 | 1.837 | 0.8900 | 16.8 | n/a |
| P1 | n320 | large | 4.4962 | 4.5707 | 0.0745 | 0.5077 | 0.9700 | 0.0000 | 0.0300 | 1.249 | 1.1798 | 0.530 | 0.010 | 14.5 | 0.738 | 0.9600 | n/a | n/a |
| P1 | n320 | carries | 0.2000 | 0.2061 | 0.0061 | 0.0312 | 0.9500 | 0.0000 | 0.0500 | 1.215 | 0.0677 | 0.570 | 0.000 | 14.8 | 1.125 | 0.9300 | 16.6 | n/a |
| P1 | n320 | depends | 0.1942 | 0.2000 | 0.0059 | 0.0300 | 0.9500 | 0.0000 | 0.0500 | 1.224 | 0.0655 | 0.570 | 0.000 | 14.8 | 0.921 | 0.9400 | 16.2 | n/a |
| P1 | n320 | carried_margin | 4.9055 | 4.9804 | 0.0749 | 0.5166 | 0.9700 | 0.0000 | 0.0300 | 1.250 | 1.1962 | 0.540 | 0.010 | 14.5 | 0.745 | 0.9600 | n/a | n/a |
| P1 | n320 | own_margin | 25.2643 | 25.0787 | -0.1857 | 1.4772 | 0.9400 | 0.0300 | 0.0300 | 1.111 | 3.2972 | 0.660 | 0.060 | 13.1 | 1.032 | 0.9000 | n/a | n/a |
| P1 | n320 | kappa | 0.9638 | 0.9636 | -0.0002 | 0.0054 | 0.9100 | 0.0600 | 0.0300 | 0.790 | 0.0101 | 0.550 | 0.000 | 14.9 | 1.595 | 0.8600 | 8.6 | n/a |
| P1 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4097 | -0.0004 | 0.0268 | 0.9400 | 0.0600 | 0.0000 | 1.519 | 0.0683 | 0.520 | 0.160 | 11.6 | 1.038 | 0.8700 | n/a | n/a |
| P1 | n320 | carried_added | 5.0897 | 5.1700 | 0.0803 | 0.5505 | 0.9700 | 0.0000 | 0.0300 | 1.240 | 1.2690 | 0.540 | 0.010 | 14.7 | 0.774 | 0.9600 | n/a | n/a |
| P1 | n320 | pooled_retention | 0.2000 | 0.2030 | 0.0030 | 0.0210 | 0.9100 | 0.0000 | 0.0900 | 0.984 | 0.0423 | 0.480 | 0.000 | 15.1 | 1.527 | 0.8800 | 18.2 | n/a |
| P1 | h2 | large | -0.2116 | -0.2116 | -0.0001 | 0.0277 | 0.9400 | 0.0600 | 0.0000 | 1.537 | 0.0697 | 0.550 | 0.150 | 11.9 | 1.042 | 0.8600 | n/a | 1.000 |
| P1 | h2 | carries | 0.2000 | 0.2028 | 0.0028 | 0.0197 | 0.9100 | 0.0000 | 0.0900 | 0.993 | 0.0402 | 0.590 | 0.000 | 15.1 | 1.776 | 0.8800 | 121.6 | 1.000 |
| P1 | h2 | depends | 0.1146 | 0.1151 | 0.0005 | 0.0024 | 0.9900 | 0.0000 | 0.0100 | 1.968 | 0.0068 | 0.530 | 0.010 | 14.6 | 0.611 | 0.9900 | 55.0 | 1.000 |
| P1 | h2 | carried_margin | 0.1978 | 0.1980 | 0.0003 | 0.0044 | 1.0000 | 0.0000 | 0.0000 | 1.822 | 0.0125 | 0.580 | 0.000 | 14.7 | 0.672 | 0.9700 | n/a | 1.000 |
| P1 | h2 | own_margin | 1.7255 | 1.7207 | -0.0049 | 0.0320 | 0.9200 | 0.0700 | 0.0100 | 1.074 | 0.0668 | 0.580 | 0.010 | 15.1 | 1.088 | 0.8900 | n/a | 1.000 |
| P1 | h2 | kappa | 0.5177 | 0.5166 | -0.0012 | 0.0579 | 0.9000 | 0.0900 | 0.0100 | 0.923 | 0.1186 | 0.600 | 0.000 | 15.0 | 1.456 | 0.8900 | 10.2 | 1.000 |
| P1 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4097 | -0.0004 | 0.0268 | 0.9400 | 0.0600 | 0.0000 | 1.514 | 0.0685 | 0.510 | 0.160 | 11.6 | 1.031 | 0.8700 | n/a | 1.000 |
| P1 | h2 | carried_added | 0.3819 | 0.3877 | 0.0058 | 0.0402 | 0.9100 | 0.0000 | 0.0900 | 0.984 | 0.0817 | 0.610 | 0.000 | 15.1 | 1.655 | 0.8800 | n/a | 1.000 |
| P1 | h2 | pooled_retention | 0.2000 | 0.2032 | 0.0032 | 0.0209 | 0.9100 | 0.0000 | 0.0900 | 0.996 | 0.0425 | 0.590 | 0.000 | 15.0 | 1.694 | 0.8700 | 124.0 | 1.000 |
| P1 | h5 | large | 0.4283 | 0.4351 | 0.0068 | 0.0556 | 0.9400 | 0.0000 | 0.0600 | 1.155 | 0.1193 | 0.590 | 0.040 | 13.6 | 1.011 | 0.9300 | n/a | 0.980 |
| P1 | h5 | carries | 0.2000 | 0.2023 | 0.0023 | 0.0212 | 0.9100 | 0.0000 | 0.0900 | 1.027 | 0.0430 | 0.700 | 0.000 | 15.1 | 1.845 | 0.8900 | 150.7 | 0.980 |
| P1 | h5 | depends | 0.1701 | 0.1719 | 0.0018 | 0.0149 | 0.9100 | 0.0000 | 0.0900 | 1.069 | 0.0307 | 0.700 | 0.000 | 15.1 | 1.428 | 0.8900 | 79.3 | 0.980 |
| P1 | h5 | carried_margin | 0.8376 | 0.8446 | 0.0069 | 0.0635 | 0.9100 | 0.0000 | 0.0900 | 1.048 | 0.1317 | 0.680 | 0.000 | 15.1 | 1.525 | 0.9000 | n/a | 0.980 |
| P1 | h5 | own_margin | 4.9248 | 4.9188 | -0.0060 | 0.0607 | 0.9500 | 0.0400 | 0.0100 | 1.181 | 0.1386 | 0.570 | 0.030 | 13.6 | 0.960 | 0.9200 | n/a | 0.980 |
| P1 | h5 | kappa | 0.8197 | 0.8197 | 0.0000 | 0.0222 | 0.8900 | 0.0900 | 0.0200 | 0.874 | 0.0438 | 0.630 | 0.000 | 15.1 | 1.477 | 0.8800 | 10.2 | 0.980 |
| P1 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4094 | -0.0001 | 0.0264 | 0.9500 | 0.0500 | 0.0000 | 1.670 | 0.0696 | 0.590 | 0.220 | 11.4 | 0.966 | 0.8800 | n/a | 0.980 |
| P1 | h5 | carried_added | 1.0218 | 1.0330 | 0.0112 | 0.1055 | 0.9100 | 0.0000 | 0.0900 | 1.011 | 0.2129 | 0.680 | 0.000 | 15.1 | 1.646 | 0.8900 | n/a | 0.980 |
| P1 | h5 | pooled_retention | 0.2000 | 0.2023 | 0.0023 | 0.0208 | 0.9100 | 0.0000 | 0.0900 | 0.995 | 0.0416 | 0.570 | 0.000 | 15.1 | 1.674 | 0.8900 | 161.1 | 0.980 |
| P1 | h10 | large | 1.5787 | 1.4925 | -0.0862 | 0.1082 | 0.8200 | 0.0000 | 0.1800 | 1.672 | 0.2829 | 0.510 | 0.000 | 15.2 | 1.934 | 0.8200 | n/a | 0.186 |
| P1 | h10 | carries | 0.2000 | 0.1886 | -0.0114 | 0.0131 | 0.8200 | 0.0000 | 0.1800 | 1.681 | 0.0348 | 0.560 | 0.000 | 15.1 | 2.245 | 0.8200 | 141.6 | 0.186 |
| P1 | h10 | depends | 0.1862 | 0.1764 | -0.0098 | 0.0114 | 0.8200 | 0.0000 | 0.1800 | 1.692 | 0.0300 | 0.540 | 0.000 | 15.1 | 2.116 | 0.8200 | 125.4 | 0.186 |
| P1 | h10 | carried_margin | 1.9880 | 1.8876 | -0.1004 | 0.1134 | 0.8200 | 0.0000 | 0.1800 | 1.754 | 0.3055 | 0.520 | 0.000 | 15.1 | 2.247 | 0.8200 | n/a | 0.186 |
| P1 | h10 | own_margin | 10.6772 | 10.7021 | 0.0249 | 0.0736 | 0.9800 | 0.0100 | 0.0100 | 1.706 | 0.1879 | 0.550 | 0.200 | 10.9 | 0.877 | 0.9000 | n/a | 0.186 |
| P1 | h10 | kappa | 0.9152 | 0.9222 | 0.0070 | 0.0075 | 0.8200 | 0.1800 | 0.0000 | 1.509 | 0.0201 | 0.520 | 0.000 | 15.2 | 2.049 | 0.8200 | 11.3 | 0.186 |
| P1 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3951 | 0.0142 | 0.0203 | 0.8500 | 0.1500 | 0.0000 | 1.464 | 0.0451 | 0.570 | 0.010 | 14.2 | 1.596 | 0.7700 | n/a | 0.186 |
| P1 | h10 | carried_added | 2.1722 | 2.0480 | -0.1242 | 0.1390 | 0.8200 | 0.0000 | 0.1800 | 1.738 | 0.3742 | 0.510 | 0.000 | 15.2 | 2.361 | 0.8200 | n/a | 0.186 |
| P1 | h10 | pooled_retention | 0.2000 | 0.1882 | -0.0118 | 0.0127 | 0.8200 | 0.0000 | 0.1800 | 1.740 | 0.0342 | 0.610 | 0.000 | 15.1 | 2.277 | 0.8200 | 148.1 | 0.186 |
| P2 | n20 | large | -0.2374 | -0.2389 | -0.0015 | 0.0461 | 0.9800 | 0.0000 | 0.0200 | 1.228 | 0.1065 | 0.530 | 0.040 | 13.4 | 0.854 | 0.9200 | n/a | n/a |
| P2 | n20 | carries | 0.6000 | 0.5981 | -0.0019 | 0.0638 | 0.9200 | 0.0000 | 0.0800 | 1.161 | 0.1430 | 0.540 | 0.020 | 13.7 | 1.117 | 0.9000 | 9.6 | n/a |
| P2 | n20 | depends | 0.4200 | 0.4172 | -0.0028 | 0.0912 | 0.9200 | 0.0000 | 0.0800 | 1.204 | 0.1989 | 0.550 | 0.010 | 14.3 | 1.108 | 0.8800 | 14.7 | n/a |
| P2 | n20 | carried_margin | 0.1719 | 0.1693 | -0.0026 | 0.0337 | 0.8800 | 0.0000 | 0.1200 | 1.261 | 0.0749 | 0.600 | 0.000 | 14.7 | 1.636 | 0.8600 | n/a | n/a |
| P2 | n20 | own_margin | 0.4093 | 0.4081 | -0.0012 | 0.0267 | 0.8900 | 0.0000 | 0.1100 | 1.373 | 0.0605 | 0.630 | 0.120 | 12.6 | 1.287 | 0.8500 | n/a | n/a |
| P2 | n20 | kappa | 0.4827 | 0.4786 | -0.0042 | 0.0773 | 0.9300 | 0.0600 | 0.0100 | 1.038 | 0.1682 | 0.600 | 0.000 | 15.2 | 1.032 | 0.8900 | 7.2 | n/a |
| P2 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4081 | 0.0012 | 0.0267 | 0.8900 | 0.1100 | 0.0000 | 1.373 | 0.0605 | 0.630 | 0.120 | 12.6 | 1.287 | 0.8500 | n/a | n/a |
| P2 | n20 | carried_added | 0.3561 | 0.3548 | -0.0013 | 0.0487 | 0.9000 | 0.0000 | 0.1000 | 1.140 | 0.1035 | 0.600 | 0.000 | 15.2 | 1.198 | 0.9100 | n/a | n/a |
| P2 | n20 | pooled_retention | 0.6000 | 0.6011 | 0.0011 | 0.0593 | 0.9000 | 0.0000 | 0.1000 | 1.089 | 0.1279 | 0.460 | 0.000 | 15.1 | 1.968 | 0.9000 | 9.7 | n/a |
| P2 | n40 | large | 0.5757 | 0.5835 | 0.0078 | 0.1403 | 0.9800 | 0.0000 | 0.0200 | 1.068 | 0.2949 | 0.650 | 0.000 | 14.8 | 0.847 | 0.9500 | n/a | n/a |
| P2 | n40 | carries | 0.6000 | 0.6049 | 0.0049 | 0.0776 | 0.9400 | 0.0100 | 0.0500 | 1.174 | 0.1764 | 0.580 | 0.010 | 14.3 | 1.003 | 0.9400 | 9.3 | n/a |
| P2 | n40 | depends | 0.5582 | 0.5641 | 0.0059 | 0.0828 | 0.9500 | 0.0100 | 0.0400 | 1.173 | 0.1901 | 0.580 | 0.000 | 14.3 | 0.990 | 0.9300 | 9.8 | n/a |
| P2 | n40 | carried_margin | 0.9850 | 0.9916 | 0.0066 | 0.1397 | 0.9800 | 0.0000 | 0.0200 | 1.134 | 0.2981 | 0.620 | 0.000 | 15.2 | 0.849 | 0.9700 | n/a | n/a |
| P2 | n40 | own_margin | 1.7645 | 1.7679 | 0.0034 | 0.1665 | 0.9500 | 0.0100 | 0.0400 | 1.270 | 0.3946 | 0.570 | 0.010 | 14.3 | 0.940 | 0.9400 | n/a | n/a |
| P2 | n40 | kappa | 0.8425 | 0.8424 | -0.0000 | 0.0261 | 0.9100 | 0.0900 | 0.0000 | 0.911 | 0.0529 | 0.600 | 0.000 | 15.3 | 1.192 | 0.9000 | 7.0 | n/a |
| P2 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4082 | 0.0011 | 0.0268 | 0.8900 | 0.1100 | 0.0000 | 1.363 | 0.0599 | 0.620 | 0.120 | 12.5 | 1.256 | 0.8400 | n/a | n/a |
| P2 | n40 | carried_added | 1.1692 | 1.1771 | 0.0079 | 0.1620 | 0.9900 | 0.0000 | 0.0100 | 1.153 | 0.3508 | 0.620 | 0.000 | 15.3 | 0.865 | 0.9600 | n/a | n/a |
| P2 | n40 | pooled_retention | 0.6000 | 0.6010 | 0.0010 | 0.0588 | 0.9100 | 0.0000 | 0.0900 | 1.107 | 0.1267 | 0.520 | 0.000 | 15.1 | 1.991 | 0.9000 | 9.5 | n/a |
| P2 | n80 | large | 5.2647 | 5.3028 | 0.0381 | 0.6909 | 0.9500 | 0.0000 | 0.0500 | 1.174 | 1.6160 | 0.580 | 0.030 | 13.5 | 0.989 | 0.9000 | n/a | n/a |
| P2 | n80 | carries | 0.6000 | 0.6079 | 0.0079 | 0.0932 | 0.9300 | 0.0000 | 0.0700 | 1.199 | 0.2136 | 0.620 | 0.030 | 13.5 | 1.051 | 0.8900 | 12.9 | n/a |
| P2 | n80 | depends | 0.5923 | 0.6006 | 0.0083 | 0.0936 | 0.9300 | 0.0000 | 0.0700 | 1.207 | 0.2140 | 0.620 | 0.030 | 13.5 | 1.042 | 0.8900 | 12.6 | n/a |
| P2 | n80 | carried_margin | 5.6740 | 5.7110 | 0.0370 | 0.6981 | 0.9400 | 0.0000 | 0.0600 | 1.180 | 1.6201 | 0.570 | 0.030 | 13.6 | 1.039 | 0.9000 | n/a | n/a |
| P2 | n80 | own_margin | 9.5794 | 9.5768 | -0.0026 | 0.6939 | 0.9900 | 0.0000 | 0.0100 | 1.402 | 1.7141 | 0.530 | 0.100 | 12.1 | 0.762 | 0.9300 | n/a | n/a |
| P2 | n80 | kappa | 0.9686 | 0.9687 | 0.0002 | 0.0044 | 0.9400 | 0.0600 | 0.0000 | 1.085 | 0.0095 | 0.560 | 0.000 | 14.2 | 1.058 | 0.9100 | 7.6 | n/a |
| P2 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4082 | 0.0011 | 0.0267 | 0.8900 | 0.1100 | 0.0000 | 1.369 | 0.0599 | 0.630 | 0.120 | 12.5 | 1.290 | 0.8400 | n/a | n/a |
| P2 | n80 | carried_added | 5.8582 | 5.8965 | 0.0383 | 0.7294 | 0.9400 | 0.0000 | 0.0600 | 1.171 | 1.6792 | 0.570 | 0.030 | 13.7 | 1.087 | 0.9000 | n/a | n/a |
| P2 | n80 | pooled_retention | 0.6000 | 0.6019 | 0.0019 | 0.0605 | 0.8900 | 0.0000 | 0.1100 | 1.054 | 0.1295 | 0.460 | 0.000 | 15.1 | 1.793 | 0.8800 | 12.7 | n/a |
| P2 | n160 | large | 12.6650 | 12.8673 | 0.2022 | 1.3637 | 0.9600 | 0.0000 | 0.0400 | 1.322 | 3.3197 | 0.590 | 0.000 | 14.6 | 0.843 | 0.9400 | n/a | n/a |
| P2 | n160 | carries | 0.6000 | 0.6154 | 0.0154 | 0.0922 | 0.9400 | 0.0000 | 0.0600 | 1.297 | 0.2124 | 0.490 | 0.000 | 14.7 | 1.074 | 0.9300 | 15.7 | n/a |
| P2 | n160 | depends | 0.5966 | 0.6123 | 0.0157 | 0.0923 | 0.9400 | 0.0000 | 0.0600 | 1.303 | 0.2123 | 0.490 | 0.000 | 14.6 | 1.067 | 0.9300 | 15.3 | n/a |
| P2 | n160 | carried_margin | 13.0743 | 13.2754 | 0.2011 | 1.3730 | 0.9600 | 0.0000 | 0.0400 | 1.323 | 3.3225 | 0.600 | 0.000 | 14.6 | 0.823 | 0.9400 | n/a | n/a |
| P2 | n160 | own_margin | 21.9134 | 21.8441 | -0.0693 | 1.2952 | 0.9800 | 0.0200 | 0.0000 | 1.284 | 3.1220 | 0.490 | 0.120 | 11.9 | 0.892 | 0.9200 | n/a | n/a |
| P2 | n160 | kappa | 0.9861 | 0.9863 | 0.0002 | 0.0018 | 0.9200 | 0.0800 | 0.0000 | 1.054 | 0.0039 | 0.570 | 0.000 | 15.1 | 1.490 | 0.9100 | 8.5 | n/a |
| P2 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4081 | 0.0012 | 0.0267 | 0.8900 | 0.1100 | 0.0000 | 1.373 | 0.0615 | 0.630 | 0.120 | 12.4 | 1.275 | 0.8400 | n/a | n/a |
| P2 | n160 | carried_added | 13.2585 | 13.4610 | 0.2024 | 1.4089 | 0.9600 | 0.0000 | 0.0400 | 1.312 | 3.4009 | 0.600 | 0.000 | 14.7 | 0.851 | 0.9400 | n/a | n/a |
| P2 | n160 | pooled_retention | 0.6000 | 0.6020 | 0.0020 | 0.0594 | 0.9100 | 0.0000 | 0.0900 | 1.074 | 0.1273 | 0.490 | 0.000 | 15.1 | 1.913 | 0.9000 | 16.2 | n/a |
| P2 | n320 | large | 14.6756 | 14.8017 | 0.1260 | 1.5216 | 0.9600 | 0.0000 | 0.0400 | 1.357 | 3.7151 | 0.590 | 0.000 | 14.7 | 0.896 | 0.9300 | n/a | n/a |
| P2 | n320 | carries | 0.6000 | 0.6106 | 0.0106 | 0.0885 | 0.9400 | 0.0000 | 0.0600 | 1.330 | 0.2040 | 0.520 | 0.000 | 14.7 | 1.091 | 0.9300 | 17.7 | n/a |
| P2 | n320 | depends | 0.5971 | 0.6079 | 0.0108 | 0.0885 | 0.9400 | 0.0000 | 0.0600 | 1.335 | 0.2038 | 0.520 | 0.000 | 14.7 | 1.087 | 0.9300 | 17.2 | n/a |
| P2 | n320 | carried_margin | 15.0849 | 15.2097 | 0.1248 | 1.5312 | 0.9600 | 0.0000 | 0.0400 | 1.358 | 3.7484 | 0.550 | 0.000 | 14.8 | 0.906 | 0.9300 | n/a | n/a |
| P2 | n320 | own_margin | 25.2643 | 25.1915 | -0.0728 | 1.3677 | 0.9900 | 0.0000 | 0.0100 | 1.298 | 3.3148 | 0.480 | 0.130 | 12.4 | 0.766 | 0.9300 | n/a | n/a |
| P2 | n320 | kappa | 0.9879 | 0.9881 | 0.0001 | 0.0016 | 0.9100 | 0.0800 | 0.0100 | 0.980 | 0.0033 | 0.580 | 0.000 | 15.1 | 1.388 | 0.8900 | 8.6 | n/a |
| P2 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4081 | 0.0012 | 0.0267 | 0.8900 | 0.1100 | 0.0000 | 1.371 | 0.0595 | 0.620 | 0.120 | 12.6 | 1.292 | 0.8500 | n/a | n/a |
| P2 | n320 | carried_added | 15.2691 | 15.3953 | 0.1262 | 1.5671 | 0.9600 | 0.0000 | 0.0400 | 1.348 | 3.8157 | 0.550 | 0.000 | 14.8 | 0.921 | 0.9300 | n/a | n/a |
| P2 | n320 | pooled_retention | 0.6000 | 0.6020 | 0.0020 | 0.0589 | 0.9000 | 0.0000 | 0.1000 | 1.101 | 0.1271 | 0.610 | 0.000 | 15.0 | 1.857 | 0.9000 | 17.6 | n/a |
| P2 | h2 | large | 0.5523 | 0.5552 | 0.0029 | 0.0693 | 0.9000 | 0.0000 | 0.1000 | 0.979 | 0.1331 | 0.670 | 0.000 | 14.7 | 1.418 | 0.8700 | n/a | 1.000 |
| P2 | h2 | carries | 0.6000 | 0.6013 | 0.0013 | 0.0566 | 0.9000 | 0.0000 | 0.1000 | 1.048 | 0.1210 | 0.550 | 0.000 | 15.1 | 1.777 | 0.9000 | 123.8 | 1.000 |
| P2 | h2 | depends | 0.5573 | 0.5596 | 0.0023 | 0.0533 | 0.9000 | 0.0000 | 0.1000 | 1.083 | 0.1130 | 0.550 | 0.000 | 15.1 | 1.812 | 0.9000 | 54.3 | 1.000 |
| P2 | h2 | carried_margin | 0.9616 | 0.9633 | 0.0017 | 0.0753 | 0.9100 | 0.0000 | 0.0900 | 1.047 | 0.1579 | 0.550 | 0.000 | 15.1 | 1.802 | 0.9100 | n/a | 1.000 |
| P2 | h2 | own_margin | 1.7255 | 1.7242 | -0.0013 | 0.0306 | 0.9300 | 0.0700 | 0.0000 | 1.121 | 0.0680 | 0.570 | 0.000 | 15.1 | 1.073 | 0.9000 | n/a | 1.000 |
| P2 | h2 | kappa | 0.8392 | 0.8403 | 0.0010 | 0.0188 | 0.9000 | 0.0900 | 0.0100 | 0.973 | 0.0403 | 0.530 | 0.000 | 15.1 | 1.479 | 0.8900 | 10.1 | 1.000 |
| P2 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4081 | 0.0012 | 0.0266 | 0.8900 | 0.1100 | 0.0000 | 1.379 | 0.0605 | 0.630 | 0.120 | 12.5 | 1.300 | 0.8400 | n/a | 1.000 |
| P2 | h2 | carried_added | 1.1458 | 1.1489 | 0.0031 | 0.1150 | 0.9000 | 0.0000 | 0.1000 | 1.050 | 0.2441 | 0.540 | 0.000 | 15.1 | 1.895 | 0.8900 | n/a | 1.000 |
| P2 | h2 | pooled_retention | 0.6000 | 0.6019 | 0.0019 | 0.0603 | 0.9000 | 0.0000 | 0.1000 | 1.042 | 0.1280 | 0.600 | 0.000 | 15.1 | 1.914 | 0.8900 | 123.7 | 1.000 |
| P2 | h5 | large | 2.4719 | 2.4808 | 0.0089 | 0.2518 | 0.9000 | 0.0000 | 0.1000 | 1.084 | 0.5394 | 0.560 | 0.000 | 15.2 | 1.538 | 0.8800 | n/a | 1.000 |
| P2 | h5 | carries | 0.6000 | 0.6020 | 0.0020 | 0.0607 | 0.9000 | 0.0000 | 0.1000 | 1.106 | 0.1293 | 0.560 | 0.000 | 15.1 | 1.681 | 0.9000 | 151.7 | 1.000 |
| P2 | h5 | depends | 0.5850 | 0.5875 | 0.0024 | 0.0598 | 0.9000 | 0.0000 | 0.1000 | 1.122 | 0.1269 | 0.550 | 0.000 | 15.1 | 1.683 | 0.9000 | 75.5 | 1.000 |
| P2 | h5 | carried_margin | 2.8812 | 2.8891 | 0.0078 | 0.2621 | 0.9000 | 0.0000 | 0.1000 | 1.103 | 0.5589 | 0.560 | 0.000 | 15.1 | 1.629 | 0.9000 | n/a | 1.000 |
| P2 | h5 | own_margin | 4.9248 | 4.9230 | -0.0018 | 0.0588 | 0.9600 | 0.0400 | 0.0000 | 1.258 | 0.1454 | 0.510 | 0.060 | 13.1 | 0.924 | 0.8900 | n/a | 1.000 |
| P2 | h5 | kappa | 0.9399 | 0.9403 | 0.0004 | 0.0071 | 0.9100 | 0.0900 | 0.0000 | 0.957 | 0.0151 | 0.550 | 0.000 | 15.1 | 1.666 | 0.8900 | 10.2 | 1.000 |
| P2 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4083 | 0.0010 | 0.0269 | 0.9000 | 0.1000 | 0.0000 | 1.466 | 0.0648 | 0.620 | 0.180 | 11.9 | 1.258 | 0.8400 | n/a | 1.000 |
| P2 | h5 | carried_added | 3.0654 | 3.0745 | 0.0091 | 0.3017 | 0.9000 | 0.0000 | 0.1000 | 1.098 | 0.6445 | 0.560 | 0.000 | 15.1 | 1.667 | 0.8900 | n/a | 1.000 |
| P2 | h5 | pooled_retention | 0.6000 | 0.6017 | 0.0017 | 0.0590 | 0.9000 | 0.0000 | 0.1000 | 1.095 | 0.1266 | 0.570 | 0.000 | 15.1 | 1.761 | 0.9000 | 162.7 | 1.000 |
| P2 | h10 | large | 5.9232 | 5.5302 | -0.3930 | 0.3610 | 0.7600 | 0.0000 | 0.2400 | 1.861 | 1.0342 | 0.590 | 0.000 | 15.2 | 2.105 | 0.7500 | n/a | 0.225 |
| P2 | h10 | carries | 0.6000 | 0.5598 | -0.0402 | 0.0366 | 0.7600 | 0.0000 | 0.2400 | 1.846 | 0.1026 | 0.540 | 0.000 | 15.2 | 2.012 | 0.7500 | 140.5 | 0.225 |
| P2 | h10 | depends | 0.5931 | 0.5534 | -0.0397 | 0.0362 | 0.7600 | 0.0000 | 0.2400 | 1.849 | 0.1013 | 0.560 | 0.000 | 15.2 | 2.017 | 0.7500 | 123.5 | 0.225 |
| P2 | h10 | carried_margin | 6.3325 | 5.9266 | -0.4060 | 0.3662 | 0.7600 | 0.0000 | 0.2400 | 1.888 | 1.0536 | 0.590 | 0.000 | 15.2 | 2.128 | 0.7600 | n/a | 0.225 |
| P2 | h10 | own_margin | 10.6772 | 10.7117 | 0.0346 | 0.0769 | 0.9800 | 0.0100 | 0.0100 | 1.612 | 0.1868 | 0.530 | 0.260 | 10.5 | 0.869 | 0.9400 | n/a | 0.225 |
| P2 | h10 | kappa | 0.9717 | 0.9742 | 0.0025 | 0.0023 | 0.7800 | 0.2200 | 0.0000 | 1.806 | 0.0067 | 0.570 | 0.000 | 15.1 | 1.996 | 0.7600 | 11.5 | 0.225 |
| P2 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3963 | 0.0130 | 0.0215 | 0.7800 | 0.2200 | 0.0000 | 1.375 | 0.0451 | 0.620 | 0.010 | 14.6 | 1.703 | 0.7200 | n/a | 0.225 |
| P2 | h10 | carried_added | 6.5167 | 6.0843 | -0.4324 | 0.3899 | 0.7600 | 0.0000 | 0.2400 | 1.889 | 1.1220 | 0.590 | 0.000 | 15.2 | 2.154 | 0.7600 | n/a | 0.225 |
| P2 | h10 | pooled_retention | 0.6000 | 0.5601 | -0.0399 | 0.0359 | 0.7700 | 0.0000 | 0.2300 | 1.872 | 0.1029 | 0.560 | 0.000 | 15.1 | 2.336 | 0.7700 | 154.0 | 0.225 |
| P3 | n20 | large | -0.0593 | -0.0596 | -0.0003 | 0.0585 | 0.9100 | 0.0100 | 0.0800 | 1.144 | 0.1297 | 0.690 | 0.020 | 14.1 | 1.257 | 0.8600 | n/a | n/a |
| P3 | n20 | carries | 0.9000 | 0.9002 | 0.0002 | 0.0981 | 0.9000 | 0.0000 | 0.1000 | 1.101 | 0.2101 | 0.680 | 0.020 | 14.2 | 1.549 | 0.8500 | 9.8 | n/a |
| P3 | n20 | depends | 0.8550 | 0.8576 | 0.0026 | 0.1417 | 0.8900 | 0.0000 | 0.1100 | 1.105 | 0.3089 | 0.680 | 0.020 | 14.2 | 1.577 | 0.8500 | 14.3 | n/a |
| P3 | n20 | carried_margin | 0.3500 | 0.3496 | -0.0003 | 0.0536 | 0.8900 | 0.0000 | 0.1100 | 1.164 | 0.1204 | 0.540 | 0.010 | 14.7 | 2.453 | 0.8800 | n/a | n/a |
| P3 | n20 | own_margin | 0.4093 | 0.4093 | -0.0000 | 0.0291 | 0.9300 | 0.0000 | 0.0700 | 1.137 | 0.0622 | 0.650 | 0.070 | 13.3 | 1.536 | 0.8700 | n/a | n/a |
| P3 | n20 | kappa | 0.6552 | 0.6585 | 0.0033 | 0.0530 | 0.9200 | 0.0800 | 0.0000 | 0.944 | 0.1132 | 0.550 | 0.000 | 15.3 | 1.348 | 0.9100 | 7.0 | n/a |
| P3 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4093 | 0.0000 | 0.0291 | 0.9300 | 0.0700 | 0.0000 | 1.137 | 0.0622 | 0.650 | 0.070 | 13.3 | 1.536 | 0.8700 | n/a | n/a |
| P3 | n20 | carried_added | 0.5341 | 0.5316 | -0.0025 | 0.0732 | 0.9100 | 0.0000 | 0.0900 | 1.103 | 0.1648 | 0.540 | 0.000 | 15.3 | 1.437 | 0.9100 | n/a | n/a |
| P3 | n20 | pooled_retention | 0.9000 | 0.8949 | -0.0051 | 0.0910 | 0.8500 | 0.0100 | 0.1400 | 0.957 | 0.1878 | 0.560 | 0.000 | 15.1 | 3.060 | 0.8500 | 9.9 | n/a |
| P3 | n40 | large | 1.1603 | 1.1408 | -0.0195 | 0.2245 | 0.9200 | 0.0000 | 0.0800 | 1.005 | 0.4751 | 0.620 | 0.000 | 15.0 | 1.217 | 0.9200 | n/a | n/a |
| P3 | n40 | carries | 0.9000 | 0.8962 | -0.0038 | 0.1297 | 0.9500 | 0.0100 | 0.0400 | 0.947 | 0.2673 | 0.470 | 0.000 | 14.3 | 1.001 | 0.8600 | 9.3 | n/a |
| P3 | n40 | depends | 0.8896 | 0.8868 | -0.0028 | 0.1424 | 0.9400 | 0.0100 | 0.0500 | 0.949 | 0.2921 | 0.480 | 0.010 | 14.3 | 1.022 | 0.8600 | 9.4 | n/a |
| P3 | n40 | carried_margin | 1.5696 | 1.5501 | -0.0195 | 0.2312 | 0.9300 | 0.0000 | 0.0700 | 1.002 | 0.4922 | 0.640 | 0.000 | 15.1 | 1.159 | 0.9100 | n/a | n/a |
| P3 | n40 | own_margin | 1.7645 | 1.7600 | -0.0045 | 0.1887 | 0.9300 | 0.0000 | 0.0700 | 1.000 | 0.4079 | 0.560 | 0.000 | 14.3 | 1.220 | 0.8800 | n/a | n/a |
| P3 | n40 | kappa | 0.8950 | 0.8951 | 0.0001 | 0.0156 | 0.9400 | 0.0600 | 0.0000 | 1.118 | 0.0360 | 0.610 | 0.000 | 15.2 | 1.022 | 0.9400 | 6.8 | n/a |
| P3 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4093 | 0.0000 | 0.0290 | 0.9300 | 0.0700 | 0.0000 | 1.146 | 0.0623 | 0.640 | 0.070 | 13.3 | 1.680 | 0.8700 | n/a | n/a |
| P3 | n40 | carried_added | 1.7538 | 1.7321 | -0.0217 | 0.2589 | 0.9000 | 0.0000 | 0.1000 | 0.979 | 0.5500 | 0.640 | 0.000 | 15.2 | 1.157 | 0.8800 | n/a | n/a |
| P3 | n40 | pooled_retention | 0.9000 | 0.8947 | -0.0053 | 0.0901 | 0.8600 | 0.0000 | 0.1400 | 0.981 | 0.1871 | 0.480 | 0.000 | 15.1 | 2.859 | 0.8500 | 9.4 | n/a |
| P3 | n80 | large | 8.1937 | 8.1586 | -0.0351 | 1.1013 | 0.9100 | 0.0000 | 0.0900 | 1.030 | 2.3761 | 0.580 | 0.030 | 13.9 | 1.254 | 0.8900 | n/a | n/a |
| P3 | n80 | carries | 0.9000 | 0.9011 | 0.0011 | 0.1378 | 0.9300 | 0.0000 | 0.0700 | 1.219 | 0.3292 | 0.600 | 0.050 | 13.2 | 1.121 | 0.9000 | 12.3 | n/a |
| P3 | n80 | depends | 0.8981 | 0.8997 | 0.0016 | 0.1403 | 0.9300 | 0.0000 | 0.0700 | 1.224 | 0.3341 | 0.590 | 0.050 | 13.2 | 1.121 | 0.9000 | 12.1 | n/a |
| P3 | n80 | carried_margin | 8.6030 | 8.5678 | -0.0352 | 1.1118 | 0.9100 | 0.0000 | 0.0900 | 1.031 | 2.4176 | 0.590 | 0.030 | 13.9 | 1.219 | 0.8900 | n/a | n/a |
| P3 | n80 | own_margin | 9.5794 | 9.5852 | 0.0058 | 0.7203 | 0.9800 | 0.0100 | 0.0100 | 1.366 | 1.7628 | 0.590 | 0.120 | 12.4 | 0.814 | 0.9200 | n/a | n/a |
| P3 | n80 | kappa | 0.9790 | 0.9793 | 0.0003 | 0.0028 | 0.9000 | 0.0900 | 0.0100 | 1.138 | 0.0063 | 0.600 | 0.010 | 14.3 | 1.315 | 0.8700 | 7.7 | n/a |
| P3 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4092 | 0.0001 | 0.0291 | 0.9300 | 0.0700 | 0.0000 | 1.138 | 0.0618 | 0.640 | 0.070 | 13.3 | 1.526 | 0.8700 | n/a | n/a |
| P3 | n80 | carried_added | 8.7872 | 8.7498 | -0.0374 | 1.1445 | 0.9100 | 0.0000 | 0.0900 | 1.024 | 2.4810 | 0.590 | 0.030 | 14.0 | 1.270 | 0.8900 | n/a | n/a |
| P3 | n80 | pooled_retention | 0.9000 | 0.8944 | -0.0056 | 0.0887 | 0.8700 | 0.0000 | 0.1300 | 1.008 | 0.1869 | 0.480 | 0.000 | 15.1 | 2.693 | 0.8600 | 12.9 | n/a |
| P3 | n160 | large | 19.2943 | 19.1881 | -0.1062 | 2.2051 | 0.9100 | 0.0000 | 0.0900 | 1.077 | 4.7468 | 0.620 | 0.000 | 14.7 | 1.183 | 0.9000 | n/a | n/a |
| P3 | n160 | carries | 0.9000 | 0.8940 | -0.0060 | 0.1299 | 0.9100 | 0.0000 | 0.0900 | 1.266 | 0.2991 | 0.620 | 0.010 | 14.7 | 1.717 | 0.8900 | 16.3 | n/a |
| P3 | n160 | depends | 0.8992 | 0.8934 | -0.0058 | 0.1310 | 0.9100 | 0.0000 | 0.0900 | 1.269 | 0.3007 | 0.620 | 0.010 | 14.7 | 1.717 | 0.8900 | 15.9 | n/a |
| P3 | n160 | carried_margin | 19.7036 | 19.5973 | -0.1063 | 2.2180 | 0.9100 | 0.0000 | 0.0900 | 1.076 | 4.7907 | 0.620 | 0.000 | 14.7 | 1.213 | 0.9000 | n/a | n/a |
| P3 | n160 | own_margin | 21.9134 | 22.0557 | 0.1424 | 1.1133 | 0.9600 | 0.0400 | 0.0000 | 1.577 | 2.9760 | 0.570 | 0.050 | 12.6 | 0.914 | 0.9400 | n/a | n/a |
| P3 | n160 | kappa | 0.9907 | 0.9909 | 0.0001 | 0.0012 | 0.8800 | 0.1100 | 0.0100 | 1.008 | 0.0027 | 0.600 | 0.000 | 15.0 | 1.486 | 0.8600 | 8.6 | n/a |
| P3 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4091 | 0.0002 | 0.0290 | 0.9300 | 0.0700 | 0.0000 | 1.143 | 0.0619 | 0.640 | 0.070 | 13.2 | 1.496 | 0.8700 | n/a | n/a |
| P3 | n160 | carried_added | 19.8878 | 19.7794 | -0.1084 | 2.2533 | 0.9100 | 0.0000 | 0.0900 | 1.073 | 4.8576 | 0.620 | 0.000 | 14.7 | 1.237 | 0.9000 | n/a | n/a |
| P3 | n160 | pooled_retention | 0.9000 | 0.8945 | -0.0055 | 0.0894 | 0.8700 | 0.0000 | 0.1300 | 0.978 | 0.1849 | 0.430 | 0.000 | 15.1 | 2.789 | 0.8500 | 15.7 | n/a |
| P3 | n320 | large | 22.3102 | 22.3313 | 0.0211 | 2.5939 | 0.9400 | 0.0000 | 0.0600 | 1.025 | 5.4383 | 0.530 | 0.020 | 14.7 | 1.213 | 0.9000 | n/a | n/a |
| P3 | n320 | carries | 0.9000 | 0.9027 | 0.0027 | 0.1349 | 0.9400 | 0.0000 | 0.0600 | 1.161 | 0.2910 | 0.590 | 0.020 | 14.6 | 1.245 | 0.8900 | 17.9 | n/a |
| P3 | n320 | depends | 0.8993 | 0.9022 | 0.0029 | 0.1358 | 0.9400 | 0.0000 | 0.0600 | 1.164 | 0.2931 | 0.590 | 0.020 | 14.6 | 1.249 | 0.8900 | 17.4 | n/a |
| P3 | n320 | carried_margin | 22.7195 | 22.7404 | 0.0210 | 2.6063 | 0.9400 | 0.0000 | 0.0600 | 1.025 | 5.4672 | 0.550 | 0.020 | 14.7 | 1.215 | 0.9000 | n/a | n/a |
| P3 | n320 | own_margin | 25.2643 | 25.3507 | 0.0863 | 1.2530 | 0.9600 | 0.0400 | 0.0000 | 1.397 | 3.0941 | 0.580 | 0.060 | 12.9 | 0.940 | 0.8900 | n/a | n/a |
| P3 | n320 | kappa | 0.9920 | 0.9921 | 0.0002 | 0.0010 | 0.8700 | 0.1200 | 0.0100 | 1.011 | 0.0022 | 0.520 | 0.010 | 15.1 | 1.537 | 0.8500 | 8.7 | n/a |
| P3 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4091 | 0.0002 | 0.0290 | 0.9300 | 0.0700 | 0.0000 | 1.144 | 0.0619 | 0.660 | 0.070 | 13.4 | 1.685 | 0.8700 | n/a | n/a |
| P3 | n320 | carried_added | 22.9037 | 22.9226 | 0.0189 | 2.6419 | 0.9400 | 0.0000 | 0.0600 | 1.023 | 5.5398 | 0.550 | 0.020 | 14.7 | 1.212 | 0.9000 | n/a | n/a |
| P3 | n320 | pooled_retention | 0.9000 | 0.8954 | -0.0046 | 0.0898 | 0.8700 | 0.0000 | 0.1300 | 0.981 | 0.1863 | 0.550 | 0.000 | 15.1 | 2.879 | 0.8600 | 16.9 | n/a |
| P3 | h2 | large | 1.1253 | 1.1191 | -0.0062 | 0.1218 | 0.8700 | 0.0000 | 0.1300 | 0.946 | 0.2414 | 0.660 | 0.000 | 15.1 | 2.053 | 0.8500 | n/a | 1.000 |
| P3 | h2 | carries | 0.9000 | 0.8953 | -0.0047 | 0.0853 | 0.8600 | 0.0000 | 0.1400 | 0.959 | 0.1765 | 0.640 | 0.000 | 15.1 | 2.808 | 0.8500 | 121.2 | 1.000 |
| P3 | h2 | depends | 0.8893 | 0.8864 | -0.0029 | 0.0930 | 0.8600 | 0.0000 | 0.1400 | 0.984 | 0.1896 | 0.640 | 0.000 | 15.1 | 2.877 | 0.8500 | 57.8 | 1.000 |
| P3 | h2 | carried_margin | 1.5346 | 1.5283 | -0.0063 | 0.1331 | 0.8600 | 0.0000 | 0.1400 | 0.966 | 0.2766 | 0.620 | 0.000 | 15.1 | 2.615 | 0.8500 | n/a | 1.000 |
| P3 | h2 | own_margin | 1.7255 | 1.7272 | 0.0017 | 0.0312 | 0.8800 | 0.1200 | 0.0000 | 0.999 | 0.0638 | 0.580 | 0.000 | 15.1 | 1.359 | 0.8700 | n/a | 1.000 |
| P3 | h2 | kappa | 0.8928 | 0.8948 | 0.0020 | 0.0127 | 0.8700 | 0.1200 | 0.0100 | 0.903 | 0.0267 | 0.620 | 0.000 | 15.0 | 2.262 | 0.8500 | 10.2 | 1.000 |
| P3 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4092 | 0.0001 | 0.0290 | 0.9300 | 0.0700 | 0.0000 | 1.146 | 0.0634 | 0.670 | 0.070 | 13.3 | 1.692 | 0.8700 | n/a | 1.000 |
| P3 | h2 | carried_added | 1.7188 | 1.7103 | -0.0084 | 0.1732 | 0.8700 | 0.0000 | 0.1300 | 0.964 | 0.3593 | 0.610 | 0.000 | 15.1 | 2.882 | 0.8600 | n/a | 1.000 |
| P3 | h2 | pooled_retention | 0.9000 | 0.8956 | -0.0044 | 0.0900 | 0.8600 | 0.0000 | 0.1400 | 0.972 | 0.1883 | 0.670 | 0.000 | 15.1 | 2.941 | 0.8400 | 121.0 | 1.000 |
| P3 | h5 | large | 4.0046 | 3.9803 | -0.0243 | 0.4031 | 0.8600 | 0.0000 | 0.1400 | 0.991 | 0.8418 | 0.600 | 0.000 | 15.2 | 2.716 | 0.8500 | n/a | 1.000 |
| P3 | h5 | carries | 0.9000 | 0.8947 | -0.0053 | 0.0920 | 0.8700 | 0.0000 | 0.1300 | 0.995 | 0.1940 | 0.560 | 0.000 | 15.2 | 2.973 | 0.8600 | 168.8 | 1.000 |
| P3 | h5 | depends | 0.8963 | 0.8916 | -0.0046 | 0.0950 | 0.8700 | 0.0000 | 0.1300 | 1.005 | 0.1988 | 0.560 | 0.000 | 15.2 | 3.012 | 0.8600 | 77.9 | 1.000 |
| P3 | h5 | carried_margin | 4.4139 | 4.3893 | -0.0246 | 0.4162 | 0.8700 | 0.0000 | 0.1300 | 0.998 | 0.8788 | 0.550 | 0.000 | 15.2 | 2.883 | 0.8600 | n/a | 1.000 |
| P3 | h5 | own_margin | 4.9248 | 4.9287 | 0.0039 | 0.0612 | 0.9200 | 0.0800 | 0.0000 | 1.010 | 0.1358 | 0.570 | 0.020 | 13.8 | 1.248 | 0.8700 | n/a | 1.000 |
| P3 | h5 | kappa | 0.9599 | 0.9607 | 0.0007 | 0.0048 | 0.8600 | 0.1300 | 0.0100 | 0.891 | 0.0098 | 0.520 | 0.000 | 15.1 | 2.214 | 0.8500 | 10.2 | 1.000 |
| P3 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4090 | 0.0003 | 0.0288 | 0.9300 | 0.0700 | 0.0000 | 1.225 | 0.0648 | 0.650 | 0.070 | 12.7 | 1.092 | 0.8700 | n/a | 1.000 |
| P3 | h5 | carried_added | 4.5981 | 4.5713 | -0.0269 | 0.4562 | 0.8700 | 0.0000 | 0.1300 | 0.995 | 0.9572 | 0.560 | 0.000 | 15.1 | 2.927 | 0.8600 | n/a | 1.000 |
| P3 | h5 | pooled_retention | 0.9000 | 0.8951 | -0.0049 | 0.0889 | 0.8700 | 0.0000 | 0.1300 | 0.998 | 0.1860 | 0.620 | 0.000 | 15.1 | 2.941 | 0.8500 | 156.3 | 1.000 |
| P3 | h10 | large | 9.1816 | 8.5135 | -0.6681 | 0.6051 | 0.7400 | 0.0000 | 0.2600 | 1.495 | 1.5615 | 0.670 | 0.000 | 15.2 | 2.726 | 0.7400 | n/a | 0.212 |
| P3 | h10 | carries | 0.9000 | 0.8348 | -0.0652 | 0.0595 | 0.7400 | 0.0000 | 0.2600 | 1.480 | 0.1544 | 0.600 | 0.000 | 15.2 | 2.934 | 0.7300 | 149.8 | 0.212 |
| P3 | h10 | depends | 0.8983 | 0.8325 | -0.0657 | 0.0600 | 0.7300 | 0.0000 | 0.2700 | 1.488 | 0.1558 | 0.600 | 0.000 | 15.2 | 2.955 | 0.7300 | 131.0 | 0.212 |
| P3 | h10 | carried_margin | 9.5909 | 8.9067 | -0.6842 | 0.6073 | 0.7400 | 0.0000 | 0.2600 | 1.517 | 1.5883 | 0.600 | 0.000 | 15.2 | 2.776 | 0.7400 | n/a | 0.212 |
| P3 | h10 | own_margin | 10.6772 | 10.7013 | 0.0241 | 0.0777 | 0.9700 | 0.0300 | 0.0000 | 1.523 | 0.1782 | 0.560 | 0.270 | 10.5 | 0.883 | 0.8900 | n/a | 0.212 |
| P3 | h10 | kappa | 0.9812 | 0.9830 | 0.0019 | 0.0017 | 0.7500 | 0.2500 | 0.0000 | 1.353 | 0.0043 | 0.580 | 0.000 | 15.2 | 2.463 | 0.7400 | 11.7 | 0.212 |
| P3 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3932 | 0.0161 | 0.0214 | 0.8000 | 0.2000 | 0.0000 | 1.218 | 0.0474 | 0.580 | 0.090 | 13.5 | 1.950 | 0.6900 | n/a | 0.212 |
| P3 | h10 | carried_added | 9.7751 | 9.0616 | -0.7134 | 0.6326 | 0.7400 | 0.0000 | 0.2600 | 1.517 | 1.6539 | 0.610 | 0.000 | 15.2 | 2.822 | 0.7300 | n/a | 0.212 |
| P3 | h10 | pooled_retention | 0.9000 | 0.8349 | -0.0651 | 0.0582 | 0.7300 | 0.0000 | 0.2700 | 1.509 | 0.1529 | 0.530 | 0.000 | 15.1 | 2.990 | 0.7300 | 148.1 | 0.212 |
| P4 | n20 | large | -0.4818 | -0.4902 | -0.0084 | 0.0689 | 0.8900 | 0.1100 | 0.0000 | 0.944 | 0.1429 | 0.200 | 0.250 | 10.3 | 1.506 | 0.7800 | n/a | n/a |
| P4 | n20 | carries | 0.2000 | 0.1978 | -0.0022 | 0.0206 | 0.8600 | 0.0000 | 0.1400 | 1.237 | 0.0479 | 0.580 | 0.020 | 13.8 | 2.656 | 0.8400 | 8.4 | n/a |
| P4 | n20 | depends | -0.1524 | -0.1587 | -0.0062 | 0.0818 | 0.9500 | 0.0500 | 0.0000 | 0.966 | 0.1609 | 0.050 | 0.040 | 15.0 | 0.959 | 0.8700 | 9.0 | n/a |
| P4 | n20 | carried_margin | -0.0637 | -0.0664 | -0.0027 | 0.0332 | 0.9200 | 0.0800 | 0.0000 | 0.990 | 0.0696 | 0.170 | 0.010 | 15.7 | 1.194 | 0.8700 | n/a | n/a |
| P4 | n20 | own_margin | 0.4181 | 0.4238 | 0.0057 | 0.0580 | 0.9700 | 0.0100 | 0.0200 | 0.923 | 0.1415 | 0.060 | 0.710 | 5.6 | 0.897 | 0.5700 | n/a | n/a |
| P4 | n20 | kappa | -0.5291 | -0.5562 | -0.0271 | 0.2751 | 0.9400 | 0.0500 | 0.0100 | 0.849 | 0.5441 | 0.170 | 0.030 | 15.1 | 1.103 | 0.9000 | 6.7 | n/a |
| P4 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4238 | -0.0057 | 0.0580 | 0.9700 | 0.0200 | 0.0100 | 0.923 | 0.1415 | 0.060 | 0.710 | 5.6 | 0.897 | 0.5700 | n/a | n/a |
| P4 | n20 | carried_added | 0.1205 | 0.1209 | 0.0005 | 0.0215 | 0.8800 | 0.0100 | 0.1100 | 0.833 | 0.0391 | 0.140 | 0.060 | 14.5 | 1.582 | 0.8200 | n/a | n/a |
| P4 | n20 | pooled_retention | 0.2000 | 0.2017 | 0.0017 | 0.0211 | 0.8800 | 0.0000 | 0.1200 | 0.960 | 0.0445 | 0.730 | 0.000 | 15.0 | 2.190 | 0.8700 | 8.6 | n/a |
| P4 | n40 | large | -0.2046 | -0.2139 | -0.0093 | 0.0571 | 0.9500 | 0.0300 | 0.0200 | 1.069 | 0.1227 | 0.400 | 0.080 | 12.8 | 0.905 | 0.9200 | n/a | n/a |
| P4 | n40 | carries | 0.2000 | 0.1999 | -0.0001 | 0.0269 | 0.9900 | 0.0000 | 0.0100 | 1.161 | 0.0618 | 0.460 | 0.020 | 13.7 | 0.877 | 0.9400 | 7.8 | n/a |
| P4 | n40 | depends | 0.1183 | 0.1168 | -0.0015 | 0.0296 | 0.9700 | 0.0000 | 0.0300 | 0.947 | 0.0606 | 0.470 | 0.030 | 13.5 | 0.951 | 0.8700 | 7.6 | n/a |
| P4 | n40 | carried_margin | 0.2135 | 0.2099 | -0.0036 | 0.0554 | 0.9200 | 0.0200 | 0.0600 | 0.890 | 0.1067 | 0.190 | 0.160 | 11.4 | 1.265 | 0.8100 | n/a | n/a |
| P4 | n40 | own_margin | 1.8041 | 1.8063 | 0.0023 | 0.2392 | 0.9600 | 0.0100 | 0.0300 | 1.050 | 0.5301 | 0.130 | 0.290 | 9.9 | 0.939 | 0.8500 | n/a | n/a |
| P4 | n40 | kappa | 0.5368 | 0.5252 | -0.0116 | 0.0930 | 0.9300 | 0.0600 | 0.0100 | 0.798 | 0.1718 | 0.190 | 0.050 | 14.3 | 1.090 | 0.8800 | 6.4 | n/a |
| P4 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4238 | -0.0057 | 0.0583 | 0.9700 | 0.0200 | 0.0100 | 0.917 | 0.1409 | 0.070 | 0.710 | 5.6 | 0.912 | 0.5600 | n/a | n/a |
| P4 | n40 | carried_added | 0.3976 | 0.3972 | -0.0004 | 0.0664 | 0.9400 | 0.0000 | 0.0600 | 0.983 | 0.1350 | 0.190 | 0.060 | 13.9 | 1.072 | 0.8500 | n/a | n/a |
| P4 | n40 | pooled_retention | 0.2000 | 0.2018 | 0.0018 | 0.0210 | 0.8800 | 0.0000 | 0.1200 | 0.970 | 0.0429 | 0.710 | 0.000 | 15.0 | 2.330 | 0.8700 | 8.4 | n/a |
| P4 | n80 | large | 1.3720 | 1.3804 | 0.0084 | 0.2672 | 0.9400 | 0.0000 | 0.0600 | 1.123 | 0.6357 | 0.190 | 0.310 | 9.3 | 1.075 | 0.8300 | n/a | n/a |
| P4 | n80 | carries | 0.2000 | 0.2036 | 0.0036 | 0.0330 | 0.9500 | 0.0100 | 0.0400 | 1.112 | 0.0689 | 0.710 | 0.030 | 13.5 | 1.040 | 0.9100 | 7.6 | n/a |
| P4 | n80 | depends | 0.1848 | 0.1879 | 0.0031 | 0.0302 | 0.9500 | 0.0100 | 0.0400 | 1.145 | 0.0636 | 0.700 | 0.050 | 13.4 | 0.935 | 0.9200 | 7.3 | n/a |
| P4 | n80 | carried_margin | 1.7901 | 1.8041 | 0.0141 | 0.3053 | 0.9600 | 0.0000 | 0.0400 | 1.070 | 0.6942 | 0.120 | 0.390 | 8.3 | 0.920 | 0.8000 | n/a | n/a |
| P4 | n80 | own_margin | 9.6872 | 9.6790 | -0.0082 | 1.3662 | 0.9500 | 0.0200 | 0.0300 | 0.953 | 3.8296 | 0.130 | 0.730 | 6.1 | 0.977 | 0.7100 | n/a | n/a |
| P4 | n80 | kappa | 0.9067 | 0.9055 | -0.0012 | 0.0173 | 0.9600 | 0.0300 | 0.0100 | 0.946 | 0.0352 | 0.120 | 0.280 | 10.2 | 0.978 | 0.8600 | 6.3 | n/a |
| P4 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4238 | -0.0057 | 0.0581 | 0.9700 | 0.0200 | 0.0100 | 0.920 | 0.1420 | 0.060 | 0.710 | 5.6 | 0.917 | 0.5700 | n/a | n/a |
| P4 | n80 | carried_added | 1.9743 | 1.9915 | 0.0172 | 0.3296 | 0.9500 | 0.0000 | 0.0500 | 1.057 | 0.7317 | 0.120 | 0.300 | 9.3 | 0.941 | 0.8300 | n/a | n/a |
| P4 | n80 | pooled_retention | 0.2000 | 0.2019 | 0.0019 | 0.0213 | 0.8800 | 0.0000 | 0.1200 | 0.947 | 0.0422 | 0.840 | 0.000 | 15.0 | 2.324 | 0.8700 | 8.2 | n/a |
| P4 | n160 | large | 3.7326 | 3.7860 | 0.0534 | 0.4402 | 0.9600 | 0.0000 | 0.0400 | 1.207 | 1.0581 | 0.560 | 0.000 | 14.7 | 0.910 | 0.9200 | n/a | n/a |
| P4 | n160 | carries | 0.2000 | 0.2049 | 0.0049 | 0.0312 | 0.9000 | 0.0000 | 0.1000 | 1.232 | 0.0710 | 0.530 | 0.000 | 14.8 | 1.406 | 0.8900 | 15.7 | n/a |
| P4 | n160 | depends | 0.1931 | 0.1980 | 0.0048 | 0.0297 | 0.9000 | 0.0000 | 0.1000 | 1.249 | 0.0684 | 0.520 | 0.000 | 14.7 | 1.159 | 0.9000 | 15.2 | n/a |
| P4 | n160 | carried_margin | 4.1507 | 4.2098 | 0.0592 | 0.4624 | 0.9400 | 0.0000 | 0.0600 | 1.173 | 1.0881 | 0.490 | 0.000 | 14.5 | 1.067 | 0.9200 | n/a | n/a |
| P4 | n160 | own_margin | 21.4901 | 21.4103 | -0.0797 | 1.2311 | 0.9600 | 0.0300 | 0.0100 | 1.384 | 3.0631 | 0.510 | 0.120 | 11.6 | 0.896 | 0.9200 | n/a | n/a |
| P4 | n160 | kappa | 0.9575 | 0.9578 | 0.0003 | 0.0058 | 0.8800 | 0.1100 | 0.0100 | 0.932 | 0.0122 | 0.500 | 0.000 | 15.0 | 1.700 | 0.8700 | 8.2 | n/a |
| P4 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4238 | -0.0057 | 0.0581 | 0.9700 | 0.0200 | 0.0100 | 0.922 | 0.1412 | 0.070 | 0.710 | 5.5 | 0.897 | 0.5600 | n/a | n/a |
| P4 | n160 | carried_added | 4.3349 | 4.3972 | 0.0623 | 0.4995 | 0.9400 | 0.0000 | 0.0600 | 1.147 | 1.1568 | 0.490 | 0.000 | 14.8 | 1.077 | 0.9000 | n/a | n/a |
| P4 | n160 | pooled_retention | 0.2000 | 0.2016 | 0.0016 | 0.0212 | 0.8800 | 0.0000 | 0.1200 | 0.952 | 0.0429 | 0.600 | 0.000 | 15.1 | 2.369 | 0.8700 | 16.8 | n/a |
| P4 | n320 | large | 4.4340 | 4.4910 | 0.0570 | 0.5362 | 0.9100 | 0.0000 | 0.0900 | 1.062 | 1.1709 | 0.600 | 0.000 | 14.8 | 1.112 | 0.8900 | n/a | n/a |
| P4 | n320 | carries | 0.2000 | 0.2039 | 0.0039 | 0.0324 | 0.8900 | 0.0000 | 0.1100 | 1.113 | 0.0706 | 0.640 | 0.000 | 14.8 | 1.531 | 0.8800 | 17.1 | n/a |
| P4 | n320 | depends | 0.1941 | 0.1980 | 0.0039 | 0.0311 | 0.8900 | 0.0000 | 0.1100 | 1.119 | 0.0682 | 0.640 | 0.000 | 14.8 | 1.422 | 0.8800 | 16.5 | n/a |
| P4 | n320 | carried_margin | 4.8521 | 4.9148 | 0.0626 | 0.5533 | 0.9200 | 0.0000 | 0.0800 | 1.050 | 1.2120 | 0.610 | 0.000 | 14.9 | 1.173 | 0.9000 | n/a | n/a |
| P4 | n320 | own_margin | 24.9973 | 25.0031 | 0.0058 | 1.3081 | 0.9500 | 0.0500 | 0.0000 | 1.401 | 3.2985 | 0.590 | 0.070 | 12.5 | 0.933 | 0.9200 | n/a | n/a |
| P4 | n320 | kappa | 0.9634 | 0.9636 | 0.0002 | 0.0049 | 0.8800 | 0.1100 | 0.0100 | 0.926 | 0.0104 | 0.590 | 0.000 | 15.1 | 1.478 | 0.8800 | 8.4 | n/a |
| P4 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4237 | -0.0056 | 0.0581 | 0.9700 | 0.0200 | 0.0100 | 0.921 | 0.1412 | 0.070 | 0.720 | 5.5 | 0.881 | 0.5700 | n/a | n/a |
| P4 | n320 | carried_added | 5.0363 | 5.1022 | 0.0659 | 0.5908 | 0.9200 | 0.0000 | 0.0800 | 1.039 | 1.2862 | 0.610 | 0.000 | 15.0 | 1.259 | 0.8900 | n/a | n/a |
| P4 | n320 | pooled_retention | 0.2000 | 0.2018 | 0.0018 | 0.0212 | 0.8800 | 0.0000 | 0.1200 | 0.949 | 0.0437 | 0.540 | 0.000 | 15.1 | 2.300 | 0.8700 | 17.8 | n/a |
| P4 | h2 | large | -0.2198 | -0.2259 | -0.0061 | 0.0580 | 0.9500 | 0.0400 | 0.0100 | 0.930 | 0.1396 | 0.080 | 0.680 | 5.9 | 0.873 | 0.6200 | n/a | 1.000 |
| P4 | h2 | carries | 0.2000 | 0.2010 | 0.0010 | 0.0197 | 0.8800 | 0.0000 | 0.1200 | 0.970 | 0.0399 | 0.570 | 0.000 | 15.1 | 2.247 | 0.8700 | 116.1 | 1.000 |
| P4 | h2 | depends | 0.1148 | 0.1145 | -0.0003 | 0.0024 | 0.9900 | 0.0000 | 0.0100 | 2.112 | 0.0071 | 0.510 | 0.010 | 13.8 | 0.648 | 0.9800 | 54.0 | 1.000 |
| P4 | h2 | carried_margin | 0.1985 | 0.1979 | -0.0007 | 0.0049 | 1.0000 | 0.0000 | 0.0000 | 1.667 | 0.0127 | 0.490 | 0.000 | 14.2 | 0.650 | 0.9900 | n/a | 1.000 |
| P4 | h2 | own_margin | 1.7295 | 1.7283 | -0.0011 | 0.0322 | 0.9200 | 0.0800 | 0.0000 | 1.044 | 0.0688 | 0.480 | 0.010 | 15.1 | 1.078 | 0.8900 | n/a | 1.000 |
| P4 | h2 | kappa | 0.5187 | 0.5197 | 0.0010 | 0.0601 | 0.8700 | 0.1200 | 0.0100 | 0.842 | 0.1217 | 0.510 | 0.000 | 15.1 | 2.060 | 0.8700 | 9.9 | 1.000 |
| P4 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4238 | -0.0054 | 0.0581 | 0.9700 | 0.0200 | 0.0100 | 0.922 | 0.1402 | 0.060 | 0.720 | 5.6 | 0.902 | 0.5700 | n/a | 1.000 |
| P4 | h2 | carried_added | 0.3827 | 0.3853 | 0.0025 | 0.0403 | 0.8800 | 0.0000 | 0.1200 | 0.965 | 0.0809 | 0.480 | 0.000 | 15.1 | 2.305 | 0.8700 | n/a | 1.000 |
| P4 | h2 | pooled_retention | 0.2000 | 0.2015 | 0.0015 | 0.0209 | 0.8800 | 0.0000 | 0.1200 | 0.976 | 0.0419 | 0.510 | 0.000 | 15.1 | 2.281 | 0.8700 | 114.5 | 1.000 |
| P4 | h5 | large | 0.4217 | 0.4235 | 0.0019 | 0.0689 | 0.9600 | 0.0000 | 0.0400 | 1.123 | 0.1635 | 0.160 | 0.330 | 9.4 | 0.909 | 0.8100 | n/a | 0.990 |
| P4 | h5 | carries | 0.2000 | 0.2022 | 0.0022 | 0.0219 | 0.8800 | 0.0000 | 0.1200 | 0.955 | 0.0450 | 0.520 | 0.000 | 15.1 | 2.177 | 0.8700 | 149.7 | 0.990 |
| P4 | h5 | depends | 0.1702 | 0.1720 | 0.0019 | 0.0156 | 0.8800 | 0.0000 | 0.1200 | 0.974 | 0.0320 | 0.520 | 0.000 | 15.2 | 1.916 | 0.8700 | 81.3 | 0.990 |
| P4 | h5 | carried_margin | 0.8400 | 0.8480 | 0.0080 | 0.0678 | 0.8900 | 0.0000 | 0.1100 | 0.946 | 0.1370 | 0.490 | 0.000 | 15.2 | 1.881 | 0.8600 | n/a | 0.990 |
| P4 | h5 | own_margin | 4.9368 | 4.9343 | -0.0024 | 0.0608 | 0.9600 | 0.0400 | 0.0000 | 1.126 | 0.1381 | 0.560 | 0.020 | 13.4 | 0.936 | 0.8900 | n/a | 0.990 |
| P4 | h5 | kappa | 0.8202 | 0.8214 | 0.0012 | 0.0221 | 0.8700 | 0.1200 | 0.0100 | 0.861 | 0.0449 | 0.510 | 0.000 | 15.1 | 2.013 | 0.8700 | 9.6 | 0.990 |
| P4 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4244 | -0.0061 | 0.0584 | 0.9600 | 0.0300 | 0.0100 | 1.004 | 0.1553 | 0.120 | 0.740 | 5.3 | 0.904 | 0.5700 | n/a | 0.990 |
| P4 | h5 | carried_added | 1.0242 | 1.0353 | 0.0111 | 0.1100 | 0.8800 | 0.0000 | 0.1200 | 0.941 | 0.2246 | 0.500 | 0.000 | 15.2 | 2.177 | 0.8700 | n/a | 0.990 |
| P4 | h5 | pooled_retention | 0.2000 | 0.2019 | 0.0019 | 0.0212 | 0.8800 | 0.0000 | 0.1200 | 0.960 | 0.0439 | 0.610 | 0.000 | 15.1 | 2.286 | 0.8700 | 150.8 | 0.990 |
| P4 | h10 | large | 1.5769 | 1.4825 | -0.0944 | 0.1204 | 0.8000 | 0.0000 | 0.2000 | 1.397 | 0.2939 | 0.460 | 0.000 | 15.3 | 1.969 | 0.7600 | n/a | 0.190 |
| P4 | h10 | carries | 0.2000 | 0.1875 | -0.0125 | 0.0134 | 0.7700 | 0.0000 | 0.2300 | 1.602 | 0.0364 | 0.630 | 0.000 | 15.2 | 2.756 | 0.7600 | 120.9 | 0.190 |
| P4 | h10 | depends | 0.1862 | 0.1754 | -0.0108 | 0.0116 | 0.7700 | 0.0000 | 0.2300 | 1.615 | 0.0313 | 0.620 | 0.000 | 15.2 | 2.354 | 0.7500 | 113.5 | 0.190 |
| P4 | h10 | carried_margin | 1.9952 | 1.8844 | -0.1109 | 0.1170 | 0.7800 | 0.0000 | 0.2200 | 1.642 | 0.3231 | 0.490 | 0.000 | 15.2 | 2.479 | 0.7700 | n/a | 0.190 |
| P4 | h10 | own_margin | 10.7131 | 10.7451 | 0.0319 | 0.1045 | 0.9500 | 0.0500 | 0.0000 | 1.246 | 0.2135 | 0.570 | 0.290 | 10.7 | 1.006 | 0.7900 | n/a | 0.190 |
| P4 | h10 | kappa | 0.9155 | 0.9225 | 0.0070 | 0.0077 | 0.7700 | 0.2300 | 0.0000 | 1.403 | 0.0202 | 0.520 | 0.000 | 15.2 | 2.149 | 0.7700 | 11.2 | 0.190 |
| P4 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4019 | 0.0165 | 0.0422 | 0.9100 | 0.0900 | 0.0000 | 0.936 | 0.0853 | 0.010 | 0.620 | 7.9 | 1.358 | 0.5700 | n/a | 0.190 |
| P4 | h10 | carried_added | 2.1794 | 2.0439 | -0.1355 | 0.1433 | 0.7800 | 0.0000 | 0.2200 | 1.630 | 0.3941 | 0.490 | 0.000 | 15.2 | 2.548 | 0.7700 | n/a | 0.190 |
| P4 | h10 | pooled_retention | 0.2000 | 0.1876 | -0.0124 | 0.0130 | 0.7700 | 0.0000 | 0.2300 | 1.643 | 0.0359 | 0.630 | 0.000 | 15.1 | 2.566 | 0.7700 | 106.7 | 0.190 |
| P5 | n20 | large | -0.2409 | -0.2441 | -0.0032 | 0.0460 | 0.9800 | 0.0200 | 0.0000 | 1.459 | 0.1163 | 0.440 | 0.100 | 12.3 | 0.743 | 0.9000 | n/a | n/a |
| P5 | n20 | carries | 0.6000 | 0.5925 | -0.0075 | 0.0619 | 0.9000 | 0.0000 | 0.1000 | 1.270 | 0.1419 | 0.600 | 0.030 | 13.1 | 1.210 | 0.8500 | 8.4 | n/a |
| P5 | n20 | depends | 0.4238 | 0.4129 | -0.0109 | 0.0909 | 0.9100 | 0.0000 | 0.0900 | 1.219 | 0.2004 | 0.480 | 0.010 | 13.5 | 1.216 | 0.8400 | 9.3 | n/a |
| P5 | n20 | carried_margin | 0.1772 | 0.1728 | -0.0044 | 0.0464 | 0.8800 | 0.0000 | 0.1200 | 0.962 | 0.0901 | 0.100 | 0.190 | 11.2 | 1.326 | 0.7200 | n/a | n/a |
| P5 | n20 | own_margin | 0.4181 | 0.4169 | -0.0012 | 0.0523 | 0.9200 | 0.0000 | 0.0800 | 0.965 | 0.1274 | 0.100 | 0.630 | 5.4 | 1.373 | 0.6300 | n/a | n/a |
| P5 | n20 | kappa | 0.4903 | 0.4830 | -0.0073 | 0.0852 | 0.9300 | 0.0500 | 0.0200 | 0.989 | 0.1803 | 0.090 | 0.010 | 15.2 | 1.230 | 0.8900 | 6.6 | n/a |
| P5 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4169 | 0.0012 | 0.0523 | 0.9200 | 0.0800 | 0.0000 | 0.965 | 0.1274 | 0.100 | 0.630 | 5.4 | 1.373 | 0.6300 | n/a | n/a |
| P5 | n20 | carried_added | 0.3614 | 0.3560 | -0.0054 | 0.0610 | 0.8700 | 0.0000 | 0.1300 | 0.902 | 0.1142 | 0.100 | 0.020 | 14.6 | 1.318 | 0.8200 | n/a | n/a |
| P5 | n20 | pooled_retention | 0.6000 | 0.5987 | -0.0013 | 0.0577 | 0.9100 | 0.0000 | 0.0900 | 1.121 | 0.1301 | 0.760 | 0.000 | 15.0 | 1.954 | 0.9100 | 8.8 | n/a |
| P5 | n40 | large | 0.5907 | 0.5752 | -0.0155 | 0.1320 | 0.9700 | 0.0000 | 0.0300 | 1.344 | 0.3163 | 0.430 | 0.010 | 13.6 | 0.900 | 0.9400 | n/a | n/a |
| P5 | n40 | carries | 0.6000 | 0.5871 | -0.0129 | 0.0694 | 0.9800 | 0.0000 | 0.0200 | 1.531 | 0.1832 | 0.580 | 0.010 | 14.0 | 0.730 | 0.9800 | 8.0 | n/a |
| P5 | n40 | depends | 0.5592 | 0.5463 | -0.0129 | 0.0721 | 0.9800 | 0.0000 | 0.0200 | 1.590 | 0.1911 | 0.560 | 0.000 | 14.0 | 0.714 | 0.9600 | 7.9 | n/a |
| P5 | n40 | carried_margin | 1.0088 | 0.9922 | -0.0166 | 0.1559 | 0.9600 | 0.0100 | 0.0300 | 1.234 | 0.3539 | 0.150 | 0.080 | 12.5 | 0.942 | 0.8800 | n/a | n/a |
| P5 | n40 | own_margin | 1.8041 | 1.8262 | 0.0221 | 0.2465 | 0.9700 | 0.0100 | 0.0200 | 0.989 | 0.5475 | 0.140 | 0.280 | 10.0 | 0.925 | 0.8300 | n/a | n/a |
| P5 | n40 | kappa | 0.8456 | 0.8442 | -0.0014 | 0.0237 | 0.9600 | 0.0400 | 0.0000 | 1.310 | 0.0571 | 0.160 | 0.010 | 14.5 | 0.884 | 0.9200 | 6.3 | n/a |
| P5 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4170 | 0.0011 | 0.0522 | 0.9300 | 0.0700 | 0.0000 | 0.968 | 0.1269 | 0.100 | 0.620 | 5.4 | 1.475 | 0.6300 | n/a | n/a |
| P5 | n40 | carried_added | 1.1929 | 1.1753 | -0.0176 | 0.1824 | 0.9500 | 0.0100 | 0.0400 | 1.145 | 0.3950 | 0.150 | 0.050 | 13.9 | 0.997 | 0.8900 | n/a | n/a |
| P5 | n40 | pooled_retention | 0.6000 | 0.5991 | -0.0009 | 0.0582 | 0.8900 | 0.0000 | 0.1100 | 1.112 | 0.1306 | 0.740 | 0.000 | 15.0 | 2.241 | 0.8900 | 8.1 | n/a |
| P5 | n80 | large | 5.3205 | 5.3296 | 0.0091 | 0.9325 | 0.9200 | 0.0100 | 0.0700 | 1.012 | 2.0308 | 0.160 | 0.290 | 9.6 | 1.303 | 0.8000 | n/a | n/a |
| P5 | n80 | carries | 0.6000 | 0.6070 | 0.0070 | 0.0912 | 0.9500 | 0.0000 | 0.0500 | 1.282 | 0.2123 | 0.660 | 0.020 | 13.7 | 0.892 | 0.9300 | 7.8 | n/a |
| P5 | n80 | depends | 0.5924 | 0.5997 | 0.0073 | 0.0916 | 0.9500 | 0.0000 | 0.0500 | 1.289 | 0.2128 | 0.650 | 0.020 | 13.7 | 0.885 | 0.9300 | 7.6 | n/a |
| P5 | n80 | carried_margin | 5.7386 | 5.7466 | 0.0080 | 0.9691 | 0.9200 | 0.0100 | 0.0700 | 1.007 | 2.1119 | 0.120 | 0.310 | 9.3 | 1.321 | 0.7900 | n/a | n/a |
| P5 | n80 | own_margin | 9.6872 | 9.6432 | -0.0440 | 1.3149 | 0.9600 | 0.0100 | 0.0300 | 1.007 | 3.5710 | 0.060 | 0.690 | 5.7 | 0.762 | 0.6900 | n/a | n/a |
| P5 | n80 | kappa | 0.9689 | 0.9689 | 0.0000 | 0.0056 | 0.9400 | 0.0500 | 0.0100 | 1.010 | 0.0118 | 0.120 | 0.240 | 10.7 | 1.015 | 0.8400 | 6.3 | n/a |
| P5 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4170 | 0.0011 | 0.0523 | 0.9200 | 0.0800 | 0.0000 | 0.966 | 0.1270 | 0.100 | 0.610 | 5.5 | 1.443 | 0.6300 | n/a | n/a |
| P5 | n80 | carried_added | 5.9228 | 5.9297 | 0.0069 | 0.9920 | 0.9200 | 0.0100 | 0.0700 | 1.008 | 2.1462 | 0.120 | 0.300 | 9.7 | 1.280 | 0.8000 | n/a | n/a |
| P5 | n80 | pooled_retention | 0.6000 | 0.5995 | -0.0005 | 0.0576 | 0.9200 | 0.0000 | 0.0800 | 1.130 | 0.1299 | 0.820 | 0.000 | 15.1 | 2.188 | 0.9200 | 8.1 | n/a |
| P5 | n160 | large | 12.4023 | 12.4023 | 0.0000 | 1.3693 | 0.9500 | 0.0000 | 0.0500 | 1.190 | 3.1314 | 0.570 | 0.000 | 14.8 | 0.936 | 0.9200 | n/a | n/a |
| P5 | n160 | carries | 0.6000 | 0.5972 | -0.0028 | 0.0865 | 0.9200 | 0.0000 | 0.0800 | 1.296 | 0.2018 | 0.580 | 0.000 | 14.7 | 1.055 | 0.9200 | 16.1 | n/a |
| P5 | n160 | depends | 0.5966 | 0.5940 | -0.0026 | 0.0865 | 0.9300 | 0.0000 | 0.0700 | 1.302 | 0.2018 | 0.580 | 0.000 | 14.7 | 1.056 | 0.9200 | 15.7 | n/a |
| P5 | n160 | carried_margin | 12.8204 | 12.8193 | -0.0011 | 1.3864 | 0.9500 | 0.0000 | 0.0500 | 1.188 | 3.1794 | 0.560 | 0.000 | 14.8 | 0.965 | 0.9100 | n/a | n/a |
| P5 | n160 | own_margin | 21.4901 | 21.7186 | 0.2285 | 1.2351 | 0.9500 | 0.0400 | 0.0100 | 1.290 | 3.0348 | 0.580 | 0.110 | 12.7 | 0.968 | 0.9000 | n/a | n/a |
| P5 | n160 | kappa | 0.9858 | 0.9860 | 0.0002 | 0.0018 | 0.9200 | 0.0800 | 0.0000 | 1.042 | 0.0040 | 0.570 | 0.000 | 15.1 | 1.587 | 0.9100 | 8.6 | n/a |
| P5 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4170 | 0.0011 | 0.0522 | 0.9200 | 0.0800 | 0.0000 | 0.970 | 0.1271 | 0.100 | 0.610 | 5.5 | 1.429 | 0.6300 | n/a | n/a |
| P5 | n160 | carried_added | 13.0046 | 13.0024 | -0.0021 | 1.4209 | 0.9500 | 0.0000 | 0.0500 | 1.183 | 3.2550 | 0.560 | 0.000 | 14.8 | 0.985 | 0.9200 | n/a | n/a |
| P5 | n160 | pooled_retention | 0.6000 | 0.5980 | -0.0020 | 0.0572 | 0.9200 | 0.0000 | 0.0800 | 1.118 | 0.1273 | 0.490 | 0.000 | 15.1 | 1.976 | 0.9100 | 17.4 | n/a |
| P5 | n320 | large | 14.5066 | 14.5008 | -0.0058 | 1.6068 | 0.9500 | 0.0000 | 0.0500 | 1.129 | 3.6279 | 0.610 | 0.010 | 14.8 | 0.944 | 0.9100 | n/a | n/a |
| P5 | n320 | carries | 0.6000 | 0.5962 | -0.0038 | 0.0887 | 0.9300 | 0.0000 | 0.0700 | 1.193 | 0.1959 | 0.540 | 0.000 | 14.9 | 1.072 | 0.9000 | 17.5 | n/a |
| P5 | n320 | depends | 0.5971 | 0.5934 | -0.0036 | 0.0887 | 0.9300 | 0.0000 | 0.0700 | 1.196 | 0.1956 | 0.550 | 0.000 | 14.9 | 1.071 | 0.9000 | 17.0 | n/a |
| P5 | n320 | carried_margin | 14.9247 | 14.9177 | -0.0070 | 1.6194 | 0.9500 | 0.0000 | 0.0500 | 1.132 | 3.6484 | 0.600 | 0.010 | 14.9 | 0.938 | 0.9100 | n/a | n/a |
| P5 | n320 | own_margin | 24.9973 | 25.2980 | 0.3007 | 1.3014 | 0.9500 | 0.0400 | 0.0100 | 1.349 | 3.1426 | 0.640 | 0.080 | 12.8 | 0.998 | 0.9200 | n/a | n/a |
| P5 | n320 | kappa | 0.9878 | 0.9880 | 0.0002 | 0.0016 | 0.9400 | 0.0600 | 0.0000 | 1.026 | 0.0034 | 0.600 | 0.000 | 15.1 | 1.300 | 0.9100 | 8.7 | n/a |
| P5 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4169 | 0.0012 | 0.0522 | 0.9200 | 0.0800 | 0.0000 | 0.969 | 0.1278 | 0.100 | 0.630 | 5.5 | 1.513 | 0.6400 | n/a | n/a |
| P5 | n320 | carried_added | 15.1089 | 15.1009 | -0.0080 | 1.6541 | 0.9500 | 0.0000 | 0.0500 | 1.129 | 3.7316 | 0.600 | 0.010 | 14.9 | 0.936 | 0.9100 | n/a | n/a |
| P5 | n320 | pooled_retention | 0.6000 | 0.5986 | -0.0014 | 0.0576 | 0.9000 | 0.0000 | 0.1000 | 1.106 | 0.1278 | 0.510 | 0.000 | 15.1 | 2.134 | 0.9100 | 18.6 | n/a |
| P5 | h2 | large | 0.5457 | 0.5440 | -0.0016 | 0.0736 | 0.9400 | 0.0100 | 0.0500 | 1.082 | 0.1707 | 0.170 | 0.160 | 11.9 | 1.019 | 0.8700 | n/a | 1.000 |
| P5 | h2 | carries | 0.6000 | 0.5969 | -0.0031 | 0.0552 | 0.9000 | 0.0000 | 0.1000 | 1.073 | 0.1221 | 0.560 | 0.000 | 15.1 | 2.403 | 0.9000 | 112.9 | 1.000 |
| P5 | h2 | depends | 0.5574 | 0.5554 | -0.0020 | 0.0516 | 0.9000 | 0.0000 | 0.1000 | 1.111 | 0.1145 | 0.540 | 0.000 | 15.1 | 2.371 | 0.9000 | 53.6 | 1.000 |
| P5 | h2 | carried_margin | 0.9640 | 0.9609 | -0.0031 | 0.0725 | 0.9100 | 0.0000 | 0.0900 | 1.108 | 0.1597 | 0.470 | 0.000 | 15.1 | 2.262 | 0.9000 | n/a | 1.000 |
| P5 | h2 | own_margin | 1.7295 | 1.7327 | 0.0032 | 0.0333 | 0.9100 | 0.0900 | 0.0000 | 0.983 | 0.0690 | 0.460 | 0.000 | 15.2 | 1.478 | 0.8900 | n/a | 1.000 |
| P5 | h2 | kappa | 0.8396 | 0.8416 | 0.0020 | 0.0190 | 0.9200 | 0.0800 | 0.0000 | 0.966 | 0.0407 | 0.450 | 0.000 | 15.1 | 1.860 | 0.9100 | 10.0 | 1.000 |
| P5 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4169 | 0.0015 | 0.0522 | 0.9200 | 0.0800 | 0.0000 | 0.968 | 0.1272 | 0.100 | 0.650 | 5.4 | 1.349 | 0.6200 | n/a | 1.000 |
| P5 | h2 | carried_added | 1.1482 | 1.1442 | -0.0041 | 0.1113 | 0.9000 | 0.0000 | 0.1000 | 1.093 | 0.2468 | 0.510 | 0.000 | 15.1 | 2.480 | 0.9100 | n/a | 1.000 |
| P5 | h2 | pooled_retention | 0.6000 | 0.5983 | -0.0017 | 0.0573 | 0.9100 | 0.0000 | 0.0900 | 1.116 | 0.1282 | 0.560 | 0.000 | 15.1 | 2.253 | 0.9100 | 115.0 | 1.000 |
| P5 | h5 | large | 2.4701 | 2.4657 | -0.0043 | 0.2407 | 0.9300 | 0.0000 | 0.0700 | 1.157 | 0.5380 | 0.490 | 0.000 | 15.4 | 1.574 | 0.9100 | n/a | 1.000 |
| P5 | h5 | carries | 0.6000 | 0.5991 | -0.0009 | 0.0588 | 0.9000 | 0.0000 | 0.1000 | 1.120 | 0.1328 | 0.590 | 0.000 | 15.1 | 2.060 | 0.9000 | 150.7 | 1.000 |
| P5 | h5 | depends | 0.5851 | 0.5847 | -0.0004 | 0.0578 | 0.9000 | 0.0000 | 0.1000 | 1.136 | 0.1306 | 0.590 | 0.000 | 15.1 | 2.044 | 0.9000 | 79.2 | 1.000 |
| P5 | h5 | carried_margin | 2.8884 | 2.8829 | -0.0054 | 0.2525 | 0.9000 | 0.0000 | 0.1000 | 1.150 | 0.5798 | 0.610 | 0.000 | 15.1 | 1.895 | 0.8900 | n/a | 1.000 |
| P5 | h5 | own_margin | 4.9368 | 4.9360 | -0.0008 | 0.0646 | 0.9200 | 0.0600 | 0.0200 | 0.982 | 0.1321 | 0.490 | 0.040 | 13.1 | 1.166 | 0.8600 | n/a | 1.000 |
| P5 | h5 | kappa | 0.9401 | 0.9409 | 0.0009 | 0.0072 | 0.9200 | 0.0800 | 0.0000 | 0.939 | 0.0151 | 0.570 | 0.000 | 15.1 | 2.169 | 0.9100 | 9.9 | 1.000 |
| P5 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4172 | 0.0011 | 0.0523 | 0.8900 | 0.1100 | 0.0000 | 0.998 | 0.1188 | 0.150 | 0.570 | 6.2 | 1.728 | 0.6300 | n/a | 1.000 |
| P5 | h5 | carried_added | 3.0726 | 3.0661 | -0.0065 | 0.2916 | 0.9000 | 0.0000 | 0.1000 | 1.138 | 0.6654 | 0.600 | 0.000 | 15.1 | 1.985 | 0.9000 | n/a | 1.000 |
| P5 | h5 | pooled_retention | 0.6000 | 0.5984 | -0.0016 | 0.0571 | 0.9000 | 0.0000 | 0.1000 | 1.123 | 0.1282 | 0.670 | 0.000 | 15.1 | 2.034 | 0.9000 | 140.8 | 1.000 |
| P5 | h10 | large | 5.9357 | 5.5604 | -0.3753 | 0.3912 | 0.7700 | 0.0000 | 0.2300 | 1.627 | 1.0162 | 0.570 | 0.000 | 15.2 | 2.563 | 0.7700 | n/a | 0.230 |
| P5 | h10 | carries | 0.6000 | 0.5618 | -0.0382 | 0.0390 | 0.7700 | 0.0000 | 0.2300 | 1.678 | 0.1032 | 0.580 | 0.000 | 15.2 | 2.505 | 0.7500 | 123.4 | 0.230 |
| P5 | h10 | depends | 0.5931 | 0.5554 | -0.0377 | 0.0385 | 0.7700 | 0.0000 | 0.2300 | 1.684 | 0.1018 | 0.570 | 0.000 | 15.2 | 2.496 | 0.7600 | 107.3 | 0.230 |
| P5 | h10 | carried_margin | 6.3541 | 5.9617 | -0.3924 | 0.3991 | 0.7600 | 0.0000 | 0.2400 | 1.631 | 1.0423 | 0.490 | 0.000 | 15.2 | 2.606 | 0.7500 | n/a | 0.230 |
| P5 | h10 | own_margin | 10.7131 | 10.7361 | 0.0229 | 0.0950 | 0.9600 | 0.0300 | 0.0100 | 1.543 | 0.2195 | 0.550 | 0.290 | 10.6 | 0.965 | 0.8800 | n/a | 0.230 |
| P5 | h10 | kappa | 0.9718 | 0.9743 | 0.0025 | 0.0024 | 0.8000 | 0.2000 | 0.0000 | 1.554 | 0.0067 | 0.530 | 0.000 | 15.1 | 2.253 | 0.7800 | 11.6 | 0.230 |
| P5 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4013 | 0.0171 | 0.0433 | 0.8600 | 0.1400 | 0.0000 | 0.778 | 0.0865 | 0.030 | 0.600 | 8.1 | 1.448 | 0.6200 | n/a | 0.230 |
| P5 | h10 | carried_added | 6.5383 | 6.1201 | -0.4182 | 0.4244 | 0.7600 | 0.0000 | 0.2400 | 1.634 | 1.1107 | 0.480 | 0.000 | 15.2 | 2.694 | 0.7500 | n/a | 0.230 |
| P5 | h10 | pooled_retention | 0.6000 | 0.5620 | -0.0380 | 0.0381 | 0.7800 | 0.0000 | 0.2200 | 1.690 | 0.1015 | 0.560 | 0.000 | 15.2 | 2.686 | 0.7700 | 128.4 | 0.230 |
| P6 | n20 | large | -0.0602 | -0.0553 | 0.0050 | 0.0633 | 0.9400 | 0.0000 | 0.0600 | 1.074 | 0.1346 | 0.600 | 0.010 | 13.6 | 1.041 | 0.8700 | n/a | n/a |
| P6 | n20 | carries | 0.9000 | 0.9074 | 0.0074 | 0.1025 | 0.9000 | 0.0000 | 0.1000 | 1.073 | 0.2196 | 0.620 | 0.010 | 13.8 | 1.457 | 0.8700 | 8.5 | n/a |
| P6 | n20 | depends | 0.8559 | 0.8667 | 0.0108 | 0.1490 | 0.8900 | 0.0000 | 0.1100 | 1.074 | 0.3135 | 0.600 | 0.000 | 13.9 | 1.545 | 0.8700 | 9.1 | n/a |
| P6 | n20 | carried_margin | 0.3579 | 0.3539 | -0.0039 | 0.0675 | 0.8900 | 0.0000 | 0.1100 | 1.068 | 0.1466 | 0.040 | 0.200 | 11.2 | 1.443 | 0.7700 | n/a | n/a |
| P6 | n20 | own_margin | 0.4181 | 0.4092 | -0.0089 | 0.0423 | 0.9700 | 0.0000 | 0.0300 | 1.452 | 0.1383 | 0.180 | 0.720 | 5.9 | 0.913 | 0.7300 | n/a | n/a |
| P6 | n20 | kappa | 0.6602 | 0.6545 | -0.0057 | 0.0550 | 0.9700 | 0.0200 | 0.0100 | 1.086 | 0.1244 | 0.050 | 0.040 | 14.9 | 0.974 | 0.9300 | 6.4 | n/a |
| P6 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4092 | 0.0089 | 0.0423 | 0.9700 | 0.0300 | 0.0000 | 1.452 | 0.1383 | 0.180 | 0.720 | 5.9 | 0.913 | 0.7300 | n/a | n/a |
| P6 | n20 | carried_added | 0.5421 | 0.5397 | -0.0023 | 0.0853 | 0.9100 | 0.0000 | 0.0900 | 1.051 | 0.1791 | 0.040 | 0.040 | 14.4 | 1.376 | 0.8500 | n/a | n/a |
| P6 | n20 | pooled_retention | 0.9000 | 0.9033 | 0.0033 | 0.0838 | 0.8900 | 0.0000 | 0.1100 | 1.206 | 0.1944 | 0.840 | 0.000 | 15.0 | 1.874 | 0.8900 | 8.6 | n/a |
| P6 | n40 | large | 1.1871 | 1.1808 | -0.0064 | 0.2611 | 0.9000 | 0.0200 | 0.0800 | 0.890 | 0.5120 | 0.340 | 0.040 | 13.9 | 1.302 | 0.8900 | n/a | n/a |
| P6 | n40 | carries | 0.9000 | 0.9001 | 0.0001 | 0.1339 | 0.9600 | 0.0100 | 0.0300 | 0.941 | 0.2746 | 0.530 | 0.000 | 13.9 | 0.966 | 0.8800 | 7.9 | n/a |
| P6 | n40 | depends | 0.8898 | 0.8908 | 0.0010 | 0.1475 | 0.9600 | 0.0100 | 0.0300 | 0.937 | 0.2990 | 0.530 | 0.000 | 13.9 | 0.990 | 0.8900 | 7.7 | n/a |
| P6 | n40 | carried_margin | 1.6052 | 1.5899 | -0.0153 | 0.2796 | 0.9100 | 0.0200 | 0.0700 | 0.924 | 0.5719 | 0.150 | 0.100 | 13.2 | 1.320 | 0.8800 | n/a | n/a |
| P6 | n40 | own_margin | 1.8041 | 1.7940 | -0.0101 | 0.2094 | 0.9700 | 0.0000 | 0.0300 | 1.284 | 0.5077 | 0.150 | 0.270 | 10.1 | 0.936 | 0.8700 | n/a | n/a |
| P6 | n40 | kappa | 0.8971 | 0.8945 | -0.0025 | 0.0180 | 0.9300 | 0.0600 | 0.0100 | 1.049 | 0.0380 | 0.150 | 0.020 | 14.5 | 1.111 | 0.9100 | 6.3 | n/a |
| P6 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4091 | 0.0090 | 0.0423 | 0.9700 | 0.0300 | 0.0000 | 1.460 | 0.1382 | 0.180 | 0.720 | 5.9 | 0.920 | 0.7300 | n/a | n/a |
| P6 | n40 | carried_added | 1.7894 | 1.7758 | -0.0137 | 0.3013 | 0.9100 | 0.0200 | 0.0700 | 0.939 | 0.6130 | 0.150 | 0.040 | 13.9 | 1.306 | 0.8800 | n/a | n/a |
| P6 | n40 | pooled_retention | 0.9000 | 0.9043 | 0.0043 | 0.0858 | 0.8900 | 0.0000 | 0.1100 | 1.165 | 0.1974 | 0.860 | 0.000 | 15.0 | 2.183 | 0.8800 | 8.1 | n/a |
| P6 | n80 | large | 8.2819 | 8.0355 | -0.2465 | 1.3857 | 0.9300 | 0.0100 | 0.0600 | 0.994 | 3.0320 | 0.120 | 0.290 | 9.1 | 1.084 | 0.8300 | n/a | n/a |
| P6 | n80 | carries | 0.9000 | 0.8921 | -0.0079 | 0.1371 | 0.9600 | 0.0000 | 0.0400 | 1.263 | 0.3132 | 0.630 | 0.010 | 13.8 | 0.948 | 0.9400 | 8.4 | n/a |
| P6 | n80 | depends | 0.8981 | 0.8905 | -0.0076 | 0.1396 | 0.9600 | 0.0000 | 0.0400 | 1.269 | 0.3197 | 0.630 | 0.010 | 13.8 | 0.942 | 0.9400 | 8.2 | n/a |
| P6 | n80 | carried_margin | 8.7000 | 8.4447 | -0.2554 | 1.4168 | 0.9300 | 0.0100 | 0.0600 | 0.998 | 3.1000 | 0.110 | 0.300 | 8.9 | 1.104 | 0.8200 | n/a | n/a |
| P6 | n80 | own_margin | 9.6872 | 9.5309 | -0.1563 | 1.0934 | 0.9800 | 0.0100 | 0.0100 | 1.392 | 3.3626 | 0.160 | 0.620 | 6.6 | 0.849 | 0.8200 | n/a | n/a |
| P6 | n80 | kappa | 0.9793 | 0.9784 | -0.0009 | 0.0034 | 0.9800 | 0.0200 | 0.0000 | 1.304 | 0.0083 | 0.110 | 0.210 | 10.2 | 0.661 | 0.9100 | 6.3 | n/a |
| P6 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4092 | 0.0089 | 0.0424 | 0.9600 | 0.0400 | 0.0000 | 1.451 | 0.1407 | 0.180 | 0.710 | 5.9 | 0.925 | 0.7300 | n/a | n/a |
| P6 | n80 | carried_added | 8.8842 | 8.6305 | -0.2538 | 1.4416 | 0.9300 | 0.0100 | 0.0600 | 0.997 | 3.1589 | 0.110 | 0.280 | 9.2 | 1.108 | 0.8300 | n/a | n/a |
| P6 | n80 | pooled_retention | 0.9000 | 0.9047 | 0.0047 | 0.0867 | 0.8900 | 0.0000 | 0.1100 | 1.130 | 0.1948 | 0.820 | 0.000 | 15.1 | 2.085 | 0.8800 | 8.1 | n/a |
| P6 | n160 | large | 18.9046 | 18.7725 | -0.1321 | 2.2063 | 0.9300 | 0.0000 | 0.0700 | 1.089 | 4.7735 | 0.510 | 0.000 | 14.5 | 1.102 | 0.8700 | n/a | n/a |
| P6 | n160 | carries | 0.9000 | 0.9040 | 0.0040 | 0.1357 | 0.9200 | 0.0000 | 0.0800 | 1.280 | 0.3095 | 0.510 | 0.010 | 14.5 | 1.141 | 0.9100 | 15.5 | n/a |
| P6 | n160 | depends | 0.8991 | 0.9034 | 0.0042 | 0.1368 | 0.9200 | 0.0000 | 0.0800 | 1.284 | 0.3121 | 0.510 | 0.010 | 14.5 | 1.142 | 0.9100 | 15.0 | n/a |
| P6 | n160 | carried_margin | 19.3227 | 19.1816 | -0.1410 | 2.2228 | 0.9300 | 0.0000 | 0.0700 | 1.087 | 4.7829 | 0.520 | 0.010 | 14.5 | 1.125 | 0.8700 | n/a | n/a |
| P6 | n160 | own_margin | 21.4901 | 21.3653 | -0.1248 | 1.2244 | 0.9600 | 0.0300 | 0.0100 | 1.369 | 3.0744 | 0.470 | 0.150 | 11.5 | 0.902 | 0.9200 | n/a | n/a |
| P6 | n160 | kappa | 0.9906 | 0.9905 | -0.0001 | 0.0012 | 0.9600 | 0.0400 | 0.0000 | 1.196 | 0.0027 | 0.530 | 0.000 | 14.8 | 0.803 | 0.9500 | 8.6 | n/a |
| P6 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4092 | 0.0089 | 0.0424 | 0.9600 | 0.0400 | 0.0000 | 1.452 | 0.1394 | 0.190 | 0.710 | 5.9 | 0.908 | 0.7300 | n/a | n/a |
| P6 | n160 | carried_added | 19.5068 | 19.3675 | -0.1394 | 2.2553 | 0.9300 | 0.0000 | 0.0700 | 1.087 | 4.8512 | 0.520 | 0.010 | 14.5 | 1.149 | 0.8700 | n/a | n/a |
| P6 | n160 | pooled_retention | 0.9000 | 0.9036 | 0.0036 | 0.0842 | 0.8900 | 0.0000 | 0.1100 | 1.193 | 0.1934 | 0.540 | 0.000 | 15.1 | 2.015 | 0.8900 | 15.9 | n/a |
| P6 | n320 | large | 22.0611 | 22.0304 | -0.0307 | 2.4918 | 0.9200 | 0.0000 | 0.0800 | 1.117 | 5.4901 | 0.600 | 0.000 | 14.8 | 1.318 | 0.8800 | n/a | n/a |
| P6 | n320 | carries | 0.9000 | 0.9042 | 0.0042 | 0.1327 | 0.9100 | 0.0000 | 0.0900 | 1.296 | 0.3016 | 0.510 | 0.010 | 14.5 | 1.240 | 0.8900 | 17.1 | n/a |
| P6 | n320 | depends | 0.8993 | 0.9037 | 0.0044 | 0.1336 | 0.9100 | 0.0000 | 0.0900 | 1.300 | 0.3031 | 0.510 | 0.010 | 14.5 | 1.240 | 0.8900 | 16.5 | n/a |
| P6 | n320 | carried_margin | 22.4792 | 22.4395 | -0.0397 | 2.5058 | 0.9300 | 0.0000 | 0.0700 | 1.115 | 5.4948 | 0.620 | 0.000 | 14.8 | 1.300 | 0.8800 | n/a | n/a |
| P6 | n320 | own_margin | 24.9973 | 24.9765 | -0.0208 | 1.2406 | 0.9900 | 0.0100 | 0.0000 | 1.568 | 3.2973 | 0.500 | 0.080 | 12.5 | 0.723 | 0.9300 | n/a | n/a |
| P6 | n320 | kappa | 0.9919 | 0.9918 | -0.0000 | 0.0010 | 0.9500 | 0.0500 | 0.0000 | 1.139 | 0.0023 | 0.610 | 0.000 | 15.1 | 0.938 | 0.9500 | 8.7 | n/a |
| P6 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4091 | 0.0090 | 0.0423 | 0.9600 | 0.0400 | 0.0000 | 1.457 | 0.1403 | 0.180 | 0.700 | 5.9 | 0.921 | 0.7300 | n/a | n/a |
| P6 | n320 | carried_added | 22.6634 | 22.6254 | -0.0380 | 2.5389 | 0.9300 | 0.0000 | 0.0700 | 1.115 | 5.5677 | 0.620 | 0.000 | 14.8 | 1.314 | 0.8800 | n/a | n/a |
| P6 | n320 | pooled_retention | 0.9000 | 0.9046 | 0.0046 | 0.0848 | 0.8900 | 0.0000 | 0.1100 | 1.177 | 0.1929 | 0.540 | 0.000 | 15.1 | 1.873 | 0.8900 | 17.4 | n/a |
| P6 | h2 | large | 1.1198 | 1.1349 | 0.0151 | 0.1200 | 0.9400 | 0.0000 | 0.0600 | 1.166 | 0.2637 | 0.200 | 0.010 | 15.3 | 1.104 | 0.8900 | n/a | 1.000 |
| P6 | h2 | carries | 0.9000 | 0.9029 | 0.0029 | 0.0827 | 0.8800 | 0.0000 | 0.1200 | 1.096 | 0.1783 | 0.460 | 0.000 | 15.1 | 1.726 | 0.8700 | 110.6 | 1.000 |
| P6 | h2 | depends | 0.8893 | 0.8943 | 0.0050 | 0.0903 | 0.8800 | 0.0000 | 0.1200 | 1.122 | 0.1930 | 0.460 | 0.000 | 15.1 | 1.762 | 0.8700 | 53.1 | 1.000 |
| P6 | h2 | carried_margin | 1.5381 | 1.5440 | 0.0058 | 0.1299 | 0.8800 | 0.0000 | 0.1200 | 1.087 | 0.2793 | 0.470 | 0.000 | 15.2 | 1.734 | 0.8700 | n/a | 1.000 |
| P6 | h2 | own_margin | 1.7295 | 1.7292 | -0.0003 | 0.0299 | 0.9300 | 0.0700 | 0.0000 | 1.250 | 0.0695 | 0.370 | 0.000 | 15.0 | 1.062 | 0.8800 | n/a | 1.000 |
| P6 | h2 | kappa | 0.8931 | 0.8936 | 0.0006 | 0.0118 | 0.8900 | 0.1100 | 0.0000 | 1.097 | 0.0269 | 0.540 | 0.000 | 15.1 | 1.713 | 0.8900 | 10.1 | 1.000 |
| P6 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4091 | 0.0093 | 0.0423 | 0.9700 | 0.0300 | 0.0000 | 1.458 | 0.1383 | 0.180 | 0.700 | 5.9 | 0.910 | 0.7300 | n/a | 1.000 |
| P6 | h2 | carried_added | 1.7223 | 1.7299 | 0.0076 | 0.1680 | 0.8800 | 0.0000 | 0.1200 | 1.099 | 0.3684 | 0.480 | 0.000 | 15.1 | 1.889 | 0.8700 | n/a | 1.000 |
| P6 | h2 | pooled_retention | 0.9000 | 0.9044 | 0.0044 | 0.0869 | 0.8800 | 0.0000 | 0.1200 | 1.114 | 0.1921 | 0.560 | 0.000 | 15.1 | 2.191 | 0.8700 | 112.8 | 1.000 |
| P6 | h5 | large | 4.0064 | 4.0299 | 0.0235 | 0.3803 | 0.8900 | 0.0000 | 0.1100 | 1.221 | 0.8931 | 0.460 | 0.000 | 15.3 | 1.668 | 0.8900 | n/a | 0.990 |
| P6 | h5 | carries | 0.9000 | 0.9036 | 0.0036 | 0.0871 | 0.8900 | 0.0000 | 0.1100 | 1.189 | 0.1992 | 0.590 | 0.000 | 15.1 | 1.862 | 0.8800 | 144.0 | 0.990 |
| P6 | h5 | depends | 0.8963 | 0.9007 | 0.0044 | 0.0900 | 0.8900 | 0.0000 | 0.1100 | 1.201 | 0.2042 | 0.590 | 0.000 | 15.1 | 1.879 | 0.8800 | 77.2 | 0.990 |
| P6 | h5 | carried_margin | 4.4247 | 4.4384 | 0.0137 | 0.3950 | 0.8900 | 0.0000 | 0.1100 | 1.199 | 0.9180 | 0.510 | 0.000 | 15.2 | 2.032 | 0.8800 | n/a | 0.990 |
| P6 | h5 | own_margin | 4.9368 | 4.9331 | -0.0037 | 0.0601 | 0.9600 | 0.0400 | 0.0000 | 1.183 | 0.1405 | 0.520 | 0.090 | 13.2 | 0.917 | 0.8800 | n/a | 0.990 |
| P6 | h5 | kappa | 0.9600 | 0.9601 | 0.0001 | 0.0045 | 0.8900 | 0.1000 | 0.0100 | 1.082 | 0.0101 | 0.560 | 0.000 | 15.1 | 1.689 | 0.9000 | 9.9 | 0.990 |
| P6 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4085 | 0.0099 | 0.0425 | 0.9600 | 0.0400 | 0.0000 | 1.530 | 0.1391 | 0.220 | 0.680 | 6.2 | 0.930 | 0.7300 | n/a | 0.990 |
| P6 | h5 | carried_added | 4.6089 | 4.6245 | 0.0156 | 0.4328 | 0.8900 | 0.0000 | 0.1100 | 1.196 | 1.0048 | 0.500 | 0.000 | 15.1 | 2.064 | 0.8900 | n/a | 0.990 |
| P6 | h5 | pooled_retention | 0.9000 | 0.9043 | 0.0043 | 0.0848 | 0.8900 | 0.0000 | 0.1100 | 1.186 | 0.1966 | 0.520 | 0.000 | 15.1 | 2.112 | 0.8900 | 147.5 | 0.990 |
| P6 | h10 | large | 9.2049 | 8.7572 | -0.4477 | 0.6515 | 0.8200 | 0.0000 | 0.1800 | 1.649 | 1.7303 | 0.660 | 0.000 | 15.2 | 2.440 | 0.8200 | n/a | 0.180 |
| P6 | h10 | carries | 0.9000 | 0.8559 | -0.0441 | 0.0638 | 0.8200 | 0.0000 | 0.1800 | 1.650 | 0.1700 | 0.590 | 0.000 | 15.1 | 2.641 | 0.8200 | 125.2 | 0.180 |
| P6 | h10 | depends | 0.8983 | 0.8538 | -0.0444 | 0.0645 | 0.8200 | 0.0000 | 0.1800 | 1.658 | 0.1710 | 0.590 | 0.000 | 15.1 | 2.652 | 0.8200 | 114.0 | 0.180 |
| P6 | h10 | carried_margin | 9.6232 | 9.1606 | -0.4627 | 0.6582 | 0.8200 | 0.0000 | 0.1800 | 1.668 | 1.7797 | 0.650 | 0.000 | 15.1 | 2.533 | 0.8200 | n/a | 0.180 |
| P6 | h10 | own_margin | 10.7131 | 10.7318 | 0.0187 | 0.0964 | 0.9400 | 0.0500 | 0.0100 | 1.415 | 0.2126 | 0.520 | 0.280 | 10.6 | 1.038 | 0.8500 | n/a | 0.180 |
| P6 | h10 | kappa | 0.9812 | 0.9826 | 0.0013 | 0.0018 | 0.8200 | 0.1800 | 0.0000 | 1.447 | 0.0048 | 0.630 | 0.000 | 15.1 | 2.517 | 0.8200 | 10.7 | 0.180 |
| P6 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4033 | 0.0150 | 0.0416 | 0.8500 | 0.1500 | 0.0000 | 0.855 | 0.0830 | 0.040 | 0.500 | 9.6 | 1.531 | 0.6000 | n/a | 0.180 |
| P6 | h10 | carried_added | 9.8074 | 9.3243 | -0.4831 | 0.6861 | 0.8200 | 0.0000 | 0.1800 | 1.667 | 1.8559 | 0.660 | 0.000 | 15.1 | 2.543 | 0.8200 | n/a | 0.180 |
| P6 | h10 | pooled_retention | 0.9000 | 0.8543 | -0.0457 | 0.0622 | 0.8200 | 0.0000 | 0.1800 | 1.689 | 0.1691 | 0.600 | 0.000 | 15.1 | 2.735 | 0.8200 | 124.0 | 0.180 |
| P7 | n20 | large | 0.0000 | 0.0028 | 0.0028 | 0.0524 | 0.9300 | 0.0000 | 0.0700 | 1.720 | 0.1388 | 0.630 | 0.010 | 14.1 | 1.320 | 0.9100 | n/a | n/a |
| P7 | n20 | carries | 1.0000 | 1.0053 | 0.0053 | 0.0871 | 0.9200 | 0.0000 | 0.0800 | 1.713 | 0.2424 | 0.640 | 0.010 | 14.1 | 1.403 | 0.9100 | 9.7 | n/a |
| P7 | n20 | depends | 1.0000 | 1.0086 | 0.0086 | 0.1281 | 0.9200 | 0.0000 | 0.0800 | 1.717 | 0.3451 | 0.640 | 0.020 | 14.1 | 1.494 | 0.9100 | 14.8 | n/a |
| P7 | n20 | carried_margin | 0.4093 | 0.4107 | 0.0014 | 0.0537 | 0.8900 | 0.0000 | 0.1100 | 1.481 | 0.1333 | 0.640 | 0.000 | 14.8 | 1.472 | 0.8900 | n/a | n/a |
| P7 | n20 | own_margin | 0.4093 | 0.4079 | -0.0014 | 0.0274 | 0.9000 | 0.0000 | 0.1000 | 1.364 | 0.0608 | 0.580 | 0.080 | 12.7 | 1.268 | 0.8600 | n/a | n/a |
| P7 | n20 | kappa | 0.6896 | 0.6843 | -0.0053 | 0.0437 | 0.9500 | 0.0300 | 0.0200 | 1.207 | 0.1035 | 0.630 | 0.000 | 15.2 | 0.960 | 0.9400 | 7.2 | n/a |
| P7 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4079 | 0.0014 | 0.0274 | 0.9000 | 0.1000 | 0.0000 | 1.364 | 0.0608 | 0.580 | 0.080 | 12.7 | 1.268 | 0.8600 | n/a | n/a |
| P7 | n20 | carried_added | 0.5935 | 0.6008 | 0.0073 | 0.0747 | 0.9700 | 0.0000 | 0.0300 | 1.390 | 0.1746 | 0.640 | 0.000 | 15.2 | 0.789 | 0.9700 | n/a | n/a |
| P7 | n20 | pooled_retention | 1.0000 | 1.0147 | 0.0147 | 0.0955 | 0.9300 | 0.0000 | 0.0700 | 1.246 | 0.2254 | 0.420 | 0.000 | 15.1 | 1.830 | 0.9100 | 10.0 | n/a |
| P7 | n40 | large | 0.0000 | 0.0056 | 0.0056 | 0.0626 | 0.9800 | 0.0000 | 0.0200 | 1.323 | 0.1485 | 0.630 | 0.010 | 14.1 | 0.754 | 0.9500 | n/a | n/a |
| P7 | n40 | carries | 0.3046 | 0.3097 | 0.0052 | 0.0407 | 0.9700 | 0.0100 | 0.0200 | 1.120 | 0.0917 | 0.680 | 0.000 | 14.5 | 0.815 | 0.9500 | 9.5 | n/a |
| P7 | n40 | depends | 0.2320 | 0.2358 | 0.0039 | 0.0402 | 0.9600 | 0.0100 | 0.0300 | 1.144 | 0.0909 | 0.690 | 0.000 | 14.4 | 0.876 | 0.9600 | 9.9 | n/a |
| P7 | n40 | carried_margin | 0.4093 | 0.4135 | 0.0042 | 0.0625 | 0.9500 | 0.0100 | 0.0400 | 1.220 | 0.1424 | 0.620 | 0.000 | 14.9 | 0.929 | 0.9500 | n/a | n/a |
| P7 | n40 | own_margin | 1.7645 | 1.7686 | 0.0041 | 0.1791 | 0.9400 | 0.0000 | 0.0600 | 1.070 | 0.3884 | 0.650 | 0.000 | 14.5 | 1.024 | 0.9000 | n/a | n/a |
| P7 | n40 | kappa | 0.6896 | 0.6849 | -0.0047 | 0.0460 | 0.9500 | 0.0500 | 0.0000 | 1.183 | 0.1065 | 0.620 | 0.000 | 15.3 | 0.958 | 0.9500 | 6.8 | n/a |
| P7 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4079 | 0.0014 | 0.0274 | 0.9000 | 0.1000 | 0.0000 | 1.370 | 0.0601 | 0.570 | 0.090 | 12.6 | 1.273 | 0.8600 | n/a | n/a |
| P7 | n40 | carried_added | 0.5935 | 0.6036 | 0.0101 | 0.0824 | 0.9800 | 0.0000 | 0.0200 | 1.225 | 0.1838 | 0.610 | 0.000 | 15.3 | 0.829 | 0.9400 | n/a | n/a |
| P7 | n40 | pooled_retention | 0.3046 | 0.3091 | 0.0045 | 0.0286 | 0.9300 | 0.0000 | 0.0700 | 1.305 | 0.0694 | 0.470 | 0.000 | 15.1 | 1.629 | 0.9200 | 9.4 | n/a |
| P7 | n80 | large | 0.0000 | 0.0083 | 0.0083 | 0.0554 | 0.9600 | 0.0000 | 0.0400 | 1.279 | 0.1232 | 0.620 | 0.130 | 12.1 | 0.958 | 0.9100 | n/a | n/a |
| P7 | n80 | carries | 0.0608 | 0.0632 | 0.0024 | 0.0104 | 0.9800 | 0.0000 | 0.0200 | 1.141 | 0.0226 | 0.530 | 0.100 | 13.2 | 0.830 | 0.9200 | 12.4 | n/a |
| P7 | n80 | depends | 0.0427 | 0.0442 | 0.0015 | 0.0072 | 0.9700 | 0.0000 | 0.0300 | 1.180 | 0.0151 | 0.530 | 0.160 | 12.3 | 0.802 | 0.9000 | 11.9 | n/a |
| P7 | n80 | carried_margin | 0.4093 | 0.4163 | 0.0070 | 0.0536 | 0.9600 | 0.0000 | 0.0400 | 1.165 | 0.1147 | 0.550 | 0.100 | 12.0 | 0.791 | 0.9100 | n/a | n/a |
| P7 | n80 | own_margin | 9.5794 | 9.4867 | -0.0927 | 0.7539 | 0.9700 | 0.0000 | 0.0300 | 1.281 | 1.7375 | 0.570 | 0.190 | 11.6 | 0.869 | 0.9200 | n/a | n/a |
| P7 | n80 | kappa | 0.6896 | 0.6877 | -0.0020 | 0.0392 | 0.9400 | 0.0400 | 0.0200 | 1.373 | 0.0975 | 0.550 | 0.010 | 14.2 | 1.047 | 0.9400 | 7.5 | n/a |
| P7 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4080 | 0.0013 | 0.0274 | 0.9000 | 0.1000 | 0.0000 | 1.365 | 0.0589 | 0.580 | 0.080 | 12.6 | 1.270 | 0.8700 | n/a | n/a |
| P7 | n80 | carried_added | 0.5935 | 0.6064 | 0.0129 | 0.0778 | 0.9700 | 0.0000 | 0.0300 | 1.141 | 0.1740 | 0.560 | 0.020 | 13.8 | 0.791 | 0.9300 | n/a | n/a |
| P7 | n80 | pooled_retention | 0.0608 | 0.0617 | 0.0010 | 0.0056 | 0.9300 | 0.0000 | 0.0700 | 1.342 | 0.0136 | 0.550 | 0.000 | 15.1 | 1.551 | 0.9200 | 12.5 | n/a |
| P7 | n160 | large | 0.0000 | 0.0059 | 0.0059 | 0.0452 | 0.9700 | 0.0100 | 0.0200 | 1.213 | 0.0988 | 0.610 | 0.100 | 12.5 | 0.908 | 0.8700 | n/a | n/a |
| P7 | n160 | carries | 0.0269 | 0.0276 | 0.0007 | 0.0042 | 0.9400 | 0.0000 | 0.0600 | 1.290 | 0.0096 | 0.530 | 0.000 | 14.9 | 1.028 | 0.9100 | 16.0 | n/a |
| P7 | n160 | depends | 0.0187 | 0.0190 | 0.0004 | 0.0025 | 0.9700 | 0.0000 | 0.0300 | 1.293 | 0.0058 | 0.550 | 0.010 | 13.8 | 0.828 | 0.9300 | 15.6 | n/a |
| P7 | n160 | carried_margin | 0.4093 | 0.4136 | 0.0043 | 0.0397 | 0.9700 | 0.0100 | 0.0200 | 1.232 | 0.0915 | 0.530 | 0.010 | 13.6 | 0.889 | 0.9300 | n/a | n/a |
| P7 | n160 | own_margin | 21.9134 | 21.8357 | -0.0777 | 1.2520 | 0.9500 | 0.0300 | 0.0200 | 1.315 | 3.0415 | 0.610 | 0.060 | 13.0 | 0.963 | 0.9300 | n/a | n/a |
| P7 | n160 | kappa | 0.6896 | 0.6870 | -0.0026 | 0.0363 | 0.9600 | 0.0300 | 0.0100 | 1.335 | 0.0891 | 0.510 | 0.000 | 15.2 | 0.901 | 0.9500 | 8.2 | n/a |
| P7 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4078 | 0.0015 | 0.0274 | 0.9000 | 0.1000 | 0.0000 | 1.366 | 0.0603 | 0.570 | 0.090 | 12.6 | 1.302 | 0.8500 | n/a | n/a |
| P7 | n160 | carried_added | 0.5935 | 0.6039 | 0.0104 | 0.0680 | 0.9600 | 0.0000 | 0.0400 | 1.190 | 0.1553 | 0.530 | 0.000 | 15.0 | 0.958 | 0.9000 | n/a | n/a |
| P7 | n160 | pooled_retention | 0.0269 | 0.0273 | 0.0004 | 0.0025 | 0.9300 | 0.0000 | 0.0700 | 1.318 | 0.0060 | 0.560 | 0.000 | 15.1 | 1.659 | 0.9200 | 16.5 | n/a |
| P7 | n320 | large | 0.0000 | 0.0043 | 0.0043 | 0.0450 | 0.9600 | 0.0100 | 0.0300 | 1.154 | 0.0955 | 0.660 | 0.130 | 12.4 | 0.977 | 0.8600 | n/a | n/a |
| P7 | n320 | carries | 0.0233 | 0.0239 | 0.0005 | 0.0035 | 0.9300 | 0.0000 | 0.0700 | 1.348 | 0.0081 | 0.490 | 0.000 | 14.8 | 1.185 | 0.9100 | 16.1 | n/a |
| P7 | n320 | depends | 0.0162 | 0.0164 | 0.0002 | 0.0020 | 0.9800 | 0.0100 | 0.0100 | 1.371 | 0.0049 | 0.520 | 0.010 | 13.4 | 0.806 | 0.9600 | 15.7 | n/a |
| P7 | n320 | carried_margin | 0.4093 | 0.4122 | 0.0029 | 0.0376 | 0.9700 | 0.0100 | 0.0200 | 1.258 | 0.0871 | 0.540 | 0.030 | 13.4 | 0.759 | 0.9300 | n/a | n/a |
| P7 | n320 | own_margin | 25.2643 | 25.2026 | -0.0618 | 1.3479 | 0.9500 | 0.0300 | 0.0200 | 1.456 | 3.4972 | 0.550 | 0.110 | 12.6 | 0.987 | 0.9400 | n/a | n/a |
| P7 | n320 | kappa | 0.6896 | 0.6865 | -0.0032 | 0.0387 | 0.9700 | 0.0200 | 0.0100 | 1.163 | 0.0890 | 0.540 | 0.000 | 15.2 | 0.938 | 0.9500 | 8.5 | n/a |
| P7 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4079 | 0.0014 | 0.0274 | 0.9000 | 0.1000 | 0.0000 | 1.364 | 0.0595 | 0.560 | 0.090 | 12.6 | 1.319 | 0.8500 | n/a | n/a |
| P7 | n320 | carried_added | 0.5935 | 0.6023 | 0.0088 | 0.0640 | 0.9300 | 0.0100 | 0.0600 | 1.286 | 0.1514 | 0.540 | 0.000 | 15.0 | 1.032 | 0.9100 | n/a | n/a |
| P7 | n320 | pooled_retention | 0.0233 | 0.0236 | 0.0003 | 0.0022 | 0.9200 | 0.0000 | 0.0800 | 1.272 | 0.0051 | 0.490 | 0.000 | 15.1 | 1.580 | 0.9100 | 17.2 | n/a |
| P7 | h2 | large | 0.0000 | 0.0038 | 0.0038 | 0.0244 | 0.9900 | 0.0000 | 0.0100 | 1.556 | 0.0586 | 0.570 | 0.110 | 13.0 | 0.835 | 0.9400 | n/a | 1.000 |
| P7 | h2 | carries | 0.3108 | 0.3146 | 0.0038 | 0.0273 | 0.9200 | 0.0000 | 0.0800 | 1.297 | 0.0656 | 0.610 | 0.000 | 15.1 | 1.520 | 0.9100 | 121.8 | 1.000 |
| P7 | h2 | depends | 0.2372 | 0.2393 | 0.0021 | 0.0145 | 0.9300 | 0.0000 | 0.0700 | 1.361 | 0.0352 | 0.620 | 0.000 | 15.2 | 1.088 | 0.9100 | 51.8 | 1.000 |
| P7 | h2 | carried_margin | 0.4093 | 0.4117 | 0.0024 | 0.0186 | 0.9500 | 0.0000 | 0.0500 | 1.340 | 0.0456 | 0.540 | 0.000 | 15.3 | 1.006 | 0.9200 | n/a | 1.000 |
| P7 | h2 | own_margin | 1.7255 | 1.7221 | -0.0034 | 0.0292 | 0.9500 | 0.0500 | 0.0000 | 1.348 | 0.0710 | 0.520 | 0.000 | 15.2 | 0.998 | 0.9100 | n/a | 1.000 |
| P7 | h2 | kappa | 0.6896 | 0.6870 | -0.0026 | 0.0335 | 0.9200 | 0.0700 | 0.0100 | 1.210 | 0.0802 | 0.560 | 0.000 | 15.0 | 1.519 | 0.9100 | 9.7 | 1.000 |
| P7 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4079 | 0.0014 | 0.0276 | 0.9000 | 0.1000 | 0.0000 | 1.346 | 0.0598 | 0.560 | 0.090 | 12.6 | 1.239 | 0.8500 | n/a | 1.000 |
| P7 | h2 | carried_added | 0.5935 | 0.6018 | 0.0084 | 0.0557 | 0.9200 | 0.0000 | 0.0800 | 1.281 | 0.1330 | 0.520 | 0.000 | 15.1 | 1.669 | 0.9100 | n/a | 1.000 |
| P7 | h2 | pooled_retention | 0.3108 | 0.3154 | 0.0046 | 0.0291 | 0.9200 | 0.0000 | 0.0800 | 1.281 | 0.0702 | 0.630 | 0.000 | 15.0 | 1.705 | 0.9100 | 121.3 | 1.000 |
| P7 | h5 | large | 0.0000 | 0.0035 | 0.0035 | 0.0240 | 0.9900 | 0.0000 | 0.0100 | 1.673 | 0.0586 | 0.620 | 0.120 | 12.6 | 0.779 | 0.9500 | n/a | 0.990 |
| P7 | h5 | carries | 0.1162 | 0.1176 | 0.0015 | 0.0110 | 0.9200 | 0.0000 | 0.0800 | 1.344 | 0.0264 | 0.550 | 0.000 | 15.2 | 1.548 | 0.9200 | 141.4 | 0.990 |
| P7 | h5 | depends | 0.0831 | 0.0836 | 0.0005 | 0.0044 | 0.9300 | 0.0000 | 0.0700 | 1.469 | 0.0111 | 0.560 | 0.000 | 15.2 | 1.194 | 0.9100 | 72.5 | 0.990 |
| P7 | h5 | carried_margin | 0.4093 | 0.4115 | 0.0022 | 0.0173 | 0.9300 | 0.0000 | 0.0700 | 1.537 | 0.0448 | 0.590 | 0.000 | 15.1 | 1.177 | 0.9200 | n/a | 0.990 |
| P7 | h5 | own_margin | 4.9248 | 4.9226 | -0.0022 | 0.0592 | 0.9700 | 0.0300 | 0.0000 | 1.348 | 0.1500 | 0.520 | 0.060 | 13.3 | 0.853 | 0.9200 | n/a | 0.990 |
| P7 | h5 | kappa | 0.6896 | 0.6874 | -0.0023 | 0.0333 | 0.9200 | 0.0700 | 0.0100 | 1.225 | 0.0809 | 0.590 | 0.000 | 15.1 | 1.569 | 0.9200 | 9.6 | 0.990 |
| P7 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4080 | 0.0013 | 0.0274 | 0.9100 | 0.0900 | 0.0000 | 1.414 | 0.0597 | 0.590 | 0.100 | 12.3 | 1.193 | 0.8600 | n/a | 0.990 |
| P7 | h5 | carried_added | 0.5935 | 0.6012 | 0.0077 | 0.0540 | 0.9200 | 0.0000 | 0.0800 | 1.352 | 0.1305 | 0.570 | 0.000 | 15.1 | 1.507 | 0.9200 | n/a | 0.990 |
| P7 | h5 | pooled_retention | 0.1162 | 0.1177 | 0.0016 | 0.0106 | 0.9200 | 0.0000 | 0.0800 | 1.351 | 0.0255 | 0.550 | 0.000 | 15.1 | 1.439 | 0.9200 | 154.7 | 0.990 |
| P7 | h10 | large | 0.0000 | 0.0026 | 0.0026 | 0.0236 | 0.9600 | 0.0300 | 0.0100 | 1.009 | 0.0459 | 0.560 | 0.010 | 14.0 | 0.939 | 0.8900 | n/a | 0.190 |
| P7 | h10 | carries | 0.0546 | 0.0512 | -0.0034 | 0.0040 | 0.7500 | 0.0000 | 0.2500 | 1.300 | 0.0097 | 0.600 | 0.000 | 15.1 | 2.663 | 0.7500 | 146.9 | 0.190 |
| P7 | h10 | depends | 0.0383 | 0.0371 | -0.0012 | 0.0016 | 0.7900 | 0.0000 | 0.2100 | 1.333 | 0.0038 | 0.590 | 0.010 | 14.4 | 1.824 | 0.7700 | 127.7 | 0.190 |
| P7 | h10 | carried_margin | 0.4093 | 0.3973 | -0.0120 | 0.0152 | 0.7900 | 0.0000 | 0.2100 | 1.327 | 0.0362 | 0.590 | 0.010 | 14.6 | 1.789 | 0.7700 | n/a | 0.190 |
| P7 | h10 | own_margin | 10.6772 | 10.6988 | 0.0216 | 0.0630 | 0.9700 | 0.0200 | 0.0100 | 2.214 | 0.1809 | 0.660 | 0.140 | 12.2 | 0.842 | 0.9500 | n/a | 0.190 |
| P7 | h10 | kappa | 0.6896 | 0.7167 | 0.0271 | 0.0305 | 0.7500 | 0.2500 | 0.0000 | 1.166 | 0.0723 | 0.570 | 0.000 | 15.1 | 2.247 | 0.7500 | 11.4 | 0.190 |
| P7 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3947 | 0.0146 | 0.0220 | 0.8300 | 0.1700 | 0.0000 | 1.212 | 0.0451 | 0.540 | 0.020 | 13.9 | 1.862 | 0.7600 | n/a | 0.190 |
| P7 | h10 | carried_added | 0.5935 | 0.5562 | -0.0373 | 0.0434 | 0.7500 | 0.0000 | 0.2500 | 1.301 | 0.1055 | 0.590 | 0.000 | 15.2 | 2.856 | 0.7500 | n/a | 0.190 |
| P7 | h10 | pooled_retention | 0.0546 | 0.0512 | -0.0034 | 0.0040 | 0.7500 | 0.0000 | 0.2500 | 1.318 | 0.0096 | 0.630 | 0.000 | 15.1 | 2.801 | 0.7500 | 143.6 | 0.190 |
| P8 | n20 | large | 0.0000 | -0.0020 | -0.0020 | 0.0671 | 0.9000 | 0.0000 | 0.1000 | 1.171 | 0.1474 | 0.610 | 0.040 | 13.6 | 1.548 | 0.8500 | n/a | n/a |
| P8 | n20 | carries | 1.0000 | 0.9983 | -0.0017 | 0.1080 | 0.8900 | 0.0000 | 0.1100 | 1.143 | 0.2522 | 0.620 | 0.030 | 13.6 | 1.618 | 0.8500 | 8.3 | n/a |
| P8 | n20 | depends | 1.0000 | 0.9994 | -0.0006 | 0.1541 | 0.8900 | 0.0000 | 0.1100 | 1.191 | 0.3613 | 0.630 | 0.040 | 13.6 | 1.662 | 0.8500 | 9.3 | n/a |
| P8 | n20 | carried_margin | 0.4181 | 0.4215 | 0.0034 | 0.0776 | 0.9200 | 0.0000 | 0.0800 | 1.068 | 0.1654 | 0.110 | 0.180 | 11.1 | 1.406 | 0.8200 | n/a | n/a |
| P8 | n20 | own_margin | 0.4181 | 0.4235 | 0.0054 | 0.0575 | 0.9200 | 0.0300 | 0.0500 | 0.852 | 0.1341 | 0.120 | 0.600 | 6.2 | 1.246 | 0.6300 | n/a | n/a |
| P8 | n20 | kappa | 0.6942 | 0.6915 | -0.0026 | 0.0461 | 0.9500 | 0.0500 | 0.0000 | 1.224 | 0.1072 | 0.120 | 0.010 | 14.9 | 0.978 | 0.9100 | 6.4 | n/a |
| P8 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4235 | -0.0054 | 0.0575 | 0.9200 | 0.0500 | 0.0300 | 0.852 | 0.1341 | 0.120 | 0.600 | 6.2 | 1.246 | 0.6300 | n/a | n/a |
| P8 | n20 | carried_added | 0.6023 | 0.6086 | 0.0063 | 0.0970 | 0.9000 | 0.0000 | 0.1000 | 1.035 | 0.2028 | 0.110 | 0.020 | 14.3 | 1.104 | 0.8600 | n/a | n/a |
| P8 | n20 | pooled_retention | 1.0000 | 1.0068 | 0.0068 | 0.0941 | 0.9300 | 0.0000 | 0.0700 | 1.170 | 0.2128 | 0.740 | 0.000 | 15.0 | 1.635 | 0.9200 | 8.4 | n/a |
| P8 | n40 | large | 0.0000 | -0.0006 | -0.0006 | 0.0713 | 0.9600 | 0.0200 | 0.0200 | 1.093 | 0.1568 | 0.640 | 0.030 | 13.8 | 0.827 | 0.9300 | n/a | n/a |
| P8 | n40 | carries | 0.3029 | 0.3077 | 0.0048 | 0.0373 | 1.0000 | 0.0000 | 0.0000 | 1.350 | 0.0912 | 0.580 | 0.000 | 14.2 | 0.770 | 0.9900 | 8.1 | n/a |
| P8 | n40 | depends | 0.2318 | 0.2357 | 0.0040 | 0.0374 | 0.9800 | 0.0100 | 0.0100 | 1.370 | 0.0943 | 0.580 | 0.010 | 14.0 | 0.795 | 0.9700 | 8.2 | n/a |
| P8 | n40 | carried_margin | 0.4181 | 0.4229 | 0.0048 | 0.0801 | 0.9400 | 0.0200 | 0.0400 | 1.077 | 0.1701 | 0.140 | 0.200 | 11.8 | 1.080 | 0.8600 | n/a | n/a |
| P8 | n40 | own_margin | 1.8041 | 1.8006 | -0.0035 | 0.2361 | 0.9300 | 0.0100 | 0.0600 | 0.964 | 0.4961 | 0.160 | 0.230 | 10.3 | 1.126 | 0.7900 | n/a | n/a |
| P8 | n40 | kappa | 0.6942 | 0.6917 | -0.0024 | 0.0502 | 0.9400 | 0.0600 | 0.0000 | 1.149 | 0.1138 | 0.150 | 0.030 | 14.3 | 1.038 | 0.8900 | 6.3 | n/a |
| P8 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4236 | -0.0055 | 0.0575 | 0.9200 | 0.0500 | 0.0300 | 0.853 | 0.1328 | 0.120 | 0.600 | 6.2 | 1.258 | 0.6200 | n/a | n/a |
| P8 | n40 | carried_added | 0.6023 | 0.6099 | 0.0076 | 0.0976 | 0.9800 | 0.0000 | 0.0200 | 1.076 | 0.2104 | 0.140 | 0.040 | 13.7 | 0.963 | 0.9100 | n/a | n/a |
| P8 | n40 | pooled_retention | 0.3029 | 0.3055 | 0.0026 | 0.0287 | 0.9200 | 0.0000 | 0.0800 | 1.168 | 0.0622 | 0.750 | 0.000 | 15.0 | 1.303 | 0.9200 | 8.0 | n/a |
| P8 | n80 | large | 0.0000 | -0.0056 | -0.0056 | 0.0574 | 0.9700 | 0.0000 | 0.0300 | 1.294 | 0.1381 | 0.500 | 0.190 | 11.3 | 0.802 | 0.9000 | n/a | n/a |
| P8 | n80 | carries | 0.0610 | 0.0611 | 0.0001 | 0.0089 | 0.9800 | 0.0000 | 0.0200 | 1.344 | 0.0210 | 0.610 | 0.010 | 13.6 | 0.771 | 0.9600 | 8.2 | n/a |
| P8 | n80 | depends | 0.0432 | 0.0428 | -0.0004 | 0.0063 | 0.9600 | 0.0000 | 0.0400 | 1.359 | 0.0147 | 0.590 | 0.070 | 12.9 | 0.924 | 0.9300 | 8.1 | n/a |
| P8 | n80 | carried_margin | 0.4181 | 0.4179 | -0.0002 | 0.0798 | 0.9300 | 0.0300 | 0.0400 | 1.074 | 0.2083 | 0.170 | 0.550 | 6.9 | 1.092 | 0.7400 | n/a | n/a |
| P8 | n80 | own_margin | 9.6872 | 9.7716 | 0.0845 | 1.2403 | 0.9300 | 0.0200 | 0.0500 | 1.196 | 3.5933 | 0.100 | 0.640 | 6.0 | 1.049 | 0.7300 | n/a | n/a |
| P8 | n80 | kappa | 0.6942 | 0.6889 | -0.0052 | 0.0531 | 0.9800 | 0.0200 | 0.0000 | 1.074 | 0.1149 | 0.170 | 0.240 | 10.5 | 0.834 | 0.9000 | 6.3 | n/a |
| P8 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4236 | -0.0055 | 0.0575 | 0.9200 | 0.0500 | 0.0300 | 0.851 | 0.1336 | 0.120 | 0.600 | 6.1 | 1.251 | 0.6200 | n/a | n/a |
| P8 | n80 | carried_added | 0.6023 | 0.6049 | 0.0027 | 0.0972 | 0.9500 | 0.0100 | 0.0400 | 1.071 | 0.2216 | 0.170 | 0.280 | 9.6 | 0.935 | 0.8600 | n/a | n/a |
| P8 | n80 | pooled_retention | 0.0610 | 0.0614 | 0.0004 | 0.0057 | 0.9200 | 0.0000 | 0.0800 | 1.175 | 0.0126 | 0.750 | 0.000 | 15.1 | 1.371 | 0.9100 | 8.4 | n/a |
| P8 | n160 | large | 0.0000 | -0.0069 | -0.0069 | 0.0581 | 0.9300 | 0.0300 | 0.0400 | 0.948 | 0.1142 | 0.420 | 0.210 | 10.5 | 1.103 | 0.8200 | n/a | n/a |
| P8 | n160 | carries | 0.0278 | 0.0280 | 0.0003 | 0.0041 | 0.9400 | 0.0000 | 0.0600 | 1.302 | 0.0091 | 0.590 | 0.010 | 14.5 | 1.062 | 0.9100 | 16.5 | n/a |
| P8 | n160 | depends | 0.0195 | 0.0195 | 0.0000 | 0.0024 | 0.9800 | 0.0000 | 0.0200 | 1.321 | 0.0056 | 0.620 | 0.030 | 13.5 | 0.803 | 0.9400 | 16.0 | n/a |
| P8 | n160 | carried_margin | 0.4181 | 0.4166 | -0.0015 | 0.0408 | 0.9700 | 0.0000 | 0.0300 | 1.194 | 0.0936 | 0.570 | 0.040 | 13.2 | 0.910 | 0.9300 | n/a | n/a |
| P8 | n160 | own_margin | 21.4901 | 21.4683 | -0.0218 | 1.2728 | 0.9500 | 0.0300 | 0.0200 | 1.191 | 2.8875 | 0.470 | 0.090 | 12.5 | 0.990 | 0.9000 | n/a | n/a |
| P8 | n160 | kappa | 0.6942 | 0.6920 | -0.0021 | 0.0404 | 0.9000 | 0.0800 | 0.0200 | 1.028 | 0.0869 | 0.550 | 0.000 | 15.0 | 1.095 | 0.9100 | 8.5 | n/a |
| P8 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4235 | -0.0054 | 0.0574 | 0.9200 | 0.0500 | 0.0300 | 0.856 | 0.1336 | 0.120 | 0.600 | 6.1 | 1.253 | 0.6200 | n/a | n/a |
| P8 | n160 | carried_added | 0.6023 | 0.6036 | 0.0013 | 0.0664 | 0.9800 | 0.0000 | 0.0200 | 1.192 | 0.1484 | 0.570 | 0.010 | 14.7 | 0.847 | 0.9600 | n/a | n/a |
| P8 | n160 | pooled_retention | 0.0278 | 0.0279 | 0.0002 | 0.0026 | 0.9300 | 0.0000 | 0.0700 | 1.149 | 0.0058 | 0.510 | 0.000 | 15.1 | 1.490 | 0.9200 | 16.3 | n/a |
| P8 | n320 | large | 0.0000 | -0.0049 | -0.0049 | 0.0608 | 0.9600 | 0.0100 | 0.0300 | 0.974 | 0.1227 | 0.310 | 0.380 | 9.3 | 0.933 | 0.7700 | n/a | n/a |
| P8 | n320 | carries | 0.0239 | 0.0243 | 0.0004 | 0.0035 | 0.9700 | 0.0000 | 0.0300 | 1.285 | 0.0078 | 0.630 | 0.010 | 14.7 | 0.816 | 0.9300 | 17.6 | n/a |
| P8 | n320 | depends | 0.0167 | 0.0169 | 0.0002 | 0.0020 | 0.9800 | 0.0000 | 0.0200 | 1.371 | 0.0046 | 0.630 | 0.030 | 13.7 | 0.704 | 0.9600 | 17.1 | n/a |
| P8 | n320 | carried_margin | 0.4181 | 0.4186 | 0.0005 | 0.0365 | 0.9800 | 0.0000 | 0.0200 | 1.338 | 0.0884 | 0.600 | 0.010 | 13.3 | 0.766 | 0.9700 | n/a | n/a |
| P8 | n320 | own_margin | 24.9973 | 24.8946 | -0.1027 | 1.3329 | 0.9500 | 0.0400 | 0.0100 | 1.310 | 3.1273 | 0.650 | 0.060 | 13.0 | 0.974 | 0.9200 | n/a | n/a |
| P8 | n320 | kappa | 0.6942 | 0.6933 | -0.0009 | 0.0392 | 0.9200 | 0.0600 | 0.0200 | 1.051 | 0.0840 | 0.590 | 0.000 | 15.1 | 1.095 | 0.8900 | 8.8 | n/a |
| P8 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4235 | -0.0054 | 0.0574 | 0.9200 | 0.0500 | 0.0300 | 0.853 | 0.1344 | 0.120 | 0.600 | 6.1 | 1.257 | 0.6300 | n/a | n/a |
| P8 | n320 | carried_added | 0.6023 | 0.6057 | 0.0034 | 0.0640 | 0.9700 | 0.0000 | 0.0300 | 1.234 | 0.1463 | 0.600 | 0.010 | 14.8 | 0.817 | 0.9500 | n/a | n/a |
| P8 | n320 | pooled_retention | 0.0239 | 0.0241 | 0.0002 | 0.0023 | 0.9200 | 0.0000 | 0.0800 | 1.153 | 0.0049 | 0.470 | 0.000 | 15.1 | 1.549 | 0.9100 | 17.5 | n/a |
| P8 | h2 | large | 0.0000 | -0.0034 | -0.0034 | 0.0524 | 0.9100 | 0.0400 | 0.0500 | 0.900 | 0.1228 | 0.140 | 0.580 | 6.4 | 1.269 | 0.6800 | n/a | 1.000 |
| P8 | h2 | carries | 0.3149 | 0.3172 | 0.0023 | 0.0281 | 0.9100 | 0.0100 | 0.0800 | 1.140 | 0.0624 | 0.660 | 0.000 | 15.1 | 1.271 | 0.9000 | 117.2 | 1.000 |
| P8 | h2 | depends | 0.2419 | 0.2436 | 0.0017 | 0.0153 | 0.9400 | 0.0000 | 0.0600 | 1.189 | 0.0344 | 0.610 | 0.000 | 15.2 | 1.157 | 0.8900 | 55.9 | 1.000 |
| P8 | h2 | carried_margin | 0.4183 | 0.4202 | 0.0019 | 0.0198 | 0.9500 | 0.0000 | 0.0500 | 1.212 | 0.0458 | 0.570 | 0.000 | 15.3 | 0.977 | 0.9200 | n/a | 1.000 |
| P8 | h2 | own_margin | 1.7295 | 1.7266 | -0.0029 | 0.0304 | 0.9500 | 0.0400 | 0.0100 | 1.130 | 0.0665 | 0.530 | 0.000 | 15.1 | 0.977 | 0.9100 | n/a | 1.000 |
| P8 | h2 | kappa | 0.6943 | 0.6952 | 0.0009 | 0.0337 | 0.9200 | 0.0700 | 0.0100 | 1.091 | 0.0753 | 0.520 | 0.000 | 15.1 | 1.183 | 0.9200 | 10.2 | 1.000 |
| P8 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4236 | -0.0053 | 0.0575 | 0.9200 | 0.0500 | 0.0300 | 0.852 | 0.1336 | 0.120 | 0.610 | 6.1 | 1.241 | 0.6200 | n/a | 1.000 |
| P8 | h2 | carried_added | 0.6025 | 0.6072 | 0.0046 | 0.0572 | 0.9200 | 0.0000 | 0.0800 | 1.147 | 0.1293 | 0.550 | 0.000 | 15.1 | 1.391 | 0.9100 | n/a | 1.000 |
| P8 | h2 | pooled_retention | 0.3149 | 0.3169 | 0.0021 | 0.0298 | 0.9200 | 0.0000 | 0.0800 | 1.145 | 0.0673 | 0.590 | 0.000 | 15.0 | 1.572 | 0.9000 | 115.5 | 1.000 |
| P8 | h5 | large | 0.0000 | -0.0029 | -0.0029 | 0.0518 | 0.8800 | 0.0600 | 0.0600 | 0.997 | 0.1302 | 0.220 | 0.580 | 6.9 | 1.283 | 0.6500 | n/a | 0.990 |
| P8 | h5 | carries | 0.1177 | 0.1186 | 0.0010 | 0.0115 | 0.9100 | 0.0000 | 0.0900 | 1.129 | 0.0252 | 0.580 | 0.000 | 15.1 | 1.497 | 0.9000 | 153.1 | 0.990 |
| P8 | h5 | depends | 0.0847 | 0.0852 | 0.0004 | 0.0049 | 0.9000 | 0.0000 | 0.1000 | 1.176 | 0.0108 | 0.590 | 0.000 | 15.1 | 1.225 | 0.8900 | 78.8 | 0.990 |
| P8 | h5 | carried_margin | 0.4183 | 0.4201 | 0.0017 | 0.0197 | 0.9000 | 0.0000 | 0.1000 | 1.190 | 0.0447 | 0.570 | 0.000 | 15.2 | 1.239 | 0.8900 | n/a | 0.990 |
| P8 | h5 | own_margin | 4.9368 | 4.9356 | -0.0011 | 0.0598 | 0.9700 | 0.0300 | 0.0000 | 1.171 | 0.1350 | 0.580 | 0.030 | 13.2 | 0.891 | 0.9000 | n/a | 0.990 |
| P8 | h5 | kappa | 0.6943 | 0.6945 | 0.0002 | 0.0339 | 0.9100 | 0.0700 | 0.0200 | 1.077 | 0.0754 | 0.630 | 0.000 | 15.1 | 1.433 | 0.9100 | 10.3 | 0.990 |
| P8 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4230 | -0.0046 | 0.0575 | 0.9000 | 0.0600 | 0.0400 | 0.914 | 0.1380 | 0.170 | 0.580 | 6.8 | 1.197 | 0.6200 | n/a | 0.990 |
| P8 | h5 | carried_added | 0.6025 | 0.6076 | 0.0051 | 0.0575 | 0.9000 | 0.0000 | 0.1000 | 1.132 | 0.1266 | 0.580 | 0.000 | 15.1 | 1.549 | 0.9100 | n/a | 0.990 |
| P8 | h5 | pooled_retention | 0.1177 | 0.1186 | 0.0010 | 0.0113 | 0.9100 | 0.0000 | 0.0900 | 1.119 | 0.0247 | 0.600 | 0.000 | 15.1 | 1.588 | 0.9100 | 141.0 | 0.990 |
| P8 | h10 | large | 0.0000 | 0.0096 | 0.0096 | 0.0378 | 0.9100 | 0.0800 | 0.0100 | 0.929 | 0.0789 | 0.080 | 0.540 | 8.3 | 1.205 | 0.6800 | n/a | 0.187 |
| P8 | h10 | carries | 0.0553 | 0.0515 | -0.0038 | 0.0038 | 0.7200 | 0.0000 | 0.2800 | 1.385 | 0.0092 | 0.550 | 0.000 | 15.1 | 2.505 | 0.7200 | 120.6 | 0.187 |
| P8 | h10 | depends | 0.0390 | 0.0376 | -0.0014 | 0.0015 | 0.7900 | 0.0000 | 0.2100 | 1.549 | 0.0037 | 0.560 | 0.010 | 14.3 | 1.689 | 0.7300 | 110.6 | 0.187 |
| P8 | h10 | carried_margin | 0.4183 | 0.4041 | -0.0142 | 0.0147 | 0.7500 | 0.0000 | 0.2500 | 1.503 | 0.0369 | 0.540 | 0.020 | 14.6 | 1.792 | 0.7200 | n/a | 0.187 |
| P8 | h10 | own_margin | 10.7131 | 10.7371 | 0.0240 | 0.1006 | 0.9700 | 0.0300 | 0.0000 | 1.275 | 0.2109 | 0.510 | 0.240 | 10.2 | 0.816 | 0.8500 | n/a | 0.187 |
| P8 | h10 | kappa | 0.6943 | 0.7226 | 0.0283 | 0.0289 | 0.7500 | 0.2500 | 0.0000 | 1.242 | 0.0708 | 0.530 | 0.000 | 15.2 | 2.014 | 0.7300 | 11.9 | 0.187 |
| P8 | h10 | shuffled_vs_yardstick | -0.4183 | -0.3945 | 0.0238 | 0.0400 | 0.8100 | 0.1800 | 0.0100 | 0.871 | 0.0853 | 0.070 | 0.660 | 7.7 | 2.043 | 0.5800 | n/a | 0.187 |
| P8 | h10 | carried_added | 0.6025 | 0.5608 | -0.0417 | 0.0416 | 0.7200 | 0.0000 | 0.2800 | 1.387 | 0.0997 | 0.580 | 0.000 | 15.2 | 2.508 | 0.7200 | n/a | 0.187 |
| P8 | h10 | pooled_retention | 0.0553 | 0.0514 | -0.0038 | 0.0038 | 0.7200 | 0.0000 | 0.2800 | 1.370 | 0.0091 | 0.600 | 0.000 | 15.2 | 2.520 | 0.7200 | 127.8 | 0.187 |
| P9 | n20 | large | -0.3274 | -0.3270 | 0.0004 | 0.0374 | 0.9700 | 0.0300 | 0.0000 | 1.560 | 0.0979 | 0.620 | 0.020 | 13.8 | 0.911 | 0.9100 | n/a | n/a |
| P9 | n20 | carries | 0.4483 | 0.4447 | -0.0036 | 0.0433 | 0.9400 | 0.0000 | 0.0600 | 1.302 | 0.1006 | 0.560 | 0.020 | 13.9 | 1.011 | 0.8700 | 9.8 | n/a |
| P9 | n20 | depends | 0.2000 | 0.1976 | -0.0024 | 0.0666 | 0.9800 | 0.0000 | 0.0200 | 1.402 | 0.1595 | 0.590 | 0.000 | 15.0 | 0.854 | 0.9600 | 15.0 | n/a |
| P9 | n20 | carried_margin | 0.0819 | 0.0801 | -0.0018 | 0.0264 | 0.9700 | 0.0000 | 0.0300 | 1.385 | 0.0622 | 0.570 | 0.000 | 15.0 | 0.827 | 0.9200 | n/a | n/a |
| P9 | n20 | own_margin | 0.4093 | 0.4071 | -0.0022 | 0.0249 | 0.8900 | 0.0000 | 0.1100 | 1.420 | 0.0603 | 0.610 | 0.110 | 12.0 | 1.186 | 0.8300 | n/a | n/a |
| P9 | n20 | kappa | 0.3077 | 0.3071 | -0.0006 | 0.0964 | 0.9300 | 0.0500 | 0.0200 | 1.176 | 0.2300 | 0.570 | 0.000 | 15.3 | 1.080 | 0.9300 | 7.2 | n/a |
| P9 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4071 | 0.0022 | 0.0249 | 0.8900 | 0.1100 | 0.0000 | 1.420 | 0.0603 | 0.610 | 0.110 | 12.0 | 1.186 | 0.8300 | n/a | n/a |
| P9 | n20 | carried_added | 0.2661 | 0.2624 | -0.0037 | 0.0382 | 0.9000 | 0.0000 | 0.1000 | 1.010 | 0.0764 | 0.560 | 0.000 | 15.2 | 1.089 | 0.8900 | n/a | n/a |
| P9 | n20 | pooled_retention | 0.4483 | 0.4464 | -0.0019 | 0.0433 | 0.8700 | 0.0000 | 0.1300 | 1.098 | 0.0947 | 0.570 | 0.000 | 15.0 | 2.302 | 0.8600 | 10.4 | n/a |
| P9 | n40 | large | -0.0564 | -0.0598 | -0.0034 | 0.0505 | 0.9800 | 0.0000 | 0.0200 | 1.585 | 0.1332 | 0.580 | 0.020 | 13.8 | 0.706 | 0.9600 | n/a | n/a |
| P9 | n40 | carries | 0.2756 | 0.2753 | -0.0004 | 0.0346 | 1.0000 | 0.0000 | 0.0000 | 1.233 | 0.0815 | 0.530 | 0.000 | 14.5 | 0.713 | 0.9700 | 9.3 | n/a |
| P9 | n40 | depends | 0.2000 | 0.2001 | 0.0001 | 0.0333 | 0.9800 | 0.0000 | 0.0200 | 1.306 | 0.0805 | 0.520 | 0.000 | 14.4 | 0.859 | 0.9600 | 9.5 | n/a |
| P9 | n40 | carried_margin | 0.3529 | 0.3471 | -0.0058 | 0.0505 | 0.9700 | 0.0000 | 0.0300 | 1.388 | 0.1244 | 0.550 | 0.000 | 14.5 | 0.886 | 0.9600 | n/a | n/a |
| P9 | n40 | own_margin | 1.7645 | 1.7484 | -0.0161 | 0.1824 | 0.9400 | 0.0100 | 0.0500 | 1.044 | 0.3967 | 0.570 | 0.000 | 14.5 | 1.033 | 0.9000 | n/a | n/a |
| P9 | n40 | kappa | 0.6571 | 0.6566 | -0.0005 | 0.0480 | 0.9900 | 0.0100 | 0.0000 | 1.284 | 0.1185 | 0.550 | 0.000 | 15.2 | 0.871 | 0.9600 | 6.8 | n/a |
| P9 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4069 | 0.0024 | 0.0248 | 0.9000 | 0.1000 | 0.0000 | 1.422 | 0.0602 | 0.600 | 0.110 | 12.0 | 1.202 | 0.8400 | n/a | n/a |
| P9 | n40 | carried_added | 0.5371 | 0.5296 | -0.0075 | 0.0746 | 0.9100 | 0.0000 | 0.0900 | 1.120 | 0.1639 | 0.540 | 0.000 | 15.2 | 1.258 | 0.9000 | n/a | n/a |
| P9 | n40 | pooled_retention | 0.2756 | 0.2743 | -0.0013 | 0.0265 | 0.8700 | 0.0000 | 0.1300 | 1.107 | 0.0587 | 0.510 | 0.000 | 15.1 | 2.336 | 0.8600 | 9.4 | n/a |
| P9 | n80 | large | 1.5066 | 1.5013 | -0.0053 | 0.2182 | 0.9600 | 0.0100 | 0.0300 | 1.236 | 0.5105 | 0.530 | 0.070 | 12.7 | 0.806 | 0.9200 | n/a | n/a |
| P9 | n80 | carries | 0.2151 | 0.2189 | 0.0038 | 0.0314 | 0.9400 | 0.0100 | 0.0500 | 1.426 | 0.0770 | 0.520 | 0.050 | 13.0 | 1.026 | 0.9500 | 11.8 | n/a |
| P9 | n80 | depends | 0.2000 | 0.2038 | 0.0038 | 0.0291 | 0.9500 | 0.0100 | 0.0400 | 1.466 | 0.0724 | 0.530 | 0.050 | 12.8 | 0.977 | 0.9500 | 11.4 | n/a |
| P9 | n80 | carried_margin | 1.9159 | 1.9083 | -0.0075 | 0.2256 | 0.9600 | 0.0100 | 0.0300 | 1.234 | 0.5337 | 0.500 | 0.070 | 12.9 | 0.914 | 0.9100 | n/a | n/a |
| P9 | n80 | own_margin | 9.5794 | 9.4163 | -0.1631 | 0.6136 | 0.9800 | 0.0000 | 0.0200 | 1.943 | 1.7280 | 0.480 | 0.150 | 11.6 | 0.632 | 0.9700 | n/a | n/a |
| P9 | n80 | kappa | 0.9123 | 0.9133 | 0.0010 | 0.0117 | 0.9200 | 0.0700 | 0.0100 | 1.173 | 0.0271 | 0.500 | 0.030 | 13.8 | 1.102 | 0.8800 | 7.4 | n/a |
| P9 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4070 | 0.0023 | 0.0249 | 0.8900 | 0.1100 | 0.0000 | 1.421 | 0.0608 | 0.590 | 0.110 | 11.9 | 1.215 | 0.8300 | n/a | n/a |
| P9 | n80 | carried_added | 2.1001 | 2.0907 | -0.0094 | 0.2568 | 0.9500 | 0.0100 | 0.0400 | 1.185 | 0.5893 | 0.500 | 0.050 | 13.4 | 0.955 | 0.9200 | n/a | n/a |
| P9 | n80 | pooled_retention | 0.2151 | 0.2140 | -0.0011 | 0.0209 | 0.8700 | 0.0000 | 0.1300 | 1.083 | 0.0463 | 0.500 | 0.000 | 15.1 | 2.307 | 0.8600 | 12.3 | n/a |
| P9 | n160 | large | 3.9734 | 3.9919 | 0.0185 | 0.4742 | 0.9500 | 0.0000 | 0.0500 | 1.130 | 1.0445 | 0.650 | 0.030 | 14.3 | 0.965 | 0.9000 | n/a | n/a |
| P9 | n160 | carries | 0.2067 | 0.2088 | 0.0021 | 0.0314 | 0.9300 | 0.0000 | 0.0700 | 1.226 | 0.0720 | 0.580 | 0.010 | 14.6 | 1.473 | 0.9000 | 16.2 | n/a |
| P9 | n160 | depends | 0.2000 | 0.2022 | 0.0022 | 0.0301 | 0.9300 | 0.0000 | 0.0700 | 1.234 | 0.0691 | 0.580 | 0.010 | 14.5 | 1.637 | 0.9000 | 15.7 | n/a |
| P9 | n160 | carried_margin | 4.3827 | 4.3988 | 0.0161 | 0.4830 | 0.9500 | 0.0000 | 0.0500 | 1.133 | 1.0762 | 0.630 | 0.030 | 14.4 | 0.936 | 0.8900 | n/a | n/a |
| P9 | n160 | own_margin | 21.9134 | 21.9011 | -0.0123 | 1.2302 | 0.9600 | 0.0400 | 0.0000 | 1.319 | 3.0220 | 0.590 | 0.090 | 12.4 | 0.907 | 0.9200 | n/a | n/a |
| P9 | n160 | kappa | 0.9597 | 0.9605 | 0.0008 | 0.0050 | 0.8800 | 0.1100 | 0.0100 | 1.106 | 0.0112 | 0.650 | 0.000 | 14.8 | 1.549 | 0.8600 | 8.5 | n/a |
| P9 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4069 | 0.0024 | 0.0251 | 0.9000 | 0.1000 | 0.0000 | 1.398 | 0.0606 | 0.610 | 0.110 | 12.0 | 1.229 | 0.8300 | n/a | n/a |
| P9 | n160 | carried_added | 4.5669 | 4.5813 | 0.0144 | 0.5170 | 0.9500 | 0.0000 | 0.0500 | 1.122 | 1.1600 | 0.630 | 0.030 | 14.5 | 0.960 | 0.8800 | n/a | n/a |
| P9 | n160 | pooled_retention | 0.2067 | 0.2057 | -0.0009 | 0.0199 | 0.8700 | 0.0000 | 0.1300 | 1.094 | 0.0439 | 0.530 | 0.000 | 15.1 | 2.443 | 0.8700 | 16.5 | n/a |
| P9 | n320 | large | 4.6436 | 4.6219 | -0.0217 | 0.5232 | 0.9300 | 0.0000 | 0.0700 | 1.172 | 1.1748 | 0.590 | 0.000 | 14.7 | 1.246 | 0.9100 | n/a | n/a |
| P9 | n320 | carries | 0.2058 | 0.2046 | -0.0012 | 0.0295 | 0.9100 | 0.0000 | 0.0900 | 1.287 | 0.0687 | 0.570 | 0.010 | 14.5 | 1.272 | 0.9000 | 17.6 | n/a |
| P9 | n320 | depends | 0.2000 | 0.1989 | -0.0011 | 0.0284 | 0.9200 | 0.0000 | 0.0800 | 1.298 | 0.0667 | 0.570 | 0.010 | 14.5 | 1.796 | 0.9000 | 17.1 | n/a |
| P9 | n320 | carried_margin | 5.0529 | 5.0291 | -0.0238 | 0.5322 | 0.9300 | 0.0000 | 0.0700 | 1.175 | 1.2088 | 0.600 | 0.000 | 14.7 | 1.227 | 0.9100 | n/a | n/a |
| P9 | n320 | own_margin | 25.2643 | 25.4337 | 0.1693 | 1.3120 | 0.9600 | 0.0400 | 0.0000 | 1.307 | 3.2648 | 0.580 | 0.090 | 12.8 | 0.785 | 0.9100 | n/a | n/a |
| P9 | n320 | kappa | 0.9648 | 0.9653 | 0.0005 | 0.0044 | 0.8700 | 0.1200 | 0.0100 | 1.067 | 0.0098 | 0.610 | 0.000 | 15.0 | 1.430 | 0.8600 | 8.7 | n/a |
| P9 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4072 | 0.0021 | 0.0250 | 0.9000 | 0.1000 | 0.0000 | 1.412 | 0.0603 | 0.620 | 0.110 | 12.0 | 1.212 | 0.8500 | n/a | n/a |
| P9 | n320 | carried_added | 5.2371 | 5.2113 | -0.0257 | 0.5666 | 0.9200 | 0.0000 | 0.0800 | 1.163 | 1.2781 | 0.600 | 0.000 | 14.8 | 1.300 | 0.8900 | n/a | n/a |
| P9 | n320 | pooled_retention | 0.2058 | 0.2048 | -0.0010 | 0.0200 | 0.8700 | 0.0000 | 0.1300 | 1.078 | 0.0436 | 0.470 | 0.000 | 15.1 | 2.378 | 0.8700 | 17.8 | n/a |
| P9 | h2 | large | -0.0642 | -0.0627 | 0.0015 | 0.0223 | 0.9800 | 0.0200 | 0.0000 | 1.527 | 0.0541 | 0.610 | 0.170 | 11.9 | 0.902 | 0.9500 | n/a | 1.000 |
| P9 | h2 | carries | 0.2772 | 0.2759 | -0.0012 | 0.0256 | 0.8700 | 0.0000 | 0.1300 | 1.052 | 0.0546 | 0.590 | 0.000 | 15.1 | 2.051 | 0.8600 | 118.3 | 1.000 |
| P9 | h2 | depends | 0.2000 | 0.1997 | -0.0003 | 0.0111 | 0.8700 | 0.0000 | 0.1300 | 1.103 | 0.0236 | 0.580 | 0.000 | 15.2 | 1.647 | 0.8500 | 56.2 | 1.000 |
| P9 | h2 | carried_margin | 0.3451 | 0.3443 | -0.0008 | 0.0136 | 0.8800 | 0.0000 | 0.1200 | 1.116 | 0.0303 | 0.610 | 0.000 | 15.2 | 1.402 | 0.8700 | n/a | 1.000 |
| P9 | h2 | own_margin | 1.7255 | 1.7254 | -0.0001 | 0.0301 | 0.9300 | 0.0700 | 0.0000 | 1.121 | 0.0658 | 0.600 | 0.000 | 15.2 | 1.425 | 0.8900 | n/a | 1.000 |
| P9 | h2 | kappa | 0.6520 | 0.6575 | 0.0055 | 0.0400 | 0.8600 | 0.1300 | 0.0100 | 1.001 | 0.0868 | 0.560 | 0.000 | 15.1 | 2.018 | 0.8600 | 10.0 | 1.000 |
| P9 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4070 | 0.0023 | 0.0250 | 0.8900 | 0.1100 | 0.0000 | 1.406 | 0.0601 | 0.590 | 0.110 | 12.0 | 1.226 | 0.8500 | n/a | 1.000 |
| P9 | h2 | carried_added | 0.5293 | 0.5267 | -0.0026 | 0.0519 | 0.8700 | 0.0000 | 0.1300 | 1.053 | 0.1135 | 0.620 | 0.000 | 15.1 | 2.210 | 0.8600 | n/a | 1.000 |
| P9 | h2 | pooled_retention | 0.2772 | 0.2761 | -0.0011 | 0.0269 | 0.8700 | 0.0000 | 0.1300 | 1.072 | 0.0591 | 0.610 | 0.000 | 15.0 | 2.238 | 0.8600 | 123.1 | 1.000 |
| P9 | h5 | large | 0.5757 | 0.5744 | -0.0013 | 0.0675 | 0.9100 | 0.0000 | 0.0900 | 1.064 | 0.1401 | 0.530 | 0.000 | 14.2 | 1.471 | 0.8600 | n/a | 0.990 |
| P9 | h5 | carries | 0.2288 | 0.2279 | -0.0010 | 0.0228 | 0.8700 | 0.0000 | 0.1300 | 1.068 | 0.0494 | 0.600 | 0.000 | 15.1 | 2.196 | 0.8700 | 158.2 | 0.990 |
| P9 | h5 | depends | 0.2000 | 0.1994 | -0.0006 | 0.0173 | 0.8700 | 0.0000 | 0.1300 | 1.083 | 0.0373 | 0.620 | 0.000 | 15.2 | 2.310 | 0.8600 | 76.9 | 0.990 |
| P9 | h5 | carried_margin | 0.9850 | 0.9815 | -0.0035 | 0.0743 | 0.8700 | 0.0000 | 0.1300 | 1.074 | 0.1602 | 0.620 | 0.000 | 15.2 | 2.063 | 0.8600 | n/a | 0.990 |
| P9 | h5 | own_margin | 4.9248 | 4.9269 | 0.0020 | 0.0595 | 0.9300 | 0.0700 | 0.0000 | 1.130 | 0.1414 | 0.600 | 0.040 | 13.6 | 1.049 | 0.8700 | n/a | 0.990 |
| P9 | h5 | kappa | 0.8425 | 0.8450 | 0.0025 | 0.0182 | 0.8500 | 0.1300 | 0.0200 | 0.985 | 0.0391 | 0.580 | 0.000 | 15.1 | 2.053 | 0.8600 | 10.3 | 0.990 |
| P9 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4071 | 0.0022 | 0.0253 | 0.9100 | 0.0900 | 0.0000 | 1.553 | 0.0633 | 0.510 | 0.200 | 10.9 | 1.365 | 0.8200 | n/a | 0.990 |
| P9 | h5 | carried_added | 1.1692 | 1.1639 | -0.0052 | 0.1131 | 0.8700 | 0.0000 | 0.1300 | 1.065 | 0.2451 | 0.640 | 0.000 | 15.1 | 2.257 | 0.8600 | n/a | 0.990 |
| P9 | h5 | pooled_retention | 0.2288 | 0.2276 | -0.0012 | 0.0222 | 0.8700 | 0.0000 | 0.1300 | 1.053 | 0.0481 | 0.510 | 0.000 | 15.1 | 2.300 | 0.8600 | 156.5 | 0.990 |
| P9 | h10 | large | 1.7261 | 1.6217 | -0.1045 | 0.1304 | 0.7400 | 0.0000 | 0.2600 | 1.345 | 0.3148 | 0.660 | 0.000 | 15.1 | 2.111 | 0.7400 | n/a | 0.169 |
| P9 | h10 | carries | 0.2136 | 0.2006 | -0.0130 | 0.0146 | 0.7600 | 0.0000 | 0.2400 | 1.521 | 0.0375 | 0.610 | 0.000 | 15.1 | 2.370 | 0.7500 | 144.9 | 0.169 |
| P9 | h10 | depends | 0.2000 | 0.1887 | -0.0113 | 0.0128 | 0.7600 | 0.0000 | 0.2400 | 1.536 | 0.0330 | 0.610 | 0.000 | 15.1 | 2.586 | 0.7500 | 124.9 | 0.169 |
| P9 | h10 | carried_margin | 2.1354 | 2.0180 | -0.1175 | 0.1313 | 0.7600 | 0.0000 | 0.2400 | 1.507 | 0.3316 | 0.620 | 0.000 | 15.2 | 2.378 | 0.7500 | n/a | 0.169 |
| P9 | h10 | own_margin | 10.6772 | 10.6985 | 0.0213 | 0.0660 | 0.9500 | 0.0300 | 0.0200 | 2.303 | 0.1844 | 0.570 | 0.250 | 10.9 | 0.849 | 0.9300 | n/a | 0.169 |
| P9 | h10 | kappa | 0.9206 | 0.9271 | 0.0065 | 0.0073 | 0.7600 | 0.2400 | 0.0000 | 1.324 | 0.0185 | 0.600 | 0.000 | 15.1 | 2.370 | 0.7500 | 11.0 | 0.169 |
| P9 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3963 | 0.0130 | 0.0216 | 0.8000 | 0.2000 | 0.0000 | 1.328 | 0.0466 | 0.570 | 0.050 | 14.0 | 1.596 | 0.7600 | n/a | 0.169 |
| P9 | h10 | carried_added | 2.3196 | 2.1779 | -0.1417 | 0.1585 | 0.7600 | 0.0000 | 0.2400 | 1.500 | 0.4006 | 0.630 | 0.000 | 15.2 | 2.455 | 0.7500 | n/a | 0.169 |
| P9 | h10 | pooled_retention | 0.2136 | 0.2004 | -0.0131 | 0.0144 | 0.7600 | 0.0000 | 0.2400 | 1.529 | 0.0369 | 0.640 | 0.000 | 15.2 | 2.572 | 0.7500 | 143.4 | 0.169 |
| P10 | n20 | large | -0.3345 | -0.3302 | 0.0043 | 0.0614 | 0.8800 | 0.1200 | 0.0000 | 0.804 | 0.1073 | 0.400 | 0.070 | 12.2 | 1.291 | 0.7800 | n/a | n/a |
| P10 | n20 | carries | 0.4447 | 0.4524 | 0.0077 | 0.0546 | 0.8800 | 0.0000 | 0.1200 | 1.001 | 0.1150 | 0.610 | 0.010 | 14.1 | 1.883 | 0.8400 | 8.9 | n/a |
| P10 | n20 | depends | 0.2000 | 0.2101 | 0.0101 | 0.0866 | 0.9300 | 0.0100 | 0.0600 | 0.991 | 0.1799 | 0.270 | 0.010 | 14.4 | 1.023 | 0.8700 | 9.9 | n/a |
| P10 | n20 | carried_margin | 0.0836 | 0.0875 | 0.0039 | 0.0384 | 0.9500 | 0.0100 | 0.0400 | 0.990 | 0.0763 | 0.070 | 0.080 | 12.7 | 1.002 | 0.8400 | n/a | n/a |
| P10 | n20 | own_margin | 0.4181 | 0.4177 | -0.0004 | 0.0589 | 0.9200 | 0.0000 | 0.0800 | 0.764 | 0.1253 | 0.130 | 0.670 | 5.9 | 1.132 | 0.5600 | n/a | n/a |
| P10 | n20 | kappa | 0.3122 | 0.3183 | 0.0061 | 0.1155 | 0.9400 | 0.0500 | 0.0100 | 0.941 | 0.2399 | 0.070 | 0.000 | 15.0 | 1.049 | 0.9300 | 6.5 | n/a |
| P10 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4177 | 0.0004 | 0.0589 | 0.9200 | 0.0800 | 0.0000 | 0.764 | 0.1253 | 0.130 | 0.670 | 5.9 | 1.132 | 0.5600 | n/a | n/a |
| P10 | n20 | carried_added | 0.2678 | 0.2716 | 0.0038 | 0.0462 | 0.9300 | 0.0000 | 0.0700 | 0.946 | 0.0871 | 0.080 | 0.020 | 14.4 | 1.254 | 0.8900 | n/a | n/a |
| P10 | n20 | pooled_retention | 0.4447 | 0.4444 | -0.0002 | 0.0433 | 0.8800 | 0.0000 | 0.1200 | 1.054 | 0.0934 | 0.830 | 0.000 | 15.0 | 2.216 | 0.8600 | 8.3 | n/a |
| P10 | n40 | large | -0.0573 | -0.0585 | -0.0012 | 0.0639 | 0.9600 | 0.0000 | 0.0400 | 1.083 | 0.1388 | 0.640 | 0.020 | 13.7 | 0.807 | 0.9400 | n/a | n/a |
| P10 | n40 | carries | 0.2741 | 0.2756 | 0.0015 | 0.0361 | 0.9400 | 0.0100 | 0.0500 | 1.127 | 0.0808 | 0.620 | 0.010 | 14.3 | 1.026 | 0.9100 | 8.3 | n/a |
| P10 | n40 | depends | 0.2000 | 0.2012 | 0.0012 | 0.0361 | 0.9500 | 0.0000 | 0.0500 | 1.123 | 0.0802 | 0.590 | 0.020 | 14.2 | 1.023 | 0.9400 | 8.4 | n/a |
| P10 | n40 | carried_margin | 0.3608 | 0.3594 | -0.0014 | 0.0718 | 0.9600 | 0.0000 | 0.0400 | 1.014 | 0.1533 | 0.160 | 0.150 | 11.1 | 0.913 | 0.8500 | n/a | n/a |
| P10 | n40 | own_margin | 1.8041 | 1.7970 | -0.0070 | 0.2501 | 0.9200 | 0.0000 | 0.0800 | 0.883 | 0.5027 | 0.160 | 0.220 | 10.2 | 1.149 | 0.8300 | n/a | n/a |
| P10 | n40 | kappa | 0.6620 | 0.6596 | -0.0024 | 0.0599 | 0.9600 | 0.0300 | 0.0100 | 0.958 | 0.1232 | 0.170 | 0.020 | 14.2 | 0.946 | 0.8900 | 6.3 | n/a |
| P10 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4178 | 0.0003 | 0.0589 | 0.9200 | 0.0800 | 0.0000 | 0.766 | 0.1270 | 0.110 | 0.670 | 6.0 | 1.134 | 0.5700 | n/a | n/a |
| P10 | n40 | carried_added | 0.5450 | 0.5433 | -0.0017 | 0.0877 | 0.9400 | 0.0000 | 0.0600 | 1.028 | 0.1790 | 0.150 | 0.030 | 13.6 | 1.175 | 0.9000 | n/a | n/a |
| P10 | n40 | pooled_retention | 0.2741 | 0.2739 | -0.0002 | 0.0270 | 0.8800 | 0.0000 | 0.1200 | 1.029 | 0.0587 | 0.790 | 0.000 | 15.1 | 2.208 | 0.8700 | 8.3 | n/a |
| P10 | n80 | large | 1.5193 | 1.5257 | 0.0064 | 0.2933 | 0.9700 | 0.0000 | 0.0300 | 1.068 | 0.6826 | 0.250 | 0.350 | 8.9 | 0.863 | 0.8400 | n/a | n/a |
| P10 | n80 | carries | 0.2149 | 0.2136 | -0.0013 | 0.0324 | 0.9600 | 0.0000 | 0.0400 | 1.274 | 0.0736 | 0.650 | 0.050 | 13.4 | 0.916 | 0.9200 | 7.8 | n/a |
| P10 | n80 | depends | 0.2000 | 0.1987 | -0.0013 | 0.0299 | 0.9700 | 0.0000 | 0.0300 | 1.312 | 0.0685 | 0.620 | 0.060 | 13.4 | 0.949 | 0.9200 | 7.7 | n/a |
| P10 | n80 | carried_margin | 1.9374 | 1.9434 | 0.0060 | 0.3346 | 0.9600 | 0.0100 | 0.0300 | 1.011 | 0.7863 | 0.140 | 0.480 | 8.4 | 0.841 | 0.7800 | n/a | n/a |
| P10 | n80 | own_margin | 9.6872 | 9.8525 | 0.1653 | 1.4413 | 0.9000 | 0.0500 | 0.0500 | 0.893 | 3.7911 | 0.130 | 0.650 | 6.0 | 1.222 | 0.6300 | n/a | n/a |
| P10 | n80 | kappa | 0.9132 | 0.9130 | -0.0002 | 0.0150 | 0.9200 | 0.0700 | 0.0100 | 1.058 | 0.0338 | 0.140 | 0.280 | 10.1 | 1.157 | 0.8400 | 6.1 | n/a |
| P10 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4177 | 0.0004 | 0.0589 | 0.9200 | 0.0800 | 0.0000 | 0.764 | 0.1252 | 0.110 | 0.680 | 5.9 | 1.156 | 0.5600 | n/a | n/a |
| P10 | n80 | carried_added | 2.1216 | 2.1275 | 0.0059 | 0.3559 | 0.9700 | 0.0000 | 0.0300 | 1.013 | 0.8006 | 0.140 | 0.350 | 9.3 | 0.857 | 0.8100 | n/a | n/a |
| P10 | n80 | pooled_retention | 0.2149 | 0.2151 | 0.0001 | 0.0211 | 0.8800 | 0.0000 | 0.1200 | 1.029 | 0.0442 | 0.790 | 0.000 | 15.0 | 2.026 | 0.8700 | 7.5 | n/a |
| P10 | n160 | large | 3.8799 | 3.8716 | -0.0083 | 0.4548 | 0.9700 | 0.0100 | 0.0200 | 1.110 | 1.0011 | 0.590 | 0.030 | 14.2 | 0.860 | 0.9300 | n/a | n/a |
| P10 | n160 | carries | 0.2068 | 0.2069 | 0.0001 | 0.0329 | 0.8900 | 0.0000 | 0.1100 | 1.084 | 0.0669 | 0.590 | 0.020 | 14.3 | 1.339 | 0.8800 | 15.1 | n/a |
| P10 | n160 | depends | 0.2000 | 0.2001 | 0.0001 | 0.0316 | 0.8900 | 0.0000 | 0.1100 | 1.088 | 0.0642 | 0.600 | 0.020 | 14.2 | 1.383 | 0.8800 | 14.8 | n/a |
| P10 | n160 | carried_margin | 4.2980 | 4.2894 | -0.0086 | 0.4801 | 0.9800 | 0.0000 | 0.0200 | 1.064 | 1.0427 | 0.560 | 0.040 | 14.2 | 0.881 | 0.9300 | n/a | n/a |
| P10 | n160 | own_margin | 21.4901 | 21.6035 | 0.1134 | 1.4060 | 0.9700 | 0.0200 | 0.0100 | 1.127 | 3.2312 | 0.440 | 0.120 | 10.8 | 0.879 | 0.9000 | n/a | n/a |
| P10 | n160 | kappa | 0.9589 | 0.9592 | 0.0003 | 0.0057 | 0.8800 | 0.1100 | 0.0100 | 0.906 | 0.0116 | 0.550 | 0.000 | 14.7 | 1.209 | 0.8700 | 8.6 | n/a |
| P10 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4179 | 0.0002 | 0.0587 | 0.9200 | 0.0800 | 0.0000 | 0.770 | 0.1248 | 0.120 | 0.650 | 5.9 | 1.161 | 0.5600 | n/a | n/a |
| P10 | n160 | carried_added | 4.4822 | 4.4734 | -0.0089 | 0.5121 | 0.9600 | 0.0000 | 0.0400 | 1.063 | 1.1067 | 0.560 | 0.030 | 14.3 | 0.943 | 0.9100 | n/a | n/a |
| P10 | n160 | pooled_retention | 0.2068 | 0.2066 | -0.0002 | 0.0205 | 0.8700 | 0.0000 | 0.1300 | 1.009 | 0.0431 | 0.580 | 0.000 | 15.0 | 2.131 | 0.8600 | 16.4 | n/a |
| P10 | n320 | large | 4.5814 | 4.5636 | -0.0178 | 0.5269 | 0.9300 | 0.0100 | 0.0600 | 1.100 | 1.1146 | 0.570 | 0.020 | 14.7 | 1.111 | 0.9200 | n/a | n/a |
| P10 | n320 | carries | 0.2059 | 0.2072 | 0.0013 | 0.0333 | 0.9400 | 0.0000 | 0.0600 | 1.040 | 0.0677 | 0.610 | 0.010 | 14.4 | 1.122 | 0.9000 | 17.2 | n/a |
| P10 | n320 | depends | 0.2000 | 0.2013 | 0.0013 | 0.0321 | 0.9400 | 0.0000 | 0.0600 | 1.042 | 0.0652 | 0.620 | 0.010 | 14.3 | 1.493 | 0.9000 | 16.8 | n/a |
| P10 | n320 | carried_margin | 4.9995 | 4.9814 | -0.0181 | 0.5501 | 0.9100 | 0.0100 | 0.0800 | 1.059 | 1.1764 | 0.520 | 0.010 | 14.7 | 1.152 | 0.9100 | n/a | n/a |
| P10 | n320 | own_margin | 24.9973 | 24.9388 | -0.0585 | 1.4206 | 0.9600 | 0.0300 | 0.0100 | 1.154 | 3.2364 | 0.580 | 0.110 | 12.1 | 0.859 | 0.9000 | n/a | n/a |
| P10 | n320 | kappa | 0.9645 | 0.9647 | 0.0002 | 0.0046 | 0.9100 | 0.0800 | 0.0100 | 0.980 | 0.0097 | 0.530 | 0.000 | 15.0 | 1.479 | 0.8700 | 8.9 | n/a |
| P10 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4178 | 0.0003 | 0.0589 | 0.9200 | 0.0800 | 0.0000 | 0.764 | 0.1262 | 0.120 | 0.670 | 6.0 | 1.146 | 0.5600 | n/a | n/a |
| P10 | n320 | carried_added | 5.1837 | 5.1654 | -0.0183 | 0.5839 | 0.9100 | 0.0100 | 0.0800 | 1.054 | 1.2367 | 0.520 | 0.010 | 14.8 | 1.213 | 0.9100 | n/a | n/a |
| P10 | n320 | pooled_retention | 0.2059 | 0.2054 | -0.0004 | 0.0201 | 0.8800 | 0.0000 | 0.1200 | 1.033 | 0.0427 | 0.550 | 0.000 | 15.1 | 2.396 | 0.8600 | 16.8 | n/a |
| P10 | h2 | large | -0.0724 | -0.0718 | 0.0006 | 0.0536 | 0.9200 | 0.0600 | 0.0200 | 0.813 | 0.1157 | 0.130 | 0.650 | 6.1 | 1.074 | 0.5600 | n/a | 1.000 |
| P10 | h2 | carries | 0.2770 | 0.2767 | -0.0003 | 0.0258 | 0.8800 | 0.0000 | 0.1200 | 1.015 | 0.0542 | 0.620 | 0.000 | 15.1 | 2.346 | 0.8500 | 116.8 | 1.000 |
| P10 | h2 | depends | 0.2000 | 0.2002 | 0.0002 | 0.0112 | 0.9000 | 0.0000 | 0.1000 | 1.078 | 0.0236 | 0.590 | 0.000 | 15.3 | 1.827 | 0.8700 | 56.2 | 1.000 |
| P10 | h2 | carried_margin | 0.3459 | 0.3460 | 0.0001 | 0.0139 | 0.9300 | 0.0000 | 0.0700 | 1.107 | 0.0301 | 0.440 | 0.000 | 15.4 | 1.342 | 0.9100 | n/a | 1.000 |
| P10 | h2 | own_margin | 1.7295 | 1.7301 | 0.0006 | 0.0315 | 0.9000 | 0.0900 | 0.0100 | 1.034 | 0.0650 | 0.470 | 0.000 | 15.1 | 1.313 | 0.8700 | n/a | 1.000 |
| P10 | h2 | kappa | 0.6525 | 0.6566 | 0.0041 | 0.0398 | 0.8600 | 0.1200 | 0.0200 | 0.966 | 0.0863 | 0.450 | 0.000 | 15.1 | 1.952 | 0.8500 | 10.2 | 1.000 |
| P10 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4178 | 0.0006 | 0.0590 | 0.9200 | 0.0800 | 0.0000 | 0.762 | 0.1255 | 0.120 | 0.660 | 5.9 | 1.153 | 0.5600 | n/a | 1.000 |
| P10 | h2 | carried_added | 0.5301 | 0.5300 | -0.0001 | 0.0524 | 0.8800 | 0.0000 | 0.1200 | 1.019 | 0.1105 | 0.430 | 0.000 | 15.1 | 2.239 | 0.8600 | n/a | 1.000 |
| P10 | h2 | pooled_retention | 0.2770 | 0.2770 | 0.0000 | 0.0273 | 0.8800 | 0.0000 | 0.1200 | 1.015 | 0.0571 | 0.570 | 0.000 | 15.1 | 2.180 | 0.8600 | 117.0 | 1.000 |
| P10 | h5 | large | 0.5690 | 0.5694 | 0.0004 | 0.0737 | 0.9500 | 0.0000 | 0.0500 | 1.138 | 0.1654 | 0.190 | 0.130 | 11.6 | 0.933 | 0.8200 | n/a | 1.000 |
| P10 | h5 | carries | 0.2288 | 0.2290 | 0.0002 | 0.0231 | 0.8700 | 0.0000 | 0.1300 | 1.027 | 0.0496 | 0.530 | 0.000 | 15.1 | 2.336 | 0.8600 | 141.4 | 1.000 |
| P10 | h5 | depends | 0.2000 | 0.2004 | 0.0004 | 0.0176 | 0.8700 | 0.0000 | 0.1300 | 1.041 | 0.0379 | 0.540 | 0.000 | 15.2 | 2.347 | 0.8600 | 79.8 | 1.000 |
| P10 | h5 | carried_margin | 0.9874 | 0.9877 | 0.0003 | 0.0764 | 0.8700 | 0.0000 | 0.1300 | 1.029 | 0.1639 | 0.500 | 0.000 | 15.2 | 1.957 | 0.8600 | n/a | 1.000 |
| P10 | h5 | own_margin | 4.9368 | 4.9341 | -0.0027 | 0.0586 | 0.9400 | 0.0500 | 0.0100 | 1.201 | 0.1374 | 0.460 | 0.080 | 12.6 | 1.091 | 0.9100 | n/a | 1.000 |
| P10 | h5 | kappa | 0.8428 | 0.8447 | 0.0019 | 0.0180 | 0.8500 | 0.1200 | 0.0300 | 0.971 | 0.0390 | 0.460 | 0.000 | 15.1 | 1.954 | 0.8600 | 10.3 | 1.000 |
| P10 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4183 | 0.0000 | 0.0591 | 0.9000 | 0.1000 | 0.0000 | 0.789 | 0.1296 | 0.140 | 0.630 | 6.1 | 1.442 | 0.5700 | n/a | 1.000 |
| P10 | h5 | carried_added | 1.1715 | 1.1717 | 0.0002 | 0.1157 | 0.8700 | 0.0000 | 0.1300 | 1.020 | 0.2508 | 0.550 | 0.000 | 15.1 | 2.125 | 0.8600 | n/a | 1.000 |
| P10 | h5 | pooled_retention | 0.2288 | 0.2288 | 0.0000 | 0.0226 | 0.8700 | 0.0000 | 0.1300 | 1.012 | 0.0488 | 0.550 | 0.000 | 15.1 | 2.118 | 0.8500 | 142.2 | 1.000 |
| P10 | h10 | large | 1.7243 | 1.6108 | -0.1135 | 0.1154 | 0.7600 | 0.0000 | 0.2400 | 1.654 | 0.3073 | 0.450 | 0.000 | 15.2 | 2.152 | 0.7400 | n/a | 0.171 |
| P10 | h10 | carries | 0.2135 | 0.1989 | -0.0146 | 0.0133 | 0.7300 | 0.0000 | 0.2700 | 1.658 | 0.0362 | 0.510 | 0.000 | 15.3 | 2.489 | 0.7300 | 118.6 | 0.171 |
| P10 | h10 | depends | 0.2000 | 0.1873 | -0.0127 | 0.0117 | 0.7300 | 0.0000 | 0.2700 | 1.679 | 0.0320 | 0.520 | 0.000 | 15.3 | 2.511 | 0.7300 | 106.7 | 0.171 |
| P10 | h10 | carried_margin | 2.1426 | 2.0136 | -0.1290 | 0.1202 | 0.7300 | 0.0000 | 0.2700 | 1.661 | 0.3199 | 0.440 | 0.000 | 15.2 | 2.466 | 0.7200 | n/a | 0.171 |
| P10 | h10 | own_margin | 10.7131 | 10.7537 | 0.0406 | 0.0998 | 0.9700 | 0.0300 | 0.0000 | 1.447 | 0.2240 | 0.460 | 0.340 | 9.8 | 0.936 | 0.8400 | n/a | 0.171 |
| P10 | h10 | kappa | 0.9208 | 0.9283 | 0.0074 | 0.0069 | 0.7200 | 0.2800 | 0.0000 | 1.399 | 0.0175 | 0.420 | 0.000 | 15.2 | 2.224 | 0.7100 | 11.8 | 0.171 |
| P10 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4028 | 0.0155 | 0.0441 | 0.8600 | 0.1300 | 0.0100 | 0.794 | 0.0828 | 0.040 | 0.600 | 8.1 | 1.344 | 0.5600 | n/a | 0.171 |
| P10 | h10 | carried_added | 2.3268 | 2.1703 | -0.1566 | 0.1450 | 0.7300 | 0.0000 | 0.2700 | 1.645 | 0.3861 | 0.430 | 0.000 | 15.2 | 2.524 | 0.7200 | n/a | 0.171 |
| P10 | h10 | pooled_retention | 0.2135 | 0.1990 | -0.0146 | 0.0133 | 0.7200 | 0.0000 | 0.2800 | 1.627 | 0.0354 | 0.490 | 0.000 | 15.2 | 2.480 | 0.7100 | 117.1 | 0.171 |
| P11 | n20 | large | -0.4093 | -0.4174 | -0.0081 | 0.0480 | 0.9000 | 0.1000 | 0.0000 | 1.165 | 0.1137 | 0.620 | 0.000 | 14.0 | 1.323 | 0.8600 | n/a | n/a |
| P11 | n20 | carries | 0.3104 | 0.3090 | -0.0014 | 0.0294 | 0.9600 | 0.0000 | 0.0400 | 1.420 | 0.0728 | 0.580 | 0.030 | 13.9 | 0.922 | 0.9400 | 9.3 | n/a |
| P11 | n20 | depends | 0.0000 | -0.0082 | -0.0082 | 0.0769 | 0.9500 | 0.0400 | 0.0100 | 0.872 | 0.1528 | 0.630 | 0.000 | 15.2 | 1.001 | 0.8700 | 13.9 | n/a |
| P11 | n20 | carried_margin | 0.0000 | -0.0041 | -0.0041 | 0.0315 | 0.9400 | 0.0500 | 0.0100 | 0.916 | 0.0646 | 0.600 | 0.000 | 15.2 | 1.040 | 0.8700 | n/a | n/a |
| P11 | n20 | own_margin | 0.4093 | 0.4133 | 0.0040 | 0.0265 | 0.9400 | 0.0000 | 0.0600 | 1.480 | 0.0680 | 0.610 | 0.130 | 12.3 | 1.076 | 0.8700 | n/a | n/a |
| P11 | n20 | kappa | 0.0000 | -0.0183 | -0.0183 | 0.1681 | 0.8800 | 0.0900 | 0.0300 | 0.827 | 0.3367 | 0.600 | 0.000 | 15.2 | 1.175 | 0.8700 | 7.1 | n/a |
| P11 | n20 | shuffled_vs_yardstick | -0.4093 | -0.4133 | -0.0040 | 0.0265 | 0.9400 | 0.0600 | 0.0000 | 1.480 | 0.0680 | 0.610 | 0.130 | 12.3 | 1.076 | 0.8700 | n/a | n/a |
| P11 | n20 | carried_added | 0.1842 | 0.1860 | 0.0018 | 0.0223 | 0.9300 | 0.0000 | 0.0700 | 1.453 | 0.0544 | 0.590 | 0.000 | 15.2 | 1.139 | 0.9200 | n/a | n/a |
| P11 | n20 | pooled_retention | 0.3104 | 0.3149 | 0.0045 | 0.0322 | 0.8900 | 0.0100 | 0.1000 | 1.033 | 0.0708 | 0.490 | 0.000 | 15.1 | 2.191 | 0.8900 | 10.1 | n/a |
| P11 | n40 | large | -0.4093 | -0.4172 | -0.0079 | 0.0490 | 0.9200 | 0.0800 | 0.0000 | 1.159 | 0.1156 | 0.630 | 0.020 | 13.7 | 1.178 | 0.8600 | n/a | n/a |
| P11 | n40 | carries | 0.0945 | 0.0944 | -0.0001 | 0.0109 | 0.9700 | 0.0100 | 0.0200 | 1.514 | 0.0280 | 0.690 | 0.000 | 14.5 | 0.844 | 0.9500 | 9.3 | n/a |
| P11 | n40 | depends | 0.0000 | -0.0013 | -0.0013 | 0.0177 | 0.9300 | 0.0500 | 0.0200 | 0.939 | 0.0366 | 0.600 | 0.000 | 15.2 | 1.191 | 0.8700 | 9.5 | n/a |
| P11 | n40 | carried_margin | 0.0000 | -0.0039 | -0.0039 | 0.0318 | 0.9200 | 0.0600 | 0.0200 | 0.959 | 0.0673 | 0.610 | 0.000 | 15.2 | 1.184 | 0.8700 | n/a | n/a |
| P11 | n40 | own_margin | 1.7645 | 1.7926 | 0.0281 | 0.1833 | 0.9500 | 0.0100 | 0.0400 | 1.088 | 0.4132 | 0.640 | 0.000 | 14.5 | 0.879 | 0.9400 | n/a | n/a |
| P11 | n40 | kappa | 0.0000 | -0.0175 | -0.0175 | 0.1727 | 0.9000 | 0.0800 | 0.0200 | 0.885 | 0.3548 | 0.600 | 0.000 | 15.2 | 1.290 | 0.8700 | 6.7 | n/a |
| P11 | n40 | shuffled_vs_yardstick | -0.4093 | -0.4133 | -0.0040 | 0.0266 | 0.9300 | 0.0700 | 0.0000 | 1.475 | 0.0685 | 0.600 | 0.110 | 12.3 | 1.147 | 0.8600 | n/a | n/a |
| P11 | n40 | carried_added | 0.1842 | 0.1862 | 0.0020 | 0.0223 | 0.9800 | 0.0000 | 0.0200 | 1.569 | 0.0594 | 0.590 | 0.000 | 15.1 | 0.786 | 0.9700 | n/a | n/a |
| P11 | n40 | pooled_retention | 0.0945 | 0.0961 | 0.0015 | 0.0100 | 0.8900 | 0.0100 | 0.1000 | 0.999 | 0.0216 | 0.570 | 0.000 | 15.1 | 2.124 | 0.8800 | 9.4 | n/a |
| P11 | n80 | large | -0.4093 | -0.4144 | -0.0051 | 0.0438 | 0.9100 | 0.0900 | 0.0000 | 1.363 | 0.1114 | 0.560 | 0.050 | 13.1 | 1.334 | 0.8900 | n/a | n/a |
| P11 | n80 | carries | 0.0189 | 0.0197 | 0.0008 | 0.0030 | 0.9500 | 0.0100 | 0.0400 | 1.184 | 0.0067 | 0.670 | 0.020 | 14.1 | 0.943 | 0.9200 | 12.5 | n/a |
| P11 | n80 | depends | 0.0000 | -0.0002 | -0.0002 | 0.0028 | 0.9000 | 0.0900 | 0.0100 | 1.175 | 0.0066 | 0.490 | 0.010 | 14.3 | 1.259 | 0.9000 | 12.1 | n/a |
| P11 | n80 | carried_margin | 0.0000 | -0.0013 | -0.0013 | 0.0257 | 0.9000 | 0.0900 | 0.0100 | 1.204 | 0.0604 | 0.540 | 0.010 | 14.2 | 1.230 | 0.9000 | n/a | n/a |
| P11 | n80 | own_margin | 9.5794 | 9.4895 | -0.0899 | 0.7505 | 0.9800 | 0.0000 | 0.0200 | 1.221 | 1.6932 | 0.630 | 0.090 | 12.3 | 0.818 | 0.9300 | n/a | n/a |
| P11 | n80 | kappa | 0.0000 | 0.0007 | 0.0007 | 0.1353 | 0.9100 | 0.0800 | 0.0100 | 1.139 | 0.3153 | 0.550 | 0.010 | 14.2 | 1.411 | 0.9000 | 7.6 | n/a |
| P11 | n80 | shuffled_vs_yardstick | -0.4093 | -0.4131 | -0.0038 | 0.0265 | 0.9300 | 0.0700 | 0.0000 | 1.486 | 0.0680 | 0.590 | 0.120 | 12.3 | 1.210 | 0.8700 | n/a | n/a |
| P11 | n80 | carried_added | 0.1842 | 0.1890 | 0.0048 | 0.0236 | 0.9400 | 0.0100 | 0.0500 | 1.151 | 0.0540 | 0.530 | 0.010 | 13.8 | 1.050 | 0.9000 | n/a | n/a |
| P11 | n80 | pooled_retention | 0.0189 | 0.0192 | 0.0003 | 0.0019 | 0.9000 | 0.0100 | 0.0900 | 1.043 | 0.0043 | 0.490 | 0.000 | 15.1 | 2.134 | 0.9000 | 12.3 | n/a |
| P11 | n160 | large | -0.4093 | -0.4168 | -0.0075 | 0.0433 | 0.8900 | 0.1100 | 0.0000 | 1.323 | 0.1050 | 0.560 | 0.010 | 13.5 | 1.434 | 0.8600 | n/a | n/a |
| P11 | n160 | carries | 0.0083 | 0.0086 | 0.0002 | 0.0013 | 0.9200 | 0.0000 | 0.0800 | 1.144 | 0.0030 | 0.620 | 0.000 | 14.8 | 1.380 | 0.9000 | 16.3 | n/a |
| P11 | n160 | depends | 0.0000 | -0.0002 | -0.0002 | 0.0012 | 0.9100 | 0.0800 | 0.0100 | 1.132 | 0.0026 | 0.600 | 0.000 | 15.1 | 1.441 | 0.9100 | 15.9 | n/a |
| P11 | n160 | carried_margin | 0.0000 | -0.0036 | -0.0036 | 0.0253 | 0.9200 | 0.0700 | 0.0100 | 1.071 | 0.0559 | 0.640 | 0.000 | 15.1 | 1.265 | 0.9100 | n/a | n/a |
| P11 | n160 | own_margin | 21.9134 | 21.7822 | -0.1311 | 1.3105 | 0.9700 | 0.0200 | 0.0100 | 1.173 | 2.9437 | 0.600 | 0.080 | 13.0 | 0.917 | 0.9300 | n/a | n/a |
| P11 | n160 | kappa | 0.0000 | -0.0105 | -0.0105 | 0.1330 | 0.9200 | 0.0700 | 0.0100 | 1.024 | 0.2890 | 0.640 | 0.000 | 15.1 | 1.421 | 0.9100 | 8.3 | n/a |
| P11 | n160 | shuffled_vs_yardstick | -0.4093 | -0.4132 | -0.0039 | 0.0267 | 0.9200 | 0.0800 | 0.0000 | 1.464 | 0.0679 | 0.590 | 0.120 | 12.4 | 1.260 | 0.8700 | n/a | n/a |
| P11 | n160 | carried_added | 0.1842 | 0.1866 | 0.0024 | 0.0223 | 0.9200 | 0.0000 | 0.0800 | 1.022 | 0.0497 | 0.630 | 0.000 | 14.9 | 1.380 | 0.8900 | n/a | n/a |
| P11 | n160 | pooled_retention | 0.0083 | 0.0085 | 0.0001 | 0.0009 | 0.8900 | 0.0100 | 0.1000 | 1.008 | 0.0019 | 0.470 | 0.000 | 15.1 | 2.263 | 0.8900 | 17.0 | n/a |
| P11 | n320 | large | -0.4093 | -0.4169 | -0.0075 | 0.0429 | 0.9000 | 0.1000 | 0.0000 | 1.327 | 0.1057 | 0.610 | 0.010 | 13.5 | 1.446 | 0.8600 | n/a | n/a |
| P11 | n320 | carries | 0.0072 | 0.0074 | 0.0001 | 0.0012 | 0.8900 | 0.0000 | 0.1100 | 1.129 | 0.0026 | 0.630 | 0.010 | 14.8 | 1.737 | 0.8800 | 17.2 | n/a |
| P11 | n320 | depends | 0.0000 | -0.0002 | -0.0002 | 0.0010 | 0.9100 | 0.0800 | 0.0100 | 1.165 | 0.0022 | 0.660 | 0.000 | 15.1 | 1.601 | 0.9100 | 16.6 | n/a |
| P11 | n320 | carried_margin | 0.0000 | -0.0037 | -0.0037 | 0.0243 | 0.9200 | 0.0700 | 0.0100 | 1.113 | 0.0546 | 0.660 | 0.000 | 15.1 | 1.295 | 0.9100 | n/a | n/a |
| P11 | n320 | own_margin | 25.2643 | 25.2919 | 0.0275 | 1.4218 | 0.9700 | 0.0300 | 0.0000 | 1.204 | 3.2408 | 0.610 | 0.050 | 13.1 | 0.916 | 0.9000 | n/a | n/a |
| P11 | n320 | kappa | 0.0000 | -0.0103 | -0.0103 | 0.1278 | 0.9200 | 0.0700 | 0.0100 | 1.064 | 0.2858 | 0.660 | 0.000 | 15.1 | 1.490 | 0.9100 | 8.5 | n/a |
| P11 | n320 | shuffled_vs_yardstick | -0.4093 | -0.4132 | -0.0039 | 0.0264 | 0.9300 | 0.0700 | 0.0000 | 1.485 | 0.0683 | 0.600 | 0.120 | 12.3 | 1.120 | 0.8600 | n/a | n/a |
| P11 | n320 | carried_added | 0.1842 | 0.1865 | 0.0023 | 0.0224 | 0.9200 | 0.0000 | 0.0800 | 0.990 | 0.0491 | 0.670 | 0.000 | 15.0 | 1.180 | 0.8600 | n/a | n/a |
| P11 | n320 | pooled_retention | 0.0072 | 0.0073 | 0.0001 | 0.0008 | 0.8900 | 0.0100 | 0.1000 | 1.026 | 0.0017 | 0.480 | 0.000 | 15.1 | 2.341 | 0.8900 | 18.1 | n/a |
| P11 | h2 | large | -0.4093 | -0.4163 | -0.0070 | 0.0427 | 0.8500 | 0.1500 | 0.0000 | 1.268 | 0.1078 | 0.600 | 0.030 | 13.6 | 1.686 | 0.8400 | n/a | 1.000 |
| P11 | h2 | carries | 0.0965 | 0.0978 | 0.0013 | 0.0094 | 0.8800 | 0.0100 | 0.1100 | 1.037 | 0.0206 | 0.590 | 0.000 | 15.1 | 2.041 | 0.8800 | 120.9 | 1.000 |
| P11 | h2 | depends | 0.0000 | -0.0021 | -0.0021 | 0.0137 | 0.8900 | 0.1000 | 0.0100 | 1.018 | 0.0299 | 0.580 | 0.000 | 15.1 | 2.515 | 0.8900 | 52.6 | 1.000 |
| P11 | h2 | carried_margin | 0.0000 | -0.0032 | -0.0032 | 0.0233 | 0.8900 | 0.1000 | 0.0100 | 1.005 | 0.0510 | 0.560 | 0.000 | 15.1 | 2.157 | 0.8900 | n/a | 1.000 |
| P11 | h2 | own_margin | 1.7255 | 1.7219 | -0.0036 | 0.0327 | 0.9100 | 0.0800 | 0.0100 | 1.053 | 0.0697 | 0.660 | 0.000 | 15.1 | 1.312 | 0.9000 | n/a | 1.000 |
| P11 | h2 | kappa | 0.0000 | -0.0048 | -0.0048 | 0.1235 | 0.8900 | 0.1000 | 0.0100 | 0.895 | 0.2595 | 0.570 | 0.000 | 15.1 | 1.851 | 0.8900 | 9.7 | 1.000 |
| P11 | h2 | shuffled_vs_yardstick | -0.4093 | -0.4131 | -0.0038 | 0.0265 | 0.9300 | 0.0700 | 0.0000 | 1.478 | 0.0677 | 0.600 | 0.120 | 12.3 | 1.268 | 0.8600 | n/a | 1.000 |
| P11 | h2 | carried_added | 0.1842 | 0.1871 | 0.0029 | 0.0190 | 0.8800 | 0.0100 | 0.1100 | 1.038 | 0.0414 | 0.580 | 0.000 | 15.1 | 2.255 | 0.8800 | n/a | 1.000 |
| P11 | h2 | pooled_retention | 0.0965 | 0.0979 | 0.0015 | 0.0100 | 0.8900 | 0.0100 | 0.1000 | 1.015 | 0.0216 | 0.630 | 0.000 | 15.0 | 2.301 | 0.8800 | 120.5 | 1.000 |
| P11 | h5 | large | -0.4093 | -0.4165 | -0.0072 | 0.0421 | 0.8500 | 0.1500 | 0.0000 | 1.363 | 0.1091 | 0.570 | 0.040 | 13.2 | 1.707 | 0.8300 | n/a | 0.990 |
| P11 | h5 | carries | 0.0361 | 0.0367 | 0.0006 | 0.0039 | 0.8900 | 0.0100 | 0.1000 | 1.005 | 0.0085 | 0.550 | 0.000 | 15.2 | 2.274 | 0.8800 | 156.6 | 0.990 |
| P11 | h5 | depends | 0.0000 | -0.0007 | -0.0007 | 0.0047 | 0.8900 | 0.1000 | 0.0100 | 1.061 | 0.0104 | 0.590 | 0.000 | 15.1 | 2.356 | 0.8900 | 76.0 | 0.990 |
| P11 | h5 | carried_margin | 0.0000 | -0.0032 | -0.0032 | 0.0227 | 0.8900 | 0.1000 | 0.0100 | 1.053 | 0.0506 | 0.590 | 0.000 | 15.1 | 2.230 | 0.8900 | n/a | 0.990 |
| P11 | h5 | own_margin | 4.9248 | 4.9158 | -0.0090 | 0.0583 | 0.9400 | 0.0500 | 0.0100 | 1.278 | 0.1378 | 0.580 | 0.030 | 13.7 | 1.020 | 0.8900 | n/a | 0.990 |
| P11 | h5 | kappa | 0.0000 | -0.0049 | -0.0049 | 0.1207 | 0.9000 | 0.0900 | 0.0100 | 0.935 | 0.2598 | 0.590 | 0.000 | 15.1 | 1.924 | 0.8900 | 9.6 | 0.990 |
| P11 | h5 | shuffled_vs_yardstick | -0.4093 | -0.4133 | -0.0040 | 0.0267 | 0.9300 | 0.0700 | 0.0000 | 1.627 | 0.0697 | 0.550 | 0.160 | 12.1 | 1.206 | 0.8500 | n/a | 0.990 |
| P11 | h5 | carried_added | 0.1842 | 0.1873 | 0.0031 | 0.0194 | 0.8900 | 0.0100 | 0.1000 | 0.993 | 0.0422 | 0.590 | 0.000 | 15.1 | 2.295 | 0.8800 | n/a | 0.990 |
| P11 | h5 | pooled_retention | 0.0361 | 0.0366 | 0.0006 | 0.0038 | 0.8900 | 0.0100 | 0.1000 | 1.008 | 0.0082 | 0.590 | 0.000 | 15.1 | 2.259 | 0.8800 | 152.2 | 0.990 |
| P11 | h10 | large | -0.4093 | -0.3861 | 0.0232 | 0.0280 | 0.7600 | 0.2400 | 0.0000 | 1.781 | 0.0732 | 0.560 | 0.020 | 14.6 | 2.413 | 0.7200 | n/a | 0.198 |
| P11 | h10 | carries | 0.0170 | 0.0161 | -0.0009 | 0.0012 | 0.7800 | 0.0000 | 0.2200 | 1.480 | 0.0031 | 0.600 | 0.000 | 15.2 | 2.215 | 0.7700 | 147.3 | 0.198 |
| P11 | h10 | depends | 0.0000 | 0.0010 | 0.0010 | 0.0014 | 0.7900 | 0.2100 | 0.0000 | 1.495 | 0.0039 | 0.520 | 0.000 | 15.2 | 2.648 | 0.7900 | 129.0 | 0.198 |
| P11 | h10 | carried_margin | 0.0000 | 0.0113 | 0.0113 | 0.0155 | 0.7900 | 0.2100 | 0.0000 | 1.488 | 0.0413 | 0.530 | 0.000 | 15.2 | 2.361 | 0.7900 | n/a | 0.198 |
| P11 | h10 | own_margin | 10.6772 | 10.6981 | 0.0209 | 0.0673 | 0.9800 | 0.0200 | 0.0000 | 2.177 | 0.1837 | 0.560 | 0.200 | 11.0 | 0.758 | 0.9500 | n/a | 0.198 |
| P11 | h10 | kappa | 0.0000 | 0.0711 | 0.0711 | 0.0937 | 0.8200 | 0.1800 | 0.0000 | 1.317 | 0.2431 | 0.540 | 0.000 | 15.1 | 2.032 | 0.7900 | 11.2 | 0.198 |
| P11 | h10 | shuffled_vs_yardstick | -0.4093 | -0.3973 | 0.0120 | 0.0182 | 0.8700 | 0.1300 | 0.0000 | 1.873 | 0.0447 | 0.580 | 0.010 | 14.2 | 1.525 | 0.8000 | n/a | 0.198 |
| P11 | h10 | carried_added | 0.1842 | 0.1745 | -0.0097 | 0.0128 | 0.8000 | 0.0000 | 0.2000 | 1.494 | 0.0338 | 0.590 | 0.000 | 15.2 | 2.196 | 0.7900 | n/a | 0.198 |
| P11 | h10 | pooled_retention | 0.0170 | 0.0161 | -0.0009 | 0.0012 | 0.8000 | 0.0000 | 0.2000 | 1.526 | 0.0031 | 0.560 | 0.000 | 15.1 | 2.233 | 0.7900 | 150.5 | 0.198 |
| P12 | n20 | large | -0.4181 | -0.4255 | -0.0074 | 0.0586 | 0.9300 | 0.0700 | 0.0000 | 1.111 | 0.1211 | 0.270 | 0.210 | 10.7 | 1.263 | 0.8200 | n/a | n/a |
| P12 | n20 | carries | 0.3058 | 0.2989 | -0.0069 | 0.0275 | 0.9000 | 0.0000 | 0.1000 | 1.533 | 0.0714 | 0.600 | 0.030 | 13.4 | 1.411 | 0.8800 | 8.5 | n/a |
| P12 | n20 | depends | 0.0000 | -0.0139 | -0.0139 | 0.0793 | 0.9400 | 0.0500 | 0.0100 | 0.957 | 0.1571 | 0.140 | 0.020 | 14.9 | 1.082 | 0.8900 | 9.0 | n/a |
| P12 | n20 | carried_margin | 0.0000 | -0.0047 | -0.0047 | 0.0318 | 0.9600 | 0.0300 | 0.0100 | 1.027 | 0.0686 | 0.160 | 0.020 | 14.7 | 0.912 | 0.8900 | n/a | n/a |
| P12 | n20 | own_margin | 0.4181 | 0.4207 | 0.0026 | 0.0566 | 0.9400 | 0.0200 | 0.0400 | 0.971 | 0.1311 | 0.080 | 0.650 | 5.9 | 1.055 | 0.5900 | n/a | n/a |
| P12 | n20 | kappa | 0.0000 | -0.0271 | -0.0271 | 0.1761 | 0.9300 | 0.0500 | 0.0200 | 0.885 | 0.3532 | 0.160 | 0.020 | 14.8 | 1.101 | 0.8900 | 6.7 | n/a |
| P12 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4207 | -0.0026 | 0.0566 | 0.9400 | 0.0400 | 0.0200 | 0.971 | 0.1311 | 0.080 | 0.650 | 5.9 | 1.055 | 0.5900 | n/a | n/a |
| P12 | n20 | carried_added | 0.1842 | 0.1813 | -0.0029 | 0.0285 | 0.8900 | 0.0000 | 0.1100 | 1.036 | 0.0572 | 0.160 | 0.040 | 14.2 | 1.539 | 0.8700 | n/a | n/a |
| P12 | n20 | pooled_retention | 0.3058 | 0.3072 | 0.0013 | 0.0321 | 0.8700 | 0.0000 | 0.1300 | 0.975 | 0.0661 | 0.780 | 0.000 | 15.0 | 2.414 | 0.8600 | 8.9 | n/a |
| P12 | n40 | large | -0.4181 | -0.4220 | -0.0039 | 0.0582 | 0.9300 | 0.0700 | 0.0000 | 1.111 | 0.1160 | 0.230 | 0.150 | 11.1 | 1.160 | 0.8200 | n/a | n/a |
| P12 | n40 | carries | 0.0926 | 0.0919 | -0.0008 | 0.0118 | 0.9700 | 0.0000 | 0.0300 | 1.263 | 0.0280 | 0.530 | 0.010 | 14.2 | 0.972 | 0.9300 | 8.2 | n/a |
| P12 | n40 | depends | 0.0000 | -0.0012 | -0.0012 | 0.0202 | 0.9300 | 0.0600 | 0.0100 | 0.791 | 0.0381 | 0.210 | 0.010 | 14.7 | 1.134 | 0.8100 | 8.2 | n/a |
| P12 | n40 | carried_margin | 0.0000 | -0.0013 | -0.0013 | 0.0361 | 0.9200 | 0.0700 | 0.0100 | 0.848 | 0.0677 | 0.180 | 0.030 | 14.3 | 1.110 | 0.8100 | n/a | n/a |
| P12 | n40 | own_margin | 1.8041 | 1.8306 | 0.0266 | 0.2611 | 0.8900 | 0.0400 | 0.0700 | 0.902 | 0.4867 | 0.200 | 0.240 | 10.6 | 1.216 | 0.8400 | n/a | n/a |
| P12 | n40 | kappa | 0.0000 | -0.0160 | -0.0160 | 0.2055 | 0.9100 | 0.0800 | 0.0100 | 0.734 | 0.3686 | 0.180 | 0.010 | 14.4 | 1.442 | 0.8100 | 6.3 | n/a |
| P12 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4207 | -0.0026 | 0.0565 | 0.9400 | 0.0400 | 0.0200 | 0.974 | 0.1297 | 0.080 | 0.670 | 5.9 | 1.077 | 0.6000 | n/a | n/a |
| P12 | n40 | carried_added | 0.1842 | 0.1848 | 0.0006 | 0.0320 | 0.9100 | 0.0000 | 0.0900 | 0.916 | 0.0611 | 0.190 | 0.030 | 13.9 | 1.154 | 0.8700 | n/a | n/a |
| P12 | n40 | pooled_retention | 0.0926 | 0.0930 | 0.0003 | 0.0097 | 0.8700 | 0.0000 | 0.1300 | 0.969 | 0.0200 | 0.770 | 0.000 | 15.1 | 2.196 | 0.8700 | 8.2 | n/a |
| P12 | n80 | large | -0.4181 | -0.4187 | -0.0006 | 0.0534 | 0.8800 | 0.1200 | 0.0000 | 1.123 | 0.1133 | 0.430 | 0.110 | 11.9 | 1.472 | 0.8100 | n/a | n/a |
| P12 | n80 | carries | 0.0187 | 0.0191 | 0.0004 | 0.0030 | 0.9200 | 0.0000 | 0.0800 | 1.170 | 0.0070 | 0.640 | 0.030 | 13.7 | 1.225 | 0.9000 | 8.8 | n/a |
| P12 | n80 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0040 | 0.9000 | 0.0900 | 0.0100 | 0.818 | 0.0074 | 0.130 | 0.220 | 10.9 | 1.460 | 0.7800 | 8.7 | n/a |
| P12 | n80 | carried_margin | 0.0000 | 0.0022 | 0.0022 | 0.0377 | 0.9300 | 0.0500 | 0.0200 | 0.767 | 0.0701 | 0.110 | 0.220 | 10.5 | 1.119 | 0.7800 | n/a | n/a |
| P12 | n80 | own_margin | 9.6872 | 9.7472 | 0.0600 | 1.5259 | 0.8800 | 0.0500 | 0.0700 | 0.718 | 3.2403 | 0.180 | 0.560 | 7.0 | 1.259 | 0.6200 | n/a | n/a |
| P12 | n80 | kappa | 0.0000 | 0.0003 | 0.0003 | 0.2035 | 0.8900 | 0.0900 | 0.0200 | 0.765 | 0.3642 | 0.110 | 0.220 | 10.4 | 1.432 | 0.7800 | 6.5 | n/a |
| P12 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4209 | -0.0028 | 0.0565 | 0.9400 | 0.0400 | 0.0200 | 0.970 | 0.1292 | 0.080 | 0.670 | 5.9 | 1.035 | 0.6000 | n/a | n/a |
| P12 | n80 | carried_added | 0.1842 | 0.1880 | 0.0038 | 0.0350 | 0.9100 | 0.0500 | 0.0400 | 0.787 | 0.0676 | 0.130 | 0.300 | 9.5 | 1.137 | 0.7500 | n/a | n/a |
| P12 | n80 | pooled_retention | 0.0187 | 0.0187 | 0.0001 | 0.0019 | 0.8700 | 0.0000 | 0.1300 | 0.986 | 0.0041 | 0.750 | 0.000 | 15.1 | 2.422 | 0.8600 | 8.3 | n/a |
| P12 | n160 | large | -0.4181 | -0.4207 | -0.0026 | 0.0630 | 0.9300 | 0.0700 | 0.0000 | 1.053 | 0.1319 | 0.120 | 0.390 | 8.8 | 1.070 | 0.7600 | n/a | n/a |
| P12 | n160 | carries | 0.0085 | 0.0086 | 0.0001 | 0.0014 | 0.8900 | 0.0000 | 0.1100 | 1.135 | 0.0030 | 0.570 | 0.000 | 14.8 | 1.527 | 0.8700 | 16.3 | n/a |
| P12 | n160 | depends | 0.0000 | -0.0001 | -0.0001 | 0.0012 | 0.8800 | 0.1200 | 0.0000 | 1.009 | 0.0024 | 0.580 | 0.000 | 15.0 | 1.546 | 0.8600 | 15.9 | n/a |
| P12 | n160 | carried_margin | 0.0000 | 0.0001 | 0.0001 | 0.0258 | 0.8900 | 0.1100 | 0.0000 | 0.958 | 0.0513 | 0.610 | 0.000 | 14.9 | 1.429 | 0.8600 | n/a | n/a |
| P12 | n160 | own_margin | 21.4901 | 21.5527 | 0.0626 | 1.3485 | 0.9300 | 0.0600 | 0.0100 | 1.122 | 2.9177 | 0.510 | 0.090 | 12.2 | 1.082 | 0.8700 | n/a | n/a |
| P12 | n160 | kappa | 0.0000 | 0.0090 | 0.0090 | 0.1388 | 0.9000 | 0.1000 | 0.0000 | 0.874 | 0.2819 | 0.610 | 0.000 | 14.9 | 1.544 | 0.8600 | 8.6 | n/a |
| P12 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4208 | -0.0027 | 0.0564 | 0.9400 | 0.0400 | 0.0200 | 0.976 | 0.1302 | 0.080 | 0.670 | 5.9 | 1.026 | 0.6100 | n/a | n/a |
| P12 | n160 | carried_added | 0.1842 | 0.1860 | 0.0019 | 0.0223 | 0.9300 | 0.0000 | 0.0700 | 1.007 | 0.0458 | 0.570 | 0.010 | 14.7 | 1.082 | 0.9100 | n/a | n/a |
| P12 | n160 | pooled_retention | 0.0085 | 0.0085 | 0.0000 | 0.0009 | 0.8700 | 0.0000 | 0.1300 | 0.974 | 0.0018 | 0.520 | 0.000 | 15.1 | 2.440 | 0.8600 | 16.7 | n/a |
| P12 | n320 | large | -0.4181 | -0.4200 | -0.0019 | 0.0667 | 0.9300 | 0.0700 | 0.0000 | 0.988 | 0.1396 | 0.110 | 0.420 | 8.3 | 1.056 | 0.7300 | n/a | n/a |
| P12 | n320 | carries | 0.0073 | 0.0075 | 0.0002 | 0.0012 | 0.9100 | 0.0000 | 0.0900 | 1.140 | 0.0025 | 0.550 | 0.020 | 14.5 | 1.182 | 0.8800 | 17.4 | n/a |
| P12 | n320 | depends | 0.0000 | -0.0000 | -0.0000 | 0.0010 | 0.8700 | 0.1300 | 0.0000 | 1.012 | 0.0021 | 0.600 | 0.010 | 15.0 | 1.575 | 0.8300 | 16.9 | n/a |
| P12 | n320 | carried_margin | 0.0000 | 0.0008 | 0.0008 | 0.0253 | 0.8800 | 0.1200 | 0.0000 | 0.975 | 0.0511 | 0.590 | 0.010 | 15.0 | 1.544 | 0.8300 | n/a | n/a |
| P12 | n320 | own_margin | 24.9973 | 25.0067 | 0.0093 | 1.4474 | 0.9300 | 0.0600 | 0.0100 | 1.097 | 3.1659 | 0.600 | 0.080 | 12.9 | 1.240 | 0.8900 | n/a | n/a |
| P12 | n320 | kappa | 0.0000 | 0.0145 | 0.0145 | 0.1337 | 0.8600 | 0.1100 | 0.0300 | 0.907 | 0.2774 | 0.580 | 0.000 | 15.1 | 1.677 | 0.8300 | 8.7 | n/a |
| P12 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4208 | -0.0027 | 0.0565 | 0.9400 | 0.0400 | 0.0200 | 0.974 | 0.1293 | 0.090 | 0.670 | 5.9 | 1.051 | 0.6000 | n/a | n/a |
| P12 | n320 | carried_added | 0.1842 | 0.1868 | 0.0026 | 0.0207 | 0.9300 | 0.0000 | 0.0700 | 1.117 | 0.0456 | 0.590 | 0.010 | 14.9 | 1.174 | 0.9200 | n/a | n/a |
| P12 | n320 | pooled_retention | 0.0073 | 0.0073 | 0.0000 | 0.0008 | 0.8700 | 0.0000 | 0.1300 | 0.981 | 0.0016 | 0.520 | 0.000 | 15.1 | 2.370 | 0.8600 | 17.9 | n/a |
| P12 | h2 | large | -0.4183 | -0.4218 | -0.0035 | 0.0660 | 0.9500 | 0.0500 | 0.0000 | 0.992 | 0.1361 | 0.080 | 0.480 | 8.2 | 0.936 | 0.7400 | n/a | 1.000 |
| P12 | h2 | carries | 0.0963 | 0.0966 | 0.0004 | 0.0095 | 0.8700 | 0.0000 | 0.1300 | 0.964 | 0.0196 | 0.550 | 0.000 | 15.1 | 2.413 | 0.8600 | 114.4 | 1.000 |
| P12 | h2 | depends | 0.0000 | -0.0009 | -0.0009 | 0.0136 | 0.8700 | 0.1300 | 0.0000 | 0.978 | 0.0275 | 0.460 | 0.000 | 15.1 | 2.470 | 0.8500 | 52.8 | 1.000 |
| P12 | h2 | carried_margin | 0.0000 | -0.0012 | -0.0012 | 0.0232 | 0.8700 | 0.1300 | 0.0000 | 0.954 | 0.0482 | 0.500 | 0.000 | 15.1 | 2.371 | 0.8500 | n/a | 1.000 |
| P12 | h2 | own_margin | 1.7295 | 1.7271 | -0.0023 | 0.0350 | 0.8900 | 0.1100 | 0.0000 | 0.897 | 0.0702 | 0.500 | 0.010 | 14.9 | 1.583 | 0.8600 | n/a | 1.000 |
| P12 | h2 | kappa | 0.0000 | 0.0061 | 0.0061 | 0.1237 | 0.8500 | 0.1300 | 0.0200 | 0.854 | 0.2484 | 0.500 | 0.000 | 15.1 | 2.080 | 0.8500 | 10.0 | 1.000 |
| P12 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4207 | -0.0023 | 0.0565 | 0.9400 | 0.0400 | 0.0200 | 0.974 | 0.1294 | 0.080 | 0.670 | 5.9 | 1.012 | 0.6000 | n/a | 1.000 |
| P12 | h2 | carried_added | 0.1842 | 0.1849 | 0.0007 | 0.0192 | 0.8700 | 0.0000 | 0.1300 | 0.979 | 0.0400 | 0.460 | 0.000 | 15.1 | 2.330 | 0.8500 | n/a | 1.000 |
| P12 | h2 | pooled_retention | 0.0963 | 0.0967 | 0.0005 | 0.0101 | 0.8700 | 0.0000 | 0.1300 | 0.970 | 0.0206 | 0.550 | 0.000 | 15.1 | 2.314 | 0.8500 | 116.0 | 1.000 |
| P12 | h5 | large | -0.4183 | -0.4217 | -0.0034 | 0.0667 | 0.9500 | 0.0500 | 0.0000 | 1.004 | 0.1457 | 0.140 | 0.460 | 8.1 | 0.971 | 0.7500 | n/a | 1.000 |
| P12 | h5 | carries | 0.0360 | 0.0362 | 0.0003 | 0.0039 | 0.8700 | 0.0000 | 0.1300 | 0.949 | 0.0079 | 0.570 | 0.000 | 15.2 | 2.440 | 0.8500 | 147.4 | 1.000 |
| P12 | h5 | depends | 0.0000 | -0.0002 | -0.0002 | 0.0047 | 0.8700 | 0.1300 | 0.0000 | 0.990 | 0.0096 | 0.550 | 0.000 | 15.2 | 2.579 | 0.8600 | 77.7 | 1.000 |
| P12 | h5 | carried_margin | 0.0000 | -0.0007 | -0.0007 | 0.0230 | 0.8700 | 0.1300 | 0.0000 | 0.976 | 0.0474 | 0.550 | 0.000 | 15.2 | 2.532 | 0.8600 | n/a | 1.000 |
| P12 | h5 | own_margin | 4.9368 | 4.9272 | -0.0095 | 0.0650 | 0.9300 | 0.0600 | 0.0100 | 0.978 | 0.1379 | 0.500 | 0.060 | 13.3 | 1.255 | 0.8400 | n/a | 1.000 |
| P12 | h5 | kappa | 0.0000 | 0.0084 | 0.0084 | 0.1229 | 0.8600 | 0.1300 | 0.0100 | 0.869 | 0.2489 | 0.560 | 0.000 | 15.2 | 2.195 | 0.8600 | 9.9 | 1.000 |
| P12 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4210 | -0.0026 | 0.0569 | 0.9400 | 0.0400 | 0.0200 | 1.002 | 0.1437 | 0.150 | 0.620 | 6.3 | 1.052 | 0.6000 | n/a | 1.000 |
| P12 | h5 | carried_added | 0.1842 | 0.1852 | 0.0010 | 0.0194 | 0.8700 | 0.0000 | 0.1300 | 0.955 | 0.0399 | 0.580 | 0.000 | 15.1 | 2.404 | 0.8500 | n/a | 1.000 |
| P12 | h5 | pooled_retention | 0.0360 | 0.0361 | 0.0002 | 0.0038 | 0.8700 | 0.0000 | 0.1300 | 0.948 | 0.0078 | 0.560 | 0.000 | 15.1 | 2.487 | 0.8500 | 163.0 | 1.000 |
| P12 | h10 | large | -0.4183 | -0.3908 | 0.0276 | 0.0543 | 0.7900 | 0.2100 | 0.0000 | 0.782 | 0.0993 | 0.080 | 0.390 | 10.5 | 1.976 | 0.6200 | n/a | 0.184 |
| P12 | h10 | carries | 0.0169 | 0.0157 | -0.0012 | 0.0013 | 0.6600 | 0.0000 | 0.3400 | 1.066 | 0.0028 | 0.520 | 0.000 | 15.1 | 2.676 | 0.6600 | 117.2 | 0.184 |
| P12 | h10 | depends | 0.0000 | 0.0014 | 0.0014 | 0.0016 | 0.6700 | 0.3300 | 0.0000 | 1.153 | 0.0033 | 0.500 | 0.000 | 15.1 | 2.765 | 0.6700 | 108.7 | 0.184 |
| P12 | h10 | carried_margin | 0.0000 | 0.0150 | 0.0150 | 0.0168 | 0.6700 | 0.3300 | 0.0000 | 1.145 | 0.0357 | 0.510 | 0.000 | 15.1 | 2.711 | 0.6700 | n/a | 0.184 |
| P12 | h10 | own_margin | 10.7131 | 10.7430 | 0.0299 | 0.0980 | 0.9700 | 0.0300 | 0.0000 | 1.609 | 0.2165 | 0.500 | 0.260 | 10.1 | 0.856 | 0.8900 | n/a | 0.184 |
| P12 | h10 | kappa | 0.0000 | 0.0958 | 0.0958 | 0.1035 | 0.6900 | 0.3100 | 0.0000 | 0.986 | 0.2194 | 0.510 | 0.000 | 15.2 | 2.329 | 0.6700 | 12.3 | 0.184 |
| P12 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4058 | 0.0126 | 0.0494 | 0.8600 | 0.1400 | 0.0000 | 0.671 | 0.0863 | 0.070 | 0.590 | 8.2 | 1.431 | 0.5000 | n/a | 0.184 |
| P12 | h10 | carried_added | 0.1842 | 0.1716 | -0.0126 | 0.0147 | 0.6500 | 0.0000 | 0.3500 | 1.054 | 0.0304 | 0.520 | 0.000 | 15.1 | 2.827 | 0.6500 | n/a | 0.184 |
| P12 | h10 | pooled_retention | 0.0169 | 0.0157 | -0.0012 | 0.0013 | 0.6600 | 0.0000 | 0.3400 | 1.085 | 0.0027 | 0.560 | 0.000 | 15.1 | 2.940 | 0.6600 | 122.9 | 0.184 |
| P13 | n20 | large | -0.4216 | -0.4219 | -0.0003 | 0.0539 | 0.9700 | 0.0300 | 0.0000 | 1.257 | 0.1189 | 0.230 | 0.160 | 11.4 | 0.961 | 0.8400 | n/a | n/a |
| P13 | n20 | carries | 0.3000 | 0.3027 | 0.0027 | 0.0321 | 0.9300 | 0.0000 | 0.0700 | 1.241 | 0.0753 | 0.560 | 0.020 | 13.7 | 1.083 | 0.9000 | 8.6 | n/a |
| P13 | n20 | depends | -0.0084 | -0.0209 | -0.0125 | 0.0820 | 0.9700 | 0.0200 | 0.0100 | 1.000 | 0.1637 | 0.130 | 0.000 | 15.1 | 0.832 | 0.9300 | 9.0 | n/a |
| P13 | n20 | carried_margin | -0.0035 | -0.0078 | -0.0043 | 0.0322 | 0.9700 | 0.0200 | 0.0100 | 1.050 | 0.0676 | 0.120 | 0.000 | 15.2 | 0.871 | 0.9300 | n/a | n/a |
| P13 | n20 | own_margin | 0.4181 | 0.4141 | -0.0040 | 0.0484 | 0.9500 | 0.0000 | 0.0500 | 1.228 | 0.1392 | 0.080 | 0.660 | 5.8 | 0.942 | 0.6600 | n/a | n/a |
| P13 | n20 | kappa | -0.0194 | -0.0447 | -0.0253 | 0.1745 | 0.9400 | 0.0300 | 0.0300 | 0.972 | 0.3596 | 0.120 | 0.000 | 15.1 | 1.004 | 0.9200 | 6.6 | n/a |
| P13 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4141 | 0.0040 | 0.0484 | 0.9500 | 0.0500 | 0.0000 | 1.228 | 0.1392 | 0.080 | 0.660 | 5.8 | 0.942 | 0.6600 | n/a | n/a |
| P13 | n20 | carried_added | 0.1807 | 0.1828 | 0.0021 | 0.0260 | 0.9600 | 0.0000 | 0.0400 | 1.293 | 0.0582 | 0.120 | 0.010 | 14.7 | 0.896 | 0.9500 | n/a | n/a |
| P13 | n20 | pooled_retention | 0.3000 | 0.3047 | 0.0047 | 0.0297 | 0.9200 | 0.0000 | 0.0800 | 1.134 | 0.0658 | 0.790 | 0.000 | 15.0 | 1.468 | 0.9100 | 8.6 | n/a |
| P13 | n40 | large | 0.1394 | 0.1262 | -0.0132 | 0.1716 | 0.8500 | 0.0000 | 0.1500 | 0.788 | 0.2889 | 0.510 | 0.040 | 12.7 | 1.600 | 0.8100 | n/a | n/a |
| P13 | n40 | carries | 0.3730 | 0.3654 | -0.0077 | 0.0863 | 0.8900 | 0.0000 | 0.1100 | 0.850 | 0.1527 | 0.470 | 0.040 | 13.4 | 1.490 | 0.8600 | 8.3 | n/a |
| P13 | n40 | depends | 0.3090 | 0.2983 | -0.0107 | 0.0954 | 0.8600 | 0.0000 | 0.1400 | 0.801 | 0.1646 | 0.450 | 0.040 | 13.1 | 1.767 | 0.8100 | 8.2 | n/a |
| P13 | n40 | carried_margin | 0.5575 | 0.5402 | -0.0173 | 0.1943 | 0.8400 | 0.0000 | 0.1600 | 0.741 | 0.2971 | 0.250 | 0.120 | 11.2 | 2.065 | 0.7500 | n/a | n/a |
| P13 | n40 | own_margin | 1.8041 | 1.8056 | 0.0016 | 0.2090 | 0.9700 | 0.0000 | 0.0300 | 1.289 | 0.5136 | 0.200 | 0.250 | 10.5 | 0.934 | 0.9100 | n/a | n/a |
| P13 | n40 | kappa | 0.7517 | 0.7270 | -0.0246 | 0.0718 | 0.9100 | 0.0100 | 0.0800 | 0.719 | 0.1259 | 0.250 | 0.080 | 12.5 | 1.303 | 0.8700 | 4.7 | n/a |
| P13 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4141 | 0.0040 | 0.0484 | 0.9500 | 0.0500 | 0.0000 | 1.224 | 0.1403 | 0.080 | 0.680 | 5.7 | 0.939 | 0.6700 | n/a | n/a |
| P13 | n40 | carried_added | 0.7417 | 0.7309 | -0.0108 | 0.2038 | 0.8800 | 0.0000 | 0.1200 | 0.782 | 0.3265 | 0.250 | 0.090 | 12.2 | 1.396 | 0.7900 | n/a | n/a |
| P13 | n40 | pooled_retention | 0.3730 | 0.3664 | -0.0066 | 0.0586 | 0.8900 | 0.0000 | 0.1100 | 0.865 | 0.1128 | 0.520 | 0.020 | 13.5 | 1.185 | 0.8500 | 8.2 | n/a |
| P13 | n80 | large | 7.5438 | 7.6170 | 0.0732 | 1.4731 | 0.9400 | 0.0000 | 0.0600 | 1.062 | 3.3252 | 0.170 | 0.380 | 8.6 | 1.023 | 0.8100 | n/a | n/a |
| P13 | n80 | carries | 0.8252 | 0.8543 | 0.0290 | 0.1493 | 0.9600 | 0.0100 | 0.0300 | 1.125 | 0.3187 | 0.510 | 0.010 | 13.1 | 0.875 | 0.9700 | 7.7 | n/a |
| P13 | n80 | depends | 0.8219 | 0.8518 | 0.0299 | 0.1525 | 0.9600 | 0.0100 | 0.0300 | 1.122 | 0.3240 | 0.510 | 0.010 | 13.0 | 0.869 | 0.9700 | 7.5 | n/a |
| P13 | n80 | carried_margin | 7.9619 | 8.0312 | 0.0693 | 1.5054 | 0.9500 | 0.0000 | 0.0500 | 1.066 | 3.4111 | 0.170 | 0.400 | 8.5 | 0.996 | 0.8100 | n/a | n/a |
| P13 | n80 | own_margin | 9.6872 | 9.4849 | -0.2023 | 1.2509 | 0.9600 | 0.0100 | 0.0300 | 1.140 | 3.6142 | 0.090 | 0.650 | 5.9 | 0.971 | 0.7400 | n/a | n/a |
| P13 | n80 | kappa | 0.9774 | 0.9765 | -0.0009 | 0.0048 | 0.9600 | 0.0200 | 0.0200 | 1.004 | 0.0101 | 0.160 | 0.320 | 9.4 | 0.862 | 0.8400 | 5.5 | n/a |
| P13 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4142 | 0.0039 | 0.0484 | 0.9600 | 0.0400 | 0.0000 | 1.225 | 0.1409 | 0.080 | 0.670 | 5.8 | 0.915 | 0.6700 | n/a | n/a |
| P13 | n80 | carried_added | 8.1461 | 8.2217 | 0.0756 | 1.5259 | 0.9400 | 0.0000 | 0.0600 | 1.067 | 3.4182 | 0.170 | 0.360 | 8.7 | 1.025 | 0.8100 | n/a | n/a |
| P13 | n80 | pooled_retention | 0.8252 | 0.8342 | 0.0089 | 0.0860 | 0.9400 | 0.0000 | 0.0600 | 1.081 | 0.1858 | 0.460 | 0.010 | 15.1 | 1.085 | 0.8900 | 7.9 | n/a |
| P13 | n160 | large | 18.7263 | 18.9643 | 0.2380 | 2.2945 | 0.9400 | 0.0100 | 0.0500 | 1.104 | 5.0031 | 0.490 | 0.000 | 14.5 | 1.019 | 0.9100 | n/a | n/a |
| P13 | n160 | carries | 0.8918 | 0.9153 | 0.0236 | 0.1480 | 0.9300 | 0.0000 | 0.0700 | 1.170 | 0.3140 | 0.500 | 0.010 | 14.5 | 1.010 | 0.9300 | 15.6 | n/a |
| P13 | n160 | depends | 0.8908 | 0.9149 | 0.0240 | 0.1493 | 0.9300 | 0.0000 | 0.0700 | 1.172 | 0.3161 | 0.500 | 0.010 | 14.5 | 1.013 | 0.9300 | 15.0 | n/a |
| P13 | n160 | carried_margin | 19.1444 | 19.3785 | 0.2341 | 2.3126 | 0.9400 | 0.0100 | 0.0500 | 1.102 | 5.0311 | 0.500 | 0.010 | 14.5 | 1.015 | 0.9100 | n/a | n/a |
| P13 | n160 | own_margin | 21.4901 | 21.3411 | -0.1490 | 1.3102 | 0.9600 | 0.0000 | 0.0400 | 1.257 | 3.0180 | 0.490 | 0.130 | 11.8 | 0.809 | 0.9400 | n/a | n/a |
| P13 | n160 | kappa | 0.9905 | 0.9903 | -0.0001 | 0.0012 | 0.9500 | 0.0500 | 0.0000 | 1.225 | 0.0028 | 0.500 | 0.000 | 14.8 | 0.979 | 0.9300 | 8.1 | n/a |
| P13 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4142 | 0.0039 | 0.0485 | 0.9500 | 0.0500 | 0.0000 | 1.218 | 0.1391 | 0.080 | 0.660 | 5.8 | 0.949 | 0.6700 | n/a | n/a |
| P13 | n160 | carried_added | 19.3286 | 19.5690 | 0.2404 | 2.3469 | 0.9400 | 0.0100 | 0.0500 | 1.100 | 5.1205 | 0.500 | 0.010 | 14.5 | 1.012 | 0.9100 | n/a | n/a |
| P13 | n160 | pooled_retention | 0.8918 | 0.9044 | 0.0127 | 0.0876 | 0.9200 | 0.0000 | 0.0800 | 1.143 | 0.1964 | 0.620 | 0.000 | 15.1 | 1.404 | 0.9000 | 15.8 | n/a |
| P13 | n320 | large | 21.9357 | 22.1936 | 0.2579 | 2.4981 | 0.9300 | 0.0000 | 0.0700 | 1.192 | 5.7863 | 0.610 | 0.000 | 14.8 | 1.017 | 0.8900 | n/a | n/a |
| P13 | n320 | carries | 0.8950 | 0.9095 | 0.0144 | 0.1382 | 0.9400 | 0.0000 | 0.0600 | 1.257 | 0.3182 | 0.520 | 0.000 | 14.8 | 1.137 | 0.9100 | 16.9 | n/a |
| P13 | n320 | depends | 0.8942 | 0.9090 | 0.0148 | 0.1393 | 0.9400 | 0.0000 | 0.0600 | 1.260 | 0.3206 | 0.520 | 0.000 | 14.8 | 1.140 | 0.9100 | 16.4 | n/a |
| P13 | n320 | carried_margin | 22.3538 | 22.6077 | 0.2539 | 2.5083 | 0.9400 | 0.0000 | 0.0600 | 1.195 | 5.8152 | 0.620 | 0.000 | 14.8 | 1.031 | 0.8900 | n/a | n/a |
| P13 | n320 | own_margin | 24.9973 | 25.0345 | 0.0372 | 1.2928 | 0.9700 | 0.0200 | 0.0100 | 1.437 | 3.3194 | 0.540 | 0.090 | 12.3 | 0.838 | 0.9600 | n/a | n/a |
| P13 | n320 | kappa | 0.9918 | 0.9917 | -0.0001 | 0.0010 | 0.9300 | 0.0600 | 0.0100 | 1.156 | 0.0024 | 0.610 | 0.000 | 14.9 | 1.030 | 0.9300 | 8.3 | n/a |
| P13 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4141 | 0.0040 | 0.0484 | 0.9500 | 0.0500 | 0.0000 | 1.227 | 0.1393 | 0.080 | 0.670 | 5.7 | 0.929 | 0.6900 | n/a | n/a |
| P13 | n320 | carried_added | 22.5380 | 22.7983 | 0.2603 | 2.5437 | 0.9300 | 0.0000 | 0.0700 | 1.192 | 5.9026 | 0.620 | 0.000 | 14.8 | 1.038 | 0.8900 | n/a | n/a |
| P13 | n320 | pooled_retention | 0.8950 | 0.9092 | 0.0141 | 0.0885 | 0.9200 | 0.0000 | 0.0800 | 1.141 | 0.2020 | 0.520 | 0.000 | 15.1 | 1.412 | 0.8900 | 16.9 | n/a |
| P13 | h2 | large | -0.0284 | -0.0216 | 0.0068 | 0.0468 | 0.9600 | 0.0300 | 0.0100 | 1.174 | 0.1289 | 0.120 | 0.690 | 5.6 | 0.945 | 0.6800 | n/a | 1.000 |
| P13 | h2 | carries | 0.3000 | 0.3044 | 0.0044 | 0.0279 | 0.9100 | 0.0100 | 0.0800 | 1.132 | 0.0626 | 0.560 | 0.000 | 15.1 | 1.282 | 0.9100 | 113.8 | 1.000 |
| P13 | h2 | depends | 0.2254 | 0.2279 | 0.0025 | 0.0140 | 0.9500 | 0.0000 | 0.0500 | 1.217 | 0.0321 | 0.520 | 0.000 | 15.2 | 0.988 | 0.9300 | 54.7 | 1.000 |
| P13 | h2 | carried_margin | 0.3899 | 0.3926 | 0.0026 | 0.0174 | 0.9600 | 0.0000 | 0.0400 | 1.297 | 0.0419 | 0.480 | 0.000 | 15.4 | 0.851 | 0.9500 | n/a | 1.000 |
| P13 | h2 | own_margin | 1.7295 | 1.7243 | -0.0052 | 0.0327 | 0.9400 | 0.0500 | 0.0100 | 1.042 | 0.0671 | 0.530 | 0.000 | 15.2 | 1.068 | 0.9100 | n/a | 1.000 |
| P13 | h2 | kappa | 0.6792 | 0.6767 | -0.0025 | 0.0372 | 0.8900 | 0.0800 | 0.0300 | 1.008 | 0.0817 | 0.520 | 0.000 | 15.1 | 1.337 | 0.8900 | 9.8 | 1.000 |
| P13 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4141 | 0.0042 | 0.0485 | 0.9500 | 0.0500 | 0.0000 | 1.223 | 0.1381 | 0.080 | 0.660 | 5.7 | 0.941 | 0.6800 | n/a | 1.000 |
| P13 | h2 | carried_added | 0.5741 | 0.5831 | 0.0090 | 0.0562 | 0.9200 | 0.0000 | 0.0800 | 1.162 | 0.1288 | 0.480 | 0.000 | 15.1 | 1.303 | 0.9000 | n/a | 1.000 |
| P13 | h2 | pooled_retention | 0.3000 | 0.3048 | 0.0048 | 0.0295 | 0.9200 | 0.0000 | 0.0800 | 1.142 | 0.0673 | 0.550 | 0.000 | 15.1 | 1.372 | 0.9000 | 114.0 | 1.000 |
| P13 | h5 | large | 3.9236 | 3.9855 | 0.0619 | 0.4095 | 0.9200 | 0.0000 | 0.0800 | 1.108 | 0.9169 | 0.540 | 0.000 | 15.3 | 1.169 | 0.9000 | n/a | 1.000 |
| P13 | h5 | carries | 0.8838 | 0.8970 | 0.0131 | 0.0916 | 0.9200 | 0.0000 | 0.0800 | 1.125 | 0.2044 | 0.600 | 0.000 | 15.2 | 1.276 | 0.9100 | 146.8 | 1.000 |
| P13 | h5 | depends | 0.8795 | 0.8938 | 0.0142 | 0.0946 | 0.9200 | 0.0000 | 0.0800 | 1.137 | 0.2111 | 0.600 | 0.000 | 15.2 | 1.291 | 0.9100 | 75.9 | 1.000 |
| P13 | h5 | carried_margin | 4.3419 | 4.3994 | 0.0575 | 0.4170 | 0.9200 | 0.0000 | 0.0800 | 1.133 | 0.9406 | 0.580 | 0.000 | 15.2 | 1.225 | 0.9100 | n/a | 1.000 |
| P13 | h5 | own_margin | 4.9368 | 4.9280 | -0.0088 | 0.0622 | 0.9400 | 0.0400 | 0.0200 | 1.171 | 0.1484 | 0.510 | 0.040 | 12.9 | 1.035 | 0.9100 | n/a | 1.000 |
| P13 | h5 | kappa | 0.9593 | 0.9589 | -0.0004 | 0.0047 | 0.9200 | 0.0600 | 0.0200 | 1.056 | 0.0106 | 0.560 | 0.000 | 15.2 | 1.193 | 0.9000 | 9.6 | 1.000 |
| P13 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4139 | 0.0044 | 0.0480 | 0.9400 | 0.0600 | 0.0000 | 1.289 | 0.1425 | 0.100 | 0.640 | 5.7 | 1.145 | 0.6800 | n/a | 1.000 |
| P13 | h5 | carried_added | 4.5261 | 4.5901 | 0.0639 | 0.4560 | 0.9200 | 0.0000 | 0.0800 | 1.130 | 1.0271 | 0.590 | 0.000 | 15.2 | 1.263 | 0.9100 | n/a | 1.000 |
| P13 | h5 | pooled_retention | 0.8838 | 0.8968 | 0.0129 | 0.0881 | 0.9200 | 0.0000 | 0.0800 | 1.141 | 0.1987 | 0.530 | 0.000 | 15.2 | 1.310 | 0.9200 | 156.5 | 1.000 |
| P13 | h10 | large | 9.2049 | 8.5850 | -0.6199 | 0.6037 | 0.7400 | 0.0000 | 0.2600 | 1.561 | 1.6197 | 0.540 | 0.000 | 15.1 | 2.207 | 0.7400 | n/a | 0.195 |
| P13 | h10 | carries | 0.9000 | 0.8404 | -0.0596 | 0.0584 | 0.7400 | 0.0000 | 0.2600 | 1.618 | 0.1561 | 0.580 | 0.000 | 15.0 | 2.264 | 0.7400 | 118.0 | 0.195 |
| P13 | h10 | depends | 0.8983 | 0.8382 | -0.0600 | 0.0590 | 0.7400 | 0.0000 | 0.2600 | 1.623 | 0.1575 | 0.580 | 0.000 | 15.0 | 2.269 | 0.7400 | 104.6 | 0.195 |
| P13 | h10 | carried_margin | 9.6232 | 8.9903 | -0.6329 | 0.6055 | 0.7400 | 0.0000 | 0.2600 | 1.609 | 1.6396 | 0.520 | 0.000 | 15.2 | 2.263 | 0.7400 | n/a | 0.195 |
| P13 | h10 | own_margin | 10.7131 | 10.7279 | 0.0148 | 0.0962 | 0.9800 | 0.0100 | 0.0100 | 1.508 | 0.2301 | 0.440 | 0.290 | 9.9 | 0.910 | 0.8800 | n/a | 0.195 |
| P13 | h10 | kappa | 0.9812 | 0.9830 | 0.0017 | 0.0016 | 0.7400 | 0.2600 | 0.0000 | 1.445 | 0.0044 | 0.560 | 0.000 | 15.2 | 2.257 | 0.7400 | 11.4 | 0.195 |
| P13 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4054 | 0.0130 | 0.0403 | 0.9500 | 0.0500 | 0.0000 | 1.007 | 0.0913 | 0.060 | 0.550 | 8.5 | 0.973 | 0.6700 | n/a | 0.195 |
| P13 | h10 | carried_added | 9.8074 | 9.1472 | -0.6602 | 0.6310 | 0.7400 | 0.0000 | 0.2600 | 1.607 | 1.7043 | 0.520 | 0.000 | 15.2 | 2.285 | 0.7400 | n/a | 0.195 |
| P13 | h10 | pooled_retention | 0.9000 | 0.8400 | -0.0600 | 0.0586 | 0.7400 | 0.0000 | 0.2600 | 1.555 | 0.1548 | 0.580 | 0.000 | 15.2 | 2.441 | 0.7400 | 121.5 | 0.195 |
| T1 | n20 | large | -0.2236 | -0.2209 | 0.0027 | 0.0395 | 0.9600 | 0.0300 | 0.0100 | 1.057 | 0.0827 | 0.470 | 0.080 | 12.2 | 0.944 | n/a | n/a | n/a |
| T1 | n20 | carries | 0.6000 | 0.6008 | 0.0008 | 0.0595 | 0.8700 | 0.0000 | 0.1300 | 0.910 | 0.1102 | 0.610 | 0.020 | 13.4 | 1.743 | n/a | 10.8 | n/a |
| T1 | n20 | depends | 0.4041 | 0.4072 | 0.0031 | 0.0852 | 0.9300 | 0.0000 | 0.0700 | 1.015 | 0.1561 | 0.460 | 0.040 | 13.5 | 1.098 | n/a | 10.5 | n/a |
| T1 | n20 | carried_margin | 0.1517 | 0.1522 | 0.0005 | 0.0374 | 0.9600 | 0.0000 | 0.0400 | 0.960 | 0.0721 | 0.050 | 0.390 | 9.4 | 0.953 | n/a | n/a | n/a |
| T1 | n20 | own_margin | 0.3753 | 0.3731 | -0.0022 | 0.0440 | 0.9400 | 0.0000 | 0.0600 | 0.818 | 0.1094 | 0.080 | 0.750 | 5.3 | 1.222 | n/a | n/a | n/a |
| T1 | n20 | kappa | 0.4521 | 0.4557 | 0.0035 | 0.0770 | 0.9400 | 0.0400 | 0.0200 | 0.924 | 0.1571 | 0.040 | 0.120 | 13.7 | 1.016 | n/a | 8.3 | n/a |
| T1 | n20 | shuffled_vs_yardstick | -0.3753 | -0.3731 | 0.0022 | 0.0440 | 0.9400 | 0.0600 | 0.0000 | 0.818 | 0.1094 | 0.080 | 0.750 | 5.3 | 1.222 | n/a | n/a | n/a |
| T1 | n20 | carried_added | 0.3354 | 0.3323 | -0.0031 | 0.0469 | 0.8800 | 0.0000 | 0.1200 | 0.934 | 0.0865 | 0.050 | 0.170 | 12.7 | 1.339 | n/a | n/a | n/a |
| T1 | n20 | pooled_retention | 0.6000 | 0.5945 | -0.0055 | 0.0493 | 0.7600 | 0.0000 | 0.2400 | 0.997 | 0.1048 | 0.710 | 0.000 | 15.1 | 1.859 | n/a | 10.7 | n/a |
| T1 | n40 | large | 0.5777 | 0.5853 | 0.0076 | 0.1559 | 0.9200 | 0.0000 | 0.0800 | 0.906 | 0.3092 | 0.310 | 0.050 | 12.7 | 1.330 | n/a | n/a | n/a |
| T1 | n40 | carries | 0.6000 | 0.6036 | 0.0036 | 0.0914 | 0.9200 | 0.0300 | 0.0500 | 0.897 | 0.1814 | 0.680 | 0.000 | 14.0 | 1.084 | n/a | 8.2 | n/a |
| T1 | n40 | depends | 0.5570 | 0.5624 | 0.0053 | 0.0979 | 0.9300 | 0.0300 | 0.0400 | 0.897 | 0.1925 | 0.650 | 0.000 | 14.0 | 1.038 | n/a | 7.7 | n/a |
| T1 | n40 | carried_margin | 0.9530 | 0.9584 | 0.0054 | 0.1753 | 0.9300 | 0.0000 | 0.0700 | 0.888 | 0.3444 | 0.120 | 0.170 | 11.1 | 1.117 | n/a | n/a | n/a |
| T1 | n40 | own_margin | 1.7109 | 1.7192 | 0.0084 | 0.2550 | 0.9200 | 0.0100 | 0.0700 | 0.889 | 0.5086 | 0.170 | 0.350 | 9.6 | 1.316 | n/a | n/a | n/a |
| T1 | n40 | kappa | 0.8384 | 0.8399 | 0.0016 | 0.0262 | 0.9400 | 0.0600 | 0.0000 | 0.973 | 0.0522 | 0.120 | 0.100 | 12.6 | 1.085 | n/a | 6.7 | n/a |
| T1 | n40 | shuffled_vs_yardstick | -0.3753 | -0.3731 | 0.0022 | 0.0441 | 0.9300 | 0.0700 | 0.0000 | 0.816 | 0.1089 | 0.070 | 0.730 | 5.3 | 1.217 | n/a | n/a | n/a |
| T1 | n40 | carried_added | 1.1368 | 1.1386 | 0.0018 | 0.1906 | 0.9300 | 0.0000 | 0.0700 | 0.888 | 0.3697 | 0.130 | 0.120 | 12.0 | 1.223 | n/a | n/a | n/a |
| T1 | n40 | pooled_retention | 0.6000 | 0.5945 | -0.0055 | 0.0494 | 0.7700 | 0.0000 | 0.2300 | 0.987 | 0.1053 | 0.720 | 0.000 | 15.1 | 1.830 | n/a | 8.0 | n/a |
| T1 | n80 | large | 5.4462 | 5.4093 | -0.0369 | 0.8985 | 0.9400 | 0.0100 | 0.0500 | 1.028 | 2.1532 | 0.120 | 0.540 | 7.5 | 1.036 | n/a | n/a | n/a |
| T1 | n80 | carries | 0.6000 | 0.5970 | -0.0030 | 0.0725 | 0.9400 | 0.0000 | 0.0600 | 1.496 | 0.1770 | 0.690 | 0.030 | 13.9 | 1.029 | n/a | 7.9 | n/a |
| T1 | n80 | depends | 0.5925 | 0.5896 | -0.0029 | 0.0729 | 0.9400 | 0.0000 | 0.0600 | 1.503 | 0.1781 | 0.700 | 0.030 | 13.8 | 1.019 | n/a | 7.8 | n/a |
| T1 | n80 | carried_margin | 5.8214 | 5.7822 | -0.0392 | 0.9323 | 0.9400 | 0.0100 | 0.0500 | 1.010 | 2.2193 | 0.100 | 0.580 | 7.3 | 1.041 | n/a | n/a | n/a |
| T1 | n80 | own_margin | 9.8249 | 9.8536 | 0.0287 | 1.4031 | 0.9000 | 0.0400 | 0.0600 | 0.913 | 3.7682 | 0.150 | 0.650 | 6.5 | 1.238 | n/a | n/a | n/a |
| T1 | n80 | kappa | 0.9694 | 0.9693 | -0.0002 | 0.0063 | 0.9400 | 0.0500 | 0.0100 | 0.720 | 0.0115 | 0.100 | 0.490 | 8.2 | 1.047 | n/a | 6.5 | n/a |
| T1 | n80 | shuffled_vs_yardstick | -0.3753 | -0.3729 | 0.0023 | 0.0440 | 0.9400 | 0.0600 | 0.0000 | 0.815 | 0.1095 | 0.080 | 0.750 | 5.3 | 1.224 | n/a | n/a | n/a |
| T1 | n80 | carried_added | 6.0052 | 5.9625 | -0.0427 | 0.9427 | 0.9400 | 0.0100 | 0.0500 | 1.022 | 2.2310 | 0.100 | 0.550 | 7.6 | 1.018 | n/a | n/a | n/a |
| T1 | n80 | pooled_retention | 0.6000 | 0.5947 | -0.0053 | 0.0488 | 0.7700 | 0.0000 | 0.2300 | 1.014 | 0.1036 | 0.850 | 0.000 | 15.0 | 1.896 | n/a | 7.3 | n/a |
| T1 | n160 | large | 12.8347 | 12.7297 | -0.1050 | 1.2199 | 0.9300 | 0.0000 | 0.0700 | 1.121 | 2.7475 | 0.570 | 0.040 | 13.6 | 1.192 | n/a | n/a | n/a |
| T1 | n160 | carries | 0.6000 | 0.5938 | -0.0062 | 0.0716 | 0.9100 | 0.0000 | 0.0900 | 1.228 | 0.1655 | 0.600 | 0.070 | 13.7 | 1.220 | n/a | 19.2 | n/a |
| T1 | n160 | depends | 0.5967 | 0.5906 | -0.0061 | 0.0717 | 0.9100 | 0.0000 | 0.0900 | 1.232 | 0.1657 | 0.600 | 0.070 | 13.7 | 1.220 | n/a | 18.9 | n/a |
| T1 | n160 | carried_margin | 13.2100 | 13.1028 | -0.1072 | 1.2318 | 0.9300 | 0.0000 | 0.0700 | 1.119 | 2.7693 | 0.540 | 0.050 | 13.6 | 1.171 | n/a | n/a | n/a |
| T1 | n160 | own_margin | 22.1392 | 22.2792 | 0.1400 | 1.2343 | 0.9500 | 0.0500 | 0.0000 | 1.066 | 2.6251 | 0.550 | 0.190 | 11.7 | 1.005 | n/a | n/a | n/a |
| T1 | n160 | kappa | 0.9863 | 0.9865 | 0.0002 | 0.0016 | 0.8400 | 0.1600 | 0.0000 | 0.892 | 0.0033 | 0.530 | 0.000 | 14.2 | 1.597 | n/a | 10.1 | n/a |
| T1 | n160 | shuffled_vs_yardstick | -0.3753 | -0.3730 | 0.0022 | 0.0441 | 0.9400 | 0.0600 | 0.0000 | 0.817 | 0.1093 | 0.080 | 0.740 | 5.2 | 1.226 | n/a | n/a | n/a |
| T1 | n160 | carried_added | 13.3937 | 13.2830 | -0.1108 | 1.2577 | 0.9300 | 0.0000 | 0.0700 | 1.117 | 2.8339 | 0.540 | 0.050 | 13.7 | 1.190 | n/a | n/a | n/a |
| T1 | n160 | pooled_retention | 0.6000 | 0.5945 | -0.0055 | 0.0488 | 0.7900 | 0.0000 | 0.2100 | 1.012 | 0.1033 | 0.490 | 0.000 | 15.1 | 1.933 | n/a | 19.1 | n/a |
| T1 | n320 | large | 14.9997 | 14.9589 | -0.0408 | 1.4843 | 0.9100 | 0.0000 | 0.0900 | 0.999 | 3.0820 | 0.600 | 0.030 | 14.0 | 1.201 | n/a | n/a | n/a |
| T1 | n320 | carries | 0.6000 | 0.5979 | -0.0021 | 0.0767 | 0.9200 | 0.0000 | 0.0800 | 1.088 | 0.1635 | 0.520 | 0.040 | 13.7 | 1.279 | n/a | 20.6 | n/a |
| T1 | n320 | depends | 0.5971 | 0.5952 | -0.0020 | 0.0768 | 0.9200 | 0.0000 | 0.0800 | 1.089 | 0.1636 | 0.520 | 0.050 | 13.7 | 1.274 | n/a | 20.2 | n/a |
| T1 | n320 | carried_margin | 15.3749 | 15.3319 | -0.0430 | 1.4856 | 0.9100 | 0.0000 | 0.0900 | 1.006 | 3.1176 | 0.590 | 0.030 | 14.0 | 1.160 | n/a | n/a | n/a |
| T1 | n320 | own_margin | 25.7474 | 25.8697 | 0.1223 | 1.1678 | 0.9600 | 0.0400 | 0.0000 | 1.370 | 2.8012 | 0.590 | 0.150 | 12.0 | 0.925 | n/a | n/a | n/a |
| T1 | n320 | kappa | 0.9882 | 0.9884 | 0.0002 | 0.0013 | 0.8600 | 0.1400 | 0.0000 | 0.992 | 0.0027 | 0.590 | 0.000 | 14.4 | 1.599 | n/a | 10.6 | n/a |
| T1 | n320 | shuffled_vs_yardstick | -0.3753 | -0.3730 | 0.0023 | 0.0440 | 0.9300 | 0.0700 | 0.0000 | 0.817 | 0.1097 | 0.070 | 0.740 | 5.3 | 1.212 | n/a | n/a | n/a |
| T1 | n320 | carried_added | 15.5587 | 15.5121 | -0.0465 | 1.5133 | 0.9000 | 0.0000 | 0.1000 | 1.005 | 3.1800 | 0.590 | 0.030 | 14.0 | 1.174 | n/a | n/a | n/a |
| T1 | n320 | pooled_retention | 0.6000 | 0.5954 | -0.0046 | 0.0489 | 0.7800 | 0.0000 | 0.2200 | 1.015 | 0.1059 | 0.500 | 0.000 | 15.1 | 1.836 | n/a | 20.7 | n/a |
| T1 | h2 | large | 0.5840 | 0.5806 | -0.0034 | 0.0723 | 0.9200 | 0.0000 | 0.0800 | 0.809 | 0.1325 | 0.140 | 0.180 | 11.8 | 1.155 | n/a | n/a | 1.000 |
| T1 | h2 | carries | 0.6000 | 0.5958 | -0.0042 | 0.0459 | 0.8000 | 0.0000 | 0.2000 | 1.027 | 0.0978 | 0.630 | 0.000 | 15.1 | 1.918 | n/a | 132.5 | 1.000 |
| T1 | h2 | depends | 0.5573 | 0.5543 | -0.0030 | 0.0434 | 0.8000 | 0.0000 | 0.2000 | 1.051 | 0.0915 | 0.650 | 0.000 | 15.1 | 1.899 | n/a | 63.7 | 1.000 |
| T1 | h2 | carried_margin | 0.9595 | 0.9537 | -0.0058 | 0.0618 | 0.7900 | 0.0000 | 0.2100 | 0.983 | 0.1296 | 0.530 | 0.000 | 15.2 | 1.710 | n/a | n/a | 1.000 |
| T1 | h2 | own_margin | 1.7216 | 1.7223 | 0.0007 | 0.0258 | 0.9200 | 0.0800 | 0.0000 | 1.228 | 0.0581 | 0.450 | 0.010 | 14.6 | 1.054 | n/a | n/a | 1.000 |
| T1 | h2 | kappa | 0.8393 | 0.8423 | 0.0030 | 0.0152 | 0.7900 | 0.2100 | 0.0000 | 0.966 | 0.0325 | 0.580 | 0.000 | 15.1 | 1.634 | n/a | 12.4 | 1.000 |
| T1 | h2 | shuffled_vs_yardstick | -0.3755 | -0.3731 | 0.0024 | 0.0441 | 0.9300 | 0.0700 | 0.0000 | 0.810 | 0.1095 | 0.080 | 0.760 | 5.2 | 1.229 | n/a | n/a | 1.000 |
| T1 | h2 | carried_added | 1.1432 | 1.1338 | -0.0094 | 0.0939 | 0.7800 | 0.0000 | 0.2200 | 0.988 | 0.1975 | 0.560 | 0.000 | 15.1 | 1.955 | n/a | n/a | 1.000 |
| T1 | h2 | pooled_retention | 0.6000 | 0.5949 | -0.0051 | 0.0490 | 0.7700 | 0.0000 | 0.2300 | 0.990 | 0.1039 | 0.700 | 0.000 | 15.1 | 1.930 | n/a | 133.6 | 1.000 |
| T1 | h5 | large | 2.5194 | 2.4938 | -0.0255 | 0.2148 | 0.8200 | 0.0000 | 0.1800 | 0.984 | 0.4293 | 0.440 | 0.000 | 15.3 | 1.660 | n/a | n/a | 1.000 |
| T1 | h5 | carries | 0.6000 | 0.5944 | -0.0056 | 0.0489 | 0.7900 | 0.0000 | 0.2100 | 1.045 | 0.1051 | 0.580 | 0.000 | 15.2 | 1.797 | n/a | 163.7 | 1.000 |
| T1 | h5 | depends | 0.5851 | 0.5799 | -0.0052 | 0.0482 | 0.7900 | 0.0000 | 0.2100 | 1.055 | 0.1033 | 0.580 | 0.000 | 15.2 | 1.790 | n/a | 101.9 | 1.000 |
| T1 | h5 | carried_margin | 2.8948 | 2.8669 | -0.0279 | 0.2137 | 0.7900 | 0.0000 | 0.2100 | 1.047 | 0.4613 | 0.560 | 0.000 | 15.3 | 1.763 | n/a | n/a | 1.000 |
| T1 | h5 | own_margin | 4.9472 | 4.9468 | -0.0004 | 0.0537 | 0.9500 | 0.0500 | 0.0000 | 1.005 | 0.1129 | 0.580 | 0.100 | 13.1 | 0.946 | n/a | n/a | 1.000 |
| T1 | h5 | kappa | 0.9403 | 0.9413 | 0.0010 | 0.0058 | 0.7800 | 0.2100 | 0.0100 | 0.931 | 0.0123 | 0.510 | 0.000 | 15.2 | 1.653 | n/a | 12.4 | 1.000 |
| T1 | h5 | shuffled_vs_yardstick | -0.3755 | -0.3731 | 0.0024 | 0.0442 | 0.9200 | 0.0600 | 0.0200 | 0.804 | 0.1018 | 0.130 | 0.650 | 5.9 | 1.163 | n/a | n/a | 1.000 |
| T1 | h5 | carried_added | 3.0786 | 3.0471 | -0.0315 | 0.2461 | 0.7900 | 0.0000 | 0.2100 | 1.039 | 0.5303 | 0.580 | 0.000 | 15.2 | 1.851 | n/a | n/a | 1.000 |
| T1 | h5 | pooled_retention | 0.6000 | 0.5940 | -0.0060 | 0.0486 | 0.7800 | 0.0000 | 0.2200 | 1.006 | 0.1032 | 0.530 | 0.000 | 15.1 | 1.999 | n/a | 155.7 | 1.000 |
| T1 | h10 | large | 5.9817 | 5.8314 | -0.1502 | 0.4101 | 0.7900 | 0.0000 | 0.2100 | 1.145 | 0.8922 | 0.570 | 0.000 | 15.1 | 1.890 | n/a | n/a | 0.455 |
| T1 | h10 | carries | 0.6000 | 0.5853 | -0.0147 | 0.0411 | 0.7700 | 0.0000 | 0.2300 | 1.153 | 0.0925 | 0.730 | 0.000 | 15.0 | 1.884 | n/a | 125.6 | 0.455 |
| T1 | h10 | depends | 0.5931 | 0.5787 | -0.0145 | 0.0408 | 0.7700 | 0.0000 | 0.2300 | 1.159 | 0.0918 | 0.730 | 0.000 | 15.0 | 1.881 | n/a | 116.5 | 0.455 |
| T1 | h10 | carried_margin | 6.3571 | 6.2080 | -0.1491 | 0.4150 | 0.7800 | 0.0000 | 0.2200 | 1.169 | 0.9331 | 0.530 | 0.000 | 15.1 | 1.925 | n/a | n/a | 0.455 |
| T1 | h10 | own_margin | 10.7177 | 10.7309 | 0.0132 | 0.0996 | 0.9300 | 0.0300 | 0.0400 | 1.129 | 0.2006 | 0.570 | 0.200 | 11.3 | 1.243 | n/a | n/a | 0.455 |
| T1 | h10 | kappa | 0.9719 | 0.9730 | 0.0011 | 0.0024 | 0.7600 | 0.2400 | 0.0000 | 0.989 | 0.0051 | 0.560 | 0.000 | 15.2 | 1.879 | n/a | 13.7 | 0.455 |
| T1 | h10 | shuffled_vs_yardstick | -0.3755 | -0.3766 | -0.0012 | 0.0404 | 0.9300 | 0.0500 | 0.0200 | 0.799 | 0.0809 | 0.050 | 0.610 | 7.8 | 1.117 | n/a | n/a | 0.455 |
| T1 | h10 | carried_added | 6.5409 | 6.3811 | -0.1597 | 0.4422 | 0.7600 | 0.0000 | 0.2400 | 1.164 | 0.9909 | 0.530 | 0.000 | 15.1 | 1.948 | n/a | n/a | 0.455 |
| T1 | h10 | pooled_retention | 0.6000 | 0.5848 | -0.0152 | 0.0402 | 0.7600 | 0.0000 | 0.2400 | 1.168 | 0.0908 | 0.550 | 0.000 | 15.2 | 2.054 | n/a | 117.6 | 0.455 |
| T2 | n20 | large | -0.2755 | -0.2685 | 0.0071 | 0.0675 | 0.9400 | 0.0500 | 0.0100 | 0.993 | 0.1363 | 0.630 | 0.020 | 13.4 | 1.011 | n/a | n/a | n/a |
| T2 | n20 | carries | 0.6000 | 0.5968 | -0.0032 | 0.0786 | 0.9400 | 0.0000 | 0.0600 | 0.985 | 0.1675 | 0.710 | 0.000 | 14.3 | 1.162 | n/a | 7.7 | n/a |
| T2 | n20 | depends | 0.4531 | 0.4515 | -0.0015 | 0.1060 | 0.9300 | 0.0100 | 0.0600 | 1.017 | 0.2245 | 0.640 | 0.000 | 14.4 | 1.069 | n/a | 8.5 | n/a |
| T2 | n20 | carried_margin | 0.2282 | 0.2192 | -0.0090 | 0.0573 | 0.9000 | 0.0000 | 0.1000 | 1.035 | 0.1197 | 0.160 | 0.100 | 11.4 | 1.529 | n/a | n/a | n/a |
| T2 | n20 | own_margin | 0.5038 | 0.4877 | -0.0161 | 0.0684 | 0.8800 | 0.0100 | 0.1100 | 0.908 | 0.1553 | 0.190 | 0.540 | 7.2 | 1.951 | n/a | n/a | n/a |
| T2 | n20 | kappa | 0.5522 | 0.5525 | 0.0002 | 0.0906 | 0.9500 | 0.0300 | 0.0200 | 0.960 | 0.1908 | 0.160 | 0.000 | 15.1 | 0.993 | n/a | 5.7 | n/a |
| T2 | n20 | shuffled_vs_yardstick | -0.5038 | -0.4877 | 0.0161 | 0.0684 | 0.8800 | 0.1100 | 0.0100 | 0.908 | 0.1553 | 0.190 | 0.540 | 7.2 | 1.951 | n/a | n/a | n/a |
| T2 | n20 | carried_added | 0.4133 | 0.3949 | -0.0184 | 0.0679 | 0.8900 | 0.0000 | 0.1100 | 1.163 | 0.1500 | 0.160 | 0.020 | 14.3 | 1.189 | n/a | n/a | n/a |
| T2 | n20 | pooled_retention | 0.6000 | 0.5856 | -0.0144 | 0.0623 | 0.9300 | 0.0000 | 0.0700 | 1.143 | 0.1442 | 0.800 | 0.000 | 15.0 | 1.101 | n/a | 7.6 | n/a |
| T2 | n40 | large | 0.6165 | 0.5748 | -0.0417 | 0.1303 | 0.9400 | 0.0000 | 0.0600 | 1.567 | 0.3362 | 0.490 | 0.020 | 14.6 | 1.005 | n/a | n/a | n/a |
| T2 | n40 | carries | 0.6000 | 0.5849 | -0.0151 | 0.0624 | 0.9900 | 0.0000 | 0.0100 | 1.763 | 0.1755 | 0.610 | 0.010 | 14.3 | 0.848 | n/a | 8.4 | n/a |
| T2 | n40 | depends | 0.5628 | 0.5479 | -0.0149 | 0.0660 | 0.9700 | 0.0000 | 0.0300 | 1.759 | 0.1841 | 0.610 | 0.010 | 14.4 | 0.822 | n/a | 8.6 | n/a |
| T2 | n40 | carried_margin | 1.1202 | 1.0625 | -0.0578 | 0.1522 | 0.9500 | 0.0000 | 0.0500 | 1.488 | 0.3953 | 0.150 | 0.040 | 14.0 | 0.969 | n/a | n/a | n/a |
| T2 | n40 | own_margin | 1.9905 | 1.9479 | -0.0426 | 0.2356 | 0.9600 | 0.0000 | 0.0400 | 1.029 | 0.4956 | 0.110 | 0.180 | 11.0 | 0.940 | n/a | n/a | n/a |
| T2 | n40 | kappa | 0.8582 | 0.8584 | 0.0002 | 0.0261 | 0.9700 | 0.0300 | 0.0000 | 1.096 | 0.0571 | 0.140 | 0.000 | 15.6 | 0.879 | n/a | 6.0 | n/a |
| T2 | n40 | shuffled_vs_yardstick | -0.5038 | -0.4877 | 0.0161 | 0.0685 | 0.8800 | 0.1100 | 0.0100 | 0.906 | 0.1558 | 0.200 | 0.540 | 7.2 | 2.019 | n/a | n/a | n/a |
| T2 | n40 | carried_added | 1.3053 | 1.2381 | -0.0672 | 0.1755 | 0.9400 | 0.0000 | 0.0600 | 1.456 | 0.4485 | 0.150 | 0.020 | 15.0 | 1.140 | n/a | n/a | n/a |
| T2 | n40 | pooled_retention | 0.6000 | 0.5861 | -0.0139 | 0.0614 | 0.9400 | 0.0000 | 0.0600 | 1.174 | 0.1442 | 0.710 | 0.000 | 15.0 | 1.059 | n/a | 8.0 | n/a |
| T2 | n80 | large | 5.0693 | 4.7438 | -0.3254 | 0.8065 | 0.9100 | 0.0000 | 0.0900 | 1.165 | 1.8931 | 0.220 | 0.240 | 10.0 | 1.309 | n/a | n/a | n/a |
| T2 | n80 | carries | 0.6000 | 0.5784 | -0.0216 | 0.1004 | 0.9600 | 0.0000 | 0.0400 | 1.081 | 0.2146 | 0.650 | 0.010 | 14.0 | 0.899 | n/a | 8.8 | n/a |
| T2 | n80 | depends | 0.5921 | 0.5707 | -0.0215 | 0.1005 | 0.9600 | 0.0000 | 0.0400 | 1.084 | 0.2143 | 0.630 | 0.010 | 14.0 | 0.900 | n/a | 8.5 | n/a |
| T2 | n80 | carried_margin | 5.5730 | 5.2316 | -0.3414 | 0.8552 | 0.9200 | 0.0000 | 0.0800 | 1.145 | 1.9801 | 0.180 | 0.320 | 9.8 | 1.317 | n/a | n/a | n/a |
| T2 | n80 | own_margin | 9.4118 | 9.2794 | -0.1323 | 1.3542 | 0.8900 | 0.0400 | 0.0700 | 0.832 | 3.2550 | 0.140 | 0.570 | 6.9 | 1.498 | n/a | n/a | n/a |
| T2 | n80 | kappa | 0.9679 | 0.9675 | -0.0004 | 0.0061 | 0.9400 | 0.0400 | 0.0200 | 1.095 | 0.0133 | 0.180 | 0.130 | 11.9 | 1.077 | n/a | 6.0 | n/a |
| T2 | n80 | shuffled_vs_yardstick | -0.5038 | -0.4877 | 0.0160 | 0.0685 | 0.8800 | 0.1100 | 0.0100 | 0.905 | 0.1556 | 0.200 | 0.540 | 7.1 | 1.976 | n/a | n/a | n/a |
| T2 | n80 | carried_added | 5.7581 | 5.4072 | -0.3509 | 0.8805 | 0.9000 | 0.0000 | 0.1000 | 1.147 | 2.0506 | 0.180 | 0.240 | 10.2 | 1.328 | n/a | n/a | n/a |
| T2 | n80 | pooled_retention | 0.6000 | 0.5857 | -0.0143 | 0.0616 | 0.9300 | 0.0000 | 0.0700 | 1.152 | 0.1423 | 0.760 | 0.000 | 15.0 | 1.106 | n/a | 8.3 | n/a |
| T2 | n160 | large | 11.5374 | 11.2413 | -0.2960 | 1.4606 | 0.9500 | 0.0000 | 0.0500 | 1.145 | 3.2629 | 0.580 | 0.000 | 15.0 | 0.882 | n/a | n/a | n/a |
| T2 | n160 | carries | 0.6000 | 0.5884 | -0.0116 | 0.1056 | 0.9000 | 0.0000 | 0.1000 | 1.179 | 0.2331 | 0.620 | 0.000 | 14.9 | 1.198 | n/a | 14.4 | n/a |
| T2 | n160 | depends | 0.5963 | 0.5850 | -0.0113 | 0.1056 | 0.9000 | 0.0000 | 0.1000 | 1.182 | 0.2329 | 0.620 | 0.000 | 14.9 | 1.200 | n/a | 13.9 | n/a |
| T2 | n160 | carried_margin | 12.0411 | 11.7290 | -0.3121 | 1.4845 | 0.9500 | 0.0000 | 0.0500 | 1.143 | 3.3754 | 0.590 | 0.000 | 15.0 | 0.886 | n/a | n/a | n/a |
| T2 | n160 | own_margin | 20.1919 | 20.2655 | 0.0736 | 1.4825 | 0.9800 | 0.0200 | 0.0000 | 1.057 | 3.2825 | 0.600 | 0.080 | 12.9 | 0.954 | n/a | n/a | n/a |
| T2 | n160 | kappa | 0.9849 | 0.9854 | 0.0005 | 0.0023 | 0.9700 | 0.0300 | 0.0000 | 1.113 | 0.0050 | 0.560 | 0.000 | 15.3 | 0.945 | n/a | 7.5 | n/a |
| T2 | n160 | shuffled_vs_yardstick | -0.5038 | -0.4877 | 0.0161 | 0.0685 | 0.8800 | 0.1100 | 0.0100 | 0.907 | 0.1561 | 0.190 | 0.540 | 7.2 | 2.022 | n/a | n/a | n/a |
| T2 | n160 | carried_added | 12.2262 | 11.9047 | -0.3215 | 1.5193 | 0.9500 | 0.0000 | 0.0500 | 1.142 | 3.4527 | 0.590 | 0.000 | 15.0 | 0.891 | n/a | n/a | n/a |
| T2 | n160 | pooled_retention | 0.6000 | 0.5860 | -0.0140 | 0.0616 | 0.9400 | 0.0000 | 0.0600 | 1.162 | 0.1448 | 0.460 | 0.000 | 15.0 | 1.090 | n/a | 13.2 | n/a |
| T2 | n320 | large | 13.5205 | 13.2335 | -0.2870 | 1.6890 | 0.9400 | 0.0000 | 0.0600 | 1.140 | 3.7855 | 0.620 | 0.000 | 15.0 | 1.095 | n/a | n/a | n/a |
| T2 | n320 | carries | 0.6000 | 0.5871 | -0.0129 | 0.1038 | 0.9100 | 0.0000 | 0.0900 | 1.177 | 0.2301 | 0.570 | 0.010 | 15.0 | 1.154 | n/a | 15.1 | n/a |
| T2 | n320 | depends | 0.5968 | 0.5842 | -0.0127 | 0.1038 | 0.9200 | 0.0000 | 0.0800 | 1.181 | 0.2298 | 0.580 | 0.010 | 15.0 | 1.150 | n/a | 14.6 | n/a |
| T2 | n320 | carried_margin | 14.0243 | 13.7213 | -0.3030 | 1.7064 | 0.9300 | 0.0000 | 0.0700 | 1.145 | 3.8615 | 0.600 | 0.000 | 15.1 | 1.116 | n/a | n/a | n/a |
| T2 | n320 | own_margin | 23.4972 | 23.7266 | 0.2294 | 1.5814 | 0.9600 | 0.0300 | 0.0100 | 1.134 | 3.4976 | 0.540 | 0.050 | 13.4 | 0.961 | n/a | n/a | n/a |
| T2 | n320 | kappa | 0.9870 | 0.9875 | 0.0005 | 0.0019 | 0.9600 | 0.0300 | 0.0100 | 1.121 | 0.0042 | 0.610 | 0.000 | 15.3 | 0.982 | n/a | 7.6 | n/a |
| T2 | n320 | shuffled_vs_yardstick | -0.5038 | -0.4877 | 0.0160 | 0.0685 | 0.8900 | 0.1000 | 0.0100 | 0.905 | 0.1555 | 0.190 | 0.540 | 7.1 | 1.957 | n/a | n/a | n/a |
| T2 | n320 | carried_added | 14.2094 | 13.8968 | -0.3125 | 1.7415 | 0.9300 | 0.0000 | 0.0700 | 1.144 | 3.9494 | 0.600 | 0.000 | 15.1 | 1.119 | n/a | n/a | n/a |
| T2 | n320 | pooled_retention | 0.6000 | 0.5862 | -0.0138 | 0.0611 | 0.9400 | 0.0000 | 0.0600 | 1.164 | 0.1414 | 0.540 | 0.000 | 15.0 | 1.071 | n/a | 14.1 | n/a |
| T2 | h2 | large | 0.4690 | 0.4667 | -0.0023 | 0.0895 | 0.9300 | 0.0200 | 0.0500 | 0.832 | 0.1846 | 0.210 | 0.240 | 10.7 | 1.058 | n/a | n/a | 1.000 |
| T2 | h2 | carries | 0.6000 | 0.5862 | -0.0138 | 0.0584 | 0.9400 | 0.0000 | 0.0600 | 1.133 | 0.1343 | 0.700 | 0.000 | 15.1 | 1.040 | n/a | 103.8 | 1.000 |
| T2 | h2 | depends | 0.5576 | 0.5460 | -0.0116 | 0.0539 | 0.9400 | 0.0000 | 0.0600 | 1.163 | 0.1232 | 0.680 | 0.000 | 15.1 | 1.098 | n/a | 52.6 | 1.000 |
| T2 | h2 | carried_margin | 0.9731 | 0.9544 | -0.0187 | 0.0775 | 0.9400 | 0.0000 | 0.0600 | 1.175 | 0.1810 | 0.520 | 0.000 | 15.1 | 1.070 | n/a | n/a | 1.000 |
| T2 | h2 | own_margin | 1.7452 | 1.7511 | 0.0059 | 0.0325 | 0.9500 | 0.0500 | 0.0000 | 1.078 | 0.0712 | 0.520 | 0.000 | 15.0 | 0.994 | n/a | n/a | 1.000 |
| T2 | h2 | kappa | 0.8402 | 0.8467 | 0.0065 | 0.0212 | 0.9500 | 0.0500 | 0.0000 | 1.068 | 0.0461 | 0.490 | 0.000 | 15.0 | 0.925 | n/a | 8.9 | 1.000 |
| T2 | h2 | shuffled_vs_yardstick | -0.5041 | -0.4877 | 0.0164 | 0.0685 | 0.8800 | 0.1100 | 0.0100 | 0.906 | 0.1559 | 0.180 | 0.540 | 7.1 | 1.921 | n/a | n/a | 1.000 |
| T2 | h2 | carried_added | 1.1582 | 1.1300 | -0.0281 | 0.1192 | 0.9400 | 0.0000 | 0.0600 | 1.151 | 0.2753 | 0.530 | 0.000 | 15.1 | 1.035 | n/a | n/a | 1.000 |
| T2 | h2 | pooled_retention | 0.6000 | 0.5861 | -0.0139 | 0.0623 | 0.9300 | 0.0000 | 0.0700 | 1.122 | 0.1422 | 0.590 | 0.000 | 15.0 | 1.024 | n/a | 100.8 | 1.000 |
| T2 | h5 | large | 2.3716 | 2.3271 | -0.0445 | 0.2682 | 0.9400 | 0.0000 | 0.0600 | 1.041 | 0.5766 | 0.350 | 0.000 | 15.5 | 1.016 | n/a | n/a | 1.000 |
| T2 | h5 | carries | 0.6000 | 0.5865 | -0.0135 | 0.0645 | 0.9400 | 0.0000 | 0.0600 | 1.113 | 0.1467 | 0.630 | 0.000 | 15.1 | 1.028 | n/a | 148.0 | 1.000 |
| T2 | h5 | depends | 0.5849 | 0.5723 | -0.0126 | 0.0633 | 0.9400 | 0.0000 | 0.0600 | 1.122 | 0.1447 | 0.640 | 0.000 | 15.1 | 1.037 | n/a | 69.9 | 1.000 |
| T2 | h5 | carried_margin | 2.8757 | 2.8144 | -0.0612 | 0.2775 | 0.9500 | 0.0000 | 0.0500 | 1.114 | 0.6303 | 0.530 | 0.000 | 15.1 | 1.008 | n/a | n/a | 1.000 |
| T2 | h5 | own_margin | 4.9161 | 4.9241 | 0.0079 | 0.0665 | 0.9400 | 0.0600 | 0.0000 | 1.108 | 0.1502 | 0.620 | 0.000 | 14.1 | 1.016 | n/a | n/a | 1.000 |
| T2 | h5 | kappa | 0.9395 | 0.9421 | 0.0025 | 0.0080 | 0.9600 | 0.0400 | 0.0000 | 1.082 | 0.0174 | 0.530 | 0.000 | 15.1 | 0.897 | n/a | 9.0 | 1.000 |
| T2 | h5 | shuffled_vs_yardstick | -0.5041 | -0.4873 | 0.0168 | 0.0687 | 0.8900 | 0.1000 | 0.0100 | 0.977 | 0.1646 | 0.220 | 0.570 | 7.1 | 1.922 | n/a | n/a | 1.000 |
| T2 | h5 | carried_added | 3.0607 | 2.9901 | -0.0706 | 0.3193 | 0.9400 | 0.0000 | 0.0600 | 1.113 | 0.7253 | 0.520 | 0.000 | 15.1 | 1.014 | n/a | n/a | 1.000 |
| T2 | h5 | pooled_retention | 0.6000 | 0.5864 | -0.0136 | 0.0621 | 0.9400 | 0.0000 | 0.0600 | 1.127 | 0.1422 | 0.590 | 0.000 | 15.0 | 1.038 | n/a | 136.9 | 1.000 |
| T2 | h10 | large | 5.8435 | 5.0645 | -0.7790 | 0.3668 | 0.7222 | 0.0000 | 0.2778 | 2.196 | 1.1780 | 0.611 | 0.000 | 15.2 | 1.923 | n/a | n/a | 0.018 |
| T2 | h10 | carries | 0.6000 | 0.5194 | -0.0806 | 0.0391 | 0.6667 | 0.0000 | 0.3333 | 2.022 | 0.1168 | 0.500 | 0.000 | 15.2 | 1.846 | n/a | 130.3 | 0.018 |
| T2 | h10 | depends | 0.5931 | 0.5137 | -0.0794 | 0.0384 | 0.6667 | 0.0000 | 0.3333 | 2.029 | 0.1148 | 0.500 | 0.000 | 15.2 | 1.856 | n/a | 120.0 | 0.018 |
| T2 | h10 | carried_margin | 6.3475 | 5.5234 | -0.8241 | 0.4086 | 0.6667 | 0.0000 | 0.3333 | 1.916 | 1.1914 | 0.500 | 0.000 | 15.2 | 1.879 | n/a | n/a | 0.018 |
| T2 | h10 | own_margin | 10.7031 | 10.7534 | 0.0503 | 0.0972 | 0.9444 | 0.0556 | 0.0000 | 1.415 | 0.2018 | 0.500 | 0.111 | 12.5 | 0.955 | n/a | n/a | 0.018 |
| T2 | h10 | kappa | 0.9717 | 0.9771 | 0.0055 | 0.0029 | 0.7222 | 0.2778 | 0.0000 | 1.927 | 0.0084 | 0.389 | 0.000 | 15.1 | 1.509 | n/a | 9.2 | 0.018 |
| T2 | h10 | shuffled_vs_yardstick | -0.5041 | -0.4590 | 0.0451 | 0.0764 | 0.6111 | 0.3889 | 0.0000 | 0.537 | 0.0851 | 0.000 | 0.389 | 11.7 | 1.454 | n/a | n/a | 0.018 |
| T2 | h10 | carried_added | 6.5326 | 5.6538 | -0.8788 | 0.4343 | 0.6667 | 0.0000 | 0.3333 | 1.920 | 1.2663 | 0.500 | 0.000 | 15.2 | 1.877 | n/a | n/a | 0.018 |
| T2 | h10 | pooled_retention | 0.6000 | 0.5186 | -0.0814 | 0.0379 | 0.6667 | 0.0000 | 0.3333 | 2.100 | 0.1163 | 0.444 | 0.000 | 15.1 | 1.910 | n/a | 110.8 | 0.018 |
| T3 | n20 | large | -0.1809 | -0.1846 | -0.0037 | 0.0428 | 0.9300 | 0.0400 | 0.0300 | 1.072 | 0.0929 | 0.460 | 0.160 | 11.2 | 1.105 | n/a | n/a | n/a |
| T3 | n20 | carries | 0.6997 | 0.7023 | 0.0026 | 0.0417 | 0.9700 | 0.0000 | 0.0300 | 1.357 | 0.0998 | 0.560 | 0.180 | 11.4 | 0.784 | n/a | 8.3 | n/a |
| T3 | n20 | depends | 0.5674 | 0.5702 | 0.0028 | 0.0568 | 0.9700 | 0.0100 | 0.0200 | 1.338 | 0.1384 | 0.500 | 0.190 | 11.7 | 0.931 | n/a | 8.6 | n/a |
| T3 | n20 | carried_margin | 0.2372 | 0.2418 | 0.0046 | 0.0323 | 0.9600 | 0.0200 | 0.0200 | 1.172 | 0.0872 | 0.050 | 0.790 | 5.5 | 0.862 | n/a | n/a | n/a |
| T3 | n20 | own_margin | 0.4181 | 0.4264 | 0.0083 | 0.0594 | 0.9000 | 0.0400 | 0.0600 | 0.900 | 0.1446 | 0.170 | 0.680 | 6.4 | 1.204 | n/a | n/a | n/a |
| T3 | n20 | kappa | 0.5629 | 0.5639 | 0.0010 | 0.0651 | 0.9000 | 0.0800 | 0.0200 | 0.870 | 0.1297 | 0.050 | 0.100 | 14.3 | 1.198 | n/a | 7.9 | n/a |
| T3 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4264 | -0.0083 | 0.0594 | 0.9000 | 0.0600 | 0.0400 | 0.900 | 0.1446 | 0.170 | 0.680 | 6.4 | 1.204 | n/a | n/a | n/a |
| T3 | n20 | carried_added | 0.4214 | 0.4308 | 0.0094 | 0.0505 | 0.9900 | 0.0000 | 0.0100 | 1.225 | 0.1166 | 0.050 | 0.190 | 13.2 | 0.877 | n/a | n/a | n/a |
| T3 | n20 | pooled_retention | 0.6997 | 0.7150 | 0.0153 | 0.0972 | 0.9100 | 0.0200 | 0.0700 | 0.874 | 0.1955 | 0.630 | 0.000 | 15.1 | 1.110 | n/a | 8.2 | n/a |
| T3 | n40 | large | 0.8233 | 0.8448 | 0.0214 | 0.1655 | 0.9700 | 0.0000 | 0.0300 | 1.344 | 0.3784 | 0.250 | 0.100 | 12.4 | 0.823 | n/a | n/a | n/a |
| T3 | n40 | carries | 0.7170 | 0.7235 | 0.0064 | 0.0781 | 0.9900 | 0.0000 | 0.0100 | 1.510 | 0.1961 | 0.630 | 0.000 | 13.9 | 0.820 | n/a | 8.3 | n/a |
| T3 | n40 | depends | 0.6881 | 0.6955 | 0.0074 | 0.0842 | 0.9900 | 0.0000 | 0.0100 | 1.512 | 0.2098 | 0.630 | 0.000 | 13.8 | 0.781 | n/a | 8.2 | n/a |
| T3 | n40 | carried_margin | 1.2414 | 1.2713 | 0.0298 | 0.1930 | 0.9900 | 0.0000 | 0.0100 | 1.289 | 0.4422 | 0.120 | 0.230 | 11.1 | 0.790 | n/a | n/a | n/a |
| T3 | n40 | own_margin | 1.8041 | 1.8339 | 0.0299 | 0.2194 | 0.9800 | 0.0100 | 0.0100 | 1.183 | 0.5011 | 0.170 | 0.270 | 10.4 | 0.925 | n/a | n/a | n/a |
| T3 | n40 | kappa | 0.8708 | 0.8703 | -0.0005 | 0.0235 | 0.9200 | 0.0500 | 0.0300 | 0.866 | 0.0460 | 0.120 | 0.080 | 13.2 | 1.046 | n/a | 6.5 | n/a |
| T3 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4265 | -0.0084 | 0.0593 | 0.9000 | 0.0600 | 0.0400 | 0.903 | 0.1446 | 0.170 | 0.680 | 6.4 | 1.197 | n/a | n/a | n/a |
| T3 | n40 | carried_added | 1.4256 | 1.4602 | 0.0345 | 0.2137 | 0.9800 | 0.0000 | 0.0200 | 1.285 | 0.4828 | 0.120 | 0.130 | 12.5 | 0.783 | n/a | n/a | n/a |
| T3 | n40 | pooled_retention | 0.7170 | 0.7309 | 0.0138 | 0.0911 | 0.9000 | 0.0100 | 0.0900 | 0.964 | 0.1904 | 0.640 | 0.000 | 15.1 | 1.108 | n/a | 8.0 | n/a |
| T3 | n80 | large | 6.8973 | 7.1282 | 0.2309 | 1.2490 | 0.9800 | 0.0100 | 0.0100 | 1.093 | 2.8573 | 0.150 | 0.270 | 10.4 | 0.827 | n/a | n/a | n/a |
| T3 | n80 | carries | 0.7597 | 0.7864 | 0.0267 | 0.1192 | 0.9900 | 0.0000 | 0.0100 | 1.436 | 0.3001 | 0.620 | 0.030 | 13.8 | 0.727 | n/a | 8.2 | n/a |
| T3 | n80 | depends | 0.7552 | 0.7827 | 0.0275 | 0.1209 | 0.9900 | 0.0000 | 0.0100 | 1.445 | 0.3044 | 0.620 | 0.030 | 13.8 | 0.727 | n/a | 8.0 | n/a |
| T3 | n80 | carried_margin | 7.3154 | 7.5548 | 0.2394 | 1.2902 | 0.9800 | 0.0100 | 0.0100 | 1.079 | 2.9244 | 0.130 | 0.280 | 10.2 | 0.839 | n/a | n/a | n/a |
| T3 | n80 | own_margin | 9.6872 | 9.7178 | 0.0307 | 1.3095 | 0.9200 | 0.0300 | 0.0500 | 1.067 | 3.5698 | 0.140 | 0.630 | 6.6 | 1.309 | n/a | n/a | n/a |
| T3 | n80 | kappa | 0.9754 | 0.9754 | -0.0000 | 0.0049 | 0.9600 | 0.0400 | 0.0000 | 0.895 | 0.0095 | 0.120 | 0.180 | 11.2 | 0.966 | n/a | 5.9 | n/a |
| T3 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4266 | -0.0085 | 0.0594 | 0.9000 | 0.0600 | 0.0400 | 0.899 | 0.1443 | 0.160 | 0.660 | 6.4 | 1.210 | n/a | n/a | n/a |
| T3 | n80 | carried_added | 7.4996 | 7.7436 | 0.2440 | 1.3121 | 0.9800 | 0.0100 | 0.0100 | 1.081 | 2.9777 | 0.130 | 0.270 | 10.4 | 0.838 | n/a | n/a | n/a |
| T3 | n80 | pooled_retention | 0.7597 | 0.7691 | 0.0094 | 0.0824 | 0.9000 | 0.0000 | 0.1000 | 1.047 | 0.1827 | 0.750 | 0.000 | 15.1 | 1.451 | n/a | 8.5 | n/a |
| T3 | n160 | large | 16.1075 | 16.4567 | 0.3493 | 2.1401 | 0.9400 | 0.0200 | 0.0400 | 1.061 | 4.6727 | 0.470 | 0.010 | 15.0 | 1.022 | n/a | n/a | n/a |
| T3 | n160 | carries | 0.7709 | 0.7890 | 0.0181 | 0.1274 | 0.9300 | 0.0000 | 0.0700 | 1.196 | 0.2866 | 0.580 | 0.010 | 14.9 | 1.195 | n/a | 15.5 | n/a |
| T3 | n160 | depends | 0.7690 | 0.7874 | 0.0184 | 0.1282 | 0.9300 | 0.0000 | 0.0700 | 1.200 | 0.2886 | 0.580 | 0.010 | 14.9 | 1.195 | n/a | 15.2 | n/a |
| T3 | n160 | carried_margin | 16.5256 | 16.8833 | 0.3577 | 2.1571 | 0.9400 | 0.0200 | 0.0400 | 1.061 | 4.7066 | 0.460 | 0.010 | 15.0 | 1.026 | n/a | n/a | n/a |
| T3 | n160 | own_margin | 21.4901 | 21.5858 | 0.0957 | 1.3055 | 0.9800 | 0.0200 | 0.0000 | 1.289 | 3.1521 | 0.420 | 0.190 | 11.1 | 0.784 | n/a | n/a | n/a |
| T3 | n160 | kappa | 0.9890 | 0.9890 | 0.0000 | 0.0016 | 0.9400 | 0.0500 | 0.0100 | 1.035 | 0.0032 | 0.460 | 0.000 | 15.2 | 1.014 | n/a | 7.7 | n/a |
| T3 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4265 | -0.0084 | 0.0593 | 0.9100 | 0.0500 | 0.0400 | 0.903 | 0.1438 | 0.160 | 0.680 | 6.4 | 1.216 | n/a | n/a | n/a |
| T3 | n160 | carried_added | 16.7098 | 17.0721 | 0.3624 | 2.1896 | 0.9400 | 0.0200 | 0.0400 | 1.060 | 4.7705 | 0.460 | 0.010 | 15.0 | 1.020 | n/a | n/a | n/a |
| T3 | n160 | pooled_retention | 0.7709 | 0.7798 | 0.0088 | 0.0809 | 0.8800 | 0.0000 | 0.1200 | 1.062 | 0.1766 | 0.550 | 0.000 | 15.1 | 1.621 | n/a | 16.1 | n/a |
| T3 | n320 | large | 18.8086 | 19.1389 | 0.3303 | 2.4711 | 0.9300 | 0.0200 | 0.0500 | 1.032 | 5.3278 | 0.550 | 0.000 | 15.0 | 1.009 | n/a | n/a | n/a |
| T3 | n320 | carries | 0.7708 | 0.7886 | 0.0178 | 0.1286 | 0.9200 | 0.0000 | 0.0800 | 1.143 | 0.2806 | 0.590 | 0.000 | 15.1 | 1.120 | n/a | 16.7 | n/a |
| T3 | n320 | depends | 0.7691 | 0.7872 | 0.0181 | 0.1292 | 0.9200 | 0.0000 | 0.0800 | 1.146 | 0.2818 | 0.590 | 0.000 | 15.1 | 1.119 | n/a | 16.2 | n/a |
| T3 | n320 | carried_margin | 19.2267 | 19.5653 | 0.3386 | 2.4849 | 0.9300 | 0.0200 | 0.0500 | 1.033 | 5.3651 | 0.560 | 0.000 | 15.0 | 1.006 | n/a | n/a | n/a |
| T3 | n320 | own_margin | 24.9973 | 25.0212 | 0.0238 | 1.3890 | 0.9800 | 0.0200 | 0.0000 | 1.362 | 3.3595 | 0.540 | 0.160 | 11.7 | 0.761 | n/a | n/a | n/a |
| T3 | n320 | kappa | 0.9905 | 0.9905 | -0.0000 | 0.0013 | 0.9300 | 0.0700 | 0.0000 | 1.055 | 0.0028 | 0.570 | 0.000 | 15.1 | 1.184 | n/a | 7.9 | n/a |
| T3 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4264 | -0.0083 | 0.0594 | 0.9000 | 0.0600 | 0.0400 | 0.902 | 0.1447 | 0.170 | 0.670 | 6.3 | 1.204 | n/a | n/a | n/a |
| T3 | n320 | carried_added | 19.4109 | 19.7543 | 0.3434 | 2.5179 | 0.9400 | 0.0100 | 0.0500 | 1.032 | 5.4302 | 0.560 | 0.000 | 15.0 | 1.012 | n/a | n/a | n/a |
| T3 | n320 | pooled_retention | 0.7708 | 0.7789 | 0.0081 | 0.0811 | 0.8800 | 0.0000 | 0.1200 | 1.046 | 0.1780 | 0.550 | 0.000 | 15.1 | 1.591 | n/a | 16.7 | n/a |
| T3 | h2 | large | 0.8269 | 0.8343 | 0.0074 | 0.1249 | 0.9500 | 0.0000 | 0.0500 | 0.904 | 0.2432 | 0.170 | 0.030 | 15.1 | 0.988 | n/a | n/a | 1.000 |
| T3 | h2 | carries | 0.7470 | 0.7563 | 0.0094 | 0.0801 | 0.9000 | 0.0000 | 0.1000 | 0.986 | 0.1694 | 0.620 | 0.000 | 15.1 | 1.325 | n/a | 118.9 | 1.000 |
| T3 | h2 | depends | 0.7200 | 0.7314 | 0.0114 | 0.0837 | 0.9000 | 0.0000 | 0.1000 | 1.013 | 0.1766 | 0.610 | 0.000 | 15.1 | 1.297 | n/a | 51.1 | 1.000 |
| T3 | h2 | carried_margin | 1.2453 | 1.2608 | 0.0155 | 0.1244 | 0.9200 | 0.0000 | 0.0800 | 0.978 | 0.2551 | 0.500 | 0.000 | 15.2 | 1.183 | n/a | n/a | 1.000 |
| T3 | h2 | own_margin | 1.7295 | 1.7270 | -0.0025 | 0.0331 | 0.9200 | 0.0800 | 0.0000 | 1.041 | 0.0716 | 0.540 | 0.000 | 15.0 | 1.087 | n/a | n/a | 1.000 |
| T3 | h2 | kappa | 0.8711 | 0.8709 | -0.0002 | 0.0163 | 0.9200 | 0.0800 | 0.0000 | 0.939 | 0.0340 | 0.550 | 0.000 | 15.1 | 1.293 | n/a | 9.1 | 1.000 |
| T3 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4265 | -0.0081 | 0.0594 | 0.9000 | 0.0600 | 0.0400 | 0.901 | 0.1441 | 0.170 | 0.680 | 6.4 | 1.236 | n/a | n/a | 1.000 |
| T3 | h2 | carried_added | 1.4295 | 1.4497 | 0.0203 | 0.1605 | 0.9000 | 0.0000 | 0.1000 | 1.000 | 0.3447 | 0.490 | 0.000 | 15.1 | 1.417 | n/a | n/a | 1.000 |
| T3 | h2 | pooled_retention | 0.7470 | 0.7574 | 0.0104 | 0.0861 | 0.9000 | 0.0000 | 0.1000 | 0.979 | 0.1798 | 0.640 | 0.000 | 15.0 | 1.410 | n/a | 114.1 | 1.000 |
| T3 | h5 | large | 3.2326 | 3.2739 | 0.0414 | 0.3917 | 0.9200 | 0.0000 | 0.0800 | 0.996 | 0.8414 | 0.380 | 0.000 | 15.4 | 1.180 | n/a | n/a | 1.000 |
| T3 | h5 | carries | 0.7489 | 0.7598 | 0.0109 | 0.0871 | 0.8900 | 0.0000 | 0.1100 | 1.023 | 0.1879 | 0.570 | 0.000 | 15.1 | 1.328 | n/a | 147.2 | 1.000 |
| T3 | h5 | depends | 0.7395 | 0.7513 | 0.0118 | 0.0887 | 0.8900 | 0.0000 | 0.1100 | 1.034 | 0.1911 | 0.570 | 0.000 | 15.1 | 1.316 | n/a | 75.7 | 1.000 |
| T3 | h5 | carried_margin | 3.6509 | 3.7006 | 0.0497 | 0.4003 | 0.9100 | 0.0000 | 0.0900 | 1.017 | 0.8596 | 0.510 | 0.000 | 15.1 | 1.203 | n/a | n/a | 1.000 |
| T3 | h5 | own_margin | 4.9368 | 4.9315 | -0.0053 | 0.0636 | 0.9400 | 0.0500 | 0.0100 | 1.084 | 0.1415 | 0.560 | 0.030 | 13.3 | 1.143 | n/a | n/a | 1.000 |
| T3 | h5 | kappa | 0.9520 | 0.9519 | -0.0001 | 0.0063 | 0.9200 | 0.0800 | 0.0000 | 0.919 | 0.0128 | 0.520 | 0.000 | 15.1 | 1.286 | n/a | 8.9 | 1.000 |
| T3 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4267 | -0.0083 | 0.0591 | 0.8900 | 0.0700 | 0.0400 | 0.899 | 0.1427 | 0.200 | 0.650 | 6.4 | 1.204 | n/a | n/a | 1.000 |
| T3 | h5 | carried_added | 3.8351 | 3.8895 | 0.0544 | 0.4358 | 0.9000 | 0.0000 | 0.1000 | 1.024 | 0.9381 | 0.510 | 0.000 | 15.1 | 1.306 | n/a | n/a | 1.000 |
| T3 | h5 | pooled_retention | 0.7489 | 0.7590 | 0.0101 | 0.0844 | 0.8900 | 0.0000 | 0.1100 | 1.017 | 0.1826 | 0.540 | 0.000 | 15.1 | 1.396 | n/a | 142.7 | 1.000 |
| T3 | h10 | large | 7.8013 | 7.4906 | -0.3107 | 0.5037 | 0.8500 | 0.0000 | 0.1500 | 1.764 | 1.4094 | 0.640 | 0.000 | 15.2 | 1.943 | n/a | n/a | 0.174 |
| T3 | h10 | carries | 0.7712 | 0.7389 | -0.0323 | 0.0488 | 0.8400 | 0.0000 | 0.1600 | 1.821 | 0.1379 | 0.550 | 0.000 | 15.2 | 1.884 | n/a | 124.4 | 0.174 |
| T3 | h10 | depends | 0.7672 | 0.7351 | -0.0321 | 0.0490 | 0.8400 | 0.0000 | 0.1600 | 1.829 | 0.1383 | 0.550 | 0.000 | 15.2 | 1.879 | n/a | 106.9 | 0.174 |
| T3 | h10 | carried_margin | 8.2196 | 7.8933 | -0.3264 | 0.5066 | 0.8500 | 0.0000 | 0.1500 | 1.795 | 1.4196 | 0.500 | 0.000 | 15.2 | 1.901 | n/a | n/a | 0.174 |
| T3 | h10 | own_margin | 10.7131 | 10.7398 | 0.0267 | 0.0991 | 0.9600 | 0.0300 | 0.0100 | 1.367 | 0.2275 | 0.520 | 0.270 | 10.2 | 0.821 | n/a | n/a | 0.174 |
| T3 | h10 | kappa | 0.9781 | 0.9802 | 0.0021 | 0.0019 | 0.8400 | 0.1600 | 0.0000 | 1.433 | 0.0050 | 0.510 | 0.000 | 15.2 | 2.254 | n/a | 11.6 | 0.174 |
| T3 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4027 | 0.0156 | 0.0460 | 0.9200 | 0.0800 | 0.0000 | 0.742 | 0.0861 | 0.020 | 0.680 | 7.4 | 1.201 | n/a | n/a | 0.174 |
| T3 | h10 | carried_added | 8.4038 | 8.0539 | -0.3499 | 0.5303 | 0.8500 | 0.0000 | 0.1500 | 1.789 | 1.4843 | 0.500 | 0.000 | 15.2 | 1.944 | n/a | n/a | 0.174 |
| T3 | h10 | pooled_retention | 0.7712 | 0.7392 | -0.0320 | 0.0484 | 0.8500 | 0.0000 | 0.1500 | 1.787 | 0.1366 | 0.580 | 0.000 | 15.1 | 1.990 | n/a | 124.4 | 0.174 |
| T4 | n20 | large | -0.2628 | -0.2736 | -0.0108 | 0.0889 | 0.9400 | 0.0600 | 0.0000 | 1.116 | 0.1419 | 0.230 | 0.320 | 9.6 | 1.128 | n/a | n/a | n/a |
| T4 | n20 | carries | 0.6000 | 0.5889 | -0.0111 | 0.0651 | 0.9300 | 0.0000 | 0.0700 | 1.228 | 0.1510 | 0.620 | 0.060 | 13.1 | 1.193 | n/a | 5.1 | n/a |
| T4 | n20 | depends | 0.4441 | 0.4243 | -0.0199 | 0.0940 | 0.9100 | 0.0000 | 0.0900 | 1.175 | 0.2100 | 0.420 | 0.070 | 12.8 | 1.137 | n/a | 4.0 | n/a |
| T4 | n20 | carried_margin | 0.2100 | 0.2047 | -0.0053 | 0.0876 | 0.9200 | 0.0000 | 0.0800 | 1.061 | 0.1701 | 0.000 | 0.840 | 6.2 | 1.157 | n/a | n/a | n/a |
| T4 | n20 | own_margin | 0.4727 | 0.4783 | 0.0055 | 0.1484 | 0.9500 | 0.0000 | 0.0500 | 1.075 | 0.2969 | 0.000 | 0.970 | 4.0 | 0.909 | n/a | n/a | n/a |
| T4 | n20 | kappa | 0.5327 | 0.5179 | -0.0148 | 0.1100 | 0.9600 | 0.0300 | 0.0100 | 0.993 | 0.2324 | 0.000 | 0.560 | 9.7 | 0.982 | n/a | 4.9 | n/a |
| T4 | n20 | shuffled_vs_yardstick | -0.4727 | -0.4783 | -0.0055 | 0.1484 | 0.9500 | 0.0500 | 0.0000 | 1.075 | 0.2969 | 0.000 | 0.970 | 4.0 | 0.909 | n/a | n/a | n/a |
| T4 | n20 | carried_added | 0.3941 | 0.3871 | -0.0071 | 0.0984 | 0.9300 | 0.0000 | 0.0700 | 0.983 | 0.1794 | 0.000 | 0.660 | 8.7 | 1.601 | n/a | n/a | n/a |
| T4 | n20 | pooled_retention | 0.6000 | 0.5973 | -0.0027 | 0.0691 | 0.8100 | 0.0200 | 0.1700 | 0.712 | 0.1222 | 0.950 | 0.000 | 15.0 | 2.461 | n/a | 5.7 | n/a |
| T4 | n40 | large | 0.7084 | 0.7130 | 0.0046 | 0.2845 | 0.9400 | 0.0000 | 0.0600 | 0.946 | 0.4450 | 0.120 | 0.370 | 9.5 | 1.037 | n/a | n/a | n/a |
| T4 | n40 | carries | 0.6000 | 0.6071 | 0.0071 | 0.0892 | 0.9700 | 0.0000 | 0.0300 | 1.056 | 0.1907 | 0.750 | 0.040 | 14.4 | 0.820 | n/a | 4.7 | n/a |
| T4 | n40 | depends | 0.5648 | 0.5719 | 0.0071 | 0.0930 | 0.9700 | 0.0000 | 0.0300 | 1.092 | 0.2044 | 0.740 | 0.030 | 14.3 | 0.794 | n/a | 4.4 | n/a |
| T4 | n40 | carried_margin | 1.1811 | 1.1913 | 0.0102 | 0.4098 | 0.9500 | 0.0000 | 0.0500 | 0.970 | 0.7290 | 0.010 | 0.800 | 6.9 | 1.014 | n/a | n/a | n/a |
| T4 | n40 | own_margin | 2.0914 | 2.0950 | 0.0037 | 0.6588 | 0.9100 | 0.0000 | 0.0900 | 0.987 | 1.1929 | 0.010 | 0.890 | 5.3 | 1.128 | n/a | n/a | n/a |
| T4 | n40 | kappa | 0.8651 | 0.8611 | -0.0040 | 0.0367 | 0.9600 | 0.0300 | 0.0100 | 0.969 | 0.0758 | 0.010 | 0.680 | 8.5 | 0.959 | n/a | 4.3 | n/a |
| T4 | n40 | shuffled_vs_yardstick | -0.4727 | -0.4783 | -0.0056 | 0.1484 | 0.9500 | 0.0500 | 0.0000 | 1.075 | 0.2965 | 0.000 | 0.970 | 4.0 | 0.910 | n/a | n/a | n/a |
| T4 | n40 | carried_added | 1.3653 | 1.3737 | 0.0083 | 0.4251 | 0.9100 | 0.0000 | 0.0900 | 0.949 | 0.7337 | 0.010 | 0.730 | 7.8 | 1.241 | n/a | n/a | n/a |
| T4 | n40 | pooled_retention | 0.6000 | 0.5977 | -0.0023 | 0.0700 | 0.8100 | 0.0200 | 0.1700 | 0.702 | 0.1227 | 0.960 | 0.000 | 15.0 | 2.783 | n/a | 4.6 | n/a |
| T4 | n80 | large | 5.5237 | 5.5389 | 0.0152 | 1.3122 | 0.9500 | 0.0100 | 0.0400 | 1.182 | 3.4421 | 0.040 | 0.860 | 6.0 | 0.930 | n/a | n/a | n/a |
| T4 | n80 | carries | 0.6000 | 0.6090 | 0.0090 | 0.1117 | 0.9600 | 0.0100 | 0.0300 | 0.859 | 0.2066 | 0.730 | 0.050 | 13.3 | 0.925 | n/a | 4.8 | n/a |
| T4 | n80 | depends | 0.5927 | 0.6022 | 0.0095 | 0.1127 | 0.9600 | 0.0100 | 0.0300 | 0.859 | 0.2070 | 0.730 | 0.050 | 13.3 | 0.912 | n/a | 4.7 | n/a |
| T4 | n80 | carried_margin | 5.9964 | 6.0172 | 0.0208 | 1.4246 | 0.9500 | 0.0100 | 0.0400 | 1.176 | 3.8303 | 0.040 | 0.890 | 5.8 | 0.964 | n/a | n/a | n/a |
| T4 | n80 | own_margin | 10.1169 | 10.0810 | -0.0359 | 2.1352 | 0.9700 | 0.0000 | 0.0300 | 1.266 | 6.1902 | 0.010 | 0.980 | 4.1 | 0.830 | n/a | n/a | n/a |
| T4 | n80 | kappa | 0.9702 | 0.9698 | -0.0004 | 0.0077 | 0.9400 | 0.0400 | 0.0200 | 1.110 | 0.0169 | 0.040 | 0.860 | 6.6 | 1.032 | n/a | 4.2 | n/a |
| T4 | n80 | shuffled_vs_yardstick | -0.4727 | -0.4783 | -0.0056 | 0.1484 | 0.9500 | 0.0500 | 0.0000 | 1.075 | 0.2976 | 0.000 | 0.970 | 4.0 | 0.917 | n/a | n/a | n/a |
| T4 | n80 | carried_added | 6.1806 | 6.1995 | 0.0189 | 1.4479 | 0.9500 | 0.0100 | 0.0400 | 1.160 | 3.8262 | 0.040 | 0.870 | 6.0 | 0.986 | n/a | n/a | n/a |
| T4 | n80 | pooled_retention | 0.6000 | 0.5974 | -0.0026 | 0.0698 | 0.8100 | 0.0200 | 0.1700 | 0.702 | 0.1260 | 0.950 | 0.000 | 15.0 | 2.335 | n/a | 4.6 | n/a |
| T4 | n160 | large | 12.1058 | 12.0443 | -0.0616 | 1.6765 | 0.9200 | 0.0100 | 0.0700 | 0.805 | 3.0920 | 0.370 | 0.050 | 13.3 | 1.158 | n/a | n/a | n/a |
| T4 | n160 | carries | 0.6000 | 0.5985 | -0.0015 | 0.1057 | 0.8800 | 0.0200 | 0.1000 | 0.845 | 0.1954 | 0.650 | 0.010 | 14.5 | 1.416 | n/a | 14.1 | n/a |
| T4 | n160 | depends | 0.5965 | 0.5953 | -0.0012 | 0.1060 | 0.8800 | 0.0200 | 0.1000 | 0.847 | 0.1953 | 0.650 | 0.010 | 14.5 | 1.407 | n/a | 13.7 | n/a |
| T4 | n160 | carried_margin | 12.5785 | 12.5225 | -0.0561 | 1.7312 | 0.9300 | 0.0100 | 0.0600 | 0.803 | 3.1720 | 0.300 | 0.060 | 12.9 | 1.090 | n/a | n/a | n/a |
| T4 | n160 | own_margin | 21.0870 | 21.1955 | 0.1085 | 1.5520 | 0.9600 | 0.0300 | 0.0100 | 1.219 | 3.3717 | 0.340 | 0.360 | 9.5 | 0.857 | n/a | n/a | n/a |
| T4 | n160 | kappa | 0.9856 | 0.9858 | 0.0002 | 0.0022 | 0.8700 | 0.1200 | 0.0100 | 0.778 | 0.0040 | 0.300 | 0.040 | 13.9 | 1.395 | n/a | 8.5 | n/a |
| T4 | n160 | shuffled_vs_yardstick | -0.4727 | -0.4782 | -0.0055 | 0.1484 | 0.9500 | 0.0500 | 0.0000 | 1.076 | 0.2975 | 0.000 | 0.970 | 4.0 | 0.905 | n/a | n/a | n/a |
| T4 | n160 | carried_added | 12.7627 | 12.7049 | -0.0578 | 1.7711 | 0.9300 | 0.0100 | 0.0600 | 0.797 | 3.2294 | 0.300 | 0.060 | 13.0 | 1.090 | n/a | n/a | n/a |
| T4 | n160 | pooled_retention | 0.6000 | 0.5974 | -0.0026 | 0.0696 | 0.8100 | 0.0200 | 0.1700 | 0.701 | 0.1219 | 0.720 | 0.000 | 15.1 | 2.731 | n/a | 14.1 | n/a |
| T4 | n320 | large | 14.3285 | 14.2283 | -0.1002 | 1.8193 | 0.8800 | 0.0100 | 0.1100 | 0.812 | 3.4882 | 0.520 | 0.020 | 14.6 | 1.380 | n/a | n/a | n/a |
| T4 | n320 | carries | 0.6000 | 0.5986 | -0.0014 | 0.1067 | 0.8700 | 0.0100 | 0.1200 | 0.838 | 0.1987 | 0.560 | 0.020 | 14.5 | 1.626 | n/a | 17.4 | n/a |
| T4 | n320 | depends | 0.5970 | 0.5959 | -0.0011 | 0.1069 | 0.8700 | 0.0100 | 0.1200 | 0.840 | 0.1982 | 0.560 | 0.020 | 14.5 | 1.621 | n/a | 16.8 | n/a |
| T4 | n320 | carried_margin | 14.8012 | 14.7066 | -0.0946 | 1.8472 | 0.8800 | 0.0100 | 0.1100 | 0.805 | 3.5328 | 0.560 | 0.020 | 14.6 | 1.384 | n/a | n/a | n/a |
| T4 | n320 | own_margin | 24.7915 | 24.8932 | 0.1017 | 1.4141 | 0.9700 | 0.0200 | 0.0100 | 1.136 | 3.2194 | 0.530 | 0.110 | 12.5 | 0.903 | n/a | n/a | n/a |
| T4 | n320 | kappa | 0.9877 | 0.9879 | 0.0002 | 0.0018 | 0.8500 | 0.1200 | 0.0300 | 0.721 | 0.0033 | 0.550 | 0.000 | 15.0 | 1.697 | n/a | 8.8 | n/a |
| T4 | n320 | shuffled_vs_yardstick | -0.4727 | -0.4782 | -0.0055 | 0.1485 | 0.9500 | 0.0500 | 0.0000 | 1.074 | 0.2978 | 0.000 | 0.970 | 4.0 | 0.901 | n/a | n/a | n/a |
| T4 | n320 | carried_added | 14.9854 | 14.8890 | -0.0964 | 1.8898 | 0.8800 | 0.0100 | 0.1100 | 0.800 | 3.6041 | 0.560 | 0.020 | 14.7 | 1.410 | n/a | n/a | n/a |
| T4 | n320 | pooled_retention | 0.6000 | 0.5980 | -0.0020 | 0.0692 | 0.8100 | 0.0200 | 0.1700 | 0.714 | 0.1229 | 0.660 | 0.000 | 15.1 | 2.682 | n/a | 18.5 | n/a |
| T4 | h2 | large | 0.4942 | 0.4859 | -0.0083 | 0.1501 | 0.9800 | 0.0200 | 0.0000 | 1.039 | 0.2806 | 0.000 | 0.730 | 7.1 | 0.792 | n/a | n/a | 1.000 |
| T4 | h2 | carries | 0.6000 | 0.5971 | -0.0029 | 0.0654 | 0.8200 | 0.0200 | 0.1600 | 0.708 | 0.1146 | 0.550 | 0.000 | 15.1 | 2.371 | n/a | 97.0 | 1.000 |
| T4 | h2 | depends | 0.5575 | 0.5565 | -0.0010 | 0.0626 | 0.8200 | 0.0200 | 0.1600 | 0.717 | 0.1072 | 0.560 | 0.000 | 15.2 | 2.331 | n/a | 51.7 | 1.000 |
| T4 | h2 | carried_margin | 0.9671 | 0.9642 | -0.0029 | 0.0865 | 0.8200 | 0.0200 | 0.1600 | 0.742 | 0.1564 | 0.260 | 0.000 | 15.4 | 2.457 | n/a | n/a | 1.000 |
| T4 | h2 | own_margin | 1.7346 | 1.7367 | 0.0020 | 0.0397 | 0.9100 | 0.0600 | 0.0300 | 0.791 | 0.0723 | 0.190 | 0.050 | 13.8 | 1.071 | n/a | n/a | 1.000 |
| T4 | h2 | kappa | 0.8400 | 0.8434 | 0.0034 | 0.0216 | 0.8000 | 0.1700 | 0.0300 | 0.665 | 0.0389 | 0.310 | 0.000 | 15.2 | 2.183 | n/a | 10.3 | 1.000 |
| T4 | h2 | shuffled_vs_yardstick | -0.4729 | -0.4783 | -0.0054 | 0.1485 | 0.9500 | 0.0500 | 0.0000 | 1.074 | 0.2971 | 0.000 | 0.970 | 4.0 | 0.910 | n/a | n/a | 1.000 |
| T4 | h2 | carried_added | 1.1513 | 1.1465 | -0.0048 | 0.1333 | 0.8100 | 0.0200 | 0.1700 | 0.714 | 0.2375 | 0.280 | 0.000 | 15.3 | 2.885 | n/a | n/a | 1.000 |
| T4 | h2 | pooled_retention | 0.6000 | 0.5977 | -0.0023 | 0.0692 | 0.8100 | 0.0200 | 0.1700 | 0.710 | 0.1234 | 0.590 | 0.000 | 15.0 | 2.789 | n/a | 101.5 | 1.000 |
| T4 | h5 | large | 2.4230 | 2.4084 | -0.0146 | 0.3142 | 0.8500 | 0.0100 | 0.1400 | 0.772 | 0.5529 | 0.070 | 0.090 | 14.8 | 1.576 | n/a | n/a | 1.000 |
| T4 | h5 | carries | 0.6000 | 0.5976 | -0.0024 | 0.0722 | 0.8100 | 0.0200 | 0.1700 | 0.683 | 0.1247 | 0.540 | 0.000 | 15.1 | 2.450 | n/a | 123.1 | 1.000 |
| T4 | h5 | depends | 0.5851 | 0.5834 | -0.0017 | 0.0717 | 0.8100 | 0.0200 | 0.1700 | 0.684 | 0.1226 | 0.540 | 0.000 | 15.1 | 2.450 | n/a | 74.5 | 1.000 |
| T4 | h5 | carried_margin | 2.8959 | 2.8861 | -0.0098 | 0.3144 | 0.8100 | 0.0200 | 0.1700 | 0.692 | 0.5414 | 0.370 | 0.010 | 15.2 | 2.237 | n/a | n/a | 1.000 |
| T4 | h5 | own_margin | 4.9493 | 4.9544 | 0.0051 | 0.0818 | 0.9300 | 0.0500 | 0.0200 | 0.806 | 0.1475 | 0.340 | 0.170 | 11.2 | 1.082 | n/a | n/a | 1.000 |
| T4 | h5 | kappa | 0.9402 | 0.9415 | 0.0013 | 0.0079 | 0.8100 | 0.1700 | 0.0200 | 0.691 | 0.0147 | 0.360 | 0.000 | 15.3 | 2.285 | n/a | 10.4 | 1.000 |
| T4 | h5 | shuffled_vs_yardstick | -0.4729 | -0.4777 | -0.0048 | 0.1470 | 0.9500 | 0.0500 | 0.0000 | 1.175 | 0.3087 | 0.000 | 0.980 | 3.7 | 0.902 | n/a | n/a | 1.000 |
| T4 | h5 | carried_added | 3.0801 | 3.0685 | -0.0116 | 0.3613 | 0.8100 | 0.0200 | 0.1700 | 0.689 | 0.6246 | 0.370 | 0.000 | 15.2 | 2.374 | n/a | n/a | 1.000 |
| T4 | h5 | pooled_retention | 0.6000 | 0.5972 | -0.0028 | 0.0698 | 0.8100 | 0.0200 | 0.1700 | 0.690 | 0.1218 | 0.520 | 0.000 | 15.1 | 2.566 | n/a | 118.3 | 1.000 |
| T4 | h10 | large | 5.9093 | 5.5049 | -0.4044 | 0.3755 | 0.7500 | 0.0000 | 0.2500 | 1.743 | 1.0382 | 0.470 | 0.010 | 15.1 | 2.147 | n/a | n/a | 0.194 |
| T4 | h10 | carries | 0.6000 | 0.5599 | -0.0401 | 0.0362 | 0.7500 | 0.0000 | 0.2500 | 1.870 | 0.1048 | 0.540 | 0.000 | 15.1 | 2.135 | n/a | 80.1 | 0.194 |
| T4 | h10 | depends | 0.5931 | 0.5536 | -0.0395 | 0.0358 | 0.7500 | 0.0000 | 0.2500 | 1.880 | 0.1035 | 0.550 | 0.000 | 15.1 | 2.124 | n/a | 78.1 | 0.194 |
| T4 | h10 | carried_margin | 6.3826 | 5.9781 | -0.4045 | 0.3780 | 0.7500 | 0.0000 | 0.2500 | 1.792 | 1.0694 | 0.340 | 0.000 | 15.3 | 2.152 | n/a | n/a | 0.194 |
| T4 | h10 | own_margin | 10.7607 | 10.7998 | 0.0391 | 0.1530 | 0.9700 | 0.0300 | 0.0000 | 1.116 | 0.4393 | 0.220 | 0.580 | 6.8 | 0.959 | n/a | n/a | 0.194 |
| T4 | h10 | kappa | 0.9720 | 0.9747 | 0.0027 | 0.0024 | 0.7500 | 0.2500 | 0.0000 | 1.559 | 0.0065 | 0.360 | 0.000 | 15.3 | 2.402 | n/a | 11.4 | 0.194 |
| T4 | h10 | shuffled_vs_yardstick | -0.4734 | -0.4732 | 0.0002 | 0.1435 | 0.8600 | 0.1400 | 0.0000 | 0.950 | 0.2385 | 0.000 | 0.920 | 5.1 | 2.149 | n/a | n/a | 0.194 |
| T4 | h10 | carried_added | 6.5668 | 6.1344 | -0.4324 | 0.4018 | 0.7500 | 0.0000 | 0.2500 | 1.791 | 1.1374 | 0.340 | 0.000 | 15.3 | 2.145 | n/a | n/a | 0.194 |
| T4 | h10 | pooled_retention | 0.6000 | 0.5600 | -0.0400 | 0.0356 | 0.7500 | 0.0000 | 0.2500 | 1.852 | 0.1030 | 0.510 | 0.000 | 15.2 | 2.402 | n/a | 80.3 | 0.194 |
| T5 | n20 | large | 0.9339 | 0.8590 | -0.0749 | 0.6245 | 0.7900 | 0.0000 | 0.2100 | 1.199 | 1.2680 | 0.520 | 0.060 | 13.3 | 2.575 | n/a | n/a | n/a |
| T5 | n20 | carries | 2.5505 | 2.4711 | -0.0795 | 1.1044 | 0.7900 | 0.0000 | 0.2100 | 1.179 | 2.1889 | 0.520 | 0.040 | 13.1 | 2.713 | n/a | 8.7 | n/a |
| T5 | n20 | depends | 3.2336 | 3.1138 | -0.1198 | 1.6031 | 0.7900 | 0.0000 | 0.2100 | 1.169 | 3.1000 | 0.520 | 0.040 | 12.9 | 2.525 | n/a | 9.2 | n/a |
| T5 | n20 | carried_margin | 1.3520 | 1.2793 | -0.0727 | 0.6174 | 0.7900 | 0.0000 | 0.2100 | 1.226 | 1.2588 | 0.500 | 0.060 | 13.3 | 2.620 | n/a | n/a | n/a |
| T5 | n20 | own_margin | 0.4181 | 0.4203 | 0.0022 | 0.0531 | 0.9400 | 0.0100 | 0.0500 | 1.091 | 0.1338 | 0.120 | 0.710 | 5.9 | 1.046 | n/a | n/a | n/a |
| T5 | n20 | kappa | 0.8801 | 0.8519 | -0.0282 | 0.0737 | 0.9100 | 0.0500 | 0.0400 | 0.796 | 0.1304 | 0.500 | 0.020 | 13.7 | 1.209 | n/a | 2.4 | n/a |
| T5 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0531 | 0.9400 | 0.0500 | 0.0100 | 1.091 | 0.1338 | 0.120 | 0.710 | 5.9 | 1.046 | n/a | n/a | n/a |
| T5 | n20 | carried_added | 1.5362 | 1.4596 | -0.0766 | 0.6161 | 0.7900 | 0.0000 | 0.2100 | 1.235 | 1.2630 | 0.500 | 0.060 | 13.3 | 2.361 | n/a | n/a | n/a |
| T5 | n20 | pooled_retention | 2.5505 | 2.3832 | -0.1674 | 1.0231 | 0.7900 | 0.0000 | 0.2100 | 1.272 | 2.1173 | 0.500 | 0.060 | 13.3 | 2.541 | n/a | 8.3 | n/a |
| T5 | n40 | large | 1.7407 | 1.7334 | -0.0073 | 0.6128 | 0.8200 | 0.0000 | 0.1800 | 1.346 | 1.3601 | 0.540 | 0.060 | 13.1 | 2.024 | n/a | n/a | n/a |
| T5 | n40 | carries | 1.1784 | 1.1769 | -0.0015 | 0.3368 | 0.8500 | 0.0000 | 0.1500 | 1.304 | 0.6973 | 0.520 | 0.050 | 13.0 | 1.769 | n/a | 8.4 | n/a |
| T5 | n40 | depends | 1.1966 | 1.1952 | -0.0014 | 0.3698 | 0.8500 | 0.0000 | 0.1500 | 1.312 | 0.7549 | 0.510 | 0.060 | 13.0 | 1.824 | n/a | 8.4 | n/a |
| T5 | n40 | carried_margin | 2.1588 | 2.1537 | -0.0051 | 0.6163 | 0.8500 | 0.0000 | 0.1500 | 1.350 | 1.4404 | 0.500 | 0.060 | 12.8 | 1.981 | n/a | n/a | n/a |
| T5 | n40 | own_margin | 1.8041 | 1.8263 | 0.0223 | 0.2452 | 0.9500 | 0.0100 | 0.0400 | 0.977 | 0.4938 | 0.120 | 0.280 | 9.9 | 0.956 | n/a | n/a | n/a |
| T5 | n40 | kappa | 0.9214 | 0.9179 | -0.0035 | 0.0251 | 0.9400 | 0.0300 | 0.0300 | 0.997 | 0.0510 | 0.510 | 0.020 | 13.5 | 1.008 | n/a | 3.6 | n/a |
| T5 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0531 | 0.9400 | 0.0500 | 0.0100 | 1.089 | 0.1327 | 0.130 | 0.710 | 6.0 | 1.066 | n/a | n/a | n/a |
| T5 | n40 | carried_added | 2.3430 | 2.3340 | -0.0090 | 0.6219 | 0.8500 | 0.0000 | 0.1500 | 1.343 | 1.4457 | 0.510 | 0.060 | 12.9 | 1.978 | n/a | n/a | n/a |
| T5 | n40 | pooled_retention | 1.1784 | 1.1564 | -0.0220 | 0.2927 | 0.8100 | 0.0000 | 0.1900 | 1.496 | 0.6879 | 0.550 | 0.020 | 13.1 | 2.216 | n/a | 8.0 | n/a |
| T5 | n80 | large | 6.3296 | 6.3625 | 0.0329 | 0.9570 | 0.9500 | 0.0000 | 0.0500 | 1.256 | 2.2907 | 0.370 | 0.280 | 10.4 | 0.924 | n/a | n/a | n/a |
| T5 | n80 | carries | 0.7022 | 0.7011 | -0.0011 | 0.0977 | 0.9600 | 0.0100 | 0.0300 | 1.574 | 0.2565 | 0.510 | 0.070 | 12.8 | 0.729 | n/a | 8.4 | n/a |
| T5 | n80 | depends | 0.6966 | 0.6958 | -0.0007 | 0.0986 | 0.9600 | 0.0100 | 0.0300 | 1.585 | 0.2589 | 0.510 | 0.070 | 12.8 | 0.736 | n/a | 8.2 | n/a |
| T5 | n80 | carried_margin | 6.7477 | 6.7828 | 0.0351 | 0.9830 | 0.9500 | 0.0000 | 0.0500 | 1.255 | 2.3659 | 0.330 | 0.290 | 10.2 | 0.911 | n/a | n/a | n/a |
| T5 | n80 | own_margin | 9.6872 | 9.8147 | 0.1275 | 1.2260 | 0.9500 | 0.0300 | 0.0200 | 1.199 | 3.5604 | 0.140 | 0.680 | 6.0 | 0.961 | n/a | n/a | n/a |
| T5 | n80 | kappa | 0.9734 | 0.9740 | 0.0006 | 0.0049 | 0.9600 | 0.0300 | 0.0100 | 1.053 | 0.0104 | 0.350 | 0.120 | 11.8 | 0.942 | n/a | 6.6 | n/a |
| T5 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4203 | -0.0022 | 0.0531 | 0.9400 | 0.0500 | 0.0100 | 1.091 | 0.1324 | 0.130 | 0.700 | 6.0 | 1.028 | n/a | n/a | n/a |
| T5 | n80 | carried_added | 6.9319 | 6.9631 | 0.0312 | 1.0038 | 0.9500 | 0.0000 | 0.0500 | 1.243 | 2.4296 | 0.330 | 0.280 | 10.3 | 0.911 | n/a | n/a | n/a |
| T5 | n80 | pooled_retention | 0.7022 | 0.7022 | -0.0001 | 0.0777 | 0.9500 | 0.0000 | 0.0500 | 1.229 | 0.1754 | 0.570 | 0.000 | 13.4 | 0.965 | n/a | 7.8 | n/a |
| T5 | n160 | large | 13.2003 | 12.9592 | -0.2411 | 1.4913 | 0.9200 | 0.0000 | 0.0800 | 1.013 | 3.2650 | 0.470 | 0.010 | 13.9 | 1.281 | n/a | n/a | n/a |
| T5 | n160 | carries | 0.6368 | 0.6271 | -0.0097 | 0.0968 | 0.8900 | 0.0000 | 0.1100 | 1.038 | 0.2032 | 0.580 | 0.030 | 14.2 | 1.329 | n/a | 16.3 | n/a |
| T5 | n160 | depends | 0.6337 | 0.6241 | -0.0096 | 0.0969 | 0.8900 | 0.0000 | 0.1100 | 1.043 | 0.2033 | 0.580 | 0.030 | 14.2 | 1.334 | n/a | 16.0 | n/a |
| T5 | n160 | carried_margin | 13.6184 | 13.3794 | -0.2390 | 1.5030 | 0.9100 | 0.0000 | 0.0900 | 1.018 | 3.2985 | 0.460 | 0.020 | 14.0 | 1.288 | n/a | n/a | n/a |
| T5 | n160 | own_margin | 21.4901 | 21.5976 | 0.1075 | 1.3118 | 0.9600 | 0.0300 | 0.0100 | 1.183 | 2.9353 | 0.550 | 0.130 | 11.9 | 0.868 | n/a | n/a | n/a |
| T5 | n160 | kappa | 0.9867 | 0.9868 | 0.0001 | 0.0019 | 0.9300 | 0.0600 | 0.0100 | 0.941 | 0.0040 | 0.460 | 0.000 | 14.7 | 1.047 | n/a | 8.9 | n/a |
| T5 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4202 | -0.0021 | 0.0531 | 0.9400 | 0.0500 | 0.0100 | 1.092 | 0.1338 | 0.130 | 0.710 | 5.9 | 1.059 | n/a | n/a | n/a |
| T5 | n160 | carried_added | 13.8026 | 13.5598 | -0.2428 | 1.5350 | 0.9100 | 0.0000 | 0.0900 | 1.014 | 3.3639 | 0.460 | 0.020 | 14.0 | 1.311 | n/a | n/a | n/a |
| T5 | n160 | pooled_retention | 0.6368 | 0.6286 | -0.0082 | 0.0640 | 0.9000 | 0.0000 | 0.1000 | 0.859 | 0.1229 | 0.600 | 0.000 | 14.8 | 1.692 | n/a | 15.8 | n/a |
| T5 | n320 | large | 15.2419 | 14.9692 | -0.2727 | 1.6666 | 0.9300 | 0.0000 | 0.0700 | 1.007 | 3.5061 | 0.530 | 0.030 | 14.0 | 1.277 | n/a | n/a | n/a |
| T5 | n320 | carries | 0.6292 | 0.6202 | -0.0090 | 0.0948 | 0.9100 | 0.0000 | 0.0900 | 1.021 | 0.1903 | 0.550 | 0.020 | 14.4 | 1.206 | n/a | 18.2 | n/a |
| T5 | n320 | depends | 0.6265 | 0.6176 | -0.0089 | 0.0949 | 0.9100 | 0.0000 | 0.0900 | 1.025 | 0.1903 | 0.550 | 0.020 | 14.3 | 1.204 | n/a | 17.9 | n/a |
| T5 | n320 | carried_margin | 15.6600 | 15.3896 | -0.2705 | 1.6717 | 0.9300 | 0.0000 | 0.0700 | 1.017 | 3.5365 | 0.500 | 0.030 | 14.1 | 1.286 | n/a | n/a | n/a |
| T5 | n320 | own_margin | 24.9973 | 25.0984 | 0.1011 | 1.3880 | 0.9700 | 0.0300 | 0.0000 | 1.196 | 3.2829 | 0.580 | 0.110 | 12.5 | 0.804 | n/a | n/a | n/a |
| T5 | n320 | kappa | 0.9884 | 0.9885 | 0.0001 | 0.0015 | 0.8900 | 0.1000 | 0.0100 | 1.015 | 0.0033 | 0.520 | 0.000 | 14.8 | 1.300 | n/a | 9.3 | n/a |
| T5 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4204 | -0.0023 | 0.0532 | 0.9400 | 0.0500 | 0.0100 | 1.088 | 0.1340 | 0.130 | 0.720 | 5.9 | 1.033 | n/a | n/a | n/a |
| T5 | n320 | carried_added | 15.8442 | 15.5698 | -0.2745 | 1.7062 | 0.9300 | 0.0000 | 0.0700 | 1.011 | 3.5943 | 0.500 | 0.030 | 14.1 | 1.283 | n/a | n/a | n/a |
| T5 | n320 | pooled_retention | 0.6292 | 0.6232 | -0.0060 | 0.0620 | 0.8900 | 0.0000 | 0.1100 | 0.890 | 0.1202 | 0.560 | 0.000 | 15.0 | 1.453 | n/a | 17.1 | n/a |
| T5 | h2 | large | 1.6970 | 1.6545 | -0.0425 | 0.5567 | 0.8400 | 0.0000 | 0.1600 | 1.370 | 1.2710 | 0.620 | 0.030 | 13.7 | 2.104 | n/a | n/a | 1.000 |
| T5 | h2 | carries | 1.2016 | 1.1781 | -0.0235 | 0.3000 | 0.8500 | 0.0000 | 0.1500 | 1.295 | 0.6535 | 0.640 | 0.010 | 13.8 | 2.018 | n/a | 120.0 | 1.000 |
| T5 | h2 | depends | 1.2231 | 1.1982 | -0.0249 | 0.3330 | 0.8500 | 0.0000 | 0.1500 | 1.293 | 0.7327 | 0.640 | 0.010 | 13.8 | 2.056 | n/a | 57.3 | 1.000 |
| T5 | h2 | carried_margin | 2.1154 | 2.0748 | -0.0406 | 0.5699 | 0.8400 | 0.0000 | 0.1600 | 1.303 | 1.2302 | 0.640 | 0.010 | 13.8 | 2.041 | n/a | n/a | 1.000 |
| T5 | h2 | own_margin | 1.7295 | 1.7332 | 0.0037 | 0.0316 | 0.9500 | 0.0500 | 0.0000 | 1.014 | 0.0657 | 0.450 | 0.030 | 14.8 | 0.990 | n/a | n/a | 1.000 |
| T5 | h2 | kappa | 0.9199 | 0.9160 | -0.0039 | 0.0250 | 0.9300 | 0.0200 | 0.0500 | 0.972 | 0.0515 | 0.630 | 0.000 | 14.2 | 1.279 | n/a | 3.7 | 1.000 |
| T5 | h2 | shuffled_vs_yardstick | -0.4183 | -0.4203 | -0.0019 | 0.0532 | 0.9500 | 0.0400 | 0.0100 | 1.088 | 0.1337 | 0.120 | 0.700 | 6.0 | 1.006 | n/a | n/a | 1.000 |
| T5 | h2 | carried_added | 2.2996 | 2.2551 | -0.0444 | 0.5774 | 0.8500 | 0.0000 | 0.1500 | 1.288 | 1.2426 | 0.640 | 0.010 | 13.8 | 2.017 | n/a | n/a | 1.000 |
| T5 | h2 | pooled_retention | 1.2016 | 1.1767 | -0.0250 | 0.3021 | 0.8500 | 0.0000 | 0.1500 | 1.282 | 0.6509 | 0.640 | 0.010 | 13.9 | 2.000 | n/a | 112.8 | 1.000 |
| T5 | h5 | large | 3.5641 | 3.4457 | -0.1183 | 0.5393 | 0.8700 | 0.0000 | 0.1300 | 1.518 | 1.2777 | 0.610 | 0.040 | 13.6 | 1.587 | n/a | n/a | 1.000 |
| T5 | h5 | carries | 0.8136 | 0.7896 | -0.0240 | 0.1098 | 0.8800 | 0.0000 | 0.1200 | 1.483 | 0.2651 | 0.620 | 0.040 | 13.9 | 1.584 | n/a | 140.1 | 1.000 |
| T5 | h5 | depends | 0.8067 | 0.7824 | -0.0243 | 0.1129 | 0.8800 | 0.0000 | 0.1200 | 1.494 | 0.2729 | 0.620 | 0.040 | 13.8 | 1.585 | n/a | 78.4 | 1.000 |
| T5 | h5 | carried_margin | 3.9824 | 3.8660 | -0.1164 | 0.5444 | 0.8800 | 0.0000 | 0.1200 | 1.503 | 1.3068 | 0.620 | 0.040 | 13.7 | 1.559 | n/a | n/a | 1.000 |
| T5 | h5 | own_margin | 4.9368 | 4.9446 | 0.0078 | 0.0608 | 0.9700 | 0.0300 | 0.0000 | 1.081 | 0.1402 | 0.410 | 0.100 | 12.2 | 0.959 | n/a | n/a | 1.000 |
| T5 | h5 | kappa | 0.9558 | 0.9553 | -0.0005 | 0.0083 | 0.9400 | 0.0300 | 0.0300 | 1.044 | 0.0181 | 0.630 | 0.030 | 14.5 | 1.063 | n/a | 6.4 | 1.000 |
| T5 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4202 | -0.0019 | 0.0533 | 0.9400 | 0.0500 | 0.0100 | 1.144 | 0.1302 | 0.160 | 0.640 | 6.2 | 1.096 | n/a | n/a | 1.000 |
| T5 | h5 | carried_added | 4.1666 | 4.0463 | -0.1203 | 0.5618 | 0.8800 | 0.0000 | 0.1200 | 1.475 | 1.3643 | 0.620 | 0.040 | 13.8 | 1.545 | n/a | n/a | 1.000 |
| T5 | h5 | pooled_retention | 0.8136 | 0.7898 | -0.0238 | 0.1107 | 0.8800 | 0.0000 | 0.1200 | 1.452 | 0.2666 | 0.600 | 0.040 | 13.8 | 1.537 | n/a | 147.4 | 1.000 |
| T5 | h10 | large | 6.9265 | 6.6014 | -0.3250 | 0.7917 | 0.8300 | 0.0000 | 0.1700 | 1.097 | 1.5906 | 0.550 | 0.050 | 13.8 | 2.586 | n/a | n/a | 0.195 |
| T5 | h10 | carries | 0.6909 | 0.6574 | -0.0335 | 0.0736 | 0.8100 | 0.0000 | 0.1900 | 1.132 | 0.1528 | 0.540 | 0.040 | 14.0 | 2.607 | n/a | 122.3 | 0.195 |
| T5 | h10 | depends | 0.6856 | 0.6524 | -0.0332 | 0.0742 | 0.8200 | 0.0000 | 0.1800 | 1.130 | 0.1535 | 0.540 | 0.040 | 13.9 | 2.634 | n/a | 107.8 | 0.195 |
| T5 | h10 | carried_margin | 7.3448 | 7.0065 | -0.3383 | 0.7869 | 0.8300 | 0.0000 | 0.1700 | 1.131 | 1.6131 | 0.580 | 0.050 | 13.7 | 2.736 | n/a | n/a | 0.195 |
| T5 | h10 | own_margin | 10.7131 | 10.7413 | 0.0282 | 0.0871 | 0.9700 | 0.0100 | 0.0200 | 1.839 | 0.2167 | 0.510 | 0.310 | 10.2 | 0.819 | n/a | n/a | 0.195 |
| T5 | h10 | kappa | 0.9755 | 0.9780 | 0.0024 | 0.0029 | 0.8500 | 0.1500 | 0.0000 | 1.396 | 0.0071 | 0.550 | 0.000 | 14.5 | 1.421 | n/a | 9.3 | 0.195 |
| T5 | h10 | shuffled_vs_yardstick | -0.4183 | -0.4051 | 0.0132 | 0.0479 | 0.8700 | 0.1100 | 0.0200 | 0.683 | 0.0850 | 0.070 | 0.550 | 8.6 | 1.747 | n/a | n/a | 0.195 |
| T5 | h10 | carried_added | 7.5290 | 7.1640 | -0.3650 | 0.7992 | 0.8400 | 0.0000 | 0.1600 | 1.145 | 1.6607 | 0.580 | 0.050 | 13.8 | 2.689 | n/a | n/a | 0.195 |
| T5 | h10 | pooled_retention | 0.6909 | 0.6572 | -0.0337 | 0.0732 | 0.8200 | 0.0000 | 0.1800 | 1.136 | 0.1543 | 0.520 | 0.040 | 14.0 | 2.711 | n/a | 118.9 | 0.195 |
| T6[0.3] | n20 | large | -0.1807 | -0.1840 | -0.0033 | 0.0521 | 0.9800 | 0.0000 | 0.0200 | 1.161 | 0.1125 | 0.460 | 0.040 | 12.5 | 0.841 | n/a | n/a | n/a |
| T6[0.3] | n20 | carries | 0.7000 | 0.6941 | -0.0059 | 0.0747 | 0.8700 | 0.0000 | 0.1300 | 1.143 | 0.1631 | 0.560 | 0.030 | 13.3 | 1.543 | n/a | 8.7 | n/a |
| T6[0.3] | n20 | depends | 0.6845 | 0.6788 | -0.0057 | 0.0783 | 0.8600 | 0.0000 | 0.1400 | 1.141 | 0.1710 | 0.560 | 0.010 | 13.4 | 1.509 | n/a | 11.1 | n/a |
| T6[0.3] | n20 | carried_margin | 0.3920 | 0.3865 | -0.0054 | 0.0539 | 0.8700 | 0.0000 | 0.1300 | 1.004 | 0.1055 | 0.130 | 0.180 | 11.5 | 1.698 | n/a | n/a | n/a |
| T6[0.3] | n20 | own_margin | 0.5727 | 0.5705 | -0.0022 | 0.0566 | 0.9500 | 0.0000 | 0.0500 | 1.002 | 0.1293 | 0.090 | 0.530 | 7.0 | 0.923 | n/a | n/a | n/a |
| T6[0.3] | n20 | kappa | 0.9297 | 0.9319 | 0.0022 | 0.0524 | 0.9100 | 0.0800 | 0.0100 | 1.025 | 0.1117 | 0.230 | 0.000 | 15.3 | 1.637 | n/a | 6.6 | n/a |
| T6[0.3] | n20 | shuffled_vs_yardstick | -0.5727 | -0.5705 | 0.0022 | 0.0566 | 0.9500 | 0.0500 | 0.0000 | 1.002 | 0.1293 | 0.090 | 0.530 | 7.0 | 0.923 | n/a | n/a | n/a |
| T6[0.3] | n20 | carried_added | 0.4216 | 0.4164 | -0.0052 | 0.0654 | 0.9200 | 0.0000 | 0.0800 | 1.025 | 0.1337 | 0.130 | 0.020 | 14.5 | 1.537 | n/a | n/a | n/a |
| T6[0.3] | n20 | pooled_retention | 0.7000 | 0.7009 | 0.0009 | 0.0711 | 0.9200 | 0.0000 | 0.0800 | 1.008 | 0.1493 | 0.760 | 0.000 | 15.0 | 1.492 | n/a | 8.7 | n/a |
| T6[0.3] | n80 | large | 6.3077 | 6.3564 | 0.0487 | 1.0600 | 0.9500 | 0.0100 | 0.0400 | 1.148 | 2.5005 | 0.090 | 0.400 | 9.0 | 0.905 | n/a | n/a | n/a |
| T6[0.3] | n80 | carries | 0.7000 | 0.7237 | 0.0237 | 0.1294 | 0.9300 | 0.0200 | 0.0500 | 0.910 | 0.2471 | 0.590 | 0.040 | 13.6 | 1.018 | n/a | 7.8 | n/a |
| T6[0.3] | n80 | depends | 0.5806 | 0.6170 | 0.0364 | 0.1702 | 0.9600 | 0.0000 | 0.0400 | 0.960 | 0.3170 | 0.580 | 0.040 | 13.4 | 0.979 | n/a | 5.3 | n/a |
| T6[0.3] | n80 | carried_margin | 4.0996 | 4.1421 | 0.0425 | 0.9525 | 0.9700 | 0.0100 | 0.0200 | 1.206 | 2.4357 | 0.070 | 0.540 | 7.0 | 0.975 | n/a | n/a | n/a |
| T6[0.3] | n80 | own_margin | 7.0610 | 6.9041 | -0.1569 | 1.3717 | 0.9500 | 0.0100 | 0.0400 | 1.033 | 3.6375 | 0.100 | 0.610 | 6.3 | 0.972 | n/a | n/a | n/a |
| T6[0.3] | n80 | kappa | 0.5933 | 0.5893 | -0.0040 | 0.0528 | 0.9600 | 0.0300 | 0.0100 | 1.191 | 0.1498 | 0.070 | 0.670 | 5.9 | 0.725 | n/a | 6.2 | n/a |
| T6[0.3] | n80 | shuffled_vs_yardstick | 2.2081 | 2.2143 | 0.0063 | 0.2592 | 0.9000 | 0.0000 | 0.1000 | 0.961 | 0.5250 | 0.090 | 0.000 | 15.7 | 1.330 | n/a | n/a | n/a |
| T6[0.3] | n80 | carried_added | 6.9100 | 6.9568 | 0.0468 | 1.1183 | 0.9500 | 0.0100 | 0.0400 | 1.138 | 2.5973 | 0.070 | 0.400 | 9.1 | 0.943 | n/a | n/a | n/a |
| T6[0.3] | n80 | pooled_retention | 0.7000 | 0.7006 | 0.0006 | 0.0706 | 0.9100 | 0.0100 | 0.0800 | 0.992 | 0.1483 | 0.870 | 0.000 | 15.0 | 1.547 | n/a | 8.2 | n/a |
| T6[0.5] | n20 | large | -0.1807 | -0.1838 | -0.0031 | 0.0514 | 0.9900 | 0.0000 | 0.0100 | 1.169 | 0.1109 | 0.590 | 0.060 | 13.1 | 0.819 | n/a | n/a | n/a |
| T6[0.5] | n20 | carries | 0.7000 | 0.6943 | -0.0057 | 0.0743 | 0.9200 | 0.0000 | 0.0800 | 1.141 | 0.1568 | 0.600 | 0.010 | 13.6 | 1.390 | n/a | 8.7 | n/a |
| T6[0.5] | n20 | depends | 0.5583 | 0.5467 | -0.0116 | 0.1104 | 0.9100 | 0.0000 | 0.0900 | 1.095 | 0.2355 | 0.540 | 0.030 | 13.5 | 1.284 | n/a | 9.1 | n/a |
| T6[0.5] | n20 | carried_margin | 0.2284 | 0.2217 | -0.0067 | 0.0524 | 0.9100 | 0.0000 | 0.0900 | 1.056 | 0.1038 | 0.110 | 0.300 | 10.3 | 1.253 | n/a | n/a | n/a |
| T6[0.5] | n20 | own_margin | 0.4091 | 0.4054 | -0.0036 | 0.0490 | 0.9400 | 0.0100 | 0.0500 | 1.071 | 0.1289 | 0.160 | 0.690 | 6.2 | 1.002 | n/a | n/a | n/a |
| T6[0.5] | n20 | kappa | 0.5416 | 0.5306 | -0.0111 | 0.0802 | 0.9200 | 0.0600 | 0.0200 | 0.885 | 0.1631 | 0.110 | 0.050 | 14.4 | 1.075 | n/a | 6.5 | n/a |
| T6[0.5] | n20 | shuffled_vs_yardstick | -0.4091 | -0.4054 | 0.0036 | 0.0490 | 0.9400 | 0.0500 | 0.0100 | 1.071 | 0.1289 | 0.160 | 0.690 | 6.2 | 1.002 | n/a | n/a | n/a |
| T6[0.5] | n20 | carried_added | 0.4216 | 0.4169 | -0.0047 | 0.0663 | 0.9400 | 0.0000 | 0.0600 | 1.059 | 0.1334 | 0.110 | 0.070 | 13.9 | 1.057 | n/a | n/a | n/a |
| T6[0.5] | n20 | pooled_retention | 0.7000 | 0.7037 | 0.0037 | 0.0742 | 0.8500 | 0.0100 | 0.1400 | 0.938 | 0.1550 | 0.750 | 0.000 | 15.0 | 2.142 | n/a | 8.7 | n/a |
| T6[0.5] | n80 | large | 6.3077 | 6.3480 | 0.0404 | 1.0138 | 0.9900 | 0.0000 | 0.0100 | 1.241 | 2.4747 | 0.120 | 0.310 | 8.8 | 0.842 | n/a | n/a | n/a |
| T6[0.5] | n80 | carries | 0.7000 | 0.7108 | 0.0108 | 0.1096 | 0.9300 | 0.0100 | 0.0600 | 1.234 | 0.2481 | 0.620 | 0.070 | 13.5 | 1.029 | n/a | 7.5 | n/a |
| T6[0.5] | n80 | depends | 0.4128 | 0.4251 | 0.0123 | 0.1870 | 0.9500 | 0.0000 | 0.0500 | 1.594 | 0.3859 | 0.480 | 0.140 | 11.7 | 0.907 | n/a | 3.3 | n/a |
| T6[0.5] | n80 | carried_margin | 2.0822 | 2.0968 | 0.0146 | 0.8875 | 0.9700 | 0.0200 | 0.0100 | 1.220 | 2.5584 | 0.100 | 0.640 | 6.0 | 0.827 | n/a | n/a | n/a |
| T6[0.5] | n80 | own_margin | 5.0436 | 5.0146 | -0.0290 | 1.5763 | 0.9500 | 0.0100 | 0.0400 | 0.937 | 3.5632 | 0.110 | 0.490 | 7.7 | 0.998 | n/a | n/a | n/a |
| T6[0.5] | n80 | kappa | 0.3013 | 0.2918 | -0.0095 | 0.0924 | 0.9500 | 0.0400 | 0.0100 | 1.157 | 0.2755 | 0.110 | 0.660 | 5.8 | 0.969 | n/a | 6.3 | n/a |
| T6[0.5] | n80 | shuffled_vs_yardstick | 4.2255 | 4.2512 | 0.0257 | 0.4826 | 0.8500 | 0.0100 | 0.1400 | 0.911 | 0.9923 | 0.150 | 0.000 | 15.4 | 2.228 | n/a | n/a | n/a |
| T6[0.5] | n80 | carried_added | 6.9100 | 6.9487 | 0.0388 | 1.0694 | 1.0000 | 0.0000 | 0.0000 | 1.232 | 2.5870 | 0.100 | 0.310 | 8.9 | 0.876 | n/a | n/a | n/a |
| T6[0.5] | n80 | pooled_retention | 0.7000 | 0.7024 | 0.0024 | 0.0741 | 0.8500 | 0.0100 | 0.1400 | 0.931 | 0.1565 | 0.850 | 0.000 | 15.1 | 2.149 | n/a | 8.0 | n/a |
| T6[0.7] | n20 | large | -0.1807 | -0.1857 | -0.0050 | 0.0527 | 0.9900 | 0.0000 | 0.0100 | 1.324 | 0.1185 | 0.500 | 0.050 | 12.9 | 0.851 | n/a | n/a | n/a |
| T6[0.7] | n20 | carries | 0.7000 | 0.6973 | -0.0027 | 0.0721 | 0.8900 | 0.0000 | 0.1100 | 1.301 | 0.1675 | 0.580 | 0.020 | 13.8 | 1.391 | n/a | 8.3 | n/a |
| T6[0.7] | n20 | depends | 0.2638 | 0.2303 | -0.0335 | 0.2189 | 0.9400 | 0.0000 | 0.0600 | 1.091 | 0.4426 | 0.300 | 0.040 | 13.3 | 1.011 | n/a | 5.2 | n/a |
| T6[0.7] | n20 | carried_margin | 0.0647 | 0.0611 | -0.0036 | 0.0551 | 0.9100 | 0.0000 | 0.0900 | 1.052 | 0.1060 | 0.130 | 0.110 | 12.7 | 1.203 | n/a | n/a | n/a |
| T6[0.7] | n20 | own_margin | 0.2454 | 0.2469 | 0.0014 | 0.0547 | 0.9700 | 0.0100 | 0.0200 | 0.923 | 0.1338 | 0.090 | 0.680 | 5.7 | 0.894 | n/a | n/a | n/a |
| T6[0.7] | n20 | kappa | 0.1536 | 0.1336 | -0.0199 | 0.1157 | 0.9200 | 0.0100 | 0.0700 | 0.927 | 0.2309 | 0.130 | 0.070 | 13.1 | 1.067 | n/a | 6.7 | n/a |
| T6[0.7] | n20 | shuffled_vs_yardstick | -0.2454 | -0.2469 | -0.0014 | 0.0547 | 0.9700 | 0.0200 | 0.0100 | 0.923 | 0.1338 | 0.090 | 0.680 | 5.7 | 0.894 | n/a | n/a | n/a |
| T6[0.7] | n20 | carried_added | 0.4216 | 0.4263 | 0.0047 | 0.0706 | 0.9200 | 0.0100 | 0.0700 | 0.959 | 0.1322 | 0.130 | 0.020 | 14.7 | 1.160 | n/a | n/a | n/a |
| T6[0.7] | n20 | pooled_retention | 0.7000 | 0.7101 | 0.0101 | 0.0659 | 0.9500 | 0.0100 | 0.0400 | 1.212 | 0.1517 | 0.750 | 0.000 | 15.0 | 0.985 | n/a | 9.3 | n/a |
| T6[0.7] | n80 | large | 6.3077 | 6.3283 | 0.0206 | 1.1225 | 0.9100 | 0.0100 | 0.0800 | 0.940 | 2.3772 | 0.210 | 0.250 | 10.4 | 1.071 | n/a | n/a | n/a |
| T6[0.7] | n80 | carries | 0.7000 | 0.7114 | 0.0114 | 0.1121 | 0.9500 | 0.0000 | 0.0500 | 1.197 | 0.2481 | 0.510 | 0.010 | 13.7 | 0.898 | n/a | 7.7 | n/a |
| T6[0.7] | n80 | depends | 0.0214 | -34.0302 | -34.0516 | 337.6033 | 1.0000 | 0.0000 | 0.0000 | 21355476.636 | 0.8774 | 0.190 | 0.430 | 8.2 | 0.789 | n/a | 1.8 | n/a |
| T6[0.7] | n80 | carried_margin | 0.0647 | -0.0051 | -0.0698 | 0.9582 | 0.8900 | 0.0400 | 0.0700 | 0.897 | 2.1753 | 0.160 | 0.510 | 7.1 | 1.316 | n/a | n/a | n/a |
| T6[0.7] | n80 | own_margin | 3.0262 | 2.8790 | -0.1472 | 1.5209 | 0.9200 | 0.0300 | 0.0500 | 1.082 | 3.5347 | 0.180 | 0.390 | 9.1 | 1.107 | n/a | n/a | n/a |
| T6[0.7] | n80 | kappa | 0.0094 | -0.0216 | -0.0310 | 0.1491 | 0.8700 | 0.0700 | 0.0600 | 0.821 | 0.3257 | 0.160 | 0.520 | 7.0 | 1.271 | n/a | 6.6 | n/a |
| T6[0.7] | n80 | shuffled_vs_yardstick | 6.2429 | 6.3334 | 0.0905 | 0.5965 | 0.9500 | 0.0100 | 0.0400 | 1.250 | 1.4338 | 0.170 | 0.000 | 15.1 | 0.982 | n/a | n/a | n/a |
| T6[0.7] | n80 | carried_added | 6.9100 | 6.9403 | 0.0304 | 1.1915 | 0.9100 | 0.0200 | 0.0700 | 0.929 | 2.4989 | 0.160 | 0.240 | 10.4 | 1.057 | n/a | n/a | n/a |
| T6[0.7] | n80 | pooled_retention | 0.7000 | 0.7096 | 0.0096 | 0.0654 | 0.9500 | 0.0100 | 0.0400 | 1.237 | 0.1551 | 0.790 | 0.000 | 15.0 | 0.949 | n/a | 8.7 | n/a |
| T6[0.85] | n20 | large | -0.1807 | -0.1805 | 0.0002 | 0.0479 | 0.9800 | 0.0000 | 0.0200 | 1.336 | 0.1138 | 0.500 | 0.060 | 12.6 | 0.794 | n/a | n/a | n/a |
| T6[0.85] | n20 | carries | 0.7000 | 0.6940 | -0.0060 | 0.0702 | 0.9000 | 0.0000 | 0.1000 | 1.258 | 0.1661 | 0.610 | 0.050 | 13.8 | 1.153 | n/a | 8.8 | n/a |
| T6[0.85] | n20 | depends | -0.4724 | -0.6154 | -0.1430 | 1.8968 | 0.9700 | 0.0300 | 0.0000 | 10.148 | 1.3489 | 0.110 | 0.260 | 10.5 | 0.846 | n/a | 2.5 | n/a |
| T6[0.85] | n20 | carried_margin | -0.0580 | -0.0621 | -0.0042 | 0.0600 | 0.9300 | 0.0000 | 0.0700 | 0.899 | 0.1143 | 0.150 | 0.030 | 13.7 | 1.086 | n/a | n/a | n/a |
| T6[0.85] | n20 | own_margin | 0.1227 | 0.1184 | -0.0043 | 0.0544 | 0.9400 | 0.0400 | 0.0200 | 0.856 | 0.1294 | 0.080 | 0.620 | 6.3 | 1.011 | n/a | n/a | n/a |
| T6[0.85] | n20 | kappa | -0.1375 | -0.1657 | -0.0282 | 0.1605 | 0.8900 | 0.0100 | 0.1000 | 0.741 | 0.2956 | 0.150 | 0.090 | 12.4 | 1.369 | n/a | 6.8 | n/a |
| T6[0.85] | n20 | shuffled_vs_yardstick | -0.1227 | -0.1184 | 0.0043 | 0.0544 | 0.9400 | 0.0200 | 0.0400 | 0.856 | 0.1294 | 0.080 | 0.620 | 6.3 | 1.011 | n/a | n/a | n/a |
| T6[0.85] | n20 | carried_added | 0.4216 | 0.4098 | -0.0118 | 0.0665 | 0.8600 | 0.0000 | 0.1400 | 0.923 | 0.1236 | 0.150 | 0.010 | 14.5 | 1.215 | n/a | n/a | n/a |
| T6[0.85] | n20 | pooled_retention | 0.7000 | 0.6920 | -0.0080 | 0.0667 | 0.8900 | 0.0000 | 0.1100 | 1.060 | 0.1391 | 0.780 | 0.000 | 15.0 | 2.098 | n/a | 9.0 | n/a |
| T6[0.85] | n80 | large | 6.3077 | 6.2097 | -0.0980 | 1.1126 | 0.9100 | 0.0100 | 0.0800 | 0.994 | 2.4013 | 0.190 | 0.380 | 9.1 | 1.218 | n/a | n/a | n/a |
| T6[0.85] | n80 | carries | 0.7000 | 0.6977 | -0.0023 | 0.1073 | 0.9700 | 0.0000 | 0.0300 | 1.144 | 0.2283 | 0.700 | 0.050 | 13.9 | 0.915 | n/a | 8.6 | n/a |
| T6[0.85] | n80 | depends | -0.9572 | -0.7709 | 0.1863 | 5.1740 | 0.8600 | 0.1400 | 0.0000 | 159.668 | 2.8233 | 0.200 | 0.460 | 8.5 | 2.056 | n/a | 0.8 | n/a |
| T6[0.85] | n80 | carried_margin | -1.4483 | -1.4590 | -0.0107 | 0.9441 | 0.9300 | 0.0300 | 0.0400 | 1.065 | 2.4671 | 0.170 | 0.590 | 6.9 | 1.198 | n/a | n/a | n/a |
| T6[0.85] | n80 | own_margin | 1.5131 | 1.5599 | 0.0468 | 1.7437 | 0.9400 | 0.0200 | 0.0400 | 0.870 | 3.4967 | 0.180 | 0.290 | 9.9 | 1.014 | n/a | n/a | n/a |
| T6[0.85] | n80 | kappa | -0.2096 | -0.2401 | -0.0305 | 0.1851 | 0.9100 | 0.0600 | 0.0300 | 0.932 | 0.4564 | 0.170 | 0.650 | 6.6 | 1.046 | n/a | 6.2 | n/a |
| T6[0.85] | n80 | shuffled_vs_yardstick | 7.7560 | 7.6687 | -0.0873 | 0.7651 | 0.9000 | 0.0000 | 0.1000 | 1.039 | 1.5294 | 0.140 | 0.000 | 15.1 | 1.934 | n/a | n/a | n/a |
| T6[0.85] | n80 | carried_added | 6.9100 | 6.8000 | -0.1100 | 1.1749 | 0.9000 | 0.0200 | 0.0800 | 0.985 | 2.5484 | 0.170 | 0.400 | 9.2 | 1.254 | n/a | n/a | n/a |
| T6[0.85] | n80 | pooled_retention | 0.7000 | 0.6918 | -0.0082 | 0.0658 | 0.9000 | 0.0000 | 0.1000 | 1.076 | 0.1351 | 0.790 | 0.000 | 15.0 | 1.961 | n/a | 7.8 | n/a |
| T6[0.95] | n20 | large | -0.1807 | -0.1683 | 0.0124 | 0.0504 | 0.9900 | 0.0000 | 0.0100 | 1.271 | 0.1114 | 0.530 | 0.050 | 12.7 | 0.860 | n/a | n/a | n/a |
| T6[0.95] | n20 | carries | 0.7000 | 0.7091 | 0.0091 | 0.0802 | 0.9300 | 0.0100 | 0.0600 | 1.167 | 0.1784 | 0.550 | 0.020 | 13.3 | 1.101 | n/a | 9.4 | n/a |
| T6[0.95] | n20 | depends | -3.4173 | -3.6123 | -0.1950 | 13.8058 | 0.6600 | 0.3400 | 0.0000 | 227.240 | 7.8649 | 0.120 | 0.390 | 9.2 | 2.727 | n/a | 0.9 | n/a |
| T6[0.95] | n20 | carried_margin | -0.1398 | -0.1334 | 0.0064 | 0.0739 | 0.9300 | 0.0200 | 0.0500 | 0.771 | 0.1345 | 0.090 | 0.050 | 13.8 | 1.099 | n/a | n/a | n/a |
| T6[0.95] | n20 | own_margin | 0.0409 | 0.0349 | -0.0060 | 0.0608 | 0.9200 | 0.0500 | 0.0300 | 0.721 | 0.1129 | 0.100 | 0.530 | 7.7 | 1.081 | n/a | n/a | n/a |
| T6[0.95] | n20 | kappa | -0.3315 | -0.3429 | -0.0113 | 0.2020 | 0.8600 | 0.0200 | 0.1200 | 0.685 | 0.3595 | 0.090 | 0.120 | 12.1 | 1.378 | n/a | 6.4 | n/a |
| T6[0.95] | n20 | shuffled_vs_yardstick | -0.0409 | -0.0349 | 0.0060 | 0.0608 | 0.9200 | 0.0300 | 0.0500 | 0.721 | 0.1129 | 0.100 | 0.530 | 7.7 | 1.081 | n/a | n/a | n/a |
| T6[0.95] | n20 | carried_added | 0.4216 | 0.4116 | -0.0100 | 0.0746 | 0.8700 | 0.0100 | 0.1200 | 0.811 | 0.1331 | 0.090 | 0.030 | 14.2 | 1.526 | n/a | n/a | n/a |
| T6[0.95] | n20 | pooled_retention | 0.7000 | 0.6860 | -0.0140 | 0.0753 | 0.7800 | 0.0000 | 0.2200 | 0.760 | 0.1392 | 0.800 | 0.000 | 15.0 | 2.814 | n/a | 8.1 | n/a |
| T6[0.95] | n80 | large | 6.3077 | 5.9825 | -0.3252 | 0.9149 | 0.9200 | 0.0000 | 0.0800 | 1.225 | 2.1901 | 0.170 | 0.330 | 9.1 | 1.184 | n/a | n/a | n/a |
| T6[0.95] | n80 | carries | 0.7000 | 0.6774 | -0.0226 | 0.1008 | 0.9700 | 0.0000 | 0.0300 | 1.213 | 0.2318 | 0.570 | 0.040 | 12.9 | 0.912 | n/a | 7.9 | n/a |
| T6[0.95] | n80 | depends | -4.8716 | 2.0659 | 6.9376 | 18.4684 | 0.5200 | 0.4800 | 0.0000 | 2457.758 | 5.3477 | 0.160 | 0.460 | 8.7 | 5.745 | n/a | 0.4 | n/a |
| T6[0.95] | n80 | carried_margin | -2.4571 | -2.6109 | -0.1538 | 1.0251 | 0.9500 | 0.0000 | 0.0500 | 0.800 | 2.1503 | 0.140 | 0.530 | 7.3 | 1.009 | n/a | n/a | n/a |
| T6[0.95] | n80 | own_margin | 0.5044 | 0.5968 | 0.0924 | 1.8189 | 0.9600 | 0.0200 | 0.0200 | 0.854 | 3.8532 | 0.100 | 0.380 | 9.1 | 0.991 | n/a | n/a | n/a |
| T6[0.95] | n80 | kappa | -0.3556 | -0.4187 | -0.0631 | 0.2081 | 0.9500 | 0.0100 | 0.0400 | 0.782 | 0.4959 | 0.140 | 0.610 | 6.4 | 0.947 | n/a | 6.6 | n/a |
| T6[0.95] | n80 | shuffled_vs_yardstick | 8.7647 | 8.5933 | -0.1714 | 0.9749 | 0.7700 | 0.0000 | 0.2300 | 0.750 | 1.7782 | 0.180 | 0.000 | 15.1 | 2.764 | n/a | n/a | n/a |
| T6[0.95] | n80 | carried_added | 6.9100 | 6.5624 | -0.3476 | 0.9676 | 0.9200 | 0.0000 | 0.0800 | 1.206 | 2.2997 | 0.140 | 0.330 | 9.2 | 1.269 | n/a | n/a | n/a |
| T6[0.95] | n80 | pooled_retention | 0.7000 | 0.6853 | -0.0147 | 0.0749 | 0.7800 | 0.0000 | 0.2200 | 0.775 | 0.1400 | 0.830 | 0.000 | 15.1 | 2.840 | n/a | 8.1 | n/a |
| T6[1] | n20 | large | -0.1807 | -0.1777 | 0.0030 | 0.0544 | 0.9700 | 0.0100 | 0.0200 | 1.186 | 0.1200 | 0.570 | 0.050 | 12.8 | 0.868 | n/a | n/a | n/a |
| T6[1] | n20 | carries | 0.7000 | 0.7069 | 0.0069 | 0.0800 | 0.9200 | 0.0000 | 0.0800 | 1.126 | 0.1774 | 0.640 | 0.010 | 13.4 | 1.232 | n/a | 8.5 | n/a |
| T6[1] | n20 | depends | n/a | 4.9439 | n/a | 34.3029 | n/a | n/a | n/a | 1518.294 | 13.2717 | 0.180 | 0.500 | 8.2 | n/a | n/a | 0.3 | n/a |
| T6[1] | n20 | carried_margin | -0.1807 | -0.1711 | 0.0096 | 0.0756 | 0.9300 | 0.0400 | 0.0300 | 0.832 | 0.1398 | 0.120 | 0.040 | 14.2 | 1.010 | n/a | n/a | n/a |
| T6[1] | n20 | own_margin | 0.0000 | 0.0066 | 0.0066 | 0.0571 | 0.9500 | 0.0400 | 0.0100 | 0.953 | 0.1375 | 0.140 | 0.510 | 7.4 | 0.963 | n/a | n/a | n/a |
| T6[1] | n20 | kappa | -0.4286 | -0.4194 | 0.0092 | 0.1977 | 0.8900 | 0.0400 | 0.0700 | 0.793 | 0.3815 | 0.130 | 0.140 | 11.7 | 1.384 | n/a | 6.5 | n/a |
| T6[1] | n20 | shuffled_vs_yardstick | 0.0000 | -0.0066 | -0.0066 | 0.0571 | 0.9500 | 0.0100 | 0.0400 | 0.953 | 0.1375 | 0.140 | 0.510 | 7.4 | 0.963 | n/a | n/a | n/a |
| T6[1] | n20 | carried_added | 0.4216 | 0.4264 | 0.0048 | 0.0646 | 0.9500 | 0.0000 | 0.0500 | 1.183 | 0.1357 | 0.130 | 0.040 | 14.4 | 0.961 | n/a | n/a | n/a |
| T6[1] | n20 | pooled_retention | 0.7000 | 0.6960 | -0.0040 | 0.0656 | 0.8600 | 0.0000 | 0.1400 | 1.142 | 0.1444 | 0.790 | 0.000 | 15.0 | 2.295 | n/a | 8.5 | n/a |
| T6[1] | n80 | large | 6.3077 | 6.2807 | -0.0270 | 1.0363 | 0.9300 | 0.0100 | 0.0600 | 1.171 | 2.4133 | 0.150 | 0.350 | 9.5 | 1.057 | n/a | n/a | n/a |
| T6[1] | n80 | carries | 0.7000 | 0.6988 | -0.0012 | 0.1053 | 0.9600 | 0.0000 | 0.0400 | 1.328 | 0.2501 | 0.600 | 0.030 | 13.2 | 0.913 | n/a | 8.0 | n/a |
| T6[1] | n80 | depends | n/a | 2.9441 | n/a | 65.2789 | n/a | n/a | n/a | 39310.878 | 9.4846 | 0.140 | 0.330 | 10.0 | n/a | n/a | 0.1 | n/a |
| T6[1] | n80 | carried_margin | -2.9614 | -2.9243 | 0.0371 | 1.0124 | 0.9200 | 0.0300 | 0.0500 | 1.000 | 2.3390 | 0.120 | 0.540 | 7.6 | 1.150 | n/a | n/a | n/a |
| T6[1] | n80 | own_margin | 0.0000 | 0.1098 | 0.1098 | 1.6868 | 0.9400 | 0.0400 | 0.0200 | 1.106 | 3.8988 | 0.160 | 0.290 | 10.5 | 1.121 | n/a | n/a | n/a |
| T6[1] | n80 | kappa | -0.4286 | -0.4492 | -0.0206 | 0.1995 | 0.9300 | 0.0400 | 0.0300 | 0.949 | 0.5001 | 0.120 | 0.600 | 6.6 | 1.146 | n/a | 6.3 | n/a |
| T6[1] | n80 | shuffled_vs_yardstick | 9.2691 | 9.2050 | -0.0641 | 0.8977 | 0.8600 | 0.0000 | 0.1400 | 1.100 | 1.9562 | 0.150 | 0.000 | 15.1 | 2.360 | n/a | n/a | n/a |
| T6[1] | n80 | carried_added | 6.9100 | 6.8848 | -0.0252 | 1.0896 | 0.9300 | 0.0100 | 0.0600 | 1.168 | 2.4855 | 0.120 | 0.330 | 9.6 | 1.105 | n/a | n/a | n/a |
| T6[1] | n80 | pooled_retention | 0.7000 | 0.6952 | -0.0048 | 0.0649 | 0.8600 | 0.0000 | 0.1400 | 1.160 | 0.1468 | 0.820 | 0.000 | 15.1 | 2.523 | n/a | 8.2 | n/a |
| T6[1.1] | n20 | large | -0.1807 | -0.1789 | 0.0018 | 0.0623 | 0.9700 | 0.0100 | 0.0200 | 0.890 | 0.1256 | 0.470 | 0.060 | 12.8 | 0.867 | n/a | n/a | n/a |
| T6[1.1] | n20 | carries | 0.7000 | 0.7025 | 0.0025 | 0.0855 | 0.8900 | 0.0100 | 0.1000 | 0.955 | 0.1682 | 0.580 | 0.000 | 13.9 | 1.508 | n/a | 9.0 | n/a |
| T6[1.1] | n20 | depends | 3.2086 | 4.7045 | 1.4959 | 69.3146 | 0.9400 | 0.0000 | 0.0600 | 49544.467 | 4.8646 | 0.260 | 0.400 | 8.7 | 1.049 | n/a | -1.3 | n/a |
| T6[1.1] | n20 | carried_margin | -0.2625 | -0.2491 | 0.0134 | 0.0673 | 0.9800 | 0.0200 | 0.0000 | 1.107 | 0.1458 | 0.080 | 0.020 | 14.3 | 0.882 | n/a | n/a | n/a |
| T6[1.1] | n20 | own_margin | -0.0818 | -0.0702 | 0.0116 | 0.0530 | 0.9900 | 0.0100 | 0.0000 | 1.291 | 0.1332 | 0.110 | 0.430 | 8.6 | 0.794 | n/a | n/a | n/a |
| T6[1.1] | n20 | kappa | -0.6226 | -0.6167 | 0.0059 | 0.1959 | 0.9300 | 0.0300 | 0.0400 | 1.053 | 0.4397 | 0.090 | 0.150 | 11.1 | 1.035 | n/a | 6.5 | n/a |
| T6[1.1] | n20 | shuffled_vs_yardstick | 0.0818 | 0.0702 | -0.0116 | 0.0530 | 0.9900 | 0.0000 | 0.0100 | 1.291 | 0.1332 | 0.110 | 0.430 | 8.6 | 0.794 | n/a | n/a | n/a |
| T6[1.1] | n20 | carried_added | 0.4216 | 0.4178 | -0.0038 | 0.0665 | 0.9200 | 0.0000 | 0.0800 | 1.028 | 0.1383 | 0.090 | 0.030 | 13.8 | 1.192 | n/a | n/a | n/a |
| T6[1.1] | n20 | pooled_retention | 0.7000 | 0.6856 | -0.0144 | 0.0623 | 0.8500 | 0.0000 | 0.1500 | 1.123 | 0.1355 | 0.830 | 0.000 | 15.0 | 2.103 | n/a | 8.4 | n/a |
| T6[1.1] | n80 | large | 6.3077 | 6.1206 | -0.1871 | 1.0542 | 0.9300 | 0.0000 | 0.0700 | 1.043 | 2.3878 | 0.140 | 0.330 | 9.0 | 1.147 | n/a | n/a | n/a |
| T6[1.1] | n80 | carries | 0.7000 | 0.6866 | -0.0134 | 0.1131 | 0.9100 | 0.0000 | 0.0900 | 1.084 | 0.2310 | 0.690 | 0.050 | 13.8 | 1.113 | n/a | 7.4 | n/a |
| T6[1.1] | n80 | depends | 3.9358 | -0.5918 | -4.5277 | 8.9087 | 0.7900 | 0.0000 | 0.2100 | 236.443 | 8.4726 | 0.190 | 0.290 | 10.3 | 2.520 | n/a | -0.4 | n/a |
| T6[1.1] | n80 | carried_margin | -3.9701 | -3.9496 | 0.0205 | 0.9260 | 0.9500 | 0.0100 | 0.0400 | 1.204 | 2.3966 | 0.140 | 0.490 | 7.3 | 0.936 | n/a | n/a | n/a |
| T6[1.1] | n80 | own_margin | -1.0087 | -0.8104 | 0.1983 | 1.7385 | 0.9600 | 0.0100 | 0.0300 | 1.116 | 4.1041 | 0.140 | 0.300 | 10.2 | 0.794 | n/a | n/a | n/a |
| T6[1.1] | n80 | kappa | -0.5746 | -0.6159 | -0.0414 | 0.2129 | 0.9500 | 0.0100 | 0.0400 | 1.069 | 0.5949 | 0.140 | 0.660 | 6.0 | 0.946 | n/a | 6.3 | n/a |
| T6[1.1] | n80 | shuffled_vs_yardstick | 10.2778 | 10.0702 | -0.2076 | 0.9346 | 0.8500 | 0.0000 | 0.1500 | 1.113 | 2.0236 | 0.190 | 0.000 | 15.1 | 2.078 | n/a | n/a | n/a |
| T6[1.1] | n80 | carried_added | 6.9100 | 6.7173 | -0.1926 | 1.1182 | 0.9300 | 0.0000 | 0.0700 | 1.031 | 2.5201 | 0.140 | 0.340 | 8.9 | 1.156 | n/a | n/a | n/a |
| T6[1.1] | n80 | pooled_retention | 0.7000 | 0.6870 | -0.0130 | 0.0631 | 0.8500 | 0.0000 | 0.1500 | 1.114 | 0.1381 | 0.790 | 0.000 | 15.0 | 2.160 | n/a | 8.0 | n/a |
| T6[1.25] | n20 | large | -0.1807 | -0.1823 | -0.0016 | 0.0557 | 0.9700 | 0.0100 | 0.0200 | 1.068 | 0.1221 | 0.370 | 0.080 | 12.3 | 0.790 | n/a | n/a | n/a |
| T6[1.25] | n20 | carries | 0.7000 | 0.6979 | -0.0021 | 0.0833 | 0.8900 | 0.0000 | 0.1100 | 0.962 | 0.1632 | 0.550 | 0.030 | 13.5 | 1.501 | n/a | 8.6 | n/a |
| T6[1.25] | n20 | depends | 1.8835 | 2.0482 | 0.1648 | 0.5916 | 0.9800 | 0.0000 | 0.0200 | 1.793 | 1.0351 | 0.210 | 0.350 | 8.9 | 0.904 | n/a | -3.1 | n/a |
| T6[1.25] | n20 | carried_margin | -0.3852 | -0.3837 | 0.0016 | 0.0812 | 0.9700 | 0.0100 | 0.0200 | 0.990 | 0.1680 | 0.080 | 0.050 | 14.8 | 0.879 | n/a | n/a | n/a |
| T6[1.25] | n20 | own_margin | -0.2045 | -0.2014 | 0.0032 | 0.0696 | 0.9800 | 0.0000 | 0.0200 | 0.940 | 0.1524 | 0.040 | 0.420 | 9.0 | 0.920 | n/a | n/a | n/a |
| T6[1.25] | n20 | kappa | -0.9137 | -0.9366 | -0.0229 | 0.2387 | 0.9600 | 0.0100 | 0.0300 | 0.965 | 0.5125 | 0.080 | 0.270 | 10.5 | 0.925 | n/a | 6.7 | n/a |
| T6[1.25] | n20 | shuffled_vs_yardstick | 0.2045 | 0.2014 | -0.0032 | 0.0696 | 0.9800 | 0.0200 | 0.0000 | 0.940 | 0.1524 | 0.040 | 0.420 | 9.0 | 0.920 | n/a | n/a | n/a |
| T6[1.25] | n20 | carried_added | 0.4216 | 0.4205 | -0.0011 | 0.0683 | 0.9000 | 0.0000 | 0.1000 | 1.014 | 0.1355 | 0.090 | 0.090 | 13.7 | 1.529 | n/a | n/a | n/a |
| T6[1.25] | n20 | pooled_retention | 0.7000 | 0.6985 | -0.0015 | 0.0718 | 0.8800 | 0.0000 | 0.1200 | 0.943 | 0.1427 | 0.830 | 0.000 | 15.0 | 2.405 | n/a | 8.9 | n/a |
| T6[1.25] | n80 | large | 6.3077 | 6.4353 | 0.1276 | 1.1789 | 0.9400 | 0.0100 | 0.0500 | 1.012 | 2.6409 | 0.110 | 0.440 | 8.4 | 1.081 | n/a | n/a | n/a |
| T6[1.25] | n80 | carries | 0.7000 | 0.7060 | 0.0060 | 0.1240 | 0.9500 | 0.0100 | 0.0400 | 0.937 | 0.2449 | 0.640 | 0.030 | 13.5 | 0.982 | n/a | 8.0 | n/a |
| T6[1.25] | n80 | depends | 2.1743 | 2.4172 | 0.2429 | 9.8054 | 0.9000 | 0.0000 | 0.1000 | 210.125 | 2.6386 | 0.250 | 0.200 | 11.1 | 1.310 | n/a | -1.3 | n/a |
| T6[1.25] | n80 | carried_margin | -5.4832 | -5.3277 | 0.1555 | 1.1875 | 0.9700 | 0.0200 | 0.0100 | 0.972 | 2.6981 | 0.090 | 0.490 | 7.8 | 0.869 | n/a | n/a | n/a |
| T6[1.25] | n80 | own_margin | -2.5218 | -2.3152 | 0.2066 | 2.0625 | 0.9600 | 0.0300 | 0.0100 | 0.924 | 4.3024 | 0.110 | 0.270 | 10.9 | 0.861 | n/a | n/a | n/a |
| T6[1.25] | n80 | kappa | -0.7935 | -0.7923 | 0.0013 | 0.2587 | 0.9600 | 0.0300 | 0.0100 | 1.026 | 0.6983 | 0.090 | 0.720 | 5.4 | 0.992 | n/a | 6.1 | n/a |
| T6[1.25] | n80 | shuffled_vs_yardstick | 11.7909 | 11.7630 | -0.0279 | 1.2364 | 0.8600 | 0.0100 | 0.1300 | 0.920 | 2.4603 | 0.080 | 0.000 | 15.1 | 2.538 | n/a | n/a | n/a |
| T6[1.25] | n80 | carried_added | 6.9100 | 7.0381 | 0.1281 | 1.2333 | 0.9400 | 0.0100 | 0.0500 | 1.022 | 2.7449 | 0.090 | 0.440 | 8.5 | 1.061 | n/a | n/a | n/a |
| T6[1.25] | n80 | pooled_retention | 0.7000 | 0.6984 | -0.0016 | 0.0725 | 0.8500 | 0.0100 | 0.1400 | 0.928 | 0.1443 | 0.860 | 0.000 | 15.0 | 2.238 | n/a | 7.6 | n/a |
| T7 | h5 | large | 2.9822 | 3.0215 | 0.0393 | 0.2886 | 0.9500 | 0.0000 | 0.0500 | 1.269 | 0.6836 | 0.420 | 0.000 | 15.3 | 0.886 | n/a | n/a | 0.746 |
| T7 | h5 | carries | 0.7000 | 0.7110 | 0.0110 | 0.0682 | 0.9300 | 0.0000 | 0.0700 | 1.272 | 0.1611 | 0.590 | 0.000 | 15.1 | 1.141 | n/a | 140.7 | 0.746 |
| T7 | h5 | depends | 0.6888 | 0.7003 | 0.0115 | 0.0686 | 0.9300 | 0.0000 | 0.0700 | 1.286 | 0.1623 | 0.590 | 0.000 | 15.1 | 1.139 | n/a | 74.1 | 0.746 |
| T7 | h5 | carried_margin | 3.4005 | 3.4462 | 0.0457 | 0.3017 | 0.9400 | 0.0000 | 0.0600 | 1.267 | 0.7232 | 0.490 | 0.000 | 15.2 | 1.261 | n/a | n/a | 0.746 |
| T7 | h5 | own_margin | 4.9368 | 4.9261 | -0.0107 | 0.0590 | 0.9900 | 0.0100 | 0.0000 | 1.449 | 0.1457 | 0.530 | 0.060 | 13.2 | 0.742 | n/a | n/a | 0.746 |
| T7 | h5 | kappa | 0.9486 | 0.9480 | -0.0007 | 0.0059 | 0.9300 | 0.0600 | 0.0100 | 1.107 | 0.0133 | 0.510 | 0.000 | 15.1 | 1.085 | n/a | 9.6 | 0.746 |
| T7 | h5 | shuffled_vs_yardstick | -0.4183 | -0.4247 | -0.0064 | 0.0575 | 0.9100 | 0.0700 | 0.0200 | 0.858 | 0.1123 | 0.230 | 0.570 | 6.8 | 1.393 | n/a | n/a | 0.746 |
| T7 | h5 | carried_added | 3.5847 | 3.6374 | 0.0527 | 0.3405 | 0.9400 | 0.0000 | 0.0600 | 1.260 | 0.8138 | 0.500 | 0.000 | 15.1 | 1.284 | n/a | n/a | 0.746 |
| T7 | h5 | pooled_retention | 0.7000 | 0.7111 | 0.0111 | 0.0677 | 0.9300 | 0.0000 | 0.0700 | 1.213 | 0.1585 | 0.440 | 0.000 | 15.1 | 1.297 | n/a | 141.8 | 0.746 |
| T8 | n20 | large | -0.1807 | -0.1855 | -0.0048 | 0.0912 | 1.0000 | 0.0000 | 0.0000 | 0.940 | 0.1855 | 0.500 | 0.040 | 6.9 | 0.824 | n/a | n/a | n/a |
| T8 | n20 | carries | 0.7000 | 0.7068 | 0.0068 | 0.1174 | 0.8700 | 0.0000 | 0.1300 | 1.055 | 0.2750 | 0.550 | 0.070 | 6.8 | 1.550 | n/a | 6.6 | n/a |
| T8 | n20 | depends | 0.5678 | 0.5780 | 0.0102 | 0.1723 | 0.8700 | 0.0000 | 0.1300 | 0.987 | 0.3960 | 0.510 | 0.030 | 7.0 | 1.309 | n/a | 7.6 | n/a |
| T8 | n20 | carried_margin | 0.2374 | 0.2440 | 0.0066 | 0.0675 | 0.9000 | 0.0000 | 0.1000 | 1.202 | 0.1531 | 0.150 | 0.220 | 6.7 | 1.404 | n/a | n/a | n/a |
| T8 | n20 | own_margin | 0.4181 | 0.4295 | 0.0114 | 0.0690 | 0.9400 | 0.0000 | 0.0600 | 0.986 | 0.1544 | 0.150 | 0.530 | 4.7 | 1.129 | n/a | n/a | n/a |
| T8 | n20 | kappa | 0.5631 | 0.5631 | -0.0000 | 0.1066 | 0.8800 | 0.1000 | 0.0200 | 0.782 | 0.2209 | 0.130 | 0.000 | 7.9 | 1.262 | n/a | 5.0 | n/a |
| T8 | n20 | shuffled_vs_yardstick | -0.4181 | -0.4295 | -0.0114 | 0.0690 | 0.9400 | 0.0600 | 0.0000 | 0.986 | 0.1544 | 0.150 | 0.530 | 4.7 | 1.129 | n/a | n/a | n/a |
| T8 | n20 | carried_added | 0.4216 | 0.4325 | 0.0109 | 0.0800 | 0.9400 | 0.0000 | 0.0600 | 1.428 | 0.2002 | 0.140 | 0.020 | 7.8 | 1.211 | n/a | n/a | n/a |
| T8 | n20 | pooled_retention | 0.7000 | 0.7083 | 0.0083 | 0.0994 | 0.8200 | 0.0000 | 0.1800 | 1.078 | 0.2473 | 0.610 | 0.000 | 7.1 | 1.799 | n/a | 6.6 | n/a |
| T8 | n40 | large | 0.7895 | 0.8170 | 0.0275 | 0.2354 | 0.9500 | 0.0000 | 0.0500 | 1.285 | 0.5565 | 0.430 | 0.030 | 7.3 | 0.912 | n/a | n/a | n/a |
| T8 | n40 | carries | 0.7000 | 0.7197 | 0.0197 | 0.1313 | 0.9900 | 0.0000 | 0.0100 | 1.198 | 0.3276 | 0.530 | 0.030 | 7.1 | 0.732 | n/a | 6.0 | n/a |
| T8 | n40 | depends | 0.6694 | 0.6921 | 0.0228 | 0.1427 | 0.9900 | 0.0000 | 0.0100 | 1.194 | 0.3551 | 0.530 | 0.030 | 7.1 | 0.749 | n/a | 6.1 | n/a |
| T8 | n40 | carried_margin | 1.2076 | 1.2468 | 0.0392 | 0.2544 | 0.9700 | 0.0000 | 0.0300 | 1.264 | 0.5941 | 0.280 | 0.040 | 7.5 | 0.838 | n/a | n/a | n/a |
| T8 | n40 | own_margin | 1.8041 | 1.8254 | 0.0214 | 0.2951 | 0.9700 | 0.0000 | 0.0300 | 1.102 | 0.7061 | 0.260 | 0.130 | 6.9 | 0.907 | n/a | n/a | n/a |
| T8 | n40 | kappa | 0.8677 | 0.8684 | 0.0007 | 0.0313 | 0.9200 | 0.0700 | 0.0100 | 0.941 | 0.0705 | 0.280 | 0.030 | 7.6 | 1.226 | n/a | 4.7 | n/a |
| T8 | n40 | shuffled_vs_yardstick | -0.4181 | -0.4298 | -0.0117 | 0.0691 | 0.9400 | 0.0600 | 0.0000 | 0.985 | 0.1559 | 0.150 | 0.520 | 4.7 | 1.163 | n/a | n/a | n/a |
| T8 | n40 | carried_added | 1.3918 | 1.4349 | 0.0432 | 0.2848 | 0.9800 | 0.0000 | 0.0200 | 1.258 | 0.6893 | 0.280 | 0.020 | 7.6 | 0.767 | n/a | n/a | n/a |
| T8 | n40 | pooled_retention | 0.7000 | 0.7065 | 0.0065 | 0.0966 | 0.7900 | 0.0000 | 0.2100 | 1.133 | 0.2476 | 0.710 | 0.000 | 7.0 | 1.787 | n/a | 6.1 | n/a |
| T8 | n80 | large | 6.3077 | 6.3843 | 0.0766 | 1.3780 | 0.9500 | 0.0000 | 0.0500 | 1.088 | 3.3056 | 0.220 | 0.150 | 6.6 | 0.998 | n/a | n/a | n/a |
| T8 | n80 | carries | 0.7000 | 0.7123 | 0.0123 | 0.1726 | 0.9500 | 0.0000 | 0.0500 | 1.051 | 0.3820 | 0.610 | 0.020 | 6.9 | 0.919 | n/a | 6.7 | n/a |
| T8 | n80 | depends | 0.6943 | 0.7077 | 0.0134 | 0.1755 | 0.9500 | 0.0000 | 0.0500 | 1.054 | 0.3861 | 0.610 | 0.020 | 6.9 | 0.916 | n/a | 6.6 | n/a |
| T8 | n80 | carried_margin | 6.7258 | 6.8140 | 0.0883 | 1.4255 | 0.9300 | 0.0100 | 0.0600 | 1.071 | 3.3625 | 0.200 | 0.150 | 6.7 | 1.014 | n/a | n/a | n/a |
| T8 | n80 | own_margin | 9.6872 | 9.8103 | 0.1232 | 1.5008 | 0.9200 | 0.0200 | 0.0600 | 1.159 | 3.8432 | 0.280 | 0.410 | 5.4 | 1.075 | n/a | n/a | n/a |
| T8 | n80 | kappa | 0.9733 | 0.9731 | -0.0003 | 0.0063 | 0.9300 | 0.0700 | 0.0000 | 0.937 | 0.0136 | 0.190 | 0.140 | 7.0 | 1.120 | n/a | 4.9 | n/a |
| T8 | n80 | shuffled_vs_yardstick | -0.4181 | -0.4297 | -0.0116 | 0.0688 | 0.9300 | 0.0700 | 0.0000 | 0.993 | 0.1526 | 0.150 | 0.550 | 4.7 | 1.084 | n/a | n/a | n/a |
| T8 | n80 | carried_added | 6.9100 | 7.0023 | 0.0923 | 1.4641 | 0.9500 | 0.0000 | 0.0500 | 1.069 | 3.4770 | 0.200 | 0.130 | 6.8 | 1.002 | n/a | n/a | n/a |
| T8 | n80 | pooled_retention | 0.7000 | 0.7069 | 0.0069 | 0.0995 | 0.7800 | 0.0000 | 0.2200 | 1.091 | 0.2451 | 0.680 | 0.000 | 7.1 | 1.700 | n/a | 7.0 | n/a |
| T8 | n160 | large | 14.5697 | 14.6252 | 0.0555 | 2.5805 | 0.9100 | 0.0000 | 0.0900 | 0.978 | 5.7304 | 0.580 | 0.040 | 7.2 | 1.060 | n/a | n/a | n/a |
| T8 | n160 | carries | 0.7000 | 0.7261 | 0.0261 | 0.1821 | 0.8700 | 0.0000 | 0.1300 | 1.013 | 0.3831 | 0.560 | 0.010 | 7.1 | 1.311 | n/a | 11.2 | n/a |
| T8 | n160 | depends | 0.6974 | 0.7242 | 0.0268 | 0.1835 | 0.8700 | 0.0000 | 0.1300 | 1.018 | 0.3838 | 0.560 | 0.010 | 7.1 | 1.304 | n/a | 10.9 | n/a |
| T8 | n160 | carried_margin | 14.9878 | 15.0547 | 0.0669 | 2.6115 | 0.9200 | 0.0000 | 0.0800 | 0.973 | 5.7796 | 0.570 | 0.040 | 7.1 | 1.061 | n/a | n/a | n/a |
| T8 | n160 | own_margin | 21.4901 | 21.1945 | -0.2956 | 2.0057 | 0.9200 | 0.0600 | 0.0200 | 0.978 | 4.7102 | 0.590 | 0.150 | 6.5 | 1.165 | n/a | n/a | n/a |
| T8 | n160 | kappa | 0.9879 | 0.9878 | -0.0000 | 0.0021 | 0.9400 | 0.0600 | 0.0000 | 1.190 | 0.0051 | 0.600 | 0.000 | 7.3 | 1.141 | n/a | 5.9 | n/a |
| T8 | n160 | shuffled_vs_yardstick | -0.4181 | -0.4295 | -0.0114 | 0.0687 | 0.9400 | 0.0600 | 0.0000 | 0.994 | 0.1528 | 0.150 | 0.530 | 4.7 | 1.106 | n/a | n/a | n/a |
| T8 | n160 | carried_added | 15.1720 | 15.2431 | 0.0711 | 2.6616 | 0.9100 | 0.0000 | 0.0900 | 0.972 | 5.9237 | 0.570 | 0.040 | 7.1 | 1.078 | n/a | n/a | n/a |
| T8 | n160 | pooled_retention | 0.7000 | 0.7071 | 0.0071 | 0.0998 | 0.8100 | 0.0000 | 0.1900 | 1.056 | 0.2365 | 0.460 | 0.000 | 7.1 | 1.718 | n/a | 10.9 | n/a |
| T8 | n320 | large | 17.0248 | 17.0433 | 0.0185 | 2.8460 | 0.9500 | 0.0000 | 0.0500 | 1.024 | 6.4825 | 0.640 | 0.020 | 7.1 | 0.972 | n/a | n/a | n/a |
| T8 | n320 | carries | 0.7000 | 0.7215 | 0.0215 | 0.1714 | 0.8700 | 0.0000 | 0.1300 | 1.071 | 0.3800 | 0.670 | 0.000 | 7.1 | 1.457 | n/a | 12.3 | n/a |
| T8 | n320 | depends | 0.6978 | 0.7198 | 0.0220 | 0.1724 | 0.8700 | 0.0000 | 0.1300 | 1.076 | 0.3810 | 0.670 | 0.000 | 7.1 | 1.454 | n/a | 12.0 | n/a |
| T8 | n320 | carried_margin | 17.4429 | 17.4727 | 0.0298 | 2.8736 | 0.9500 | 0.0000 | 0.0500 | 1.022 | 6.5984 | 0.640 | 0.020 | 7.1 | 0.980 | n/a | n/a | n/a |
| T8 | n320 | own_margin | 24.9973 | 24.7034 | -0.2939 | 2.1351 | 0.9300 | 0.0600 | 0.0100 | 1.012 | 4.9801 | 0.610 | 0.060 | 6.6 | 1.081 | n/a | n/a | n/a |
| T8 | n320 | kappa | 0.9896 | 0.9895 | -0.0001 | 0.0018 | 0.9400 | 0.0600 | 0.0000 | 1.119 | 0.0044 | 0.640 | 0.000 | 7.2 | 1.040 | n/a | 6.2 | n/a |
| T8 | n320 | shuffled_vs_yardstick | -0.4181 | -0.4294 | -0.0113 | 0.0690 | 0.9400 | 0.0600 | 0.0000 | 0.987 | 0.1539 | 0.150 | 0.540 | 4.7 | 1.122 | n/a | n/a | n/a |
| T8 | n320 | carried_added | 17.6271 | 17.6612 | 0.0342 | 2.9241 | 0.9500 | 0.0000 | 0.0500 | 1.021 | 6.6986 | 0.640 | 0.020 | 7.1 | 0.991 | n/a | n/a | n/a |
| T8 | n320 | pooled_retention | 0.7000 | 0.7071 | 0.0071 | 0.0984 | 0.7900 | 0.0000 | 0.2100 | 1.089 | 0.2383 | 0.460 | 0.000 | 7.1 | 1.865 | n/a | 11.7 | n/a |

## Verdict and Reading Frequencies

Where a signed reading's truth sits on a line, how often each verdict is printed; for the shuffled ratio always, how often each reading.

| Scenario | Row | Statistic | Line | yes | no | undetermined | a | b | c | d | no reading defined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | n20 | carries | 0.2 | 0.000 | 0.100 | 0.900 | n/a | n/a | n/a | n/a | n/a |
| P1 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.380 | 0.000 | 0.620 |
| P1 | n40 | carries | 0.2 | 0.000 | 0.020 | 0.980 | n/a | n/a | n/a | n/a | n/a |
| P1 | n40 | depends |  | n/a | n/a | n/a | 0.000 | 0.770 | 0.000 | 0.230 | 0.000 |
| P1 | n80 | carries | 0.2 | 0.010 | 0.050 | 0.940 | n/a | n/a | n/a | n/a | n/a |
| P1 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.080 | 0.000 | 0.920 | 0.000 |
| P1 | n160 | carries | 0.2 | 0.000 | 0.040 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P1 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 0.060 | 0.000 | 0.940 | 0.000 |
| P1 | n320 | carries | 0.2 | 0.000 | 0.050 | 0.950 | n/a | n/a | n/a | n/a | n/a |
| P1 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 0.060 | 0.000 | 0.940 | 0.000 |
| P1 | h2 | carries | 0.2 | 0.000 | 0.090 | 0.910 | n/a | n/a | n/a | n/a | n/a |
| P1 | h2 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P1 | h5 | carries | 0.2 | 0.000 | 0.090 | 0.910 | n/a | n/a | n/a | n/a | n/a |
| P1 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 0.490 | 0.000 | 0.510 | 0.000 |
| P1 | h10 | carries | 0.2 | 0.000 | 0.180 | 0.820 | n/a | n/a | n/a | n/a | n/a |
| P1 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 0.410 | 0.000 | 0.590 | 0.000 |
| P2 | n20 | depends |  | n/a | n/a | n/a | 0.590 | 0.000 | 0.000 | 0.410 | 0.000 |
| P2 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P2 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| P4 | n20 | carries | 0.2 | 0.000 | 0.140 | 0.860 | n/a | n/a | n/a | n/a | n/a |
| P4 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.550 | 0.000 | 0.450 |
| P4 | n40 | carries | 0.2 | 0.000 | 0.010 | 0.990 | n/a | n/a | n/a | n/a | n/a |
| P4 | n40 | depends |  | n/a | n/a | n/a | 0.000 | 0.700 | 0.030 | 0.270 | 0.000 |
| P4 | n80 | carries | 0.2 | 0.010 | 0.040 | 0.950 | n/a | n/a | n/a | n/a | n/a |
| P4 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.110 | 0.000 | 0.890 | 0.000 |
| P4 | n160 | carries | 0.2 | 0.000 | 0.100 | 0.900 | n/a | n/a | n/a | n/a | n/a |
| P4 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 0.130 | 0.000 | 0.870 | 0.000 |
| P4 | n320 | carries | 0.2 | 0.000 | 0.110 | 0.890 | n/a | n/a | n/a | n/a | n/a |
| P4 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 0.120 | 0.000 | 0.880 | 0.000 |
| P4 | h2 | carries | 0.2 | 0.000 | 0.120 | 0.880 | n/a | n/a | n/a | n/a | n/a |
| P4 | h2 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P4 | h5 | carries | 0.2 | 0.000 | 0.120 | 0.880 | n/a | n/a | n/a | n/a | n/a |
| P4 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 0.480 | 0.000 | 0.520 | 0.000 |
| P4 | h10 | carries | 0.2 | 0.000 | 0.230 | 0.770 | n/a | n/a | n/a | n/a | n/a |
| P4 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 0.380 | 0.000 | 0.620 | 0.000 |
| P5 | n20 | depends |  | n/a | n/a | n/a | 0.530 | 0.000 | 0.000 | 0.470 | 0.000 |
| P5 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P5 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n80 | depends |  | n/a | n/a | n/a | 0.990 | 0.000 | 0.000 | 0.010 | 0.000 |
| P6 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P6 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P7 | n20 | large | 0.0 | 0.000 | 0.070 | 0.930 | n/a | n/a | n/a | n/a | n/a |
| P7 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P7 | n40 | large | 0.0 | 0.000 | 0.020 | 0.980 | n/a | n/a | n/a | n/a | n/a |
| P7 | n40 | depends |  | n/a | n/a | n/a | 0.040 | 0.020 | 0.000 | 0.940 | 0.000 |
| P7 | n80 | large | 0.0 | 0.000 | 0.040 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P7 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | n160 | large | 0.0 | 0.010 | 0.020 | 0.970 | n/a | n/a | n/a | n/a | n/a |
| P7 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | n320 | large | 0.0 | 0.010 | 0.030 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P7 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | h2 | large | 0.0 | 0.000 | 0.010 | 0.990 | n/a | n/a | n/a | n/a | n/a |
| P7 | h2 | depends |  | n/a | n/a | n/a | 0.740 | 0.000 | 0.000 | 0.260 | 0.000 |
| P7 | h5 | large | 0.0 | 0.000 | 0.010 | 0.990 | n/a | n/a | n/a | n/a | n/a |
| P7 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P7 | h10 | large | 0.0 | 0.030 | 0.010 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P7 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | n20 | large | 0.0 | 0.000 | 0.100 | 0.900 | n/a | n/a | n/a | n/a | n/a |
| P8 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P8 | n40 | large | 0.0 | 0.020 | 0.020 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P8 | n40 | depends |  | n/a | n/a | n/a | 0.020 | 0.000 | 0.000 | 0.980 | 0.000 |
| P8 | n80 | large | 0.0 | 0.000 | 0.030 | 0.970 | n/a | n/a | n/a | n/a | n/a |
| P8 | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.990 | 0.010 | 0.000 | 0.000 |
| P8 | n160 | large | 0.0 | 0.030 | 0.040 | 0.930 | n/a | n/a | n/a | n/a | n/a |
| P8 | n160 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | n320 | large | 0.0 | 0.010 | 0.030 | 0.960 | n/a | n/a | n/a | n/a | n/a |
| P8 | n320 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | h2 | large | 0.0 | 0.040 | 0.050 | 0.910 | n/a | n/a | n/a | n/a | n/a |
| P8 | h2 | depends |  | n/a | n/a | n/a | 0.890 | 0.000 | 0.000 | 0.110 | 0.000 |
| P8 | h5 | large | 0.0 | 0.060 | 0.060 | 0.880 | n/a | n/a | n/a | n/a | n/a |
| P8 | h5 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P8 | h10 | large | 0.0 | 0.080 | 0.010 | 0.910 | n/a | n/a | n/a | n/a | n/a |
| P8 | h10 | depends |  | n/a | n/a | n/a | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| P9 | n20 | depends | 0.2 | 0.000 | 0.020 | 0.980 | 0.000 | 0.000 | 0.020 | 0.980 | 0.000 |
| P9 | n40 | depends | 0.2 | 0.000 | 0.020 | 0.980 | 0.000 | 0.020 | 0.000 | 0.980 | 0.000 |
| P9 | n80 | depends | 0.2 | 0.010 | 0.040 | 0.950 | 0.010 | 0.040 | 0.000 | 0.950 | 0.000 |
| P9 | n160 | depends | 0.2 | 0.000 | 0.070 | 0.930 | 0.000 | 0.070 | 0.000 | 0.930 | 0.000 |
| P9 | n320 | depends | 0.2 | 0.000 | 0.080 | 0.920 | 0.000 | 0.080 | 0.000 | 0.920 | 0.000 |
| P9 | h2 | depends | 0.2 | 0.000 | 0.130 | 0.870 | 0.000 | 0.130 | 0.000 | 0.870 | 0.000 |
| P9 | h5 | depends | 0.2 | 0.000 | 0.130 | 0.870 | 0.000 | 0.130 | 0.000 | 0.870 | 0.000 |
| P9 | h10 | depends | 0.2 | 0.000 | 0.240 | 0.760 | 0.000 | 0.240 | 0.000 | 0.760 | 0.000 |
| P10 | n20 | depends | 0.2 | 0.010 | 0.060 | 0.930 | 0.010 | 0.020 | 0.040 | 0.930 | 0.000 |
| P10 | n40 | depends | 0.2 | 0.000 | 0.050 | 0.950 | 0.000 | 0.050 | 0.000 | 0.950 | 0.000 |
| P10 | n80 | depends | 0.2 | 0.000 | 0.030 | 0.970 | 0.000 | 0.030 | 0.000 | 0.970 | 0.000 |
| P10 | n160 | depends | 0.2 | 0.000 | 0.110 | 0.890 | 0.000 | 0.110 | 0.000 | 0.890 | 0.000 |
| P10 | n320 | depends | 0.2 | 0.000 | 0.060 | 0.940 | 0.000 | 0.060 | 0.000 | 0.940 | 0.000 |
| P10 | h2 | depends | 0.2 | 0.000 | 0.100 | 0.900 | 0.000 | 0.100 | 0.000 | 0.900 | 0.000 |
| P10 | h5 | depends | 0.2 | 0.000 | 0.130 | 0.870 | 0.000 | 0.130 | 0.000 | 0.870 | 0.000 |
| P10 | h10 | depends | 0.2 | 0.000 | 0.270 | 0.730 | 0.000 | 0.270 | 0.000 | 0.730 | 0.000 |
| P11 | n20 | depends | 0.0 | 0.000 | 0.810 | 0.190 | 0.000 | 0.000 | 0.800 | 0.190 | 0.010 |
| P11 | n40 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.050 | 0.930 | 0.000 | 0.020 |
| P11 | n80 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.090 | 0.900 | 0.000 | 0.010 |
| P11 | n160 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.080 | 0.910 | 0.000 | 0.010 |
| P11 | n320 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.080 | 0.910 | 0.000 | 0.010 |
| P11 | h2 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.100 | 0.890 | 0.000 | 0.010 |
| P11 | h5 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.100 | 0.890 | 0.000 | 0.010 |
| P11 | h10 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.210 | 0.790 | 0.000 | 0.000 |
| P12 | n20 | depends | 0.0 | 0.000 | 0.780 | 0.220 | 0.000 | 0.030 | 0.740 | 0.220 | 0.010 |
| P12 | n40 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.060 | 0.930 | 0.000 | 0.010 |
| P12 | n80 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.090 | 0.900 | 0.000 | 0.010 |
| P12 | n160 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.120 | 0.880 | 0.000 | 0.000 |
| P12 | n320 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.130 | 0.870 | 0.000 | 0.000 |
| P12 | h2 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.130 | 0.870 | 0.000 | 0.000 |
| P12 | h5 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.130 | 0.870 | 0.000 | 0.000 |
| P12 | h10 | depends | 0.0 | 0.000 | 1.000 | 0.000 | 0.000 | 0.330 | 0.670 | 0.000 | 0.000 |
| P13 | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.730 | 0.260 | 0.010 |
| P13 | n40 | depends |  | n/a | n/a | n/a | 0.070 | 0.000 | 0.000 | 0.930 | 0.000 |
| P13 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | h2 | depends |  | n/a | n/a | n/a | 0.280 | 0.000 | 0.000 | 0.720 | 0.000 |
| P13 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| P13 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | n20 | depends |  | n/a | n/a | n/a | 0.720 | 0.000 | 0.000 | 0.280 | 0.000 |
| T1 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | n80 | depends |  | n/a | n/a | n/a | 0.990 | 0.000 | 0.000 | 0.010 | 0.000 |
| T1 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T1 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n20 | depends |  | n/a | n/a | n/a | 0.590 | 0.000 | 0.000 | 0.410 | 0.000 |
| T2 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T2 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n40 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n80 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T3 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | n20 | depends |  | n/a | n/a | n/a | 0.580 | 0.000 | 0.000 | 0.420 | 0.000 |
| T4 | n40 | depends |  | n/a | n/a | n/a | 0.990 | 0.000 | 0.000 | 0.010 | 0.000 |
| T4 | n80 | depends |  | n/a | n/a | n/a | 0.980 | 0.000 | 0.000 | 0.020 | 0.000 |
| T4 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h2 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T4 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | n20 | depends |  | n/a | n/a | n/a | 0.330 | 0.000 | 0.000 | 0.670 | 0.000 |
| T5 | n40 | depends |  | n/a | n/a | n/a | 0.800 | 0.000 | 0.000 | 0.200 | 0.000 |
| T5 | n80 | depends |  | n/a | n/a | n/a | 0.990 | 0.000 | 0.000 | 0.010 | 0.000 |
| T5 | n160 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | n320 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T5 | h2 | depends |  | n/a | n/a | n/a | 0.950 | 0.000 | 0.000 | 0.050 | 0.000 |
| T5 | h5 | depends |  | n/a | n/a | n/a | 0.970 | 0.000 | 0.000 | 0.030 | 0.000 |
| T5 | h10 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T6[0.3] | n20 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T6[0.3] | n80 | depends |  | n/a | n/a | n/a | 0.800 | 0.000 | 0.000 | 0.200 | 0.000 |
| T6[0.5] | n20 | depends |  | n/a | n/a | n/a | 0.950 | 0.000 | 0.000 | 0.050 | 0.000 |
| T6[0.5] | n80 | depends |  | n/a | n/a | n/a | 0.060 | 0.000 | 0.000 | 0.940 | 0.000 |
| T6[0.7] | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.010 | 0.990 | 0.000 |
| T6[0.7] | n80 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.040 | 0.960 | 0.000 |
| T6[0.85] | n20 | depends |  | n/a | n/a | n/a | 0.000 | 0.000 | 0.010 | 0.990 | 0.000 |
| T6[0.85] | n80 | depends |  | n/a | n/a | n/a | 0.010 | 0.000 | 0.040 | 0.950 | 0.000 |
| T6[0.95] | n20 | depends |  | n/a | n/a | n/a | 0.020 | 0.000 | 0.030 | 0.930 | 0.020 |
| T6[0.95] | n80 | depends |  | n/a | n/a | n/a | 0.020 | 0.000 | 0.000 | 0.960 | 0.020 |
| T6[1] | n20 | depends |  | n/a | n/a | n/a | 0.030 | 0.000 | 0.000 | 0.960 | 0.010 |
| T6[1] | n80 | depends |  | n/a | n/a | n/a | 0.020 | 0.000 | 0.000 | 0.960 | 0.020 |
| T6[1.1] | n20 | depends |  | n/a | n/a | n/a | 0.270 | 0.000 | 0.000 | 0.730 | 0.000 |
| T6[1.1] | n80 | depends |  | n/a | n/a | n/a | 0.080 | 0.000 | 0.000 | 0.920 | 0.000 |
| T6[1.25] | n20 | depends |  | n/a | n/a | n/a | 0.770 | 0.000 | 0.000 | 0.230 | 0.000 |
| T6[1.25] | n80 | depends |  | n/a | n/a | n/a | 0.260 | 0.000 | 0.000 | 0.740 | 0.000 |
| T7 | h5 | depends |  | n/a | n/a | n/a | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| T8 | n20 | depends |  | n/a | n/a | n/a | 0.500 | 0.000 | 0.000 | 0.500 | 0.000 |
| T8 | n40 | depends |  | n/a | n/a | n/a | 0.940 | 0.000 | 0.000 | 0.060 | 0.000 |
| T8 | n80 | depends |  | n/a | n/a | n/a | 0.890 | 0.000 | 0.000 | 0.110 | 0.000 |
| T8 | n160 | depends |  | n/a | n/a | n/a | 0.960 | 0.000 | 0.000 | 0.040 | 0.000 |
| T8 | n320 | depends |  | n/a | n/a | n/a | 0.980 | 0.000 | 0.000 | 0.020 | 0.000 |

## In Words

- **Core cells:** 299 judged, 163 failing: P1 n20 carries, P1 n80 carries, P1 n160 carries, P1 n320 carries, P1 h2 carries, P1 h5 carries, P1 h5 depends, P1 h10 large, P1 h10 carries, P1 h10 depends, P2 n20 carries, P2 n20 depends, P2 h2 carries, P2 h2 depends, P2 h5 large, P2 h5 carries, P2 h5 depends, P2 h10 large, P2 h10 carries, P2 h10 depends, P3 n20 carries, P3 n20 depends, P3 n160 large, P3 n160 carries, P3 n160 depends, P3 h2 large, P3 h2 carries, P3 h2 depends, P3 h5 large, P3 h5 carries, P3 h5 depends, P3 h10 large, P3 h10 carries, P3 h10 depends, P4 n20 carries, P4 n80 carries, P4 n160 carries, P4 n320 large, P4 n320 carries, P4 n320 depends, P4 h2 carries, P4 h5 carries, P4 h5 depends, P4 h10 large, P4 h10 carries, P4 h10 depends, P5 n20 depends, P5 n160 carries, P5 n320 carries, P5 n320 depends, P5 h2 carries, P5 h2 depends, P5 h5 large, P5 h5 carries, P5 h5 depends, P5 h10 large, P5 h10 carries, P5 h10 depends, P6 n20 carries, P6 n20 depends, P6 n160 carries, P6 n160 depends, P6 n320 carries, P6 n320 depends, P6 h2 carries, P6 h2 depends, P6 h5 large, P6 h5 carries, P6 h5 depends, P6 h10 large, P6 h10 carries, P6 h10 depends, P7 n20 carries, P7 n20 depends, P7 h2 carries, P7 h2 depends, P7 h5 carries, P7 h5 depends, P7 h10 carries, P7 h10 depends, P8 n20 carries, P8 n20 depends, P8 h2 large, P8 h2 carries, P8 h5 large, P8 h5 carries, P8 h5 depends, P8 h10 large, P8 h10 carries, P8 h10 depends, P9 n160 carries, P9 n160 depends, P9 n320 carries, P9 n320 depends, P9 h2 carries, P9 h2 depends, P9 h5 large, P9 h5 carries, P9 h5 depends, P9 h10 large, P9 h10 carries, P9 h10 depends, P10 n20 depends, P10 n40 depends, P10 n160 carries, P10 n160 depends, P10 n320 depends, P10 h2 carries, P10 h2 depends, P10 h5 carries, P10 h5 depends, P10 h10 large, P10 h10 carries, P10 h10 depends, P11 n40 large, P11 n40 depends, P11 n80 large, P11 n80 depends, P11 n160 large, P11 n160 carries, P11 n160 depends, P11 n320 large, P11 n320 carries, P11 n320 depends, P11 h2 large, P11 h2 carries, P11 h2 depends, P11 h5 large, P11 h5 carries, P11 h5 depends, P11 h10 large, P11 h10 carries, P11 h10 depends, P12 n20 carries, P12 n40 large, P12 n40 depends, P12 n80 large, P12 n80 depends, P12 n160 carries, P12 n160 depends, P12 n320 carries, P12 n320 depends, P12 h2 carries, P12 h2 depends, P12 h5 carries, P12 h5 depends, P12 h10 large, P12 h10 carries, P12 h10 depends, P13 n20 carries, P13 n40 large, P13 n40 carries, P13 n40 depends, P13 n160 carries, P13 n160 depends, P13 n320 large, P13 h2 carries, P13 h5 large, P13 h5 carries, P13 h5 depends, P13 h10 large, P13 h10 carries, P13 h10 depends.
- **n20:** needs more than 1.5; the row goes to the PI.
- **n40:** multiplier 1.40, confirmed on seed 2 (lowest coverage 0.9650).
- **n80:** needs more than 1.5; the row goes to the PI.
- **n160:** needs more than 1.5; the row goes to the PI.
- **n320:** needs more than 1.5; the row goes to the PI.
- **h2:** needs more than 1.5; the row goes to the PI.
- **h5:** needs more than 1.5; the row goes to the PI.
- **h10:** needs more than 1.5; the row goes to the PI.
- **Stress cells under 92.5 percent:** 277, listed above as limits for the post.
- **G1:** yes. **G2:** yes.
- **Seeds:** master 20261005. **Commit:** b410ddb7946c8150c15f777271888cb68f1b7f75 (code as committed: no).
