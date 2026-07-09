Finally, we have seen examples suggesting that the conjunction of of the experimental information with the theoretical information corresponds exactly to the AND operation defined over the probability densities, to obtain the 'conjunction of information', as represented by the probability density

$$\sigma(\mathbf{m}, \mathbf{d}) = k \frac{\rho(\mathbf{m}, \mathbf{d}) \vartheta(\mathbf{m}, \mathbf{d})}{\mu(\mathbf{m}, \mathbf{d})} \quad \text{(conjunction of informations)} \quad , \tag{68}$$

with marginal probability densities

$$\sigma_m(\mathbf{m}) = \int_{\mathcal{D}} d\mathbf{d} \, \sigma(\mathbf{m}, \mathbf{d}) \quad ; \quad \sigma_d(\mathbf{d}) = \int_{\mathcal{M}} d\mathbf{m} \, \sigma(\mathbf{m}, \mathbf{d}) \quad . \tag{69}$$

**Example 15** *We may assume that the physical correlations between the parameters* $\mathbf{m}$ *and* $\mathbf{d}$ *are of the form*

$$\vartheta(\mathbf{m}, \mathbf{d}) = \vartheta_{D|M}(\mathbf{d}|\mathbf{m}) \, \vartheta_M(\mathbf{m}) \quad , \tag{70}$$

*this expressing that a 'physical theory' gives, one the one hand, the conditional probability for* $\mathbf{d}$ *, given* $\mathbf{m}$ *, and on the other hand, the marginal probability density for* $\mathbf{m}$ *. See appendix C for more details. [END OF EXAMPLE.]*

**Example 16** *Many applications concern the special situation where we have*

$$\mu(\mathbf{m}, \mathbf{d}) = \mu_m(\mathbf{m}) \, \mu_d(\mathbf{d}) \quad ; \quad \rho(\mathbf{m}, \mathbf{d}) = \rho_m(\mathbf{m}) \, \rho_d(\mathbf{d}) \quad . \tag{71}$$

*In this case, equations 68–69 give*

$$\sigma_m(\mathbf{m}) = k \frac{\rho_m(\mathbf{m})}{\mu_m(\mathbf{m})} \int_{\mathcal{D}} d\mathbf{d} \, \frac{\rho_d(\mathbf{d}) \, \vartheta(\mathbf{m}, \mathbf{d})}{\mu_d(\mathbf{d})} \quad . \tag{72}$$

*If equation 70 holds, then*

$$\sigma_m(\mathbf{m}) = k \, \rho_m(\mathbf{m}) \, \frac{\vartheta_m(\mathbf{m})}{\mu_m(\mathbf{m})} \int_{\mathcal{D}} d\mathbf{d} \, \frac{\rho_d(\mathbf{d}) \, \vartheta_{D|M}(\mathbf{d} \mid \mathbf{m})}{\mu_d(\mathbf{d})} \quad . \tag{73}$$

*Finally, if the simplification* $\vartheta_M(\mathbf{m}) = \mu_m(\mathbf{m})$ *arises (see appendix C for an illustration) then,*

$$\sigma_m(\mathbf{m}) = k \, \rho_m(\mathbf{m}) \int_{\mathcal{D}} d\mathbf{d} \, \frac{\rho_d(\mathbf{d}) \, \vartheta(\mathbf{d}|\mathbf{m})}{\mu_d(\mathbf{d})} \quad . \tag{74}$$

[END OF EXAMPLE.]

**Example 17** *In the context of the previous example, assume that observational uncertainties are Gaussian,*

$$\rho_d(\mathbf{d}) = k \, \exp \left( -\frac{1}{2} \, (\mathbf{d} - \mathbf{d}_{\text{obs}})^t \, \mathbf{C}_D^{-1} \, (\mathbf{d} - \mathbf{d}_{\text{obs}}) \right) \quad . \tag{75}$$

*Note that the limit for infinite variances gives the homogeneous probability density* $\mu_d(\mathbf{d}) = k$ *. Furthermore, assume that uncertainties in the physical law are also Gaussian:*

$$\vartheta(\mathbf{d}|\mathbf{m}) = k \, \exp \left( -\frac{1}{2} \, (\mathbf{d} - \mathbf{f}(\mathbf{m}))^t \, \mathbf{C}_T^{-1} \, (\mathbf{d} - \mathbf{f}(\mathbf{m})) \right) \quad . \tag{76}$$

*Here 'the physical theory says' that the data values must be 'close' to the 'computed values'* $\mathbf{f}(\mathbf{m})$ *, with a notion of closeness defined by the 'theoretical covariance matrix'* $\mathbf{C}_T$ *. As demonstrated in Tarantola (1987, page 158), the integral in equation 74 can be analytically evaluated, and gives*

$$\int_{\mathcal{D}} d\mathbf{d} \, \frac{\rho_d(\mathbf{d}) \, \vartheta(\mathbf{d}|\mathbf{m})}{\mu_d(\mathbf{d})} = k \, \exp \left( -\frac{1}{2} \, (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}})^t \, (\mathbf{C}_D + \mathbf{C}_T)^{-1} \, (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}}) \right) \quad . \tag{77}$$

*This shows that when using the Gaussian probabilistic model, observational and theoretical uncertainties combine through addition of the respective covariance operators (a nontrivial result). [END OF EXAMPLE.]*

25