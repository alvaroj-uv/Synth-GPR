Remote Sens. 2024, 16, 4146

18 of 19

clearly indicate that the quadratic Wasserstein distance is a promising choice for mismatch functions in FWI methods.

## 5. Conclusions

This study developed a high-resolution full-waveform inversion method for GPR relative permittivity and conductivity based on the quadratic Wasserstein ($W_2$) metric. Due to the lack of low-frequency components in the data and the limited accuracy of the initial model, cycle skipping can occur. The sensitivity of the $W_2$ distance to low-frequency information enables it to effectively mitigate local minima issues. To implement the proposed method, the Sinkhorn optimization algorithm was used to solve the optimal transport matrix. Additionally, a Softplus function normalization method was introduced to ensure mass conservation and non-negativity assumptions while maintaining good convexity of the objective function. Three numerical examples demonstrate that the $W_2$-based FWI effectively avoids cycle skipping, exhibits strong noise robustness, and has low dependence on the initial model, with significant improvement in conductivity inversion results. Thus, the quadratic Wasserstein distance is a promising choice for the misfit function in dual-parameter FWI methods for GPR data.

**Author Contributions:** K.L. and H.H. conceived the numerical experiments. K.L., Y.W. and H.H. performed the experiments, analyzed the data, and wrote the paper. Y.W. revised the paper. Y.W., Y.Z. and S.Z. gave advice for the numerical simulation and laboratory experiment. All authors have read and agreed to the published version of the manuscript.

**Funding:** This work was supported by the National Natural Science Foundation of China (Grant No. 42025403) and the Institute of Geology and Geophysics, Chinese Academy of Sciences (Grant No. IGGCAS-202102).

**Data Availability Statement:** The data presented in this study are available on request from the corresponding author. The data are not publicly available due to privacy.

**Conflicts of Interest:** The authors declare no conflicts of interest.

## References

1. 1. Irving, J.D.; Knoll, M.D.; Knight, R.J. Improving crosshole radar velocity tomograms: A new approach to incorporating high-angle traveltime data. *Geophysics* **2007**, *72*, J31–J41. [\[CrossRef\]](#)
2. 2. Binley, A.; Winship, P.; Middleton, R.; Pokar, M.; West, J. High-resolution characterization of vadose zone dynamics using cross-borehole radar. *Water Resour. Res.* **2001**, *37*, 2639–2652. [\[CrossRef\]](#)
3. 3. Fisher, E.; McMechan, G.A.; Annan, A.P. Acquisition and processing of wide-aperture ground-penetrating radar data. *Geophys.* **1992**, *57*, 495–504. [\[CrossRef\]](#)
4. 4. Zhong, S.; Wang, Y.; Zheng, Y. Frequency-domain wavefield reconstruction inversion of ground-penetrating radar based on sensitivity analysis. *Geophys. Prospect.* **2023**, *71*, 1655–1672. [\[CrossRef\]](#)
5. 5. Leong, Z.X.; Zhu, T. Direct velocity inversion of ground penetrating radar data using GPRNet. *J. Geophys. Res. Solid Earth* **2021**, *126*, e2020JB021047. [\[CrossRef\]](#)
6. 6. Liu, B.; Ren, Y.; Liu, H.; Xu, H.; Wang, Z.; Cohn, A.G.; Jiang, P. GPRInvNet: Deep learning-based ground-penetrating radar data inversion for tunnel linings. *IEEE Trans. Geosci. Remote Sens.* **2021**, *59*, 8305–8325. [\[CrossRef\]](#)
7. 7. Leeuwen, T.V.; Herrmann, F.J. A penalty method for PDE-constrained optimization in inverse problems. *Inverse Probl.* **2015**, *32*, 015007. [\[CrossRef\]](#)
8. 8. Lavoué, F.; Brossier, R.; Métivier, L.; Garambois, S.; Virieux, J. Two-dimensional permittivity and conductivity imaging by full waveform inversion of multioffset GPR data: A frequency-domain quasi-Newton approach. *Geophys. J. Int.* **2014**, *197*, 248–268. [\[CrossRef\]](#)
9. 9. Plessix, R.E. A review of the adjoint-state method for computing the gradient of a functional with geophysical applications. *Geophys. J. Int.* **2006**, *167*, 495–503. [\[CrossRef\]](#)
10. 10. Liu, D.C.; Nocedal, J. On the limited memory BFGS method for large scale optimization. *Math. Program.* **1989**, *45*, 503–528. [\[CrossRef\]](#)
11. 11. Virieux, J.; Operto, S. An overview of full-waveform inversion in exploration geophysics. *Geophysics* **2009**, *74*, WCC1–WCC26. [\[CrossRef\]](#)
12. 12. Tarantola, A. Inversion of seismic reflection data in the acoustic approximation. *Geophysics* **1984**, *49*, 1259–1266. [\[CrossRef\]](#)
13. 13. Klotzsche, A.; Vereecken, H.; van der Kruk, J. Review of crosshole ground-penetrating radar full-waveform inversion of experimental data: Recent developments, challenges, and pitfalls. *Geophysics* **2019**, *84*, H13–H28. [\[CrossRef\]](#)