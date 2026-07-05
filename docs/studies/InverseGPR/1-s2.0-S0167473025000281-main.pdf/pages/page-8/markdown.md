Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

The solution error of the probabilistic inverse problem can be quantified by the discrepancy between the identification results and the true values of the assigned probability of each Voronoi cell:

\[
\text { error } = \sqrt {\sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \left| \operatorname * {P r} _ {q} - \hat {\operatorname * {P r}} _ {q} \right| ^ {2}} = \| \boldsymbol {y} - \hat {\boldsymbol {y}} \| _ {2} \tag {45}
\]

where  \( \boldsymbol{y} = (\mathrm{Pr}_{1}, \mathrm{Pr}_{2}, \ldots, \mathrm{Pr}_{N_{\mathrm{sel}}})^{\top}, \hat{\boldsymbol{y}} = (\hat{\mathrm{Pr}}_{1}, \hat{\mathrm{Pr}}_{2}, \ldots, \hat{\mathrm{Pr}}_{N_{\mathrm{sel}}})^{\top} \)  denote the true assigned probability vector and the one derived from identification results.

Eq. (19) indicates that \( p_{\pmb{x}}^{\mathrm{par}}(\pmb{x},t) \) and \( p_{\pmb{x}}^{\mathrm{opt}}(\pmb{x},t) \) are assembled as follows:

\[
p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x}, t) = \sum_ {q = 1} ^ {N _ {\text { sel }}} \operatorname * {P r} _ {q} p _ {q} (\boldsymbol {x}, t), \quad p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x}, t) = \sum_ {q = 1} ^ {N _ {\text { sel }}} \hat {\operatorname * {P r}} _ {q} p _ {q} (\boldsymbol {x}, t) \tag {46}
\]

Using an analogous method as described earlier, \( p_{\pmb{x}}^{\mathrm{par}}(\pmb{x},t), p_{\pmb{x}}^{\mathrm{opt}}(\pmb{x},t), p_{q}(\pmb{x},t) \) can be stored as vectors when different coordinate arrays \( x_{1}, x_{2}, \ldots, x_{l_{k}} \) are selected for different time instants \( t_k \):

\[
J _ {k} ^ {\text { par }} = \left(p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {1}, t _ {k}), p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47a}
\]

\[
J _ {k} ^ {\text { opt }} = \left(p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {1}, t _ {k}), p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47b}
\]

\[
\boldsymbol {P} _ {k} ^ {(q)} = \left(p _ {q} (\boldsymbol {x} _ {1}, t _ {k}), p _ {q} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {q} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47c}
\]

Thus, the discretized version of Eq. (46) can be obtained:

\[
J _ {\mathrm{ex}} ^ {\text { par }} = P _ {\mathrm{ex}} y, \quad J _ {\mathrm{ex}} ^ {\text { opt }} = P _ {\mathrm{ex}} \hat {y} \tag {48}
\]

where:

\[
J _ {\mathrm{ex}} ^ {\text { par }} = \left(\left(f _ {1} ^ {\text { par }}\right) ^ {\top}, \left(f _ {2} ^ {\text { par }}\right) ^ {\top}, \dots , \left(f _ {N _ {1}} ^ {\text { par }}\right) ^ {\top}\right) ^ {\top} \tag {49a}
\]

\[
J _ {\mathrm{ex}} ^ {\text { opt }} = \left(\left(f _ {1} ^ {\text { opt }}\right) ^ {\top}, \left(f _ {2} ^ {\text { opt }}\right) ^ {\top}, \dots , \left(f _ {N _ {1}} ^ {\text { opt }}\right) ^ {\top}\right) ^ {\top} \tag {49b}
\]

\[
\boldsymbol {P} _ {\mathrm{ex}} = \left[ \boldsymbol {P} _ {1} ^ {\top}, \boldsymbol {P} _ {2} ^ {\top}, \dots , \boldsymbol {P} _ {N _ {k}} ^ {\top} \right] ^ {\top}, \quad \boldsymbol {P} _ {k} = \left[ \boldsymbol {P} _ {k} ^ {(1)}, \boldsymbol {P} _ {k} ^ {(2)}, \dots , \boldsymbol {P} _ {k} ^ {(N _ {\mathrm{sel}})} \right] \tag {49c}
\]

The two equations in Eq. (48) form overdetermined systems of equations, and their exact solutions, i.e., the least squares solutions, can be written as:

\[
\boldsymbol {y} = \boldsymbol {A} ^ {- 1} \boldsymbol {P} _ {\mathrm{ex}} ^ {\top} \boldsymbol {J} _ {\mathrm{ex}} ^ {\text { par }}, \quad \hat {\boldsymbol {y}} = \boldsymbol {A} ^ {- 1} \boldsymbol {P} _ {\mathrm{ex}} ^ {\top} \boldsymbol {J} _ {\mathrm{ex}} ^ {\text { opt }}, \tag {50}
\]

