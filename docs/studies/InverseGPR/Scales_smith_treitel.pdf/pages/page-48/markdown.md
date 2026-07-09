# Chapter 4

## A Little Linear Algebra

**Linear algebra background** The parts of this chapter dealing with linear algebra follow the outstanding book by Strang [Str88] closely. If this summary is too condensed, you would be well advised to spend some time working your way through Strang's book. One difference to note however is that Strang's matrices are $m \times n$, whereas ours are $n \times m$. This is not a big deal, but it can be confusing. We'll stick with $n \times m$ because that is common in geophysics and later we will see that $m$ is the number of *model* parameters in an inverse calculation.

### 4.1 Linear Vector Spaces

The only kind of mathematical spaces we will deal with in this course are linear vector spaces. You are already well familiar with concrete examples of such spaces, at least in the geometrical setting of vectors in three-dimensional space. We can add any two, say, force vectors and get another force vector. We can scale any such vector by a numerical quantity and still have a legitimate vector. However, in this course we will use vectors to encapsulate discrete information about models and data. If we record one seismic trace, one second in length at a sample rate of 1000 samples per second, and let each sample be defined by one byte, then we can put these 1000 bytes of information in a 1000-tuple

$$(s_1, s_2, s_3, \cdots, s_{1000}) \tag{4.1}$$

where $s_i$ is the i-th sample, and treat it just as we would a 3-component physical vector. That is, we can add any two such vectors together, scale them, and so on. When we 'stack' seismic traces, we're just adding these n-dimensional vectors component by component, say trace $s$ plus trace $t$,

$$s + t = (s_1 + t_1, s_2 + t_2, s_3 + t_3, \cdots, s_{1000} + t_{1000}). \tag{4.2}$$

0