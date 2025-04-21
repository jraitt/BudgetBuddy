import numpy as np
import pandas as pd
from copy import deepcopy

def calculate_debt_payoff(debts, extra_payment, sort_key):
    """
    Calculate debt payoff plan based on provided strategy.
    
    Parameters:
    -----------
    debts : list
        List of debt dictionaries with name, balance, payment, and rate
    extra_payment : float
        Additional monthly payment to apply to debts
    sort_key : callable
        Function to determine the order of debt payoff
    
    Returns:
    --------
    dict
        Debt payoff plan with timeline and statistics
    """
    if not debts:
        return {
            "months_to_payoff": 0,
            "total_interest_paid": 0,
            "sorted_debts": [],
            "payoff_schedule": []
        }
    
    # Deep copy to avoid modifying original data
    debts_copy = deepcopy(debts)
    
    # Sort debts based on the provided key function
    sorted_debts = sorted(debts_copy, key=sort_key)
    
    # Initialize variables
    remaining_debts = sorted_debts.copy()
    total_interest_paid = 0
    month = 0
    payoff_schedule = []
    
    # Continue until all debts are paid off
    while remaining_debts:
        month += 1
        month_balances = {}
        extra_available = extra_payment
        paid_this_month = []
        
        # Make minimum payments on all debts
        for debt in remaining_debts:
            # Calculate interest for this month
            monthly_interest = debt["balance"] * (debt["rate"] / 12)
            total_interest_paid += monthly_interest
            
            # Add interest to balance
            debt["balance"] += monthly_interest
            
            # Make minimum payment
            if debt["balance"] <= debt["payment"]:
                # Debt will be paid off this month
                extra_available += debt["payment"] - debt["balance"]
                debt["balance"] = 0
                paid_this_month.append(debt)
            else:
                # Make regular payment
                debt["balance"] -= debt["payment"]
            
            # Record current balance
            month_balances[debt["name"]] = debt["balance"]
        
        # Remove paid off debts
        for debt in paid_this_month:
            remaining_debts.remove(debt)
        
        # Apply extra payment to first debt in list
        if remaining_debts and extra_available > 0:
            first_debt = remaining_debts[0]
            if first_debt["balance"] <= extra_available:
                # Can pay off this debt with extra payment
                extra_available -= first_debt["balance"]
                first_debt["balance"] = 0
                remaining_debts.remove(first_debt)
                month_balances[first_debt["name"]] = 0
            else:
                # Apply extra payment to balance
                first_debt["balance"] -= extra_available
                month_balances[first_debt["name"]] = first_debt["balance"]
        
        # Add this month's balances to schedule
        payoff_schedule.append(month_balances)
    
    return {
        "months_to_payoff": month,
        "total_interest_paid": total_interest_paid,
        "sorted_debts": sorted_debts,
        "payoff_schedule": payoff_schedule
    }

def debt_snowball(debts, extra_payment):
    """
    Calculate debt payoff using the snowball method (smallest balance first).
    
    Parameters:
    -----------
    debts : list
        List of debt dictionaries with name, balance, payment, and rate
    extra_payment : float
        Additional monthly payment to apply to debts
    
    Returns:
    --------
    dict
        Debt payoff plan with timeline and statistics
    """
    return calculate_debt_payoff(debts, extra_payment, lambda x: x["balance"])

def debt_avalanche(debts, extra_payment):
    """
    Calculate debt payoff using the avalanche method (highest interest rate first).
    
    Parameters:
    -----------
    debts : list
        List of debt dictionaries with name, balance, payment, and rate
    extra_payment : float
        Additional monthly payment to apply to debts
    
    Returns:
    --------
    dict
        Debt payoff plan with timeline and statistics
    """
    return calculate_debt_payoff(debts, extra_payment, lambda x: -x["rate"])
