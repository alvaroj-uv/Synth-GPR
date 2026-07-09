MEINCKE: LINEAR GPR INVERSION

2717

assume that the radar data $\tilde{s}_o$ are available at $N_\omega$ equidistant frequencies

$$\omega_p = (p-1)\Delta\omega + \omega_{\min} \quad p = 1, \dots, N_\omega \quad (24)$$

where $\Delta\omega = (\omega_{\max} - \omega_{\min}) / (N_\omega - 1)$. With $q(\mathbf{K})$ denoting the lowest integer in the range $1, \dots, N_\omega$ for which $\tilde{s}_o(\mathbf{K}, \omega_{q(\mathbf{K})}) \neq 0$, there are $q(\mathbf{K}) - 1$ values of the radar data $\tilde{s}_o(\mathbf{K}, \omega_p)$ and the filtered data $\tilde{s}_o^f(\mathbf{K}, \omega_p)$ that are zero and $N_{nz} = N_\omega - q(\mathbf{K}) + 1$ values that are nonzero. Second, a simple quadrature rule applied to (23) transforms the filtering step (20) into the following matrix equation:

$$\tilde{s}_o(\mathbf{K}, \omega_p) = \sum_{p'=q(\mathbf{K})}^{N_\omega} R_{pp'}(\mathbf{K}) \tilde{s}_o^f(\mathbf{K}, \omega_{p'}) \quad (25)$$

where $p = q(\mathbf{K}), \dots, N_\omega, |\mathbf{K}| \leq K_m$ and $\delta_{pp'}$ denotes Kronecker's delta. Moreover

$$R_{pp'}(\mathbf{K}) = (2\pi)^2 i \omega_p D(\mathbf{K}, z_r, \omega_p) W_{pp'}(\mathbf{K}) + \delta_{pp'} \lambda^2 \quad (26)$$

and

$$W_{pp'}(\mathbf{K}) = \frac{\Delta\omega D^*(\mathbf{K}, z_r, \omega_{p'}) \omega_{p'}}{\sqrt{4k_1^2(\omega_p) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega_{p'}) - |\mathbf{K}|^2}}. \quad (27)$$

This completes the derivation of the inversion scheme. In summary, to obtain the image of the buried object one must first filter the radar data using (25) and subsequently backpropagate the filtered data employing (21).

B. Incorporating a Priori Information

Due to the fact that the buried object can be illuminated from one side only in a GPR survey, the obtained radar data does not contain enough information to estimate the correct value of $\Delta\epsilon_1$ using a linear inversion scheme. However, if a priori information about the object can be incorporated in the inversion scheme, a better estimate of $\Delta\epsilon_1$ can be obtained. This is the case in [4], in which the fact that the object function is real is used as a priori information. Unfortunately, the same procedure cannot be applied in an exact manner in this work because it requires that the soil is lossless. However, the procedure can be used approximately. To see this, consider the forward model (14). This model can be written as

$$\tilde{s}_o(\mathbf{K}, z_r, \omega) = -i\omega D(\mathbf{K}, z_r, \omega) \cdot \widetilde{\Delta\epsilon_1} \left( \mathbf{K} + \tilde{\mathbf{Z}} \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \right). \quad (28)$$

When there is no loss and $|\mathbf{K}| < 2k_1(\omega)$ the argument of $\widetilde{\Delta\epsilon_1}$ is real and thus, the forward model (28) can be inverted using the inverse spatial FT $\mathcal{F}^{-1}$. This is indeed the procedure of [4]. Hence, $\Delta\epsilon_1 = \mathcal{F}^{-1}(\widetilde{\Delta\epsilon_1})$. From (28), it is seen that the radar data only provides information about $\widetilde{\Delta\epsilon_1}(\mathbf{k})$ in the upper half space $k_z > 0$. To obtain the information in the lower half space, the relation $\widetilde{\Delta\epsilon_1}(\mathbf{k}) = \widetilde{\Delta\epsilon_1}^*(-\mathbf{k})$ is used, which holds for real functions $\Delta\epsilon_1$ and for real arguments $\mathbf{k}$. Using this a priori information yields

