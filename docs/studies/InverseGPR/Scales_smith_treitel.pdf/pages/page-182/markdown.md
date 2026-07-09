11.2 Conjugate Gradient

167

$$\mathbf{h} - A\mathbf{x}_0, \mathbf{r}_0 = \mathbf{p}_0 = A^T(\mathbf{h} - A\mathbf{x}_0) = A^T\mathbf{s}_0, \mathbf{q}_0 = A\mathbf{p}_0. \text{ Then for } k = 0, 1, 2, \dots$$

$$\alpha_{k+1} = \frac{(\mathbf{r}_k, \mathbf{r}_k)}{(\mathbf{q}_k, \mathbf{q}_k)}$$

$$\mathbf{x}_{k+1} = \mathbf{x}_k + \alpha_{k+1}\mathbf{p}_k$$

$$\mathbf{s}_{k+1} = \mathbf{s}_k - \alpha_{k+1}\mathbf{q}_k$$

$$\mathbf{r}_{k+1} = A^T\mathbf{s}_{k+1} \tag{11.54}$$

$$\beta_{k+1} = \frac{(\mathbf{r}_{k+1}, \mathbf{r}_{k+1})}{(\mathbf{r}_k, \mathbf{r}_k)}$$

$$\mathbf{p}_{k+1} = \mathbf{r}_{k+1} + \beta_{k+1}\mathbf{p}_k$$

$$\mathbf{q}_{k+1} = A\mathbf{p}_{k+1}$$

[Cha78] shows that factoring the matrix multiplications in this way results in improved rounding behavior.

For a more detailed discussion of the applications of CGLS see [HS52], [Läu59], [Hes75], [Law73], and [Bjö75]. Paige and Saunders [PS82] present a variant of CGLS called LSQR which is very popular since it is freely available through the Transactions on Mathematical Software. [PS82] also has a very useful discussion of stopping criteria for least squares problems. Our experience is that CGLS performs just as well as LSQR and since the CG code is so easy to write, it makes sense to do this in order to easily take advantage of the kinds of weighting and regularization schemes that will be discussed later.

### 11.2.9 Computer Exercise: Conjugate Gradient

Write a program implementing CG for symmetric, positive definite matrices. Consider the following matrix, right-hand side, and initial approximation:

n=6;
A = Table[1/(i+j-1),{i,n},{j,n}];
h = Table[1,{i,nx}];
x = Table[0,{i,nx}];

To switch to floating point arithmetic, use $i+j-1$. instead of $i+j-1$ in the specification of the matrix.

The first step is to familiarize yourself with CG and make sure your code is working. First try $n = 4$ or $n = 5$. On a PC, floating point arithmetic should work nearly perfectly in the sense that you get the right answer in $n$ iterations. Now go to $n = 6$. You should begin to see significant discrepancies between the exact and floating point answers if you use only $n$ iterations. On other machines, these particular values of $n$ may be different, but the trend will always be the same.

1