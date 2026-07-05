4.8 Orthogonal decomposition of rectangular matrices

53

then the eigenvalue problem for $S$ reduces to two coupled eigenvalue problems, one for $A$ and one for $A^T$

$$A^T \mathbf{u}_i = \lambda_i \mathbf{v}_i \tag{4.81}$$

$$A \mathbf{v}_i = \lambda_i \mathbf{u}_i. \tag{4.82}$$

We can multiply the first of these equations by $A$ and the second by $A^T$ to get

$$A^T A \mathbf{v}_i = \lambda_i^2 \mathbf{v}_i \tag{4.83}$$

$$A A^T \mathbf{u}_i = \lambda_i^2 \mathbf{u}_i. \tag{4.84}$$

So we see, once again, that the model eigenvectors $\mathbf{u}_i$ are eigenvectors of $A A^T$ and the data eigenvectors $\mathbf{v}_i$ are eigenvectors of $A^T A$. Also note that if we change sign of the eigenvalue we see that $(-\mathbf{u}_i, \mathbf{v}_i)$ is an eigenvector too. So if there are $r$ pairs of nonzero eigenvalues $\pm \lambda_i$ then there are $r$ eigenvectors of the form $(\mathbf{u}_i, \mathbf{v}_i)$ for the positive $\lambda_i$ and $r$ of the form $(-\mathbf{u}_i, \mathbf{v}_i)$ for the negative $\lambda_i$.

Keep in mind that the matrices $U$ and $V$ whose columns are the date and model eigenvectors are square (respectively $n \times n$ and $m \times m$) and orthogonal. Therefore we have $U^T U = U U^T = I_n$ and $V^T V = V V^T = I_m$. But it is important to distinguish between the eigenvectors associated with zero and nonzero eigenvalues. Let $U_r$ and $V_r$ be the matrices whose columns are the $r$ model and data eigenvectors associated with the $r$ nonzero eigenvalues and $U_0$ and $V_0$ be the matrices whose columns are the eigenvectors associated with the zero eigenvalues, and let $\Lambda_r$ be the $r \times r$ square, diagonal matrix containing the $r$ nonzero eigenvalues. Then we have by 4.81 and 4.82 the following eigenvalue problem

$$A V_r = U_r \Lambda_r \tag{4.85}$$

$$A^T U_r = V_r \Lambda_r \tag{4.86}$$

$$A V_0 = 0 \tag{4.87}$$

$$A^T U_0 = 0. \tag{4.88}$$

Since the full matrices $U$ and $V$ satisfy $U^T U = U U^T = I_n$ and $V^T V = V V^T = I_m$ it can be readily seen that $A V = U \Lambda$ implies $A = U \Lambda V^T$ and therefore

$$A = [U_r, U_0] \begin{bmatrix} \Lambda_r & \mathbf{0} \\ \mathbf{0} & \mathbf{0} \end{bmatrix} \begin{bmatrix} V_r^T \\ V_0^T \end{bmatrix} = U_r \Lambda_r V_r^T, \tag{4.89}$$

This is the singular value decomposition. Notice that $\mathbf{0}$ represent rectangular matrices of zeros. Since $\Lambda_r$ is $r \times r$ and $\Lambda$ is $n \times m$ then the lower left block of zeros must be $n - r \times r$, the upper right must be $r \times m - r$ and the lower right must be $n - r \times m - r$.

It is important to keep the subscript $r$ in mind since the fact that $A$ can be reconstructed from the eigenvectors associated with the nonzero eigenvalues means that the

0