Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

\[
\boldsymbol {f} _ {\mathrm{ex}} = \left\{ \begin{array}{l} \boldsymbol {f} _ {1} \\ \boldsymbol {f} _ {2} \\ \dots \\ \boldsymbol {f} _ {k} \\ \dots \\ \boldsymbol {f} _ {N _ {s}} \end{array} \right\} \left\{ \begin{array}{l} p _ {\boldsymbol {x}} (\boldsymbol {x} _ {1}, t _ {k}) \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {2}, t _ {k}) \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {3}, t _ {k}) \\ \dots \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {1}, t _ {k}) \end{array} \right\} \quad \boldsymbol {P} _ {\mathrm{ex}} = \left[ \begin{array}{c} \boldsymbol {P} _ {1} \\ \boldsymbol {P} _ {2} \\ \dots \\ \boldsymbol {P} _ {k} \\ \dots \\ \boldsymbol {P} _ {N _ {s}} \end{array} \right] \left[ \begin{array}{c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c} \end{array} \right] \left[ \begin{array}{c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c
\]

Fig. 3. Structures of \( f_{\mathrm{ex}} \) and \( P_{\mathrm{ex}} \).

Optimization Stage Algorithm: The initial parameters include the initial hyperrectangle  \( C^{s} = [0,1]^{s} \) , the current optimization iteration  \( n_{opt} = 1 \) , the maximum optimization iterations  \( N_{opt} \) , the number of Voronoi cells  \( N_{sel} \)  (which may change with optimization iterations), the interval of iterations for updating the Kriging model  \( n_{upd} \) , the objective function threshold  \( J_{thr} \) , and the objective function tolerance h. Then execute the following procedure (refer to Fig. 4 where the sketches are examples for a 2-dimensional case):

#### 1. Space Partitioning:

Generate \(N_{\mathrm{sel}}\) Sobol sequence points within the hyperrectangle \(C^s\), forming the initial partition point set \(P_{\mathrm{sel}} = \{\theta_1, \theta_2, \dots, \theta_{N_{\mathrm{sel}}}\}\), and partition the hyperrectangle \(C^s\) into multiple Voronoi cells.

#### 2. Local Computation:

Generate  \( N_{den} = N_{sel} n_{q} \)  densified points  \( \{\tilde{\theta}_{1}, \tilde{\theta}_{2}, \ldots, \tilde{\theta}_{N_{den}}\} \)  within  \( C^{s} \)  and ensured that each Voronoi cell contains  \( n_{q} \)  densified points. Then, use the trained Kriging model to predict the response of all densified points at each time instant. Compute  \( p_{q}(x, t) \) ,  \( P_{ex} \)  according to Eqs. (15), (31a) and (31b).

#### 3. Optimization Computation:

If  \( n_{opt} > 1 \) , extract the objective function value  \( J_{out}^{t} \)  from the previous iteration; otherwise, skip this step. Solve the optimization problem expressed in Eq. (27) and yield the assigned probability vector  \( y = (\Pr_{1}, \Pr_{2}, \ldots, \Pr_{N_{\mathrm{sel}}})^{\mathrm{T}} \)  for each Voronoi cell and the minimum objective function value  \( J_{out} \) . After computation, check if any of the following conditions are met:

\[
n _ {\text { opt }} \geq N _ {\text { opt }}, \quad J _ {\text { out }} \leq J _ {\text { thr }}, \quad | J _ {\text { out }} ^ {\prime} - J _ {\text { out }} | \leq h \tag {35}
\]

If any condition is satisfied, stop the computation and proceed to the post-processing stage. If not, update  \( n_{opt} \)  to  \( n_{opt} + 1 \) . Check whether the remainder of  \( n_{opt} \)  divided by  \( n_{upd} \)  is 0. If it is, update the Kriging model by adding all or some of the partition points into the training point set  \( P_{tr} \) ; otherwise, do not update the model. Then, check if the remainder is 1. If it is, proceed to Step; otherwise, proceed to Step 4.

#### 4. Point Set Densification:

Using the assigned probabilities as a weight, new partition points are added within each Voronoi cell, thereby expanding the set  \( P_{sel} \) . Let  \( N_{add} \)  denote the total number of added partition points in this step, then the number of new points added to the qth cell  \( N_{add,q} \)  is approximately  \( Pr_{q}N_{add} \) . This step ensures that Voronoi cells with higher assigned probabilities are subdivided into finer cells. Once this step is completed, return to Step 2.

#### 5. Point Set Reorganization:

Adjust the hyperrectangle  \( C^{s} \) : For the ith dimension, the probability centroid  \( \hat{\theta}_{i} \)  and standard deviation  \( \sigma_{i} \)  of that dimension are calculated based on the ith components of coordinates of partition points and the assigned probabilities. Then, the distribution range of the ith dimension for both the partition and densified points is adjusted to the new interval:

\[
I _ {i} = \left[ \max \left(\hat {\theta} _ {i} - a _ {i} \sigma_ {i}, 0\right), \min \left(\hat {\theta} _ {i} + a _ {i} \sigma_ {i}, 1\right) \right] \tag {36a}
\]

\[
\hat {\theta} _ {i} = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} \theta_ {q, i}, \quad \sigma_ {i} = \sqrt {\sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} (\theta_ {q , i} - \hat {\theta} _ {i}) ^ {2}} \tag {36b}
\]

