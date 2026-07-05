arXiv:1609.03555v1 [math.NA] 11 Sep 2016

EURASIAN JOURNAL OF MATHEMATICAL
AND COMPUTER APPLICATIONS

ISSN 2306–6172

Volume 4, Number (3) –

# INVERSE SOURCE PROBLEM FOR WAVE EQUATION
AND GPR DATA INTERPRETATION PROBLEM

Balgaisha Mukanova, Vladimir G. Romanov

**Abstract** The inverse problem of identifying the unknown spacewise dependent source $F(x)$ in 1D wave equation $u_{tt} = c^2 u_{xx} + F(x)H(t - x/c)$, $(x, t) \in \{(x, t) | x > 0, -\infty \leq t \leq T\}$ is considered. Measured data are taken in the form $g(t) := u(0, t)$. The relationship between that problem and Ground Penetrating Radar (GRR) data interpretation problem is shown. The non-iterative algorithm for reconstructing the unknown source $F(x)$ is developed. The algorithm is based on the Fourier expansion of the source $F(x)$ and the explicit representation of the direct problem solution via the function $F(x)$. Then the minimization problem for discrete form of the Tikhonov functional is reduced to the linear algebraic system and solved numerically. Calculations show that the proposed algorithm allows to reconstruct the spacewise dependent source $F(x)$ with enough accuracy for noise free and noisy data.

**Key words:** Wave equation, inverse source problem, GPR data interpretation

**AMS Mathematics Subject Classification:** 65N20, 47A52,35L05, 35L20, 35Q86

## 1 Introduction

In this paper we study the problem of identifying an unknown spacewise dependent source $F(x)$ in

