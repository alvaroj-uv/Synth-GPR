ISSN 2007-9737

Computer Modeling of the Outgoing GPR Signal

7

and in [14] this technique is applied to Maxwell equations in case of horizontally layered medium of any anisotropy. The above-mentioned studies of direct and inverse problems of electrical prospecting refer to a series of problems when observations are carried out on the daytime surface of plane-parallel media.

If the surface has a relief, for example, in archaeological problems of investigation of barrows, then considering the influence of relief of the surface on the electric field and on the results of 2D and 3D inversion of electric tomography (ET) survey data is an important task.

In [25] the effectiveness of elimination of topographical effects in 2D inversion programs that include topography in the grid in the presence of daylight surface topography has been studied. Modeling of the apparent resistivity curves has been performed by the method of integral equations.

Experimental studies were carried out on the laboratory polygon using Loza-V GPR. Real data are used for numerical calculations to determine the shape and tabular value of the emitted signal.

The work also uses the methodology for signal cleaning from noise and interference and signal recovery given in papers [7, 22].

## 2 Mathematical Model for Source Recovery

The propagation of electromagnetic waves in a medium is described by a system of Maxwell's equations [17].

With a special choice of a perturbation source, namely if the source is a long cable located along the coordinate axis and assuming that the functions describing the geoelectric section depend on one variable, namely the depth, then the system of Maxwell equations is simplified and we have a formulation problem for the geoelectric equation [17].

This model is suitable for the study of direct and inverse problems in the case of slime media.

Let us consider the geoelectric equation in cylindrical coordinate system:

$$\varepsilon w_{tt} + \sigma w_t = \frac{1}{\mu} \left( w_{rr} + \frac{1}{r} w_r + w_{zz} \right) + \frac{1}{r} \delta(r) \delta(z - z_*) q(t). \tag{1}$$

The initial conditions are of the form:

$$w(r, z, 0) = 0, \ w_t(r, z, 0) = 0. \tag{2}$$

Assume that $\frac{\partial w}{\partial r}$ is bounded at $r \to 0$. Let the following relation take place:

$$u(\xi, z, \omega) = \int_{-\infty}^{\infty} e^{i\omega t} \int_{0}^{\infty} w(r, z, t) r J_0(\xi r) dr dt. \tag{3}$$

Then, task (1)-(2) will take the form:

$$u_{zz} - b^2(z) u = \delta(z - z_*) \hat{q}(\omega), \tag{4}$$

$$[u_z]_{z=0} = 0, [u]_{z=0} = 0. \tag{5}$$

Let us use the definition of the generalized derivative: $u_z = \{u_z\} + [u]_{z*} \delta(z - z_*)$, in order to transfer the right-hand side of equation (4) to the boundary condition, then finally write problem (4)-(5), differently:

$$u_{zz} - b^2(z) u = 0, \tag{6}$$

$$[u_z]_{z_*=0} = 0, [u]_{z_*=0} = 0, \tag{7}$$

$$u[z]_{z=z_*} = \hat{q}(\omega), [u]_{z=z_*} = 0. \tag{8}$$

Using standard techniques, by analogy as in [13, 14], let us go to the Riccati equation, in order to derive an analytical solution, we have:

$$u_z = yu \Rightarrow y' + y^2 = b^2, \tag{9}$$

$$z \in (-\infty, z_*), z \in [0, \infty), \tag{10}$$

$$y(z) = b_0, \tag{11}$$

$$y(z) = -b_1 = y^0. \tag{12}$$

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12

doi: 10.13053/CyS-27-1-4543