import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

from utils.budget_calculator import calculate_budget, calculate_emergency_fund
from utils.debt_strategies import calculate_debt_payoff, debt_snowball, debt_avalanche
from utils.visualizations import (
    plot_budget_breakdown, 
    plot_debt_payoff_timeline, 
    plot_savings_timeline
)
from utils.database import save_profile, load_profile, get_all_profiles, delete_profile

# Set page config
st.set_page_config(
    page_title="Financial Freedom Planner",
    page_icon="💰",
    layout="wide",
)

# Initialize session state variables if they don't exist
if 'income' not in st.session_state:
    st.session_state.income = 0.0
if 'expenses' not in st.session_state:
    st.session_state.expenses = {}
if 'debts' not in st.session_state:
    st.session_state.debts = []
if 'budget' not in st.session_state:
    st.session_state.budget = None
if 'debt_payoff_plan' not in st.session_state:
    st.session_state.debt_payoff_plan = None
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'ef_months' not in st.session_state:
    st.session_state.ef_months = 3
if 'ef_allocation' not in st.session_state:
    st.session_state.ef_allocation = 50
if 'extra_payment' not in st.session_state:
    st.session_state.extra_payment = 0.0
if 'strategy' not in st.session_state:
    st.session_state.strategy = "Snowball (Smallest balance first)"
if 'profile_id' not in st.session_state:
    st.session_state.profile_id = None

# Title and introduction
st.title("Financial Freedom Planner 💰")
st.write("""
This application helps you create a comprehensive budget plan, develop a debt payoff strategy, 
and visualize your path to financial freedom. Enter your income, expenses, and debts to get started.
""")

# Sidebar for profile management
with st.sidebar:
    st.header("Profile Management")
    st.write("Save your financial data or load previously saved profiles")
    
    # Get all profiles
    all_profiles = get_all_profiles()
    
    # Save profile section
    with st.expander("Save Profile", expanded=True):
        profile_name = st.text_input("Profile Name", placeholder="e.g., My Budget 2025")
        
        if st.button("Save Current Data"):
            if profile_name:
                # Save profile to database
                profile_id = save_profile(
                    name=profile_name,
                    income=st.session_state.income,
                    expenses=st.session_state.expenses,
                    debts=st.session_state.debts,
                    ef_months=st.session_state.ef_months,
                    ef_allocation=st.session_state.ef_allocation,
                    extra_payment=st.session_state.extra_payment,
                    strategy=st.session_state.strategy
                )
                st.session_state.profile_id = profile_id
                st.success(f"Profile '{profile_name}' saved successfully!")
                st.rerun()  # Refresh to update profile list
            else:
                st.error("Please enter a profile name")
    
    # Load profile section
    if all_profiles:
        with st.expander("Load Profile", expanded=True):
            profile_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in all_profiles}
            selected_profile = st.selectbox(
                "Select a profile to load",
                options=list(profile_options.keys()),
                index=None,
                placeholder="Choose a saved profile"
            )
            
            if st.button("Load Selected Profile"):
                if selected_profile:
                    profile_id = profile_options[selected_profile]
                    # Load profile data
                    profile_data = load_profile(profile_id=profile_id)
                    
                    if profile_data:
                        # Update session state with loaded data
                        st.session_state.income = profile_data['income']
                        st.session_state.expenses = profile_data['expenses']
                        st.session_state.debts = profile_data['debts']
                        st.session_state.ef_months = profile_data['ef_months']
                        st.session_state.ef_allocation = profile_data['ef_allocation']
                        st.session_state.extra_payment = profile_data['extra_payment']
                        st.session_state.strategy = profile_data['strategy']
                        st.session_state.profile_id = profile_id
                        
                        # Clear generated data to force recalculation
                        st.session_state.generated = False
                        st.session_state.budget = None
                        st.session_state.debt_payoff_plan = None
                        
                        st.success(f"Profile loaded successfully!")
                        st.rerun()  # Refresh to update UI with loaded data
                    else:
                        st.error("Failed to load profile data")
                else:
                    st.warning("Please select a profile to load")
            
            if st.button("Delete Selected Profile"):
                if selected_profile:
                    profile_id = profile_options[selected_profile]
                    # Delete profile
                    if delete_profile(profile_id):
                        st.success(f"Profile deleted successfully!")
                        st.rerun()  # Refresh to update profile list
                    else:
                        st.error("Failed to delete profile")
                else:
                    st.warning("Please select a profile to delete")
    else:
        st.info("No saved profiles yet. Save your first profile above.")

