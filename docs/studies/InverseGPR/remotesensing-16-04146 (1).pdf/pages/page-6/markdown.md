Remote Sens. 2024, 16, 4146

6 of 19

is employed as the misfit function, comparing the entire synthetic signal profile with the observed signal profile. The objective function is as follows:

$$\Phi(\varepsilon, \sigma) = \min_{\varepsilon, S} W_2(PE_y, d_{obs}) \quad s.t. A(\varepsilon, \sigma)E_y = s \tag{12}$$

In the $L_2$-based FWI objective function, the amplitude differences between observed and simulated electromagnetic signals are calculated point by point, leading to a lack of low-frequency content. When the initial model for inversion significantly deviates from the true model, this method often encounters the issue of cycle skipping. In contrast, the $W_2$ distance directly seeks the global difference between the distributions of two signals, capturing both temporal and spatial amplitude variations. As a result, the $W_2$ distance provides the low-frequency information necessary for inversion, reduces the sensitivity of FWI to the initial model, and alleviates the cycle-skipping problem.

In FWI, the gradient of the objective function is typically obtained using the adjoint-state method [4,9]. Given the above, the forward wavefield is established through $A(\varepsilon, \sigma)E_y = s$. The adjoint wavefield $v$ can be obtained through the equation $A^{\dagger}v = P^T(PE_y - d_{obs})$, where $\dagger$ denotes the adjoint operator.

### 2.3. Convexity Comparison of Objective Functions

Two sequences of Wasserstein distances being compared must satisfy the conditions of mass conservation and non-negativity. Here, we compute the discrepancy between two probability distributions. Several existing scaling methods can be employed to modify functions and convert signals into probability distributions, ensuring they meet the computational requirements while minimally affecting the convexity of the functions.

This section compares the performances of different scaling transformations on the convexity of the objective function using simple 1D numerical simulations. These transformations will be compared on their convexity with traditional least-squares-based functions. The numerical examples provided in this section demonstrate that through applying appropriate scaling, the convexity of the objective function is significantly improved.

In existing research on seismic full-waveform inversion based on the optimal transport problem, it has been found that scaling methods are more effective [22,30]. This section focuses on comparing an effective scaling function: the Softplus scaling function (13).

$$a_s(x, b) = \log(\exp(bx) + 1) \tag{13}$$

$$f = \frac{a}{\sum a} \tag{14}$$

Here, $b$ is defined as a hyperparameter, which is distinct from the regularization coefficient $\varepsilon$ during the inversion process. After applying the aforementioned scaling functions, the function is normalized (14).

A simple numerical simulation result demonstrates that the value of the hyperparameter $b$ is related to the convexity of the objective function. Additionally, a comparison between the traditional $L_2$ norm and the Wasserstein distance, as well as the convexity of the objective function under different scaling functions, is provided. The results are shown in Figure 2. The collected GPR electromagnetic wave signal can be approximated by convolving a Ricker wavelet with the reflection coefficient. First, two Ricker wavelets, m and n, are provided. The center of m is fixed at 0.5 s, and n is shifted from 0.25 s to 0.75 s. The $L_2$ norm and Wasserstein distance are calculated for each shift, as shown in Figure 2a.

It is evident that, compared to the traditional $L_2$ norm method, the convexity of the objective function using the Wasserstein distance is significantly improved, and the cycle-skipping artifact is slightly reduced (see Figure 2b,c). In Figure 2c, as the value of the hyperparameter b increases, the objective function becomes increasingly linear with respect to larger time shifts, and the convexity of the objective function is significantly improved (as indicated by the black circles in Figure 2c). In Figure 2b,c, the scaled and normalized objective functions exhibit one global minimum and two local minima. When b = 1 or 1.5, a