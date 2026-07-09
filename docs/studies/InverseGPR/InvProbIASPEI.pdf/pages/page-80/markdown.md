from $-\pi$ to $+\pi$ (and not from $-\frac{\pi}{2}$ to $+\frac{\pi}{2}$). Borel set the following problem: Required to determine “the conditional probability distribution” of latitude $\theta$, $-\pi \leq \theta < +\pi$, for a given longitude $\psi$.

It is easy to calculate that

$$P_{\psi}(\theta_1 \leq \theta < \theta_2) = \frac{1}{4} \int_{\theta_1}^{\theta_2} |\cos \theta| \, d\theta \quad .$$

The probability distribution of $\theta$ for a given $\psi$ is not uniform.

If we assume the the conditional probability distribution of $\theta$ “with the hypothesis that $\xi$ lies on the given meridian circle” must be uniform, then we have arrived at a contradiction.

This shows that the concept of a conditional probability with regard to an isolated given hypothesis whose probability equals 0 is inadmissible. For we van obtain a probability distribution for $\theta$ on the meridian circle only if we regard this circle as an element of the decomposition of the entire spherical surface into meridian circles with the given poles.

A probability distribution is considered over the surface of the unit sphere, associating, as it should, to any region $\mathcal{A}$ of the surface of the sphere, a positive real number $P(\mathcal{A})$. To any possible choice of coordinates $\{u, v\}$ on the surface of the sphere will correspond a probability density $f(u, v)$ representing the given probability distribution, through $P(\mathcal{A}) = \int du \int dv \, f(u, v)$ (integral over the region $\mathcal{A}$). At this point of the discussion, the coordinates $\{u, v\}$ may be the standard spherical coordinates or any other system of coordinates (as, for instance, the Cartesian coordinates in a representation of the surface of the sphere as a ‘geographical map’, using any ‘geographical projection’).

A great circle is given on the surface of the sphere, that, should we use spherical coordinates, is not necessarily the ‘equator’ or a ‘meridian’. Points on this circle may be parameterized by a coordinate $\alpha$, that, for simplicity, we may take to be the circular angle (as measured from the center of the sphere).

The probability distribution $P(\cdot)$ defined over the surface of the sphere will induce a probability distribution over the circle. Said otherwise, the probability density $f(u, v)$ defined over the surface of the sphere will induce a probability density $g(\alpha)$ over the circle. This is the situation one has in mind when defining the notion of conditional probability density, so we may say that $g(\alpha)$ is the conditional probability density induced on the circle by the probability density $f(u, v)$, given the condition that points must lie on the great circle.

The Borel-Kolmogorov paradox is obtained when the probability distribution over the surface of the sphere is homogeneous. If it is homogeneous over the sphere, the conditional probability distribution over the great circle must be homogeneous too, and as we parameterize by the circular angle $\alpha$, the conditional probability density over the circle must be

$$g(\alpha) = \frac{1}{2\pi} \, , \tag{361}$$

and this is not what one gets from the standard definition of conditional probability density, as we will see below.

From now on, assume that the spherical coordinates $\{\vartheta, \varphi\}$ are used, where $\vartheta$ is the latitude (rather than the colalitude $\theta$), so the domains of definition of the variables are

$$-\pi/2 < \vartheta \leq +\pi/2 \quad ; \quad -\pi < \varphi \leq +\pi \quad . \tag{362}$$

As the surface element is $dS(\vartheta, \varphi) = \cos \vartheta \, d\vartheta \, d\varphi$, the homogeneous probability distribution over the surface of the sphere is represented, in spherical coordinates, by the probability density

$$f(\vartheta, \varphi) = \frac{1}{4\pi} \cos \vartheta \, , \tag{363}$$

and we satisfy the normalization condition

$$\int_{-\pi/2}^{+\pi/2} d\vartheta \int_{-\pi}^{+\pi} d\varphi \, f(\vartheta, \varphi) = 1 \, . \tag{364}$$

80