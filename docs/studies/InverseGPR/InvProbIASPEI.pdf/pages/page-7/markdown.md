The volume density equals the metric determinant $v(r, \theta, \varphi) = \sqrt{\det \mathbf{g}(r, \theta, \varphi)} = r^2 \sin \theta$ and therefore the volume element is $dV(r, \vartheta, \varphi) = v(r, \vartheta, \varphi) \, dr \, d\vartheta \, d\varphi = r^2 \sin \theta \, dr \, d\vartheta \, d\varphi$. [END OF EXAMPLE.]

Assume that we have defined over the space, not only the volume $V(\mathcal{A})$ of a region $\mathcal{A}$ of the space, but also its probability $P(\mathcal{A})$, that is assumed to satisfy the Kolmogorov axioms (Kolmogorov, 1933). This probability is assumed to be describable in terms of a probability density $f(x)$ through the expression

$$P(\mathcal{A}) = \int_{\mathcal{A}} d\mathbf{x} \, f(\mathbf{x}). \tag{6}$$

It is well known that, in a change of coordinates over the space, a probability density changes its value: it is multiplied by the Jacobian of the transformation (this is the Jacobian rule). Normally, the probability of the whole space is normalized to one. If it is not normalizable, we do not say that we have a probability, but a 'measure'. We can state here the

Postulate 1 Given a space $\mathcal{X}$ over which a volume measure $V(\cdot)$ is defined. Any other measure (normalizable or not) $M(\cdot)$ considered over $\mathcal{X}$ is absolutely continuous with respect to $V(\cdot)$, i.e., the measure $M(\mathcal{A})$ of any region $\mathcal{A} \subset \mathcal{X}$ with vanishing volume must be zero: $V(\mathcal{A}) = 0 \Rightarrow M(\mathcal{A}) = 0$.

## 2.2 Homogeneous Probability Distributions

In some parameter spaces, there is an obvious definition of distance between points, and therefore of volume. For instance, in the 3D Euclidean space the distance between two points is just the Euclidean distance (which is invariant under translations and rotations). Should we choose to parameterize the position of a point by its Cartesian coordinates $\{x, y, z\}$, the volume element in the space would be $dV(x, y, z) = dx \, dy \, dz$, while if we choose to use geographical coordinates, the volume element would be $dV(r, \theta, \varphi) = r^2 \sin \theta \, dr \, d\vartheta \, d\varphi$.

Definition. The homogeneous probability distribution is the probability distribution that assigns to each region of the space a probability proportional to the volume of the region.

Then, which probability density represents such a homogeneous probability distribution? Let us give the answer in three steps.

- If we use Cartesian coordinates $\{x, y, z\}$, as we have $dV(x, y, z) = dx \, dy \, dz$, the probability density representing the homogeneous probability distribution is constant: $f(x, y, z) = k$.
- If we use geographical coordinates $\{r, \theta, \varphi\}$, as we have $dV(r, \theta, \varphi) = r^2 \sin \theta \, dr \, d\theta \, d\varphi$, the probability density representing the homogeneous probability distribution is $g(r, \theta, \varphi) = k \, r^2 \sin \theta$.
- Finally, if we use an arbitrary system of coordinates $\{u, v, w\}$, in which the volume element of the space is $dV(u, v, w) = v(u, v, w) \, du \, dv \, dw$, the homogeneous probability distribution is represented by the probability density $h(u, v, w) = k \, v(u, v, w)$.

This is obviously true, since if we calculate the probability of a region $\mathcal{A}$ of the space, with volume $V(\mathcal{A})$, we get a number proportional to $V(\mathcal{A})$.

From these observations we can arrive at conclusions that are of general validity. First, the homogeneous probability distribution over some space is represented by a constant probability density only if the space is flat (in which case rectilinear systems of coordinates exist) and if we use Cartesian (or rectilinear) coordinates. The other conclusions can be stated as rules:

Rule 1 The probability density representing the homogeneous probability distribution is easily obtained if the expression of the volume element $dV(u_1, u_2, \ldots) = v(u_1, u_2, \ldots) \, du_1 \, du_2 \, \ldots$ of the space is known, as it is then given by $h(u_1, u_2, \ldots) = k \, v(u_1, u_2, \ldots)$, where $k$ is a proportionality constant (that may have physical dimensions).

Rule 2 If there is a metric $g_{ij}(u_1, u_2, \ldots)$ in the space, then the volume element is given by $dV(u_1, u_2, \ldots) = \sqrt{\det \mathbf{g}(u_1, u_2, \ldots)} \, du_1 \, du_2 \, \ldots$, i.e., we have $v(u_1, u_2, \ldots) = \sqrt{\det \mathbf{g}(u_1, u_2, \ldots)}$. The probability density representing the homogeneous probability distribution is, then, $h(u_1, u_2, \ldots) = k \sqrt{\det \mathbf{g}(u_1, u_2, \ldots)}$.

7