# lebalance.py
import random
import math

# import numpy


class Lebalance:
    def __init__(
        self,
        delta,
        firmcountry,
        ide,
        dividendRate,
        iota,
        gamma,
        deltaInnovation,
        Fcost,
        ni,
        xi,
        A,
    ):
        self.delta = delta
        self.firmcountry = firmcountry
        self.country = firmcountry
        self.ide = ide
        self.dividendRate = dividendRate
        self.iota = iota
        self.ResourceAvailable = 0
        self.gamma = gamma
        self.deltaInnovation = deltaInnovation
        self.Fcost = Fcost
        self.ni = ni
        self.totalExpenditure = 0
        self.xi = xi
        self.Aspending = A
        self.Lsold = [0, 0, 0, 0]

    def rebalancing(
        self,
        A,
        debtService,
        innovationExpenditure,
        loanReceived,
        laborExpenditure,
        xSold,
        price,
    ):
        losses = debtService
        self.loanNotUsed = 0
        self.loanUsed = 0
        self.loanEffReceived = 0
        self.Entrance = 0
        self.totProfit = -debtService
        self.ResourceAvailable = 0
        self.toWorkers = 0
        expenditure = innovationExpenditure + laborExpenditure
        p = price
        revenue = p * xSold
        Amp = A
        loan = loanReceived
        loanNotUsed = 0
        if expenditure <= Amp:
            loanNotUsed = loan
            loanUsed = 0
        if expenditure > Amp:
            loanNotUsed = loan - (expenditure - Amp)
            loanUsed = expenditure - Amp
        if expenditure > Amp + loan + 0.001:
            print("stop", stop)
        self.loanNotUsed = self.loanNotUsed + loanNotUsed
        self.loanUsed = self.loanUsed + loanUsed
        self.loanEffReceived = self.loanEffReceived + loan
        self.Entrance = self.Entrance + revenue
        profit = revenue - expenditure
        self.totalExpenditure = expenditure + debtService
        self.toWorkers = self.toWorkers + expenditure
        self.totProfit = self.totProfit + profit
        self.wantedNotToUse = 0
        Amp = Amp + self.totProfit
        self.Aspending = Amp
        self.A = Amp

    def dividending(self, A, closing, profit, loanDemand):
        self.dividends = 0
        if A > 0.0 and profit > 0 and closing == "no":
            self.dividends = profit * self.dividendRate
            base = self.wantedNotToUse + profit
            if base < 0:
                base = 0
            self.dividendToA = self.dividends
            newA = A - self.dividendToA
            self.Aspending = newA

    def producingObjectives4(self, Wage, A, phi, xProducing, price):
        self.ResourceAvailable = 0
        self.loanDemand = 0
        self.ResourceMissing = 0
        totnewA = 0
        checkA = 0
        Adisp = A
        Adisp = self.Aspending
        p = price
        xObjectProduct = xProducing
        if xObjectProduct < 0:
            print("stop", stop)
            xObjectProduct = 0
        productivity = phi
        nWorkerProduct = xObjectProduct / float(productivity)
        expenditureProduct = nWorkerProduct * Wage
        totProductivity = productivity
        totalExpenditure = expenditureProduct
        if totalExpenditure <= Adisp:
            diffExpenditureNeeded = Adisp - totalExpenditure
            Areduction = diffExpenditureNeeded
            self.ResourceAvailable = self.ResourceAvailable + Areduction
            self.Aspending = totalExpenditure
        if totalExpenditure > Adisp:
            self.ResourceMissing = totalExpenditure - Adisp
            loanDemand = totalExpenditure - Adisp
            self.loanDemand = loanDemand
            self.Aspending = A
        self.workForceProductionExpenditureDesired = totalExpenditure
        self.workForceNumberDesired = totalExpenditure / float(Wage)
        self.workForceExpenditureNoInnovation = totalExpenditure

    def innovatingAttempt(self, A, rDiscount):
        leverage = self.loanDemand / float(A)
        r = self.xi * leverage + rDiscount
        self.workForceInnovationExpenditureDesired = self.gamma * (
            self.workForceProductionExpenditureDesired + r * self.loanDemand
        )
        if self.workForceInnovationExpenditureDesired <= self.ResourceAvailable:
            self.ResourceAvailable = (
                self.ResourceAvailable - self.workForceInnovationExpenditureDesired
            )
            self.Aspending = self.Aspending + self.workForceInnovationExpenditureDesired
        else:
            self.loanDemand = (
                self.loanDemand
                + self.workForceInnovationExpenditureDesired
                - self.ResourceAvailable
            )
            self.Aspending = self.Aspending + self.ResourceAvailable
            self.ResourceAvailable = 0
        self.workForceNumberInnovation = 0.0 * self.gamma * self.workForceNumberDesired
        self.workForceNumberProduction = self.workForceNumberDesired
        self.workForceNumberDesired = (
            self.workForceNumberDesired + 0.0 * self.gamma * self.workForceNumberDesired
        )

    def innovatingEffective3(
        self,
        innovationExpenditure,
        phi,
        l,
        DglobalPhiNotTradable,
        avPhiGlobalTradable,
        tradable,
        avPriceGlobalTradable,
        McountryAvPriceNotTradable,
    ):
        if self.gamma > 0.00000001:
            if tradable == "yes":
                if l > 0 and avPriceGlobalTradable * avPhiGlobalTradable > 0:
                    workerInnovationAvailableEffective = innovationExpenditure / float(
                        avPriceGlobalTradable * avPhiGlobalTradable
                    )
                if l <= 0 or avPriceGlobalTradable * avPhiGlobalTradable <= 0:
                    workerInnovationAvailableEffective = 0
            if tradable == "no":
                if (
                    l > 0
                    and McountryAvPriceNotTradable[self.country]
                    * DglobalPhiNotTradable[self.country]
                    > 0
                ):
                    workerInnovationAvailableEffective = innovationExpenditure / float(
                        McountryAvPriceNotTradable[self.country]
                        * DglobalPhiNotTradable[self.country]
                    )
                if (
                    l <= 0
                    or McountryAvPriceNotTradable[self.country]
                    * DglobalPhiNotTradable[self.country]
                    <= 0
                ):
                    workerInnovationAvailableEffective = 0
            a = random.uniform(0, 1)
            b = 1 - math.exp(-self.ni * workerInnovationAvailableEffective)
            c = b
            if a < b:
                u = random.uniform(0, self.deltaInnovation)
                phi = phi * (1 + u)
            d = random.uniform(0, 1)
            lambdaInn = 1.0
            if d < c:
                if tradable == "yes":
                    if phi < avPhiGlobalTradable:
                        phi = phi + random.uniform(
                            0, lambdaInn * (avPhiGlobalTradable - phi)
                        )
                if tradable == "no":
                    if phi < avPhiGlobalTradable:
                        phi = phi + random.uniform(
                            0, lambdaInn * (DglobalPhiNotTradable[self.country] - phi)
                        )
        return phi

    def loanDemanding(self, A, w, phi, p, rDiscount, xi):
        leverage = self.loanDemand / float(A)
        r = xi * leverage + rDiscount
        gain = p * (self.loanDemand / float(w)) * phi
        cost = r * self.loanDemand
        if gain < cost:
            self.loanDemand = 0
