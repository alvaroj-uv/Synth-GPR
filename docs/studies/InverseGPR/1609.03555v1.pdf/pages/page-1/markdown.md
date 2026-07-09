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