2716

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

where * denotes the complex conjugation. Introducing $K_m = 2\text{Re}k_1(\omega_{\max})$, it is seen that if $|\mathbf{K}| > K_m$, then $\tilde{s}_o(\mathbf{K}, \omega) = 0$ for $\omega_{\min} < \omega < \omega_{\max}$.

Due to the compactness of the kernel in the integral equation (14), the solution $\Delta\epsilon_1$ of the inverse problem defined in (14) is unstable [9], [10], that is, the solution is highly sensitive to noise in the radar data $\tilde{s}_o$. Regularization is therefore needed, in particular when dealing with noisy data, to obtain a stable and useful solution. In this work, Tikhonov regularization is applied and hence, a minimization problem of the form

$$\min_{\Delta\epsilon_1} \left( \|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2^2 + \lambda^2 \|\Delta\epsilon_1\|_2^2 \right) \quad (17)$$

is considered. This problem can also be formulated as $\min_{\Delta\epsilon_1} \|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2$ subject to $\|\Delta\epsilon_1\|_2 < \eta$, where $\eta$ depends on $\lambda$ [9, p. 85]. The regularization parameter $\lambda$ in (17) controls the amount of filtering applied to obtain the solution. The larger the value of $\lambda$, the more filtering. It is obvious that there exists an optimum value of $\lambda$—if $\lambda$ is too small, the residual norm $\|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2$ is small but the norm $\|\Delta\epsilon_1\|_2$ is too large because the solution is affected by noise. If $\lambda$ is too large on the other hand, the norm $\|\Delta\epsilon_1\|_2$ is small but the residual norm is too large. In fact, when $\lambda$ is large the high spatial frequencies of the solution $\Delta\epsilon_1$ are efficiently damped. Consequently, the spatial bandwidth of the solution is determined by $\lambda$. A discussion on the difficulties in choosing the optimum $\lambda$ for the inversion scheme of this paper is found in Section III-C.

The minimization problem (17) could at this stage be solved by discretizing the continuous operator $\mathcal{L}$ such that it becomes a matrix $A$ and then using standard techniques for solving discrete ill-posed problems by Tikhonov regularization [9, Section 5.1]. However, in this way the matrix $A$ becomes unpractically large and also, the advantage of having the operator in the convenient explicit form (14) is not taken into account. Therefore, the operator $\mathcal{L}$ is here kept in continuous form and in line with the procedure in [5], [6], the minimization problem (17) is solved by applying the Tikhonov-regularized pseudo-inverse operator [11, p. 88]

$$\Delta\epsilon_1 = \mathcal{L}^\dagger = \left( \mathcal{L}\mathcal{L}^\dagger + \lambda^2 I \right)^{-1} \tilde{s}_o \quad (18)$$

where the adjoint operator $\mathcal{L}^\dagger$ defined by $\langle \tilde{s}_o, \mathcal{L}\Delta\epsilon_1 \rangle_V = \langle \mathcal{L}^\dagger \tilde{s}_o, \Delta\epsilon_1 \rangle_U$ is

$$\begin{aligned} (\mathcal{L}^\dagger \tilde{s}_o)(t') &= U(-z') \int_{\omega_{\min}}^{\omega_{\max}} d\omega i \omega \\ &\quad \cdot \int_{|\mathbf{K}| < 2\text{Re}k_1(\omega)} d^2\mathbf{K} D^*(\mathbf{K}, z_r, \omega) \exp(i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \tilde{s}_o(\mathbf{K}, z_r, \omega) \end{aligned} \quad (19)$$

and the unit step function $U(-z')$ serves as a masking function. It is seen that when applying $\mathcal{L}^\dagger$ to $\tilde{s}_o$, the output $s_o$ at the plane $z = z_r$ is backpropagated to the plane $z = z'$. To proceed, the filtered data $\tilde{s}_o^f$ are introduced as the solution to

$$\left( \mathcal{L}\mathcal{L}^\dagger + \lambda^2 I \right) \tilde{s}_o^f = \tilde{s}_o. \quad (20)$$

The spatial bandwidth of the filtered data is assumed to be the same as that of $\tilde{s}_o$, that is, $\tilde{s}_o^f(\mathbf{K}, \omega) = 0$ for $|\mathbf{K}| > 2\text{Re}k_1(\omega)$. Using the definition (20) along with (18), the contrast in permittivity is obtained from

$$\Delta\epsilon_1 = \mathcal{L}^\dagger \tilde{s}_o^f. \quad (21)$$

Hence, by solving (18) using the solution steps (20) and (21), the data are first filtered and then backpropagated to obtain the sought-for function $\Delta\epsilon_1$. In Section III-B it is shown how a priori information can be incorporated to give a better estimate of the object function.

The backpropagation (19) can be easily and efficiently calculated using fast Fourier transforms (FFTs). The filtering, on the other hand, is more complicated. The next section is devoted to this filtering step.

A. Filtering

The term $\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f$ in the filtering step (20) can be explicitly expressed as

$$\begin{aligned} (\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f)(\mathbf{K}, \omega) &= \omega D(\mathbf{K}, z_r, \omega) \\ &\quad \cdot \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \int_{\omega_{\min}}^{\omega_{\max}} d\omega' \omega' \\ &\quad \cdot \int_{|\mathbf{K}'| < 2\text{Re}k_1(\omega')} d^2\mathbf{K}' D^*(\mathbf{K}', z_r, \omega') \\ &\quad \cdot \exp(i[\mathbf{K}' - \mathbf{K}] \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(i \left[ \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2} \right. \right. \\ &\quad \left. \left. - \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \right] z' \right) \\ &\quad \cdot \tilde{s}_o^f(\mathbf{K}', z_r, \omega'). \end{aligned} \quad (22)$$

Using the fact that there is loss in the soil, $\text{Im}(k_1(\omega)) > 0$ and the integrations in (22) over $\mathbf{R}'$ and $z'$ can be evaluated to yield $(2\pi)^2 i \delta(\mathbf{K} - \mathbf{K}') / (\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2^*})$. By subsequently evaluating the integration over $\mathbf{K}'$, the relation

$$\begin{aligned} (\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f)(\mathbf{K}, \omega) &= (2\pi)^2 i \omega D(\mathbf{K}, z_r, \omega) \int_{\omega_{\min}}^{\omega_{\max}} d\omega' \omega' \\ &\quad \cdot D^*(\mathbf{K}, z_r, \omega') \frac{U(2\text{Re}k_1(\omega') - |\mathbf{K}|) \tilde{s}_o^f(\mathbf{K}, \omega')}{\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}|^2}} \end{aligned} \quad (23)$$

is obtained. When inserting (23) into (20), an integral equation is obtained for the determination of the filtered data $\tilde{s}_o^f(\mathbf{K}, \omega)$ for each $\mathbf{K}$, satisfying $|\mathbf{K}| \leq K_m$, where $K_m$ is defined following (16)$^2$. To solve this integral equation numerically it must be transformed into a matrix equation by discretization. There are many ways to discretize such an integral equation. In this case, the discretization method should be chosen such that the resulting matrix A is self adjoint (Hermitian). The reason for this is that A reflects the self-adjoint operator $\mathcal{L}\mathcal{L}^\dagger$. This requirement is satisfied by using a simple quadrature rule. To this end, first

$^2$If $|\mathbf{K}| > K_m$, then $\tilde{s}_o^f(\mathbf{K}, \omega) = 0$ for $\omega_{\min} < \omega < \omega_{\max}$ and no integral equation must be solved.

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.