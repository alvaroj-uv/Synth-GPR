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