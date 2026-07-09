8.3 Computer Example: Cross-well tomography

125

The second complicating factor is that a “travel time” is only unambiguously defined at asymptotically high frequencies. In general, we could define the travel time in various ways: first recorded energy above a threshold, first peak after the threshold value is surpassed, and others. Further, the travel times themselves must be inferred from the recorded data, although it is possible in some cases that this can be done automatically; perhaps by using a triggering mechanism which records a time whenever some threshold of activity is crossed.

For purposes of this example, we will neglect both of these difficulties. We will compute the travel times as if we were dealing with an infinite frequency (perfectly localized) pulse, and we will assume straight ray propagation. The first assumption is made in most travel time inversion calculations since there is no easy way around the difficulty without invoking a more elaborate theory of wave propagation. The second assumption, that of linearity, is easily avoided in practice by numerically tracing rays through the approximate medium. But we won’t worry about this now.

## 8.3 Computer Example: Cross-well tomography

In the code directory you will find various implementations of straight-ray tomography. These are extensive codes and will not be described in detail here. They begin by setting up the source/receiver geometry of the problem, computing a Jacobian matrix and fake travel times, adding noise to these and doing the least squares problem via SVD. Here we just show some of the results that you will be able to get.

In Figure (8.8) you see a plot of the Jacobian matrix itself. The $i - j$ element of this matrix is the length the $i$-th ray travels in the $j$-th cell. This comes from discretizing the travel time integral ($t = \int s(\mathbf{r})d\mathbf{r}$) along each ray (one for each travel time). Black indicates zero elements and white nonzero. This particular matrix is about 95% sparse, so until we take advantage of this fact, we’ll be doing a lot of redundant operations, e.g., $0 \times 0 = 0$.

Below this we show the “hit count”. This is the summation of the ray segments within each cell of the model and represents the total “illumination” of each cell.

Below this we show the exact model whose features we will attempt to reconstruct via a linear inversion.

Finally, before we can do an inversion, we need some data to invert. First we’ll compute the travel times in the true model shown above, then we’ll compute the travel times through a background model which is presumed to be correct except for the absence of the anomaly. It’s the difference between these two that we take to be the right hand side of the linear system

$$J\delta\mathbf{m} = \delta\mathbf{d}$$

relating model perturbations to data perturbations. The computed solutions are shown

1