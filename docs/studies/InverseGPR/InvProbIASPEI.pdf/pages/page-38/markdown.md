# Appendixes

## A Volumetric Probability and Probability Density

A probability distribution $\mathcal{A} \to P(\mathcal{A})$ over a manifold can be represented by a volumetric probability $F(\mathbf{x})$, defined through

$$P(\mathcal{A}) = \int_{\mathcal{A}} dV(\mathbf{x}) \, F(\mathbf{x}) \quad . \tag{120}$$

or by a probability density $f(\mathbf{x})$, defined through

$$P(\mathcal{A}) = \int_{\mathcal{A}} d\mathbf{x} \, f(\mathbf{x}) \tag{121}$$

where $d\mathbf{x} = dx^1 dx^2 \ldots$

While, under a change of variables, a probability density behaves as a density (i.e., its value at a point gets multiplied by the Jacobian of the transformation), a volumetric probability is a scalar (i.e., its value at a point remains invariant: it is defined independently of any coordinate system).

Defining the volume density through

$$V(\mathcal{A}) = \int_{\mathcal{A}} d\mathbf{x} \, v(\mathbf{x}) \tag{122}$$

and considering the expression

$$V(\mathcal{A}) = \int_{\mathcal{A}} dV(\mathbf{x}) \quad , \tag{123}$$

we obtain

$$dV(\mathbf{x}) = v(\mathbf{x}) \, d\mathbf{x} \quad . \tag{124}$$

It is then clear that the relation between volumetric probability and probability density is

$$f(\mathbf{x}) = v(\mathbf{x}) \, F(\mathbf{x}) \quad . \tag{125}$$

While the homogeneous probability distribution (the one assigning equal probabilities to equal volumes of the space) is, in general, not represented by a constant probability density, it is always represented by a constant volumetric probability.

The authors of this paper favor, in their own work, the use of volumetric probabilites. For pedagogical reasons, we have chosen in this work to use probability densities.

## B Conditional and Marginal Probability Densities

### B.1 Conditional Probability Density

Let be $\mathcal{A}_p$ a set of the submanifold $\mathcal{M}_p$ and let be $\mathcal{A}_n(\delta)$ the set of points in $\mathcal{M}_n$ whose distance to the submanifold $\mathcal{M}_p$ is less or equal to $\delta$, and whose normal projection on the submanifold $\mathcal{M}_p$ falls inside $\mathcal{A}_p$. Given $\mathcal{A}_p$ and given $\delta$, the set $\mathcal{A}_n(\delta)$ is uniquely defined (see figure 12). In particular, $\mathcal{M}_n(\delta)$ is the set of all points of $\mathcal{M}_n$ whose distance to the submanifold $\mathcal{M}_p$ is less or equal to $\delta$ (i.e., $\mathcal{M}_n(\delta)$ is the 'tube' or radius $\delta$ around $\mathcal{M}_p$). It is clear that for any value of $\delta$,

$$Q_\delta(\mathcal{A}_p) = \frac{P(\mathcal{A}_n(\delta))}{P(\mathcal{M}_n(\delta))} \tag{126}$$

defines a probability over the submanifold $\mathcal{M}_p$. The conditional probability over the submanifold $\mathcal{M}_p$ is defined as the limit of $Q_\delta$ for $\delta \to 0$:

$$Q(\mathcal{A}_p) = \lim_{\delta \to 0} \frac{P(\mathcal{A}_n(\delta))}{P(\mathcal{M}_n(\delta))} \quad . \tag{127}$$

The expression of the probability density (or the volumetric probability) associated to $Q$ may be complicated is the hypersurface is nor flat, if the metric is not Euclidean, or if the coordinates being used are not Cartesian.

38