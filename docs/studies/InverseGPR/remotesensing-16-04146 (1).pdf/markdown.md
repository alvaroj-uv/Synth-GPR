remote sensing

MDPI

Article

# Full-Waveform Inversion of Two-Parameter Ground-Penetrating Radar Based on Quadratic Wasserstein Distance

Kai Lu 1, Yibo Wang 2,3,*, Heting Han 2,3, Shichao Zhong 4 and Yikang Zheng 2,3

1 MNR Key Laboratory of Polar Science, Polar Research Institute of China, Shanghai 200062, China; lukai@pric.org.cn
2 Key Laboratory of Petroleum Resource Research, Institute of Geology and Geophysics, Chinese Academy of Sciences, Beijing 100029, China; hetinghan@mail.iggcas.ac.cn (H.H.); zhengyk@mail.iggcas.ac.cn (Y.Z.)
3 University of Chinese Academy of Sciences, Beijing 100049, China
4 Yangtze Delta Region Academy of Beijing Institute of Technology, Jiaxing 314019, China; zhongshichao16@bit.edu.cn
* Correspondence: wangyibo@mail.iggcas.ac.cn

Abstract: Full-waveform inversion (FWI) is one of the most promising techniques in current ground-penetrating radar (GPR) inversion methods. The least-squares method is usually used, minimizing the mismatch between the observed signal and the simulated signal. However, the cycle-skipping problem has become an urgent focus of this method because of the nonlinearity of the inversion problem. To mitigate the issue of local minima, the optimal transport problem has been introduced into full-waveform inversion in this study. The Wasserstein distance derived from the optimal transport problem is defined as the mismatch function in the FWI objective function, replacing the L2 norm. In this study, the Wasserstein distance is computed by using entropy regularization and the Sinkhorn algorithm to reduce computational complexity and improve efficiency. Additionally, this study presents the objective function for dual-parameter full-waveform inversion of ground-penetrating radar, with the Wasserstein distance as the mismatch function. By normalizing with the Softplus function, the electromagnetic wave signals are adjusted to meet the non-negativity and mass conservation assumptions of the Wasserstein distance, and the convexity of the method has been proven. A multi-scale frequency-domain Wasserstein distance full-waveform inversion method based on the Softplus normalization approach is proposed, enabling the simultaneous inversion of relative permittivity and conductivity from ground-penetrating radar data. Numerical simulation cases demonstrate that this method has low initial model dependency and low noise sensitivity, allowing for high-precision inversion of relative permittivity and conductivity. The inversion results show that it, in particular, significantly improves the accuracy of conductivity inversion.

Keywords: Wasserstein distance; optimal transport distance; relative permittivity and conductivity; full-waveform inversion

Citation: Lu, K.; Wang, Y.; Han, H.; Zhong, S.; Zheng, Y. Full-Waveform Inversion of Two-Parameter Ground-Penetrating Radar Based on Quadratic Wasserstein Distance. Remote Sens. 2024, 16, 4146. https://doi.org/10.3390/rs16224146

Academic Editor: Roberto Orosei

Received: 9 October 2024

Revised: 26 October 2024

Accepted: 30 October 2024

Published: 7 November 2024

Copyright: © 2024 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https://creativecommons.org/licenses/by/4.0/).

## 1. Introduction

Ground-penetrating radar (GPR) is an efficient, non-destructive geophysical method used for near-surface investigation. GPR works in the way of emitting high-frequency electromagnetic waves into the ground by transmitting antenna and receiving the reflected waves from subsurface structures by receiving antenna. This allows for imaging of shallow subsurface structures and electromagnetic properties. GPR inversion refers to the process of reconstructing the subsurface distribution of electrical parameters, such as relative permittivity and conductivity, from GPR observational data. The inversion result is crucial for analyzing and interpreting subsurface structures and has significant implications for engineering applications. Currently, common methods used in GPR inversion imaging include tomography [1,2], common midpoint (CMP) velocity analysis [3], full-waveform

Remote Sens. 2024, 16, 4146. https://doi.org/10.3390/rs16224146

https://www.mdpi.com/journal/remotesensing

Remote Sens. 2024, 16, 4146

2 of 19

inversion (FWI) [4], and deep learning-based inversion methods [5,6]. Among these, FWI is one of the most promising techniques.

GPR full-waveform inversion is a high-resolution imaging method used to reconstruct complex geological structures based on observed signals and initial models. Mathematically, FWI is a nonlinear inverse problem, typically solved through optimization by strictly enforcing partial differential equations (PDE) [7,8]. The adjoint-state method is commonly used to obtain the gradient of the objective function [9]. Due to the large scale of the inversion problem, the computational cost of FWI is high. Therefore, gradient-based local optimization methods are typically employed to solve large-scale PDE-constrained optimization problems, such as gradient descent, quasi-Newton methods, and L-BFGS [10]. The theoretical resolution of FWI is half of the wavelength $\lambda/2$ [11]. FWI establishes an objective function by minimizing the mismatch between observed and simulated data, aiming to find a parameter model that best represents the observed data [12]. Additionally, the least-squares method is the most widely used mismatch function in traditional FWI objective functions.

It is well known that when the $L_2$ norm is used as the mismatch function, the objective function measures the amplitude difference between observed and simulated data at each point [4,8]. This method focuses on local amplitude variations, which makes it difficult to capture low-frequency information. Local minima issues, commonly known as cycle-skipping artifacts, appear when the initial inversion model differs significantly from the true model or when the phase difference between the two signals exceeds half a wavelength [13,14]. Therefore, current GPR full-waveform inversion faces challenges such as strong dependence on the initial model, susceptibility to local minima, and sensitivity to noise. In dual-parameter inversion of GPR data, conductivity is more sensitive to low-frequency signals, making conductivity inversion more prone to local minima issues [4,8]. To address these problems, methods like multi-scale inversion in the time domain [15] and frequency domain [16,17], as well as wavefield-reconstruction-based FWI [4,18], have been proposed to mitigate local minima problem and improve the robustness of imaging. The multi-scale inversion approach addresses the data in the frequency domain sequentially [4]. It starts with low-frequency information to obtain a smooth background model, then gradually incorporates high-frequency information, thereby partially improving the precision of the inversion results. However, this fundamental issue with the convexity of the objective function remains unresolved, as the $L_2$ norm mismatch function is difficult to effectively capture the phase shifts of shaking electromagnetic signals, and the problem of local minima continues to be prominent.

