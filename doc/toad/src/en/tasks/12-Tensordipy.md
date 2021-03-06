# Tensordipy
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensordipy                                            |
|**Goal**        | Reconstruction of the tensor using dipy               |
|**Config file** | `fitMethod` <br> `ignore`                                              |
|**Time**        | About 30 minutes                                      |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3) |

#

## Goal

The tensordipy step reconstructs tensors from diffusion-weighted images and extracts tensor metrics such as fractional anisotropy (FA) or mean diffusivity (MD).
This step uses the `fit` command line from dipy [ref: <a href="http://nipy.org/dipy/examples_built/reconst_dti.html#example-reconst-dti" target="_blank">dipy</a>]

## Requirements

- Diffusion-weighted images (dwi)
- Diffusion-weighted gradient scheme (bvec and bval)
- Mask of the brain (optional)

## Config file

Method to reconstruct tensor: WLS (weighted least square), LS (ordinary least square), NLLS (Non linear least square), RT or RESTORE (Restore)

- `fitMethod: WLS`

Ignore tensordipy task: **not recommended**

- `ignore: False`

## Implementation

### 1- Reconstruction of the tensor

<a href="http://nipy.org/dipy/examples_built/reconst_dti.html#example-reconst-dti" target="_blank">Dipy reconst_dti</a>

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- Production of an image (png) for each metric (fa. ad, rd and md)

## References

### Associated documentation

<a href="http://nipy.org/dipy/examples_built/reconst_dti.html#example-reconst-dti" target="_blank">Dipy reconst_dti</a>

### Articles

- Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. *Biophysical journal, 66(1)*, 259-267. [<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1275686&tool=pmcentrez&rendertype=abstract" target="_blank">Link to the article</a>] 

- [WLS, OLS] Chung, S., Lu, Y., & Henry, R. G. (2006). Comparison of bootstrap approaches for estimation of uncertainties of DTI parameters. NeuroImage, 33(2), 531–541. doi:10.1016/j.neuroimage.2006.07.001. [<a href="http://www.sciencedirect.com/science/article/pii/S1053811906007403" target="_blank">Link to the article</a>]

- [NLLS, RE] Chang, L.-C., Jones, D. K., & Pierpaoli, C. (2005). RESTORE: robust estimation of tensors by outlier rejection. Magnetic Resonance in Medicine, 53(5), 1088–95. doi:10.1002/mrm.20426 [<a href="http://onlinelibrary.wiley.com/doi/10.1002/mrm.20426/epdf" target="_blank">Link to the article</a>] 

