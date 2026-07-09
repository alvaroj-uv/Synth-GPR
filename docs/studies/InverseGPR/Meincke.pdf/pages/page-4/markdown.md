MEINCKE: LINEAR GPR INVERSION

2715

characteristic $\mathbf{R}(\mathbf{K}, \omega)$ of the receiving antenna, the output $s_o$ of this antenna can be written as

$$\begin{aligned} s_o(\mathbf{r}_r, \omega) &= \frac{\omega^2 \mu_0^2}{64\pi^4} \int_{-\infty}^{\infty} d^2\mathbf{K} \int_{-\infty}^{\infty} d^2\mathbf{K}' \\ &\quad \cdot \exp\left(i \left[ (\mathbf{k}_0(\mathbf{K}, \omega) + \mathbf{k}_0(\mathbf{K}', \omega)) \cdot \mathbf{r}_r + \mathbf{k}_0(\mathbf{K}', \omega) \cdot \mathbf{r}_\Delta \right]\right) \\ &\quad \cdot \mathbf{R}(\mathbf{K}, \omega) \cdot \tilde{\mathbf{F}}(\mathbf{K}, \omega) \\ &\quad \cdot \tilde{\mathbf{J}}_{s_i}(-\mathbf{k}_0(\mathbf{K}', \omega)) \cdot \tilde{\mathbf{F}}(\mathbf{K}', \omega) \\ &\quad \cdot \int_{z' < 0} d^3\mathbf{r}' O(\mathbf{r}', \omega) \\ &\quad \cdot \exp\left(-i \left[ \mathbf{k}_1(\mathbf{K}, \omega) + \mathbf{k}_1(\mathbf{K}', \omega) \right] \cdot \mathbf{r}'\right). \end{aligned} \quad (8)$$

The plane-wave characteristic $\mathbf{R}(\mathbf{K}, \omega)$ is defined such that $\mathbf{R}(\mathbf{K}, \omega) \cdot \mathbf{E}(\mathbf{K}, \omega)$ is the output when the receiving antenna is located at $\mathbf{r} = 0$ and the incident electric field is the plane wave $\mathbf{E}(\mathbf{K}, \omega) \exp(i\mathbf{k}_0(\mathbf{K}, \omega) \cdot \mathbf{r})$ with $\mathbf{k}_0(\mathbf{K}, \omega) \cdot \mathbf{E}(\mathbf{K}) = 0$ [7], [8, p. 266].

Defining the FT $\tilde{s}_o(\mathbf{K}, z_r, \omega)$ with respect to the horizontal components $\mathbf{R}_r$ of the observation point as

$$\tilde{s}_o(\mathbf{K}, z_r, \omega) = \int_{-\infty}^{\infty} d^2\mathbf{R}_r s_o(\mathbf{r}_r, \omega) \exp(-i\mathbf{K} \cdot \mathbf{R}_r) \quad (9)$$

and using (8), the expression for $\tilde{s}_o$ can be written as

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &= \int_{-\infty}^{\infty} d^2\mathbf{K}' C(\mathbf{K}, \mathbf{K}', z_r, \omega) \\ &\quad \cdot \int_{z' < 0} d^3\mathbf{r}' O(\mathbf{r}', \omega) \\ &\quad \cdot \exp\left(-i \left[ \mathbf{k}_1(\mathbf{K} - \mathbf{K}', \omega) + \mathbf{k}_1(\mathbf{K}', \omega) \right] \cdot \mathbf{r}'\right) \end{aligned} \quad (10)$$

where

$$\begin{aligned} C(\mathbf{K}, \mathbf{K}', z_r, \omega) &= \frac{\omega^2 \mu_0^2}{16\pi^2} \mathbf{R}(\mathbf{K} - \mathbf{K}', \omega) \\ &\quad \cdot \tilde{\mathbf{F}}(\mathbf{K} - \mathbf{K}', \omega) \cdot \tilde{\mathbf{J}}_{s_i}(-\mathbf{k}_0(\mathbf{K}', \omega)) \\ &\quad \cdot \tilde{\mathbf{F}}(\mathbf{K}', \omega) \\ &\quad \cdot \exp\left(i \left[ (\gamma_0(\mathbf{K} - \mathbf{K}', \omega) + \gamma_0(\mathbf{K}', \omega)) z_r + \mathbf{k}_1(\mathbf{K}', \omega) \cdot \mathbf{r}_\Delta \right]\right). \end{aligned} \quad (11)$$

