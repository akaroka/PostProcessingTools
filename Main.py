import matplotlib.pyplot as pl
import DataAnalysis as Da
import numpy as np

filename = "data.txt"
disp_list1 = list(np.loadtxt(filename, delimiter='	', usecols=(0,), skiprows=1, dtype=float))
force_list1 = list(np.loadtxt(filename, delimiter='	', usecols=(1,), skiprows=1, dtype=float))
data1 = Da.CyclicData(disp_list1, force_list1)
result1 = data1.backbone

with open("result.txt", "w+") as fw:  # 打开文件
    for disp1, force1 in zip(result1[0], result1[1]):
        fw.write("%.2f %.5f\n" % (disp1, force1))  # 读取文件

pl.plot(disp_list1, force_list1, 'b')
pl.plot(result1[0], result1[1], 'r')
pl.show()