Our study attempts to improve the objective function formulation to mitigate the cycle-skipping problem in GPR parameter inversion and build on the multi-scale inversion approach. The optimal transport problem and Wasserstein distance are introduced to describe the difference between two electromagnetic signals. Initially, the optimal transport theory and the Wasserstein distance were proposed to find the best mapping between two probability distributions [19], minimizing the transportation cost. The unit transportation cost can be defined by Manhattan or Euclidean distance, among others. The quadratic cost function and its corresponding quadratic Wasserstein distance ($W_2$) have received significant attention [20,21]. Unlike the local approach of the $L_2$ norm which compares point-by-point amplitude differences, the $W_2$ distance combines both local amplitude and global phase information in its comparison [22]. The FWI objective function based on the $W_2$ distance exhibits better convexity, allowing it to measure time-shift and low-frequency information between two signals, thereby alleviating the problem of local minima [23]. With the mathematical properties of the $W_2$ distance, such as its convexity in capturing signal variations, its ability to handle phase and amplitude changes, and its robustness to noise [24], the $W_2$ distance-based objective function has been demonstrated to be highly effective in seismic FWI [4,25]. However, solving the adjoint source becomes too complex when applying two-dimensional observational data in $W_2$ distance-based FWI. To address this problem, entropy regularization is used to find approximate solutions, reducing the

Remote Sens. 2024, 16, 4146

3 of 19

computational cost. On this basis, the Sinkhorn algorithm was proposed to solve the optimal transport problem efficiently [26]. The relaxed form of the Wasserstein distance, known as the Kantorovich–Rubinstein (KR) norm, has been proposed [21], and it does not require signals to satisfy non-negativity or mass balance conditions. Recently, the Wasserstein distance has been applied to relative permittivity inversion in asteroid radar studies [27], demonstrating its low dependency on the initial model and robustness to random noise in electromagnetic full-waveform inversion as well. The Wasserstein distance typically describes two non-negative, mass-equal signals, but seismic and electromagnetic signals shake around zero and do not meet these criteria. Therefore, certain transformations are needed to ensure that the signals satisfy the non-negativity and mass conservation conditions required for the optimal transport.

This study proposes to use the quadratic Wasserstein distance as the mismatch function in multi-scale frequency-domain full-waveform inversion for ground-penetrating radar data. The method is applied to multi-offset GPR data to simultaneously reconstruct images of subsurface relative permittivity and conductivity. The FWI objective function based on the $W_2$ distance for multi-offset GPR and the Sinkhorn optimization iteration algorithm are proposed, followed by the convexity analysis comparing the $L_2$ norm and $W_2$ distance under different scaling methods. Three numerical simulation examples demonstrate that FWI based on the $W_2$ distance suffers much less by local minima, has lower dependence on the initial model, and shows reduced sensitivity to noise. The conductivity inversion results from different examples demonstrate that the $W_2$ distance, which considers both phase shifts and amplitude differences, improves the inversion of low-frequency information. Additionally, it adapts to the characteristic that conductivity is more sensitive to low-frequency signals, resulting in more reliable inversion results.

## 2. Methods

### 2.1. Optimal Transport Problem and Sinkhorn Method

In traditional full-waveform inversion, the $L_2$ norm is commonly used as a misfit function. Unlike the $L_2$ norm, which measure the local difference point by point, the Wasserstein distance, based on the optimal transport problem, seeks to capture the global differences between two distributions (Figure 1).

![img-0.jpeg](img-0.jpeg)

**Figure 1.** (a) The $L_2$ norm measures the mismatch between two signals by calculating the difference point by point. (b) The Wasserstein distance computes the minimum cost required to transfer the mass of one distribution to another.

The optimal transport problem was originally designed to find a mapping from one measure to another that minimizes the total transportation cost $c(x_i, y_j)$ for all units of mass, also known as the Monge problem. Define the sets of two sampling points as $X = \{x_1, \cdots, x_n\} \in \mathbb{R}^n$ and $Y = \{y_1, \cdots, y_m\} \in \mathbb{R}^m$. Consider $n$ shipping warehouses and $m$ receiving warehouses as random variables $x$ and $y$, with different amounts of storage in

Remote Sens. 2024, 16, 4146

4 of 19

different shipping and receiving warehouses. It is necessary to send the materials from the n shipping warehouses to the m receiving locations, and each receiving location requires a different amount of materials. The distance between each shipping and receiving warehouse is denoted as $c(x_i, y_j)$. Find a transport strategy that can complete the distribution of supplies most efficiently. In other words, the optimal transport problem seeks the minimum cost required to transfer the mass of one distribution to another. Here, c represents the transportation cost for moving a unit of mass from $x$ to $y$. The discrete measures of two probability distributions are defined as follows:

$$a = \sum_{i=1}^n a_i \delta_{x_i} \text{ and } b = \sum_{i=1}^m b_i \delta_{y_i} \quad (1)$$

where $a \in \sum_n$ and $b \in \sum_m$ are both probability simplices. Due to the high computational complexity of the optimal transport problem, the Kantorovich relaxed optimal transport model was introduced [20]. A coupling matrix $P \in \mathbb{R}_+^{n \times m}$ is used to implement the transport plan between two discrete distributions, where the set of matrix $P$ is defined as follows:

