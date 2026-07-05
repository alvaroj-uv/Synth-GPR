6

Balgaisha Mukanova, Vladimir G. Romanov

where $\hat{g}(x) = 2(c + c_0)g''(2x/c)/(c_0H(0))$ and $l = cT/2$. The equation (20) represents Volterra equation of the second kind and is uniquely solvable in $L^2(0, l)$ for all $\hat{g}(x) \in L^2(0, l)$ ([20]). In other words, boundary data $g(t)$, $t \in [0, T]$ uniquely define the function $F(x)$ for $x \in [0, l]$, $l = cT/2$.

**Remark** The equation (20) gives an alternate way of solving the ISP (1)-(2). For instance, it can be solved numerically. The bigger values of $|H(0)|$ correspond to better stability estimates for the solution of the equation (20). This observation is in the concordance with numerical results presented below.

### 3 Algorithm for identifying the spacewise dependent source

Now we are going to construct a computational algorithm for solving the considered ISP. For a given $F \in L^2(0, l)$ denote by $u := u(x, t; F)$ a solution of the direct problem (1). Derive the formula for that solution at the axis $x = 0$. It follows from (17) and initial condition $u(0, 0) = 0$ that

$$u(0, t; F) = \frac{c_0}{c(c + c_0)} \int_0^t \int_0^{c\tau/2} F(\xi) H(\tau - 2\xi/c) d\xi d\tau. \tag{21}$$

We assume now that the function $F(x)$ has a finite support in $(0, l)$, $l = cT/2$, and approximate the unknown source $F(x)$ by the $N$th partial sum of the Fourier series at the interval $[0, l]$:

$$F^N(x) = \sum_{k=1}^N F_k X_k(x), \tag{22}$$

where $X_k(x)$, $k = \overline{1, \infty}$, are eigenfunctions of the following spectral problems:

$$\begin{cases} X_k'' + \lambda_k^2 X_k = 0, \quad x \in (0, l); \\ X_k(0) = 0, \quad X_k(l) = 0. \end{cases} \tag{23}$$

Solving the two-point problem (23), we find the normalized eigenfunctions

$$X_k(x) = \sqrt{\frac{2}{l}} \sin(\lambda_k x), \ \lambda_k = \frac{k\pi}{l}, \ k = \overline{1, \infty}, \tag{24}$$

corresponding to the eigenvalues $\lambda_k$. Note that the eigenfunctions system $X_k(x)$, $k = \overline{1, \infty}$, is complete in $L^2(0, l)$.

Substituting (22) into (21) we get

$$u(0, t; F^N) = \frac{c_0}{c(c + c_0)} \sum_{k=1}^N F_k \int_0^t \int_0^{c\tau/2} X_k(\xi) H(\tau - 2\xi/c) d\xi d\tau. \tag{25}$$

Changing the integration order and introducing new variable $s = \tau - 2\xi/c$ in (25) we obtain

$$u(0, t; F^N) = \frac{c_0}{c(c + c_0)} \sum_{k=1}^N F_k \int_0^{ct/2} X_k(\xi) \int_0^{t-2\xi/c} H(s) ds d\xi \tag{26}$$