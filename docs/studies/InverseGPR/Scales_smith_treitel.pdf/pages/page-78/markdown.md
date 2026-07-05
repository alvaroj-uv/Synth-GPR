63

## No Null Space

First consider the case in which there is no data or model null space. This can only happen when $r = m = n$, in which case the generalized inverse is the ordinary inverse.

## A Data Null Space

Next consider the case in which there is a data null space $U_0$ but no model null space ($n > m$). Since $A^T U_0 = 0$, it follows that $U_0^T A = 0$. And hence, the forward operator $A$ always maps models into vectors that have no component in $U_0$. That means that if there is a data null space, and **if the data have a component in this null space, then it will be impossible to fit them exactly**.

That being the case, it would seem reasonable to try to minimize the misfit between observed and predicted data, say,

$$\min \|A\mathbf{m} - \mathbf{d}\|^2, \tag{5.1}$$

where $\mathbf{m}$ is an element of the model space. I.e., least-squares. A least-squares minimizing model must be associated with a critical point of this mis-fit function. Differentiating Equation 5.1 with respect to $\mathbf{m}$ and setting the result equal to zero results in the *normal equations*:

$$A^T A \mathbf{m} = A^T \mathbf{d}. \tag{5.2}$$

There are many ways to derive the normal equations. In the next section we will derive them without using any calculus. But it is not too hard to do the differentiation in Equation 5.1. First, write the norm-squared as an inner product:

$$\|A\mathbf{m} - \mathbf{d}\|^2 = (A\mathbf{m} - \mathbf{d}, A\mathbf{m} - \mathbf{d}).$$

Expand this. You'll get a sum of 4 inner products, such as $(A\mathbf{m}, A\mathbf{m})$. You can differentiate these with respect to each of the components of $\mathbf{m}$ if you like, but you can do this in vector notation with a little practice. For instance, the derivative of $(\mathbf{m}, \mathbf{m})$ with respect to $\mathbf{m}$ is $2\mathbf{m}$. The derivative of $(\mathbf{m}, \mathbf{a})$ (which equals $(\mathbf{a}, \mathbf{m})$) with respect to $\mathbf{m}$ is $\mathbf{a}$. Further, since $(A\mathbf{m}, A\mathbf{m}) = (A^T A \mathbf{m}, \mathbf{m}) = (\mathbf{m}, A^T A \mathbf{m})$, the derivative of $(A\mathbf{m}, A\mathbf{m})$ with respect to $\mathbf{m}$ is $2A^T A \mathbf{m}$. You can move $A$ back and forth across the inner product just by taking the transpose.

Now, by Equation 4.89

$$A^T A = (U_r \Lambda_r V_r^T)^T U_r \Lambda_r V_r^T = V_r \Lambda_r^T U_r^T U_r \Lambda_r V_r^T.$$

At this point we have to be a bit careful. We can be sure that $UU^T = U^T U = I_n$, an n-dimensional identity. And that $VV^T = V^T V = I_m$. But this is *not* true of $V_r$ if there

1