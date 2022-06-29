#---------------------------------------------------------------------
###################################################################### imports
#---------------------------------------------------------------------

from math import sqrt, ceil
#import pandas as pd

#my classes
import Date_Class as dc
from Loan_Class import Loan_Container

#---------------------------------------------------------------------
###################################################################### global variables
#---------------------------------------------------------------------

all_loans_repayment_start_date = dc.Date(2022,10)

#loan terms are for 15 years, I'm assuming; therefore, 12*15 months
standard_payoff_date = all_loans_repayment_start_date + int(12*15 - 1)

student_loan_forgiveness_amount = 10000

#---------------------------------------------------------------------
###################################################################### data
#---------------------------------------------------------------------


#loans: 'name' : [balance, outstanding interest, APR, maturity_date]
#status for June, 2022
loans_dict = {
         'michelle - perkins':       [1138,
                                      0, 5.00, dc.Date(2025,2)],
         'chandler - federal unsub': [10314 - student_loan_forgiveness_amount,
                                      960, 4.66, standard_payoff_date],
         'michelle - federal unsub': [998,
                                      0, 4.5, standard_payoff_date],
         'chandler - citizens':      [79341,
                                      0, 4.37, dc.Date(2042,2)],
         'chandler - federal sub':   [13183,
                                      0, 0, standard_payoff_date],
         'michelle - federal sub':   [18601 - student_loan_forgiveness_amount,
                                      0, 0, standard_payoff_date]}


#---------------------------------------------------------------------
###################################################################### main()
#---------------------------------------------------------------------

def main():
    
    try:
        ############################################## set up
        start_date = dc.Date(2022,7)
        loans = Loan_Container(loans_dict, start_date)
        
        #sort by APR descending
        loans.loans.sort(key = lambda loan: loan.apr, reverse = True)
        
        #log = dict()
        months = 0
        
        starting_minimum_total_payment = loans.update_minimum_payments()
        
        ############################################### payments for jul, aug, sep
        
        #update balance for citizens loan and perkins loan as expected to be after payments
        #made in sept, 2022
        loans.loans[3].balance -= loans.loans[3].minimum_payment*3
        loans.loans[0].balance -= loans.loans[0].minimum_payment*3
        
        loans.increment_month(3)
        months += 3
        
        
        ############################################### payments for oct and beyond
        
        while(loans):
            
            #------------------------------------------------------------------
            #calculate interest
            loans.update_monthly_interest()
            
            #update minimum payments
            loans.update_minimum_payments()
            
            #display status
            print('MONTH: '+str(months)+' | '+str(loans.current_date)+'\n')
            print(loans)
            print('='*35+'\n')
            
            #append log - this records the status of a loan at the beginning of the month
            #log[loans.current_date] = copy.deepcopy(loans.__repr__())
            
            
            #------------------------------------------------------------------
            #make minimum payments
            loans.make_minimum_payments()
                
            #make additional payments
            payed_down_bonus = ceil(starting_minimum_total_payment) - int(loans.total_minimum_payment)
            pymnt = payed_down_bonus
            loans.make_extra_payments(pymnt)
            
            #compound any interest
            loans.compound_interests()
            
            #increment month
            months += 1
            loans.increment_month()
                
        
        payoff_date = start_date + months
        
        #display output
        print(loans.current_date)
        print('balance: ', round(sum([loan.balance for loan in loans])))
        print('your age: ', round(dc.months_differential(dc.Date(1995,10), payoff_date)/12, 1))
        print('michelle\'s age: ', round(dc.months_differential(dc.Date(1997,11), payoff_date)/12,1))
        print('ideal savings: ', int(sqrt(300*900)*months))
        
        #df = pd.DataFrame(log).transpose()
        #df.to_csv("output.csv")
        
        return 0
    
    except dc.Date_Error as de:
        print(de.message)
        return 1
        
    except Exception as e:
        print(e)
        return 2

#---------------------------------------------------------------------
######################################################################  call main()
#---------------------------------------------------------------------

main()



