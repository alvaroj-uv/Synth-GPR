142

Bayesian versus Frequentist Methods of Inference

### 10.2.1 Bayes Risk

Start with an observation, $d$, from $N(\eta, 1)$ and suppose we know a priori that $|\eta|$ is bounded by $\beta$. We incorporate the bound by assigning to $\eta$ a prior uniformly distributed on $[-\beta, \beta]$. The joint distribution of $\eta$ and $d$ is then

$$f(d, \eta) = \frac{1}{2\beta} \mathcal{I}_{[-\beta, \beta]} \frac{1}{\sqrt{2\pi}} \exp \left[ -\frac{1}{2}(d - \eta)^2 \right],$$

where $\mathcal{I}_{[-\beta, \beta]}(x) = 1$ for $x \in [-\beta, \beta]$ and zero otherwise.

We reproduce Stark's Monte Carlo calculation of the Bayes risk for this problem. Figure 10.1 shows the Bayes risk, using a uniform prior on $[-\beta, \beta]$, and the minimax risk to be described next. As the constraint weakens ($\beta$ increases) the Bayes risk gets closer to 1. (The dashed and dotted curves in this figure will be explained in the next section.)

### 10.2.2 The Flat Prior is Informative

We have used the uniform distribution to 'soften' (i.e., convert to a probabilistic statement) the constraint $|\eta| \leq \beta$. Now we want to measure the effect of this constraint softening. Have we included more information than we really had?

Given the observation, $d$, from $N(\eta, 1)$ and knowing that $|\eta| \leq \beta$, what is the worst risk (mean square error) we may hope to achieve with the *best* possible estimator without imposing a prior distribution on $\eta$? In other words we want to compute the *minimax risk*, $R(\beta)$, given the bound $\beta$

$$R(\beta) = \min_{\delta} \max_{\eta \in [-\beta, \beta]} \mathrm{E}_P [\eta - \delta(d)]^2.$$

$R(\beta)$ is a lower bound for the maximum risk of any other estimator. Although it is difficult to compute its exact value, it is easy to see that $R(\beta) \leq \min\{\beta^2, 1\}$. In addition, Donoho et al. [DLM90] show that

$$\frac{4}{5} \frac{\beta^2}{\beta^2 + 1} \leq R(\beta).$$

Figure 1 shows upper and lower bounds for the minimax risk as a function of $\beta$. Note that for $\beta \leq 3$ the Bayes risk is outside the minimax bounds. This is an artifact of the way we have 'softened' the bound. In other words, the uniform prior distribution injects more information than the hard bound on $\eta$, as judged by comparing the most pessimistic frequentist risk with that of the Bayesian estimator. It can also be shown that $R(b) \to 1$ as $b \to \infty$. So, as the bound weakens the Bayes and minimax risk both approach 1.

1