# Main sections
tab1, tab2, tab3 = st.tabs(["Input Information", "Budget Plan", "Debt Payoff Strategy"])

with tab1:
    st.header("Financial Information")
    
    # Income input
    st.subheader("Monthly Income")
    income = st.number_input(
        "Take-home pay (after taxes and deductions)",
        min_value=0.0,
        value=st.session_state.income,
        format="%.2f",
        help="Your monthly income after taxes and other deductions"
    )
    st.session_state.income = income
    
    # Expenses input
    st.subheader("Monthly Expenses")
    col1, col2 = st.columns(2)
    
    with col1:
        housing = st.number_input(
            "Rent/Mortgage", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Housing', 0.0),
            format="%.2f",
            help="Monthly rent or mortgage payment"
        )
        
        utilities = st.number_input(
            "Utilities", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Utilities', 0.0),
            format="%.2f",
            help="Electric, water, gas, internet, etc."
        )
        
        groceries = st.number_input(
            "Groceries", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Groceries', 0.0),
            format="%.2f",
            help="Food and household items"
        )
        
        transportation = st.number_input(
            "Transportation", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Transportation', 0.0),
            format="%.2f",
            help="Gas, insurance, public transit, etc."
        )
    
    with col2:
        subscriptions = st.number_input(
            "Subscriptions", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Subscriptions', 0.0),
            format="%.2f",
            help="Streaming services, apps, etc."
        )
        
        childcare = st.number_input(
            "Childcare/School", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Childcare', 0.0),
            format="%.2f",
            help="Daycare, tuition, etc."
        )
        
        medical = st.number_input(
            "Medical/Insurance", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Medical', 0.0),
            format="%.2f",
            help="Health insurance, medications, doctor visits, etc."
        )
        
        miscellaneous = st.number_input(
            "Miscellaneous", 
            min_value=0.0, 
            value=st.session_state.expenses.get('Miscellaneous', 0.0),
            format="%.2f",
            help="Other expenses not covered in other categories"
        )
    
    # Update expenses in session state
    st.session_state.expenses = {
        'Housing': housing,
        'Utilities': utilities,
        'Groceries': groceries,
        'Transportation': transportation,
        'Subscriptions': subscriptions,
        'Childcare': childcare,
        'Medical': medical,
        'Miscellaneous': miscellaneous
    }
    
    # Debt input
    st.subheader("Debts")
    st.write("Enter your current debts below. Add as many as needed.")
    
    # Show existing debts
    if st.session_state.debts:
        debt_df = pd.DataFrame(st.session_state.debts)
        st.dataframe(debt_df)
    
    # Form for adding new debt
    with st.form("debt_form"):
        col1, col2 = st.columns(2)
        with col1:
            debt_name = st.text_input("Debt Name (e.g., Credit Card, Car Loan)")
            debt_balance = st.number_input("Current Balance ($)", min_value=0.0, format="%.2f")
        with col2:
            debt_payment = st.number_input("Minimum Monthly Payment ($)", min_value=0.0, format="%.2f")
            debt_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=100.0, format="%.2f")
        
        submitted = st.form_submit_button("Add Debt")
        if submitted and debt_name and debt_balance > 0:
            new_debt = {
                "name": debt_name,
                "balance": debt_balance,
                "payment": debt_payment,
                "rate": debt_rate/100  # Convert to decimal
            }
            st.session_state.debts.append(new_debt)
            st.rerun()
    
    # Clear debts button
    if st.session_state.debts and st.button("Clear All Debts"):
        st.session_state.debts = []
        st.rerun()
    
    # Strategy selection and calculations
    st.subheader("Debt Payoff Strategy")
    strategy = st.radio(
        "Choose a debt payoff strategy:",
        ["Snowball (Smallest balance first)", "Avalanche (Highest interest first)"],
        help="Snowball: Pay smallest debts first for psychological wins. Avalanche: Pay highest interest first to minimize total interest."
    )
    st.session_state.strategy = strategy
    
    # Additional money toward debt
    extra_payment = st.number_input(
        "Additional monthly amount to put toward debt ($)",
        min_value=0.0,
        format="%.2f",
        help="Any extra money you can contribute monthly to accelerate debt payoff"
    )
    st.session_state.extra_payment = extra_payment
    
    # Emergency fund goal
    st.subheader("Emergency Fund")
    ef_months = st.slider(
        "Months of expenses to save for emergency fund:",
        min_value=1,
        max_value=12,
        value=st.session_state.ef_months,
        help="Financial experts typically recommend 3-6 months of expenses saved"
    )
    st.session_state.ef_months = ef_months
    
    # Emergency fund allocation
    ef_allocation = st.slider(
        "Percentage of surplus to allocate to emergency fund (vs. debt):",
        min_value=0,
        max_value=100,
        value=st.session_state.ef_allocation,
        help="How to split extra money between emergency fund and debt payoff"
    )
    st.session_state.ef_allocation = ef_allocation
    
    # Generate budget and payoff plan
    if st.button("Generate Financial Plan"):
        with st.spinner("Calculating your financial plan..."):
            # Calculate total expenses and surplus
            total_expenses = sum(st.session_state.expenses.values())
            total_min_debt_payments = sum(debt["payment"] for debt in st.session_state.debts)
            
            # Calculate budget
            st.session_state.budget = calculate_budget(
                income=income,
                expenses=st.session_state.expenses,
                total_min_debt=total_min_debt_payments
            )
            
            # Calculate emergency fund
            emergency_fund_goal, ef_monthly = calculate_emergency_fund(
                total_expenses=total_expenses,
                months=ef_months,
                surplus=st.session_state.budget["surplus"],
                allocation_percent=ef_allocation
            )
            
            # Determine available for debt
            available_for_debt = st.session_state.budget["surplus"] - ef_monthly + extra_payment
            
            # Calculate debt payoff
            if strategy.startswith("Snowball"):
                st.session_state.debt_payoff_plan = debt_snowball(
                    debts=st.session_state.debts,
                    extra_payment=available_for_debt
                )
            else:
                st.session_state.debt_payoff_plan = debt_avalanche(
                    debts=st.session_state.debts,
                    extra_payment=available_for_debt
                )
            
            st.session_state.ef_data = {
                "goal": emergency_fund_goal,
                "monthly": ef_monthly,
                "allocation_percent": ef_allocation
            }
            
            st.session_state.generated = True
            st.success("Your financial plan has been generated! Check the 'Budget Plan' and 'Debt Payoff Strategy' tabs.")

