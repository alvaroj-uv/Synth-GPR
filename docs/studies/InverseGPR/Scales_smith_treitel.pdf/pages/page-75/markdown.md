60

SVD and Resolution in Least Squares

$$A A ^ { T } \mathbf { u } _ { \mathrm { i } } = \lambda _ { i } ^ { 2 } \mathbf { u } _ { \mathrm { i } }$$

for $\lambda _ { i } ^ { 2 }$ equal to 2 and 1. So

$$\left[ \begin{array} { l l } { 2 } & { 0 } \\ { 0 } & { 1 } \end{array} \right] \left( \begin{array} { l } { u _ { 1 1 } } \\ { u _ { 2 1 } } \end{array} \right) = 2 \left( \begin{array} { l } { u _ { 1 1 } } \\ { u _ { 2 1 } } \end{array} \right) .$$

The only way this can be true is if

$$\mathbf { u } _ { 1 } = \left( \begin{array} { l } { 1 } \\ { 0 } \end{array} \right) .$$

Similarly, for $\lambda _ { i } ^ { 2 } = 1$ we have

$$\mathbf { u } _ { 2 } = \left( \begin{array} { l } { 0 } \\ { 1 } \end{array} \right) .$$

In this example, there is no data null space:

$$U _ { r } = U = \left[ \begin{array} { l l } { 1 } & { 0 } \\ { 0 } & { 1 } \end{array} \right]$$

We could also solve the eigenvalue problem for $A ^ { T } A$ to get the model eigenvectors $\mathbf { v } _ { \mathrm { i } }$, but a shortcut is to take advantage of the coupling of the model and data eigenvectors, namely that $A ^ { T } U _ { r } = V _ { r } \Lambda _ { r }$, so all we have to do is take the inner product of $A ^ { T }$ with the data eigenvectors and divide by the corresponding singular value. But remember, the singular value is the square root of $\lambda ^ { 2 }$, so

$$\mathbf { v } _ { 1 } = { \frac { 1 } { \sqrt { 2 } } } \left[ \begin{array} { l l } { 1 } & { 0 } \\ { 1 } & { 0 } \\ { 0 } & { 1 } \end{array} \right] \left( \begin{array} { l } { 1 } \\ { 0 } \end{array} \right) = \left( \begin{array} { l } { { \frac { 1 } { \sqrt { 2 } } } } \\ { { \frac { 1 } { \sqrt { 2 } } } } \\ { 0 } \end{array} \right)$$

and

$$\mathbf { v } _ { 2 } = \left[ \begin{array} { l l } { 1 } & { 0 } \\ { 1 } & { 0 } \\ { 0 } & { 1 } \end{array} \right] \left( \begin{array} { l } { 0 } \\ { 1 } \end{array} \right) = \left( \begin{array} { l } { 0 } \\ { 0 } \\ { 1 } \end{array} \right) .$$

This gives us

$$V _ { r } = \left[ \begin{array} { l l } { { \frac { 1 } { \sqrt { 2 } } } } & { 0 } \\ { { \frac { 1 } { \sqrt { 2 } } } } & { 0 } \\ { 0 } & { 1 } \end{array} \right] .$$

To find the model null space we must solve $A V _ { 0 } = 0$:

$$\left[ \begin{array} { l l l } { 1 } & { 1 } & { 0 } \\ { 0 } & { 0 } & { 1 } \end{array} \right] \left( \begin{array} { l } { v _ { 1 3 } } \\ { v _ { 2 3 } } \\ { v _ { 3 3 } } \end{array} \right) = 0 .$$

1