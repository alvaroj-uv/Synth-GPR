168

Iterative Linear Solvers

Try to assess what's going on here in terms of the numerical loss of A-orthogonality of the search vectors. You'll need to do more than look at adjacent search vectors. You might try comparing $\mathbf{p}_0$ with all subsequent search vectors.

Now see if you can fix this problem simply by doing more iterations. If you get the right answer ultimately, why? What are the search vectors doing during these extra iterations. This is a subtle problem. Don't be discouraged if you have trouble coming up with a compelling answer.

Are the residuals monotonically decreasing? Should they be?

What's the condition number of the matrix for $n = 6$?

## 11.3 Practical Implementation

### 11.3.1 Sparse Matrix Data Structures

Clearly one needs to store all of the nonzero elements of the sparse matrix and enough additional information to be able to unambiguously reconstruct the matrix. But these two principles leave wide latitude for data structures.$^{\text{d}}$ It would seem that the more sophisticated a data structure, and hence the more compact its representation of the matrix, the more difficult are the matrix operations. Probably the simplest scheme is to store the row and column indices in separate integer arrays. Calling the three arrays $elem$ (a real array containing the nonzero elements of $A$), $irow$ and $icol$, one has

$$
elem(i) = A(irow(i), icol(i)) \qquad i = 1, 2, \dots, NZ \tag{11.55}
$$

where $NZ$ is the number of nonzero elements in the matrix. Thus if the matrix is

$$
\left( \begin{array}{cccc} 1 & 0 & 0 & 4 \\ 3 & -2 & 0 & 0 \\ 0 & 0 & -1 & 0 \end{array} \right)
$$

then $elem = (1, 4, 3, -2, -1)$, $irow = (1, 1, 2, 2, 3)$, and $icol = (1, 4, 1, 2, 3)$. The storage requirement for this scheme is $nzero$ real words plus $2 \times nzero$ integer words. But clearly there is redundant information in this scheme. For example, instead of storing all of the row indices one could simply store a pointer to the beginning of each new row within $elem$. Then $irow$ would be $(1, 3, 5, 6)$. The 6 is necessary so that one knows how many nonzero elements there are in the last row of $A$. The storage requirement for this scheme (probably the most common in use) is $nzero$ real words plus $nzero + nrow$ integer words, where $nrow$ is the number of rows in $A$. In the first scheme, call it the

$^{\text{d}}$A well-written and thorough introduction to sparse matrix methods is contained in Serge Pissanetsky's book *Sparse Matrix Technology* [Pis84].

1