with tab2:
    if st.session_state.generated and st.session_state.budget:
        st.header("Your Budget Plan")
        
        # Display budget summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly Income", f"${st.session_state.income:.2f}")
        col2.metric("Total Expenses", f"${sum(st.session_state.expenses.values()):.2f}")
        col3.metric("Debt Payments", f"${sum(debt['payment'] for debt in st.session_state.debts):.2f}")
        
        surplus = st.session_state.budget["surplus"]
        col4.metric("Available Surplus", f"${surplus:.2f}")
        
        st.divider()
        
        # Display budget breakdown
        st.subheader("Budget Breakdown")
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.write("#### Monthly Budget Allocation")
            budget_df = pd.DataFrame({
                "Category": list(st.session_state.expenses.keys()) + 
                           ["Debt Payments", "Emergency Fund", "Remaining Surplus"],
                "Amount": list(st.session_state.expenses.values()) + 
                         [sum(debt['payment'] for debt in st.session_state.debts),
                          st.session_state.ef_data["monthly"],
                          surplus - st.session_state.ef_data["monthly"]]
            })
            st.dataframe(budget_df.style.format({"Amount": "${:.2f}"}), use_container_width=True)
        
        with col2:
            # Visualize budget breakdown
            fig = plot_budget_breakdown(
                expenses=st.session_state.expenses,
                total_debt=sum(debt['payment'] for debt in st.session_state.debts),
                emergency_fund=st.session_state.ef_data["monthly"],
                remaining=surplus - st.session_state.ef_data["monthly"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Emergency fund information
        st.subheader("Emergency Fund Plan")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            #### Emergency Fund Goal: ${st.session_state.ef_data['goal']:.2f}
            - Monthly contribution: ${st.session_state.ef_data['monthly']:.2f}
            - Allocation: {st.session_state.ef_data['allocation_percent']}% of surplus
            - Fund covers: {ef_months} months of expenses
            """)
        
        with col2:
            # Calculate time to reach emergency fund goal
            if st.session_state.ef_data["monthly"] > 0:
                months_to_ef = st.session_state.ef_data["goal"] / st.session_state.ef_data["monthly"]
                ef_timeline = np.minimum(
                    np.cumsum([st.session_state.ef_data["monthly"]] * int(np.ceil(months_to_ef))),
                    st.session_state.ef_data["goal"]
                )
                fig = plot_savings_timeline(ef_timeline, st.session_state.ef_data["goal"])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No funds allocated to emergency fund.")
        
        # Export budget button
        budget_data = {
            "Income": st.session_state.income,
            "Expenses": st.session_state.expenses,
            "Debt Payments": sum(debt['payment'] for debt in st.session_state.debts),
            "Emergency Fund Contribution": st.session_state.ef_data["monthly"],
            "Emergency Fund Goal": st.session_state.ef_data["goal"],
            "Remaining Surplus": surplus - st.session_state.ef_data["monthly"],
            "Date Generated": datetime.now().strftime("%Y-%m-%d")
        }
        
        budget_df = pd.DataFrame([budget_data])
        
        buffer = io.BytesIO()
        budget_df.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Budget Summary (CSV)",
            data=buffer,
            file_name="budget_summary.csv",
            mime="text/csv"
        )
    else:
        st.info("Please enter your financial information and generate a plan in the 'Input Information' tab.")

with tab3:
    if st.session_state.generated and st.session_state.debt_payoff_plan and st.session_state.debts:
        st.header("Debt Payoff Strategy")
        
        # Summary metrics
        total_debt = sum(debt["balance"] for debt in st.session_state.debts)
        total_interest = st.session_state.debt_payoff_plan["total_interest_paid"]
        payoff_months = st.session_state.debt_payoff_plan["months_to_payoff"]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Debt", f"${total_debt:.2f}")
        col2.metric("Total Interest to be Paid", f"${total_interest:.2f}")
        
        if payoff_months < 12:
            payoff_text = f"{payoff_months:.1f} months"
        else:
            years = int(payoff_months // 12)
            months = int(payoff_months % 12)
            payoff_text = f"{years} years, {months} months"
        
        col3.metric("Time to Debt Freedom", payoff_text)
        
        st.divider()
        
        # Display debt details
        st.subheader("Your Debts")
        sorted_debts = st.session_state.debt_payoff_plan["sorted_debts"]
        
        debts_df = pd.DataFrame(sorted_debts)
        debts_df = debts_df.rename(columns={
            "name": "Debt Name",
            "balance": "Current Balance",
            "payment": "Minimum Payment",
            "rate": "Interest Rate"
        })
        
        # Format the dataframe
        debts_df["Interest Rate"] = debts_df["Interest Rate"].apply(lambda x: f"{x*100:.2f}%")
        debts_df["Current Balance"] = debts_df["Current Balance"].apply(lambda x: f"${x:.2f}")
        debts_df["Minimum Payment"] = debts_df["Minimum Payment"].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(debts_df, use_container_width=True)
        
        st.divider()
        
        # Payoff visualization
        st.subheader("Debt Payoff Timeline")
        payoff_schedule = st.session_state.debt_payoff_plan["payoff_schedule"]
        
        # Display total payment by month
        fig = plot_debt_payoff_timeline(payoff_schedule)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed payoff information
        with st.expander("View Detailed Payoff Schedule"):
            # Convert payoff schedule to dataframe
            schedule_data = []
            for month, balances in enumerate(payoff_schedule):
                month_data = {"Month": month + 1}
                for debt_name, balance in balances.items():
                    month_data[debt_name] = balance
                schedule_data.append(month_data)
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Format the dataframe
            for col in schedule_df.columns:
                if col != "Month":
                    schedule_df[col] = schedule_df[col].apply(lambda x: f"${x:.2f}" if not pd.isna(x) else "PAID OFF")
            
            st.dataframe(schedule_df, use_container_width=True)
        
        # Payoff strategy explanation
        st.divider()
        strategy_used = "Snowball" if strategy.startswith("Snowball") else "Avalanche"
        
        st.subheader(f"About the {strategy_used} Method")
        
        if strategy_used == "Snowball":
            st.write("""
            The **Debt Snowball** method focuses on paying off debts from smallest to largest balance, 
            regardless of interest rate. This creates psychological wins as you eliminate debts quickly, 
            helping you stay motivated.
            
            ### How it works:
            1. Make minimum payments on all debts
            2. Put extra money toward the smallest debt
            3. Once that debt is paid off, roll that payment to the next smallest debt
            4. Repeat until all debts are paid off
            
            This method may cost more in interest over time compared to the Avalanche method, but many 
            people find it more effective because it provides early success.
            """)
        else:
            st.write("""
            The **Debt Avalanche** method focuses on paying off debts with the highest interest rates first. 
            This is mathematically optimal and minimizes the total interest you'll pay.
            
            ### How it works:
            1. Make minimum payments on all debts
            2. Put extra money toward the debt with the highest interest rate
            3. Once that debt is paid off, roll that payment to the debt with the next highest rate
            4. Repeat until all debts are paid off
            
            This method will save you the most money over time, but may take longer to eliminate individual 
            debts compared to the Snowball method.
            """)
        
        # Export debt plan
        payoff_data = {
            "Strategy": strategy_used,
            "Total Debt": total_debt,
            "Total Interest to be Paid": total_interest,
            "Months to Payoff": payoff_months,
            "Date Generated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add debt information
        for i, debt in enumerate(sorted_debts):
            payoff_data[f"Debt_{i+1}_Name"] = debt["name"]
            payoff_data[f"Debt_{i+1}_Balance"] = debt["balance"]
            payoff_data[f"Debt_{i+1}_Rate"] = debt["rate"]
        
        payoff_df = pd.DataFrame([payoff_data])
        
        buffer = io.BytesIO()
        payoff_df.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Debt Payoff Plan (CSV)",
            data=buffer,
            file_name="debt_payoff_plan.csv",
            mime="text/csv"
        )
    else:
        st.info("Please enter your financial information and generate a plan in the 'Input Information' tab.")

# Add footer
st.divider()
st.write("### Financial Freedom Planner")
st.write("""
This tool is for educational purposes only and does not constitute financial advice. 
Please consult with a financial professional for personalized guidance.
""")
