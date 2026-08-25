# firm.py
from mind import *

# from technology import *
# from pricing import *
# from balance import *
from lebalance import *

# from innovation import *
import csv
from time import *
import math


class Firm:
    def __init__(
        self,
        ide,
        country,
        A,
        phi,
        Lcountry,
        w,
        folder,
        name,
        run,
        delta,
        dividendRate,
        xi,
        iota,
        upsilon,
        gamma,
        deltaInnovation,
        avPrice,
        Fcost,
        ni,
        minMarkUp,
        eX,
        theta,
    ):
        self.ide = ide
        self.country = country
        self.A = A
        self.phi = phi
        self.Lcountry = Lcountry
        self.w = w
        self.PreviouswAv = self.w
        self.delta = delta
        self.Fcost = Fcost
        self.upsilon = upsilon
        self.minMarkUp = minMarkUp
        x = (self.A / float(self.w)) * phi
        self.xE = max(x, eX)
        lForecasted = x / float(phi)
        p = avPrice
        if p < (1.0 + self.minMarkUp) * (self.w / float(phi)):
            p = (1.0 + self.minMarkUp) * (self.w / float(phi))
        self.price = p
        self.markUp = self.price * (phi / float(self.w)) - 1
        profit = p * x - self.A
        Resources = lForecasted * self.w
        self.dividendRate = dividendRate
        self.productionEffective = 0
        self.spendingA = self.A
        self.xSold = 0
        xSold = 0
        xProd = 0
        loan = 0
        self.lebalance = Lebalance(
            delta,
            self.country,
            self.ide,
            self.dividendRate,
            iota,
            gamma,
            deltaInnovation,
            self.Fcost,
            ni,
            xi,
            self.A,
        )
        self.gamma = gamma
        self.mind = Mind(ide, delta, self.country, self.minMarkUp, self.xE, theta)
        self.folder = folder
        self.name = name
        self.run = run
        self.omega = 1 * random.uniform(0, 2 * math.pi)
        self.theta = theta
        # for the first cycle
        self.Lowner = []
        self.l = 0
        self.closing = "no"
        self.ListOwners = []
        self.loanReceived = 0
        self.Mloan = {}
        self.loanDemand = 0
        self.lebalance.loanDemand = self.loanDemand
        self.ResourceAvailable = 0
        self.PreviousA = self.A
        self.xi = xi
        self.iota = iota
        self.PastA = self.A
        self.CapitalDismiss = 0
        self.Downer = {}
        self.Mdeposit = {}
        self.depositInterest = 0
        self.profit = 0
        self.pastProfit = 0
        self.profitRate = 0
        self.nWorkerDesired = lForecasted
        self.innovationExpenditure = 0
        self.ratioGamma = self.gamma
        self.firmSaving = 0
        self.pastFirmSaving = 0
        self.laborExpenditure = 0
        self.inventory = 0
        self.pastInventory = 0
        self.changeInventory = 0
        self.changeInventoryValue = 0
        self.inventoryValue = 0

    def learning(self):
        if self.closing == "no":
            self.mind.alphaParameterSmooth16(
                self.phi,
                self.w,
                self.inventory,
                self.pastInventory,
                self.price,
                self.productionEffective,
                self.xSold,
            )
            self.price = self.mind.pSelling

    def changingInventory(self):
        if self.xOfferedEffective >= self.xSold:
            self.pastInventory = self.inventory
            self.inventory = 1.0 * (self.xOfferedEffective - self.xSold)
            self.changeInventory = self.inventory - self.pastInventory
            self.changeInventoryValue = (self.w / self.phi) * (
                self.inventory - self.pastInventory
            )
            self.inventoryValue = (self.w / self.phi) * (self.inventory)

    def checkExistence(self):
        self.PreviousA = self.A
        if self.A <= self.Fcost or self.A <= 0.001:
            self.closing = "yes"

    def existence(self, McountryBank, McountryCentralBank):
        self.PreviousA = self.A
        self.pastX = self.productionEffective
        self.receiving(self.sellingMoney, McountryBank, McountryCentralBank)
        self.depositInterest = 0
        for bank in self.Mdeposit:
            self.depositInterest = (
                self.depositInterest + self.Mdeposit[bank][2] * self.Mdeposit[bank][3]
            )
        self.receivingInterestDeposit(McountryBank, McountryCentralBank)
        if self.closing == "yes":
            self.A = self.A + self.depositInterest
            self.pastDepositInterest = self.depositInterest
            self.profitRate = 0
        if self.closing == "no":
            self.debtService = 0
            for bank in self.Mloan:
                self.debtService = (
                    self.debtService + self.Mloan[bank][2] * self.Mloan[bank][3]
                )
            self.netInterest = self.debtService - self.depositInterest
            self.pastDepositInterest = self.depositInterest
            self.lebalance.rebalancing(
                self.A,
                self.netInterest,
                self.innovationExpenditure,
                self.loanReceived,
                self.laborExpenditure,
                self.xSold,
                self.price,
            )
            self.toWorkers = self.lebalance.toWorkers
            self.loanUsed = self.lebalance.loanUsed
            self.loanEffReceived = self.lebalance.loanEffReceived
            self.Entrance = self.lebalance.Entrance
            self.profitRate = self.lebalance.totProfit / float(self.A)
            self.A = self.A + self.lebalance.totProfit
            self.pastProfit = self.profit
            self.profit = self.lebalance.totProfit
            self.netProfit = self.profit
            self.loanNotUsed = self.lebalance.loanNotUsed
            if self.loanReceived < -0.000000001:
                print("stop", stop)
            self.loanReimboursed = 0
            inte = 0
            for bank in self.Mdeposit:
                inte = inte + self.Mdeposit[bank][2] * self.Mdeposit[bank][3]
        if self.closing == "no" and self.A > self.Fcost * self.w:
            for bank in self.Mloan:
                bankIde = self.Mloan[bank][1]
                loanValue = self.Mloan[bank][2]
                service = self.Mloan[bank][2] * self.Mloan[bank][3]
                countryBank = self.Mloan[bank][4]
                loanVolume = loanValue + service
                self.repayingLoan(
                    bankIde,
                    loanValue,
                    loanVolume,
                    McountryBank,
                    McountryCentralBank,
                    countryBank,
                )
            self.checkNetWorth()
        if self.closing == "yes" or self.A <= self.Fcost * self.w:
            self.closing = "yes"
            self.ResourceAvailable = 0
            if self.A >= 0:
                self.CapitalDismiss = self.A
                self.loanReimboursed = self.loanReceived + self.debtService
            if self.A < 0:
                self.CapitalDismiss = 0
                self.loanReimboursed = self.A + self.loanReceived + self.debtService
            self.A = 0
        if self.A < -0.000001:
            print("stop", stop)

    def distributingDividends(
        self, McountryConsumer, McountryBank, McountryCentralBank
    ):
        self.dividending()
        self.capitalVariation(McountryConsumer, McountryBank, McountryCentralBank)

    def dividending(self):
        self.lebalance.dividending(
            self.A, self.closing, self.netProfit, self.loanDemand
        )
        self.dividends = self.lebalance.dividends
        self.pastFirmSaving = self.firmSaving
        self.firmSaving = self.netProfit - self.dividends
        self.A = self.A - self.dividends

    def productionDesired(
        self, McountryBank, McountryCentralBank, time, McountryAvPrice
    ):
        self.loanDemand = 0
        pastSold_x = self.xSold
        if self.closing == "no":
            self.lebalance.producingObjectives4(
                self.w, self.A, self.phi, self.mind.xProducing, self.price
            )
            self.lebalance.innovatingAttempt(
                self.A, McountryCentralBank[self.country].rDiscount
            )
            self.ResourceAvailable = self.lebalance.ResourceAvailable
            p = self.price
            self.lebalance.loanDemanding(
                self.A,
                self.w,
                self.phi,
                p,
                McountryCentralBank[self.country].rDiscount,
                self.xi,
            )
            self.loanDemand = self.lebalance.loanDemand
            self.workForceNumberDesired = self.lebalance.workForceNumberDesired
            self.workForceExpenditureNoInnovation = (
                self.lebalance.workForceExpenditureNoInnovation
            )
            self.workForceNumberInnovation = self.lebalance.workForceNumberInnovation
            self.workForceNumberProduction = self.lebalance.workForceNumberProduction
            self.workForceInnovationExpenditureDesired = (
                self.lebalance.workForceInnovationExpenditureDesired
            )
            self.ratioGamma = 0
            if self.workForceExpenditureNoInnovation > 0:
                self.ratioGamma = self.workForceInnovationExpenditureDesired / float(
                    self.workForceExpenditureNoInnovation
                )
        if self.closing == "yes":
            self.loanDemand = 0

    def capitalVariation(self, McountryConsumer, McountryBank, McountryCentralBank):
        self.PastA = self.A
        self.ResourceAvailable = 0
        Ashare = 0
        if self.PreviousA + self.CapitalDismiss > 0:
            Ashare = self.A / float(self.PreviousA + self.CapitalDismiss)
        if (
            self.PreviousA + self.CapitalDismiss < -0.000000000001
            and len(self.ListOwners) > 0
        ):
            print("stop", stop)
        if self.CapitalDismiss > 0.00001 and self.closing == "no":
            print("stop", stop)
        lastA = 0
        Avariation = self.A - self.PreviousA
        totalPayement = 0
        for consumerIde in self.Downer:
            if self.closing == "yes":
                ConsumerA = McountryConsumer[self.country][consumerIde].DLA[self.ide][2]
                DismissShareCapital = (
                    self.CapitalDismiss * ConsumerA / float(self.PreviousA)
                )
                DividendShare = self.dividends * ConsumerA / float(self.PreviousA)
                McountryConsumer[self.country][consumerIde].capitalDismiss = (
                    McountryConsumer[self.country][consumerIde].capitalDismiss
                    + DismissShareCapital
                )
                McountryConsumer[self.country][consumerIde].DividendShare = (
                    McountryConsumer[self.country][consumerIde].DividendShare
                    + DividendShare
                )
                totalPayement = totalPayement + DismissShareCapital + DividendShare
                oldShare = McountryConsumer[self.country][consumerIde].DLA[self.ide][2]
                McountryConsumer[self.country][consumerIde].totProfit = (
                    McountryConsumer[self.country][consumerIde].totProfit
                    + self.profitRate * oldShare
                )
                paymentConsumer = DismissShareCapital + DividendShare
                McountryConsumer[self.country][consumerIde].receiving(
                    paymentConsumer, McountryBank, McountryCentralBank
                )
                del McountryConsumer[self.country][consumerIde].DLA[self.ide]
            else:
                oldShare = McountryConsumer[self.country][consumerIde].DLA[self.ide][2]
                ConsumerAshare = (
                    self.A
                    * McountryConsumer[self.country][consumerIde].DLA[self.ide][4]
                )
                if self.CapitalDismiss > 0.00001:
                    print("stop", stop)
                DismissShareCapital = (
                    self.CapitalDismiss * ConsumerAshare / float(self.A)
                )
                DividendShare = self.dividends * ConsumerAshare / float(self.A)
                ratioA = ConsumerAshare / float(self.A)
                McountryConsumer[self.country][consumerIde].DLA[self.ide][
                    2
                ] = ConsumerAshare
                McountryConsumer[self.country][consumerIde].DLA[self.ide][4] = ratioA
                McountryConsumer[self.country][consumerIde].totProfit = (
                    McountryConsumer[self.country][consumerIde].totProfit
                    + self.profitRate * oldShare
                )
                self.Downer[consumerIde][2] = McountryConsumer[self.country][
                    consumerIde
                ].DLA[self.ide][2]
                self.Downer[consumerIde][4] = McountryConsumer[self.country][
                    consumerIde
                ].DLA[self.ide][4]
                McountryConsumer[self.country][consumerIde].capitalDismiss = (
                    McountryConsumer[self.country][consumerIde].capitalDismiss
                    + DismissShareCapital
                )
                McountryConsumer[self.country][consumerIde].DividendShare = (
                    McountryConsumer[self.country][consumerIde].DividendShare
                    + DividendShare
                )
                totalPayement = totalPayement + DismissShareCapital + DividendShare
                paymentConsumer = DismissShareCapital + DividendShare
                McountryConsumer[self.country][consumerIde].receiving(
                    paymentConsumer, McountryBank, McountryCentralBank
                )
        self.paying(totalPayement, McountryBank, McountryCentralBank)
        self.CapitalDismiss = 0

    def effectiveSelling(
        self,
        DglobalPhiNotTradable,
        avPhiGlobalTradable,
        avPriceGlobalTradable,
        McountryAvPriceNotTradable,
    ):
        workersProductionAvailable = self.l
        workerInnovationAvailable = 0
        if self.l > self.workForceNumberProduction + 0.001:
            print("stop", stop)
        if workersProductionAvailable <= 0:
            self.productionEffective = 0
        if workersProductionAvailable > 0:
            self.productionEffective = workersProductionAvailable * self.phi
        self.xOfferedEffective = self.productionEffective + self.inventory
        self.phi = self.lebalance.innovatingEffective3(
            self.innovationExpenditure,
            self.phi,
            self.l,
            DglobalPhiNotTradable,
            avPhiGlobalTradable,
            self.tradable,
            avPriceGlobalTradable,
            McountryAvPriceNotTradable,
        )

    def wageOffered(self, McountryAvPrice, McountryUnemployement, nconsumer, avWage):
        nWorkerDesired = self.nWorkerDesired
        l = self.l
        p = self.price
        u = McountryUnemployement[self.country]
        a = random.uniform(0, 1)
        if nWorkerDesired > self.l:
            direction = "plus"
        if nWorkerDesired <= self.l and a > math.exp(-u * self.upsilon):
            direction = "minus"
        if nWorkerDesired <= self.l and a <= math.exp(-u * self.upsilon):
            direction = "stay"
        if direction == "plus":
            self.w = random.uniform(self.w, self.w * (1 + self.delta))
        if direction == "minus":
            self.w = random.uniform(self.w, self.w * (1 - self.delta))
        if self.w < 0:
            self.w = 0

    def initialCycleVariable(self):
        self.PreviousA = self.A
        self.l = 0
        self.CapitalDismiss = 0
        self.laborExpenditure = 0

    def write(self, t, run):
        nameWrite = self.folder + "/" + self.name + "r" + str(run) + "Firm.csv"
        f = open(nameWrite, "a")
        x_prod = self.productionEffective
        x_programmed = self.mind.xProducing
        x_sold = self.xSold
        p = self.price
        revenue = x_sold * p
        F = [
            self.run,
            self.ide,
            t,
            self.country,
            self.phi,
            self.profit,
            p,
            self.w,
            self.l,
            x_prod,
            self.mind.xE,
            x_sold,
            self.inventory,
            self.workForceNumberDesired,
            self.A,
            revenue,
        ]
        writer = csv.writer(f)
        writer.writerow(F)
        f.close()

    def orderCreditor(self):
        self.Lcreditor = []
        for bank in self.Mloan:
            # print('stop', stop)
            self.Lcreditor.append(self.Mloan[bank][1])
        random.shuffle(self.Lcreditor)
        # self.Mloan=[]

    def orderBankDeposit(self, McountryBank):
        self.LbankDeposit = []
        LdelBank = []
        for bank in self.Mdeposit:
            countryBank = self.Mdeposit[bank][4]
            if (bank in McountryBank[countryBank]) == True or bank == self.country:
                self.LbankDeposit.append(bank)
            else:
                if self.Mdeposit[bank][2] > 0.000001:
                    print("stop", stop)
                LdelBank.append(bank)
        for bank in LdelBank:
            del self.Mdeposit[bank]

    def paying(self, payment, McountryBank, McountryCentralBank):
        random.shuffle(self.LbankDeposit)
        for bank in self.LbankDeposit:
            volumeDeposit = self.Mdeposit[bank][2]
            countryBank = self.Mdeposit[bank][4]
            if payment <= volumeDeposit:
                reduction = payment
                self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                if bank != self.country:
                    volumeCheck = McountryBank[countryBank][bank].Mdeposit[self.ide][2]
                if bank == self.country:
                    volumeCheck = McountryCentralBank[countryBank].Mdeposit[self.ide][2]
                if (
                    volumeDeposit < volumeCheck - 0.00001
                    or volumeDeposit > volumeCheck + 0.00001
                ):
                    print("stop", stop)
                if bank != self.country:
                    McountryBank[countryBank][bank].depositWithdrawal(
                        reduction, self.ide, McountryCentralBank
                    )
                if bank == self.country:
                    McountryCentralBank[self.country].depositWithdrawal(
                        reduction, self.ide
                    )
                    if len(self.LbankDeposit) > 1:
                        print("stop", stop)
                payment = payment - reduction
                if countryBank != self.country:
                    McountryCentralBank[self.country].moneyInflow = (
                        McountryCentralBank[self.country].moneyInflow + reduction
                    )
                    McountryCentralBank[countryBank].moneyOutflow = (
                        McountryCentralBank[countryBank].moneyOutflow + reduction
                    )
                break
            else:
                reduction = volumeDeposit
                self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                if bank != self.country:
                    volumeCheck = McountryBank[countryBank][bank].Mdeposit[self.ide][2]
                if bank == self.country:
                    volumeCheck = McountryCentralBank[countryBank].Mdeposit[self.ide][2]
                if (
                    volumeDeposit < volumeCheck - 0.00001
                    or volumeDeposit > volumeCheck + 0.00001
                ):
                    print("stop", stop)
                if bank != self.country:
                    McountryBank[countryBank][bank].depositWithdrawal(
                        reduction, self.ide, McountryCentralBank
                    )
                if bank == self.country:
                    McountryCentralBank[self.country].depositWithdrawal(
                        reduction, self.ide
                    )
                payment = payment - reduction
                if countryBank != self.country:
                    McountryCentralBank[self.country].moneyInflow = (
                        McountryCentralBank[self.country].moneyInflow + reduction
                    )
                    McountryCentralBank[countryBank].moneyOutflow = (
                        McountryCentralBank[countryBank].moneyOutflow + reduction
                    )
        if payment > 0.001:
            print("stop", stop)

    def receivingInterestDeposit(self, McountryBank, McountryCentralBank):
        for bank in self.Mdeposit:
            if bank != self.country:
                volume = self.Mdeposit[bank][2]
                interest = self.Mdeposit[bank][3]
                countryBank = self.Mdeposit[bank][4]
                service = volume * interest
                self.Mdeposit[bank][2] = self.Mdeposit[bank][2] + service
                McountryBank[countryBank][bank].Mdeposit[self.ide][2] = (
                    McountryBank[countryBank][bank].Mdeposit[self.ide][2] + service
                )
                McountryBank[countryBank][bank].Deposit = (
                    McountryBank[countryBank][bank].Deposit + service
                )
                McountryBank[countryBank][bank].serviceFirm = (
                    McountryBank[countryBank][bank].serviceFirm + service
                )
                if countryBank != self.country:
                    McountryCentralBank[self.country].moneyInflow = (
                        McountryCentralBank[self.country].moneyInflow + service
                    )
                    McountryCentralBank[countryBank].moneyOutflow = (
                        McountryCentralBank[countryBank].moneyOutflow + service
                    )

    def receiving(self, payment, McountryBank, McountryCentralBank):
        random.shuffle(self.LbankDeposit)
        ideBank = self.LbankDeposit[0]
        volumeDeposit = self.Mdeposit[ideBank][2]
        countryBank = self.Mdeposit[ideBank][4]
        if ideBank != self.country:
            volumeCheck = McountryBank[countryBank][ideBank].Mdeposit[self.ide][2]
        if ideBank == self.country:
            volumeCheck = McountryCentralBank[self.country].Mdeposit[self.ide][2]
        if (
            volumeDeposit < volumeCheck - 0.00001
            or volumeDeposit > volumeCheck + 0.00001
        ):
            print("stop", stop)
        if ideBank != self.country:
            self.Mdeposit[ideBank][2] = self.Mdeposit[ideBank][2] + payment
            McountryBank[countryBank][ideBank].depositInjection(
                payment, self.ide, McountryCentralBank
            )
            if countryBank != self.country:
                McountryCentralBank[countryBank].moneyInflow = (
                    McountryCentralBank[countryBank].moneyInflow + payment
                )
                McountryCentralBank[self.country].moneyOutflow = (
                    McountryCentralBank[self.country].moneyOutflow + payment
                )
        if ideBank == self.country:
            if len(self.LbankDeposit) > 1:
                print("stop", stop)
            self.Mdeposit[ideBank][2] = self.Mdeposit[ideBank][2] + payment
            McountryCentralBank[self.country].depositInjection(payment, self.ide)

    def receavingLoan(
        self,
        ideBank,
        loan,
        interestRate,
        interestRateDeposit,
        countryBank,
        McountryBank,
        McountryCentralBank,
    ):
        if self.country == countryBank:
            self.receavingLoanDomestic(
                ideBank, loan, interestRate, interestRateDeposit, countryBank
            )
        if self.country != countryBank:
            self.receavingLoanForeigner(
                ideBank,
                loan,
                interestRate,
                interestRateDeposit,
                countryBank,
                McountryBank,
                McountryCentralBank,
            )

    def receavingLoanDomestic(
        self, ideBank, loan, interestRate, interestRateDeposit, countryBank
    ):
        self.Mloan[ideBank] = [self.ide, ideBank, loan, interestRate, countryBank]
        if (ideBank in self.Mdeposit) == True:
            self.Mdeposit[ideBank][2] = self.Mdeposit[ideBank][2] + loan
        elif (ideBank in self.Mdeposit) == False:
            self.Mdeposit[ideBank] = [
                self.ide,
                ideBank,
                loan,
                interestRateDeposit,
                countryBank,
            ]
        self.loanReceived = self.loanReceived + loan
        self.interestRate = interestRate
        self.Lcreditor.append(ideBank)
        self.LbankDeposit.append(ideBank)

    def receavingLoanForeigner(
        self,
        ideBank,
        loan,
        interestRate,
        interestRateDeposit,
        countryBank,
        McountryBank,
        McountryCentralBank,
    ):
        self.Mloan[ideBank] = [self.ide, ideBank, loan, interestRate, countryBank]
        self.loanReceived = self.loanReceived + loan
        self.interestRate = interestRate
        self.Lcreditor.append(ideBank)
        self.receiving(loan, McountryBank, McountryCentralBank)

    def repayingLoan(
        self,
        bankIde,
        loanValue,
        loanVolume,
        McountryBank,
        McountryCentralBank,
        countryBank,
    ):
        if countryBank == self.country:
            self.repayingLoanDomestic(
                bankIde,
                loanValue,
                loanVolume,
                McountryBank,
                McountryCentralBank,
                countryBank,
            )
        if countryBank != self.country:
            self.repayingLoanForeigner(
                bankIde,
                loanValue,
                loanVolume,
                McountryBank,
                McountryCentralBank,
                countryBank,
            )

    def repayingLoanDomestic(
        self,
        bankIde,
        loanValue,
        loanVolume,
        McountryBank,
        McountryCentralBank,
        countryBank,
    ):
        countryBank = self.Mdeposit[bankIde][4]
        McountryBank[countryBank][bankIde].Loan = (
            McountryBank[countryBank][bankIde].Loan - loanValue
        )
        volumeDeposit = self.Mdeposit[bankIde][2]
        if loanVolume <= volumeDeposit:
            reduction = loanVolume
            self.Mdeposit[bankIde][2] = self.Mdeposit[bankIde][2] - reduction
            McountryBank[countryBank][bankIde].Mdeposit[self.ide][2] = (
                McountryBank[countryBank][bankIde].Mdeposit[self.ide][2] - reduction
            )
            McountryBank[countryBank][bankIde].Deposit = (
                McountryBank[countryBank][bankIde].Deposit - reduction
            )
            if countryBank != self.country:
                McountryCentralBank[countryBank].moneyInflow = (
                    McountryCentralBank[countryBank].moneyInflow + reduction
                )
                McountryCentralBank[self.country].moneyOutflow = (
                    McountryCentralBank[self.country].moneyOutflow + reduction
                )
        if loanVolume > volumeDeposit:
            reduction = volumeDeposit
            self.Mdeposit[bankIde][2] = self.Mdeposit[bankIde][2] - reduction
            McountryBank[countryBank][bankIde].Mdeposit[self.ide][2] = (
                McountryBank[countryBank][bankIde].Mdeposit[self.ide][2] - reduction
            )
            McountryBank[countryBank][bankIde].Deposit = (
                McountryBank[countryBank][bankIde].Deposit - reduction
            )
            loanVolume = loanVolume - reduction
            random.shuffle(self.LbankDeposit)
            for bank in self.LbankDeposit:
                volumeDeposit = self.Mdeposit[bank][2]
                countryBankNew = self.Mdeposit[bank][4]
                if loanVolume <= volumeDeposit:
                    reduction = loanVolume
                    self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                    McountryBank[countryBankNew][bank].depositWithdrawal(
                        reduction, self.ide, McountryCentralBank
                    )
                    McountryBank[countryBank][bankIde].Reserves = (
                        McountryBank[countryBank][bankIde].Reserves + reduction
                    )
                    McountryCentralBank[countryBank].Reserves = (
                        McountryCentralBank[countryBank].Reserves + reduction
                    )
                    if countryBankNew != self.country:
                        McountryCentralBank[self.country].moneyInflow = (
                            McountryCentralBank[self.country].moneyInflow + reduction
                        )
                        McountryCentralBank[countryBank].moneyOutflow = (
                            McountryCentralBank[countryBank].moneyOutflow + reduction
                        )
                    break
                else:
                    reduction = volumeDeposit
                    self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                    McountryBank[countryBankNew][bank].depositWithdrawal(
                        reduction, self.ide, McountryCentralBank
                    )
                    McountryBank[countryBank][bankIde].Reserves = (
                        McountryBank[countryBank][bankIde].Reserves + reduction
                    )
                    McountryCentralBank[countryBank].Reserves = (
                        McountryCentralBank[countryBank].Reserves + reduction
                    )
                    loanVolume = loanVolume - reduction
                    if countryBankNew != self.country:
                        McountryCentralBank[self.country].moneyInflow = (
                            McountryCentralBank[self.country].moneyInflow + reduction
                        )
                        McountryCentralBank[countryBank].moneyOutflow = (
                            McountryCentralBank[countryBank].moneyOutflow + reduction
                        )

    def repayingLoanForeigner(
        self,
        bankIde,
        loanValue,
        loanVolume,
        McountryBank,
        McountryCentralBank,
        countryBank,
    ):
        McountryBank[countryBank][bankIde].Loan = (
            McountryBank[countryBank][bankIde].Loan - loanValue
        )
        random.shuffle(self.LbankDeposit)
        for bank in self.LbankDeposit:
            volumeDeposit = self.Mdeposit[bank][2]
            countryBankNew = self.Mdeposit[bank][4]
            if loanVolume <= volumeDeposit:
                reduction = loanVolume
                self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                McountryBank[countryBankNew][bank].depositWithdrawal(
                    reduction, self.ide, McountryCentralBank
                )
                McountryBank[countryBank][bankIde].Reserves = (
                    McountryBank[countryBank][bankIde].Reserves + reduction
                )
                McountryCentralBank[countryBank].Reserves = (
                    McountryCentralBank[countryBank].Reserves + reduction
                )
                McountryCentralBank[countryBank].moneyInflow = (
                    McountryCentralBank[countryBank].moneyInflow + reduction
                )
                McountryCentralBank[self.country].moneyOutflow = (
                    McountryCentralBank[self.country].moneyOutflow + reduction
                )
                break
            else:
                reduction = volumeDeposit
                self.Mdeposit[bank][2] = self.Mdeposit[bank][2] - reduction
                McountryBank[countryBankNew][bank].depositWithdrawal(
                    reduction, self.ide, McountryCentralBank
                )
                McountryBank[countryBank][bankIde].Reserves = (
                    McountryBank[countryBank][bankIde].Reserves + reduction
                )
                McountryCentralBank[countryBank].Reserves = (
                    McountryCentralBank[countryBank].Reserves + reduction
                )
                loanVolume = loanVolume - reduction
                McountryCentralBank[countryBank].moneyInflow = (
                    McountryCentralBank[countryBank].moneyInflow + reduction
                )
                McountryCentralBank[self.country].moneyOutflow = (
                    McountryCentralBank[self.country].moneyOutflow + reduction
                )

    def computeDeposit(self):
        self.Deposit = 0
        for bank in self.Mdeposit:
            self.Deposit = self.Deposit + self.Mdeposit[bank][2]

    def checkNetWorth(self):
        Liabilities = self.A
        Deposit = 0
        for bank in self.Mdeposit:
            Deposit = Deposit + self.Mdeposit[bank][2]
        Assets = Deposit
        if (Liabilities - Assets) / float(Liabilities + Assets) > 0.0001 or (
            Liabilities - Assets
        ) / float(Liabilities + Assets) < -0.0001:
            print("stop", stop)

    def checkOwnerhip(self, McountryConsumer):
        totConsumerA = 0
        totFirmA = 0
        for consumerIde in self.Downer:
            totConsumerA = (
                totConsumerA
                + McountryConsumer[self.country][consumerIde].DLA[self.ide][2]
            )
            totFirmA = totFirmA + self.Downer[consumerIde][2]