As shown in the Appendix of [4], the double integral over $\mathbf{K}'$ in (10) can be asymptotically evaluated when the object is located deep in the soil and the GPR antennas are close to the interface to yield

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &\sim D(\mathbf{K}, z_r, \omega) \\ &\quad \cdot \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' O_1(\mathbf{r}', \omega) \\ &\quad \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(-i \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \end{aligned} \quad (12)$$

with $O(\mathbf{r}', \omega) = O_1(\mathbf{r}', \omega)/z' = \Delta\sigma_1(\mathbf{r}') - i\omega\Delta\epsilon_1(\mathbf{r}') \cdot \mathbf{r}' = \mathbf{R}' + \mathbf{z} z'$, and

$$\begin{aligned} D(\mathbf{K}, z_r, \omega) &= \frac{i\omega^2 \mu_0^2}{64\pi k_1(\omega)} \left( 4k_1^2(\omega) - |\mathbf{K}|^2 \right) \\ &\quad \cdot \mathbf{R}\left(\frac{1}{2}\mathbf{K}, \omega\right) \cdot \tilde{\mathbf{F}}\left(\frac{1}{2}\mathbf{K}, \omega\right) \\ &\quad \cdot \tilde{\mathbf{J}}_{s_i}\left(-\mathbf{k}_0\left(\frac{1}{2}\mathbf{K}, \omega\right)\right) \cdot \tilde{\mathbf{F}}\left(\frac{1}{2}\mathbf{K}, \omega\right) \\ &\quad \cdot \exp\left(i \left[ \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \left(z_r + \frac{z_\Delta}{2} + \frac{1}{2}\mathbf{K} \cdot \mathbf{R}_\Delta \right]\right)\right). \end{aligned} \quad (13)$$

Equation (12) constitutes the 3-D forward model to be inverted in Section III. Although this forward model is derived using the assumption that the object is deep in the soil, it remains valid for surprisingly shallow objects. In [4] it is shown through numerical investigations that inversion schemes based on (12) give accurate images of objects buried just two center wavelengths from the interface. Unfortunately, the asymptotic evaluation in the Appendix of [4] becomes too inaccurate for $|\mathbf{K}| > 2\text{Re}k_1(\omega)$, and the forward model (12) should therefore only be used when $|\mathbf{K}| < 2\text{Re}k_1(\omega)$. Physically, this means that the forward model does include some of the evanescent plane waves in the air but it does not include any evanescent plane waves in the soil.

### III. INVERSION

To carry out the inversion, it is assumed that $\omega\Delta\epsilon \gg \Delta\sigma$ over the frequency interval of consideration $\omega_{\min} < \omega < \omega_{\max}$ (the case in which $\omega\Delta\epsilon \ll \Delta\sigma$ is dealt with in Section III-F). Then $O_1(\mathbf{r}') \approx -i\omega\Delta\epsilon_1(\mathbf{r}')$ and the forward model (12) can be written as

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &= (\mathcal{L}\Delta\epsilon_1)(\mathbf{K}, z_r, \omega) \\ &= -i\omega D(\mathbf{K}, z_r, \omega) \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \\ &\quad \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(-i \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \\ &\quad \cdot \Delta\epsilon_1(\mathbf{r}') \end{aligned} \quad (14)$$

where $\mathcal{L}: U \to V$ is a linear operator mapping $U$ into $V$. $U$ is the space of square integrable functions of position $\mathbf{r}'$ confined within $z' < 0$. $V$ is the space of square integrable functions defined on $\{(\mathbf{K}, \omega)|\omega_{\min} < \omega < \omega_{\max} \wedge |\mathbf{K}| < 2\text{Re}k_1(\omega)\}$. The inner products in $U$ and $V$ are defined in the usual way

$$\begin{aligned} \langle\Delta\epsilon_1, \Delta\epsilon_2\rangle_U &= \int_{z<0} d^3\mathbf{r} \Delta\epsilon_1^*(\mathbf{r}) \Delta\epsilon_2(\mathbf{r}) \\ \langle\tilde{s}_{o1}, \tilde{s}_{o2}\rangle_V &= \int_{\omega_{\min}}^{\omega_{\max}} d\omega \\ &\quad \cdot \int_{|\mathbf{K}| < 2\text{Re}k_1(\omega)} d^2\mathbf{K} \\ &\quad \cdot \tilde{s}_{o1}^*(\mathbf{K}, \omega) \tilde{s}_{o2}(\mathbf{K}, \omega) \end{aligned} \quad (15)$$

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.