11.2 Conjugate Gradient

155

### 11.2.3 Quadratic Minimization

The fact that solutions of $A\mathbf{x} = \mathbf{h}$ can be maxima or saddle points complicates things slightly. We will use the concept of positivity for a matrix. A matrix $A$ is said to be positive if $(\mathbf{x}, A\mathbf{x}) \geq 0$ for all $\mathbf{x}$. So one must make a few assumptions which are clarified by the following lemma.

**Lemma 2** *Suppose that $\mathbf{z}$ is a solution of the system $A\mathbf{z} = \mathbf{h}$, $A$ is positive and symmetric, and $f(\mathbf{x})$ is the quadratic form associated with $A$, then*

$$f(\mathbf{x}) = f(\mathbf{z}) + \frac{1}{2}((\mathbf{x} - \mathbf{z}), A(\mathbf{x} - \mathbf{z})). \tag{11.23}$$

This means that $\mathbf{z}$ must be a minimum of the quadratic form since the second term on the right is positive. Thus the value of $f$ at an arbitrary point $\mathbf{x}$ must be greater than its value at $\mathbf{z}$. To prove this, let $\mathbf{x} = \mathbf{z} + \mathbf{p}$ where $A\mathbf{z} = \mathbf{h}$. Then

$$\begin{aligned} f(\mathbf{x}) &= f(\mathbf{z} + \mathbf{p}) = \frac{1}{2}((\mathbf{z} + \mathbf{p}), A(\mathbf{z} + \mathbf{p})) - (\mathbf{h}, (\mathbf{z} + \mathbf{p})) + c. \\ &= f(\mathbf{z}) + \frac{1}{2}\{(\mathbf{z}, A\mathbf{p}) + (\mathbf{p}, A\mathbf{z}) + (\mathbf{p}, A\mathbf{p})\} - (\mathbf{h}, \mathbf{p}). \end{aligned}$$

If $A$ is symmetric, the first two terms in brackets are equal, hence:

$$f(\mathbf{x}) = f(\mathbf{z}) + \frac{1}{2}(\mathbf{p}, A\mathbf{p}) + (A\mathbf{z}, \mathbf{p}) - (\mathbf{h}, \mathbf{p}).$$

But by assumption $A\mathbf{z} = \mathbf{h}$, so that

$$f(\mathbf{x}) = f(\mathbf{z}) + \frac{1}{2}(\mathbf{p}, A\mathbf{p}) = f(\mathbf{z}) + \frac{1}{2}((\mathbf{x} - \mathbf{z}), A(\mathbf{x} - \mathbf{z}))$$

which completes the proof.

As a corollary one observes that if $A$ is positive definite as well as symmetric, then $\mathbf{z}$ is the unique minimum of $f(\mathbf{z})$ since in that case the term $((\mathbf{x} - \mathbf{z}), A(\mathbf{x} - \mathbf{z}))$ is equal to zero if and only if $\mathbf{x} = \mathbf{z}$. It will be assumed, unless otherwise stated, that the matrices are symmetric and positive definite.

The level surfaces of a positive definite quadratic form (i.e., the locus of points for which $f(\mathbf{x})$ is constant) is an ellipsoid centered about the global minimum. And the semiaxes of this ellipsoid are related to the eigenvalues of the defining matrix.

The negative gradient of any function points in the direction of steepest descent of the function. Calling this direction $r$ one has

$$\mathbf{r} = -f'(\mathbf{x}) = \mathbf{h} - A\mathbf{x} = A(\mathbf{z} - \mathbf{x}) \tag{11.24}$$

since $A\mathbf{z} = \mathbf{h}$. The idea behind the method of steepest descents is to repeatedly minimize $f$ along lines defined by the residual vector. A prescription for this is given by the following lemma.

1