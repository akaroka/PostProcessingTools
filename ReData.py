from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as pl


class ReData(object):

    def __init__(self, originaldata, datatype, incr, rangepara):
        self.disp_list = originaldata[0]
        self.force_list = originaldata[1]
        self.datatype = datatype
        self.incr = incr
        self.rangepara = rangepara
        self.true_cycin_list = None
        self.true_protocal = None

    @staticmethod
    def ipdata(x_list, y_list, xrange, incr):
        range_lower = xrange[0]
        range_upper = xrange[1]
        if range_lower > range_upper:
            incr = -incr
        f = interp1d(x_list, y_list, fill_value='extrapolate')
        x_list_new = list(np.arange(range_lower, range_upper, incr))
        y_list_new = list(f(x_list_new))
        return [x_list_new, y_list_new]

    @staticmethod
    def modvalue(value, incr):
        modified_value = round(value / incr) * incr
        return modified_value

    @property
    def cycin_list(self):
        """
        :return: index list for the first point of each cycle
        """
        self.true_cycin_list = [0]
        if self.datatype == 'mono':
            self.true_cycin_list.append(len(self.disp_list)-1)
        elif self.datatype == 'cyc_half':
            for i in range(len(self.disp_list) - 1):
                if self.disp_list[i] > 0 >= self.disp_list[i + 1] and i - self.true_cycin_list[-1] > 3:
                    disp_cycle_list = self.disp_list[self.true_cycin_list[-1]:i]
                    max_disp_index = disp_cycle_list.index(max(disp_cycle_list)) + self.true_cycin_list[-1]
                    self.true_cycin_list.append(max_disp_index)
                    self.true_cycin_list.append(i + 1)
        elif self.datatype == 'cyc_full':
            for i in range(len(self.disp_list) - 1):
                if self.disp_list[i] < 0 <= self.disp_list[i + 1] and i - self.true_cycin_list[-1] > 3:
                    disp_cycle_list = self.disp_list[self.true_cycin_list[-1]:i]
                    max_disp_index = disp_cycle_list.index(max(disp_cycle_list)) + self.true_cycin_list[-1]
                    min_disp_index = disp_cycle_list.index(min(disp_cycle_list)) + self.true_cycin_list[-1]
                    self.true_cycin_list.append(max_disp_index)
                    self.true_cycin_list.append(min_disp_index)
                    self.true_cycin_list.append(i + 1)
        return self.true_cycin_list

    @property
    def protocal(self):
        self.true_protocal = []
        if self.datatype == 'mono':
            self.true_protocal += [self.rangepara[0], self.rangepara[1] + self.incr]
        elif self.datatype == 'cyc_half':
            amptitude_list = self.rangepara[0]
            cyctime_list = self.rangepara[1]
            self.true_protocal.append(0)
            for amptitude, cyctime in zip(amptitude_list, cyctime_list):
                protocal_cycle = [self.modvalue(amptitude, self.incr), 0] * cyctime
                self.true_protocal += protocal_cycle
        elif self.datatype == 'cyc_full':
            amptitude_list = self.rangepara[0]
            cyctime_list = self.rangepara[1]
            self.true_protocal.append(0)
            for amptitude, cyctime in zip(amptitude_list, cyctime_list):
                protocal_cycle = [self.modvalue(amptitude, self.incr), -self.modvalue(amptitude, self.incr), 0] * cyctime
                self.true_protocal += protocal_cycle
        return self.true_protocal

    def stadata(self):
        """
        :return:
        """
        disp_list_new = []
        force_list_new = []
        for no, index in enumerate(self.cycin_list):
            disp = self.disp_list[self.cycin_list[no]:self.cycin_list[no + 1]]
            force = self.force_list[self.cycin_list[no]:self.cycin_list[no + 1]]
            result = self.ipdata(disp, force, [self.protocal[no], self.protocal[no + 1]], self.incr)
            disp_new = result[0]
            force_new = result[1]
            disp_list_new = disp_list_new + disp_new
            force_list_new = force_list_new + force_new
            if no == len(self.cycin_list) - 2:
                break
        return [disp_list_new, force_list_new]


if __name__ == '__main__':
    datatype1 = 'cyc_full'
    incr1 = 0.1
    # (1)for cyclic protocol
    amptitude_list1 = [1.50, 2.25, 1.69, 3.00, 2.25, 6.00, 4.50, 9.00, 6.75, 12.00, 9.00, 21.00, 15.75, 30.00, 22.50, 42.00, 31.50, 54.00, 40.50]
    cyctime_list1 = [6, 1, 6, 1, 6, 1, 3, 1, 3, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
    rangepara1 = [amptitude_list1, cyctime_list1]
    # (2)for monotonic protocol
    # rangepara1 = [0, 50]

    filename = 'data.txt'
    disp_list1 = list(np.loadtxt(filename, delimiter='	', usecols=(0,), dtype=float))
    force_list1 = list(np.loadtxt(filename, delimiter='	', usecols=(1,), dtype=float))
    redata1 = ReData([disp_list1, force_list1], datatype1, incr1, rangepara1)
    result1 = redata1.stadata()
    # print(origindata1.cycin_list)
    # print(origindata1.protocal)
    #
    with open("result.txt", "w+") as fw:  # 打开文件
        for disp1, force1 in zip(result1[0], result1[1]):
            fw.write("%.2f %.5f\n" % (disp1, force1))  # 读取文件

    pl.plot(disp_list1, force_list1, 'b')
    pl.plot(result1[0], result1[1], 'r')
    pl.show()
