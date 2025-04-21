import pandas as pd

def calculate_budget(income, expenses, total_min_debt):
    """
    Calculate budget breakdown based on income, expenses, and debt.
    
    Parameters:
    -----------
    income : float
        Monthly take-home pay
    expenses : dict
        Dictionary of expense categories and amounts
    total_min_debt : float
        Total minimum debt payments
    
    Returns:
    --------
    dict
        Budget breakdown with categories and surplus
    """
    # Calculate total expenses
    total_expenses = sum(expenses.values())
    
    # Calculate total obligated amount (expenses + minimum debt payments)
    total_obligated = total_expenses + total_min_debt
    
    # Calculate surplus
    surplus = income - total_obligated
    
    # Calculate expense percentages
    expense_percentages = {}
    for category, amount in expenses.items():
        if income > 0:
            expense_percentages[category] = (amount / income) * 100
        else:
            expense_percentages[category] = 0
    
    # Debt percentage
    if income > 0:
        debt_percentage = (total_min_debt / income) * 100
    else:
        debt_percentage = 0
    
    # Create budget breakdown
    budget_breakdown = {
        "income": income,
        "total_expenses": total_expenses,
        "total_min_debt": total_min_debt,
        "total_obligated": total_obligated,
        "surplus": surplus,
        "expense_percentages": expense_percentages,
        "debt_percentage": debt_percentage
    }
    
    return budget_breakdown

def calculate_emergency_fund(total_expenses, months, surplus, allocation_percent):
    """
    Calculate emergency fund goal and monthly contribution.
    
    Parameters:
    -----------
    total_expenses : float
        Total monthly expenses
    months : int
        Number of months to save for
    surplus : float
        Monthly surplus available
    allocation_percent : int
        Percentage of surplus to allocate to emergency fund
    
    Returns:
    --------
    tuple
        (emergency_fund_goal, monthly_contribution)
    """
    # Calculate emergency fund goal
    emergency_fund_goal = total_expenses * months
    
    # Calculate monthly contribution
    monthly_contribution = (surplus * allocation_percent) / 100
    
    return emergency_fund_goal, monthly_contribution