where A represents  \( P_{ex}^{x}P_{ex} \) . The upper bound of the error expressed in Eq. (45) can be estimated as follows:

\[
\begin{array}{l} \text { error } = \| \boldsymbol {y} - \hat {\boldsymbol {y}} \| _ {2} \leq \| \boldsymbol {A} ^ {- 1} \| _ {2} \| \boldsymbol {P} _ {\mathrm{ex}} \| _ {2} \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \\ = \frac {s _ {\max}}{s _ {\min} ^ {2}} \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \\ \leq \frac {s _ {\max}}{s _ {\min} ^ {2}} (e _ {\text { par }} + e _ {\text { kde }} + e _ {\text { opt }} + e ^ {\prime}) \tag {51a} \\ \end{array}
\]

\[
e _ {\text { par }} = \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { true }} \| _ {2}, \quad e _ {\mathrm{kde}} = \| J _ {\mathrm{ex}} ^ {\text { true }} - J _ {\mathrm{ex}} ^ {\mathrm{kde}} \| _ {2}, \quad e _ {\text { opt }} = \| J _ {\mathrm{ex}} ^ {\mathrm{kde}} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \tag {51b}
\]

where  \( s_{max} \) ,  \( s_{min} \)  is the maximum and minimal singular value of  \( P_{ex} \) ; the vectors  \( f_{ex}^{true} \) ,  \( f_{ex}^{kde} \)  are constructed in the same manner, as outlined in Eq. (49).  \( s_{max}/s_{min}^{2} \)  quantify the error amplification effect and  \( e_{par} \) ,  \( e_{kde} \) ,  \( e_{opt} \) ,  \( e' \)  represents errors arising from the random source space partition, the KDE of the observed samples of system responses, the random source identification algorithm, and additional factors, respectively. Among these,  \( e_{kde} \)  vanishes as sample size increases and  \( e_{opt} \)  is, in fact, the objective function of the random source identification algorithms. The analysis of  \( e_{par} \)  and the error amplification effect factor  \( s_{max}/s_{min}^{2} \)  is carried out as follows.

It is noted that the local probability density \( p_{q}(\pmb{x},t) \) converges to the Dirac function \( \delta [\pmb {x} - \pmb {H}(\theta_q,t)] \) when the size of each subdomain

\(\Omega_q\) vanishes. Therefore an asymptotic expression of \(e_{\mathrm{par}}\) is derived as follows:

\[
\begin{array}{l} e _ {\text { par }} = \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| p _ {\boldsymbol {x}} ^ {\text { true }} (\boldsymbol {x} _ {i} , t _ {k}) - p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {i} , t _ {k}) \right| ^ {2}} \\ = \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| \int_ {\Omega_ {\boldsymbol {\theta}}} \delta [ \boldsymbol {x} _ {i} - \boldsymbol {H} (\boldsymbol {\theta} , t _ {k}) ] p _ {\boldsymbol {\theta}} (\boldsymbol {\theta}) \mathrm{d} \boldsymbol {\theta} - \sum_ {q = 1} ^ {N _ {\text {sel}}} \operatorname * {P r} _ {q} p _ {q} (\boldsymbol {x} _ {i} , t _ {k}) \right| ^ {2}} \\ \approx \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| \int_ {\Omega_ {\boldsymbol {\theta}}} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} , t _ {k}) p _ {\boldsymbol {\theta}} (\boldsymbol {\theta}) \mathrm{d} \boldsymbol {\theta} - \sum_ {q = 1} ^ {N _ {\text {sel}}} \operatorname * {P r} _ {q} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} _ {q} , t _ {k}) \right| ^ {2}} \\ \leq D _ {\mathrm{EF}} \left(\mathcal {P} _ {\text {sel}}\right) \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left[ T V \left(f \left(x _ {i} , \bullet , t _ {k}\right)\right) \right] ^ {2}} \tag {52} \\ \end{array}
\]

where \(\Theta\) is the standardized the random source taking values in the hyperrectangle \(C^\gamma = [0,1]^{\gamma}\), \(f(x,\theta ,t) = \sum_{q = 1}^{N_1}p_q(x,t)I_{\Omega_q}(\theta)\) and \(I_{\Omega_q}\) is the indicator function of \(\Omega_q\).

The last line of the above equation is derived from the extended Koksma–Hlawka inequality for multi-dimensional case proposed by Chen et al. [52], where  \( D_{\mathrm{EF}}(\mathcal{P}_{\mathrm{sel}}) \)  represents the EF-discrepancy of  \( P_{sel} \)  and  \( TV(f(x_{i},\bullet,t_{k})) \)  denotes the total variation of  \( f(x_{i},\theta,t_{k}) \)  which is regarded as the function of  \( \theta \) . The expressions for these two are as follows [53]:

