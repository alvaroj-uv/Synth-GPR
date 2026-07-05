98

A Summary of Probability and Statistics

we can compute $E[u]$, $E[u^2]$, etc. The second-order PDF involves two times, $t_1$ and $t_2$, and is the joint PDF of $U(t_1)$ and $U(t_2)$: $\rho_2(u_1, u_2; t_1, t_2)$. With this we can compute quantities such as:

$$E[u_1 u_2] = \int \int u_1 u_2 \rho_U(u_1, u_2; t_1, t_2) du_1 du_2.$$

It is relatively uncommon to go beyond second order statistical characterizations (means and covariances) and we will not do so in this class.

# Time versus statistical autocorrelation

Given a known function $u(t)$ (or this could be discrete samples of a known function $u(t_i)$), the time autocorrelation function of $u$ is defined as:

$$\tilde{\Gamma}_u(\tau) = \lim_{T \to \infty} \frac{1}{T} \int_{-T/2}^{T/2} u(t+\tau) u(t) dt.$$

This measures the similarity of $u(t+\tau)$ and $u(t)$ averaged over all time. Closely related is the statistical autocorrelation function. Let $U(t)$ be a random process. Implicitly the random process constitutes the set of all possible sample functions $u(t)$ and their associated probability measure.

$$\Gamma_u(t_1, t_2) \equiv E[u(t_1)u(t_2)] = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} u_2 u_1 \rho_U(u_1, u_2; t_1, t_2) du_1 du_2.$$

$\Gamma_u(t_1, t_2)$ measures the statistical similarity of $u(t_1)$ and $u(t_2)$ over the ensemble of all possible realizations of $U(t)$.

For stationary processes, $\Gamma_u(t_1, t_2)$ depends only on $\tau \equiv t_2 - t_1$. And for ergodic processes:

$$\tilde{\Gamma}(\tau) = \Gamma_u(\tau)$$

## 6.10 Probabilistic Information About Earth Models

In geophysics there is a large amount of a priori information that could be used to influence inverse calculations. Here, a priori refers to the assumption that this information is known independently of the data. Plausible geologic models can be based on rock outcrops, models of sedimentological deposition, subsidence, etc. There are also often in situ and laboratory measurements of rock properties that have a direct bearing on macroscopic seismic observations, such as porosity, permeability, crack orientation, etc. There are other, less quantitative, forms of information as well, the knowledge of experts for instance.

This prior information can be deterministic or probabilistic. Examples of deterministic information include: density is positive, wave velocity is positive (and less than the

0