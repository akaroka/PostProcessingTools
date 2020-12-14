import numpy as np
from scipy import interpolate
from scipy import integrate


class CyclicData(object):

    def __init__(self, disp_list, force_list, half=None):
        """
        :param disp_list: displacement list
        :param force_list: force list
        :param half: if the specimen were only tested with positive displacements
        """
        self.disp_list = disp_list
        self.force_list = force_list
        self.half = half
        self.true_backbone = None
        self.true_cycleNo = None

    def cycin(self):
        """
        :return: index list for the first point of each cycle
        """
        cycin_list = [0]
        if self.half:
            for i in range(len(self.disp_list) - 1):
                if self.disp_list[i] > 0 >= self.disp_list[i + 1] and i - cycin_list[-1] > 3:
                    cycin_list.append(i + 1)
        else:
            for i in range(len(self.disp_list) - 1):
                if self.disp_list[i] < 0 <= self.disp_list[i + 1] and i - cycin_list[-1] > 3:
                    cycin_list.append(i + 1)
        return cycin_list

    @property
    def cycle_no(self):
        """
        :return: cycle number
        """
        cycin_list = self.cycin()
        self.true_cycle_no = len(cycin_list) - 1
        return self.true_cycle_no

    def data_cycle(self, cycle):
        """
        :return: [disp_list,force_list] in ith cycle
        """
        cycin_list = self.cycin()
        begin = cycin_list[cycle-1]
        end = cycin_list[cycle]
        disp_list_cycle = self.disp_list[begin:end]
        force_list_cycle = self.force_list[begin:end]
        return [disp_list_cycle, force_list_cycle]

    @property
    def backbone(self):
        """
        :return: backbone curve, in form of [disp_list,force_list]
        """
        backbonedisp_list = [0]
        backboneforce_list = [0]
        maxdisp_hist = 0
        mindisp_hist = 0
        for cycle in range(1, self.cycle_no+1):
            cycledisp_list = self.data_cycle(cycle)[0]
            cycleforce_list = self.data_cycle(cycle)[1]
            for cycledisp, cycleforce in zip(cycledisp_list, cycleforce_list):
                # add point corresponding to max force in this cycle
                if cycleforce == max(cycleforce_list) and cycledisp > maxdisp_hist:
                    maxdisp_hist = cycledisp
                    backboneforce_list.append(cycleforce)
                    backbonedisp_list.append(cycledisp)
                # add point corresponding to min force in this cycle
                if cycleforce == min(cycleforce_list) and cycledisp < mindisp_hist:
                    mindisp_hist = cycledisp
                    backboneforce_list.insert(0, cycleforce)
                    backbonedisp_list.insert(0, cycledisp)
        self.true_backbone = [backbonedisp_list, backboneforce_list]
        return self.true_backbone

    def energy(self, cumulative=None):
        """
        :param cumulative: decide whether the cumulative energy is considered
        :return: Energy dissipated in each cycle (or Energy cumulated for each cycle), in form of [cycle_list,energy_list]
        """
        cycle_list = list(range(self.cycle_no+1))
        energy_list = [0]
        for cycle in range(1, self.cycle_no+1):
            cycledisp_list = self.data_cycle(cycle)[0]
            cycleforce_list = self.data_cycle(cycle)[1]
            energy = integrate.trapz(cycleforce_list, cycledisp_list)
            if cumulative:
                energy_list.append(energy + energy_list[-1])
            else:
                energy_list.append(energy)
        return [cycle_list, energy_list]


class MonoData(object):

    def __init__(self, disp, force):
        """
        :param disp: displacement
        :param force: force
        """

        self.disp = disp
        self.force = force
        self.DFdata = interpolate.interp1d(disp, force, kind="slinear")