$$\begin{aligned} \Delta\epsilon_1 &= 2\text{Re} \left[ \mathcal{F}_{\text{up}}^{-1} \left( \widetilde{\Delta\epsilon_1} \right) \right] \\ &= 2\text{Re} \left[ \mathcal{F}_{\text{up}}^{-1} \left( \frac{\tilde{s}_o(\mathbf{K}, z_r, \omega)}{-i\omega D(\mathbf{K}, z_r, \omega)} \right) \right] \end{aligned} \quad (29)$$

where $\mathcal{F}_{\text{up}}^{-1}$ denotes the inverse FT with integration in the upper half space only. When loss is present in the soil the argument of $\widetilde{\Delta\epsilon_1}$ in (28) is no longer real, and the inverse FT cannot be used to accurately invert the forward model. The artifacts in Fig. 5 of [4] are the result of such an invalid application of the inverse FT. To get rid of the artifacts, the pseudo-inverse operator of this paper must be applied. Unfortunately, it is difficult to incorporate a priori information exactly using the pseudo-inverse operator. However, since the pseudo-inverse operator reduces to the inverse FT when there is no loss (see Section III-D) it is suggested to incorporate a priori information in the same way as done in (29). Hence, instead of using (21), it is suggested to use

$$\Delta\epsilon_1 = 2\text{Re} \left( \mathcal{L}^\dagger \tilde{s}_o^f \right) \quad (30)$$

to obtain a more accurate estimate of $\Delta\epsilon_1$.

C. Discussion

Although there exist many other and more accurate discretization methods the simple procedure outlined above turns out to give surprisingly good results even for low values of $N_\omega$, see the numerical example in Section IV. A more accurate method of moments approach with pulse expansion functions and point matching has been investigated [12]. The image quality of this method is not significantly better than that obtained from the simple quadrature rule of the present paper. The simple quadrature rule is preferred here due to its simplicity.

The FT $\tilde{s}_o(\mathbf{K}, z_r, \omega)$ in (9) is most conveniently calculated using FFTs. Hence, $\tilde{s}_o$ is available at $N_{\mathbf{K}}$ discrete values of $\mathbf{K}$ and for each of these values, (25) constitutes an $N_{nz}$ by $N_{nz}$ square matrix equation, where $N_{nz}$ defined following (24) depends on $\mathbf{K}$. When $|\mathbf{K}| = 0$, $N_{nz}$ is maximum and equals $N_\omega$, whereas $N_{nz}$ takes on the minimum value 1 when $|\mathbf{K}| = K_m$.

The filters $R_{pp'}$ depend on the properties of the GPR, i.e., the frequencies $(\omega_{\min}, \omega_{\max}, \Delta\omega)$, the offset $(\mathbf{r}_\Delta)$, the antennas $(\mathbf{J}_{s_1}, \mathbf{R}(\mathbf{K}, \omega))$ and the distance over the air-soil interface $(z_r)$. They also depend on the electromagnetic properties of the soil $(\epsilon_1, \sigma_1)$. All these quantities are independent of the radar data and $R_{pp'}$ can therefore be calculated in advance before data are to be processed.

There exist many methods for an efficient determination of the optimum regularization parameter $\lambda$, e.g., the generalized cross-validation and L-curve methods [9, Ch. 7]. It is important to note that these methods must be applied to the problem (18). They cannot be applied to the filtering step (20) because it does not satisfy the Picard condition [9, p. 9]. This is explained more carefully in the Appendix of this paper. Future research aims to find an efficient way to determine the optimum $\lambda$ for the special problem (18). Until this goal has been achieved, the regularization parameter $\lambda$ is to be determined by trial and error.

There are several differences between the pseudo-inverse based inversion scheme of this paper and that of [6]. First, the forward model of this paper takes into account the air-soil interface which, as mentioned in the Introduction, is not accounted for in [6]. Second, by using the asymptotic forward model (12) instead of the full model (10) the filters in the filtering step become much easier and faster to calculate. The application of the asymptotic forward model implies, however, that evanescent plane waves in the soil are neglected

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.