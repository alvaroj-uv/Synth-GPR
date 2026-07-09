Inverse source problem for wave equation

7

By notation (12)

$$\int_{0}^{t} H(s)ds = \frac{\mu_0 c_0 c^3}{c_0 + c}(\Phi'(t) - \Phi'(0)). \tag{27}$$

Taking into account (26) and (27) we have

$$u(0, t; F^N) = \frac{\mu_0}{(c^{-1} + c_0^{-1})^2} \sum_{k=1}^N F_k \int_{0}^{ct/2} X_k(\xi)(\Phi'(t - 2\xi/c) - \Phi'(0))d\xi = \sum_{k=1}^N F_k G_k(t),$$

where the following notation is used:

$$G_k(t) \triangleq \frac{\mu_0}{(c^{-1} + c_0^{-1})^2} \int_{0}^{ct/2} X_k(\xi)(\Phi'(t - 2\xi/c) - \Phi'(0))d\xi, \ k = \overline{1, N}. \tag{28}$$

Because the measured data $g(t)$ always contain a random noise, we look for the unique regularized solution of the inverse problem (1)-(2). This solution $F_\alpha \in L^2(0, l)$ is defined as a minimum of the Tikhonov functional (3). The regularized cost functional (3) on the finite-dimensional approximation $F^N(x)$ is the $N$-variable function $J_\alpha(F^N) \equiv J_\alpha(F_1^N, F_2^N, \cdots F_N^N)$:

$$J_\alpha(F^N) \triangleq \frac{1}{2} \int_{0}^{T} \left( \sum_{k=1}^N F_k^N G_k(t) - g(t) \right)^2 dt + \frac{\alpha}{2} \sum_{k=1}^N (F_k^N)^2.$$

The $N$-dimensional vector of unknown parameters $(F_1^N, F_2^N, \ldots, F_N^N)$ is the unique minimizer of this functional and is defined from the conditions

$$\frac{\partial J_\alpha(F_1^N, F_2^N, \ldots, F_N^N)}{\partial F_k^N} := \sum_{i=1}^N F_i^N \int_{0}^{T} G_i(t)G_k(t)dt + \alpha F_k^N - \int_{0}^{T} G_k(t)g(t)dt = 0, \ k = \overline{1, N}.$$

This yields the following system of linear algebraic equations

$$(\mathbf{A}^N + \alpha \mathbf{I})\mathbf{F}_\alpha^N = \mathbf{b}^N, \tag{29}$$

with respect to the unknown vector $\mathbf{F}_\alpha^N := (F_{\alpha 1}^N, F_{\alpha 2}^N, \ldots, F_{\alpha N}^N)$, with the matrix $\mathbf{A}^N$ and right hand side vector $\mathbf{b}^N$, defined as

$$\begin{array}{l} A_{ij}^N = \int_{0}^{T} G_i(t)G_j(t)dt, \ i, j = \overline{1, N}, \\ b_{j}^N = \int_{0}^{T} G_j(t)g(t)dt, \ j = \overline{1, N}. \end{array} \tag{30}$$

Here $\mathbf{I}$ is the identity matrix and the functions $G_j(t)$ are defined by (28). Hence, the unique solution of the discrete problem (29)-(30) defines an approximate solution of the regularized inverse problem. The problem of choosing the regularization parameters $N$ and $\alpha$ will be discussed in the next section.