$$\left\{ \begin{array}{l} u_{tt} - c^2 u_{xx} = F(x)H(t - x/c), \ c = const > 0, \\ (x, t) \in \Omega_T = \{(x, t) \mid x > 0, -\infty \leq t \leq T\}; \\ (u_t - c_0 u_x)_{x=0} = 0, \ c_0 = const > 0, \quad u|_{t<0} = 0, \end{array} \right. \quad (1)$$

from boundary measured data

$$g(t) := u(0, t), \quad t \in [0, T]. \quad (2)$$

Here the function $F(x)$ is assumed to have a finite support in $(0, \infty)$ and $H(t)$ is a given piecewise smooth function such that $H(t) \equiv 0$ for $t < 0$ and $H(+0) \neq 0$. We define this problem as an inverse source problem (ISP) for wave equation (1) with Dirichlet type boundary measured data (2).

Inverse problems for hyperbolic equations naturally arise from medical applications, seismology and geophysical prospecting, radar technology, electrical networks and many other physical problems (see [1]-[11] and references therein). An inverse source problem of identifying an unknown source term $S(u)$ in the wave equation $u_{tt} - u_{xx} = S(u)$, $x, t > 0$, from boundary data $u(0, t) = f(t)$, $u_x(0, t) = g(t)$, has first been studied in [1]. Here an existence result for the identification problem is derived. Unicity of the solution

2

Balgaisha Mukanova, Vladimir G. Romanov

and ill-conditionedness of the ISP for wave equation with variable speed function and final measured data has been studied in [12]. Uniqueness results for multidimensional parabolic and hyperbolic ISPs have been established in [13]. Stability estimate and a reconstruction formula for $f(x)$ in the hyperbolic equation $u_{tt} = \Delta u + \sigma(t)f(x)$, $x \in \Omega \subset \mathbb{R}^r$, $t > 0$, from the Neumann type additional data $\partial u(x, t; f)/\partial n$ have been obtained in [14]. Regarding the numerical approaches to hyperbolic coefficient inverse problems, we refer to monographs [6], [7].

Most of numerical approaches to ISP for parabolic and hyperbolic equations deal with source term in separable form $F(x)H(t)$ (see, for instance, [2], [14], [15], [16] and references therein). In this paper the function $H(x, t)$ has the form $H(t - x/c)$, since, as it is shown below, the linearized GPR data interpretation problem takes the form (1)-(2); therefore the proposed method is applicable in radar techniques. In practice inverse problems arising in GPR techniques are solved via different approximate ways, most relevant of them are described in [17] and in the review [18].

In this paper, we develop new non-iterative algorithm for identifying the spacewise dependent source $F(x)$ in (1)-(2). This algorithm is based on integral formula for the solution of wave equation (1) and use of the $N$th partial sum of the Fourier expansion for the term $F(x)$. Substituting then this formula in the regularized cost functional

$$J_\alpha(F) := \frac{1}{2}\|u(0, \cdot; F) - g(\cdot)\|_{L^2(0,T)}^2 + \frac{\alpha}{2}\|F\|_{L^2(0,l)}^2, \quad \alpha > 0, \tag{3}$$

where $l = l(T)$, we obtain a system of algebraic equations which unique solution gives an approximate regularized solution of the considered inverse problem. The algorithm is simple, effective and does not require any iterative procedures. Our numerical results demonstrate that the accuracy of all reconstructions are sufficient for high noise levels of measured data. The similar approach for an inverse source problem related to the advection–diffusion equation has been proposed in [15], [16].

The paper is organized as follows. In Section 2 we reduce the GPR data interpretation problem to the ISP (1)-(2). Numerical algorithm for identification of a spacewise dependent source from Dirichlet type measured output data is described in Section 3. Results of computational experiments are given in Section 4. Some concluding remarks are made in Section 5.

## 2 Linearized mathematical model of GPR method

Let us formulate the 1D inverse problem for the model of GPR technique. As it is common in geophysics, assume that the medium fills the half-space $z > 0$ and the half-space $z < 0$ corresponds to the air. Let the electrical permittivity $\varepsilon$ of the medium depend on the coordinate $z$ only, magnetic permittivity $\mu = \mu_0 = \text{const} > 0$ in the whole space and the conductivity is negligible. Let the current source with intensity

$$j^{\varepsilon x}(t) = \Phi(t)\delta(z), \ \Phi(t) = 0 \text{ if } t \le 0, \ \Phi(t) \in C^2[0, \infty), \ \Phi''(+0) \ne 0,$$

be placed at the boundary $z = 0$ and directed along the axis $y$. Then it follows from Maxwell's equations that the electromagnetic field depends on $(z, t)$ only. The field has

Inverse source problem for wave equation

3

an electric component $E_2(z,t)$ along the axis $y$, and a magnetic component $H_1(z,t)$ along the axis $x$ that satisfy the Cauchy problem:

$$\frac{\partial H_1}{\partial z} = \varepsilon(z)\frac{\partial E_2}{\partial t} + \delta(z)\Phi(t), \quad \frac{\partial E_2}{\partial z} = \mu(z)\frac{\partial H_1}{\partial t}, \quad (E_2, H_1)_{t<0} = 0. \tag{4}$$

We assume below $\mu(z) = \mu_0 > 0$. By taking first derivatives with respect to $t$ from first equation and with respect to $z$ from second one in (4) and eliminating $\partial^2 H_1/\partial t \partial z$ we get

$$\frac{\partial^2 E_2}{\partial z^2} = \mu_0 \varepsilon(z)\frac{\partial^2 E_2}{\partial t^2} + \mu_0 \delta(z)\Phi'(t), \quad E_2|_{t<0} = 0. \tag{5}$$

Denote by $c(z) = 1/\sqrt{\mu_0 \varepsilon(z)}$. Suppose that the function $c^{-2}(z)$ is presented in the following form

$$c^{-2}(z) = \begin{cases} c_0^{-2}, & \text{if } z < 0 \\ c_1^{-2} + F(z), & \text{if } z \ge 0, \end{cases} \tag{6}$$

$$c_0, c_1 = const, \ F(z) \in C(R), \ |F(z)| \ll c_1^{-2}, \tag{7}$$

where the function $F(z)$ has a finite support in $z \in (0, \infty)$ and values $c_0 > 0$, $c_1 > 0$ are given. As it has been shown in [19], the conditions imposed to the functions $\Phi(t)$, $c^2(z)$ provide the existence and uniqueness of the solution to the Cauchy problem (5).

Now represent the solution of the direct problem (5) in the form $E_2(z,t) = U(z,t) + u(z,t)$ where $U(z,t)$ is the generalized solution of the Cauchy problem:

$$U_{zz} = \frac{1}{\Phi'(z)} U_{tt} + \mu_0 \Phi'(t) \delta(z), \quad (z \in \mathbb{R}, \ t > -\infty),$$

$$U|_{t<0} \equiv 0,$$

$$\overline{c}^2(z) = \begin{cases} c_0^2, & \text{if } z < 0, \\ c_1^2, & \text{if } z \ge 0. \end{cases} \tag{8}$$

Then the solution of the problem (8) is given by the formula:

$$U(z,t) = -\frac{\mu_0 c_0 c_1}{c_0 + c_1} \begin{cases} \Phi(t+z/c_0), & z < 0, \\ \Phi(t-z/c_1), & z > 0. \end{cases} \tag{9}$$

It can be checked directly that the function $U(z,t)$ is continuous anywhere and twice continuously differentiable in the half spaces $\mathbb{R}_-^2 = \{(z,t) \mid z < 0, t \in \mathbb{R}\}$, $\mathbb{R}_+^2 = \{(z,t) \mid z > 0, t \in \mathbb{R}\}$ and its first derivatives at $z=0$ are expressed as

$$U_z(-0,t) = -\frac{\mu_0 c_1}{c_0 + c_1} \Phi'(t), \quad U_z(+0,t) = \frac{\mu_0 c_0}{c_0 + c_1} \Phi'(t),$$

i.e.

$$U_z(+0,t) - U_z(-0,t) = \mu_0 \Phi'(t).$$

The last formula confirms that the second derivative $U_{zz}$ is represented as the singular function $\mu_0 \Phi'(t) \delta(z)$ and a regular one.

4

Balgaisha Mukanova, Vladimir G. Romanov

The linearization of the equation (5) with respect to $u(z,t)$ shows that the function $u(z,t)$ satisfies the equation

$$\frac{\partial^2 u}{\partial z^2} = \frac{1}{c^2(z)} \frac{\partial^2 u}{\partial t^2} + F(z) \frac{\partial^2 U}{\partial t^2}, \qquad u|_{t<0} = 0.$$

Since the support of the function $F(z)$ belongs to the domain $z > 0$, the function $u(z,t)$ with its first derivatives are continuous at the axis $z = 0$. For $z < 0$ the function $u(z,t)$ is a solution of the homogeneous equation and is expressed in the form $u(z,t) = r(t + z/c_0)$, where $r(t) = u(0,t)$. Therefore it satisfies the condition $u_t - c_0 u_z = 0$ for $z \le 0$ and, by the continuity, for $z = +0$. Then for $z > 0$ the function $u(z,t)$ is a solution to the following problem

$$c_1^2 \frac{\partial^2 u}{\partial z^2} = \frac{\partial^2 u}{\partial t^2} + F(z) c_1^2 \frac{\partial^2 U}{\partial t^2}, \ z > 0; \quad \left( \frac{\partial u}{\partial t} - c_0 \frac{\partial u}{\partial z} \right)_{z=0} = 0, \qquad u|_{t<0} = 0. \tag{10}$$

In GPR method electrical field $E_2(0,t)$ is measured, therefore additional data for inverse problem are

$$u|_{z=0} = g(t) \equiv E_2|_{z=0} - U|_{z=0}, \quad t \in [0,T], \ T > 0. \tag{11}$$

Now introduce the notation

$$H(t) = \frac{\mu_0 c_0 c_1^3}{c_0 + c_1} \Phi''(t), \tag{12}$$

replace $z$ by $x$ and $c_1$ by $c$ in (10) and define $\Omega_T = \{(x,t) | x > 0, -\infty \le t \le T\}$. Then the direct problem for $u(x,t)$ is formulated as follows

$$\frac{\partial^2 u}{\partial t^2} - c^2 \frac{\partial^2 u}{\partial x^2} = F(x) H(t - x/c), \quad (x,t) \in \Omega_T;$$
$$\left( \frac{\partial u}{\partial t} - c_0 \frac{\partial u}{\partial x} \right)_{x=0} = 0, \qquad u|_{t<0} = 0,$$

which coincides with the direct problem statement (1).

Therefore, the GPR data interpretation problem is reduced to the linear ISP (1)-(2).

Note that $H(t) = 0$ for $t < 0$, then $u(x,t) \equiv 0$ for $t \le x/c$. Moreover, to calculate $g(t) = u(0,t)$ for $t \in [0,T]$ we need only to find the solution of (1) in the domain

$$D_T = \{(x,t) \mid 0 \le x/c \le t \le T - x/c\}. \tag{13}$$

**Proposition.** If $H(t) \in H^1[0,T]$, $H(0) \neq 0$ and $g(t) \in H^2[0,T]$ then the space-dependent source $F(x) \in L^2(0,l)$ for $x \in [0,l]$, $l = cT/2$, for ISP (1), can be identified uniquely from the boundary measured data (2).

**Proof** By introducing the notation

$$v(x,t) = \left( \frac{\partial u}{\partial t} + c \frac{\partial u}{\partial x} \right) \tag{14}$$

Inverse source problem for wave equation

5

the equation (1) is rewritten as follows:

$$
\frac {\partial v}{\partial t} - c \frac {\partial v}{\partial x} = F (x) H (t - x / c). \tag {15}
$$

Since $u(x,t) = 0$ , then $v(x,t) = 0$ for $\{(x,t) \mid 0 \leq t \leq x / c\}$ , and, in particular, $v(x,x / c) = 0$ . Let $(x_0,t_0)$ be an arbitrary point in $D_T$ . Integrate the equation (15) along the line $t + x / c = t_0 + x_0 / c$ from the point $(x_0,t_0)$ up to the intersection with the characteristic line $t = x / c$ , i.e. the point $((x_0 + ct_0) / 2,(t_0 + x_0 / c) / 2)$ , and obtain

$$
v (x _ {0}, t _ {0}) = \frac {1}{c} \int_ {x _ {0}} ^ {(x _ {0} + c t _ {0}) / 2} F (x) H (t _ {0} + x _ {0} / c - 2 x / c) d x, \quad (x _ {0}, t _ {0}) \in D _ {T}.
$$

Then for all $(x,t)\in D_T$ the following equality

$$
\left(\frac {\partial}{\partial t} + c \frac {\partial}{\partial x}\right) u (x, t) = \frac {1}{c} \int_ {x} ^ {(x + c t) / 2} F (\xi) H (t + x / c - 2 \xi / c) d \xi , (x, t) \in D _ {T}. \tag {16}
$$

holds. The combination of the expression above at $x = 0$ with the boundary condition

$$
\left(\frac {\partial u}{\partial t} - c _ {0} \frac {\partial u}{\partial x}\right) _ {x = 0} = 0
$$

defines the derivative

$$
\left. \frac {\partial u}{\partial t} \right| _ {x = 0} = \frac {c _ {0}}{c (c + c _ {0})} \int_ {0} ^ {c t / 2} F (\xi) H (t - 2 \xi / c) d \xi . \tag {17}
$$

It follows from expressions (17) that

$$
g ^ {\prime} (t) = \frac {c _ {0}}{c (c + c _ {0})} \int_ {0} ^ {c t / 2} F (\xi) H (t - 2 \xi / c) d \xi , \quad t \in [ 0, T ] \tag {18}
$$

Let us analyze the expression (18). If $F(x) \in L^2(0, l)$ , $l = T / (2c)$ , $H(t) \in H^1[0, T]$ then $g(t) \in H^2[0, T]$ and $g'(0) = 0$ . Taking first derivative of (18), we have

$$
g ^ {\prime \prime} (t) = \frac {c _ {0}}{c (c + c _ {0})} \left[ F (c t / 2) H (0) c / 2 + \int_ {0} ^ {c t / 2} F (\xi) H ^ {\prime} (t - \xi / (2 c)) d \xi \right], \quad t \in [ 0, T ]. \tag {19}
$$

If $H(0) \neq 0$ then (18) is rewritten as follows:

$$
\hat {g} (x) = F (x) + \frac {2}{c H (0)} \int_ {0} ^ {x} F (\xi) H ^ {\prime} (2 (x - \xi) / c) d \xi , \quad x \in [ 0, l ], \tag {20}
$$

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

Inverse source problem for wave equation

9

Table 1. Values of the condition number \( C(\mathbf{A}^N, \alpha) \) depending on the parameters \( N \), \( \alpha \) for different \( \Phi(t) \), \( \beta_1 = 1.546 \), \( \beta_2 = 1.373 \), \( T = 12 \cdot 10^{-9} \) sec, \( c = 1.5 \cdot 10^8 \) m/sec, \( l = 0.9 \) m:

|  \( \Phi(t) = \sin(8t + \beta_1)\exp(-0.2t) \) |   |   |   |   |   | \( \Phi(t) = \sin(t + \beta_2)\exp(-0.2t) \)  |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  \( N\backslash \alpha \) | 0 | \( 10^{-4} \) | \( 10^{-3} \) | \( 10^{-2} \) | \( 10^{-1} \) | 0 | \( 10^{-5} \) | \( 10^{-4} \) | \( 10^{-3} \) | \( 10^{-2} \) | \( 10^{-1} \)  |
|  5 | 1.06 | 1.06 | 1.06 | 1.06 | 1.057 | 4.5 | 4.5 | 4.5 | 4.5 | 4.45 | 4.20  |
|  8 | 1.17 | 1.17 | 1.17 | 1.17 | 1.16 | 45.0 | 45.0 | 45 | 44.6 | 41.4 | 24.2  |
|  11 | 1.39 | 1.39 | 1.39 | 1.38 | 1.36 | 197 | 196.6 | 196 | 189 | 142 | 41.1  |
|  14 | 1.75 | 1.75 | 1.75 | 1.75 | 1.71 | 562 | 562 | 556 | 507 | 268 | 47.6  |
|  17 | 2.43 | 2.43 | 2.43 | 2.42 | 2.34 | 1278 | 1275 | 1247 | 1022 | 365 | 50.1  |
|  20 | 3.72 | 3.72 | 3.72 | 3.70 | 3.55 | 2511 | 2498 | 2393 | 1685 | 426 | 51.1  |

value of the number \(\sqrt{N} C(\mathbf{A}^N,\alpha)\). The last point leads to the practical way to choose these parameters.

The additional analysis has been done by computing the values of discrepancy  \( \eta \)  defined as follows

\[
\eta = \left(\int_ {0} ^ {T} \left(\sum_ {k = 1} ^ {N} F _ {\alpha k} ^ {N} G _ {k} (t) - g (t)\right) ^ {2} d t\right) ^ {1 / 2}. \tag {34}
\]

Let the assumptions of the Proposition hold and  \( F(x) \)  be the exact solution of the considered ISP. Let  \( F^{N}(x) \)  and  \( F_{ex}^{N}(x) \)  be computed and exact versions of the partial Fourier sums of  \( F(x) \) . Denote by  \( C_{i}, i = 1, 2, 3 \)  different constants which do not depend on  \( F(x) \)  and can depend on N,  \( \alpha \)  and physical parameters of the problem. Then the difference between exact and numerical solution of the inverse problem is estimated as follows:

\[
\| F (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq \| F (x) - F _ {e x} ^ {N} (x) \| _ {L ^ {2} (0, l)} + \| F _ {e x} ^ {N} (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)}. \tag {35}
\]

Define the function  \(  g^{N}(t) = u(0, t; F_{ex}^{N})  \) . Subtracting the equation (26) from (21) we obtain the integral equation which links the functions  \(  g(t) - g^{N}(t)  \)  and  \(  F(x) - F_{ex}^{N}(x)  \) . The solution of that equation satisfies the stability estimate which can be obtained in standard way:

\[
\| F (x) - F _ {e x} ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq C _ {2} \| g (t) - g ^ {N} (t) \| _ {H ^ {1} [ 0, T ]}. \tag {36}
\]

Due to the orthogonality of basic functions  \( X_{k}(x) \)  the  \( L_{2} \) -norm of the function  \( \delta F^{N}(x)=F_{ex}^{N}(x)-F^{N}(x) \)  is equal to Euclidean norm of the vector  \( \delta\mathbf{F}^{N}(x) \) ; therefore combination of (36) with (33) estimates the computational error of the solution to the inverse problem:

\[
\| F (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq C _ {2} \| g (t) - g ^ {N} (t) \| _ {H ^ {1} [ 0, T ]} + C _ {3} \| \delta g ^ {N} (t) \| _ {L ^ {2} [ 0, T ]}. \tag {37}
\]

As it is seen from the definition of the matrix \(\mathbf{A}\), it can be calculated independently before measurements. Therefore the condition numbers \(C(\mathbf{A}^N,\alpha)\) for different values of \(N\), \(\alpha\) and given physical data \(c\), \(c_0\), \(T\), \(H(t)\), \(l\) can be defined. Then the most admissible combinations of \(N\) and \(\alpha\) can be established. Table 1 shows values of condition numbers

10

Balgaisha Mukanova, Vladimir G. Romanov

Table 2. Values of the discrepancy η for noise free data depending on the parameters N, α and other inputs defined in Table 1:

|  Φ(t) = sin(8t + β₁) exp(−0.2t)  |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- |
|  N\α | 0 | 10⁻⁵ | 10⁻⁴ | 10⁻³ | 10⁻² | 10⁻¹  |
|  5 | 0.084 | 0.084 | 0.084 | 0.084 | 0.084 | 0.093  |
|  8 | 0.054 | 0.054 | 0.054 | 0.054 | 0.054 | 0.067  |
|  11 | 0.012 | 0.012 | 0.012 | 0.012 | 0.013 | 0.042  |
|  14 | 0.0065 | 0.0065 | 0.0065 | 0.0065 | 0.008 | 0.041  |
|  17 | 0.0043 | 0.0043 | 0.0043 | 0.0043 | 0.006 | 0.04  |
|  20 | 0.0029 | 0.0029 | 0.0029 | 0.003 | 0.005 | 0.04  |
|  Φ(t) = sin(t + β₂) exp(−0.2t)  |   |   |   |   |   |   |
|  N\α | 0 | 10⁻⁵ | 10⁻⁴ | 10⁻³ | 10⁻² | 10⁻¹  |
|  5 | 0.0034 | 0.034 | 0.034 | 0.034 | 0.034 | 0.049  |
|  8 | 0.01 | 0.01 | 0.01 | 0.01 | 0.011 | 0.039  |
|  11 | 0.001 | 0.001 | 0.001 | 0.0011 | 0.0043 | 0.038  |
|  14 | 0.00044 | 0.00044 | 0.00044 | 0.0006 | 0.0043 | 0.038  |
|  17 | 0.00037 | 0.00036 | 0.00046 | 0.00054 | 0.0043 | 0.038  |
|  20 | 0.00037 | 0.00036 | 0.00036 | 0.00054 | 0.0043 | 0.038  |

C(𝒜ᴺ, α) computed for the function Φ(t) = sin(ωt + β) exp(−γt) − Φ₀ with different values of ω, α and N. The parameters β and Φ₀ are taken to satisfy the conditions Φ(0) = 0, Φ'(0) = 0, namely, β = arctan(ω/γ), Φ₀ = sin β. Values of discrepancies η(N, α) calculated for noise free data are collected in Table 2.

It is seen in Table 1 that the most important parameters that influence to the condition number are the frequency ω of the perturbation Φ(t) and the cut-off parameter N. It follows from calculations that higher values of ω are preferable. Numerical experiments show that the value of C(𝒜ᴺ, α) increases when N grows and almost does not depend on α for ω = 8 and decreases when α grows for ω = 1. On the other hand, Table 2 shows that lower values of α correspond to smaller discrepancy η. This is the reason why the value of α = 0 has been set in the experiments described below.

Results shown in Table 1 confirm also the Remark made in previous Section. Values of |H(0)| for Φ(t) = sin(8t + β₁) exp(−0.2t) and Φ(t) = sin(t + β₂) exp(−0.2t) are 64.02 and 1.02 respectively. It is seen from Table 1 that the function Φ(t) with bigger |H(0)| = |Φ''(0)| is preferable.

Further we have checked different values of decay coefficient ν = 0.2 ÷ 10 of the function Φ(t) = sin(ωt + β) exp(−νt). It turned out that bigger values of ν are preferable because they decrease C(𝒜ᴺ, α). For instance, for the value ν = 10 and N changing in the range 5 ÷ 20 the computed values of C(𝒜ᴺ, α) monotonously raise in the intervals 1.03 ÷ 1.6 and 1.0 ÷ 1.11 for ω = 8 and ω = 1 respectively.

In order to obtain admissible values of parameter N for different noise level γ, we generate synthetic data for T = 12 · 10⁻⁹ sec, c = 1.5 · 10⁸ m/sec, l = 0.9 m, F(x) = exp(−((x − 0.3l)/0.15l)²) + exp(−((x − 0.7l)/0.1l)²) with function H(t) = Φ''(t), Φ(t) = sin(8t + 1.546) exp(−0.2t). Different values of N has been tested and the most favorable ones are established. The results are collected in Table 3.

Inverse source problem for wave equation

11

We see in Table 3 that the discrepancy \(\eta\) is above the absolute noise level in \(g(t)\): \(\eta \approx \gamma_{1}\). This verifies the choice of the values of \(N\) and \(\alpha = 0\) made in the table for the each relative noise level \(\gamma\).

Table 3. Admissible values of the cut-off parameter \(N\), corresponding recovery errors \(\varepsilon_{F}\), discrepancy values \(\eta\) for different relative \((\gamma)\) and absolute \((\gamma_{1} = \| \delta g(t)\|_{L_{2}[0,T]})\) noise levels:

|  \( \omega = 8 \) | \( \gamma \) | 0% | 1% | 3% | 5% | 7% | 10% | 20%  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|   |  \( \gamma_1 \) | 0 | 0.0064 | 0.019 | 0.032 | 0.045 | 0.064 | 0.128  |
|   |  N | 20 | 17 | 14 | 11 | 11 | 11 | 9  |
|   |  \( \varepsilon_F \) | 0.46% | 0.7% | 1.5% | 2.3% | 3% | 4% | 7.6%  |
|   |  \( \eta \) | 0.003 | 0.008 | 0.021 | 0.033 | 0.044 | 0.061 | 0.122  |
|  \( \omega = 1 \) | \( \gamma \) | 0% | 1% | 3% | 5% | 7% | 10% | 20%  |
|   |  \( \gamma_1 \) | 0 | 0.0076 | 0.023 | 0.038 | 0.053 | 0.076 | 0.152  |
|   |  N | 20 | 13 | 11 | 10 | 10 | 9 | 9  |
|   |  \( \varepsilon_F \) | 0.6% | 2.3% | 3.7% | 4% | 5% | 6.5% | 12%  |
|   |  \( \eta \) | 0.0005 | 0.008 | 0.025 | 0.036 | 0.05 | 0.072 | 0.143  |

Results of recovery based on parameters and other inputs taken from Table 3 are presented in Fig.1 for the case of \( H(t) = \Phi''(t) \), \( \Phi(t) = \sin (t + 1.373)\exp (-0.2t) \).

![img-0.jpeg](img-0.jpeg)

![img-1.jpeg](img-1.jpeg)

Рис. 1: The identified spacewise source \( F(x) \) (right figure) from \( 20\% \) noisy data (left figure) with parameter \( N = 9 \) defined in Table 3 for \( \omega = 1 \).

Since the matrix \(\mathbf{A}\) does not depend on \(F(x)\), the parameters \(N\), \(\alpha\) can be defined once for given \(H(t)\) and then used again for wide range of functions \(F(x)\). Further we take parameters listed in Table 3 to recover other functions, including the combination of three Gaussians \(F(x) = -0.1\exp (-((x - 0.3l) / 0.05l)^2) + 0.1\exp (-((x - 0.5l) / 0.05l)^2) + \exp (-((x - 0.7l) / 0.05l)^2)\) and the function generated from the standard linear finite element \(F(x) = \eta (4(x - 0.5l) / l)\). The results are depicted in Fig. 2-3 for the case of \(5\%\) noisy data. Then the algorithm has been applied for recovery of discontinuous functions \(F(x)\). In that case only approximate agreement has been achieved. The result is represented in Fig.4. It follows from numerical simulations that better results are obtained for higher frequency \(\omega\) and higher decay coefficient \(\nu\) of the function \(\Phi (t) =\)

12

Balgaisha Mukanova, Vladimir G. Romanov

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)

Рис. 2: The identified spacewise source $F(x)$ (right figure) from noise free and 5% noisy data (left figure) with $N = 20$ and 10 for $\Phi(t) = \sin(t + 1.373) \exp(-0.2t)$.

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

Рис. 3: The identified spacewise source $F(x) = \eta(4(x - 0.5l)/l)$ (right figure) from 5% noisy data (left figure) with $N = 10$ for $\Phi(t) = \sin(t + 1.373) \exp(-0.2t)$.

$\sin(\omega t + \beta) \exp(-\nu t)$. Numerical simulations show that in the case of smooth $F(x)$ for given parameters $c, T$ and the function $H(t)$, the admissible values of $N$ can be found via numerical experiments on synthetic data.

## Conclusion

In this paper, we studied an inverse problem of identifying the unknown spacewise dependent source $F(x)$ in the one-dimensional wave equation $u_{tt} = c^2 u_{xx} + F(x)H(t - x/c)$, $(x, t) \in \Omega_T$, which is treated as an approximate model of GPR data interpretation process. The case of boundary measured data $g(t) := u(0, t)$ is considered. Perturbation of the media via the radar signal is formulated in terms of the function $H(t - x/c)$ and the non-homogeneity of electrical permittivity is expressed via the function $F(x)$ with

Inverse source problem for wave equation

13

![img-6.jpeg](img-6.jpeg)

Рис. 4: Recovery of discontinuous source $F(x)$ (right figure) from 5% noisy data (left figure) with parameters listed in Table 2 for $\omega = 1$.

finite support in $(0, l)$, $l = cT/2$. We develop a simple algorithm for reconstruction of a spacewise dependent source term $F(x)$, based on integral formula for the solution of the direct problem with subsequent minimization of the regularized Tikhonov functional. The proposed algorithm allows one to reconstruct the unknown source from random noisy data up to 10% noise level for a reasonable choice of the function $H(t)$. Note that this method can also be applied to obtain an initial iteration for Conjugate Gradient Algorithm solving the coefficient inverse problem for a hyperbolic equation $u_{tt} = c^2(x)u_{xx}$ with variable wave propagation speed.

## Acknowledgement

The work of the first author was supported by the Ministry of Education and Science of Republic of Kazakhstan, under the Grant No. 316 (13 May, 2016).

14

Balgaisha Mukanova, Vladimir G. Romanov

# References

[1] J. R. Cannon and P. DuChateau, An inverse problem for an unknown source term in a wave equation, SIAM J. Appl. Math. Vol.43(3) (1983) 553-564.
[2] M. Chapouly, M. Mirrahimi, Distributed source identification for wave equations: An off-line observer-based approach, Automatic Control, IEEE Trans. 57(8) (2012) 2076-2073.
[3] J. Deguenon, G. Sallet, C.-Z. Xu, Infinite dimensional observers for vibrating systems, in Proc. IEEE Conf. on Decision and Control, (2006) 3979-3983.
[4] V. Isakov, Inverse Source Problem, Mathematical Surveys and Monographs, Vol. 34, American Mathematical Society, 1990.
[5] S.I. Kabanikhin, Inverse and Ill-Posed Problems. Theory and Applications, De Gruyter, Germany, 2011.
[6] S.I. Kabanikhin, A. D. Satybaev and M. A. Shishlenin, Direct Methods of Solving Multidimensional Inverse Hyperbolic Problem, VSP, Utrecht, 2004.
[7] M.V. Klibanov and A.Timonov, Carleman Estimates for Coefficient Inverse Problems and Numerical Applications, VSP, Utrecht, 2004.
[8] Maarten V de Hoop, Justin Tittelfitz, An inverse source problem for a variable speed wave equation with discrete-in-time sources, Inverse Problems, 31(7) (2015) 075007.
[9] Rakesh, W.W. Symes, Uniqueness for an inverse problem for the wave equation, Commun. Partial Diff. Eq. 13 (1988) 87-96.
[10] V.G. Romanov, Inverse Problem of Mathematical Physics, VNU Science Press, Utrecht, 1987.
[11] A. Tikhonov, V. Arsenin, Solution of Ill-Posed Problems, Wiley, New York, 1977.
[12] A. Hasanov, Simultaneous determination of source terms in a linear hyperbolic problem from the final overdetermination: weak solution approach, IMA J. Appl. Math. Vol. 74 (2009) 1-19.
[13] H.W. Engl, O. Scherzer, M. Yamamoto, Uniqueness and stable determination of forcing terms in linear partial differential equations with overspecified boundary data, Inverse Probl. Vol. 10 (1994) 1253-1276.
[14] M. Yamamoto, Stability, reconstruction formula and regularization for an inverse source hyperbolic problem by a control method, Inverse Problems, Vol.11 (1995) 481-496.
[15] A. Hasanov, B. Mukanova, Fourier collocation algorithm for identifying the spacewise-dependent source in the advection-diffusion equation from boundary data measurements, Appl. Numer. Math., 97 (2015) 1-14.
[16] M. Kulbay, B. Mukanova, C. Sebu, Identification of separable sources for advection-diffusion equations with variable diffusion coefficient from boundary measured data, Inverse Problems in Science and Engineering, 2016, c.1-30, DOI:10.1080/17415977.2016.1160396.
[17] R.H. Stolt, Migration by Fourier transform, Geophysics, Vol.43(1) (1978) 23-43.
[18] Caner Özdemir, Fevket Demirci, Enes Yiğit, and Betül Yılmaz, A Review on Migration Methods in B-Scan Ground Penetrating Radar Imaging, Mathematical Problems in Engineering, Vol. 2014, Article ID 280738, http://dx.doi.org/10.1155/2014/280738.
[19] S.I. Kabanikhin, K.T. Isakov, Inverse and ill-posed problems for hyperbolic equations, Almaty, KazNPU, 2007 (in Russian).

*Inverse source problem for wave equation*

15

[20] F.G. Tricomi, *Integral equations*, Interscience Publishers Inc., New York, 1957.

Balgaisha Mukanova,  
L.N. Gumilyov Eurasian National University,  
2, Satpayev Str., 010008 Astana, Republic of Kazakhstan,  
Email: mukanova\_bg@enu.kz

Vladimir G. Romanov,  
Sobolev Institute of Mathematics,  
Novosibirsk 630090, Koptyug prosp., 4, Russia,  
Email: romanov@math.nsc.ru

Received 12.07.2016, Accepted 05.08.2016