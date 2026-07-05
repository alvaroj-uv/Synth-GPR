154

Iterative Linear Solvers

## 11.2 Conjugate Gradient

Conjugate gradient is by far the most widely used iterative method for solving large linear systems. In its simplest forms it is easy to program and use, yet retains the flexibility to tackle some very demanding problems. Theoretically, $CG$ is a descendant of the method of steepest descent, which is where the discussion begins. But first, a few definitions.

### 11.2.1 Inner Products

We will assume that vectors lie in finite dimensional Cartesian spaces such as $\mathbf{R}^n$. An inner product is a scalar-valued function on $\mathbf{R}^n \times \mathbf{R}^n$, whose values are denoted by $(\mathbf{x}, \mathbf{y})$, which has the following properties:

$$\text{positivity} \quad (\mathbf{x}, \mathbf{x}) \geq 0; (\mathbf{x}, \mathbf{x}) = 0 \Leftrightarrow \mathbf{x} = 0 \tag{11.17}$$

$$\text{symmetry} \quad (\mathbf{x}, \mathbf{y}) = (\mathbf{y}, \mathbf{x}) \tag{11.18}$$

$$\text{linearity} \quad (\mathbf{x}, \mathbf{y} + \mathbf{z}) = (\mathbf{x}, \mathbf{y}) + (\mathbf{x}, \mathbf{z}) \tag{11.19}$$

$$\text{continuity} \quad (\alpha \mathbf{x}, \mathbf{y}) = \alpha (\mathbf{x}, \mathbf{y}). \tag{11.20}$$

This definition applies to general linear spaces. A specific inner product for Cartesian spaces is $(\mathbf{x}, \mathbf{y}) \equiv \mathbf{x}^T \cdot \mathbf{y} = \sum_{i=1}^n x_i y_i$

### 11.2.2 Quadratic Forms

A quadratic form on $\mathbf{R}^n$ is defined by

$$f(\mathbf{x}) = \frac{1}{2}(\mathbf{x}, A\mathbf{x}) - (\mathbf{h}, \mathbf{x}) + c \tag{11.21}$$

where $A \in \mathbf{R}^{n \times n}$; $\mathbf{h}, \mathbf{x} \in \mathbf{R}^n$; and $c$ is a constant. The quadratic form is said to be symmetric, positive, or positive definite, according to whether the matrix $A$ has these properties. The gradient of a symmetric quadratic form $f$ is

$$f'(\mathbf{x}) = A\mathbf{x} - \mathbf{h}. \tag{11.22}$$

This equation leads to the key observation: finding critical points of quadratic forms (i.e., vectors $\mathbf{x}$ where $f'(\mathbf{x})$ vanishes) is very closely related to solving linear systems.

1