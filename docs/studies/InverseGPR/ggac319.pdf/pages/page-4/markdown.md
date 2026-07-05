FWI of GPR data in frequency-dependent media

507

In fact, the effective optical parameters are the real effective parameters at infinite frequency. The attenuation factor $\alpha$, phase velocity $v$ and quality factor $Q$ are described as (Turner & Siggins 1994)

$$\alpha = \omega \left[ \frac{\mu \varepsilon^e(\omega)}{2} \left( \sqrt{1 + \tan^2 \delta} - 1 \right) \right]^{1/2},$$

$$v = \left[ \frac{\mu \varepsilon^e(\omega)}{2} \left( \sqrt{1 + \tan^2 \delta} + 1 \right) \right]^{-1/2},$$

$$Q = \tan^{-1} \delta, \tag{14}$$

where the loss tangent $\tan \delta = \sigma^e(\omega) / [\omega \varepsilon^e(\omega)]$. With $\tan \delta = 1$, we obtain the transition angular frequency $\omega_t = 2\pi f_t = \sigma^e(\omega_t) / \varepsilon^e(\omega_t)$ where $f_t$ is the transition frequency. In frequency-independent media where $\tau_e = 0$, $\sigma_\infty^e$ can be simplified to $\sigma_s$. Therefore the attenuation is determined by $\sigma_s$ alone, which is called conductivity attenuation. In frequency-dependent media, however, both $\sigma_s$ and $\tau_e$ contribute to attenuation. Based on eqs (7) and (11), we rewrite eq. (3) as

$$-\mu \partial_t \mathbf{H} - \nabla \times \mathbf{E} = 0,$$

$$-\nabla \times \mathbf{H} + \varepsilon_\infty^e \partial_t \mathbf{E} + \sigma_\infty^e \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l = -\mathbf{J}_e,$$

$$\mathbf{E} + \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e} \partial_t \mathbf{r}_l + \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} \mathbf{r}_l = 0, \quad l = 1, \dots, L. \tag{15}$$

We solve eq. (15) using the FDTD method of second order in time and fourth order in space. In the standard staggered grid of Yee (1966), the memory variable $\mathbf{r}_l$ locates at the same position of the electric field $\mathbf{E}$. The electrical parameters $\varepsilon_\infty^e$, $\varepsilon_s$, $\sigma_\infty^e$ and $\tau_e$ are averaged to the location of $\mathbf{E}$, while the magnetic parameter $\mu$ is averaged to the location of the magnetic field $\mathbf{H}$. The convolutional perfectly matched layer is included at the model boundary to absorb the outgoing waves (Roden & Gedney 2000).

Unlike eqs (6)–(8) in Papadopoulos & Rekanos (2011), eq. (15) uses the effective optical conductivity, resulting from different definitions of the polarization current density and memory variable (see eq. 8). Our modification in eq. (15) takes three advantages of the $\tau$-method (Blanch et al. 1995). First, we use one $\tau_e$ for all Debye models and set $\tau_{Dl}$ as a priori, which means less memory usage and computations in numerical modelling of EM waves than using $\tau_{Dl}$ and $\tau_{Dl}$ for $L$ Debye models. Second, if $\sigma_s \ll \sigma_\infty^e$, we can simply approximate a constant $Q$ by $Q \approx 2/\tau_e$. Thus, the attenuation is similar to a linear function of frequency and the simulator can account for the waveform distortion of EM waves (see Section 3 for an example). Third, we use only one $\tau_e$ in eqs (13) and (14) to quantify the magnitude of attenuation and dispersion introduced by complex permittivity, which is intuitive and reduces the number of parameters reconstructed by frequency-dependent GPR FWI in Section 2.2.

For convenience, we express eq. (15) in a matrix–vector formalism

$$\mathbf{M}_1 \partial_t \mathbf{u} + \mathbf{M}_2 \mathbf{u} - \mathbf{A} \mathbf{u} = \mathbf{s}, \tag{16}$$

with

$$\mathbf{u} = \left( H_x, H_y, H_z, E_x, E_y, E_z, r_{x1}, r_{y1}, r_{z1}, \dots, r_{xL}, r_{yL}, r_{zL} \right)^T,$$

$$\mathbf{s} = \left( 0, 0, 0, -J_{xx}, -J_{yy}, -J_{zz}, 0, 0, 0, \dots, 0, 0, 0 \right)^T,$$

$$\text{diag}(\mathbf{M}_1) = \left( -\mu, -\mu, -\mu, \varepsilon_\infty^e, \varepsilon_\infty^e, \varepsilon_\infty^e, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \dots, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e} \right),$$

$$\mathbf{M}_2 = \begin{pmatrix} 0_3 & 0_3 & 0_3 & \dots & 0_3 \\ 0_3 & \sigma_\infty^e I_3 & I_3 & \dots & I_3 \\ 0_3 & I_3 & \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} I_3 & & \\ \dots & \dots & & \ddots & \\ 0_3 & I_3 & & & \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} I_3 \end{pmatrix}, \quad \mathbf{A} = \begin{pmatrix} 0_3 & D & 0_3 & \dots & 0_3 \\ D & 0_3 & 0_3 & \dots & 0_3 \\ 0_3 & 0_3 & 0_3 & \dots & 0_3 \\ \dots & \dots & & \ddots & \\ 0_3 & 0_3 & & & 0_3 \end{pmatrix},$$

$$D = \begin{pmatrix} 0 & -\partial_z & \partial_y \\ \partial_z & 0 & -\partial_x \\ -\partial_y & \partial_x & 0 \end{pmatrix} = D_1 \partial_x + D_2 \partial_y + D_3 \partial_z, \quad D_i^* = D_i^T = -D_i,$$

$$D_1 = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & -1 \\ 0 & 1 & 0 \end{pmatrix}, \quad D_2 = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 0 & 0 \\ -1 & 0 & 0 \end{pmatrix}, \quad D_3 = \begin{pmatrix} 0 & -1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}, \quad D^T = D,$$

$$D^* = (D_i \partial_i)^* = -D_i^* \partial_i = D_i \partial_i = D \quad \Rightarrow \quad \mathbf{A}^* = \mathbf{A}, \tag{17}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022