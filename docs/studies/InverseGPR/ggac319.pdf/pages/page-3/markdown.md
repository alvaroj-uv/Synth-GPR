506 T. Qin, T. Bohlen and N. Allroggen

in the frequency domain.

$$\varepsilon(t) = \partial_t \Psi_t(t) \quad \text{with} \quad \Psi_t(t) = \varepsilon_s \left[ 1 - \frac{1}{L} \sum_{l=1}^L \left( 1 - \frac{\tau_{EI}}{\tau_{DI}} \right) e^{-t/\tau_{DI}} \right] H(t), \quad (4)$$

where $\tau_{EI}$ and $\tau_{DI}$ are the relaxation times of the electric field and displacement of the $l$th Debye model, respectively. $\tau_{EI} < \tau_{DI}$ for the $l$th mechanism. $\tau_{DI} = 1/(2\pi f_l)$ where $f_l$ is the relaxation frequency of the $l$th Debye peak and $L$ is the number of relaxation mechanisms. $H(t)$ is the Heaviside function. $\varepsilon_s$ is the static dielectric permittivity, corresponding to the permittivity in the frequency-independent media. Following the $\tau$-method proposed by Blanch *et al.* (1995), we define the permittivity attenuation $\tau_s = 1 - \tau_{EI}/\tau_{DI}$ as the attenuation level of the $l$th Debye model for EM waves. By doing so, $\Psi_t$ can be rewritten as

$$\Psi_t(t) = \varepsilon_s \left( 1 - \tau_s \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{DI}} \right) H(t). \quad (5)$$

In eq. (5), one can see that $\tau_s$ is independent of the $l$th Debye model, which means the same $\tau_s$ can be used for different Debye models. The newly defined variable is dimensionless ($0 \leq \tau_s < 1$) and more straightforward for identifying attenuation and dispersion caused by the complex permittivity. Using the Debye model, the convolution $\varepsilon * \partial_t \mathbf{E}$ becomes

$$\varepsilon(t) * \partial_t \mathbf{E} = \partial_t \Psi_t(t) * \partial_t \mathbf{E} = \varepsilon_s (1 - \tau_s) \partial_t \mathbf{E} + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{DI}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l. \quad (6)$$

Due to space limitations in the main content, we omit the computational process of convolution (readers can find details of eqs 6, 7, 10, and 11 in Appendix A). We introduce an ADE with a memory variable $\mathbf{r}_l$ of the $l$th mechanism corresponding to $\mathbf{E}$:

$$\partial_t \mathbf{r}_l = - \frac{\varepsilon_s \tau_s}{L \tau_{DI}^2} \mathbf{E} - \frac{1}{\tau_{DI}} \mathbf{r}_l. \quad (7)$$

Note that the definition of $\mathbf{r}_l$ is slightly different from the memory variable in Carcione (1996) and Bergmann *et al.* (1998). Similar to viscoelastic wave equations described in Bohlen (2002), we incorporate $\varepsilon_s$ into $\mathbf{r}_l$. By doing so, we can easily develop self-adjoint wave equations for GPR FWI (shown in Section 2.2). If only one Debye model is used, the memory variable $\mathbf{r}_l$ is related to the polarization current density $\mathbf{J}$ used in the microwave imaging of Papadopoulos & Rekanos (2011) by

$$\mathbf{J} = \mathbf{r}_l + \frac{\Delta \varepsilon}{\tau_{DI}} \mathbf{E} \quad \text{with} \quad \Delta \varepsilon = \varepsilon_s \tau_s \text{ and } l = 1. \quad (8)$$

On the other hand, the relaxation function of the conductivity can be described by a Kelvin–Voigt type model (Pipkin 2012) as

$$\sigma(t) = \partial_t \Psi_\sigma(t) \quad \text{with} \quad \Psi_\sigma(t) = \sigma_s [H(t) + \tau_\sigma \delta(t)], \quad (9)$$

where $\tau_\sigma$ is the relaxation time including the out-of-phase component of conductivity, $\sigma_s$ is the static conductivity, and $\delta(t)$ is the Dirac function. Then, the convolution $\sigma * \mathbf{E}$ becomes

$$\sigma(t) * \mathbf{E} = \partial_t \Psi_\sigma(t) * \mathbf{E} = \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}). \quad (10)$$

Hence, we replace two convolutions with multiplications

$$\varepsilon(t) * \partial_t \mathbf{E} + \sigma(t) * \mathbf{E} = \varepsilon_\infty^e \partial_t \mathbf{E} + \sigma_\infty^e \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l, \quad (11)$$

with the effective optical permittivity $\varepsilon_\infty^e$ and effective optical conductivity $\sigma_\infty^e$ as below:

$$\varepsilon_\infty^e = \varepsilon_s (1 - \tau_s) + \sigma_s \tau_\sigma, \quad \sigma_\infty^e = \sigma_s + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{DI}}. \quad (12)$$

The real effective permittivity and real effective conductivity with respect to the angular frequency $\omega$ are given by (Bergmann *et al.* 1998)

$$\begin{aligned} \varepsilon^e(\omega) &= \varepsilon_s \left( 1 - \tau_s \frac{1}{L} \sum_{l=1}^L \frac{\omega^2 \tau_{DI}^2}{1 + \omega^2 \tau_{DI}^2} \right) + \sigma_s \tau_\sigma, \\ \sigma^e(\omega) &= \sigma_s + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{\omega^2 \tau_{DI}^2}{1 + \omega^2 \tau_{DI}^2}. \end{aligned} \quad (13)$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022