29

We have assumed that the number of layers is known, 40 in this example, but this is usually not the case. Choosing too many layers may lead to an over-fitting of the data. In other words we may end up fitting noise induced structures. Using an insufficient number of layers will not capture important features in the data. There are tricks and methods to try to avoid over- and under-fitting. In the present example we do not have to worry since we will be using simulated data. To determine the slowness values through (3.5) we have used a truncated SVD$^{a}$

reconstruction, throwing away all the eigenvectors in the generalized inverse approximation of s that are not required to fit the data at the $\chi^{2} = 1$ level. Fitting the data this level means that, on average, all the predicted data agree with the measurements to within one $\sigma$. The resulting model is not unique, but it is representative of models that do not over-fit the data (to the assumed noise level).

### 3.0.2 Travel time fitting

We will consider the problem of fitting the data under two different assumptions about the noise. Figure 3.3 shows the observed and predicted data for models that fit the travel times on average to within 0.3 ms and 1.0 ms. Remember, the actual pseudo-random noise in the data is fixed throughout, all we are changing is our assumption about the noise, which is reflected in the data misfit criterion.

We refer to these as the optimistic (*low noise*) and pessimistic (*high noise*) scenarios. You can clearly see that the smaller the assumed noise level in the data, the more the predicted data must follow the pattern of the observed data. It takes a complicated model to predict complicated data! Therefore, we should expect the best fitting model that produced the low noise response to be more complicated than the model that produced the high noise response. If the error bars are large, then a simple model will explain the data.

Now let us look at the models that actually fit the data to these different noise levels; these are shown in Figure 3.4. It is clear that if the data uncertainty is only 0.3 ms, then the model predicts (or requires) a low velocity zone. However, if the data errors are as much as 1 ms, then a very smooth response is enough to fit the data, in which case a low velocity zone is not required. In fact, for the high noise case essentially a linear $v(z)$ increase will fit the data, while for the low noise case a rather complicated model is required. (In both cases, because of the singularity of $J$, the variances of the estimated parameters become very large near the bottom of the borehole.)

Hopefully this example illustrates the importance of understanding the noise distribu-

$^{a}$We will study the singular value decomposition (SVD) in great detail later. For now just consider it to be something like a Fourier decomposition of a matrix. From it we can get an approximate inverse of the matrix, which we use to solve Equation3.3. Truncating the SVD is somewhat akin to low-pass filtering a time series in the frequency domain. The more you truncate the simpler the signal.

1