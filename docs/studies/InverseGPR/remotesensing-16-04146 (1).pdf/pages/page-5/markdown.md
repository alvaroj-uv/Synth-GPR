Remote Sens. 2024, 16, 4146

5 of 19

$$\frac{\partial W_2(a, b)}{\partial P_{i,j}^{OT}} = C_{i,j} + \epsilon \log P_{i,j}^{OT} - \alpha_i - \beta_j = 0 \tag{8}$$

$$P_{i,j}^{OT} = e^{\alpha_i / \epsilon} e^{-C_{i,j} / \epsilon} e^{\beta_j / \epsilon} \tag{9}$$

Let $K = e^{-C_{i,j} / \epsilon}, u = e^{-\alpha / \epsilon}, v = e^{-\beta / \epsilon}$, then the transmission matrix can be represented as follows:

$$P^{OT} = diag(u)Kdiag(v) \tag{10}$$

The Sinkhorn algorithm updates the vectors u and v alternately through iterative procedures to obtain the optimal solution for the optimal transport problem. The iteration process terminates after a certain number of iterations. Based on the above derivations, the detailed algorithm for Sinkhorn's method is shown in Algorithm 1. For more detailed derivations, please refer to [28,29].

# Algorithm 1. Sinkhorn method

Input: $C, \epsilon, a, b$

Initialization: $v^0 = 1_m, u^0 = 1_n, K = e^{-C_{i,j} / \epsilon}$

While Sinkhorn not converged do

$$u_i^{(n+1)} = \frac{a}{(Kv^{(i)})_i}$$

$$v_j^{(n+1)} = \frac{b}{(K'u^{(i+1)})_j}$$

End while

Optimal transportation matrix $P = diag(u)Kdiag(v)$

Output: $W_2(a, b) = \langle C, P \rangle$

$$\nabla_a W^2(a, b) = \epsilon \log(u_i)$$

It is a tradeoff for the choice of the regularization parameter $\epsilon$. Small $\epsilon$ yields more accurate results but increases computational costs. If $\epsilon$ approaches 0, the optimal solution P converges to the optimal solution of the original problem. Therefore, $\epsilon$ should be selected carefully based on the data and the specific requirements.

# 2.2. Multi-Scale Two-Parameter FWI Based on $W_2$

When solving the inversion problem for GPR data, the goal is to minimize the difference between the simulated data $d_{cal} = PE_y$ and the observed data $d_{obs}$. The $L_2$ norm is typically used as a misfit function to measure the difference between them. Therefore, the frequency-domain GPR full-waveform inversion objective function for dual-parameter inversion can be formulated as an optimization problem constrained by a partial differential equation [8,12].

$$\Phi(\epsilon, \sigma) = \min_{\varepsilon, \delta} |PE_y - d_{obs}|_2^2 \quad s.t. A(\epsilon, \sigma)E_y = s \tag{11}$$

Here, the $\epsilon$ and $\sigma$ represent the relative permittivity and conductivity determined during the inversion process, respectively. The $E_y$ is the electric field vector, and the source term is denoted by s. The discretized PDE Helmholtz operator matrix is represented as $A$, where $A(\epsilon, \sigma) = \mu \omega^2 (\epsilon + i\sigma / \omega) + \Delta$. The $\Delta$ represents the Laplace operator, $\mu$ is the magnetic permeability, and $\omega = 2\pi f$ is the angular frequency. The P is the detector operator, which samples the simulated wavefield at the receiver locations. The $\|\cdot\|_2^2$ term represents the $L_2$ norm used as the misfit function. For simplicity, Equation (11) only shows a single frequency and source. The extension to multiple frequencies and sources is achieved by summing over all frequencies and sources in the objective function. Additionally, we apply the $W_2$ distance to two-dimensional multi-offset GPR data and provide update formulas for the relative permittivity and conductivity using the limited-memory BFGS algorithm [10].

The $W_2$ distance, based on the optimal transport problem, is used as the misfit function to measure the mismatch between observed and simulated data. The global $W_2$ distance