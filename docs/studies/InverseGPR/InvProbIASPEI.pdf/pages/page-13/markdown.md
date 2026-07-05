## 2.5 Marginal Probability Density

In the special circumstance described above, where we have a Cartesian product of two spaces, $\mathcal{X} = \mathcal{U} \times \mathcal{V}$, given a 'joint' probability density $f(\mathbf{u}, \mathbf{v})$, it is possible to give an intrinsic sense to the definitions

$$f_u(\mathbf{u}) = \int_{\mathcal{V}} d\mathbf{v} \ f(\mathbf{u}, \mathbf{v}) \quad ; \quad f_v(\mathbf{v}) = \int_{\mathcal{U}} d\mathbf{u} \ f(\mathbf{u}, \mathbf{v}) \quad . \tag{20}$$

These two densities are called *marginal probability densities*. Their intuitive interpretation is clear, as the 'projection' of the joint probability density respectively over $\mathcal{U}$ and over $\mathcal{V}$.

## 2.6 Independence and Bayes Theorem

Dropping the index $_0$ in equation 19 and using the second of equations 20 gives

$$f_{u|v}(\mathbf{u}|\mathbf{v}) = \frac{f(\mathbf{u}, \mathbf{v})}{f_v(\mathbf{v})} \quad , \tag{21}$$

or, equivalently, $f(\mathbf{u}, \mathbf{v}) = f_{u|v}(\mathbf{u}|\mathbf{v}) \ f_v(\mathbf{v})$. As we can also define $f_{v|u}(\mathbf{v}|\mathbf{u})$, we have the two equations

$$\begin{array}{rcl} f(\mathbf{u}, \mathbf{v}) & = & f_{u|v}(\mathbf{u}|\mathbf{v}) \ f_v(\mathbf{v}) \\ f(\mathbf{u}, \mathbf{v}) & = & f_{v|u}(\mathbf{v}|\mathbf{u}) \ f_u(\mathbf{u}) \quad , \end{array} \tag{22}$$

that can be read as follows: 'when we work in a space that is the Cartesian product $\mathcal{U} \times \mathcal{V}$ of two subspaces, a joint probability density can always be expressed as the product of a conditional times a marginal'.

From these last equations it follows the expression

$$f_{u|v}(\mathbf{u}|\mathbf{v}) = \frac{f_{v|u}(\mathbf{v}|\mathbf{u}) \ f_u(\mathbf{u})}{f_v(\mathbf{v})} \quad , \tag{23}$$

known as the *Bayes theorem*, and generally used as the starting point to solve inverse problems. We do not think this is a useful setting, and we prefer in this paper *not* to use the Bayes theorem (or, more precisely, not to use the intuitive paradigm usually associated to it).

It also follows from equations 22 that the two conditions

$$f_{u|v}(\mathbf{u}|\mathbf{v}) = f_u(\mathbf{u}) \quad ; \quad f_{v|u}(\mathbf{v}|\mathbf{u}) = f_v(\mathbf{v}) \tag{24}$$

are equivalent. It is then said that $\mathbf{u}$ and $\mathbf{v}$ are *independent parameters* (with respect to the probability density $f(\mathbf{u}, \mathbf{v})$). The term 'independent' is easy to understand, as the conditional of any of the two (vector) variables, given the other variable equals the (unconditional) marginal of the variable. Then, one clearly has

$$f(\mathbf{u}, \mathbf{v}) = f_u(\mathbf{u}) \ f_v(\mathbf{v}) \quad , \tag{25}$$

i.e., for independent variables, the joint probability density can be simply expressed as the product of the two marginals.

## 3 Monte Carlo Methods

When a probability distribution has been defined, we face the problem of how to 'use' it. The definition of 'central estimators' (like the mean or the median) and 'estimators of dispersion' (like the covariance matrix) lacks generality as it is quite easy to find examples (like multimodal distributions in highly-dimensional spaces) where these estimators fail to have any interesting meaning.

When a probability distribution has been defined over a space of low dimension (say, from one to four dimensions) we can directly represent the associated probability density. This is trivial in one or two dimensions. It is easy in three dimensions, and some tricks may allow us to represent a four-dimensional probability distribution, but clearly this approach cannot be generalized to the high dimensional case.

Let us explain the only approach that seems practical, with help of figure 3. At the left of the figure, there is an explicit representation of a 2D probability distribution (by means of the associated probability density or the associated (2D) volumetric probability). In the middle, some random points have been generated (using the

13