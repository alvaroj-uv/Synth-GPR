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