# Triangle Scan Method (TSM)

The triangle scan method is a 2-step process which determines the central crop row from the U-Net prediction. The first step (Anchor Scan) and the second step (Line Scan) scan for the topmost (Anchor Point) and the lowermost ($P_{r}$) points of the central crop row respectively. The anchor point $A$ and point $P_{r}$ always lie on the top and bottom edges of the image respectively. These two steps are explained below.

<figure>
  <img src="media/ROIs.png" alt="Alt Text">
  <figcaption>Figure 1: Regions of interest for anchor scan and line scan. Anchor Scan ROI: RED, Line Scan ROI: Green. </figcaption>
</figure>

## Anchor Scans

Anchor scans stage scans a rectangular region of interest (ROI) of the predicted crop row mask as indicated in red in Figure 1. The width of the rectangular ROI is the same as the width of the image while the height of the rectangular ROI is defined by $h$ such that $h=sH$. The height of the input image is $H$ and $s$ is a scaling factor between $0$ and $1$. By default $s$ was set to $0.2$. Equation 1 describes the scanning process for $A$. $I$ is the U-Net prediction and $X$ represents horizontal coordinates within a predefined range in the rectangular ROI. The predefined range (0.2H to 0.7H) for $X$ was experimentally determined by observing the usual anchor point occurrence in the dataset. The anchor point is only validated if the scanner parameter: $\left( \sum_{y=0 → y=h} I(X,y) \right)$ meets an experimentally predetermined threshold value. The ROI is shifted down by a distance of $h$ (maximum up to 2 times) if the detected anchor point is invalid. This shifting down helps to identify the $A$ when the robot reaches the end of a crop row. An in-depth analysis for the $s$ parameter, range for $X$ and validation threshold for scanner parameter are presented in detail in Section \ref{sec:ascansroi}.

$A = argmax \left( \sum_{y=0 → y=h} I(X,y) \right)   (1)$

<figure>
  <img src="media/ascans.png" alt="Alt Text">
  <figcaption>Figure 2: Anchor scans distribution. </figcaption>
</figure>

## Line Scans

A triangular ROI is defined in the line scans stage with points A, B (Begin Point) and C (Cease Point) as shown in Figure 1. Equation 2 describes the scanning process for $P_{r}$ by searching for an instance of a variable point $P$ on $BC$ line which yields the highest pixel sum along $AP$ line.

$P_{r} = argmax \Biggl[ \sum{I_{xy}=A}^{P} I(x,y) \Biggr]_{P=B}^{P=C}    (2)$

The definition of points $B$ and $C$ are dependent on the crop height, camera mounting height and camera mounting angle. The calibration procedure outlined in Section \ref{sec:calib} allows to set the $B,C$ points at bottom left and bottom right corners of the image frame respectively. However, the $B,C$ points could be tightly defined based on additional observations relevant to a given scenario. For example, a visual servoing controller will always attempt to align the central crop row to a vertical position within the image frame. A maximum possible crop row orientation limit could be established as a prior with sufficient testing of the visual servoing setup. Such priors could be used to limit the relative offset of $B,C$ points from point $A$, leading to a lower computational time for scanning procedure given in Equation 2. Points $B$ and $C$ will always lie on the lowermost edge of the image.

<figure>
  <img src="media/scans.png" alt="Alt Text">
  <figcaption>Figure 3: Line scans distribution. </figcaption>
</figure>
