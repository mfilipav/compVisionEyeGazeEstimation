# GazeNet -- Eye Gaze Estimation
Project for Machine Perception 2019 Spring semester by Modestas Filipavicius
Link to paper: https://www.overleaf.com/read/tzvrpffsdrxx

![dataset overview](https://github.com/mfilipav/compVisionEyeGazeEstimation/blob/master/figures/hiliges_fig.jpg)
*Comparison of model predictive performance on 4 canonical datasets. Adapted from: Park 2018, Learning to Find Eye Region Landmarks for Remote Gaze Estimation in Unconstrained Settings*

# Project Introduction
Conventional feature-based and model-based gaze estimation methods have proven to perform well in settings with controlled illumination and specialized cameras. In unconstrained real-world settings, however, such methods are surpassed by recent appearance-based methods due to difficulties in modeling factors such as illuminationchanges and other visual artifacts.

Here presented is a novel learning based method for eye region landmark localization that enables conventional methods to be competitive to latest appearance-based methods. Despite having been trained exclusively on synthetic data, our method exceeds the state of the art for iris localization and eye shape registration on real-world imagery. We then use the detected landmarks as input to iterative model-fitting and lightweight learning-based gaze estimation methods. 

This model outperforms existing model-fitting and appearance-based methods in the context of person-independent and personalized gaze estimation 
