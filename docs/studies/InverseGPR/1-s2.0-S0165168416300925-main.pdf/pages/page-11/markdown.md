282

M. Sun et al. / Signal Processing 132 (2017) 272–283

(estimated roughness parameters are $\hat{b}_1 = 1.50 \times 10^{-3} \text{ GHz}^{-2}$, $\hat{b}_2 = 1.83 \times 10^{-2} \text{ GHz}^{-2}$ and $\hat{b}_3 = 2.93 \times 10^{-2} \text{ GHz}^{-2}$).

## 6. Conclusion

In this paper, we have studied time delays and interface roughness estimation with coherent backscattered echoes. After applying the interpolated spatial smoothing technique to decorrelate the received echoes, we propose a modified MUSIC algorithm, which is able to estimate the time delays without knowing the frequency behaviour from roughness. Then, the influence of the interface roughness is estimated by MLE. These algorithms are applied to evaluate the pavement. The performance of the proposed algorithms is tested on data from MoM. The proposed algorithms show good performance for time delays and interface roughness estimation. In perspective, the proposed method will be extended to dispersive media (soils or hydraulic concretes).

## Acknowledgment

The authors would like to thank the China Scholarship Council (No. 201306150010) and the grant of Science and Technology Planning Project of Guangdong (No. 2015A050502011) for funding part of this work. This work may contribute to COST Action TU1208 "Civil Engineering Applications of Ground Penetrating Radar".

## Appendix A.

The mode vector can be written as:

$$\begin{array}{l} \mathbf{a}(t_k) = [\exp(-2j\pi f_1 t_k)w_k(f_1)\exp(-2j\pi f_2 t_k)w_k(f_2) \\ \quad \dots \exp(-2j\pi f_N t_k)w_k(f_N)]^T \\ = diag\{w_k(f_1), w_k(f_2) \dots w_k(f_N)\} \\ \quad [\exp(-2j\pi f_1 t_k), \exp(-2j\pi f_2 t_k) \dots \exp(-2j\pi f_N t_k)]^T \\ = \mathbf{C}\bar{\mathbf{a}} \end{array}$$

The frequency behaviour $w(f)$ depends on the RMS height $\sigma_h$ and the correlation length $L_h$, thus matrix $\mathbf{C}$ also changes with $\sigma_h$ and $L_h$, it can be expressed as $\mathbf{C}(\sigma_h, L_h)$. We propose to interpolate $w(f)$ into a uniform linear frequency behaviour. The procedure is as follows:

- Define a set of $\sigma_h = \{\sigma_{h1}, \sigma_{h2} \dots \sigma_{hC}\}$ and a set of $L_h = \{L_{h1}, L_{h2} \dots L_{hP}\}$;
- Compute the model vectors associated with the set $\sigma_h$ and $L_h$, and arrange them into a matrix form as follows: $\mathbf{C}_r = [\mathbf{C}(\sigma_{h1}, L_{h1})\mathbf{C}(\sigma_{h2}, L_{h2}) \dots \mathbf{C}(\sigma_{h3}, L_{hP})\mathbf{C}(\sigma_{h4}, L_{h4}) \dots \mathbf{C}(\sigma_{hC}, L_{hP})]$;
- Decide where to place the "virtual elements" of the interpolation matrix $\mathbf{C}_r = [\hat{\mathbf{C}}(\sigma_{h1}, L_{h1})\hat{\mathbf{C}}(\sigma_{h2}, L_{h2}) \dots \hat{\mathbf{C}}(\sigma_{h3}, L_{hP})\hat{\mathbf{C}}(\sigma_{h4}, L_{h4}) \dots \hat{\mathbf{C}}(\sigma_{hC}, L_{hP})]$, $\hat{\mathbf{C}}(\sigma_h, L_h)$ has a uniform linear frequency behaviour.
- Find the transformation matrix $\mathbf{B}$ by a least squares solution of $\mathbf{B}\mathbf{C}_r = \mathbf{C}_r$. The "best" interpolation matrix $\mathbf{C}_r$ is the one which will minimize $\|\mathbf{B}\mathbf{C}_r - \mathbf{C}_r\|^2$.

## Appendix B.

In this appendix, we present why a false peak exists. Only the case of two echoes is presented, but the same calculation can be carried out when the number of echoes is superior to 2. We assume $t_1$ and $t_2$ are the time delays of two echoes ($t_1 < t_2$) and define $t_3 = (t_1 + t_2)/2$, $\Delta t = (t_2 - t_1)/2$, $\Phi(t) = \hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)$. By

definition, the rank of $\mathbf{U}_h\mathbf{U}_h^H$ is $L-2$, it has always 2 zero eigenvalues with 2 eigenvectors, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t)$ is real valued. Following the subspace principle, we have 2 equalities:

- $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t) = \mathbf{k}^T\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k} = \mathbf{k}^T\Phi(t)\mathbf{k} = 0$, for $t = t_1$ or $t_2$.
- $\mathbf{k}^T\Phi(t)\mathbf{k} \neq 0$, for $t \neq t_1$ or $t_2$.

Then we can have the following 3 situations:

