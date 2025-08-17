import numpy as np
import pandas as pd
from typing import List, Dict, Optional

class LoanCalculator:
    """
    A comprehensive loan calculator class for EMI calculation and amortization schedule generation.
    Supports prepayment strategies including monthly and quarterly prepayments.
    """
    
    def __init__(self, loan_amount: float, annual_rate: float, tenure_years: int):
        """
        Initialize the loan calculator with basic loan parameters.
        
        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate as percentage (e.g., 8.5 for 8.5%)
            tenure_years: Loan tenure in years
        """
        self.loan_amount = loan_amount
        self.annual_rate = annual_rate
        self.tenure_years = tenure_years
        self.monthly_rate = annual_rate / 100 / 12
        self.tenure_months = tenure_years * 12
        
        # Calculate EMI using standard formula
        self.emi = self._calculate_emi()
    
    def _calculate_emi(self) -> float:
        """
        Calculate the Equated Monthly Installment (EMI) using the standard formula:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        
        Returns:
            Monthly EMI amount
        """
        if self.monthly_rate == 0:
            return self.loan_amount / self.tenure_months
        
        numerator = self.loan_amount * self.monthly_rate * (1 + self.monthly_rate) ** self.tenure_months
        denominator = (1 + self.monthly_rate) ** self.tenure_months - 1
        
        return numerator / denominator
    
    def generate_amortization_schedule(self, 
                                     monthly_prepayment: float = 0,
                                     quarterly_prepayment: float = 0,
                                     max_months: int = None) -> List[Dict]:
        """
        Generate a detailed amortization schedule with optional prepayments.
        
        Args:
            monthly_prepayment: Additional monthly payment towards principal
            quarterly_prepayment: Additional quarterly payment towards principal
            max_months: Maximum number of months to simulate (None for full tenure)
            
        Returns:
            List of dictionaries containing monthly payment details
        """
        schedule = []
        outstanding_balance = self.loan_amount
        max_months = max_months or self.tenure_months
        
        for month in range(1, max_months + 1):
            if outstanding_balance <= 0:
                break
            
            # Calculate interest for current month
            monthly_interest = outstanding_balance * self.monthly_rate
            
            # Calculate principal component of EMI
            monthly_principal = self.emi - monthly_interest
            
            # Ensure principal doesn't exceed outstanding balance
            if monthly_principal > outstanding_balance:
                monthly_principal = outstanding_balance
                monthly_interest = self.emi - monthly_principal
            
            # Apply prepayments
            current_monthly_prepayment = monthly_prepayment
            current_quarterly_prepayment = quarterly_prepayment if month % 3 == 0 else 0
            
            total_prepayment = current_monthly_prepayment + current_quarterly_prepayment
            
            # Ensure prepayments don't exceed outstanding balance
            if total_prepayment > outstanding_balance - monthly_principal:
                total_prepayment = max(0, outstanding_balance - monthly_principal)
                current_monthly_prepayment = total_prepayment
                current_quarterly_prepayment = 0
            
            # Update outstanding balance
            outstanding_balance -= (monthly_principal + total_prepayment)
            outstanding_balance = max(0, outstanding_balance)  # Ensure non-negative
            
            # Calculate total payment for the month
            total_monthly_payment = monthly_interest + monthly_principal + total_prepayment
            
            # Add to schedule
            schedule.append({
                "Month": month,
                "Interest Paid": round(monthly_interest, 2),
                "Principal Paid": round(monthly_principal, 2),
                "Monthly Prepayment": round(current_monthly_prepayment, 2),
                "Quarterly Prepayment": round(current_quarterly_prepayment, 2),
                "Total Payment": round(total_monthly_payment, 2),
                "Outstanding Balance": round(outstanding_balance, 2)
            })
            
            # Break if loan is fully paid
            if outstanding_balance <= 0:
                break
        
        return schedule
    
    def calculate_total_interest(self, schedule: List[Dict]) -> float:
        """
        Calculate total interest paid over the loan duration.
        
        Args:
            schedule: Amortization schedule list
            
        Returns:
            Total interest paid
        """
        return sum(month['Interest Paid'] for month in schedule)
    
    def calculate_total_payments(self, schedule: List[Dict]) -> float:
        """
        Calculate total payments made over the loan duration.
        
        Args:
            schedule: Amortization schedule list
            
        Returns:
            Total payments made
        """
        return sum(month['Total Payment'] for month in schedule)
    
    def calculate_interest_savings(self, 
                                 schedule_with_prepayments: List[Dict],
                                 schedule_without_prepayments: List[Dict]) -> Dict:
        """
        Calculate interest and time savings from prepayments.
        
        Args:
            schedule_with_prepayments: Schedule with prepayment strategy
            schedule_without_prepayments: Schedule without prepayments
            
        Returns:
            Dictionary containing savings analysis
        """
        interest_with_prepay = self.calculate_total_interest(schedule_with_prepayments)
        interest_without_prepay = self.calculate_total_interest(schedule_without_prepayments)
        
        months_with_prepay = len(schedule_with_prepayments)
        months_without_prepay = len(schedule_without_prepayments)
        
        return {
            "interest_savings": interest_without_prepay - interest_with_prepay,
            "time_savings_months": months_without_prepay - months_with_prepay,
            "time_savings_years": (months_without_prepay - months_with_prepay) / 12,
            "total_prepayments": sum(
                month['Monthly Prepayment'] + month['Quarterly Prepayment'] 
                for month in schedule_with_prepayments
            )
        }
    
    def get_loan_summary(self) -> Dict:
        """
        Get a summary of loan parameters and calculated values.
        
        Returns:
            Dictionary containing loan summary
        """
        return {
            "loan_amount": self.loan_amount,
            "annual_rate": self.annual_rate,
            "tenure_years": self.tenure_years,
            "tenure_months": self.tenure_months,
            "monthly_rate": self.monthly_rate,
            "emi": self.emi
        }
    
    def validate_inputs(self) -> List[str]:
        """
        Validate loan calculator inputs and return any error messages.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if self.loan_amount <= 0:
            errors.append("Loan amount must be greater than zero")
        
        if self.annual_rate < 0 or self.annual_rate > 50:
            errors.append("Annual interest rate must be between 0% and 50%")
        
        if self.tenure_years <= 0 or self.tenure_years > 50:
            errors.append("Loan tenure must be between 1 and 50 years")
        
        return errors