\[
D _ {\mathrm{EF}} \left(\mathcal {P} _ {\text {sel}}\right) = \sup _ {\theta \in \mathbb {R} ^ {d}} \left| \sum_ {q = 1} ^ {N _ {1}} \operatorname * {P r} _ {q} I \left(\theta_ {q} \leq \theta\right) - F _ {\boldsymbol {\theta}} (\theta) \right| \tag {53a}
\]

\[
T V (f (\boldsymbol {x} _ {i}, \bullet , t _ {k})) = \sum_ {\beta = 1} ^ {s} \sum_ {\alpha_ {1} + \alpha_ {2} + \dots + \alpha_ {n} = \beta} \int_ {C ^ {\gamma}} \left| \frac {\partial^ {\beta} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} , t _ {k})}{\partial \theta_ {1} ^ {\alpha_ {1}} \partial \theta_ {2} ^ {\alpha_ {2}} \dots \partial \theta_ {n} ^ {\alpha_ {n}}} \right| d \boldsymbol {\theta} \tag {53b}
\]

where \(F_{\theta}(\theta)\) is the CDF of \(\theta\).

In most cases, the total variation of  \( f(x_{i},\bullet,t_{k}) \)  is strongly related to the degree of the nonlinearity of the system and is nearly impossible to calculate, while the EF-discrepancy is controllable. As long as the density of the partition points is approximately proportional to the probability density function of the random source, the EF-discrepancy can be kept small, thereby effectively controlling the error term  \( e_{par} \) . This is also why the multi-dimensional random source identification algorithm densifies the partition point set using the assigned probabilities as weights.

In the upper bound error estimation expressed by Eq. (51), as the ill-conditioning of  \( P_{ex} \)  worsens, the error amplification factor grows, leading to a sharp decline in the accuracy of the random source identification algorithm. Let the number of rows of the matrix  \( P_{ex} \)  be M. By performing singular value decomposition(SVD), two real orthogonal matrices U and V can be found such that:

\[
\boldsymbol {P} _ {\mathrm{ex}} = \boldsymbol {U} \boldsymbol {S} \boldsymbol {V} ^ {\top} \tag {54a}
\]

\[
\boldsymbol {S} = \left[ \begin{array}{c} \boldsymbol {\Delta} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right], \quad \boldsymbol {\Delta} = \operatorname{diag} (s _ {1}, s _ {2}, \dots , s _ {N _ {\mathrm{sel}}}) \tag {54b}
\]

\[
\boldsymbol {U} = \left[ \boldsymbol {U} ^ {(1)}, \boldsymbol {U} ^ {(2)}, \dots , \boldsymbol {U} ^ {(M)} \right], \quad \boldsymbol {V} = \left[ \boldsymbol {V} ^ {(1)}, \boldsymbol {V} ^ {(2)}, \dots , \boldsymbol {V} ^ {(N _ {\mathrm{sel}})} \right] \tag {54c}
\]

where \( s_i, i = 1,2,\dots,N_{\mathrm{sel}} \) are the singular values of \( P_{\mathrm{ex}} \) arranged in descending order, and \( U^{(i)}, V^{(i)} \) represents the column vectors of \( U, V \). The SVD of \( P_{\mathrm{ex}} \) is rearranged as follows:

\[
\boldsymbol {S} \boldsymbol {V} ^ {\top} = \left[ \begin{array}{c} \boldsymbol {\Delta} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right] \left[ \begin{array}{c} \boldsymbol {V} ^ {(1) \top} \\ \boldsymbol {V} ^ {(2) \top} \\ \dots \\ \boldsymbol {V} ^ {(N _ {\mathrm{sel}}) \top} \end{array} \right] = \left[ \begin{array}{c} s _ {1} \boldsymbol {V} ^ {(1) \top} \\ s _ {2} \boldsymbol {V} ^ {(2) \top} \\ \dots \\ s _ {N _ {\mathrm{sel}}} \boldsymbol {V} ^ {(N _ {\mathrm{sel}}) \top} \\ \boldsymbol {O} \end{array} \right] = \left[ \begin{array}{c} \boldsymbol {D} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right] \tag {55a}
\]

\[
\boldsymbol {P} _ {\mathrm{ex}} = \left[ \boldsymbol {U} ^ {(1)}, \dots , \boldsymbol {U} ^ {(M)} \right] \left[ \begin{array}{l} \boldsymbol {D} \\ \boldsymbol {O} \end{array} \right] = \left[ \sum_ {i = 1} ^ {N _ {\mathrm{sel}}} \boldsymbol {U} ^ {(i)} D _ {i 1}, \dots , \sum_ {i = 1} ^ {N _ {\mathrm{sel}}} \boldsymbol {U} ^ {(i)} D _ {i N _ {\mathrm{sel}}} \right] \tag {55b}
\]

If, starting from \( s_i \), singular values are either zero or near zero, some rows of the matrix \( D \) in Eq. (55) become zero or nearly zero, leading to

8