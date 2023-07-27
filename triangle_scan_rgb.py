import cv2
import numpy as np
from skimage.draw import line
import seaborn
import pandas
import matplotlib.pyplot as plt
import math

#global_selector = 0
#anchors = deque([277]*40, maxlen=40)

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
    def __init__(self, image, rgb, imnum, out_path="./out/", img_type=".jpg"):
        self.out_path = out_path
        self.image = image       #                            ←――― Width of Image ――→
        self.imnum = imnum       #                            |⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺Ⓐ⎺⎺⎺⎺⎺⎺⎺⎺⎺|↑
        self.img_type = img_type #                            |          / \        ||
        self.A = [0, 277] #Anchor Point (y,x) from top left   |         /   \       |Height of Image 
        self.B = [511, 200] #Begin Point (y,x) from top left  |        /     \      ||
        self.C = [511, 450] #Cease Point (y,x) from top left  |_______Ⓑ______Ⓒ_____|↓
        self.ScanPeriod = 1 #Periodicity of Pixel Scan through Ⓑ to Ⓒ 
        self.rgb = rgb
        self.scale = 0.2# Percentage of the image used for anchor scans (from top)
        self.first=True if (imnum==1) else False
        self.a_range = [100, 350]#Range for anchor scans

    def anchor_scan(self, step):
        self.ascans = [0]*self.a_range[0]#For anchor scans
        for i in range(self.a_range[0],self.a_range[1]):
            rows, columns = line(0+(step*int(((self.image.shape[0]-1)*self.scale))), i, ((step+1)*int(((self.image.shape[0]-1)*self.scale))), i)
            single_count = np.sum(I[rows, columns])
            self.ascans.append(single_count)
        #self.A[1] = int((0.95*float(global_anchor)) + (0.05*float(np.argmax(self.ascans)))) # anchor update with complementary filter
        self.A[1] = int(np.argmax(self.ascans))#Uncomment for non-filtered image specific anchor
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
        outpathfullplot = self.out_path + f"{self.imnum+2000}" + self.img_type
        plt.savefig(outpathfullplot)
        plt.clf()

    def scan(self):
        #Preprocess Image
        I = self.image
        I = cv2.cvtColor(I,cv2.COLOR_BGR2GRAY)
        ret,I = cv2.threshold(I, 200, 1, 0)

        #Anchor Scans
        self.anchor_scan(0)
        #anchors.appendleft(np.argmax(self.ascans))

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
            single_count = np.sum(I[rows, columns])
            self.scans.append(single_count)
        #print(np.max(self.scans))
      
        self.image = cv2.addWeighted(self.rgb,1.0,self.image,0.45,0)
        #self.image = cv2.addWeighted(self.image,1.0,self.rgb,0.3,0)

        selector = int(np.argmax(self.scans))
        #print(self.A[1]-selector)
 
        #Smoothened out line movement between frames.  Uncomment last line to use unsmoothened operation
        #global global_selector
        #global_selector = int((0.95*float(global_selector)) + (0.05*float(selector))) if not self.first else selector # Complementary filter to smooth out sudden line jumps
        #global_selector = selector
        
        cv2.line(self.image, (self.A[1],self.A[0]), (selector, (self.image.shape[0]-1)), (0, 0, 255), thickness=2)
        #self.plot()

        outpathfull = self.out_path + f"{self.imnum:03}" + self.img_type     
        cv2.imwrite(outpathfull,self.image)
        #print(math.degrees(math.atan(abs(self.A[1]-selector)/self.C[0])))
        #print(selector)
        return 0

if __name__ == "__main__":

    for x in range(0,500):
        name=str(x)+".jpg"
        n="./img/"+name
        m="./src/"+name

        I = cv2.imread(n)
        B = cv2.imread(m)

        try:
            myscan = LineScan(I,B,x)
            out = myscan.scan()
            print(str(x))
            #print("$$$$$$$$$$$")
            del myscan
        except:
            pass



