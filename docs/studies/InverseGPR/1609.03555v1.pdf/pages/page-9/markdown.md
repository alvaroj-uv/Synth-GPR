Inverse source problem for wave equation

9

Table 1. Values of the condition number \( C(\mathbf{A}^N, \alpha) \) depending on the parameters \( N \), \( \alpha \) for different \( \Phi(t) \), \( \beta_1 = 1.546 \), \( \beta_2 = 1.373 \), \( T = 12 \cdot 10^{-9} \) sec, \( c = 1.5 \cdot 10^8 \) m/sec, \( l = 0.9 \) m:

|  \( \Phi(t) = \sin(8t + \beta_1)\exp(-0.2t) \) |   |   |   |   |   | \( \Phi(t) = \sin(t + \beta_2)\exp(-0.2t) \)  |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  \( N\backslash \alpha \) | 0 | \( 10^{-4} \) | \( 10^{-3} \) | \( 10^{-2} \) | \( 10^{-1} \) | 0 | \( 10^{-5} \) | \( 10^{-4} \) | \( 10^{-3} \) | \( 10^{-2} \) | \( 10^{-1} \)  |
|  5 | 1.06 | 1.06 | 1.06 | 1.06 | 1.057 | 4.5 | 4.5 | 4.5 | 4.5 | 4.45 | 4.20  |
|  8 | 1.17 | 1.17 | 1.17 | 1.17 | 1.16 | 45.0 | 45.0 | 45 | 44.6 | 41.4 | 24.2  |
|  11 | 1.39 | 1.39 | 1.39 | 1.38 | 1.36 | 197 | 196.6 | 196 | 189 | 142 | 41.1  |
|  14 | 1.75 | 1.75 | 1.75 | 1.75 | 1.71 | 562 | 562 | 556 | 507 | 268 | 47.6  |
|  17 | 2.43 | 2.43 | 2.43 | 2.42 | 2.34 | 1278 | 1275 | 1247 | 1022 | 365 | 50.1  |
|  20 | 3.72 | 3.72 | 3.72 | 3.70 | 3.55 | 2511 | 2498 | 2393 | 1685 | 426 | 51.1  |

value of the number \(\sqrt{N} C(\mathbf{A}^N,\alpha)\). The last point leads to the practical way to choose these parameters.

The additional analysis has been done by computing the values of discrepancy  \( \eta \)  defined as follows

\[
\eta = \left(\int_ {0} ^ {T} \left(\sum_ {k = 1} ^ {N} F _ {\alpha k} ^ {N} G _ {k} (t) - g (t)\right) ^ {2} d t\right) ^ {1 / 2}. \tag {34}
\]

Let the assumptions of the Proposition hold and  \( F(x) \)  be the exact solution of the considered ISP. Let  \( F^{N}(x) \)  and  \( F_{ex}^{N}(x) \)  be computed and exact versions of the partial Fourier sums of  \( F(x) \) . Denote by  \( C_{i}, i = 1, 2, 3 \)  different constants which do not depend on  \( F(x) \)  and can depend on N,  \( \alpha \)  and physical parameters of the problem. Then the difference between exact and numerical solution of the inverse problem is estimated as follows:

\[
\| F (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq \| F (x) - F _ {e x} ^ {N} (x) \| _ {L ^ {2} (0, l)} + \| F _ {e x} ^ {N} (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)}. \tag {35}
\]

Define the function  \(  g^{N}(t) = u(0, t; F_{ex}^{N})  \) . Subtracting the equation (26) from (21) we obtain the integral equation which links the functions  \(  g(t) - g^{N}(t)  \)  and  \(  F(x) - F_{ex}^{N}(x)  \) . The solution of that equation satisfies the stability estimate which can be obtained in standard way:

\[
\| F (x) - F _ {e x} ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq C _ {2} \| g (t) - g ^ {N} (t) \| _ {H ^ {1} [ 0, T ]}. \tag {36}
\]

Due to the orthogonality of basic functions  \( X_{k}(x) \)  the  \( L_{2} \) -norm of the function  \( \delta F^{N}(x)=F_{ex}^{N}(x)-F^{N}(x) \)  is equal to Euclidean norm of the vector  \( \delta\mathbf{F}^{N}(x) \) ; therefore combination of (36) with (33) estimates the computational error of the solution to the inverse problem:

\[
\| F (x) - F ^ {N} (x) \| _ {L ^ {2} (0, l)} \leq C _ {2} \| g (t) - g ^ {N} (t) \| _ {H ^ {1} [ 0, T ]} + C _ {3} \| \delta g ^ {N} (t) \| _ {L ^ {2} [ 0, T ]}. \tag {37}
\]

As it is seen from the definition of the matrix \(\mathbf{A}\), it can be calculated independently before measurements. Therefore the condition numbers \(C(\mathbf{A}^N,\alpha)\) for different values of \(N\), \(\alpha\) and given physical data \(c\), \(c_0\), \(T\), \(H(t)\), \(l\) can be defined. Then the most admissible combinations of \(N\) and \(\alpha\) can be established. Table 1 shows values of condition numbers