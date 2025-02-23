#import numpy as np
import math
import numpy as np

class ProbabilityField():
    def __init__(self, ave, var):
        self.lat_ave = ave[0] # 平均
        self.lat_var = var[0] # 分散
        self.long_ave = ave[1]
        self.long_var = var[1]

    def calc(self, lat, long):
        K = 0
        try:
            K =  1.0 / ( 2.0 * 3.141592 * math.sqrt(self.lat_var * self.long_var))
        except:
            K =  1.0 / ( 2.0 * 3.1415921)
        latv = (lat - self.lat_ave) ** 2
        longv = (long - self.long_ave) ** 2
        value = K * math.exp(-1.0 / 2.0 * (latv / self.lat_var + longv / self.long_var))
        return value #if value > 0.001 else 0

    def getAverage(self):
        return [self.lat_ave, self.long_ave]

    def getVariance(self):
        return [self.lat_var, self.long_var]

    def getProbableRadius(self, probability):
        r = 0
        d = 0.05
        val = 0.0
        while(val * 4 < probability):
            val = 0.0
            r += d
            for x in np.arange(0, r, d):
                for y in np.arange(0, np.sqrt(r**2 - x**2), d):
                    val += self.calc(self.lat_ave + y, self.long_ave + x) * d * d
                
            print(val * 4)
        print(r)
        return r