Monte Carlo full-waveform inversion

H21

coverage. Finally, we demonstrate how the geostatistically formulated a priori information serves as a guide in the initial burn-in part of the inversion procedure. In this way, convergence of the suggested full-waveform inversion algorithm becomes independent of the initial model.

The present method is completely explicit with regard to the data uncertainty model and a priori information. Establishment of an adequate a priori information and data uncertainty model (comprising data noise and modeling inadequacies) demands effort from the user to obtain trustworthy a posteriori probability density. These issues are far from trivial when considering field experiments and are beyond the scope of this work.

## METHODOLOGY

Consider that the subsurface can be represented by a discrete set of model parameters, m (referred to as the model) and that a data set, d, of indirect observations of the model parameters is provided. The model parameters describe some physical properties of the subsurface that influence the data. Hence, the forward relation between the model and the data can be expressed as the relation (e.g., Tarantola, 2005)

$$\mathbf{d} = g(\mathbf{m}), \tag{1}$$

in which g is a linear or nonlinear mapping operator that often relies on a physical law. In this particular study the model represents a tomographic image of dielectric permittivity of the subsurface material, and data are waveforms of the vertical electrical component of electromagnetic waves propagated across the model between two boreholes. The forward relation in equation 1 is given as a finite-difference time-domain (FDTD) solution of Maxwell's equations (Ernst et al., 2007b). However, any numerical wave propagation modeling strategy (for GPR or seismic signals) can be applied. The inverse problem is to infer information about the model parameters on the basis of a set of data (and their uncertainties), a priori information about the model, and the forward relation between the model and the data.

In a Bayesian formulation the solution to the inverse problem is given as an a posteriori probability density, which can be formulated as (e.g., Tarantola, 2005)

$$\sigma_M(\mathbf{m}) = c\rho_M(\mathbf{m})L(\mathbf{m}), \tag{2}$$

where c is a normalization constant, $\rho_M(\mathbf{m})$ is the a priori probability density, and $L(\mathbf{m})$ is the likelihood function. $\rho_M(\mathbf{m})$ describes the probability that the model satisfies the a priori information. $L(\mathbf{m})$ describes how well the modeled (i.e., simulated) data explain the observed data, given a statistical description of the data noise and modeling inadequacies (from here on referred to as the data uncertainty model). Hence, the a posteriori probability density describes the resulting state of information on the model parameters provided by the independent states of information given by the data (related to the model through the forward relation) and an a priori state of information on the model parameters. Hence, an adequate specification of the data uncertainty model (through the likelihood function) as well as the a priori information are crucial in order to ensure a correct a posteriori state of information (i.e., solution of the inverse problem).

## Sampling the a posteriori probability density

A highly nonlinear inverse problem refers to the case in which the a priori probability density is far from being Gaussian or the likelihood function is highly non-Gaussian (typically) due to the nonlinear forward relation between model and data. According to equation 2 the product of these non-Gaussian probability densities signifies a highly non-Gaussian a posteriori probability density. In the case of full-waveform inversion, the forward relation is expected to be highly nonlinear. Moreover, realistic a priori information, as we introduce here, is typically far from being Gaussian.

The extended Metropolis algorithm is a versatile tool which, in particular, is useful to sample the a posteriori probability density of nonlinear inverse problems using arbitrarily complex a priori information. This algorithm is convenient in that it does not need an explicit expression of the a priori probability density. A black box algorithm that is able to perform a random walk in the a priori probability density is sufficient (Mosegaard and Tarantola, 1995). In this study we use sequential Gibbs sampling, which will be described below, as the black box algorithm for sampling the a priori probability density.

The extended Metropolis Algorithm consists of two randomized steps:

1) Exploration: one proposes a candidate model, $\mathbf{m}_{\text{propose}}$, which is a perturbation of a current model, $\mathbf{m}_{\text{current}}$, and at the same time is a realization of the a priori probability density.
2) Exploitation: one decides if the proposed model should be accepted or rejected. The proposed model is accepted with the Metropolis acceptance probability (referred to as the Metropolis rule)

$$P_{\text{accept}} = \min \left( 1, \frac{L(\mathbf{m}_{\text{propose}})}{L(\mathbf{m}_{\text{current}})} \right), \tag{3}$$

where $L(\mathbf{m}_{\text{propose}})/L(\mathbf{m}_{\text{current}})$ is the ratio between the likelihood evaluated in the proposed and the current model, respectively. If accepted, the proposed model becomes the current model and is a realization of the a posteriori probability density. Otherwise the proposed model is rejected and the current model counts again. Thus, in each iteration, the sample size of the a posteriori probability density increases.

The exploration step constitutes the strategy by which proposed models are drawn from the a priori probability density. For small exploration steps the proposed model will be relatively highly correlated with the current model, compared with large exploration steps. Thus, according to equation 3, small exploration steps will result in a high acceptance probability and vice versa. Recall that each evaluation of the likelihood function involves a computationally expensive (FDTD) forward calculation. It is, therefore, important to choose an appropriate exploration step size that does not explore the a posteriori probability density too slowly, but on the other hand does not waste too many expensive evaluations of the likelihood that are very unlikely to be accepted. In particular, the exploration strategy becomes very important when dealing with high-dimensional probability densities, since traditional sampling strategies may lead to a very inefficient exploration strategy (Hansen et al., 2008; 2012). Recently, Hansen, et al., (2008; 2012) introduced a flexible sampling strategy to sample high-dimensional a priori probability densities

Downloaded 02 Mar 2012 to 130.225.69.247. Redistribution subject to SEG license or copyright; see Terms of Use at http://segdl.org/