where  \( \alpha_{i} \)  is a parameter related to the random source distribution characteristics. For Gaussian distribution,  \( \alpha = 3 \)  can be used. The hyperrectangle  \( C^{s} \)  is then updated to the Cartesian product of the new intervals for each dimension:

\[
C ^ {s} = I _ {1} \times I _ {2} \times \dots \times I _ {s} \tag {37}
\]

Once this step is completed, return to Step 1.

#### Post-processing Stage Algorithm:

The purpose of this step is to calculate the PDF of each component of the random source based on the assigned-probabilities.

#### 1. Calculation of the Empirical Distribution Function:

For ith component of randoms source, the empirical distribution function  \( \hat{F}_{i}(\theta_{i}) \)  can be obtained as follows:

\[
\hat {F} _ {i} (\theta_ {i}) = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} I (\theta_ {q, i} \leq \theta_ {i}) \tag {38}
\]

where \(I(\bullet)\) is the indicator function.

#### 2. Adjustment:

The function \(\hat{F}_i\) exhibits discontinuous steps at each partition point \(\theta_{q,i}\), with the values corresponding to the respective assigned probabilities \(\mathrm{Pr}_q\). To smooth this, the function values at each point \(\theta_{q,i}\) are reduced by \(1/2\mathrm{Pr}_q\), with boundary values set to 0 and 1. This is equivalent to connecting the midpoints of each step in the empirical distribution function. The specific process is as follows:

\[
\hat {F} _ {i} ^ {\prime} \left(\theta_ {q, i}\right) = \left\{ \begin{array}{l l} 0, & q = 0 \\ \sum_ {m = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {m} I \left(\theta_ {m, i} \leq \theta_ {q, i}\right) - \frac {1}{2} \operatorname * {P r} _ {q}, & 1 \leq q \leq N _ {\mathrm{sel}} \\ 1, & q = N _ {\mathrm{sel}} + 1 \end{array} \right. \tag {39}
\]

The boundary points are defined as:

\[
\theta_ {0, i} = \max (2 \theta_ {1, i} ^ {*} - \theta_ {2, i} ^ {*}, 0), \quad \theta_ {N _ {\mathrm{sel}} + 1, i} = \min (2 \theta_ {N _ {\mathrm{sel}}, i} ^ {*} - \theta_ {N _ {\mathrm{sel}} - 1, i} ^ {*}, 1) \tag {40}
\]

where \(\{\theta_{q,i}^{*}, q = 1,2,\dots,N_{\mathrm{sel}}\}\) are the result of sorting \(\{\theta_{q,i}, q = 1,2,\dots,N_{\mathrm{sel}}\}\) in ascending numerical order.

#### 3. Linear Interpolation and Smoothing:

The discrete points  \( \{(\theta_{q,i},\hat{F}_{i}^{\prime}(\theta_{q,i})),q=0,1,\ldots,N_{\mathrm{sel}}+1\} \)  are linearly interpolated over the interval  \( \theta_{i}\in[0,1] \) , and the interpolation results are then smoothed using a moving average filter. The length of the moving average can be set empirically, typically between 1/30 and 1/10 of the length of the interval  \( I_{i} \)  in Eq. (36). This yields the final distribution function calculation result  \( F_{i}(\theta_{i}) \) .

4. Numerical Differentiation: The function  \( F_{i}(\theta_{i}) \)  is numerically differentiated to obtain its derivative  \( \hat{p}_{i}(\theta_{i}) \) , and the result is processed to ensure non-negativity in the following manner:

\[
\hat {p} _ {i} ^ {\prime} (\theta_ {i}) = \max (0, \hat {p} _ {i} (\theta_ {i})) \tag {41}
\]

6