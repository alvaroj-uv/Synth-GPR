10

Balgaisha Mukanova, Vladimir G. Romanov

Table 2. Values of the discrepancy η for noise free data depending on the parameters N, α and other inputs defined in Table 1:

|  Φ(t) = sin(8t + β₁) exp(−0.2t)  |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- |
|  N\α | 0 | 10⁻⁵ | 10⁻⁴ | 10⁻³ | 10⁻² | 10⁻¹  |
|  5 | 0.084 | 0.084 | 0.084 | 0.084 | 0.084 | 0.093  |
|  8 | 0.054 | 0.054 | 0.054 | 0.054 | 0.054 | 0.067  |
|  11 | 0.012 | 0.012 | 0.012 | 0.012 | 0.013 | 0.042  |
|  14 | 0.0065 | 0.0065 | 0.0065 | 0.0065 | 0.008 | 0.041  |
|  17 | 0.0043 | 0.0043 | 0.0043 | 0.0043 | 0.006 | 0.04  |
|  20 | 0.0029 | 0.0029 | 0.0029 | 0.003 | 0.005 | 0.04  |
|  Φ(t) = sin(t + β₂) exp(−0.2t)  |   |   |   |   |   |   |
|  N\α | 0 | 10⁻⁵ | 10⁻⁴ | 10⁻³ | 10⁻² | 10⁻¹  |
|  5 | 0.0034 | 0.034 | 0.034 | 0.034 | 0.034 | 0.049  |
|  8 | 0.01 | 0.01 | 0.01 | 0.01 | 0.011 | 0.039  |
|  11 | 0.001 | 0.001 | 0.001 | 0.0011 | 0.0043 | 0.038  |
|  14 | 0.00044 | 0.00044 | 0.00044 | 0.0006 | 0.0043 | 0.038  |
|  17 | 0.00037 | 0.00036 | 0.00046 | 0.00054 | 0.0043 | 0.038  |
|  20 | 0.00037 | 0.00036 | 0.00036 | 0.00054 | 0.0043 | 0.038  |

C(𝒜ᴺ, α) computed for the function Φ(t) = sin(ωt + β) exp(−γt) − Φ₀ with different values of ω, α and N. The parameters β and Φ₀ are taken to satisfy the conditions Φ(0) = 0, Φ'(0) = 0, namely, β = arctan(ω/γ), Φ₀ = sin β. Values of discrepancies η(N, α) calculated for noise free data are collected in Table 2.

It is seen in Table 1 that the most important parameters that influence to the condition number are the frequency ω of the perturbation Φ(t) and the cut-off parameter N. It follows from calculations that higher values of ω are preferable. Numerical experiments show that the value of C(𝒜ᴺ, α) increases when N grows and almost does not depend on α for ω = 8 and decreases when α grows for ω = 1. On the other hand, Table 2 shows that lower values of α correspond to smaller discrepancy η. This is the reason why the value of α = 0 has been set in the experiments described below.

Results shown in Table 1 confirm also the Remark made in previous Section. Values of |H(0)| for Φ(t) = sin(8t + β₁) exp(−0.2t) and Φ(t) = sin(t + β₂) exp(−0.2t) are 64.02 and 1.02 respectively. It is seen from Table 1 that the function Φ(t) with bigger |H(0)| = |Φ''(0)| is preferable.

Further we have checked different values of decay coefficient ν = 0.2 ÷ 10 of the function Φ(t) = sin(ωt + β) exp(−νt). It turned out that bigger values of ν are preferable because they decrease C(𝒜ᴺ, α). For instance, for the value ν = 10 and N changing in the range 5 ÷ 20 the computed values of C(𝒜ᴺ, α) monotonously raise in the intervals 1.03 ÷ 1.6 and 1.0 ÷ 1.11 for ω = 8 and ω = 1 respectively.

In order to obtain admissible values of parameter N for different noise level γ, we generate synthetic data for T = 12 · 10⁻⁹ sec, c = 1.5 · 10⁸ m/sec, l = 0.9 m, F(x) = exp(−((x − 0.3l)/0.15l)²) + exp(−((x − 0.7l)/0.1l)²) with function H(t) = Φ''(t), Φ(t) = sin(8t + 1.546) exp(−0.2t). Different values of N has been tested and the most favorable ones are established. The results are collected in Table 3.