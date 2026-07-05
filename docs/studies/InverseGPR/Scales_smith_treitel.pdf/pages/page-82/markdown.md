67

It is obvious that $m_3 = 1$ and that there are not enough equations to specify $m_1$ or $m_2$. All we can say at this point is that $m_1 + m_2 = 1$. Some possible solutions then are: $m_1 = 0, m_2 = 1, m_1 = 1, m_2 = 0, m_1 = .5, m_2 = .5$, and so on. All of these choices explain the “data”.

The generalized inverse solution is $A^{\dagger}\mathbf{d} = (1/2, 1/2, 1)^T$. Here we see the key feature of least squares (or generalized inverses): when faced with uncertainty least squares splits the difference.

### 5.0.4 Resolution

Resolution is all about how precisely one can infer model parameters from data. The issue is complicated by all of the uncertainties that exist in any inverse problem: uncertainties in the forward modeling, the discretization of the model itself (i.e., replacing continuous functions by finite-dimensional vectors), noise in the data, and uncertainties in the constraints or *a priori* information we have. This is why we need a fairly elaborate statistical machinery to tackle such problems. However, there are situations in which resolution becomes relatively straightforward—whether these situations pertain in practice is another matter.

One of these occurs when the problem is linear and the only uncertainties arise from random noise in the data. In this case the *true* Earth model is linearly related to the observed data by $\mathbf{d} = A\mathbf{m} + \mathbf{e}$ where $\mathbf{e}$ is an $n$-dimensional vector of random errors. The meaning of this equation is as follows: if there were no random noise in the problem, $\mathbf{e}$ would be zero and the true Earth model would predict the data exactly ($\mathbf{d} = A\mathbf{m}$). We could then estimate the true model by applying the pseudo-inverse of $A$ to the measurements. On the other hand, if $\mathbf{e}$ is nonzero, $\mathbf{d} = A\mathbf{m} + \mathbf{e}$, we still get the generalized inverse solution by applying the pseudo-inverse to the data: $\mathbf{m}^{\dagger} = A^{\dagger}\mathbf{d}$. It follows that

$$\mathbf{m}^{\dagger} = A^{\dagger} (A\mathbf{m} + \mathbf{e}). \tag{5.5}$$

Later on we will discuss the error term explicitly. For now we can finesse the issue by assuming that the errors have zero mean, in which case if we simply take the average of Equation 5.5 the error term goes away. For now let’s simply assume that the errors are zero

$$\mathbf{m}^{\dagger} = A^{\dagger}A\mathbf{m}. \tag{5.6}$$

This result can be interpreted as saying that the matrix $A^{\dagger}A$ acts as a kind of filter relating the true Earth model to the computed Earth model. Thus, if $A^{\dagger}A$ were equal

After we discuss probability in more detail we would take expectations as follows:

$$E[\mathbf{m}^{\dagger}] = E[A^{\dagger} (A\mathbf{m} + \mathbf{e})] = A^{\dagger}A\mathbf{m} + A^{\dagger}E[\mathbf{e}] = A^{\dagger}A\mathbf{m}$$

since if the data have zero mean, $E[\mathbf{e}] = 0$.

1