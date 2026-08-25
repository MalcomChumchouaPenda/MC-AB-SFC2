import csv
import os
import math

# mu5.8

current_dir = os.path.dirname(__file__)
data_folder = os.path.join(current_dir, "data")


class Parameter:
    def __init__(self):
        self.name = "a"
        self.folder = data_folder  # specify saving data folder
        # Monte Carlo runs
        firstrun = 0  #
        lastrun = 0  #
        self.Lrun = range(firstrun, lastrun + 1)
        self.weSeedRun = "yes"
        # space and time
        self.ncycle = 1001
        self.ncountry = 2  # (K)
        self.nconsumer = 500  # #(H)
        self.propTradable = 0.4  # (c_T)
        # firms
        self.A = 10  # (A^0)
        self.upsilon = 1.0  # (upsilon)
        self.phi = 1.0  # (phi_0)
        self.delta = 0.03  # (delta)
        self.dividendRate = 0.95  # (rho)
        self.gamma = 0.03  # (gamma)
        self.ni = 1.5  # (ni)
        self.deltaInnovation = 0.03  # (delta)
        self.Fcost = 1.0  # (F)
        self.minMarkUp = 0.0  # (minimum mark-up)
        self.theta = 0.2
        # consumers
        self.bound = 10  # # (psi)  n. matching
        self.cDisposableIncome = 0.9  # (c_y)
        self.cWealth = 0.2  # (c_D)
        self.liqPref = 0.2  # (lambda)
        self.beta = 2.0  # (beta)
        self.ls = 1.0  # (l^S)
        self.wBar = 0.1  # (w bar)
        self.w0 = 1.0  # (w_0)
        # bank
        self.probBank = 0.03  # (eta)
        self.sigma = 4.0
        self.minReserve = 0.1  # (mu_2)
        self.xi = 0.003  # (chi)
        self.rDeposit = 0.001  # (r_re)
        self.mu1 = 20.0  # (mu_1)
        self.iota = 1.0  # (iota_l)
        self.iotaE = 0.1  # (iota_b)
        # etat
        self.taxRatio = 0.4  # (tau_0)
        self.G = 0.4 * self.nconsumer  # (G)
        self.xiBonds = self.xi  # (chi_B)
        self.maxPublicDeficit = 0.03  # (d^max)
        self.taxRatioMin = 0.35  # (tau_{min})
        self.taxRatioMax = 0.45  # (tau_{max})
        self.gMin = 0.4  # (g_min)
        self.gMax = 0.6  # (g_max)
        # central bank initial discount value
        self.rDiscount = 0.001  # (r_ {re})
        self.rBonds = 0.001  # (r_{b0})
        self.zeta = 0.1  # (zeta)
        self.rBar = 0.0075  # (rBar)
        self.csi = 0.8  # (xi)
        self.csiDP = 2.0  # (xiDP)
        self.inflationTarget = 0.005  # (DeltaP)
        # policy
        self.policyKind = "austerity"  # which policy
        self.startingPolicy = 500  # (policy starting time)
        self.maxPublicDeficitAusterity = 0.03  # (d)
        # timing  collecting simulation data
        self.timeCollectingStart = 0  #
        self.LtimeCollecting = []
        self.printAgent = "no"
        for cycle in range(self.ncycle):
            self.LtimeCollecting.append(cycle)

    def directory(self):
        newpath = self.folder
        if os.path.exists(newpath) == False:
            os.makedirs(newpath)
