H22

Cordua et al.

defined by geostatistical algorithms. This sampling strategy provides a means of using a variable exploration step size when sampling such high-dimensional probability densities. This method is briefly outlined in the following.

### Sampling geostatistically defined a priori information

Hansen et al. (2012) suggest a strategy referred to as sequential Gibbs sampling, which is a method that is capable of sampling probability densities defined by geostatistical algorithms based on sequential simulation. Originally, sequential simulation was used to generate realizations of two-point based statistical models, such as Gaussian models (e.g., Gomez-Hernandez and Journel, 1993). Two-point statistical models are limited to specify the spatial variability between pairs of data (hence the name two-point statistics) defined by a covariance model. Two-point statistics does not provide enough information to model plausible geological structures, such as channels and tortuosity. This can be overcome by using a model based on multiple-point statistics, as suggested by Guardiano and Srivastava (1993). In multiple-point-based statistical models, the a priori information is learned from a training image. The training image is scanned by a template that jointly considers spatial variability among a number of (more than two) pixel values in the image to obtain a joint probability distribution that holds information about these spatial correlations. The model parameter values are subsequently sequentially simulated from conditional probabilities on the basis of the jointly considered pixel values (e.g., Strebelle, 2002). The algorithm originally suggested by Guardiano and Srivastava (1993) was, however, computationally unfeasible. It originally was not until an efficient way of storing multiple-point statistics in machine memory was proposed that the use of multiple-point based models became computationally feasible (Strebelle, 2002). See e.g., Remy et al. (2008) for numerous examples of the application of sequential simulation from both two-point and multiple-point-based a priori models.

In this study sequential Gibbs sampling serves as the black box algorithm that samples the a priori probability density $\rho_M(\mathbf{m})$, described by a geostatistical simulation algorithm, with a controllable exploration step size. The flow of the sequential Gibbs sampling is as follows:

1) An initial unconditional realization of the a priori probability density, $\mathbf{m}_{\text{current}}$, defined in a 2D regular grid of model parameters is provided.
2) A square subarea, corresponding to model parameters $\mathbf{m}_{\text{subarea}}$, with side-length $E_{\text{step}}$ (exploration step size) of the current model $\mathbf{m}_{\text{current}}$ is randomly chosen.
3) A realization of the conditional probability density $\rho_M(\mathbf{m}_{\text{subarea}}|\tilde{\mathbf{m}}_{\text{current}})$ is obtained using sequential simulation. $\tilde{\mathbf{m}}_{\text{current}}$ are the current model parameters outside the subarea. $\rho_M(\mathbf{m})$ is an a priori probability density that may be described by either two- or multiple-point statistics. This step is an application of the Gibbs sampler where sequential simulation is used to efficiently generate a realization from the conditional probability density (hence the name sequential Gibbs sampling). In practice this is performed simply by running the sequential simulation algorithm conditional to the model parameters outside the subarea. In this way a new, perturbed model, $\mathbf{m}_{\text{propose}}$ is obtained.
4) The proposed model becomes the current model and steps 2 and 3 are repeated to obtain multiple realizations of the a priori probability density.

Recall that, when applying sequential Gibbs sampling as an a priori model sampler in the extended Metropolis algorithm, the current model $\mathbf{m}_{\text{current}}$ is reused if the proposed model $\mathbf{m}_{\text{propose}}$ is rejected by the Metropolis rule. Moreover, the resemblance (i.e., correlation) between the current and proposed model, and thus the average Metropolis acceptance probability (cf. the Metropolis rule), can be controlled by the explorations step size $E_{\text{step}}$ (i.e., the side length of the resimulated area).

### The likelihood function and correlated data uncertainties

GPR or seismic full-waveform data are often contaminated with temporally correlated uncertainties along the individual waveform traces or spatially correlated (i.e., static) errors among data related to certain transmitter (source) or receiver positions. The probabilistic formulation of the inverse problem allows for an arbitrary data uncertainty model and it is, therefore, possible to account for these correlations in the data uncertainties. In the present study we consider that data uncertainties are Gaussian distributed with a temporal correlation along the individual waveform traces, but are uncorrelated among the individual traces. This type of uncertainty influences the state of information on the model parameters provided by the data and is, therefore, accounted for through the likelihood function. This particular likelihood function takes on the following form

$$L(\mathbf{m}) = c \prod_{k=1}^K \exp \left[ -\frac{1}{2} (g(\mathbf{m})^k - \mathbf{d}_{\text{obs}}^k)^\top \mathbf{C}_D^{-1} (g(\mathbf{m})^k - \mathbf{d}_{\text{obs}}^k) \right], \quad (4)$$

where $g(\mathbf{m})^k$ and $\mathbf{d}_{\text{obs}}^k$ are vectors that contain the simulated and observed waveform traces related to the $k$th transmitter-receiver pair. $K$ is the total number of waveform traces (i.e., transmitter-receiver pairs). The factor $c$ is a normalization constant. The term $\mathbf{C}_D$ is the data covariance matrix that defines the variances and covariances of the data uncertainties. The temporal correlation of the data uncertainties is described by an exponential correlation function (e.g., Goovaerts, 1997)

$$\mathbf{C}_D(i, j) = c \exp \left( \frac{-3s(i, j)}{a} \right), \quad (5)$$

where $c$ is the sill (i.e., variance) and $a$ is the range (i.e., correlation length) of the uncertainties. The term $s(i, j)$ is the temporal distance between the $i$th and $j$th sample point along the waveforms. $\mathbf{C}_D$ is a symmetric $N \times N$ matrix, where $N$ is the number of samples in the individual waveform traces.

Cordua et al. (2009) quantified the influence of static-like errors in crosshole GPR experiments, which are data uncertainties that are spatially correlated among data related to the individual transmitter and receiver positions. This kind of data uncertainty may also be accounted for through the data covariance matrix, but this is not considered here. For a description of how to set up a data covariance matrix that accounts for static (i.e., spatially correlated) errors, see Cordua et al. (2008).

### The burn-in period

If the probability that a sampling algorithm at any time enters an infinitesimal neighborhood $N_j$, that surrounds the model $\mathbf{m}_j$, is

Downloaded 02 Mar 2012 to 130.225.69.247. Redistribution subject to SEG license or copyright; see Terms of Use at http://segdl.org/