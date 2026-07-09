$$\begin{array}{l} = k \exp \left(- \frac {1}{2} \left((\mathbf {m} - \mathbf {m} _ {\text {prior}}) ^ {t} \mathbf {C} _ {M} ^ {- 1} (\mathbf {m} - \mathbf {m} _ {\text {prior}}) + (\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}}) ^ {t} \mathbf {C} _ {D} ^ {- 1} (\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}})\right)\right) \times \\ \times \frac {\sqrt {\det \left(\mathbf {C} _ {M} ^ {- 1} + \mathbf {F} ^ {T} (\mathbf {m}) \mathbf {C} _ {D} ^ {- 1} \mathbf {F} (\mathbf {m})\right)}}{\sqrt {\det \mathbf {C} _ {M} ^ {- 1}}} \tag {50} \end{array}$$

(the constant factor $\sqrt{\det \mathbf{C}_M^{-1}}$ has been left for subsequent simplifications). Defining the misfit

$$S (\mathbf {m}) = - 2 \log \frac {\sigma_ {m} (\mathbf {m})}{\sigma_ {0}} \quad , \tag {51}$$

where $\sigma_0$ is an arbitrary value of $\sigma_m(\mathbf{m})$ , gives, up to an additive constant,

$$S (\mathbf {m}) = S _ {1} (\mathbf {m}) - S _ {2} (\mathbf {m}) \quad , \tag {52}$$

where $S_{1}(\mathbf{m})$ is the usual least-squares misfit function

$$S _ {1} (\mathbf {m}) = \left(\mathbf {m} - \mathbf {m} _ {\text {prior}}\right) ^ {t} \mathbf {C} _ {M} ^ {- 1} \left(\mathbf {m} - \mathbf {m} _ {\text {prior}}\right) + \left(\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}}\right) ^ {t} \mathbf {C} _ {D} ^ {- 1} \left(\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}}\right) \tag {53}$$

and where$^{14}$

$$S _ {2} (\mathbf {m}) = \log \det \left(\mathbf {I} + \mathbf {C} _ {M} \mathbf {F} ^ {T} (\mathbf {m}) \mathbf {C} _ {D} ^ {- 1} \mathbf {F} (\mathbf {m})\right) . \tag {54}$$

[END OF EXAMPLE.]

Example 11 If, in the context of example 10, we have$^{15}$ $\mathbf{C}_M\mathbf{F}^T\mathbf{C}_D^{-1}\mathbf{F} << \mathbf{I}$ , we can use the low order approximation for $S_2(\mathbf{m})$ , that is$^{16}$

$$S _ {2} (\mathbf {m}) \approx \operatorname {t r a c e} \mathbf {C} _ {M} \mathbf {F} ^ {T} (\mathbf {m}) \mathbf {C} _ {D} ^ {- 1} \mathbf {F} (\mathbf {m}) . \tag {55}$$

[END OF EXAMPLE.]

Example 12 If in the context of example 10 we assume that the nonlinearities are weak, then the matrix of partial derivatives $\mathbf{F}$ is approximately constant, and equation 50 simplifies to

$$\sigma_ {m} (\mathbf {m}) = \tag {56}$$

$$= k \exp \left(- \frac {1}{2} \left((\mathbf {m} - \mathbf {m} _ {\text {prior}}) ^ {t} \mathbf {C} _ {M} ^ {- 1} (\mathbf {m} - \mathbf {m} _ {\text {prior}}) + (\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}}) ^ {t} \mathbf {C} _ {D} ^ {- 1} (\mathbf {f} (\mathbf {m}) - \mathbf {d} _ {\text {obs}})\right)\right) \quad ,$$

and the function $S_{2}(\mathbf{m})$ is just a constant. [END OF EXAMPLE.]

Example 13 If the 'relation solving the forward problem' $\mathbf{d} = \mathbf{f}(\mathbf{m})$ happens to be a linear relation, $\mathbf{d} = \mathbf{F}\mathbf{m}$ , then one gets the standard equations for linear problems (see appendix F). [END OF EXAMPLE.]

Example 14 We examine here the simplifications at we arrive at when assuming that the 'input' probability densities are Laplacian:

$$\rho_ {m} (\mathbf {m}) = k \exp \left(- \sum_ {\alpha} \frac {\left| m ^ {\alpha} - m _ {\text {prior}} ^ {\alpha} \right|}{\sigma_ {\alpha}}\right) \tag {57}$$

$$\rho_ {d} (\mathbf {d}) = k \exp \left(- \sum_ {i} \frac {\left| d ^ {i} - d _ {\mathrm{obs}} ^ {i} \right|}{\sigma_ {i}}\right) \quad . \tag {58}$$

$^{14}$We use here the properties $\log \sqrt{\mathbf{A}} = \frac{1}{2}\log \mathbf{A}$ , and $\det \mathbf{A}\mathbf{B} = \det \mathbf{B}\mathbf{A}$

$^{15}$Typically, this may happen because the derivatives $\mathbf{F}$ are small or because the variances in $\mathbf{C}_M$ are large.

$^{16}$We first use $\log \det \mathbf{A} = \operatorname {trace}\log \mathbf{A}$ , and then the series expansion of the logarithm of an operator, $\log (\mathbf{I} + \mathbf{A}) = \mathbf{A} - \frac{1}{2}\mathbf{A}^2 +\dots$

22