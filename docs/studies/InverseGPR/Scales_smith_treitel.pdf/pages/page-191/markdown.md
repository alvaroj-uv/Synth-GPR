176

Iterative Linear Solvers

nx =8;

A = Table[1/(i+j-1.),{i,nx},{j,nx}];

The condition number of this matrix is $10^{10}$. The exact solution to the system $A\mathbf{x} = \mathbf{y}$, where $\mathbf{y}$ consists of all ones is:

$$(-8,504, -7560, 46200, -138600, 216216, -168168, 51480).$$

After just 5 iterations, using 16 digits of precision, $CG$ produces the following solution:

$$(0.68320, -4.01647, -127.890, 413.0889, -19.3687, -498.515, -360.440, 630.5659)$$

which doesn't look very promising. However, even after only 5 iterations we have excellent approximations to the first 4 eigenvalues. The progression towards these eigenvalues is illustrated in the following table, which shows the fractional error in each eigenvalue as a function of $CG$ iterations. Even after only one iteration, we've already got the first eigenvalue to within 12%. After 3 iterations, we have the first eigenvalue to within 1 part in a million and the second eigenvalue to within less than 1%.

|  Eigenvalue | 1.6959389 | 0.2981252 | 0.0262128 | 0.0014676 | 0.0000543 | Iteration  |
| --- | --- | --- | --- | --- | --- | --- |
|  Fractional | 0.122 |  |  |  |  | 1  |
|  error in | 0.015 | 0.52720 |  |  |  | 2  |
|  CG-computed | 1.0 $10^{-5}$ | 0.006 | 1.284 |  |  | 3  |
|  eigenvalues | 9.0 $10^{-12}$ | 1.9 $10^{-7}$ | 0.002 | 1.184 |  | 4  |
|   | 0.0 | 7.3 $10^{-15}$ | 1.13 $10^{-8}$ | 8.0 $10^{-4}$ | 1.157 | 5  |

## 11.4.2 Finite Precision Arithmetic

Using $CG$ or Lanczos methods to compute the spectrum of a matrix, rather than simply solving linear systems, gives a close look at the very peculiar effects of rounding error on these algorithms. Intuitively one might think that the main effects of finite precision arithmetic would be a general loss of accuracy of the computed eigenvalues. This does not seem to be the case. Instead, 'spurious' eigenvalues are calculated. These spurious eigenvalues fall into two categories. First, there are numerically multiple eigenvalues; in other words duplicates appear in the list of computed eigenvalues. Secondly, and to a much lesser extent, there are extra eigenvalues. The appearance of spurious eigenvalues is associated with the loss of orthogonality of the $CG$ search vectors. A detailed explanation of this phenomenon, which was first explained by Paige [Pai71] is beyond the scope of this discussion. For an excellent review see ([CW85], Chapter 4). In practice, the duplicate eigenvalues are not difficult to detect and remove. Various strategies have been developed for identifying the extra eigenvalues. These rely either on changes in the $T$ matrix from iteration to iteration (in other words, on changes in $T_m$ as $m$ increases), or differences in the spectra between $T$ (at a given iteration) and the principle submatrix of $T$ formed by deleting its first row and column. An extensive

1