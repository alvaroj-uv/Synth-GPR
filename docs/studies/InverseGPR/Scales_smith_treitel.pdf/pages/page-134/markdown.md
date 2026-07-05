8.1 The X-ray Absorber

119

For our uses, we will need *two* types of absorption calculations:

exact We will want an *exact* calculation which we can use to generate synthetic data to test our inverse algorithms. This calculation mimics the data generation process in nature. This calculation should either be exact or at least much more accurate than the associated linearized calculation (if we wish to study uncertainties and ambiguities in the inverse process, rather than errors in the synthetic data generator).

linear We will also want a calculation in which the relation between a model's parameters and the observations predicted for that model is *linear*. The precise linear relationship will form the heart of a linear inverse calculation.

The difference between these two calculations is a measure of the problem's *non-linearity*. The next few subsections describe these two calculations in more detail.

### Exact Absorption

Let $\rho_{exact}$ be the exact absorption calculation. We can think of $\rho_{exact}(c; T, R)$ as a computer program to which is given the transmitter and receiver locations and the function $c(x, y)$ which defines the absorption coefficient everywhere in $\mathcal{D}_{\mathrm{X}}$. This program then returns the fractional intensity drop for the path $\overline{TR}$ through the medium $c(x, y)$.

The calculation itself is quite straightforward. In an actual application we would have to specify the accuracy with which the quadrature along the ray path is performed. In the calculations discussed here, we performed the quadrature by dividing the ray path into segments of a fixed length and then summing the contribution to the integral from each tiny segment. We took the segment length to be about $10^{-3}$; recall that the sides of the model are of unit length.

### 8.1.2 Linear Absorption

A simple way to linearize the exact calculation, equation (8.1), is to assume that the path integral,

$$
\int_{R}^{T} c(x, y) d\lambda
$$

is small. Since $e^x \approx 1 + x$ for small $x$, we have

$$
\mathbf{I}_R \approx \mathbf{I}_T \left( 1 - \int_{R}^{T} c(x, y) d\lambda \right)
$$

or

$$
\rho_{linear} \approx \int_{R}^{T} c(x, y) d\lambda \tag{8.3}
$$

1