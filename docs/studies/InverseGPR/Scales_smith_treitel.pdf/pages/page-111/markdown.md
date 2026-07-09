96

A Summary of Probability and Statistics

The vector $z$ should now have a standard deviation of approximately 1 and a correlation length of 10. To see the autocorrelation of the vector you could do:

plot(corr(z,200))

the autocorrelation function will be approximately exponential for short lags. For longer lags you will see oscillatory departures from exponential behavior—even though the samples are drawn from an analytic exponential covariance. This is due to the small number of realizations. From the exponential part of the autocorrelation you can estimate the correlation length by simply looking for the point at which the autocorrelation has decayed by $1/e$. Or you can fit the log of the autocorrelation with a straight line.

## 6.9 Random Fields

If we were to make $N$ measurements of, say, the density of a substance, we could plot these $N$ data as a function of the sample number. This plot might look something like the top left curve in Figure 6.6. But these are $N$ measurements of the same thing, unless we believe that the density of the sample is changing with time. So a histogram of the measurements would approximate the probability density function of the parameter and that would be the end of the story.

On the other hand, curves such as those in Figure 6.6 might result from measuring a random, time-varying process. For instance, these might be measurements of a noisy accelerometer, in which case the plot would be $N$ samples of voltage versus time. But then these would not be $N$ measurements of the same parameter, rather they would constitute a single measurement of a random function of time, sampled at $N$ times. The distinction we are making here is the distinction between a scalar-valued random process and a random function. Now when we measure a function we always measure it at a finite number of locations (in space or time). So our measurements of random function result in finite-dimensional random vectors. This is why the sampling of a time series of voltage, say, at $N$ times, is really the realization of an $N$-dimensional random process. For such a process it is not sufficient to simply make a histogram of the samples. We need higher order characterizations of the probability law behind the time-series in order to account for the correlations of the measured values. This is the study of *random fields* or *stochastic processes*.

A real-data example of measurements of a random field is shown in Figure 6.7. These traces represent 38 realizations of a time series recorded in a random medium. In this case the randomness is spatial: each realization is made at a different location in the medium. But you could easily imagine the same situation arising with a temporal random process. For example, these could be measurements of wave propagation in a medium undergoing random fluctuations in time, such as the ocean or the atmosphere.

0