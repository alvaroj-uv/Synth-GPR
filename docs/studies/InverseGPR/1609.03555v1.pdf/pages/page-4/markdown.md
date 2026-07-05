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