#Loan class and container with helper functions


import Date_Class as dc
from typing import List, Dict
from math import ceil

#---------------------------------------------------------------------
###################################################################### classes
#---------------------------------------------------------------------

class Loan:
    #static
    payed_off: bool = False
    balance: float = 0
    interest: float = 0
    apr: float = 0
    maturity_date: dc.Date = dc.Date(1900,1)
    
    #dynamic
    minimum_payment: float = 1000

    #methods
    def __init__(self, b, i, apr, m_d)->None:
        self.balance = b
        self.interest = i
        self.apr = apr
        self.maturity_date = m_d
        return None

    def __repr__(self)->str:
        return 'loan: '+ str(self.balance) + '\ninterest: ' + str(self.interest) + '\napr:' + str(
            self.apr) + '\nmin_payment: ' + str(self.minimum_payment) + '\nmdate: ' + str(self.maturity_date) + '\n'
    
    def update_minimum_payment(self, current_date: dc.Date)->None:
        self.minimum_payment = monthly_payment(self.balance,
                                               self.interest,
                                               self.apr,
                                               current_date,
                                               self.maturity_date)
        return None
    
    def update_interest(self)->None:
        self.interest += self.balance * (self.apr/100/12)
        return None
    
    def compound_interest(self)->None:
        self.balance += self.interest
        self.interest = 0
        return None
    
    def make_payment(self, payment: float)->float:
        #make payment towards interest, balance; return leftover amount if any
        
        if payment < 0: raise Exception('payment attempt less than zero: ' + str(payment))
        
        if payment >= (self.balance + self.interest):
            payment -= (self.balance + self.interest)
            self.balance = 0
            self.interest = 0
            self.payed_off = True
            return payment
            
        else:
            if payment <= self.interest:
                self.interest -= payment
            else:
                payment -= self.interest
                self.interest = 0
                self.balance -= payment
            return 0.0
            

class Loan_Container:
    loans: List[Loan] = []
    
    total_minimum_payment: float = 0
    current_date: dc.Date

    def __init__(self, loans_dict: Dict, date: dc.Date)->None:
        for loan in loans_dict.values(): self.loans.append(Loan(*loan))
        self.current_date = date
        return None
            
    def update_minimum_payments(self)->float:
        self.total_minimum_payment = 0
        
        for loan in self.loans:
            if loan.payed_off: continue
            loan.update_minimum_payment(self.current_date)
            self.total_minimum_payment += loan.minimum_payment
            
        return self.total_minimum_payment
            
    def __iter__(self)->iter:
        return iter(self.loans)
    
    def update_monthly_interest(self)->None:
        for loan in self.loans:
            if loan.payed_off: continue
            loan.update_interest()
        
        return None
    
    def make_minimum_payments(self)->None:
        for loan in self.loans:
            if loan.payed_off: continue
            loan.make_payment(loan.minimum_payment)
        return None
            
    def compound_interests(self)->None:
        for loan in self.loans:
            if loan.payed_off: continue
            loan.compound_interest()
        return None
    
    def __repr__(self)->List:
        st = str(self.current_date)+'\n'
        for loan in self.loans:
            st += str(loan)+'\n'
        return st
    
    def increment_month(self, months: int = 1)->None:
        self.current_date += months
        return None
    
    def make_extra_payments(self, payment: float)->None:
        pymnt = payment
        for loan in self.loans:
            if loan.payed_off: continue
            pymnt = loan.make_payment(pymnt)
            
    def still_loans(self)->bool:
        #are all the loans payed off yet??
        for loan in self.loans:
            loan.payed_off = not(loan.balance > 0.0 or loan.interest > 0.0)
        for loan in self.loans:
            if not loan.payed_off:
                return True
        return False
    
    def __bool__(self)->bool:
        return self.still_loans()
        
            
    
#---------------------------------------------------------------------
###################################################################### helper functions
#---------------------------------------------------------------------


def monthly_payment(balance: float, interest: float,
                    apr: float, current_date: dc.Date,
                    maturity_date: dc.Date, end_balance: float = 0)->float:
    #determine the minimum monthly payment such that the loan will be paid
    #off by the maturity date given that minimum
    
    if current_date > maturity_date:
        raise Exception('maturity date passed in monthly_payment(): '+str(current_date))
    
    balance += interest #add any interest to be compounded
    
    remaining_months = dc.months_differential(current_date, maturity_date)+1 #plus 1 because a payment will be made in that month
    
    if remaining_months == 1: #if youre on the final month, pay the balance
        return ceil(balance - end_balance)
    
    else:
        if apr == 0:
            return ceil((balance-end_balance)/remaining_months)
        
        elif apr > 0:
            rate = apr/100.0/12.0
            
            numerator = rate * end_balance - balance*pow(1+rate,remaining_months)*rate
            denominator = 1 - pow(1+rate,remaining_months)
            
            if denominator == 0: raise Exception('zero denominator in monthly_payment()')
            return ceil(numerator/denominator)
        
        else:
            raise Exception('APR less than zero in monthly_payment()')
            
