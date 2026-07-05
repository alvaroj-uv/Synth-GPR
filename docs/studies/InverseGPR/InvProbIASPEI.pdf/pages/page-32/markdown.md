Example 23 In the context of example 22 the model space $\mathcal{M}$ has an obvious metric, namely that defined by the inverse of the 'a priori' covariance operator $\mathbf{g} = \mathbf{C}_M^{-1}$. Using this metric and the gradient given by equation 109, the steepest descent algorithm 107 becomes

$$\mathbf{m}_{k+1} = \mathbf{m}_k - \varepsilon_k \left( \mathbf{C}_M \mathbf{F}_k^t \mathbf{C}_D^{-1} (\mathbf{f}_k - \mathbf{d}_{\text{obs}}) + (\mathbf{m}_k - \mathbf{m}_{\text{prior}}) \right) \quad , \tag{111}$$

where $\mathbf{F}_k \equiv \mathbf{F}(\mathbf{m}_k)$ and $\mathbf{f}_k \equiv \mathbf{f}(\mathbf{m}_k)$. The real positive quantities $\varepsilon_k$ can be fixed after some trial and error by accurate linear search, or by using a linearized approximation$^{22}$. [END OF EXAMPLE.]

Example 24 In the context of example 22 the model space $\mathcal{M}$ has a less obvious metric, namely that defined by the inverse of the 'posterior' covariance operator, $\mathbf{g} = \widetilde{\mathbf{C}}_M^{-1}$ $^{23}$. Using this metric and the gradient given by equation 109, the steepest descent algorithm 107 becomes

$$\mathbf{m}_{k+1} = \mathbf{m}_k - \varepsilon_k \left( \mathbf{F}_k^t \mathbf{C}_D^{-1} \mathbf{F}_k + \mathbf{C}_M^{-1} \right)^{-1} \left( \mathbf{F}_k^t \mathbf{C}_D^{-1} (\mathbf{f}_k - \mathbf{d}_{\text{obs}}) + \mathbf{C}_M^{-1} (\mathbf{m}_k - \mathbf{m}_{\text{prior}}) \right) \quad , \tag{113}$$

where $\mathbf{F}_k \equiv \mathbf{F}(\mathbf{m}_k)$ and $\mathbf{f}_k \equiv \mathbf{f}(\mathbf{m}_k)$. The real positive quantities $\varepsilon_k$ can be fixed, after some trial and error, by accurate linear search, or by using a linearized approximation that simply gives$^{24}$ $\varepsilon_k \approx 1$. [END OF EXAMPLE.]

The algorithm 113 is usually called a 'quasi-Newton algorithm'. This name is not well chosen: a Newton method applied to minimization of a misfit function $S(\mathbf{m})$ would be a method using the second derivatives of $S(\mathbf{m})$, and thus the derivatives $H_{\alpha\beta}^i = \frac{\partial^2 I^i}{\partial m^\alpha \partial m^\beta}$, that are not computed (or not estimated) when using this algorithm. It is just a steepest descent algorithm with a nontrivial definition of the metric in the working space. In this sense it belongs to the wider class of 'variable metric methods', not discussed in this article.

## 7.5 Estimating Posterior Uncertainties

In the Gaussian context, the Gaussian probability density that is tangent to $\sigma_m(\mathbf{m})$ has its center at the point given by the iterative algorithm

$$\mathbf{m}_{k+1} = \mathbf{m}_k - \varepsilon_k \left( \mathbf{C}_M \mathbf{F}_k^t \mathbf{C}_D^{-1} (\mathbf{f}_k - \mathbf{d}_{\text{obs}}) + (\mathbf{m}_k - \mathbf{m}_{\text{prior}}) \right) \quad , \tag{114}$$

(equation 111) or, equivalently, by the iterative algorithm

$$\mathbf{m}_{k+1} = \mathbf{m}_k - \varepsilon_k \left( \mathbf{F}_k^t \mathbf{C}_D^{-1} \mathbf{F}_k + \mathbf{C}_M^{-1} \right)^{-1} \left( \mathbf{F}_k^t \mathbf{C}_D^{-1} (\mathbf{f}_k - \mathbf{d}_{\text{obs}}) + \mathbf{C}_M^{-1} (\mathbf{m}_k - \mathbf{m}_{\text{prior}}) \right) \tag{115}$$

(equation 113). The covariance of the tangent gaussian is

$$\widetilde{\mathbf{C}}_M \approx \left( \mathbf{F}_\infty^t \mathbf{C}_D^{-1} \mathbf{F}_\infty + \mathbf{C}_M^{-1} \right)^{-1} \quad , \tag{116}$$

where $\mathbf{F}_\infty$ refers to the value of the matrix of partial derivatives at the convergence point.

## 7.6 Some Comments on the Use of Deterministic Methods

### 7.6.1 Linear, Weakly Nonlinear and Nonlinear Problems

There are different degrees of nonlinearity. Figure 9 illustrates four domains of nonlinearity, calling for different optimization algorithms. In this figure the abscissa symbolically represents the model space, and the ordinate represents the data space. The gray oval represents the combination of prior information on the model parameters, and information from the observed data$^{25}$. It is the probability density $\rho(\mathbf{d}, \mathbf{m}) = \rho_d(\mathbf{d}) \rho_m(\mathbf{m})$. seen elsewhere.

To fix ideas, the oval suggests here a Gaussian probability, but our distinction between problems according to their nonlinearity will not depend fundamentally on this.

$^{22}$As shown in Tarantola (1987), if $\gamma_k$ is the direction of steepest ascent at point $\mathbf{m}_k$, i.e., $\gamma_k = \mathbf{C}_M \mathbf{F}_k^t \mathbf{C}_D^{-1} (\mathbf{f}_k - \mathbf{d}_{\text{obs}}) + (\mathbf{m}_k - \mathbf{m}_{\text{prior}})$, then, a local linearized approximation for the optimal $\varepsilon_k$ gives $\varepsilon_k = \frac{\gamma_k^t \mathbf{C}_M^{-1} \gamma_k}{\gamma_k^t (\mathbf{F}_k^t \mathbf{C}_D^{-1} \mathbf{F}_k + \mathbf{C}_M^{-1}) \gamma_k}$.

$^{23}$The 'best estimator' of $\widetilde{\mathbf{C}}_M$ is

$$\widetilde{\mathbf{C}}_M \approx \left( \mathbf{F}_k^t \mathbf{C}_D^{-1} \mathbf{F}_k + \mathbf{C}_M^{-1} \right)^{-1} \quad . \tag{112}$$

See, e.g., Tarantola (1987)

$^{24}$While a sensible estimation of the optimal values of the real positive quantities $\varepsilon_k$ is crucial for the algorithm 111, they can in many usual circumstances be dropped from the algorithm 113.

$^{25}$The gray oval is the product of the probability density over the model space, representing the prior information, and the probability density over the data space representing the experimental results.

32