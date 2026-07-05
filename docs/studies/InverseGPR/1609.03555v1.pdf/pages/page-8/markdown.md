8

Balgaisha Mukanova, Vladimir G. Romanov

## 4 Numerical results

Before using the described algorithm, let us analyze the behavior of the relative error for different values of the parameter of regularization $\alpha > 0$, cut-off parameter $N$ and noise level $\gamma > 0$.

Let

$$\varepsilon_F := \|F - F^N\|_{L^2(0,1)} / \|F\|_{L^2(0,1)}.$$

In order to obtain noise free synthetic measured data we have used the formula (21) and calculated the integral in (21) numerically. But in practice, measured data always contain noise, so, we define the random noisy output data as follows:

$$g^\gamma(t) = g(t) + \delta g(t) = g(t) + \gamma n(t) \|g(t)\|_{L^2[0,T]} / \|n(t)\|_{L^2[0,T]},$$

where $\gamma > 0$ is the relative noise level and

$$n(t) = \sum_{j=0}^{N_n} \xi_j \eta\left(\frac{t - j\tau}{\tau}\right), \ \tau = T/N_n$$

is the random function. Here $\eta(t)$ is a standard linear finite element and the values $\xi_j$, $j = 0, .., N_n$ are obtained using the MATLAB "randn" function, which generates arrays of random numbers whose elements are normally distributed with mean 0 and standard deviation $\sigma = 1$.

Let us assume now that the right hand side of the linear system (29) contains an error $\delta\mathbf{b}^N$. Then the relative error of the solution $\delta\mathbf{F}^N$, which is defined as the difference between solutions obtained for noise free and noisy data, is estimated as follows:

$$|\delta\mathbf{F}^N| \le C(\mathbf{A}^N, \alpha) |\delta\mathbf{b}^N|, \tag{31}$$

here $C(\mathbf{A}^N, \alpha)$ is a condition number of the matrix $\mathbf{A}^N + \alpha\mathbf{I}$, which depends on $N$, $\alpha$, $T$, $c$, $c_0$ and the function $H(\cdot)$ as well. The expressions (30) show that the errors in coordinates of $\delta\mathbf{b}_N$ in (31) are estimated via the relative noise level $\gamma = \|\delta g(t)\|_{L_2} / \|g(t)\|_{L_2}$ as follows:

$$|\delta b_j^N| = \left| \int_0^T G_j(t) \delta g(t) dt \right| \le C_1 \|\delta g(t)\|_{L_2(0,T)} = C_1 \gamma \|g(t)\|_{L_2(0,T)}, \tag{32}$$

where $C_1 = \max_{1 \le j \le N} \|G_j(t)\|_{L_2(0,T)}$. This yields:

$$|\delta\mathbf{F}^N| \le C(\mathbf{A}^N, \alpha) \sqrt{\sum_{j=1}^N (\delta\mathbf{b}_j^N)^2} \le C(\mathbf{A}^N, \alpha) \sqrt{N} C_1 \gamma \|g(t)\|_{L_2(0,T)}. \tag{33}$$

Therefore, the estimate (33) establishes relationship between relative error of the approximate solution $F^N(x)$ for noisy data and the noise level $\gamma$. This estimate also shows that the most admissible parameters $N$ and $\alpha$ should correspond to minimal