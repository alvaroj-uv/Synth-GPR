We do not mean that the relation is necessarily explicit. Given $\mathbf{m}$ we may need to solve a complex system of equations in order to get $\mathbf{d}$, but this nevertheless defines a function $\mathbf{m} \to \mathbf{d} = \mathbf{f}(\mathbf{m})$.

At this point, given the probability density $\rho(\mathbf{m}, \mathbf{d})$ and given the relation $\mathbf{d} = \mathbf{f}(\mathbf{m})$, we can define the associated conditional probability density $\rho_{m|d(m)}(\mathbf{m}|\mathbf{d} = \mathbf{f}(\mathbf{m}))$. We could here use the more general definition of conditional probability density of appendix B, but let us simplify the text by using a simplification assumption: that the total parameter space $(\mathcal{M}, \mathcal{D})$ is just the cartesian product $\mathcal{M} \times \mathcal{D}$ of the model parameter space $\mathcal{M}$ times the space of directly observable parameters (or 'data space') $\mathcal{D}$. Then, rather than a general metric in the total space, we have a metric $\mathbf{g}_m$ over the model parameter space $\mathcal{M}$ and a metric $\mathbf{g}_d$ over the data space, and the total metric is just the Cartesian product of the two metrics. In particular, then, the total volume element in the space, $dV(\mathbf{m}, \mathbf{d})$ is just the product of the two volume elements in the model parameter space and the data space: $dV(\mathbf{m}, \mathbf{d}) = dV_m(\mathbf{m}) dV_d(\mathbf{d})$. Most of inverse problems satisfy this assumption$^{13}$. In this setting, the formulas of section 2.4 are valid.

### 4.5.2 Inverse Problems

In the $(\mathcal{M}, \mathcal{D}) = \mathcal{M} \times \mathcal{D}$ space, we have the probability density $\rho(\mathbf{m}, \mathbf{d})$ and we have the hypersurface defined by the relation $\mathbf{d} = \mathbf{f}(\mathbf{m})$. The natural way to 'compose' these two kinds of information is by defining the conditional probability density induced by $\rho(\mathbf{m}, \mathbf{d})$ on the hypersurface $\mathbf{d} = \mathbf{f}(\mathbf{m})$,

$$\sigma_m(\mathbf{m}) \equiv \rho_{m|d(m)}(\mathbf{m}|\mathbf{d} = \mathbf{f}(\mathbf{m})) \text{ ,} \tag{44}$$

this giving (see equation 17)

$$\sigma_m(\mathbf{m}) = k \rho(\mathbf{m}, \mathbf{f}(\mathbf{m})) \left. \frac{\sqrt{\det(\mathbf{g}_m + \mathbf{F}^T \mathbf{g}_d \mathbf{F})}}{\sqrt{\det \mathbf{g}_m} \sqrt{\det \mathbf{g}_d}} \right|_{\mathbf{d}=\mathbf{f}(\mathbf{m})} \text{ ,} \tag{45}$$

where $\mathbf{F} = \mathbf{F}(\mathbf{m})$ is the matrix of partial derivatives, with components $F_{i\alpha} = \partial f_i / \partial m_\alpha$, where $\mathbf{g}_m$ is the metric in the model parameter space $\mathcal{M}$ and where $\mathbf{g}_d$ is the metric in the data space $\mathcal{D}$.

**Example 8** *Quite often, $\rho(\mathbf{m}, \mathbf{d}) = \rho_m(\mathbf{m}) \rho_d(\mathbf{d})$. Then, equation 45 can be written*

$$\sigma_m(\mathbf{m}) = k \rho_m(\mathbf{m}) \left. \left( \frac{\rho_d(\mathbf{d})}{\sqrt{\det \mathbf{g}_d}} \frac{\sqrt{\det(\mathbf{g}_m + \mathbf{F}^T \mathbf{g}_d \mathbf{F})}}{\sqrt{\det \mathbf{g}_m}} \right) \right|_{\mathbf{d}=\mathbf{f}(\mathbf{m})} \text{ .} \tag{46}$$

[END OF EXAMPLE.]

**Example 9** *If $\mathbf{F}^T \mathbf{g}_d \mathbf{F}$ is negligible compared to $\mathbf{g}_m$, then equation 46 reduces to*

$$\sigma_m(\mathbf{m}) = k \rho_m(\mathbf{m}) \left. \frac{\rho_d(\mathbf{d})}{\mu_d(\mathbf{d})} \right|_{\mathbf{d}=\mathbf{f}(\mathbf{m})} \text{ ,} \tag{47}$$

*where we have used $\mu_d(\mathbf{d}) = k \sqrt{\det \mathbf{g}_d(\mathbf{d})}$ (see rule 2). [END OF EXAMPLE.]*

**Example 10** *We examine here the simplification that we arrive at when assuming that the 'input' probability densities are Gaussian:*

$$\rho_m(\mathbf{m}) = k \exp \left( -\frac{1}{2} (\mathbf{m} - \mathbf{m}_{\text{prior}})^t \mathbf{C}_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) \right) \tag{48}$$

$$\rho_d(\mathbf{d}) = k \exp \left( -\frac{1}{2} (\mathbf{d} - \mathbf{d}_{\text{obs}})^t \mathbf{C}_D^{-1} (\mathbf{d} - \mathbf{d}_{\text{obs}}) \right) \text{ .} \tag{49}$$

*In this circumstance, quite often, it is the covariance operators $\mathbf{C}_M$ and $\mathbf{C}_D$ that are used to define the metrics over the spaces $\mathcal{M}$ and $\mathcal{D}$. Then, $\mathbf{g}_m = \mathbf{C}_M^{-1}$ and $\mathbf{g}_d = \mathbf{C}_D^{-1}$. Grouping some of the constant factors in the factor $k$, equation 45 becomes here*

$$\sigma_m(\mathbf{m}) =$$

$^{13}$It would be violated, for instance, if we use the pair of elastic parameters longitudinal wave velocity – shear wave velocity, as the volume element in the space of elastic wave velocities does not factorize (see appendix H).

21