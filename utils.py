import pandas as pd
import numpy as np
from typing import List, Dict, Union
import io

def format_currency(amount: float, currency_symbol: str = "₹") -> str:
    """
    Format a number as currency with Indian numbering system.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
        
    Returns:
        Formatted currency string
    """
    if amount == 0:
        return f"{currency_symbol}0"
    
    # Handle negative amounts
    is_negative = amount < 0
    amount = abs(amount)
    
    # Convert to string and add commas (Indian system)
    if amount >= 10000000:  # 1 crore
        formatted = f"{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        formatted = f"{amount/100000:.2f} L"
    else:
        formatted = f"{amount:,.0f}"
    
    result = f"{currency_symbol}{formatted}"
    
    if is_negative:
        result = f"-{result}"
        
    return result

def calculate_interest_savings(schedule_with_prepay: List[Dict], 
                             schedule_without_prepay: List[Dict]) -> Dict:
    """
    Calculate comprehensive savings from prepayment strategy.
    
    Args:
        schedule_with_prepay: Amortization schedule with prepayments
        schedule_without_prepay: Amortization schedule without prepayments
        
    Returns:
        Dictionary containing detailed savings analysis
    """
    # Calculate totals
    total_interest_with = sum(month['Interest Paid'] for month in schedule_with_prepay)
    total_interest_without = sum(month['Interest Paid'] for month in schedule_without_prepay)
    
    total_prepayments = sum(
        month['Monthly Prepayment'] + month['Quarterly Prepayment'] 
        for month in schedule_with_prepay
    )
    
    # Time savings
    months_with = len(schedule_with_prepay)
    months_without = len(schedule_without_prepay)
    months_saved = months_without - months_with
    
    # Calculate effective savings rate
    interest_saved = total_interest_without - total_interest_with
    effective_savings_rate = (interest_saved / total_prepayments) * 100 if total_prepayments > 0 else 0
    
    return {
        'interest_saved': interest_saved,
        'months_saved': months_saved,
        'years_saved': months_saved / 12,
        'total_prepayments': total_prepayments,
        'effective_savings_rate': effective_savings_rate,
        'total_interest_with_prepay': total_interest_with,
        'total_interest_without_prepay': total_interest_without
    }

def export_to_csv(schedule_df: pd.DataFrame) -> str:
    """
    Export amortization schedule to CSV format.
    
    Args:
        schedule_df: DataFrame containing amortization schedule
        
    Returns:
        CSV data as string
    """
    # Create a copy for export
    export_df = schedule_df.copy()
    
    # Add calculated columns for better analysis
    export_df['Cumulative Interest'] = export_df['Interest Paid'].cumsum()
    export_df['Cumulative Principal'] = export_df['Principal Paid'].cumsum()
    export_df['Cumulative Prepayments'] = (
        export_df['Monthly Prepayment'] + export_df['Quarterly Prepayment']
    ).cumsum()
    
    # Round all numeric columns
    numeric_columns = export_df.select_dtypes(include=[np.number]).columns
    export_df[numeric_columns] = export_df[numeric_columns].round(2)
    
    # Convert to CSV
    output = io.StringIO()
    export_df.to_csv(output, index=False)
    return output.getvalue()

