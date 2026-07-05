Table 4.1: The true, ray-based estimated and FWI-estimated parameter values for the synthetic model shown in Figure 4.3. $x$ represents the horizontal location in $cm$, $y$ the depth in $cm$ and $d$ the diameter in $mm$. $\epsilon$ is the unit-less concrete relative permittivity and $\sigma$ is the concrete conductivity in $mS/m$.

|  rebar# | True |   |   | Ray-based |   |   | FWI  |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|   |  x | y | d | x | y | d | x | y | d  |
|  1 | 15 | 3.5 | 20 | 16.46 | 4.64 | 24.9 | 14.99 | 3.62 | 21.63  |
|  2 | 35 | 3.5 | 20 | 36.51 | 4.04 | 7.2 | 35.00 | 3.57 | 19.02  |
|  3 | 60 | 4 | 20 | 61.47 | 5.9 | 44.8 | 60.00 | 3.78 | 16.95  |
|  4 | 80 | 2.7 | 20 | 81.46 | 3.89 | 35.7 | 77.96 | 2.56 | 22.31  |
|  Parameter | True | Ray-based | FWI |   |   |   |   |   |   |
|  $\bar{\epsilon}_{concrete}$ | 5 | 3.89 | 4.77 |   |   |   |   |   |   |
|  $\sigma_{concrete}$ | 10 | 14.2 | 11.2 |   |   |   |   |   |   |

minimum of 4% and maximum of 15.2%. Since the FWI estimate for $\epsilon_{concrete}$ is improved over the ray-based value, depths are also more accurately estimated. The concrete conductivity estimate is similarly improved.

#### 4.5.2 Real data, case 1

A concrete block with length 137 $cm$, width 25 $cm$ and depth 15 $cm$ was constructed using normal weight concrete ($^{water}/_{cement}$ ratio of 0.4; maximum aggregate size of 19 $mm$ with a 28 day target compressive strength of 4000 $psi$) (Figure 4.7 in next page) Hasan and Yazdani (2016b). Three different standard 19 $mm$ ($^{3}/_{4}''$) rebar were embedded with different concrete covers (2.5, 5, 7.5 $cm$) (Figure 4.8). A ground-coupled 2.6 $GHz$ GSSI system was used to collect GPR B-scans perpendicular to rebar direction.

Initial basic processing of the collected data is required before FWI. A standard dewow filter and time-zero correction are applied first. Finally, high frequency noise was removed from the data using a simple low pass filter to remove the frequencies greater than 3.2 GHz.

As for the synthetic example, the returns from the least deep rebar (thinnest cover thickness) are mixed in the direct wave (Figure 4.9) and background removal is applied before SBD (Figure 4.10). The initial source wavelet for SBD is captured from the data (black boxes

20