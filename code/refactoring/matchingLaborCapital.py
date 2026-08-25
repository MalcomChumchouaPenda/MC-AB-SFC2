# matchingLaborCapital.py
import random


class MatchingLaborCapital:
    def __init__(self, bound):
        self.bound = bound

    def working(
        self,
        McountryFirm,
        McountryConsumer,
        McountryEtat,
        McountryBank,
        McountryCentralBank,
        McountryUnemployement,
    ):
        self.laborMatch(
            McountryFirm, McountryConsumer, McountryEtat, McountryUnemployement
        )
        self.laborDisMatch(
            McountryFirm,
            McountryConsumer,
            McountryEtat,
            McountryBank,
            McountryCentralBank,
        )

    def laborMatch(
        self, McountryFirm, McountryConsumer, McountryEtat, McountryUnemployement
    ):
        self.McountryDemandLabor = {}
        self.McountrySupplyLabor = {}
        for country in McountryFirm:
            self.McountryDemandLabor[country] = []
            self.McountrySupplyLabor[country] = []
            LdemandLabor = []
            LsupplyLabor = []
            posFirm = 0
            for firm in McountryFirm[country]:
                Deposit = 0
                for bank in McountryFirm[country][firm].Mdeposit:
                    Deposit = Deposit + McountryFirm[country][firm].Mdeposit[bank][2]
                if McountryFirm[country][firm].closing == "no":
                    McountryFirm[country][firm].initialCycleVariable()
                    McountryFirm[country][firm].Lemployed = []
                    totAdisp = 0
                    totAdispEffective = 0
                    McountryFirm[country][firm].workerSearching = 0
                    x = McountryFirm[country][firm].mind.xProducing
                    nworkerPr = McountryFirm[country][firm].workForceNumberDesired
                    w = McountryFirm[country][firm].w
                    Adisp = nworkerPr * w
                    AdispEffective = (
                        McountryFirm[country][firm].lebalance.Aspending
                        + McountryFirm[country][firm].loanReceived
                    )
                    p = McountryFirm[country][firm].price
                    nWorkerPossible = AdispEffective / float(w)
                    nWorkerDesired = min(
                        McountryFirm[country][firm].workForceNumberDesired,
                        nWorkerPossible,
                    )
                    McountryFirm[country][firm].nWorkerDesired = nWorkerDesired
                    LdemandLabor.append(
                        [
                            McountryFirm[country][firm].ide,
                            x,
                            0,
                            McountryFirm[country][firm].country,
                            0,
                            posFirm,
                            AdispEffective,
                            0,
                            "firm",
                            country,
                            0,
                            p,
                            nWorkerDesired,
                        ]
                    )
                    totAdisp = totAdisp + Adisp
                    totAdispEffective = totAdispEffective + AdispEffective
                    posFirm = posFirm + 1
            # Consumers
            posConsumer = 0
            for consumer in McountryConsumer[country]:
                McountryConsumer[country][consumer].pastL = McountryConsumer[country][
                    consumer
                ].l
                McountryConsumer[country][consumer].laborSupply(McountryUnemployement)
                McountryConsumer[country][consumer].l = 0
                McountryConsumer[country][consumer].laborIncome = 0
                McountryConsumer[country][consumer].innovationIncome = 0
                McountryConsumer[country][consumer].LwOffered = []
                McountryConsumer[country][consumer].Lphip = []
                wageDemanded = McountryConsumer[country][consumer].wageDemanded
                LfirmConsumer = []
                LsupplyLabor.append(
                    [
                        wageDemanded,
                        McountryConsumer[country][consumer].w,
                        McountryConsumer[country][consumer].ide,
                        posConsumer,
                        0,
                        0,
                        LfirmConsumer,
                    ]
                )
                posConsumer = posConsumer + 1
            # start matching
            random.shuffle(LsupplyLabor)
            for supply in LsupplyLabor:
                wageDemanded = supply[0]
                posWorker = supply[3]
                ideWorker = supply[2]
                lenJob = len(LdemandLabor)
                length = self.bound
                if lenJob < length:
                    length = lenJob
                LchoiceJob = []
                if lenJob > 0:
                    LlenJob = range(lenJob)
                    LchoiceJob = random.sample(LlenJob, length)
                LdelMcountryJob = []
                LwageOffered = []
                for job in LchoiceJob:
                    posDemand = job
                    if LdemandLabor[posDemand][8] == "firm":
                        firmide = LdemandLabor[posDemand][0]
                        countryFirm = LdemandLabor[posDemand][3]
                        wOffered = McountryFirm[countryFirm][firmide].w
                        McountryFirm[countryFirm][firmide].workerSearching = (
                            McountryFirm[countryFirm][firmide].workerSearching + 1
                        )
                        if countryFirm != country:
                            print("stop", stop)
                        nWorkerDesired = LdemandLabor[posDemand][12]
                        # if nWorkerDesired>=1:
                        #   h=1
                        # else:
                        #   h=nWorkerDesired
                        money = LdemandLabor[posDemand][6]
                        LwageOffered.append(
                            [wOffered, posDemand, nWorkerDesired, money]
                        )
                random.shuffle(LwageOffered)
                for wageOffer in LwageOffered:
                    posDemand = wageOffer[1]
                    posFirm = LdemandLabor[posDemand][5]
                    firmide = LdemandLabor[posDemand][0]
                    countryFirm = LdemandLabor[posDemand][3]
                    p = McountryFirm[countryFirm][firmide].price
                    wOffered = McountryFirm[countryFirm][firmide].w
                    nWorkerDesired = LdemandLabor[posDemand][12]
                    phi = McountryFirm[countryFirm][firmide].phi
                    if (
                        nWorkerDesired > 0.001
                        and LdemandLabor[posDemand][6] >= 0.001
                        and supply[4] <= McountryConsumer[country][ideWorker].ls - 0.001
                        and wOffered >= wageDemanded
                    ):
                        Adisp = LdemandLabor[posDemand][6]
                        demandQuantity = LdemandLabor[posDemand][1]
                        supplyLabor = (
                            McountryConsumer[country][ideWorker].ls - supply[4]
                        )
                        if supplyLabor >= nWorkerDesired:
                            labor = nWorkerDesired
                        if supplyLabor < nWorkerDesired:
                            labor = supplyLabor
                        if labor > 0.001:
                            supply[4] = supply[4] + labor
                            supply[5] = supply[5] + labor * wOffered
                            LdemandLabor[posDemand][2] = (
                                LdemandLabor[posDemand][2] + labor
                            )
                            LdemandLabor[posDemand][4] = (
                                LdemandLabor[posDemand][4] + wOffered * labor
                            )
                            LdemandLabor[posDemand][6] = (
                                LdemandLabor[posDemand][6] - wOffered * labor
                            )
                            LdemandLabor[posDemand][12] = (
                                LdemandLabor[posDemand][12] - labor
                            )
                            if labor >= 0.001:
                                McountryConsumer[country][ideWorker].LwOffered.append(
                                    wOffered
                                )
                                McountryConsumer[country][ideWorker].Lphip.append(
                                    p * phi
                                )
                                McountryFirm[countryFirm][firmide].Lemployed.append(
                                    [ideWorker, labor]
                                )
                        if LdemandLabor[posDemand][6] < -0.001:
                            print("stop", stop)
                        if (
                            LdemandLabor[posDemand][1] <= 0.001
                            or LdemandLabor[posDemand][6] <= 0.001
                        ):
                            if LdemandLabor[posDemand][1] < -0.001:
                                print("stop", stop)
                        if (
                            LdemandLabor[posDemand][6] <= 0.001
                            or nWorkerDesired <= 0.001
                        ):
                            self.McountryDemandLabor[country].append(
                                LdemandLabor[posDemand]
                            )
                            LdelMcountryJob.append(posDemand)
                        if supply[4] > McountryConsumer[country][ideWorker].ls + 0.001:
                            print("stop", stop)
                        if supply[4] > McountryConsumer[country][ideWorker].ls - 0.001:
                            li = 0
                            break
                LdelMcountryJob.sort()
                shift = 0
                for posi in LdelMcountryJob:
                    correctPosition = posi - shift
                    del LdemandLabor[correctPosition]
                    shift = shift + 1
            for demandLabor in LdemandLabor:
                self.McountryDemandLabor[country].append(demandLabor)
            for supplyLabor in LsupplyLabor:
                self.McountrySupplyLabor[country].append(supplyLabor)

    def laborDisMatch(
        self,
        McountryFirm,
        McountryConsumer,
        McountryEtat,
        McountryBank,
        McountryCentralBank,
    ):
        for country in McountryFirm:
            for firm in McountryFirm[country]:
                McountryFirm[country][firm].l = 0
                McountryFirm[country][firm].laborExpenditure = 0
                McountryFirm[country][firm].innovationExpenditure = 0
            sumExpInnovation = 0
            for demand in self.McountryDemandLabor[country]:
                posFirm = demand[5]
                firmide = demand[0]
                McountryFirm[country][firmide].l = (
                    McountryFirm[country][firmide].l + demand[2]
                )
                McountryFirm[country][firmide].laborExpenditure = demand[4]  #
                wagebill = demand[4]
                AdispEffective = (
                    McountryFirm[country][firmide].lebalance.Aspending
                    + McountryFirm[country][firmide].loanReceived
                )
                resources = 0
                if (
                    AdispEffective
                    > McountryFirm[country][firmide].workForceExpenditureNoInnovation
                ):
                    resources = (
                        AdispEffective
                        - McountryFirm[country][
                            firmide
                        ].workForceExpenditureNoInnovation
                    )
                McountryFirm[country][firmide].innovationExpenditure = 0
                if McountryFirm[country][firmide].l > 0:
                    expenditureTotWorker = McountryFirm[country][
                        firmide
                    ].workForceInnovationExpenditureDesired * (
                        McountryFirm[country][firmide].l
                        / float(McountryFirm[country][firmide].nWorkerDesired)
                    )
                    McountryFirm[country][firmide].innovationExpenditure = min(
                        resources,
                        McountryFirm[country][
                            firmide
                        ].workForceInnovationExpenditureDesired,
                    )
                    McountryFirm[country][
                        firmide
                    ].innovationExpenditurePerWorker = McountryFirm[country][
                        firmide
                    ].innovationExpenditure / float(
                        McountryFirm[country][firmide].l
                    )
                sumExpInnovation = (
                    sumExpInnovation
                    + McountryFirm[country][firmide].innovationExpenditure
                )
                sumExpWorker = 0
                for worker in McountryFirm[country][firmide].Lemployed:
                    ideworker = worker[0]
                    laborworker = worker[1]
                    McountryConsumer[country][ideworker].innovationIncome = (
                        McountryConsumer[country][ideworker].innovationIncome
                        + McountryFirm[country][firmide].innovationExpenditurePerWorker
                        * laborworker
                    )
                    sumExpWorker = (
                        sumExpWorker
                        + McountryFirm[country][firmide].innovationExpenditurePerWorker
                        * laborworker
                    )
                    if McountryConsumer[country][ideworker].innovationIncome < -0.0001:
                        print("stop", stop)
                if (
                    sumExpWorker
                    > McountryFirm[country][firmide].innovationExpenditure + 0.001
                    or sumExpWorker
                    < McountryFirm[country][firmide].innovationExpenditure - 0.001
                ):
                    print("stop", stop)
                wagebill = (
                    McountryFirm[country][firmide].laborExpenditure
                    + McountryFirm[country][firmide].innovationExpenditure
                )
                McountryFirm[country][firmide].paying(
                    wagebill, McountryBank, McountryCentralBank
                )
            for supply in self.McountrySupplyLabor[country]:
                posConsumer = supply[3]
                ideConsumer = supply[2]
                if supply[2] != McountryConsumer[country][ideConsumer].ide:
                    print("stop", stop)
                McountryConsumer[country][ideConsumer].l = supply[4]
                McountryConsumer[country][ideConsumer].laborIncome = supply[5]
                if McountryConsumer[country][ideConsumer].l > 0.0:
                    wOffered = McountryConsumer[country][
                        ideConsumer
                    ].laborIncome / float(McountryConsumer[country][ideConsumer].l)
                    McountryConsumer[country][ideConsumer].wOffered = wOffered
                    McountryConsumer[country][ideConsumer].maxwOffered = max(
                        McountryConsumer[country][ideConsumer].LwOffered
                    )
                    McountryConsumer[country][ideConsumer].minwOffered = min(
                        McountryConsumer[country][ideConsumer].LwOffered
                    )
                    McountryConsumer[country][ideConsumer].minphip = min(
                        McountryConsumer[country][ideConsumer].Lphip
                    )
                    McountryConsumer[country][ideConsumer].averagewOffered = sum(
                        McountryConsumer[country][ideConsumer].LwOffered
                    ) / float(len(McountryConsumer[country][ideConsumer].LwOffered))
                if McountryConsumer[country][ideConsumer].l <= 0.0:
                    McountryConsumer[country][ideConsumer].wOffered = 0
                    McountryConsumer[country][ideConsumer].maxwOffered = 0
                    McountryConsumer[country][ideConsumer].averagewOffered = 0
                    McountryConsumer[country][ideConsumer].minwOffered = 0
                    McountryConsumer[country][ideConsumer].minphip = 0
                McountryConsumer[country][ideConsumer].laborIncome = (
                    McountryConsumer[country][ideConsumer].laborIncome
                    + McountryConsumer[country][ideConsumer].innovationIncome
                )
                McountryConsumer[country][ideConsumer].receiving(
                    McountryConsumer[country][ideConsumer].laborIncome,
                    McountryBank,
                    McountryCentralBank,
                )
