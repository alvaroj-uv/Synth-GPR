## 6 Solving Inverse Problems (II): Monte Carlo Methods

### 6.1 Basic Equations

The starting point could be the explicit expression (equation 46) for $\sigma_m(\mathbf{m})$ given in section 4.5.2:

$$\sigma_m(\mathbf{m}) = k \rho_m(\mathbf{m}) L(\mathbf{m}) \quad . \tag{82}$$

where

$$L(\mathbf{m}) = \left. \left( \frac{\rho_d(\mathbf{d})}{\sqrt{\det \mathbf{g}_d(\mathbf{d})}} \frac{\sqrt{\det (\mathbf{g}_m(\mathbf{m}) + \mathbf{F}^T(\mathbf{m}) \mathbf{g}_d(\mathbf{d}) \mathbf{F}(\mathbf{m}))}}{\sqrt{\det \mathbf{g}_m(\mathbf{m})}} \right) \right|_{\mathbf{d}=\mathbf{f}(\mathbf{m})}. \tag{83}$$

In this expression the matrix of partial derivatives $\mathbf{F} = \mathbf{F}(\mathbf{m})$, with components $D_{i\alpha} = \partial f_i / \partial m_\alpha$, appears. The 'slope' $\mathbf{F}$ enters here because the steeper the slope for a given $\mathbf{m}$, the greater the accumulation of points we will have with this particular $\mathbf{m}$. This is because we use explicitly the analytic expression $\mathbf{d} = \mathbf{f}(\mathbf{m})$. One should realize that using the more general approach based on equation 68 of section 4.6.2, the effect is automatically accounted for, and there is no need to explicitly consider the partial derivatives.

Equation 82 has the standard form of a conjunction of two probability densities, and is therefore ready to be integrated in a Metropolis algorithm. But one should note that, contrary to many 'nonlinear' formulations of inverse problems, the partial derivatives $\mathbf{F}$ are needed even if we use a Monte Carlo method.

In some weakly nonlinear problems, we have $\mathbf{F}^T(\mathbf{m}) \mathbf{g}_d(\mathbf{d}) \mathbf{F}(\mathbf{m}) << \mathbf{g}_m(\mathbf{m})$ and, then, equation 83 becomes

$$L(\mathbf{m}) = \left. \frac{\rho_d(\mathbf{d})}{\mu_d(\mathbf{d})} \right|_{\mathbf{d}=\mathbf{f}(\mathbf{m})}, \tag{84}$$

where we have used $\mu_d(\mathbf{d}) = k \sqrt{\det \mathbf{g}_d(\mathbf{d})}$ (see rule 2).

This expression is also ready for use in the Metropolis algorithm. In this way sampling of the prior $\rho_m(\mathbf{m})$ is modified into a sampling of the posterior $\sigma_m(\mathbf{m})$, and the Metropolis Rule uses the 'Likelihood function' $L(\mathbf{m})$ to calculate acceptance probabilities.

### 6.2 Sampling the Homogeneous Probability Distribution

If we do not have an algorithm that samples the prior probability density directly, the first step in a Monte Carlo analysis of an inverse problem is to design a random walk that samples the model space according to the homogeneous probability distribution $\mu_m(\mathbf{m})$. In some cases this is easy, but in other cases only an algorithm (a *primeval random walk*) that samples an arbitrary (possibly constant) probability density $\psi(\mathbf{m}) \neq \mu_m(\mathbf{m})$ is available. Then the Metropolis Rule can be used to modify $\psi(\mathbf{m})$ into $\mu_m(\mathbf{m})$ (see section 3.4). This way of generating samples from $\mu_m(\mathbf{m})$ is efficient if $\psi(\mathbf{m})$ is close to $\mu_m(\mathbf{m})$, otherwise it may be very inefficient.

Once $\mu(\mathbf{m})$ can be sampled, the Metropolis Rule allows us to modify this sampling into an algorithm that samples the prior.

### 6.3 Sampling the Prior Probability Distribution

The first step in the Monte Carlo analysis is to temporarily 'switch off' the comparison between computed and observed data, thereby generating samples of the prior probability density. This allows us to verify statistically that the algorithm is working correctly, and it allows us to understand the prior information we are using. We will refer to a large collection of models representing the prior probability distribution as the 'prior movie' (in a computer screen, when the models are displayed one after the other, we have a 'movie'). The more models present in this movie, the more accurate representation of the prior probability density.

### 6.4 Sampling the Posterior Probability Distribution

If we now switch on the comparison between computed and observed data using, e.g., the Metropolis Rule for the actual equation 82, the random walk sampling the prior distribution is modified into a walk sampling the posterior distribution.

Since data rarely put strong constraints on the Earth, the 'posterior movie' typically shows that many different models are possible. But even though the models in the posterior movie may be quite different, all of them predict

27