case 1: $t = t_1$ and $t_2$. When $t = t_1$ or $t_2$, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t) = \mathbf{k}^T\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k} = \mathbf{k}^T\Phi(t)\mathbf{k} = 0$. $\Phi(t)$ has 2 zero eigenvalues with 2 eigenvectors and $\mathbf{k}$ is a real eigenvector. For $t = t_1$, we can see also:

$$\begin{array}{l} \mathbf{k}^T\hat{\mathbf{A}}^H(t_2 - t_1)\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\hat{\mathbf{A}}(t_2 - t_1)\mathbf{k} \\ = \mathbf{k}_{10}^H\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k}_{10} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_2)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} \end{array}$$

where $\mathbf{k}_{10} = \hat{\mathbf{A}}(t_2 - t_1)\mathbf{k}$ is another eigenvector. Similarly, $\mathbf{k}_{20} = \hat{\mathbf{A}}(t_1 - t_2)\mathbf{k}$ is the second eigenvector for $t = t_2$. $\mathbf{k}_{10}$ and $\mathbf{k}_{20}$ are complex valued and not collinear with $\mathbf{k}$, any non-zero coefficients linear combination of $\mathbf{k}$ and $\mathbf{k}_{10}$ or $\mathbf{k}$ and $\mathbf{k}_{20}$ is complex valued. Therefore, $\Phi(t)$ has only one real eigenvector ($\mathbf{k}$) corresponding to one single zero eigenvalue, and $real\{\mathbf{k}^T\Phi(t)\mathbf{k}\} = \mathbf{k}^T real\{\Phi(t)\}\mathbf{k} = 0$, only one solution for $t_1$ or $t_2$. Thus, the number of zero eigenvalue of $real\{\Phi(t_1)\}$ and $real\{\Phi(t_2)\}$ is 1.

case 2: $t \neq t_1$, $t_2$ and $t_3$. $\Phi(t)$ has 2 zero eigenvalues, we can find easily 2 non-linearly correlated eigenvectors $\mathbf{k}_1$ and $\mathbf{k}_2$ corresponding to the zero eigenvalues:

$$\mathbf{k}_1^H\Phi(t)\mathbf{k}_1 = \mathbf{k}_1^H\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k}_1 = 0$$

$$\mathbf{k}_2^H\Phi(t)\mathbf{k}_2 = \mathbf{k}_2^H\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k}_2 = 0$$

where $\mathbf{k}_1 = \hat{\mathbf{A}}(t_1 - t)\mathbf{k}$ and $\mathbf{k}_2 = \hat{\mathbf{A}}(t_2 - t)\mathbf{k}$. Due to $t \neq t_1$, $t_2$ and $t_3$, $\mathbf{k}_1$ and $\mathbf{k}_2$ are complex and non-linearly correlated. For these values of $t$, we can show that any linear combination of $\mathbf{k}_1$ and $\mathbf{k}_2$ will always be complex valued. $\Phi(t)$ has no real eigenvector corresponding to zero eigenvalue. Then, $\mathbf{k}^T\Phi(t)\mathbf{k} \neq 0$, $real\{\mathbf{k}^T\Phi(t)\mathbf{k}\} = \mathbf{k}^T real\{\Phi(t)\}\mathbf{k} \neq 0$, which means $real\{\Phi(t)\}$ is full rank, there is no zero eigenvalue.

case 3: $t = t_3$. When $t = t_1$ and $t_2$, We have:

$$\mathbf{k}^T\Phi(t_1)\mathbf{k} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} = 0$$

$$\mathbf{k}^T\Phi(t_2)\mathbf{k} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_2)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = 0$$

which are equivalent to

$$\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} = 0$$

$$\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = 0$$

For $t = t_3$, any linear combination of above equations leads $\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} + \alpha\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = \mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) + \alpha\hat{\mathbf{A}}(\Delta t))\mathbf{k} = 0$. Only when $\alpha$ is equal to 1 or $-1$, $\hat{\mathbf{A}}^H(\Delta t) + \alpha\hat{\mathbf{A}}(\Delta t)$ is a pure real or imaginary matrix.

For $\alpha = 1$, $\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) + \hat{\mathbf{A}}(\Delta t))\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)real\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)\mathbf{k}_3$. For $\alpha = -1$, $\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) - \hat{\mathbf{A}}(\Delta t))\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)imag\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)\mathbf{k}_4$. Therefore, $\mathbf{k}_1^H\Phi(t_3)\mathbf{k}_3 = \mathbf{k}_1^H\Phi(t_3)\mathbf{k}_4 = 0$ with $\mathbf{k}_3 = real\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k}$ and $\mathbf{k}_4 = imag\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k}$. In addition, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t)$ is always real valued, thus, $t_3$ is a solution of $\lambda_{\min}(t) = 0$ and $real\{\Phi(t_3)\}$ only two zero eigenvalues with corresponding eigenvectors $\mathbf{k}_3$ and $\mathbf{k}_4$. When the number of echoes is superior to 2, the number of zero eigenvalues of $real\{\Phi(t)\}$ corresponding to the true time delay is odd. For false time delay, this number is even.

## Appendix C.

In this appendix, we present MLE for the roughness parameters estimation. The time delays are estimated ($\hat{t}_k$ is the $k$th estimated