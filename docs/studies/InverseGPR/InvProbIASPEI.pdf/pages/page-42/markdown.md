The top of figure 15 represents the measured 'trajectory' of a single particle. The bottom of the figure shows the 'free-fall law' of a blinking mass. It is built as follows: if each individual measurement of a blink produces the probability density $f_i(t, x)$, and the OR operation produces, using all the measurements,

$$f(t, x) = k \sum_i f_i(t, x) \quad . \tag{141}$$

Once this 'law' is known, having used as many measurement as possible, we can consider a new blink of a new particle. A measurement of this particular blink gives the probability density $g(t, x)$. As special cases, we may have, in fact, only have measured the position of the blink,

$$g(t, x) = g_x(x) \quad \text{position measured only} \tag{142}$$

of the instant of the blink

$$g(t, x) = g_t(t) \quad \text{instant measured only} \quad , \tag{143}$$

but let us continue with the general case $g(t, x)$.

To 'combine' the 'law' $f(t, x)$ with the 'measurement' $g(t, x)$, we use the AND operation (here, as the use Galilean coordinates, the homogeneous probability density is a constant)

$$h(t, x) = k f(t, x) g(t, x) \quad . \tag{144}$$

See figure 16 for a graphical illustration.

## C.2 "Ideal Theory" (Conditional Probability Density)

In order to have a natural metric in the space-time, assume that we are in the context of the (special) relativistic space-time, where the distance element is assumed to be

$$ds^2 = dt^2 - \frac{1}{c^2} dx^2 \quad , \tag{145}$$

this meaning that the metric tensor of the working space is

$$\mathbf{g} = \begin{pmatrix} g_{tt} & g_{tx} \\ g_{xt} & g_{xx} \end{pmatrix} = \begin{pmatrix} 1 & 0 \\ 0 & -1/c^2 \end{pmatrix} \quad . \tag{146}$$

In special relativity, a particle of mass $m$ submitted to a force $f$ satisfies the dynamic equation

$$f = \frac{d}{dt} \frac{m v}{\sqrt{1 - (v/c)^2}} \quad , \tag{147}$$

where $v$ is the particle's velocity. If the force is constant, this integrates (assuming $v(0) = 0$) into

$$v(t) = \frac{a t}{\sqrt{1 + (at/c)^2}} \quad , \tag{148}$$

where the constant $a$, having the dimensions of an acceleration, is the ratio

$$a = \frac{f}{m} \quad . \tag{149}$$

In turn, the expression 148 integrates into the expression for the trajectory:

$$x(t) = \frac{c^2}{a} \left( \sqrt{1 + (a t/c)^2} - 1 \right) \quad . \tag{150}$$

The developments for the velocity and the position for $t \to 0$ and for $t \to \infty$ are given as a footnote$^{30}$.

$^{30}$For $t \to 0$ we obtain $v(t) = a t \left( 1 - \frac{1}{2} \left( \frac{a t}{c} \right)^2 + \dots \right)$ and $x(t) = \frac{1}{2} a t^2 \left( 1 - \frac{1}{4} \left( \frac{a t}{c} \right)^2 + \dots \right)$, while for $t \to \infty$ we obtain $v(t) = c \left( 1 - \frac{1}{2} \left( \frac{c}{a t} \right)^2 + \dots \right)$ and $x(t) = c \left( t - \frac{c}{a} + \dots \right)$.

42