def validate_prepayment_inputs(monthly_prepayment: float, 
                              quarterly_prepayment: float,
                              emi: float) -> List[str]:
    """
    Validate prepayment input parameters.
    
    Args:
        monthly_prepayment: Monthly prepayment amount
        quarterly_prepayment: Quarterly prepayment amount
        emi: Monthly EMI amount
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if monthly_prepayment < 0:
        errors.append("Monthly prepayment cannot be negative")
    
    if quarterly_prepayment < 0:
        errors.append("Quarterly prepayment cannot be negative")
    
    if monthly_prepayment > emi * 10:
        errors.append("Monthly prepayment seems unusually high compared to EMI")
    
    if quarterly_prepayment > emi * 50:
        errors.append("Quarterly prepayment seems unusually high compared to EMI")
    
    return errors

def calculate_loan_metrics(schedule: List[Dict], loan_amount: float) -> Dict:
    """
    Calculate comprehensive loan metrics from amortization schedule.
    
    Args:
        schedule: Amortization schedule
        loan_amount: Original loan amount
        
    Returns:
        Dictionary containing loan metrics
    """
    df = pd.DataFrame(schedule)
    
    total_interest = df['Interest Paid'].sum()
    total_principal = df['Principal Paid'].sum()
    total_prepayments = (df['Monthly Prepayment'] + df['Quarterly Prepayment']).sum()
    total_payments = df['Total Payment'].sum()
    
    # Calculate average monthly payment
    avg_monthly_payment = df['Total Payment'].mean()
    
    # Calculate interest as percentage of loan amount
    interest_percentage = (total_interest / loan_amount) * 100
    
    # Calculate month when loan is 50% paid
    cumulative_principal = df['Principal Paid'].cumsum()
    halfway_month = None
    for idx, cum_principal in enumerate(cumulative_principal):
        if cum_principal >= loan_amount * 0.5:
            halfway_month = idx + 1
            break
    
    return {
        'total_interest': total_interest,
        'total_principal': total_principal,
        'total_prepayments': total_prepayments,
        'total_payments': total_payments,
        'avg_monthly_payment': avg_monthly_payment,
        'interest_percentage': interest_percentage,
        'loan_duration_months': len(schedule),
        'loan_duration_years': len(schedule) / 12,
        'halfway_point_month': halfway_month
    }

def generate_payment_summary(schedule: List[Dict]) -> Dict:
    """
    Generate a summary of payment patterns from the schedule.
    
    Args:
        schedule: Amortization schedule
        
    Returns:
        Dictionary containing payment summary statistics
    """
    df = pd.DataFrame(schedule)
    
    # Monthly statistics
    monthly_stats = {
        'avg_interest': df['Interest Paid'].mean(),
        'avg_principal': df['Principal Paid'].mean(),
        'avg_prepayment': (df['Monthly Prepayment'] + df['Quarterly Prepayment']).mean(),
        'max_interest': df['Interest Paid'].max(),
        'min_interest': df['Interest Paid'].min(),
        'max_principal': df['Principal Paid'].max(),
        'min_principal': df['Principal Paid'].min()
    }
    
    # Yearly aggregation
    df['Year'] = ((df['Month'] - 1) // 12) + 1
    yearly_stats = df.groupby('Year').agg({
        'Interest Paid': 'sum',
        'Principal Paid': 'sum',
        'Monthly Prepayment': 'sum',
        'Quarterly Prepayment': 'sum',
        'Total Payment': 'sum'
    }).to_dict(orient='index')
    
    return {
        'monthly_stats': monthly_stats,
        'yearly_breakdown': yearly_stats
    }

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a decimal value as a percentage.
    
    Args:
        value: Decimal value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"

def format_time_period(months: int) -> str:
    """
    Format months into a readable time period string.
    
    Args:
        months: Number of months
        
    Returns:
        Formatted time period string
    """
    if months < 12:
        return f"{months} months"
    
    years = months // 12
    remaining_months = months % 12
    
    if remaining_months == 0:
        return f"{years} years"
    else:
        return f"{years} years {remaining_months} months"

def calculate_compound_interest(principal: float, rate: float, time: float, 
                               compound_frequency: int = 12) -> float:
    """
    Calculate compound interest.
    
    Args:
        principal: Initial principal amount
        rate: Annual interest rate (as decimal)
        time: Time in years
        compound_frequency: Compounding frequency per year
        
    Returns:
        Final amount after compound interest
    """
    return principal * (1 + rate/compound_frequency) ** (compound_frequency * time)

def validate_payment_data(df: pd.DataFrame) -> List[str]:
    """
    Validate uploaded payment history data.
    
    Args:
        df: DataFrame containing payment history
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check required columns
    required_columns = ['amount_paid', 'month']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    if len(errors) == 0:  # Only proceed if required columns exist
        # Check for negative amounts
        if df['amount_paid'].lt(0).any():
            errors.append("Payment amounts cannot be negative")
        
        # Check for duplicate months
        if df['month'].duplicated().any():
            errors.append("Duplicate months found in the data")
        
        # Check for missing values
        if df['amount_paid'].isna().any():
            errors.append("Missing payment amounts found")
        
        if df['month'].isna().any():
            errors.append("Missing month values found")
    
    return errors

