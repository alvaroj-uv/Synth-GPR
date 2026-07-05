Equation 45 becomes, here

$$\sigma_{m}(\mathbf{m}) = k \exp \left( - \left( \sum_{\alpha} \frac{|m^{\alpha} - m_{\text{prior}}^{\alpha}|}{\sigma_{\alpha}} + \sum_{i} \frac{|f^{i}(\mathbf{m}) - d_{\text{obs}}^{i}|}{\sigma_{i}} \right) \right) \Psi(\mathbf{m}) \quad , \tag{59}$$

where $\Psi(\mathbf{m})$ is a complex term containing, in particular, the matrix of partial derivatives $\mathbf{F}$. If this term is approximately constant (weak nonlinearities, constant metrics), then

$$\sigma_{m}(\mathbf{m}) = k \exp \left( - \left( \sum_{\alpha} \frac{|m^{\alpha} - m_{\text{prior}}^{\alpha}|}{\sigma_{\alpha}} + \sum_{i} \frac{|f^{i}(\mathbf{m}) - d_{\text{obs}}^{i}|}{\sigma_{i}} \right) \right) \quad . \tag{60}$$

[END OF EXAMPLE.]

The formulas in the examples above give expressions that contain analytic parts (like the square roots containing the matrix of partial derivatives $\mathbf{F}$). What we write as $\mathbf{d} = \mathbf{f}(\mathbf{m})$ may sometimes correspond to an explicit expression; sometimes it may corresponds to the solution of an implicit equation$^{17}$. Should $\mathbf{d} = \mathbf{f}(\mathbf{m})$ be an explicit expression, and should the 'prior probability densities' $\rho_{m}(\mathbf{m})$ and $\rho_{d}(\mathbf{d})$ (or the joint $\rho(\mathbf{m}, \mathbf{d})$) also be given by explicit expressions (like when we have Gaussian probability densities), then the formulas of this section would give explicit expressions for the posterior probability density $\sigma_{m}(\mathbf{m})$.

If the relation $\mathbf{d} = \mathbf{f}(\mathbf{m})$ is a linear relation, then the expression giving $\sigma_{m}(\mathbf{m})$ can sometimes be simplified easily (as with the linear Gaussian case to be examined below). More often than not the relation $\mathbf{d} = \mathbf{f}(\mathbf{m})$ is a complex nonlinear relation, and the expression we are left with for $\sigma_{m}(\mathbf{m})$ is explicit, but complex.

Once the probability density $\sigma_{m}(\mathbf{m})$ has been defined, there are different ways of 'using' it.

If the 'model space' $\mathcal{M}$ has a small number of dimensions (say between one and four) the values of $\sigma_{m}(\mathbf{m})$ can be computed at every point of a grid and a graphical representation of $\sigma_{m}(\mathbf{m})$ can be attempted. A visual inspection of such a representation is usually worth a thousand 'estimators' (central estimators or estimators of dispersion). But, of course, if the values of $\sigma_{m}(\mathbf{m})$ are known at all points where $\sigma_{m}(\mathbf{m})$ has a significant value, these estimators can also be computed.

If the 'model space' $\mathcal{M}$ has a large number of dimensions (say from five to many millions or billions), then an exhaustive exploration of the space is not possible, and we must turn to Monte Carlo sampling methods to extract information from $\sigma_{m}(\mathbf{m})$. We discuss the application of Monte Carlo methods to inverse problems, and optimization techniques in section 6 and 7, respectively.

## 4.6 Physical Laws as Probabilistic Correlations

### 4.6.1 Physical Laws

We return here to the general case where it is not assumed that the total space $(\mathcal{M}, \mathcal{D})$ is the Cartesian product of two spaces.

In section 4.5 we have examined the situation where the physical correlation between the parameters of the problem are expressed using an exact, analytic expression $\mathbf{d} = \mathbf{g}(\mathbf{m})$. In this case, the notion of conditional probability density has been used to combine the 'physical theory' with the 'data' and the 'a priori information' on model parameters.

But we have seen that in order to properly define the notion of conditional probability density, it has been necessary to introduce a metric over the space, and to take a limit using the metric of the space. This is equivalent to put some 'thickness' around the theoretical relation $\mathbf{d} = \mathbf{g}(\mathbf{m})$, and to take the limit when the thickness tends to zero.

But actual theories have some uncertainties, and, for more generality, it is better to explicitly introduce these uncertainties. Assume, then, that the physical correlations between the model parameters $\mathbf{m}$ and the data parameters $\mathbf{d}$ are not represented by an analytical expression like $\mathbf{d} = \mathbf{f}(\mathbf{m})$, but by a probability density

$$\vartheta(\mathbf{m}, \mathbf{d}) \quad . \tag{61}$$

$^{17}$Practically, it may correspond to the output of some 'black box' solving the 'forward problem'.

23