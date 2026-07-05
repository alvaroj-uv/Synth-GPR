# Chapter 3

## Example: A Vertical Seismic Profile

Here we will look at another simple example of a geophysical inverse calculation. We will cover the technical issues in due course. The goal here is simply to illustrate the fundamental role of data uncertainties in any inverse calculation. In this example we will see that a certain model feature is near the limit of the resolution of the data. Depending on whether we are bold or conservative in assessing the errors of our data, this feature will or will not be required to fit the data.

We use a vertical seismic profile (VSP—used in exploration seismology to image the Earth's near surface) experiment to illustrate how a fitted response depends on the assumed noise level in the data. Figure 3.1 shows the geometry of a VSP. A source of acoustic energy is at the surface near a vertical bore-hole (left side). A receiver is lowered into a bore-hole, recording the travel time of the down-going acoustic pulse. These times are used to construct a "best-fitting" model of the wavespeed as a function of depth $v(z)$.

Of course the real velocity is a function of $x$, $y$, and $z$, but since in this example the rays propagate almost vertically, there will be no point in trying to resolve lateral variations in $v$. If the Earth is not laterally invariant, this assumption introduces a systematic error into the calculation.

For each observation (and hence each ray) the problem of data prediction boils down to computing the following integral:

$$t = \int_{\text{ray}} \frac{1}{v(z)} d\ell. \tag{3.1}$$

We can simplify the analysis somewhat by introducing the reciprocal velocity (called slowness): $s = 1/v$. Now the travel time integral is linear in slowness:

$$t = \int_{\text{ray}} s(z) d\ell. \tag{3.2}$$

If the velocity model $v(z)$ (or slowness $s(z)$) and the ray paths are known, then the

1