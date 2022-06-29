# basic date class

from copy import deepcopy

class Date_Error(Exception):
    message: str = 'Date Class Error'
    
    def __init__(self, m: str = 'Date Class Error'):
        self.message = m


class Date:
    month: int = 1
    year: int = 2000

    def __init__(self, y: int, m: int):
        self.month = 12 if m%12 == 0 else m%12
        self.year = y
        return None
    
    def __repr__(self):
        return str(self.year) + ', ' + str(self.month)

    def increment(self, months: int = 1):
        self.year += (self.month + months - 1)//12
        self.month = 1+(self.month-1+months)%12
        return self
    
    def __add__(self, months: int):
        _y = self.year + (self.month + months - 1)//12
        _m = 1+(self.month-1+months)%12
        
        return Date(_y, _m)
    
    def __eq__(self, other)->bool:
        if (self.month, self.year) == (other.month, other.year):
            return True
        return False
    
    def __gt__(self, other)->bool:
        if self.year > other.year: return True
        elif self.year < other.year: return False
        else:
            if self.month > other.month:
                return True
            

    
def project_date(start: Date, months: int)->Date:
    #determine what the ending month and year are given a start date and months passed
    new_Date = deepcopy(start)
    new_Date.increment(months = months)
    
    return new_Date


def months_differential(start: Date, end: Date)->int:
    #determin how many months after start date and end date occurs
    years = end.year - start.year
    months = (end.month - start.month)
    months += 12*years

    return months