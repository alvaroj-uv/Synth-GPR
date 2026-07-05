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