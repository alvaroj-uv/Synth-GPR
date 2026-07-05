## M.7 The Green Operator

The pressure field $p(\mathbf{x}, t)$ propagating in an elastic medium with uncompressibility modulus $\kappa(\mathbf{x})$ and volumetric mass $\rho(\mathbf{x})$ satisfies the 'acoustic wave equation'

$$\frac{1}{\kappa(\mathbf{x})} \frac{\partial^2 p}{\partial t^2}(\mathbf{x}, t) - \operatorname{div} \left( \frac{1}{\rho(\mathbf{x})} \mathbf{grad} p(\mathbf{x}, t) \right) = S(\mathbf{x}, t) \ . \tag{308}$$

Here, $\mathbf{x}$ denotes a point inside the medium (the coordinate system being still unspecified), $t$ is the Newtonian time, and $S(\mathbf{x}, t)$ is a source function. To simplify the notations, the variables $\mathbf{x}$ and $t$ will be dropped when there is no risk of confusion. For instance, the equation above will be written

$$\frac{1}{\kappa} \frac{\partial^2 p}{\partial t^2} - \operatorname{div} \left( \frac{1}{\rho} \mathbf{grad} p \right) = S \ . \tag{309}$$

Also, I shall denote $\mathbf{p}$ the function $\{p(\mathbf{x}, t)\}$ as a whole, and not its value at a given point of space and time. Similarly, $\mathbf{S}$ shall denote the source function $S(\mathbf{x}, t)$ .

For fixed $\kappa(\mathbf{x})$ and $\rho(\mathbf{x})$ , the wave equation above can be written, for short,

$$\mathbf{L} \mathbf{p} = \mathbf{S} \ , \tag{310}$$

where $\mathbf{L}$ is the second order differential operator defined through equation 309. In order to define an unique wavefield $\mathbf{p}$ , we have to prescribe some boundary and initial conditions. An example of those are, if we work inside the time interval $(t_1, t_2)$ , and inside a volume $V$ bounded by the surface $S$ ,

$$\begin{array}{l} p(\mathbf{x}, t_1) = 0 \quad ; \quad \mathbf{x} \in V \\ \dot{p}(\mathbf{x}, t_1) = 0 \quad ; \quad \mathbf{x} \in V \\ p(\mathbf{x}, t) = 0 \quad ; \quad \mathbf{x} \in S \ ; \ t \in (t_1, t_2) \ . \end{array} \tag{311}$$

Here, a dot means time derivative. With prescribed initial and boundary conditions, then, there is an one to one correspondence between the source field $\mathbf{S}$ and the wavefield $\mathbf{p}$ . The inverse of the wave equation operator, $\mathbf{L}^{-1}$ , is called the Green operator, and is denoted $\mathbf{G}$ :

$$\mathbf{G} = \mathbf{L}^{-1} \ . \tag{312}$$

We can then write

$$\mathbf{L} \mathbf{p} = \mathbf{S} \quad \Longleftrightarrow \quad \mathbf{p} = \mathbf{G} \mathbf{S} \ . \tag{313}$$

As $\mathbf{L}$ is a differential operator, its inverse $\mathbf{G}$ is an integral operator. The kernel of the Green operator is named the Green function, and is usually denoted $G(\mathbf{x}, t; \mathbf{x}', t')$ . The explicit expression for $\mathbf{p} = \mathbf{G} \mathbf{S}$ is then

$$p(\mathbf{x}, t) = \int_V dV(\mathbf{x}') \int_{t_1}^{t_2} dt' \ G(\mathbf{x}, t; \mathbf{x}', t') \ S(\mathbf{x}', t') \ . \tag{314}$$

It is easy to demonstrate$^{39}$ that the wave equation operator $\mathbf{L}$ is a symmetric operator, so this is also true for the Green operator $\mathbf{G}$ . But we have seen that the transpose operators work in spaces with have dual boundary conditions (see section 30 above).

Using the method outlined in section 30, the boundary conditions dual to those in equations 311 are

$$\begin{array}{l} p(\mathbf{x}, t_2) = 0 \quad ; \quad \mathbf{x} \in V \\ \dot{p}(\mathbf{x}, t_2) = 0 \quad ; \quad \mathbf{x} \in V \\ p(\mathbf{x}, t) = 0 \quad ; \quad \mathbf{x} \in S \ ; \ t \in (t_1, t_2) \ , \end{array} \tag{315}$$

i.e., we have final conditions of rest instead of initial conditions of rest (and the same surface condition). We have to understand that while the equation $\mathbf{L} \mathbf{p} = \mathbf{S}$ is associated to the boundary conditions 311, equations like

$$\mathbf{L}^T \widehat{\mathbf{p}} = \widehat{\mathbf{S}} \quad ; \quad \widehat{\mathbf{p}} = \mathbf{G}^T \widehat{\mathbf{S}} \tag{316}$$

$^{39}$This comes from the property that the derivative operator is antisymmetric, (so that the second derivative is a symmetric operator) and from the properties $\mathbf{grad}^T = -\operatorname{div}$ and $\operatorname{div}^T = -\mathbf{grad}$ , mentioned in section protect30.

73