6.8 Correlation of Sequences

95

For example, an exponential covariance matrix could be defined by $C_{i,j} = \sigma^2 e^{-\|i-j\|/\ell}$ where $\sigma^2$ is the (in this example) constant variance and $\ell$ is the correlation length. To impose this correlation on an uncorrelated, Gaussian sequence, we do a Cholesky decomposition of the covariance matrix and dot the lower triangular part into the uncorrelated sequence [Par94]. If $A$ is a symmetric matrix, then we can always write

$$A = LL^T,$$

where $L$ is lower triangular [GvL83]. This is called the Cholesky decomposition of the matrix $A$. You can think of the Cholesky decomposition as being somewhat like the square root of the matrix. Now suppose we apply this to the covariance matrix $C = LL^T$. Let $x$ be a mean zero pseudo-random vector whose covariance is the identity. We will use $L$ to transform $x$: $z \equiv Lx$. The covariance of $z$ is given by

$$\text{Cov}(z) = E[zz^T] = E[(Lx)(Lx)^T] = LE[xx^T]L^T = LIL^T = C$$

which is what we wanted.

Here is a simple Scilab code that builds an exponential covariance matrix $C_{i,j} = \sigma^2 e^{-\|i-j\|/l}$ and then returns $n$ pseudo-random samples drawn from a Gaussian process with this covariance (and mean zero).

function [z] = correlatedgaussian(n,s,l)

// returns n samples of an exponentially correlated gaussian process
// with variance s^2 and correlation length l.

// first build the covariance matrix.

C = zeros(n,n);
for i = 1:n
  for j = 1:n
    C(i,j) = s^2 * exp(-abs(i-j)/l);
  end
end

L = chol(C);
x = rand(n,1,'normal');
z = L*x;

We would call this, for example, by:

z = correlatedgaussian(200,1,10);

0