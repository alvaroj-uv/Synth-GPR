136

Bayesian versus Frequentist Methods of Inference

we have assimilated the data and the prior information. The point of using the data is that the posterior information hopefully constrains the model more tightly than the prior model distribution.

However, the selection of a prior statistical model can in practice be somewhat shaky. For example, in a seismic survey we may have a fairly accurate idea of the realistic ranges of seismic velocity and density, and perhaps even of the vertical correlation length (if bore-hole measurements are available). However, the horizontal length scale of the velocity and density variation is to a large extent unknown. Given this, how can Bayesian inversion be so popular when our prior knowledge is often so poor? The reason for this is that in practice the prior model is used to regularize the posterior solution. Via a succession of different calculations, the characteristics of the prior model are often tuned in such a way that the retrieved model has subjectively agreeable features. But logically, the prior distribution must be fixed before hand. The features used to tune the prior should in fact be included as part of the prior information [GS97]. So, the practice of using the data to tune the prior suggests that the reason for the popularity of Bayesian inversion within the Earth sciences is inconsistent with the underlying philosophy. A common attitude seems to be: 'If I hadn't believed it, I wouldn't have seen it.'

Since Bayesian statistics relies completely on the specification of a prior statistical model, the flexibility taken in using the prior model as a knob to tune properties of the retrieved model is completely at odds with the philosophy of Bayesian inversion. One can, however, use an *empirical Bayes* approach to use data to help determine a prior distribution. But having used the data to select a prior, one has to correct the uncertainty estimates so as not to be overconfident [see Carlin and Louis [CL96]]. This correction is not usually done in geophysical Bayesian inversion.

### 10.0.1 Bayesian Inversion in Practice

There are two important questions that have to be addressed in any Bayesian inversion:

- How do we represent the prior information? This applies both to the prior model information and to the description of the data statistics.

The second question is the easiest one to answer, at least in principle. It is just a matter of applying Bayes' theorem to compute the posterior distribution. We then use this distribution to study the statistics of different parameter estimates. For example, we can find credible regions for the model parameters given the data, or simply use posterior means as estimates and posterior standard deviations as 'error bars'. However, very seldom will we be able to compute all the posterior estimates analytically; we often

1