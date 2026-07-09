The probability of any region equals the relative surface of the region (i.e., the ratio of the surface of the region divided by the surface of the sphere, $4\pi$), so the probability density in equation 363 do represents the homogeneous probability distribution.

Two different computations follow. Both are aimed at computing the conditional probability density over a great circle.

The first one uses the nonconventional definition of conditional probability density introduced in section in appendix B of this article (and claimed to be 'consistent'). No paradox appears. No matter if we take as great circle a meridian or the equator.

The second computation is the conventional one. The traditional Borel-Kolmogorov paradox appears, when the great circle is taken to be a meridian. We interpret this as a sign of the inconsistency of the conventional theory. Let us develop the example.

We have the line element (taking a sphere of radius 1),

$$ds^2 = d\vartheta^2 + \cos^2 \vartheta \, d\varphi^2 \, , \tag{365}$$

which gives the metric components

$$g_{\vartheta\vartheta}(\vartheta, \varphi) = 1 \qquad ; \qquad g_{\varphi\varphi}(\vartheta, \varphi) = \cos^2 \vartheta \tag{366}$$

and the surface element

$$dS(\vartheta, \varphi) = \cos \vartheta \, d\vartheta \, d\varphi \, . \tag{367}$$

Letting $f(\vartheta, \varphi)$ be a probability density over the sphere, consider the restriction of this probability on the (half) meridian $\varphi = \varphi_0$, i.e., the conditional probability density on this (half) meridian. It is, following equation 131,

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = k \frac{f(\vartheta, \varphi_0)}{\sqrt{g_{\varphi\varphi}(\vartheta, \varphi_0)}} \quad . \tag{368}$$

In our case, using the second of equations 366

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = k \frac{f(\vartheta, \varphi_0)}{\cos \vartheta} \quad , \tag{369}$$

or, in normalized version,

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = \frac{f(\vartheta, \varphi_0)/\cos \vartheta}{\int_{-\pi/2}^{+\pi/2} d\vartheta \, f(\vartheta, \varphi_0)/\cos \vartheta} \quad . \tag{370}$$

If the original probability density $f(\vartheta, \varphi)$ represents an homogeneous probability, then it must be proportional to the surface element $dS$ (equation 367), so, in normalized form, the homogeneous probability density is

$$f(\vartheta, \varphi) = \frac{1}{4\pi} \cos \vartheta \, . \tag{371}$$

Then, equation 369 gives

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = \frac{1}{\pi} \, . \tag{372}$$

We see that this conditional probability density is constant$^{40}$.

This is in contradiction with usual 'definitions' of conditional probability density, where the metric of the space is not considered, and where instead of the correct equation 368, the conditional probability density is 'defined' by

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = k f(\vartheta, \varphi_0) = \frac{f(\vartheta, \varphi_0)}{\int_{-\pi/2}^{+\pi/2} d\vartheta \, f(\vartheta, \varphi_0)/\cos \vartheta} \quad \text{wrong definition} \quad , \tag{373}$$

this leading, in the considered case, to the conditional probability density

$$f_\vartheta(\vartheta|\varphi = \varphi_0) = \frac{\cos \vartheta}{2} \quad \text{wrong result} \quad . \tag{374}$$

$^{40}$This constant value is $1/\pi$ if we consider half a meridian, or it is $1/2\pi$ if we consider a whole meridian.

81