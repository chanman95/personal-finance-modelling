#---------------------------------------------------------------------
###################################################################### imports
#---------------------------------------------------------------------

import datetime
from datetime import date
from typing import List, Dict
import copy
import pandas as pd
import numpy as np

#---------------------------------------------------------------------
###################################################################### global variables
#---------------------------------------------------------------------

standard_payoff_date = date(2022,10,1) + datetime.timedelta(weeks = 52*15)
student_loan_forgiveness_amount = 10000


#---------------------------------------------------------------------
###################################################################### data
#---------------------------------------------------------------------


#loans: 'name' : [balance, outstanding interest, APR, maturity_date]
loans_dict = {
         'michelle - perkins':       [1138, 0, 5.00, date(2025,2,1)],
         'chandler - federal unsub': [10314 - student_loan_forgiveness_amount, 960, 4.66, standard_payoff_date],
         'michelle - federal unsub': [998, 0, 4.5, standard_payoff_date],
         'chandler - citizens':      [79341, 0, 4.37, date(2042,2,18)],
         'chandler - federal sub':   [13183, 0, 0, standard_payoff_date],
         'michelle - federal sub':   [18601 - student_loan_forgiveness_amount, 0, 0, standard_payoff_date]}

#---------------------------------------------------------------------
###################################################################### classes
#---------------------------------------------------------------------
class Loan:
    #static
    payed_off: bool = False
    balance: float = 0
    interest: float = 0
    apr: float = 0
    maturity_date: datetime.date = date.min
    
    #dynamic
    minimum_payment: float = 1000

    #methods
    def __init__(self, b, i, apr, m_d):
        self.balance = b
        self.interest = i
        self.apr = apr
        self.maturity_date = m_d
        return None

    def __repr__(self):
        return 'loan: '+ str(self.balance) + '\ninterest: ' + str(self.interest) + '\napr:' + str(
            self.apr) + '\nmin_payment: ' + str(self.minimum_payment) + '\nmdate: ' + str(self.maturity_date)
    
    def update_minimum_payment(self, current_date: date):
        self.minimum_payment = monthly_payment(self.balance, self.interest,
                                               self.apr, current_date,
                                               self.maturity_date,
                                               guess_payment = self.minimum_payment)
        return None
    
    def update_interest(self):
        self.interest += self.balance * (self.apr/100/12)
        return None
    
    def compound_interest(self):
        self.balance += self.interest
        self.interest = 0
        return None
    
    def make_payment(self, payment: float):
        #make payment towards interest, balance; return leftover amount if any
        if payment < 0: raise Exception('payment attempt less than zero: ' + str(payment))
        
        if payment >= (self.balance + self.interest):
            payment -= (self.balance + self.interest)
            self.balance = 0
            self.interest = 0
            self.payed_off = True
            return payment
            
        else:
            if payment >= self.interest:
                payment -= self.interest
                self.interest = 0
                self.balance -= payment
                return 0
            else:
                self.interest -= payment
                return 0
            
            

class Loan_Container:
    loans: List[Loan] = []
    
    total_minimum_payment: float = 0

    def __init__(self, loans_dict: Dict):
        for loan in loans_dict.values():
            self.loans.append(Loan(*loan))
            
    def update_minimum_payments(self, current_date: date):
        self.total_minimum_payment = 0
        for loan in self.loans:
            if loan.payed_off: continue
            loan.update_minimum_payment(current_date)
            self.total_minimum_payment += loan.minimum_payment
        return self.total_minimum_payment
            
    def __iter__(self):
        return iter(self.loans)
    
    def update_monthly_interest(self):
        for loan in self.loans:
            if loan.payed_off: continue
            loan.update_interest()
            
    def compound_interests(self):
        for loan in self.loans:
            if loan.payed_off: continue
            loan.compound_interest()
    def __repr__(self):
        return [(round(loan.balance), loan.apr) for loan in self.loans]
            
    
#---------------------------------------------------------------------
###################################################################### helper functions
#---------------------------------------------------------------------