def analyze_payment_history(payment_df: pd.DataFrame, loan_amount: float, 
                          annual_rate: float, emi: float) -> Dict:
    """
    Analyze payment history against expected loan schedule.
    
    Args:
        payment_df: DataFrame with payment history
        loan_amount: Original loan amount
        annual_rate: Annual interest rate
        emi: Monthly EMI amount
        
    Returns:
        Dictionary containing comprehensive payment analysis
    """
    # Sort by month
    payment_df = payment_df.sort_values('month').reset_index(drop=True)
    
    monthly_rate = annual_rate / 100 / 12
    current_balance = loan_amount
    analysis_results = []
    
    # Calculate expected vs actual payments
    total_paid = 0
    total_interest_paid = 0
    total_principal_paid = 0
    total_overpayment = 0
    
    for idx, row in payment_df.iterrows():
        month = row['month']
        amount_paid = row['amount_paid']
        
        # Calculate expected interest for this month
        expected_interest = current_balance * monthly_rate
        expected_principal = emi - expected_interest
        
        # Actual breakdown (assuming payment first goes to interest, then principal)
        actual_interest = min(float(amount_paid), expected_interest)
        actual_principal = amount_paid - actual_interest
        
        # Calculate overpayment (amount beyond EMI)
        overpayment = max(0, amount_paid - emi)
        
        # Update running totals
        total_paid += amount_paid
        total_interest_paid += actual_interest
        total_principal_paid += actual_principal
        total_overpayment += overpayment
        
        # Update balance
        current_balance -= actual_principal
        current_balance = max(0.0, current_balance)
        
        analysis_results.append({
            'month': month,
            'amount_paid': amount_paid,
            'expected_emi': emi,
            'expected_interest': expected_interest,
            'expected_principal': expected_principal,
            'actual_interest': actual_interest,
            'actual_principal': actual_principal,
            'overpayment': overpayment,
            'remaining_balance': current_balance
        })
    
    # Calculate summary metrics
    last_month = payment_df['month'].max()
    months_completed = len(payment_df)
    
    # Project remaining loan details
    if current_balance > 0:
        # Calculate remaining months if continuing with EMI
        remaining_months = np.ceil(np.log(1 + (current_balance * monthly_rate) / emi) / 
                                 np.log(1 + monthly_rate)) if monthly_rate > 0 else current_balance / emi
        remaining_months = max(0, remaining_months)
    else:
        remaining_months = 0
    
    # Calculate interest savings from overpayments
    expected_interest_final = current_balance * monthly_rate if current_balance > 0 else 0
    original_total_interest = (emi * (loan_amount / emi * (1 + monthly_rate)**np.ceil(loan_amount / emi)) - loan_amount)
    estimated_interest_savings = original_total_interest - total_interest_paid - (remaining_months * expected_interest_final)
    
    return {
        'payment_summary': {
            'total_paid': total_paid,
            'total_interest_paid': total_interest_paid,
            'total_principal_paid': total_principal_paid,
            'total_overpayment': total_overpayment,
            'months_completed': months_completed,
            'last_payment_month': last_month
        },
        'loan_status': {
            'remaining_balance': current_balance,
            'remaining_months': remaining_months,
            'estimated_interest_savings': estimated_interest_savings,
            'loan_completion_percentage': (total_principal_paid / loan_amount) * 100
        },
        'monthly_breakdown': analysis_results,
        'recommendations': generate_payment_recommendations(
            current_balance, remaining_months, emi, total_overpayment, months_completed
        )
    }

def generate_payment_recommendations(remaining_balance: float, remaining_months: float,
                                   emi: float, total_overpayment: float, 
                                   months_completed: int) -> List[str]:
    """
    Generate personalized payment recommendations based on payment history.
    
    Args:
        remaining_balance: Current outstanding balance
        remaining_months: Estimated remaining months
        emi: Monthly EMI
        total_overpayment: Total overpayments made so far
        months_completed: Number of months completed
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    if remaining_balance <= 0:
        recommendations.append("🎉 Congratulations! Your loan is fully paid off!")
        return recommendations
    
    # Calculate average overpayment per month
    avg_overpayment = total_overpayment / months_completed if months_completed > 0 else 0
    
    if avg_overpayment > 0:
        recommendations.append(f"📈 Great job! You've been making overpayments averaging ₹{avg_overpayment:,.0f} per month")
        
        # Calculate impact of continuing current overpayment strategy
        if avg_overpayment > emi * 0.1:  # Significant overpayment (>10% of EMI)
            time_saved = remaining_months * 0.15  # Rough estimate
            recommendations.append(f"⏰ Continue your current strategy to save approximately {time_saved:.0f} more months")
    else:
        recommendations.append("💡 Consider making small overpayments to reduce interest and loan duration")
    
    # Balance-based recommendations
    if remaining_balance > emi * 60:  # More than 5 years remaining
        recommendations.append("🎯 Focus on consistent overpayments - even ₹5,000 extra monthly can save significant interest")
    elif remaining_balance > emi * 24:  # 2-5 years remaining
        recommendations.append("🏃‍♂️ You're in the home stretch! Consider larger prepayments to finish strong")
    else:  # Less than 2 years remaining
        recommendations.append("🏁 Final sprint! Consider paying off the remaining balance in lump sum if possible")
    
    # Payment frequency recommendations
    if months_completed >= 6:
        payment_consistency = len([1 for month in range(1, months_completed + 1) 
                                 if month in [row['month'] for row in []]])  # Placeholder logic
        if payment_consistency < 0.8:
            recommendations.append("📅 Try to maintain consistent monthly payments for better loan management")
    
    return recommendations
