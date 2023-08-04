import cv2
import numpy as np
from skimage.draw import line
import seaborn
import pandas
import matplotlib.pyplot as plt
import math
import glob
import argparse
import os
import csv

global_selector = 0
global_anchor = 0

class SaturatedInteger(object):
    """Emulates an integer, but with a built-in minimum and maximum."""

    def __init__(self, min_, max_, value=None):
        self.min = min_
        self.max = max_
        self.value = min_ if value is None else value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        self._value = min(self.max, max(self.min, new_val))

    @staticmethod
    def _other_val(other):
        """Get the value from the other object."""
        if hasattr(other, 'value'):
            return other.value
        return other

    def __add__(self, other):
        new_val = self.value + self._other_val(other)
        return SaturatedInteger(self.min, self.max, new_val)

    __radd__ = __add__

    def __eq__(self, other):
        return self.value == self._other_val(other)

class LineScan(object):
    def __init__(self, mask_image, rgb_image, A, B, C, Amax, Amin, s, scan_period, imname, img_type, is_first, filter_enable, anchor_filter, line_filter, out_path="./out/", plot_path="./plots/"):
        self.out_path = out_path
        self.plot_path = plot_path
        self.filter = filter_enable
        self.anchor_filter = anchor_filter # Filter Strength for complementary filter on anchor scans
        self.line_filter = line_filter # Filter Strength for complementary filter on line scans

        self.image = mask_image  #                            ←――― Width of Image ――→
        self.imname = imname     #                            |⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺Ⓐ⎺⎺⎺⎺⎺⎺⎺⎺⎺|↑
        self.img_type = img_type #                            |          / \        ||
        self.A = [0, A]   #Anchor Point (y,x) from top left   |         /   \       |Height of Image 
        self.B = [511, B]   #Begin Point (y,x) from top left  |        /     \      ||
        self.C = [511, C]   #Cease Point (y,x) from top left  |_______Ⓑ______Ⓒ_____|↓
        self.ScanPeriod = scan_period #Periodicity of Pixel Scan through Ⓑ to Ⓒ 
        self.rgb = rgb_image
        self.scale = s# Percentage of the image used for anchor scans (from top)
        self.first=is_first
        self.a_range = [Amin, Amax]#Range for anchor scans

    def anchor_scan(self, step):
        global global_anchor
        self.ascans = [0]*self.a_range[0]#For anchor scans
        for i in range(self.a_range[0],self.a_range[1]):
            rows, columns = line(0+(step*int(((self.image.shape[0]-1)*self.scale))), i, ((step+1)*int(((self.image.shape[0]-1)*self.scale))), i)
            single_count = np.sum(self.I[rows, columns])
            self.ascans.append(single_count)

        if self.filter:
            self.A[1] = int((self.anchor_filter*float(global_anchor)) + ((1.0-self.anchor_filter)*float(np.argmax(self.ascans)))) if not self.first else self.A[1] # anchor update with complementary filter
            global_anchor = self.A[1]
        else:
            self.A[1] = int(np.argmax(self.ascans)) # non-filtered image specific anchor
        self.B[1] = SaturatedInteger(200,450,self.A[1]-100).value
        self.C[1] = SaturatedInteger(200,450,self.A[1]+100).value
 
    def plot(self):
        seaborn.set(font_scale = 30)
        seaborn.set(rc={'axes.facecolor':'white'})
        res = seaborn.lineplot(color='b', data=(self.scans/np.amax(self.scans)), lw=1)
        res = seaborn.lineplot(color='r', data=(self.ascans/np.amax(self.ascans)), lw=1)
        res.set_xlabel("Coordinate", fontsize = 15)
        res.set_ylabel("Endpoint Scan", fontsize = 15)
        #plt.axhline(y=0.25, color='r', linestyle='-', lw=3)
        #plt.axvline(x=450, color='b', linestyle='-', lw=3)
        #plt.axvline(x=200, color='b', linestyle='-', lw=3)
        plt.legend(labels=["Pr Scans","Anchor Scans"], fontsize=10)
        #plt.show()
        outpathfullplot = self.plot_path + self.imname
        plt.savefig(outpathfullplot)
        plt.clf()

    def scan(self):
        #Preprocess Image
        self.I = self.image.copy()
        self.I = cv2.cvtColor(self.I,cv2.COLOR_BGR2GRAY)
        ret,self.I = cv2.threshold(self.I, 200, 1, 0)

        #Anchor Scans
        self.anchor_scan(0)

        if np.max(self.ascans) < 30000:#If anchor scan strength is below thresold, scan next stage
            self.anchor_scan(1)
            #print("Step 1")
        if np.max(self.ascans) < 30000:#If anchor scan strength is below thresold, scan next stage 
            self.anchor_scan(2)
            #print("Step 2")
        if np.max(self.ascans) < 30000:#If anchor scan strength is below thresold, reset anchor point
            self.A[1] = 277
            #print("Reset")

        #Primary Scans
        self.scans = [0] * self.B[1] #Create a zero list to fill image origin to Ⓑ
        for i in range(self.B[1],self.C[1],self.ScanPeriod):
            rows, columns = line(self.A[0], self.A[1], (self.image.shape[0]-1), i)
            single_count = np.sum(self.I[rows, columns])
            self.scans.append(single_count)
        #print(np.max(self.scans))
      
        self.image = cv2.addWeighted(self.rgb,1.0,self.image,0.45,0)

        selector = int(np.argmax(self.scans))
 
        #Filter Implementation for line scans filter
        global global_selector
        if self.filter:
            global_selector = int((self.line_filter*float(global_selector)) + ((1.0-self.line_filter)*float(selector))) if not self.first else selector # Complementary filter to smooth out sudden line jumps
        else:
            global_selector = selector
        
        cv2.line(self.image, (self.A[1],self.A[0]), (global_selector, (self.image.shape[0]-1)), (0, 0, 255), thickness=2)
        self.plot()

        outpathfull = os.path.join(self.out_path, self.imname)  
        cv2.imwrite(outpathfull,self.image)
        #print(math.degrees(math.atan(abs(self.A[1]-global_selector)/self.C[0])))
        #print(global_selector)
        return (self.imname, math.degrees(math.atan(abs(self.A[1]-global_selector)/self.C[0])), (global_selector-(self.image.shape[0]/2)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files in a folder.")
    parser.add_argument("--file_type", help="Specify the file type (default: .jpg)", default=".jpg")
    parser.add_argument("--A", help="Specify the standard anchor point (default: 277)", default=277)
    parser.add_argument("--B", help="Specify the begin point (B) for line scans (default: 200)", default=200)
    parser.add_argument("--C", help="Specify the cease point (C) for line scans (default: 450)", default=450)
    parser.add_argument("--Amin", help="Specify the anchor scans starting point (default: 100)", default=100)
    parser.add_argument("--Amax", help="Specify the anchor scans ending point (default: 350)", default=350)
    parser.add_argument("--s", help="Specify the anchor scans ROI height (default: 0.2)", default=0.2)
    parser.add_argument("--scan_period", help="Specify the scan period for anchor and line scans (default: 1)", default=1)
    parser.add_argument("--filter_enable", help="Enable the complementary filters for scanning in continuous sequential images (default: False)", default=False)
    parser.add_argument("--anchor_filter", help="Specify the complementary filter strength for anchor scans (default: 0.95)", default=0.95)
    parser.add_argument("--line_filter", help="Specify the complementary filter strength for line scans (default: 0.95)", default=0.95)
    args = parser.parse_args()

    csv_file_path = "crop_row_detection_data.csv" # CSV file path
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "angular_error", "linear_error"])  # Write header

    rgbs = glob.glob(os.path.join("./rgb/", f'*{args.file_type}'))
    masks = glob.glob(os.path.join("./mask/", f'*{args.file_type}'))

    for i, (rgb,mask) in enumerate(zip(rgbs,masks)):
        mask_image = cv2.imread(mask)
        rgb_image = cv2.imread(rgb)
        imname = os.path.basename(rgb)
        is_first = True if i == 0 else False

        try:
            myscan = LineScan(mask_image, rgb_image, args.A, args.B, args.C, args.Amax, args.Amin, args.s, args.scan_period, imname, args.file_type, is_first, args.filter_enable, args.anchor_filter, args.line_filter)
            errors = myscan.scan()
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([errors])  # Write data rows
            print(imname)
            del myscan
        except:
            pass