def still_loans(loans: Loan_Container)->bool:
    #are all the loans payed off yet??
    for loan in loans:
        loan.payed_off = not(loan.balance > 0.0 or loan.interest > 0.0)
    for loan in loans:
        if not loan.payed_off:
            return True
    return False
    

######################################

def calc_interest(balance: float, apr: float)->float:
    #simple calculation for now
    return balance * ( (apr/100.0)/12 )


####################################

def monthly_payment(balance: float, interest: float,
                    apr: float, current_date: date,
                    maturity_date: date, guess_payment: float = 500)->float:
    #determine the minimum monthly payment such that the loan will be paid
    #off by the maturity date given that minimum
    if current_date > maturity_date: raise Exception('problem in monthly payment')
    
    remaining_months = int((maturity_date - current_date).days//30)
    
    minimum_payment = guess_payment
    while(remaining_months != how_many_months(balance, interest, apr, minimum_payment)):
        
        if  how_many_months(balance, interest, apr, minimum_payment) > remaining_months:
            minimum_payment *= 1.0001
        else:
            minimum_payment *= 0.9999
            
        if minimum_payment > 100000:
            raise Exception('payments problem, minimum payment: ' + str(minimum_payment))

    return minimum_payment


def how_many_months(balance: float,
                    interest: float, apr: float, monthly_pymnt: float)->int:
    #helper to monthly_payment - determines how many months would be needed for payoff
    months: int = 0
    balance += interest
    
    while(balance > 0):
        months += 1
        payment = monthly_pymnt
        payment -= calc_interest(balance, apr)
        balance -= payment
    
    return int(months)


#---------------------------------------------------------------------
###################################################################### main()
#---------------------------------------------------------------------

def main():
    try:
        
        loans = Loan_Container(loans_dict)
        
        #sort by APR descending
        loans.loans.sort(key = lambda loan: loan.apr, reverse = True)
        
        #log = dict()
        
        ################################################
        current_date = start_date = date(2022,10,1) #start date for loop
        
        #update balance for citizens loan and perkins loan as expected to be in October, 2022
        loans.loans[3].balance -= 500*3
        loans.loans[0].balance -= 40*3
        
        ################################################
        excess_payment = 100
        starting_minimum_total_payment = loans.update_minimum_payments(current_date)
        ################################################
        
        #update minimum payment
        #calculate and add interest to current interest balance
        #make minimum payments on all loans
            #towards interest first
            #then balance
        #make excess payments
            #towards outstanding interest first
            #then towards balance in order of APR
        #compound any left over interest
        
        months = 0
        while(still_loans(loans) and current_date < date(2029,6,1)):
            months += 1
            current_date += datetime.timedelta(days = 364.24/12)
            
            if months%(12*2) == 0: excess_payment *= 1.75
            
            #-------------
            loans.update_minimum_payments(current_date)
            loans.update_monthly_interest()
            
            #make minimum payments
            for loan in loans:
                if loan.payed_off: continue
                loan.make_payment(loan.minimum_payment)
            
            #make excess payments
            pymnt = excess_payment
            #use money freed up from paying off other loans to payoff remaining loans
            pymnt += round(starting_minimum_total_payment - loans.total_minimum_payment)

            for loan in loans:
                if loan.payed_off: continue
                pymnt = loan.make_payment(pymnt)
            
            #compound any interest - shouldn't be any though
            loans.compound_interests()
            
            #log[current_date] = copy.deepcopy(loans.__repr__())
                
        
        payoff_date = start_date + datetime.timedelta(days=30.437*months)
        
        print(payoff_date)
        print(sum([loan.balance for loan in loans]))
        print('your age: ', round( (payoff_date - date(1995,10,14)).days/365.24 ))
        print('michelle\'s age: ', round( (payoff_date - date(1997,11,28,)).days/365.24 ))
        print('ideal savings: ', 750*months)
        
        #df = pd.DataFrame(log).transpose()
        #df.to_csv("output.csv")
        
        return 0
    
        
    except Exception as e:
        print(e)
        return 1


#---------------------------------------------------------------------
######################################################################  call main()
#---------------------------------------------------------------------

main()











    
    
    
    
    
    
    
    
    
    

