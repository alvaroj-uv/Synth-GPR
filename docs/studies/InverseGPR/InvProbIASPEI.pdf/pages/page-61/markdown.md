# K An Example of Partial Derivatives

Let us consider the problem of locating a point in space using a system like the Global Positioning System (GPS), where some sources (satellites) send waves to a receiver, which measures the travel times. Let us use Cartesian coordinates, denote by $(x^i, y^i, z^i)$ the position of the $i$-th source, and by $(x^R, y^R, z^R)$ the position of the receiver. Simplify the problem here by assuming that the the medium where the waves propagate is homogeneous, so the velocity of the waves is constant (say $v$) and the rays are straight lines. Then, the travel time from the $i$-th source to the receiver is

$$t^i = g^i(x^R, y^R, z^R, v) = \frac{\sqrt{(x^R - x^i)^2 + (y^R - y^i)^2 + (z^R - z^i)^2}}{v} \tag{228}$$

The dependence of $t^i$ on the variables describing the source positions $(x^i, y^i, z^i)$ is not explicitly considered, as the typical GPS problem consists in assuming the position of the sources exactly known, and to estimate the receiver position $(x^R, y^R, z^R)$. At no extra cost we can also try to estimate the velocity of propagation of waves $v$. The partial derivatives of the problem are then

$$\begin{pmatrix} \frac{\partial g^1}{\partial x^R} & \frac{\partial g^1}{\partial y^R} & \frac{\partial g^1}{\partial z^R} & \frac{\partial g^1}{\partial v} \\ \frac{\partial g^2}{\partial x^R} & \frac{\partial g^2}{\partial y^R} & \frac{\partial g^2}{\partial z^R} & \frac{\partial g^2}{\partial v} \\ \vdots & \vdots & \vdots & \vdots \\ \frac{\partial g^i}{\partial x^R} & \frac{\partial g^i}{\partial y^R} & \frac{\partial g^i}{\partial z^R} & \frac{\partial g^i}{\partial v} \\ \vdots & \vdots & \vdots & \vdots \end{pmatrix} = \begin{pmatrix} \frac{x^R - x^1}{v D^1} & \frac{y^R - y^1}{v D^1} & \frac{z^R - z^1}{v D^1} & -\frac{D^i}{v^2} \\ \frac{x^R - x^2}{v D^2} & \frac{y^R - y^2}{v D^2} & \frac{z^R - z^2}{v D^2} & -\frac{D^i}{v^2} \\ \vdots & \vdots & \vdots & \vdots \\ \frac{x^R - x^i}{v D^i} & \frac{y^R - y^i}{v D^i} & \frac{z^R - z^i}{v D^i} & -\frac{D^i}{v^2} \\ \vdots & \vdots & \vdots & \vdots \end{pmatrix}, \tag{229}$$

where $D^i$ is a short notation for the distance

$$D^i = \sqrt{(x^R - x^i)^2 + (y^R - y^i)^2 + (z^R - z^i)^2} \tag{230}$$

In order to keep notations simple, it has not been explicitly indicated that these partial derivatives are functions of the variables of the problem, i.e., as functions of $(x^R, y^R, z^R, v)$ (remember that the locations of the satellites, $(x^i, y^i, z^i)$ are assumed exactly known, so they are not "variables"). Assigning particular values to the variables $(x^R, y^R, z^R, v)$ gives particular values for the travel times $t^i$ (through equation 228) and for the partial derivatives (through equation 229).

# L Probabilistic Estimation of Hypocenters

Earthquakes generate waves, and the arrival times of the waves at a network of seismic observatories carries information on the location of the hypocenter. This information is better understood by a direct examination of the probability density $f(X, Y, Z)$ defined by the arrival times, rather than just estimating a particular location $(X, Y, Z)$ and the associated uncertainties.

Provided that a 'black box' is available that rapidly computes the travel times to the seismic station from any possible location of the earthquake, this probabilistic approach can be relatively efficient. Tjhis appendix shows that it is quite trivial to write a computer code that uses this probabilistic approach (much easier than to write a code using the traditional Geiger method, that seeks to obtain the 'best' hypocentral coordinates).

# L.1 A Priori Information on Model Parameters

The 'unknowns' (morel parameters) of the problem are the hypocentral coordinates of an Earthquake$^{32}$ $\{X, Z\}$, as well as the origin time $T$. We assume to have some a priori information about the location of the earthquake, as well as about ots origin time. This a priori information is assumed to be represented using the probability density

$$\rho_m(X, Z, T) \tag{231}$$

Because we use Cartesian coordinates and Newtonian time, the homogeneous probability density is just a constant,

$$\mu_m(X, Y, T) = k \tag{232}$$

For consistency, we must assume (rule 8) that the limit of $\rho_m(X, Z, T)$ for infinite 'dispersions' is $\mu_m(X, Z, T)$.

$^{32}$To simplify, here, we consider a 2D flat model of the Earth, and use Cartesian coordinates.

61