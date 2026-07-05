If, on the contrary, it is $\sigma_v$ which tends to zero, then,

$$h_t(t) = k \ g( \ t, x(t) \ ) \quad . \tag{166}$$

These equations are to be compared with equations 153–155. We see that the result we obtain crucially depends on the ‘preparation’ of the particle. To combine the result of a measurement with a theory is not a simple matter.

Case $t = t(x)$

We leave as an exercise to the reader the solution of the same problem, but where the particles are prepared so that they desintegrate (or that they blink) at some position $x$ chosen homogeneously at random inside some (large) space interval.

## D Information Content

Shannon’s definition of information content (Shannon, 1948) of a discrete probability $I = \sum_i p_i \log p_i$ does not generalize into a definition of the information content of a probability density (the ‘definition’ $I = \int d\mathbf{x} \ f(\mathbf{x}) \ \log f(\mathbf{x})$ is not invariant under a change of variables). Rather, one may define the ‘Kullback distance’ (Kullback, 1967) from the probability density $g(\mathbf{x})$ to the probability density $f(\mathbf{x})$ as

$$I(f|g) = \int d\mathbf{x} \ f(\mathbf{x}) \log \frac{f(\mathbf{x})}{g(\mathbf{x})} \ . \tag{167}$$

This means in particular that we never know if a single probability density is, by itself, informative or not. The equation above defines the information gain when we pass from $g(\mathbf{x})$ to $f(\mathbf{x})$ ($I$ is always positive). But there is also an information gain when we pass from $f(\mathbf{x})$ to $g(\mathbf{x})$: $I(g|f) = \int d\mathbf{x} \ g(\mathbf{x}) \log \ g(\mathbf{x})/f(\mathbf{x})$ . One should note that (i) the ‘Kullback distance’ is not a distance (the distance from $f(\mathbf{x})$ to $g(\mathbf{x})$ does not equal the distance from $g(\mathbf{x})$ to $f(\mathbf{x})$ ); (ii) for the ‘Kullback distance’ $I(f|g) = \int d\mathbf{x} \ f(\mathbf{x}) \log \ f(\mathbf{x})/g(\mathbf{x})$ to be defined, the probability density $f(\mathbf{x})$ has to be ‘absolutely continuous’ with respect to $g(\mathbf{x})$ , which amounts to say that $f(\mathbf{x})$ can only be zero where $g(\mathbf{x})$ is zero. We have postulated that any probability density $f(\mathbf{x})$ is absolutely continuous with respect to the homogeneous probability distribution $\mu(\mathbf{x})$ , since the homogeneous probability distribution ‘fills the space’. Then one may use the convention that the information content of any probability density $f(\mathbf{x})$ is measured with respect to the homogeneous probability density:

$$I(f) \equiv f(f|\mu) = \int d\mathbf{x} \ f(\mathbf{x}) \log \frac{f(\mathbf{x})}{\mu(\mathbf{x})} \ . \tag{168}$$

The homogeneous probability density is then ‘noninformative’, $I(\mu) = I(\mu|\mu) = 0$ , but this is just by definition.

## E Example: Prior Information for a 1D Mass Density Model

Of course, the simplest example of a probability distribution is the Gaussian (or ‘normal’) distribution. Not many physical parameters accept the Gaussian as a probabilistic model (we have, in particular, seen that many positive parameters are Jeffreys parameters, for which the simplest consistent probability density is not the normal, but the log-normal probability density [see rule 8]), and we shall therefore consider the problem of describing a model consisting of a stack of horizontal layers with variable thickness and uniform mass density. The prior information is shown in figure 19, involving marginal distributions of the mass density and the layer thickness. Spatial statistical homogeneity is assumed, hence marginals are not dependent on depth in this example. Additionally, they are independent of neighbor layer parameters.

The model parameters consist of a sequence of thicknesses and a sequence of mass density parameters, $\mathbf{m} = \{\ell_1, \ell_2, \ldots, \ell_{NL}, \rho_1, \rho_2, \ldots, \rho_{NL}\}$ . The marginal prior probability densities for the layer thicknesses are all assumed to be identical and of the form (exponential probability density)

$$f(\ell) \ = \ \frac{1}{\ell_0} \ \exp \left( -\frac{\ell}{\ell_0} \right) \quad , \tag{169}$$

45