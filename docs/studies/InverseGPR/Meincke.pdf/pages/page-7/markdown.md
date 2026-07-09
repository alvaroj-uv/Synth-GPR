2718

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

and that the object must be buried a few center wavelengths from the interface. As illustrated in Section IV below, a high image quality is obtained despite these assumptions. Third, the frequency $\omega$ is assumed continuous in (14) and thereby, the filtering step consists of solving Fredholm integral equations of the first kind. It is thus evident that the accuracy of the filtering depends on the discretization method chosen to solve these integral equations. In [6], on the other hand, $\omega$ is assumed discrete from the very beginning and therefore, one specific discretization method is chosen and the fact that the filtering step is an integral equation does not become clear.

D. No Loss in the Soil

If $\sigma_1 = 0$, that is, the soil is lossless, the step from (22) to (23) does not hold. Instead, the integrations over $\mathbf{R}'$ and $z'$ in the expression (22) for $\mathcal{L}\mathcal{L}^\dagger$ can be evaluated to yield $8\pi^3\delta(\mathbf{K}-\mathbf{K}')\delta(\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2})$. Using the relation $\delta(f(\omega)) = \delta(\omega - \omega_0)/|f'(\omega_0)|$, where $f(\omega_0) = 0$ and subsequently integrating over $\mathbf{K}'$ and $\omega'$ yields

$$(\mathcal{L}\mathcal{L}^\dagger \tilde{s}_0')(\mathbf{K}, \omega) = \frac{2\pi^3\omega^2}{k_1(\omega)\sqrt{\mu_0\epsilon_1}} |D(\mathbf{K}, z_r, \omega)|^2 \cdot \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \tilde{s}_0'(\mathbf{K}, \omega). \quad (31)$$

Hence, according to (30), the expression for $\Delta\epsilon = z\Delta\epsilon_1$ is as (32), shown at the bottom of the page. This result is identical to the one presented in [4, Eq. 20].

E. 2.5-D Case

Assume now that the object function is independent of $x$. This would be the case, for instance, when the buried object is an infinitely long $\hat{x}$-directed pipe. The solution steps (20) and (30) still hold in this case but to apply the other expressions in Section III, the relation $\mathbf{K} = \hat{y}k_y$ must be enforced and the expression (19) for the adjoint operator must be replaced by

$$(\mathcal{L}^\dagger \tilde{s}_0)(y', z') = 2\pi U(-z') \cdot \int_{\omega_{\min}}^{\omega_{\max}} d\omega \, i\omega \int_{|k_y|<2\pi\epsilon k_1(\omega)} dk_y D^*(k_y, z_r, \omega) \cdot \exp(ik_y y') \cdot \exp\left(i\sqrt{4k_1^2(\omega) - k_y^2} z'\right) \tilde{s}_0(k_y, z_r, \omega) \quad (33)$$

where $\tilde{s}_0(k_y, z_r, \omega)$ is the 1-D FT of the radar data defined by

$$\tilde{s}_0(k_y, z_r, \omega) = \int_{-\infty}^{\infty} dy \, s_0(y, z_r, \omega) \exp(-ik_y y) \quad (34)$$

and $D(k_y, z_r, \omega)$ is obtained from (13) with $\mathbf{K} = \hat{y}k_y$.

As an example, assume that the transmitting and receiving antennas are $\hat{x}$-directed ideal dipoles such that $\mathbf{R} = \hat{x}$ and $\mathbf{J} = I(\omega)\hat{x}$. Assume also that the antennas have the same $z$ and $x$ coordinates, i.e., $x_\Delta = z_\Delta = 0$. In this case, $D(k_y, z_r, \omega)$ becomes

$$D(k_y, z_r, \omega) = \frac{i\omega^2\mu_0^2 I(\omega)(4k_1^2(\omega) - k_y^2)}{4\pi k_1(\omega)\left(\sqrt{4k_0^2(\omega) - k_y^2} + \sqrt{4k_1^2(\omega) - k_y^2}\right)^2} \cdot \exp\left(i\left[\sqrt{4k_0^2(\omega) - k_y^2} z_r + \frac{1}{2}k_y y_\Delta\right]\right). \quad (35)$$

F. Case in Which $\omega\Delta\epsilon \ll \Delta\sigma$

When $\omega\Delta\epsilon \ll \Delta\sigma$ the object function can be approximated as $O_1(\mathbf{r}') \approx \Delta\sigma_1(\mathbf{r}')$ and the forward model (12) becomes

$$\tilde{s}_0(\mathbf{K}, z_r, \omega) = (\mathcal{L}\Delta\sigma_1)(\mathbf{K}, z_r, \omega) = D(\mathbf{K}, z_r, \omega) \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \cdot \exp\left(-i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \Delta\sigma_1(\mathbf{r}'). \quad (36)$$

The image of $\Delta\sigma_1$ is obtained using

$$\Delta\sigma_1 = 2\text{Re}(\mathcal{L}^\dagger \tilde{s}_0') \quad (37)$$

where the adjoint operator $\mathcal{L}^\dagger$ is

$$(\mathcal{L}^\dagger \tilde{s}_0)(\mathbf{r}') = U(-z') \cdot \int_{\omega_{\min}}^{\omega_{\max}} d\omega \int_{|\mathbf{K}|<2\pi\epsilon k_1(\omega)} d^2\mathbf{K} D^*(\mathbf{K}, z_r, \omega) \cdot \exp(i\mathbf{K} \cdot \mathbf{R}') \cdot \exp\left(i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \tilde{s}_0(\mathbf{K}, z_r, \omega). \quad (38)$$

In addition, in the matrix (25), $R_{pp'}$ must be

$$R_{pp'}(\mathbf{K}) = (2\pi)^2 i D(\mathbf{K}, z_r, \omega_p) W_{pp'}(\mathbf{K}) + \delta_{pp'} \lambda^2 \quad (39)$$

$$\Delta\epsilon(\mathbf{r}) = \text{Re}\left[ \frac{64z(\mu_0\epsilon_1)^{3/2}}{\pi^2\mu_0^2} \int_{\omega_{\min}}^{\omega_{\max}} d\omega \int_{|\mathbf{K}|<2\epsilon_1(\omega)} d^2\mathbf{K} \tilde{s}_0(\mathbf{K}, \omega) \cdot \exp\left(i\mathbf{K} \cdot \left[\mathbf{R} - \frac{1}{2}\mathbf{R}_\Delta\right]\right) \cdot \frac{\exp\left(i\left[\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z - \sqrt{4k_0^2(\omega) - |\mathbf{K}|^2} (z_r + (1/2)z_\Delta)\right]\right)}{\omega(4k_1^2(\omega) - |\mathbf{K}|^2)^{3/2} \mathbf{R}((1/2)\mathbf{K}, \omega) \cdot \bar{\mathbf{F}}((1/2)\mathbf{K}, \omega) \cdot \bar{\mathbf{J}}_{s_1}(-k_0((1/2)\mathbf{K}, \omega)) \cdot \bar{\mathbf{F}}((1/2)\mathbf{K}, \omega)} \right]. \quad (32)$$

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.