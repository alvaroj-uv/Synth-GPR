Example 25 We assume that the a priori probability density for \((X,Z)\) is constant inside the region \(0 < X < 60\mathrm{km}\), \(0 < Z < 50\mathrm{km}\), and that the (unnormalizable) probability density for \(T\) is constant. [END OF EXAMPLE.]

### L.2 Data

The data of the problem are the arrival times \(\{t^1, t^2, t^3, t^4\}\) of the seismic waves at a set of four seismic observatories whose coordinates are \(\{x^i, z^i\}\). The measurement of the arrival times will produce a probability density

\[
\rho_ {d} (t ^ {1}, t ^ {2}, t ^ {3}, t ^ {4}) \tag {233}
\]

over the 'data space'. As these are Newtonian times, the associated homogeneous probability density is constant:

\[
\mu_ {d} (t ^ {1}, t ^ {2}, t ^ {3}, t ^ {4}) = k. \tag {234}
\]

For consistency, we must assume (rule 8) that the limit of \(\rho_d(t^1,t^2,t^3,t^4)\) for infinite 'dispersions' is \(\mu_d(t^1,t^2,t^3,t^4)\).

Example 26 Assuming Gaussian, independent uncertainties, we have

\[
\begin{array}{l} \rho_ {d} (t ^ {1}, t ^ {2}, t ^ {3}, t ^ {4}) = k \exp \left(- \frac {1}{2} \frac {(t ^ {1} - t _ {\mathrm{obs}} ^ {1}) ^ {2}}{\sigma_ {1} ^ {2}}\right) \exp \left(- \frac {1}{2} \frac {(t ^ {2} - t _ {\mathrm{obs}} ^ {2}) ^ {2}}{\sigma_ {2} ^ {2}}\right) \\ \times \quad \exp \left(- \frac {1}{2} \frac {\left(t ^ {3} - t _ {\mathrm{obs}} ^ {3}\right) ^ {2}}{\sigma_ {3} ^ {2}}\right) \exp \left(- \frac {1}{2} \frac {\left(t ^ {4} - t _ {\mathrm{obs}} ^ {4}\right) ^ {2}}{\sigma_ {4} ^ {2}}\right). \tag {235} \\ \end{array}
\]

[END OF EXAMPLE.]

### L.3 Solution of the Forward Problem

The forward problem consists in calculating the arrival times \( t^i \) as a function of the hypocentral coordinates \( \{X, Z\} \), and the origin time \( T \):

\[
t ^ {i} = f ^ {i} (X, Z, T). \tag {236}
\]

Example 27 Assuming that the velocity of the medium is constant, equal to v,

\[
t _ {\text {cal}} ^ {1} = T + \frac {\sqrt {(X - x ^ {i}) ^ {2} + (Z - z ^ {i}) ^ {2}}}{v}. \tag {237}
\]

### L.4 Solution of the Inverse Problem

Putting all this together gives

\[
\sigma_ {m} (X, Z, T) = k \rho_ {m} (X, Z, T) \left. \rho_ {d} \left(t ^ {1}, t ^ {2}, t ^ {3}, t ^ {4}\right) \right| _ {t ^ {i} = f ^ {i} (X, Z, T)}. \tag {238}
\]

### L.5 Numerical Implementation

To show how simple is to implement an estimation of the hypocentral coordinates using the solution given by equation 238, we give, in extenso, all the commands that are necessary to the implementation, using a commercial mathematical software (Mathematica). Unfortunately, while it is perfectly possible, using this software, to explicitly use quantities with their physical dimensions, the plotting routines require adimensional numbers. This is why the dimensions have been suppressed in whay follows. We use kilometers for the space positions and seconds for the time positions.

We start by defining the geometry of the seismic network (the vertical coordinate z is oriented with positive sign upwards):

x1 = 5;
z1 = 0;
x2 = 10;
z2 = 0;
x3 = 15;
z3 = 0;
x4 = 20;
z4 = 0;

62