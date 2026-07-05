'contacted multiplication' will consist in making the sum (over discrete indices) and the integral (over continuous variables) of the product of the two fields, as in

$$\langle \boldsymbol{\sigma}, \boldsymbol{\varepsilon} \rangle = \int dt \int dV(\mathbf{x}) \, \sigma_{ij}(\mathbf{x}, t) \, \varepsilon^{ij}(\mathbf{x}, t) \, , \tag{247}$$

where the sum over $i, j$ is implicitly notated.

The space of strains and the space of stresses is just one example of *dual spaces*. When one space is called 'the primal space', the other one is called 'the dual space', but this is just a matter of convention.

The product 247 is one example of *duality product*, where one element of the primal space and one element of the dual space are 'multiplied' to form a scalar (that may be a real number or that may have physical dimensions). This implies the sum or the integral over the variables of the functions. Mathematicians say that 'the dual of an space $\mathcal{X}$ is the space of all linear forms over $\mathcal{X}$'. It is true that a given $\boldsymbol{\sigma}$ associates, to any $\boldsymbol{\varepsilon}$, the number defined by equation 247; and that this association defines a linear application. But this rough definition of duality doesn't help readers to understand the actual mathematical structure.

## M.4 Scalar Product in $L_2$ Spaces

When we consider a functional space, its dual appears spontaneously, and we can say that any space is *always* accompanied by its dual space (as in the example strain-stress seen above). Then, the duality product is always defined.

Things are completely different with the scalar product, that it is only defined *sometimes*.

If, for instance, we consider functions $\mathbf{f} = \{f(x)\}$ belonging to a space $\mathcal{F}$, the scalar product is a bilinear form that associates, to any pair of elements $\mathbf{f}_1$ and $\mathbf{f}_2$ of $\mathcal{F}$, a number$^{36}$ denoted $(\mathbf{f}_1, \mathbf{f}_2)$.

Practically, to define a scalar product over a space $\mathcal{F}$, we must first define a symmetric, positive definite operator $\mathbf{C}^{-1}$ mapping $\mathcal{F}$ into its dual, $\widehat{\mathcal{F}}$. The dual of a function $\mathbf{f} = \{f(x)\}$, that we may denote $\widehat{\mathbf{f}} = \{\widehat{f}(x)\}$, is then

$$\widehat{\mathbf{f}} = \mathbf{C}^{-1} \mathbf{f} \, . \tag{248}$$

The scalar product of two elements $\mathbf{f}_1$ and $\mathbf{f}_2$ of $\mathcal{F}$ is then defined as

$$(\mathbf{f}_1, \mathbf{f}_2) = \langle \widehat{\mathbf{f}}_1, \mathbf{f}_2 \rangle = \langle \mathbf{C}^{-1} \mathbf{f}_1, \mathbf{f}_2 \rangle \tag{249}$$

In the context of an infinite-dimensional Gaussian process, some mean and some covariance are always defined. If, for instance, we consider functions $\mathbf{f} = \{f(x)\}$, the mean function may be denoted $\mathbf{f}_0 = \{f_0(x)\}$ and the covariance function (the kernel of the covariance operator) may be denoted $\mathbf{C} = \{C(x, x')\}$. The space of functions we work with, say $\mathcal{F}$, is the set of all the possible random realization of such a Gaussian process with the given mean and the given covariance. The dual of $\mathcal{F}$ can be here identified with the image of $\mathcal{F}$ under $\mathbf{C}^{-1}$, the inverse of the covariance operator (that is a symmetric, positive definite operator). So, denoting $\widehat{\mathcal{F}}$ the dual of $\mathcal{F}$, we can formally write $\widehat{\mathcal{F}} = \mathbf{C}^{-1} \mathcal{F}$ o, equivalently, $\mathcal{F} = \mathbf{C} \widehat{\mathcal{F}}$. The explicit expression of the equation

$$\mathbf{f} = \mathbf{C} \widehat{\mathbf{f}} \tag{250}$$

is

$$f(x) = \int dx' \, C(x, x') \, \widehat{f}(x) \, . \tag{251}$$

Let us denote $\mathbf{W}$ the inverse of the covariance operator,

$$\mathbf{W} = \mathbf{C}^{-1} \, , \tag{252}$$

that is usually named the *weight operator*. As $\mathbf{C} \mathbf{W} = \mathbf{W} \mathbf{C} = \mathbf{I}$, its kernel, $W(x, x')$, the *weight function*, satisfies

$$\int dx' C(x, x') \, W(x', x'') = \int dx' W(x, x') \, C(x', x'') = \delta(x - x'') \, , \tag{253}$$

where $\delta(\cdot)$ is the Dirac's delta 'function'. Typically, the covariance function $C(x, x')$ is a smooth function; then, the weight function $W(x, x')$ is a distribution (sum of Dirac delta 'functions' and its derivatives).

$^{36}$It is usually a real number, but it may have physical dimensions.

67