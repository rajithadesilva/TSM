# Triangle Scan Method (TSM)

The triangle scan method is a 2-step process which determines the central crop row from a semantic skeleton segmentation of a crop row. The first step (Anchor Scan) and the second step (Line Scan) scan for the topmost (Anchor Point) and the lowermost ($P_{r}$) points of the central crop row respectively. The anchor point $A$ and point $P_{r}$ always lie on the top and bottom edges of the image respectively. Please refer the [TSM documentation](media/tsm.md) for further details.

<figure>
  <img src="media/ROIs.png" alt="Alt Text" width="50%">
  <figcaption>Figure 1: Regions of interest for anchor scan and line scan. Anchor Scan ROI: RED, Line Scan ROI: Green. </figcaption>
</figure>

## Usage
### Prerequisits
1. Install dependencies: [OpenCV, NumPy, SK-Image, Seaborn, Pandas, Matplotlib, Glob, Argparse]
```bash
pip install opencv-python numpy scikit-image seaborn pandas matplotlib glob3 argparse
```
2. Clone the repository.
```bash
git clone https://github.com/Rajitha159/TSM.git
```
3. Copy the RGB image files to "rgb" folder and predicted crop row masks to "mask" folder(all images must be resized to $512 \times 512$).
4. Run the following command to generate crop row masks and save them to "out" folder.
```bash
python triangle_scan_rgb.py
```
5. [Optional] Run the code with parameters in needed. Parameter descriptions are in table below.
Example: 
```bash
python triangle_scan_rgb.py --file_type=".png"
```

### Parameters
| Parameter         | Description                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| `--file_type`     | Specify the file type for image files. Default is `.jpg`.                                     |
| `--A`             | Specify the standard anchor point. Default is 277.                                           |
| `--B`             | Specify the begin point (B) for line scans. Default is 200.                                  |
| `--C`             | Specify the cease point (C) for line scans. Default is 450.                                 |
| `--Amin`          | Specify the anchor scans starting point. Default is 100.                                    |
| `--Amax`          | Specify the anchor scans ending point. Default is 350.                                      |
| `--s`             | Specify the anchor scans ROI (Region of Interest) height. Default is 0.2.                   |
| `--scan_period`   | Specify the scan period for anchor and line scans. Default is 1.                            |
| `--filter_enable` | Enable the complementary filters for scanning in continuous sequential images. Default is `False`. |
| `--anchor_filter` | Specify the complementary filter strength for anchor scans. Default is 0.95.                |
| `--line_filter`   | Specify the complementary filter strength for line scans. Default is 0.95.                  |

## Citation

```
@article{de2022vision,
  title={Vision based Crop Row Navigation under Varying Field Conditions in Arable Fields},
  author={de Silva, Rajitha and Cielniak, Grzegorz and Gao, Junfeng},
  journal={arXiv preprint arXiv:2209.14003},
  year={2022}
}
```

Link to full paper: [Vision based Crop Row Navigation under Varying Field Conditions in Arable Fields](https://arxiv.org/pdf/2209.14003.pdf)
