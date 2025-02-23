from osgeo import gdal, gdalconst
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import SimpleModel.StatisticTyphoon as typ
import SimpleModel.ProbabilityField as pf

class ModelMain(object):
    def __init__(self, GPVfile, position):
        if not (22.4 < float(position[0]) and float(position[0]) < 47.6 and 120 < float(position[1]) and float(position[1]) < 150):
            exit()

        #self.__loadGPV__(GPVfile)
        self.position = position

    def processing(self):
        self.__getStatisticTyphoon__()
        self.__getProbabilityField__()
        print('Finish Processing')

    def plotGraph(self):        
        fig = plt.figure()
        
        X = np.arange(120, 150.1, 0.1)
        Y = np.arange(47.6, 22.3, -0.1)
        values = np.zeros([len(Y), len(X)])
        full = 0

        for row in range(len(Y)):
            for colum in range(len(X)):
                values[row, colum] = self.field.calc(Y[row], X[colum])
                full += values[row, colum]
        print(full)

        plt.imshow(values, cmap = 'Greens')
        plt.xticks([0, len(X) / 2, len(X) - 1], [120, 120 + 0.1 * ((len(X) - 1) / 2), 150])
        plt.yticks([0, len(Y) / 2, len(Y) - 1], [47.6, 47.6 - 0.1 * ((len(X) - 1) / 2), 22.3])
        plt.show()

        
    def __getProbabilityField__(self):
        ave, var = self.__getMoveStat__()
        ave = [ave[0] + self.position[0], ave[1] + self.position[1]]
        self.field = pf.ProbabilityField(ave, var)


    def __getStatisticTyphoon__(self):
        fp = open('./typhoon/TyphoonInfo.json', 'r')
        jsondata = json.load(fp)

        self.statisticTyphoons = []
        del(jsondata['comment'])
        for index, info in jsondata.items():
            print(info)
            distance = self.__GlobalDistance__(self.position, [info['latitude'], info['longitude']])
            print(distance)
            if distance > 300: # 中心が半径300kmの円の外側だったら飛ばす
                continue
            
            self.statisticTyphoons.append( typ.StatisticTyphoon(info) )

        print('Sample : ' + str(len(self.statisticTyphoons)))


    def __getMoveStat__(self):
        lat = []
        long = []

        for sample in self.statisticTyphoons:
            move = sample.getMovement()
            lat.append(move[0])
            long.append(move[1])

        ave = [ np.average(lat), np.average(long) ]
        var = [ np.var(lat), np.var(long) ]

        return ave, var


    def __loadGPV__(self, file):
        # register drivers
        gdal.AllRegister()
        # create a data set object
        dataset = gdal.Open(file, gdalconst.GA_ReadOnly)
        
        band_num = 1 # 過去データのバンド番号 + 1

        # 読み込むラスターの情報
        bandInfo_dict = gdal.Info(dataset, format='json')
        band = dataset.GetRasterBand(band_num)

        # read the band as matrix
        data_matrix = band.ReadAsArray()

    def __GlobalDistance__(self, pos1, pos2):
        R = 6378.1370
        
        lat1 = math.radians(pos1[0])
        long1 = math.radians(pos1[1])
        lat2 = math.radians(pos2[0])
        long2 = math.radians(pos2[1])

        averageLat = (lat1 - lat2) / 2
        averageLong = (long1 - long2) / 2

        return R * 2 * math.asin( math.sqrt(math.pow( math.sin(averageLat), 2) + math.cos(lat1) * math.cos(lat2) * math.pow( math.sin(averageLong), 2)))