$$U(a, b) = \{P \in \mathbb{R}_+^{n \times m} \mid P1_m = a \text{ and } P'1_n = b\} \quad (2)$$

The cost matrix $C$ in the objective function based on the Wasserstein distance represents the cost of transporting a unit of mass from one distribution to another. In this paper, $C \in \mathbb{R}_+^{n \times m}$ is defined using the squared Euclidean distance, known as the quadratic Wasserstein metric ($W_2$):

$$C_{i,j} = c(x_i, y_j) = |x_i - y_j|^2 \quad (3)$$

The Kantorovich relaxation of the optimal transport problem between two distributions can be defined as follows:

$$W_2(a, b) = \min_{P \in U(a, b)} \langle C, P \rangle = \sum_{i,j} C_{i,j} P_{i,j}^{OT} \quad (4)$$

Finding the optimal coupling matrix $P^{OT}$ that accurately represents the mapping between two distributions is a key issue. However, obtaining the standard Kantorovich relaxation solution is computationally expensive [28].

To reduce the computational cost, the Sinkhorn algorithm was proposed by applying entropy regularization, currently one of the most widely used numerical methods for solving optimal transport problems, with its advantages of being less complex and easy to implement [29].

The definition of entropy regularization and the Kantorovich optimal transport problem with entropy regularization are defined as follows:

$$H(p) = -\sum_{i=1}^n p_i (\log p_i - 1) \quad (5)$$

$$W_2(a, b) = \min_{P \in U(a, b)} \langle C, P \rangle - \epsilon H(P) \quad (6)$$

where $\epsilon$ is the regularization parameter and $H(p)$ is the entropy. When $\epsilon$ approaches 0, the optimal solution $P^{OT}$ of the approximate Kantorovich problem converges to the optimal solution of the original problem. Conversely, a larger value of $\epsilon$ results in a more regularized coupling, with a greater distance between different solutions, which reduces computational complexity and improves inversion speed. By considering the Lagrangian of the problem (7) and differentiating with respect to each $P_{i,j}^{OT}$ (8), we obtain (9) the following:

$$W_2(a, b) = \sum_{i,j} C_{i,j} P_{i,j}^{OT} - \epsilon H(P^{OT}) - \alpha'(P^{OT}1_m - a) - \beta'(P^{OT'}1_n - b) \quad (7)$$

Remote Sens. 2024, 16, 4146

5 of 19

$$\frac{\partial W_2(a, b)}{\partial P_{i,j}^{OT}} = C_{i,j} + \epsilon \log P_{i,j}^{OT} - \alpha_i - \beta_j = 0 \tag{8}$$

$$P_{i,j}^{OT} = e^{\alpha_i / \epsilon} e^{-C_{i,j} / \epsilon} e^{\beta_j / \epsilon} \tag{9}$$

Let $K = e^{-C_{i,j} / \epsilon}, u = e^{-\alpha / \epsilon}, v = e^{-\beta / \epsilon}$, then the transmission matrix can be represented as follows:

$$P^{OT} = diag(u)Kdiag(v) \tag{10}$$

The Sinkhorn algorithm updates the vectors u and v alternately through iterative procedures to obtain the optimal solution for the optimal transport problem. The iteration process terminates after a certain number of iterations. Based on the above derivations, the detailed algorithm for Sinkhorn's method is shown in Algorithm 1. For more detailed derivations, please refer to [28,29].

# Algorithm 1. Sinkhorn method

Input: $C, \epsilon, a, b$

Initialization: $v^0 = 1_m, u^0 = 1_n, K = e^{-C_{i,j} / \epsilon}$

While Sinkhorn not converged do

$$u_i^{(n+1)} = \frac{a}{(Kv^{(i)})_i}$$

$$v_j^{(n+1)} = \frac{b}{(K'u^{(i+1)})_j}$$

End while

Optimal transportation matrix $P = diag(u)Kdiag(v)$

Output: $W_2(a, b) = \langle C, P \rangle$

$$\nabla_a W^2(a, b) = \epsilon \log(u_i)$$

It is a tradeoff for the choice of the regularization parameter $\epsilon$. Small $\epsilon$ yields more accurate results but increases computational costs. If $\epsilon$ approaches 0, the optimal solution P converges to the optimal solution of the original problem. Therefore, $\epsilon$ should be selected carefully based on the data and the specific requirements.

# 2.2. Multi-Scale Two-Parameter FWI Based on $W_2$

When solving the inversion problem for GPR data, the goal is to minimize the difference between the simulated data $d_{cal} = PE_y$ and the observed data $d_{obs}$. The $L_2$ norm is typically used as a misfit function to measure the difference between them. Therefore, the frequency-domain GPR full-waveform inversion objective function for dual-parameter inversion can be formulated as an optimization problem constrained by a partial differential equation [8,12].

$$\Phi(\epsilon, \sigma) = \min_{\varepsilon, \delta} |PE_y - d_{obs}|_2^2 \quad s.t. A(\epsilon, \sigma)E_y = s \tag{11}$$

Here, the $\epsilon$ and $\sigma$ represent the relative permittivity and conductivity determined during the inversion process, respectively. The $E_y$ is the electric field vector, and the source term is denoted by s. The discretized PDE Helmholtz operator matrix is represented as $A$, where $A(\epsilon, \sigma) = \mu \omega^2 (\epsilon + i\sigma / \omega) + \Delta$. The $\Delta$ represents the Laplace operator, $\mu$ is the magnetic permeability, and $\omega = 2\pi f$ is the angular frequency. The P is the detector operator, which samples the simulated wavefield at the receiver locations. The $\|\cdot\|_2^2$ term represents the $L_2$ norm used as the misfit function. For simplicity, Equation (11) only shows a single frequency and source. The extension to multiple frequencies and sources is achieved by summing over all frequencies and sources in the objective function. Additionally, we apply the $W_2$ distance to two-dimensional multi-offset GPR data and provide update formulas for the relative permittivity and conductivity using the limited-memory BFGS algorithm [10].

The $W_2$ distance, based on the optimal transport problem, is used as the misfit function to measure the mismatch between observed and simulated data. The global $W_2$ distance

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

Remote Sens. 2024, 16, 4146

7 of 19

global minimum is obtained in Figure 2c without local minima. It indicates that the inversion process will not fall into local minima, avoiding cycle-skipping artifacts. Therefore, choosing a larger value of b provides better convex behavior relative to time shifts.

![img-1.jpeg](img-1.jpeg)

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)

**Figure 2.** (a) Ricker wavelets $m$ and $n$. (b) The objective function with the $L_2$ norm. (c) The Softplus normalized objective function with the $W_2$ distance.

However, the choice of b should not be excessively large. As the value of b increases, the area around the global minimum of the objective function becomes smoother (indicated by the purple circle in Figure 2c). This implies that a larger b value will reduce the convergence speed toward the global minimum. Ultimately, the resolution of the final inversion result is decreased. Therefore, in this study, we chose the Softplus scaling function to preprocess the electromagnetic signals and determined the appropriate value of b through numerical experiments.

### 3. Numerical Examples

Three GPR multi-scale frequency-domain dual-parameter inversion cases are given in this section. First, a simple model is used to compare and analyze the dependence of the $W_2$ distance and $L_2$ norms on the initial model. The second study investigates the sensitivity of the $W_2$ distance and $L_2$ norm to noise. The third case validates that the FWI method using the $W_2$ distance achieves higher accuracy with a complex model. The Softplus normalization method is applied to the $W_2$ distance.

#### 3.1. Example 1: Comparison of Initial Model Dependence

This example demonstrates the difference in the objective functions between the $L_2$ norm and the $W_2$ distance for a toy model. The case involves a simple model with a homogeneous background medium and three simple geological anomalies. By changing the initial model, the dependence of the two methods on the initial model is tested.

The model is shown in Figure 3. It has dimensions of $14 \times 7$ m in both the horizontal and vertical directions. The uniform background parameters are $\varepsilon_r = 15$ and $\sigma = 0.1$ mS/m. The model contains one circular target and two rectangular targets. The circular target

Remote Sens. 2024, 16, 4146

8 of 19

has a relative permittivity of $\varepsilon_r = 10$, a conductivity of $\sigma = 3$ mS/m, and a diameter of 1.5 m. The rectangular targets have a relative permittivity of $\varepsilon_r = 5$ and a conductivity of $\sigma = 5$ mS/m. The upper rectangular target has dimensions of $2.5 \times 1$ m, while the lower target has dimensions of $3.5 \times 0.5$ m. The grid spacing is $\Delta x = 0.05$ m and $\Delta z = 0.05$ m. The model is discretized into $N_{m1} = 280 \times 140 = 39,200$ cells. In this study, ground-penetrating radar multi-offset data were used for inversion. Multi-offset radar employs a one-to-many reception working mode, allowing for the investigation of multiple reflection angles, similar to multi-offset data collection in seismology. Compared to single-offset radar, multi-offset radar data offer greater imaging advantages, significantly improving lateral imaging capabilities, and have been successfully applied in geological investigations and other areas [4]. The transmitter positions placed on the surface were spaced 0.5 m apart, with a total of 29 transmitters. The receiver antennas were spaced 0.1 m apart, with a total of 141 receivers. In Figure 3, the transmitter positions are indicated by red asterisks in the relative permittivity model (a), while the receiver positions are shown as red triangles in the conductivity model (b). All receiver antennas recorded the high-frequency electromagnetic signals transmitted by each transmitter.

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

**Figure 3.** (a) The true relative permittivity model, where the red asterisks represent the transmitter antennas. (b) The true conductivity model, where red triangles represent the receiver antennas.

In addition to the true subsurface relative permittivity model and conductivity model, an initial model is also required for the full-waveform inversion of GPR data. To further verify the dependency of the FWI method using the Wasserstein distance on the initial model, two different initial models, I and II, were used, as shown in Figures 4 and 5. Both initial models used a homogeneous background medium. Initial model I had a relative permittivity and conductivity of 15 and 0.1 mS/m, respectively, which match the background parameters of the true model. Initial model II had values of 10 and 1 mS/m.

The wave equation solver is developed in [31] to simulate GPR forward data. A frequency-domain multi-scale FWI method is employed to simultaneously invert the relative permittivity and conductivity models [8]. The inversion begins with low-frequency data to establish an accurate background model and gradually incorporates higher-frequency data as the iterations progress. The frequencies used in the inversion are divided into multiple batches, as shown in Table 1. Multiple frequency data are input in each iteration [16] to address the computational burden of single-frequency inversion. The multi-scale frequency-domain data required for inversion are obtained through the Fast Fourier Transform (FFT). For model I, the Ricker waves with a center frequency of 100 MHz are used for forward simulation. During the inversion process, the simulated GPR data are discretized into 19 frequencies and divided into 15 batches. The frequency range is from $f_{min} = 1$ MHz to $f_{max} = 120$ MHz. Each batch contains four frequencies. And after 10 iterations for each batch, inversion is continued using the frequency-domain data from the next batch.

Remote Sens. 2024, 16, 4146

9 of 19

![img-6.jpeg](img-6.jpeg)

![img-7.jpeg](img-7.jpeg)

Figure 4. Initial model I. Initial relative permittivity model (a) and initial conductivity model (b) with true model background medium.

![img-8.jpeg](img-8.jpeg)

![img-9.jpeg](img-9.jpeg)

Figure 5. Initial model II. Initial relative permittivity model (a) and initial conductivity model (b) with true model background medium.

Table 1. Iterative batches for discrete frequencies.

|  batchn |  |  |  |  | Frequency (MHz)  |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  batch1 | 1 | 5 | 10 | 15 |  |  |  |  |  |   |
|  batch2 |  | 5 | 10 | 15 | 20 |  |  |  |  |   |
|  batch3 |  |  | 10 | 15 | 20 | 25 |  |  |  |   |
|  ... |  |  |  |  |  | ... |  |  |  |   |
|  batch15 |  |  |  |  |  |  | 90 | 100 | 110 | 120  |

The multi-scale frequency-domain inversion is performed using the Wasserstein distance as the objective function. Model I (Figure 4) and model II (Figure 5) are used as initial models to compare the inversion performance of  \( W_{2} - FWI \)  and  \( L_{2} - FWI \) . The inversion results are shown in Figures 6–9.

In Figure 7, the inversion results using the \( W_{2} \) distance with initial model I are presented, while Figure 6 shows the inversion results using the \( L_{2} \) norm as the FWI misfit function. Comparing Figure 6d,h with Figure 7d,h, both inversion methods produce good imaging results for relative permittivity and conductivity when the initial model is close to the true model. However, in the \( L_{2} \) norm inversion, artifacts affect the inversion results of both the relative permittivity and conductivity of the target (Figure 6e–h). The interference in the conductivity inversion is more pronounced, causing the target's edges to appear unclear and distorted. Similar effects can also be observed in Figure 6a–d. In contrast, these

Remote Sens. 2024, 16, 4146

10 of 19

issues are significantly mitigated by using the W₂ distance (Figure 7). The target's structure is more consistent with the true model, resulting in cleaner imaging. This is attributed to the excellent convexity of the W₂ distance method and its sensitivity to low-frequency information, which helps achieve a more accurate background model and reduces the artifact interference caused by local minima.

![img-10.jpeg](img-10.jpeg)

![img-11.jpeg](img-11.jpeg)

Figure 6. The inverted images of relative permittivity and conductivity obtained from the L₂ norm method based on initial model I. (a–d) are the reconstructed relative permittivity images from frequencies in batch 1, batch 5, batch 9, and batch 14, respectively. (e–h) are the reconstructed conductivity images from frequencies for batch 1, batch 2, batch 3, and batch 4, respectively.

![img-12.jpeg](img-12.jpeg)

![img-13.jpeg](img-13.jpeg)

Figure 7. The inverted images of relative permittivity and conductivity obtained from the W₂ distance method based on initial model I. (a–d) are the reconstructed relative permittivity images from frequencies in batch 1, batch 5, batch 9, and batch 14, respectively. (e–h) are the reconstructed conductivity images from frequencies for batch 1, batch 2, batch 3, and batch 4, respectively.

Remote Sens. 2024, 16, 4146

11 of 19

![img-14.jpeg](img-14.jpeg)

Figure 8. The inverted images of relative permittivity and conductivity obtained from the L₂ norm method based on initial model II. (a–d) are the reconstructed relative permittivity images from frequencies in batch 1, batch 5, batch 9, and batch 14, respectively. (e–h) are the reconstructed conductivity images from frequencies for batch 1, batch 2, batch 3, and batch 4, respectively.

![img-15.jpeg](img-15.jpeg)

Figure 9. The inverted images of relative permittivity and conductivity obtained from the W₂ distance method based on initial model II. (a–d) are the reconstructed relative permittivity images from frequencies in batch 1, batch 5, batch 9, and batch 14, respectively. (e–h) are the reconstructed conductivity images from frequencies for batch 1, batch 2, batch 3, and batch 4, respectively.

Figure 9 shows the inversion results using W₂ – FWI with initial model II, while Figure 8 presents the inversion results using the L₂ norm as the FWI misfit function. Comparing Figures 8 and 9, when there is a significant difference between the initial model and the true model, the traditional L₂ norm-based inversion results are heavily affected by strong artifacts, with the target obscured beneath these false artifacts. In the conductivity inversion results shown in Figure 8, the shape of the target is distorted by spurious high-frequency artifacts, especially the circular target. Figure 8a, which shows the batch 2 results, demonstrates that inversion using low-frequency data in early iterations leads to errors in

Remote Sens. 2024, 16, 4146

12 of 19

the background relative permittivity and conductivity distributions, ultimately resulting in poor imaging quality. This is due to the cycle-skipping phenomenon caused by large initial model errors, trapping the parameter inversion in local minima. However, when the $W_2$ distance is used as the misfit function, although some artifacts are still present, the inversion quality improves significantly. This improvement is attributed to the $W_2$ distance interpreting the misfit as a transportation cost, inherently capturing time-shift information and overall signal variation, thereby alleviating the local minima problem.

In synthetic data, an initial model with minimal error can be established with known information. However, in field data, only limited information is available to construct an approximate initial model, which often differs significantly from the actual subsurface conditions. Therefore, the low initial model dependence and favorable convexity of the $W_2$ distance FWI method is highly beneficial for GPR parameter inversion.

Additionally, tests showed that incorporating data with higher frequencies did not enhance the inversion results, so this study only presents the iterative inversion results for the frequency batches up to 120 MHz.

### 3.2. Example 2: Dependence Analysis of Noise Sensitivity

One of the excellent attributes of the $W_2$-based method is its low sensitivity to noise. Ground-penetrating radar data collected in the field are always contaminated by various noise signals, which decreases the quality of the final inversion results. The application of the Wasserstein distance in seismic velocity FWI inversion has demonstrated that $W_2$ distance, as a misfit function, possesses noise robustness [24] compared to the traditional $L_2$ norm.

According to the mismatch function Formulas (3) and (4), when zero-mean noise is added to the effective signal, the impact on the total transportation cost of the signal can be negligible. Here, let $f$ be the effective signal and $\delta$ be the random noise. The signal affected by noise $g$ can be represented as follows:

$$
g = f + \delta \tag{15}
$$

The random noise $\delta$ has a mean of 0 and a variance of $\eta$. The signal is discretized into n sampling points. For the $L_2$ norm, the following equation is used:

$$
\mathrm{E}|f - g|^2 = \mathrm{O}(\eta) \tag{16}
$$

For the $W_2$ distance, the expected value is as follows:

$$
\mathrm{E}W_2(f, g) = \mathrm{O}\left(\frac{1}{n}\right) \tag{17}
$$

According to Equation (17), if the number of sampling points $n$ is sufficiently large, the impact of noise on the $W_2$ distance mismatch function can be negligible, even if the noise is very strong. Detailed derivations are discussed in [32]. From Equations (16) and (17), it can be seen that compared to the traditional $L_2$ norm, the $W_2$ distance has lower noise sensitivity. The following experiment compares the noise sensitivity of the two methods using the same model in the first section. All experimental methods and settings are the same as in the first section, except that the observation data used for inversion and model I (Figure 4) are used as the initial model.

In this numerical experiment, clean forward simulation signals were first obtained (as shown in Figure 10a). Random noise was then added, with a signal-to-noise ratio (SNR) of 20 dB. The SNR is defined based on the signal power and noise power, and the calculation formula is as follows:

$$
\mathrm{SNR}(\mathrm{dB}) = 10 \log_{10} \frac{P_{\text{signal}}}{P_{\text{noise}}} \tag{18}
$$

Figure 10b shows the observation data for a single source with multiple receivers after adding noise. Figures 11 and 12 compare the results of relative permittivity and conductivity

Remote Sens. 2024, 16, 4146

13 of 19

inversion using the two methods. It can be seen that in the $W_2$ distance method, the impact of random noise on the mismatch function is negligible, so the noise has minimal effect on the inversion results. However, in the traditional $L_2$ norm inversion results, there are many high-frequency artifacts that obscure the geological anomalies, significantly affecting target identification. This further demonstrates that the $W_2$ distance is insensitive to random noise. However, for other types of noise, such as high-frequency or low-frequency noise, using denoised data after processing for inversion is a more straight and effective approach.

![img-16.jpeg](img-16.jpeg)

![img-17.jpeg](img-17.jpeg)

Figure 10. (a) The original multi-offset forward simulation data with the transmitter antenna located at 7 m. (b) The image after adding random noise to the original data (a).

![img-18.jpeg](img-18.jpeg)

![img-19.jpeg](img-19.jpeg)

Figure 11. (a) The relative permittivity inversion result based on the $L_2$ norm for noisy data. (b) The relative permittivity inversion result based on the $W_2$ distance for noisy data.

![img-20.jpeg](img-20.jpeg)

![img-21.jpeg](img-21.jpeg)

Figure 12. (a) The conductivity inversion result based on the $L_2$ norm for noisy data. (b) The conductivity inversion result based on the $W_2$ distance for noisy data.

Remote Sens. 2024, 16, 4146

14 of 19

### 3.3. Example 3: Comparison of Inversion Accuracy of Complex Models

In this section, a comparison of inversion results between the $W_2$ distance and the $L_2$ norm is presented using a two-dimensional complex subsurface model. The comparison demonstrates that the $W_2$ distance provides more accurate inversion results.

The true model and initial model for this experiment are shown in Figure 13. Figure 13a depicts the relative permittivity model, while Figure 13b shows the conductivity model. The model dimensions are $20 \times 7$ m in both horizontal and vertical directions. The grid spacing is $\Delta x = 0.05$ m and $\Delta z = 0.05$ m, and the model is discretized into $N_{m2} = 400 \times 140 = 56,000$ cells. The model is divided into four layers with relative permittivity values of 25, 17, 30, and 13 and conductivity values of 2 mS/m, 1 mS/m, 10 mS/m, and 1 mS/m from the surface to the depth. The second and third layers contain rocks with relative permittivity and conductivity values of 10 and 5 mS/m, respectively. GPR multi-offset data are used for inversion in this study. The emitters, placed on the surface, are spaced 0.5 m apart, totaling 41, as shown by black stars in Figure 13a. The receiver antennas are spaced 0.1 m apart, totaling 201, as indicated by red triangles in Figure 13b. All receiver antennas record the high-frequency electromagnetic signals emitted by each transmitter, forming multi-offset data. The initial relative permittivity and conductivity models are shown in Figure 13c,d. The initial relative permittivity model increases linearly from the surface to the depth, while the initial conductivity model is uniform.

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)

**Figure 13. (a)** True relative permittivity model. **(b)** True conductivity model. In **(a)**, red stars represent transmitter locations. In **(b)**, red triangles represent receiver locations. **(c)** Initial relative permittivity model. **(d)** Initial conductivity model.

Based on the real model, we first compute the synthetic observation data. The simulated GPR data are discretized into 15 batches, with $f_{min} = 1$ MHz and $f_{max} = 70$ MHz. Each batch contains four frequencies, and after ten iterations per batch, the frequency-domain data in the next batch are used for inversion iteration. Additionally, tests show that the iteration converges after batch 15, and frequencies above 70 MHz do not improve the

Remote Sens. 2024, 16, 4146

15 of 19

inversion results. Therefore, the highest frequency shown here is up to 70 MHz. A total of 150 iterations were performed over the 15 batches. Figure 14 shows the relative permittivity inversion results based on the $L_2$ norm, with (a)–(d) representing the inversion results for batch 1, batch 4, batch 7, and batch 11. Figure 15 displays the relative permittivity inversion results based on the $W_2$ distance, with (a)–(d) representing the inversion results for batch 1, batch 4, batch 7, and batch 11. Figure 16 presents the conductivity inversion results based on the $L_2$ norm, with (a)–(d) representing the inversion results for batch 1, batch 2, batch 3, and batch 5. Figure 17 shows the conductivity inversion results based on the $W_2$ distance, with (a)–(d) representing the inversion results for batch 1, batch 2, batch 3, and batch 5.

Comparing the relative permittivity inversion results of the two methods, it is clear that in the low-frequency batches, the $W_2$ distance provides a background value closer to the true model, resulting in more accurate final inversion results. In contrast, the $L_2$ norm, in early iterations (Figure 14a), gives incorrect positions and properties of the block targets (indicated by the gray dashed boxes), leading to significant differences between the final inversion results and the true model. Additionally, the inversion results for the third layer with high relative permittivity (low velocity layer) are notably poorer, showing larger discrepancies from the true values.

In terms of conductivity inversion results, the advantage of the $W_2$ distance is even more pronounced. Due to the low sensitivity of conductivity to amplitude variations and its higher sensitivity to low-frequency signals [4], conductivity inversion is more challenging. The point-by-point calculation method of the $L_2$ norm makes it less sensitive to low-frequency information, resulting in poorer inversion results for conductivity. On the other hand, full-waveform inversion using the $W_2$ distance better captures low-frequency information and provides more accurate conductivity inversion results. Additionally, compared to the $L_2$ norm (Figure 16a), the $W_2$ distance adjusts the background model more rapidly during the inversion process (Figure 17a).

![img-26.jpeg](img-26.jpeg)

![img-27.jpeg](img-27.jpeg)

![img-28.jpeg](img-28.jpeg)

![img-29.jpeg](img-29.jpeg)

**Figure 14.** The relative permittivity inversion images obtained by using the $L_2$ norm as the mismatch function. (a–d) represent the relative permittivity images reconstructed from frequencies in batch 1, batch 4, batch 7, and batch 11, respectively.

Remote Sens. 2024, 16, 4146

16 of 19

![img-30.jpeg](img-30.jpeg)

![img-31.jpeg](img-31.jpeg)

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)

Figure 15. The relative permittivity inversion images obtained by using the W₂ distance as the mismatch function. (a–d) represent the relative permittivity images reconstructed from frequencies in batch 1, batch 4, batch 7, and batch 11, respectively.

![img-34.jpeg](img-34.jpeg)

![img-35.jpeg](img-35.jpeg)

![img-36.jpeg](img-36.jpeg)

![img-37.jpeg](img-37.jpeg)

Figure 16. The conductivity inversion images obtained by using the L₂ norm as the mismatch function. (a–d) represent the conductivity images reconstructed from frequencies in batch 1, batch 2, batch 3, and batch 5, respectively.

Remote Sens. 2024, 16, 4146

17 of 19

![img-38.jpeg](img-38.jpeg)

![img-39.jpeg](img-39.jpeg)

![img-40.jpeg](img-40.jpeg)

![img-41.jpeg](img-41.jpeg)

**Figure 17.** The conductivity inversion images obtained by using the $W_2$ distance as the mismatch function. (a–d) represent the conductivity images reconstructed from frequencies in batch 1, batch 2, batch 3, and batch 5, respectively.

#### 4. Discussion

In this study, to evaluate the effectiveness of the $W_2$ distance, Section 2 introduces entropy regularization and the Sinkhorn algorithm to compute the $W_2$ distance, which reduces the computational complexity of the transport matrix and improves computational speed. It also presents the objective function for GPR multi-scale frequency-domain dual-parameter full-waveform inversion when using the $W_2$ distance as the misfit function. Additionally, this paper presents a data normalization method: Softplus normalization, to ensure that the signed GPR electromagnetic wave data satisfy the non-negativity and mass equality assumptions of the $W_2$ distance. The convexity of the objective functions based on two types of normalization for the $W_2$ distance and the $L_2$ norm were compared by using a Ricker wavelet as an example. It is demonstrated that the $W_2$ distance with Softplus normalization has better convexity.

In Section 3, a multi-scale frequency-domain full-waveform inversion method is used to simultaneously invert for the relative permittivity and conductivity of GPR data. Experiment 1 shows that the $W_2$ distance is less sensitive to low-wavenumber models, reducing dependence on the initial model. Experiment 2 demonstrates that when the number of signal sampling points is sufficiently large, the $W_2$ distance is far more robust to noise compared to conventional $L_2$ norm-based FWI methods. Experiment 3 uses a complex geological model to show that the $W_2$ distance can achieve more reliable and accurate inversion results, particularly in terms of conductivity inversion.

The inherent insensitivity of the $L_2$ norm to low-frequency content is the primary reason why $L_2$ FWI often fails to recover the kinematics of the model. In contrast, the $W_2$ distance is more effective at capturing time-shift information and low-frequency data, making the objective function more convex. This property is crucial for the application of full-waveform inversion methods in situations with poor initial models, strong noise interference, and complex subsurface media. The numerical simulation results in this study

Remote Sens. 2024, 16, 4146

18 of 19

clearly indicate that the quadratic Wasserstein distance is a promising choice for mismatch functions in FWI methods.

## 5. Conclusions

This study developed a high-resolution full-waveform inversion method for GPR relative permittivity and conductivity based on the quadratic Wasserstein ($W_2$) metric. Due to the lack of low-frequency components in the data and the limited accuracy of the initial model, cycle skipping can occur. The sensitivity of the $W_2$ distance to low-frequency information enables it to effectively mitigate local minima issues. To implement the proposed method, the Sinkhorn optimization algorithm was used to solve the optimal transport matrix. Additionally, a Softplus function normalization method was introduced to ensure mass conservation and non-negativity assumptions while maintaining good convexity of the objective function. Three numerical examples demonstrate that the $W_2$-based FWI effectively avoids cycle skipping, exhibits strong noise robustness, and has low dependence on the initial model, with significant improvement in conductivity inversion results. Thus, the quadratic Wasserstein distance is a promising choice for the misfit function in dual-parameter FWI methods for GPR data.

**Author Contributions:** K.L. and H.H. conceived the numerical experiments. K.L., Y.W. and H.H. performed the experiments, analyzed the data, and wrote the paper. Y.W. revised the paper. Y.W., Y.Z. and S.Z. gave advice for the numerical simulation and laboratory experiment. All authors have read and agreed to the published version of the manuscript.

**Funding:** This work was supported by the National Natural Science Foundation of China (Grant No. 42025403) and the Institute of Geology and Geophysics, Chinese Academy of Sciences (Grant No. IGGCAS-202102).

**Data Availability Statement:** The data presented in this study are available on request from the corresponding author. The data are not publicly available due to privacy.

**Conflicts of Interest:** The authors declare no conflicts of interest.

## References

1. 1. Irving, J.D.; Knoll, M.D.; Knight, R.J. Improving crosshole radar velocity tomograms: A new approach to incorporating high-angle traveltime data. *Geophysics* **2007**, *72*, J31–J41. [\[CrossRef\]](#)
2. 2. Binley, A.; Winship, P.; Middleton, R.; Pokar, M.; West, J. High-resolution characterization of vadose zone dynamics using cross-borehole radar. *Water Resour. Res.* **2001**, *37*, 2639–2652. [\[CrossRef\]](#)
3. 3. Fisher, E.; McMechan, G.A.; Annan, A.P. Acquisition and processing of wide-aperture ground-penetrating radar data. *Geophys.* **1992**, *57*, 495–504. [\[CrossRef\]](#)
4. 4. Zhong, S.; Wang, Y.; Zheng, Y. Frequency-domain wavefield reconstruction inversion of ground-penetrating radar based on sensitivity analysis. *Geophys. Prospect.* **2023**, *71*, 1655–1672. [\[CrossRef\]](#)
5. 5. Leong, Z.X.; Zhu, T. Direct velocity inversion of ground penetrating radar data using GPRNet. *J. Geophys. Res. Solid Earth* **2021**, *126*, e2020JB021047. [\[CrossRef\]](#)
6. 6. Liu, B.; Ren, Y.; Liu, H.; Xu, H.; Wang, Z.; Cohn, A.G.; Jiang, P. GPRInvNet: Deep learning-based ground-penetrating radar data inversion for tunnel linings. *IEEE Trans. Geosci. Remote Sens.* **2021**, *59*, 8305–8325. [\[CrossRef\]](#)
7. 7. Leeuwen, T.V.; Herrmann, F.J. A penalty method for PDE-constrained optimization in inverse problems. *Inverse Probl.* **2015**, *32*, 015007. [\[CrossRef\]](#)
8. 8. Lavoué, F.; Brossier, R.; Métivier, L.; Garambois, S.; Virieux, J. Two-dimensional permittivity and conductivity imaging by full waveform inversion of multioffset GPR data: A frequency-domain quasi-Newton approach. *Geophys. J. Int.* **2014**, *197*, 248–268. [\[CrossRef\]](#)
9. 9. Plessix, R.E. A review of the adjoint-state method for computing the gradient of a functional with geophysical applications. *Geophys. J. Int.* **2006**, *167*, 495–503. [\[CrossRef\]](#)
10. 10. Liu, D.C.; Nocedal, J. On the limited memory BFGS method for large scale optimization. *Math. Program.* **1989**, *45*, 503–528. [\[CrossRef\]](#)
11. 11. Virieux, J.; Operto, S. An overview of full-waveform inversion in exploration geophysics. *Geophysics* **2009**, *74*, WCC1–WCC26. [\[CrossRef\]](#)
12. 12. Tarantola, A. Inversion of seismic reflection data in the acoustic approximation. *Geophysics* **1984**, *49*, 1259–1266. [\[CrossRef\]](#)
13. 13. Klotzsche, A.; Vereecken, H.; van der Kruk, J. Review of crosshole ground-penetrating radar full-waveform inversion of experimental data: Recent developments, challenges, and pitfalls. *Geophysics* **2019**, *84*, H13–H28. [\[CrossRef\]](#)

Remote Sens. 2024, 16, 4146

19 of 19

1. 14. Meles, G.; Greenhalgh, S.; Van der Kruk, J.; Green, A.; Maurer, H. Taming the non-linearity problem in GPR full-waveform inversion for high contrast media. *J. Appl. Geophys.* **2012**, *78*, 31–43. [\[CrossRef\]](#)
2. 15. Ernst, J.R.; Maurer, H.; Green, A.G.; Holliger, K. Full-waveform inversion of crosshole radar data based on 2-D finite-difference time-domain solutions of Maxwell's equations. *IEEE Trans. Geosci. Remote Sens.* **2007**, *45*, 2807–2828. [\[CrossRef\]](#)
3. 16. Pratt, R.G.; Shin, C.; Hick, G.J. Gauss–Newton and full Newton methods in frequency–space seismic waveform inversion. *Geophys. J. Int.* **1998**, *133*, 341–362. [\[CrossRef\]](#)
4. 17. Feng, X.; Ren, Q.; Liu, C.; Zhang, X. Joint acoustic full-waveform inversion of crosshole seismic and ground-penetrating radar data in the frequency domain. *Geophysics* **2017**, *82*, H41–H56. [\[CrossRef\]](#)
5. 18. Feng, D.; Ding, S.; Wang, X.; Wang, X. Wavefield reconstruction inversion of GPR data for permittivity and conductivity models in the frequency domain based on modified total variation regularization. *IEEE Trans. Geosci. Remote Sens.* **2021**, *60*, 1–14. [\[CrossRef\]](#)
6. 19. Monge, G. *Mémoire Sur la théOrie Des déBlais ET Des Remblais*; De l'Imprimerie Royale: Paris, France, 1781; pp. 666–704.
7. 20. Kantorovich, L.V. On the Translocation of Masses. *J. Math. Sci.* **2006**, *133*, 5903314. [\[CrossRef\]](#)
8. 21. Engquist, B.; Froese, B.D. Application of the Wasserstein metric to seismic signals. *Commun. Math. Sci.* **2013**, *12*, 979–988. [\[CrossRef\]](#)
9. 22. Qiu, L.; Ramos-Martínez, J.; Valenciano, A.; Yang, Y.; Engquist, B. Full-waveform inversion with an exponentially encoded optimal-transport norm. In *SEG Technical Program Expanded Abstracts 2017*; Society of Exploration Geophysicists: Tulsa, OK, USA, 2017; pp. 1286–1290.
10. 23. Métivier, L.; Brossier, R.; Mérigot, Q.; Oudet, E.; Virieux, J. Increasing the robustness and applicability of full-waveform inversion: An optimal transport distance strategy. *Lead. Edge* **2016**, *35*, 1060–1067. [\[CrossRef\]](#)
11. 24. Engquist, B.; Froese, B.D.; Yang, Y. Optimal transport for seismic full waveform inversion. *Commun. Math. Sci.* **2016**, *14*, 2309–2330. [\[CrossRef\]](#)
12. 25. Engquist, B.; Yang, Y. Seismic imaging and optimal transport. *Not. Int. Consort. Chin. Math.* **2020**, *8*, 27–49. [\[CrossRef\]](#)
13. 26. Li, D.; Lamoureux, M.P.; Liao, W. Application of an unbalanced optimal transport distance and a mixed L1/Wasserstein distance to full waveform inversion. *Geophys. J. Int.* **2022**, *230*, 1338–1357. [\[CrossRef\]](#)
14. 27. Deng, J.; Zhu, P.; Kofman, W.; Jiang, J.; Yuan, Y.; Hérique, A. Electromagnetic full waveform inversion based on quadratic Wasserstein metric. *IEEE Trans. Antennas Propag.* **2022**, *70*, 11934–11945. [\[CrossRef\]](#)
15. 28. Cuturi, M.; Doucet, A. Fast computation of Wasserstein barycenters. In Proceedings of the International Conference on Machine Learning 2014, Beijing, China, 21–26 June 2014; pp. 685–693.
16. 29. Cuturi, M. Sinkhorn distances: Lightspeed computation of optimal transport. *Adv. Neural Inf. Process. Syst.* **2013**, *26*, 2292–2300.
17. 30. Engquist, B.; Yang, Y. Optimal transport based seismic inversion: Beyond cycle skipping. *Commun. Pure Appl. Math.* **2022**, *75*, 2201–2244. [\[CrossRef\]](#)
18. 31. Irving, J.; Knight, R. Numerical modeling of ground-penetrating radar in 2-D using MATLAB. *Comput. Geosci.* **2006**, *32*, 1247–1258. [\[CrossRef\]](#)
19. 32. Yang, Y.; Engquist, B.; Sun, J.; Hamfeldt, B.F. Application of optimal transport and the quadratic Wasserstein metric to full-waveform inversion. *Geophysics* **2018**, *83*, R43–R62. [\[CrossRef\]](#)

**Disclaimer/Publisher's Note:** The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content.