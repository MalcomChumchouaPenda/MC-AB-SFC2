# policy.py

import random
import math

class policy:
      def __init__(self,timeStarting,policyKind,maxPublicDeficitAusterity,\
                   maxPublicDeficit):
          self.timeStarting=timeStarting
          self.policyKind=policyKind
          self.maxPublicDeficit=maxPublicDeficit 
          self.maxPublicDeficitAusterity=maxPublicDeficitAusterity

      def implementingPolicy(self,time,McountryEtat,McountryY,DglobalPhi,DcountryAvWage,McountryAvPrice,McountryUnemployement,\
                             DcumulativeDTBC,DcountryTradeBalance):
          self.policy='no' 
          if time>=self.timeStarting:
             LwageOnPhi=[]     
             Lphi=[]
             LY=[]  
             Ldebt=[]
             for country in McountryEtat:         
                 wageOnPhi=DcountryAvWage[country]/float(DglobalPhi[country])
                 LwageOnPhi.append(wageOnPhi)
                 Lphi.append(DglobalPhi[country]) 
                 LY.append(McountryY[country])
                 Ldebt.append(McountryEtat[country].Bonds)
             avWageOnPhi=sum(LwageOnPhi)/float(len(LwageOnPhi))
             avPhi=sum(Lphi)/float(len(Lphi))
             avY=sum(LY)/float(len(LY))
             avDebt=sum(Ldebt)/float(len(Ldebt))
             self.policy=self.policyKind                                        
             if self.policy=='austerity': 
                for country in McountryEtat: 
                    Lreturn=self.austerityPolicy(McountryY[country],McountryEtat[country].pastTaxCollected,\
                                McountryEtat[country].interestExpenditure,McountryEtat[country].addingSurplus,McountryEtat[country].G,\
                                McountryEtat[country].delta,McountryEtat[country].taxRate,DcountryAvWage[country],\
                                DglobalPhi[country],avWageOnPhi,McountryEtat[country].initialG,\
                                McountryAvPrice[country],McountryEtat[country].Bonds,avPhi,avY,\
                                McountryUnemployement[country],avDebt,McountryEtat[country].publicDeficit,DcumulativeDTBC[country],\
                                DcountryTradeBalance[country])  
                    McountryEtat[country].adjust=Lreturn[0] 
                    McountryEtat[country].realG=Lreturn[1]
                    McountryEtat[country].followingTaxRate=Lreturn[2] 
                    McountryEtat[country].G=Lreturn[1]              
           
           
      def austerityPolicy(self,Y,pastTaxCollected,interestExpenditure,addingSurplus,G,delta,taxRate,wage,phi,\
                                 avWageOnPhi,initialG,price,debt,avPhi,avY,U,avDebt,publicDeficit,cumulativeDTBC,TradeBalance):
          adjust='no' 
          realG=G
          if self.policy=='austerity' and  Y>0:
                desiredG=min(price*phi*initialG,0.6*Y)
                desiredG=max(desiredG,0.4*Y) 
                expectedDeficit=publicDeficit/float(Y)
                maxPublicDeficit=self.maxPublicDeficitAusterity              
                if desiredG<=G and expectedDeficit>=maxPublicDeficit:
                   realG=G*(1-random.uniform(0,delta))
                   followingTaxRate=taxRate*(1+random.uniform(0,delta))
                if desiredG>G and expectedDeficit>=maxPublicDeficit:
                   realG=G
                   followingTaxRate=taxRate*(1+random.uniform(0,delta))
                if desiredG<=G and expectedDeficit<maxPublicDeficit:
                   realG=G*(1-random.uniform(0,delta))
                   followingTaxRate=taxRate*(1-random.uniform(0,delta))
                if desiredG>G and expectedDeficit<maxPublicDeficit:
                   realG=G*(1+random.uniform(0,delta))
                   followingTaxRate=taxRate
                adjust='yes'   
          Lreturn=[adjust,realG,followingTaxRate]        
          return Lreturn 

     

    
