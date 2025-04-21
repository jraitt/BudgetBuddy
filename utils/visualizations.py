import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def plot_budget_breakdown(expenses, total_debt, emergency_fund, remaining):
    """
    Create a pie chart showing budget breakdown.
    
    Parameters:
    -----------
    expenses : dict
        Dictionary of expense categories and amounts
    total_debt : float
        Total debt payment amount
    emergency_fund : float
        Monthly emergency fund contribution
    remaining : float
        Remaining surplus
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Plotly figure object
    """
    labels = list(expenses.keys()) + ["Debt Payments", "Emergency Fund", "Remaining Surplus"]
    values = list(expenses.values()) + [total_debt, emergency_fund, remaining]
    
    # Filter out zero or negative values
    filtered_labels = []
    filtered_values = []
    for label, value in zip(labels, values):
        if value > 0:
            filtered_labels.append(label)
            filtered_values.append(value)
    
    # Create color palette - different color for remaining surplus
    colors = px.colors.qualitative.Plotly[:len(filtered_labels)-1] + ['#00CC96'] 
    if "Remaining Surplus" not in filtered_labels:
        colors = px.colors.qualitative.Plotly[:len(filtered_labels)]
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels,
        values=filtered_values,
        hole=.4,
        marker=dict(colors=colors)
    )])
    
    fig.update_layout(
        title="Monthly Budget Allocation",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=30, b=0, l=0, r=0),
        height=400
    )
    
    return fig

def plot_debt_payoff_timeline(payoff_schedule):
    """
    Create a line chart showing debt payoff over time.
    
    Parameters:
    -----------
    payoff_schedule : list
        List of dictionaries with debt balances by month
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Plotly figure object
    """
    # Extract unique debt names
    debt_names = set()
    for month_data in payoff_schedule:
        for debt_name in month_data.keys():
            debt_names.add(debt_name)
    
    # Prepare data for plotting
    months = list(range(1, len(payoff_schedule) + 1))
    
    fig = go.Figure()
    
    # Add a line for each debt
    for debt_name in debt_names:
        balances = []
        for month_data in payoff_schedule:
            if debt_name in month_data:
                balances.append(month_data[debt_name])
            else:
                balances.append(0)  # Debt paid off
        
        # Remove trailing zeros (paid off)
        for i in range(len(balances) - 1, -1, -1):
            if balances[i] > 0:
                break
            balances[i] = None
        
        fig.add_trace(go.Scatter(
            x=months,
            y=balances,
            mode='lines',
            name=debt_name,
            line=dict(width=3)
        ))
    
    # Add total debt line
    total_by_month = []
    for month_data in payoff_schedule:
        total = sum(month_data.values())
        total_by_month.append(total)
    
    fig.add_trace(go.Scatter(
        x=months,
        y=total_by_month,
        mode='lines',
        name='Total Debt',
        line=dict(width=4, color='black', dash='dash')
    ))
    
    fig.update_layout(
        title="Debt Payoff Timeline",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=30, b=0, l=0, r=0),
        height=500,
        hovermode="x unified"
    )
    
    fig.update_yaxes(tickprefix="$")
    
    return fig

def plot_savings_timeline(savings_by_month, goal):
    """
    Create a line chart showing emergency fund savings progress.
    
    Parameters:
    -----------
    savings_by_month : list or numpy array
        Cumulative savings by month
    goal : float
        Emergency fund goal amount
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Plotly figure object
    """
    months = list(range(1, len(savings_by_month) + 1))
    
    fig = go.Figure()
    
    # Add savings line
    fig.add_trace(go.Scatter(
        x=months,
        y=savings_by_month,
        mode='lines',
        name='Savings',
        line=dict(width=3, color='#1F77B4'),
        fill='tozeroy'
    ))
    
    # Add goal line
    fig.add_trace(go.Scatter(
        x=[1, len(savings_by_month)],
        y=[goal, goal],
        mode='lines',
        name='Goal',
        line=dict(width=2, color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Emergency Fund Progress",
        xaxis_title="Month",
        yaxis_title="Savings ($)",
        margin=dict(t=30, b=0, l=0, r=0),
        height=300,
        hovermode="x unified"
    )
    
    fig.update_yaxes(tickprefix="$")
    
    return fig
