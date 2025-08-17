import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loan_calculator import LoanCalculator
from utils import format_currency, calculate_interest_savings, export_to_csv, analyze_payment_history, validate_payment_data
import io

# Page configuration
st.set_page_config(
    page_title="Loan Prepayment Calculator & Amortization Analyzer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🏦 Loan Prepayment Calculator & Amortization Analyzer")
st.markdown("---")

# Initialize session state
if 'calculator' not in st.session_state:
    st.session_state.calculator = None
if 'amortization_schedule' not in st.session_state:
    st.session_state.amortization_schedule = None
if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = None

# Sidebar for loan parameters
st.sidebar.header("💰 Loan Parameters")

# Loan amount input
loan_amount = st.sidebar.number_input(
    "Loan Amount (₹)",
    min_value=100000,
    max_value=100000000,
    value=7499000,
    step=50000,
    help="Enter the total loan amount you want to borrow"
)

# Interest rate input
interest_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.1,
    max_value=30.0,
    value=8.5,
    step=0.1,
    format="%.2f",
    help="Enter the annual interest rate offered by the lender"
)

# Tenure input
tenure_years = st.sidebar.number_input(
    "Loan Tenure (Years)",
    min_value=1,
    max_value=50,
    value=32,
    step=1,
    help="Enter the loan tenure in years"
)

st.sidebar.markdown("---")

# Prepayment strategy section
st.sidebar.header("🎯 Prepayment Strategy")

# Monthly prepayment
monthly_prepayment = st.sidebar.number_input(
    "Monthly Prepayment (₹)",
    min_value=0,
    max_value=1000000,
    value=29700,
    step=1000,
    help="Additional amount you plan to pay every month towards principal"
)

# Quarterly prepayment
quarterly_prepayment = st.sidebar.number_input(
    "Quarterly Prepayment (₹)",
    min_value=0,
    max_value=5000000,
    value=50000,
    step=5000,
    help="Additional lump sum amount you plan to pay every quarter"
)

# Analysis duration
analysis_months = st.sidebar.number_input(
    "Analysis Duration (Months)",
    min_value=12,
    max_value=600,
    value=200,
    step=12,
    help="Number of months to simulate (default: 200 months ≈ 16 years)"
)

# Calculate button
if st.sidebar.button("🔄 Calculate & Analyze", type="primary"):
    try:
        # Create loan calculator instance
        calculator = LoanCalculator(
            loan_amount=loan_amount,
            annual_rate=interest_rate,
            tenure_years=tenure_years
        )
        
        # Generate amortization schedule with prepayments
        schedule = calculator.generate_amortization_schedule(
            monthly_prepayment=monthly_prepayment,
            quarterly_prepayment=quarterly_prepayment,
            max_months=analysis_months
        )
        
        # Generate comparison data (without prepayments)
        schedule_no_prepay = calculator.generate_amortization_schedule(
            monthly_prepayment=0,
            quarterly_prepayment=0,
            max_months=analysis_months
        )
        
        # Store in session state
        st.session_state.calculator = calculator
        st.session_state.amortization_schedule = schedule
        st.session_state.comparison_data = schedule_no_prepay
        
        st.sidebar.success("✅ Calculation completed!")
        
    except Exception as e:
        st.sidebar.error(f"❌ Error in calculation: {str(e)}")

# Main content area
if st.session_state.calculator is not None:
    calculator = st.session_state.calculator
    schedule_df = pd.DataFrame(st.session_state.amortization_schedule)
    comparison_df = pd.DataFrame(st.session_state.comparison_data)
    
    # Key metrics section
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Monthly EMI",
            format_currency(calculator.emi),
            help="Fixed monthly installment amount"
        )
    
    with col2:
        total_interest_with_prepay = schedule_df['Interest Paid'].sum()
        total_interest_without_prepay = comparison_df['Interest Paid'].sum()
        interest_savings = total_interest_without_prepay - total_interest_with_prepay
        
        st.metric(
            "Interest Savings",
            format_currency(interest_savings),
            delta=f"-{format_currency(interest_savings)}",
            help="Total interest saved through prepayments"
        )
    
    with col3:
        loan_completion_month = len(schedule_df)
        original_tenure_months = calculator.tenure_months
        time_saved_months = original_tenure_months - loan_completion_month
        
        st.metric(
            "Time Saved",
            f"{time_saved_months} months",
            delta=f"-{time_saved_months//12} years {time_saved_months%12} months",
            help="Reduction in loan tenure due to prepayments"
        )
    
    with col4:
        total_prepayment = schedule_df['Monthly Prepayment'].sum() + schedule_df['Quarterly Prepayment'].sum()
        st.metric(
            "Total Prepayments",
            format_currency(total_prepayment),
            help="Total additional payments made"
        )
    
    st.markdown("---")
    
    # Visualization section
    st.header("📈 Interactive Visualizations")
    
    # Loan balance over time chart
    st.subheader("Outstanding Balance Over Time")
    
    fig_balance = go.Figure()
    
    # With prepayments
    fig_balance.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Outstanding Balance'],
        mode='lines',
        name='With Prepayments',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='Month: %{x}<br>Balance: ₹%{y:,.0f}<extra></extra>'
    ))
    
    # Without prepayments (for comparison)
    fig_balance.add_trace(go.Scatter(
        x=comparison_df['Month'],
        y=comparison_df['Outstanding Balance'],
        mode='lines',
        name='Without Prepayments',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        hovertemplate='Month: %{x}<br>Balance: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig_balance.update_layout(
        title="Loan Balance Comparison",
        xaxis_title="Month",
        yaxis_title="Outstanding Balance (₹)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_balance, use_container_width=True)
    
    # Principal vs Interest payments
    st.subheader("Principal vs Interest Payments Over Time")
    
    fig_payments = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Monthly Payments Breakdown', 'Cumulative Payments'],
        specs=[[{"secondary_y": False}, {"type": "pie"}]]
    )
    
    # Monthly payments breakdown
    fig_payments.add_trace(
        go.Scatter(
            x=schedule_df['Month'],
            y=schedule_df['Principal Paid'],
            mode='lines',
            name='Principal',
            line=dict(color='#2ca02c'),
            stackgroup='one'
        ),
        row=1, col=1
    )
    
    fig_payments.add_trace(
        go.Scatter(
            x=schedule_df['Month'],
            y=schedule_df['Interest Paid'],
            mode='lines',
            name='Interest',
            line=dict(color='#d62728'),
            stackgroup='two'
        ),
        row=1, col=1
    )
    
    # Cumulative payments pie chart
    total_principal = schedule_df['Principal Paid'].sum()
    total_interest = schedule_df['Interest Paid'].sum()
    total_prepayments = schedule_df['Monthly Prepayment'].sum() + schedule_df['Quarterly Prepayment'].sum()
    
    fig_payments.add_trace(
        go.Pie(
            labels=['Principal (EMI)', 'Interest', 'Prepayments'],
            values=[total_principal, total_interest, total_prepayments],
            hole=0.3,
            marker_colors=['#2ca02c', '#d62728', '#ff7f0e']
        ),
        row=1, col=2
    )
    
    fig_payments.update_layout(
        template='plotly_white',
        showlegend=True
    )
    
    st.plotly_chart(fig_payments, use_container_width=True)
    
    # Monthly payment breakdown chart
    st.subheader("Monthly Payment Breakdown")
    
    fig_monthly = go.Figure()
    
    fig_monthly.add_trace(go.Bar(
        x=schedule_df['Month'],
        y=schedule_df['Principal Paid'],
        name='Principal (EMI)',
        marker_color='#2ca02c'
    ))
    
    fig_monthly.add_trace(go.Bar(
        x=schedule_df['Month'],
        y=schedule_df['Interest Paid'],
        name='Interest (EMI)',
        marker_color='#d62728'
    ))
    
    fig_monthly.add_trace(go.Bar(
        x=schedule_df['Month'],
        y=schedule_df['Monthly Prepayment'],
        name='Monthly Prepayment',
        marker_color='#ff7f0e'
    ))
    
    fig_monthly.add_trace(go.Bar(
        x=schedule_df['Month'],
        y=schedule_df['Quarterly Prepayment'],
        name='Quarterly Prepayment',
        marker_color='#1f77b4'
    ))
    
    fig_monthly.update_layout(
        barmode='stack',
        title="Monthly Payment Components",
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed amortization schedule
    st.header("📋 Detailed Amortization Schedule")
    
    # Display controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_rows = st.selectbox(
            "Rows to display:",
            options=[10, 25, 50, 100, "All"],
            index=1
        )
    
    with col2:
        filter_year = st.selectbox(
            "Filter by year:",
            options=["All"] + [f"Year {i+1}" for i in range(len(schedule_df)//12 + 1)],
            index=0
        )
    
    with col3:
        if st.button("📥 Download CSV"):
            csv_data = export_to_csv(schedule_df)
            st.download_button(
                label="💾 Download Amortization Schedule",
                data=csv_data,
                file_name=f"loan_amortization_schedule_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Filter data based on selections
    display_df = schedule_df.copy()
    
    if filter_year != "All":
        year_num = int(filter_year.split()[-1])
        start_month = (year_num - 1) * 12 + 1
        end_month = year_num * 12
        display_df = display_df[(display_df['Month'] >= start_month) & (display_df['Month'] <= end_month)]
    
    if show_rows != "All":
        display_df = display_df.head(int(show_rows))
    
    # Format currency columns for display
    display_columns = ['Month', 'Interest Paid', 'Principal Paid', 'Monthly Prepayment', 
                      'Quarterly Prepayment', 'Total Payment', 'Outstanding Balance']
    
    formatted_df = display_df[display_columns].copy()
    currency_columns = ['Interest Paid', 'Principal Paid', 'Monthly Prepayment', 
                       'Quarterly Prepayment', 'Total Payment', 'Outstanding Balance']
    
    for col in currency_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"₹{x:,.0f}")
    
    st.dataframe(
        formatted_df,
        use_container_width=True,
        height=400
    )
    
    # Summary statistics
    st.markdown("---")
    st.header("📈 Summary Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("With Prepayments")
        total_payments_with = (schedule_df['Principal Paid'].sum() + 
                              schedule_df['Interest Paid'].sum() + 
                              schedule_df['Monthly Prepayment'].sum() + 
                              schedule_df['Quarterly Prepayment'].sum())
        
        stats_with = {
            "Total Interest Paid": format_currency(schedule_df['Interest Paid'].sum()),
            "Total Principal Paid": format_currency(schedule_df['Principal Paid'].sum()),
            "Total Prepayments": format_currency(schedule_df['Monthly Prepayment'].sum() + schedule_df['Quarterly Prepayment'].sum()),
            "Total Amount Paid": format_currency(total_payments_with),
            "Loan Duration": f"{len(schedule_df)} months ({len(schedule_df)//12} years {len(schedule_df)%12} months)"
        }
        
        for key, value in stats_with.items():
            st.metric(key, value)
    
    with col2:
        st.subheader("Without Prepayments")
        total_payments_without = (comparison_df['Principal Paid'].sum() + 
                                 comparison_df['Interest Paid'].sum())
        
        stats_without = {
            "Total Interest Paid": format_currency(comparison_df['Interest Paid'].sum()),
            "Total Principal Paid": format_currency(comparison_df['Principal Paid'].sum()),
            "Total Prepayments": format_currency(0),
            "Total Amount Paid": format_currency(total_payments_without),
            "Loan Duration": f"{calculator.tenure_months} months ({calculator.tenure_months//12} years {calculator.tenure_months%12} months)"
        }
        
        for key, value in stats_without.items():
            st.metric(key, value)

    # Payment History Analysis Section
    st.markdown("---")
    st.header("📊 Payment History Analysis")
    st.markdown("Upload your payment history to get personalized loan analysis and recommendations.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your payment history (Excel file)",
        type=['xlsx', 'xls'],
        help="Excel file should contain columns: amount_paid, month, payment_date (optional), notes (optional)"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            payment_data = pd.read_excel(uploaded_file)
            
            # Display column information
            st.subheader("📋 Data Preview")
            st.write(f"**File uploaded successfully!** Found {len(payment_data)} records with columns: {', '.join(payment_data.columns.tolist())}")
            
            # Show sample data
            with st.expander("Preview uploaded data", expanded=False):
                st.dataframe(payment_data.head(10), use_container_width=True)
            
            # Column mapping section
            st.subheader("🔗 Column Mapping")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                amount_col = st.selectbox(
                    "Amount Paid Column",
                    options=payment_data.columns.tolist(),
                    help="Select the column containing payment amounts"
                )
            
            with col2:
                month_col = st.selectbox(
                    "Month Column",
                    options=payment_data.columns.tolist(),
                    help="Select the column containing month numbers (1, 2, 3...)"
                )
            
            with col3:
                date_col = st.selectbox(
                    "Payment Date Column (Optional)",
                    options=["None"] + payment_data.columns.tolist(),
                    help="Select the column containing payment dates"
                )
            
            with col4:
                notes_col = st.selectbox(
                    "Notes Column (Optional)",
                    options=["None"] + payment_data.columns.tolist(),
                    help="Select the column containing payment notes"
                )
            
            # Process the data
            if st.button("🔍 Analyze Payment History", type="primary"):
                try:
                    # Create standardized DataFrame
                    analysis_df = pd.DataFrame()
                    analysis_df['amount_paid'] = payment_data[amount_col]
                    analysis_df['month'] = payment_data[month_col]
                    
                    if date_col != "None":
                        analysis_df['payment_date'] = payment_data[date_col]
                    
                    if notes_col != "None":
                        analysis_df['notes'] = payment_data[notes_col]
                    
                    # Validate the data
                    validation_errors = validate_payment_data(analysis_df)
                    
                    if validation_errors:
                        st.error("Data validation failed:")
                        for error in validation_errors:
                            st.error(f"• {error}")
                    else:
                        # Perform analysis
                        analysis_results = analyze_payment_history(
                            analysis_df, 
                            loan_amount, 
                            interest_rate, 
                            calculator.emi
                        )
                        
                        # Store results in session state
                        st.session_state.payment_analysis = analysis_results
                        st.session_state.payment_data = analysis_df
                        
                        st.success("✅ Payment history analyzed successfully!")
                        
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
            
            # Display analysis results if available
            if 'payment_analysis' in st.session_state:
                results = st.session_state.payment_analysis
                
                st.markdown("---")
                st.header("📈 Payment Analysis Results")
                
                # Summary metrics
                st.subheader("📊 Payment Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Paid",
                        format_currency(results['payment_summary']['total_paid']),
                        help="Total amount paid so far"
                    )
                
                with col2:
                    st.metric(
                        "Months Completed",
                        f"{results['payment_summary']['months_completed']} months",
                        help="Number of months for which payments were made"
                    )
                
                with col3:
                    st.metric(
                        "Total Overpayments",
                        format_currency(results['payment_summary']['total_overpayment']),
                        delta=f"+{format_currency(results['payment_summary']['total_overpayment'])}",
                        help="Amount paid above regular EMI"
                    )
                
                with col4:
                    st.metric(
                        "Loan Completion",
                        f"{results['loan_status']['loan_completion_percentage']:.1f}%",
                        help="Percentage of loan principal paid off"
                    )
                
                # Current loan status
                st.subheader("🎯 Current Loan Status")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Remaining Balance",
                        format_currency(results['loan_status']['remaining_balance']),
                        help="Outstanding loan amount"
                    )
                
                with col2:
                    remaining_months = results['loan_status']['remaining_months']
                    years = int(remaining_months // 12)
                    months = int(remaining_months % 12)
                    st.metric(
                        "Estimated Time Left",
                        f"{years}y {months}m",
                        help="Time remaining if continuing with current EMI"
                    )
                
                with col3:
                    st.metric(
                        "Interest Savings",
                        format_currency(results['loan_status']['estimated_interest_savings']),
                        delta=f"-{format_currency(results['loan_status']['estimated_interest_savings'])}",
                        help="Estimated interest saved through overpayments"
                    )
                
                # Visualizations
                st.subheader("📈 Payment Pattern Visualization")
                
                # Payment history chart
                payment_df = pd.DataFrame(results['monthly_breakdown'])
                
                fig_payments = go.Figure()
                
                fig_payments.add_trace(go.Bar(
                    x=payment_df['month'],
                    y=payment_df['expected_emi'],
                    name='Expected EMI',
                    marker_color='lightblue',
                    opacity=0.7
                ))
                
                fig_payments.add_trace(go.Bar(
                    x=payment_df['month'],
                    y=payment_df['amount_paid'],
                    name='Actual Payment',
                    marker_color='darkblue'
                ))
                
                fig_payments.add_trace(go.Scatter(
                    x=payment_df['month'],
                    y=payment_df['remaining_balance'],
                    mode='lines+markers',
                    name='Remaining Balance',
                    yaxis='y2',
                    line=dict(color='red', width=3),
                    marker=dict(size=6)
                ))
                
                fig_payments.update_layout(
                    title="Payment History vs Expected EMI",
                    xaxis_title="Month",
                    yaxis_title="Payment Amount (₹)",
                    yaxis2=dict(
                        title="Remaining Balance (₹)",
                        overlaying='y',
                        side='right'
                    ),
                    barmode='group',
                    template='plotly_white',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_payments, use_container_width=True)
                
                # Payment breakdown pie chart
                st.subheader("💰 Payment Breakdown")
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Interest Paid', 'Principal Paid', 'Overpayments'],
                    values=[
                        results['payment_summary']['total_interest_paid'],
                        results['payment_summary']['total_principal_paid'] - results['payment_summary']['total_overpayment'],
                        results['payment_summary']['total_overpayment']
                    ],
                    hole=0.3,
                    marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1']
                )])
                
                fig_pie.update_layout(
                    title="Where Your Money Went",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Personalized recommendations
                st.subheader("💡 Personalized Recommendations")
                
                for recommendation in results['recommendations']:
                    st.info(recommendation)
                
                # Detailed payment history table
                st.subheader("📋 Detailed Payment History")
                
                display_payment_df = payment_df.copy()
                currency_cols = ['amount_paid', 'expected_emi', 'expected_interest', 'expected_principal', 
                               'actual_interest', 'actual_principal', 'overpayment', 'remaining_balance']
                
                for col in currency_cols:
                    if col in display_payment_df.columns:
                        display_payment_df[col] = display_payment_df[col].apply(lambda x: f"₹{x:,.0f}")
                
                st.dataframe(
                    display_payment_df,
                    use_container_width=True,
                    height=400
                )
                
                # Export functionality
                if st.button("📥 Download Payment Analysis"):
                    analysis_csv = export_to_csv(payment_df)
                    st.download_button(
                        label="💾 Download Analysis Report",
                        data=analysis_csv,
                        file_name=f"payment_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure your Excel file contains the required columns: amount_paid, month")
    
    else:
        # Sample data template
        st.subheader("📝 Excel File Format")
        st.markdown("Your Excel file should contain the following columns:")
        
        sample_data = pd.DataFrame({
            'amount_paid': [58000, 62000, 59500, 65000, 61000],
            'month': [1, 2, 3, 4, 5],
            'payment_date': ['2024-01-15', '2024-02-15', '2024-03-15', '2024-04-15', '2024-05-15'],
            'notes': ['Regular EMI', 'EMI + bonus', 'Regular EMI', 'Extra payment', 'Regular EMI']
        })
        
        st.dataframe(sample_data, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Required Columns:**")
            st.markdown("• `amount_paid` - Payment amount in rupees")
            st.markdown("• `month` - Month number (1, 2, 3...)")
        
        with col2:
            st.markdown("**Optional Columns:**")
            st.markdown("• `payment_date` - Date of payment")
            st.markdown("• `notes` - Payment notes/comments")
        
        # Download sample template
        if st.button("📥 Download Sample Template"):
            sample_csv = sample_data.to_csv(index=False)
            st.download_button(
                label="💾 Download Excel Template",
                data=sample_csv,
                file_name="payment_history_template.csv",
                mime="text/csv"
            )

else:
    # Welcome screen
    st.header("Welcome to the Loan Prepayment Calculator!")
    
    st.markdown("""
    This comprehensive tool helps you analyze the impact of prepayments on your loan:
    
    ### 🎯 Key Features:
    - **EMI Calculation**: Automatic calculation of your monthly installment
    - **Prepayment Strategy**: Configure monthly and quarterly prepayments
    - **Interactive Visualizations**: See how your loan balance reduces over time
    - **Interest Savings**: Calculate total interest saved through prepayments
    - **Timeline Comparison**: Compare loan duration with and without prepayments
    - **Detailed Schedule**: Month-by-month breakdown of payments
    - **Export Functionality**: Download your amortization schedule
    
    ### 📚 Financial Terms Explained:
    - **EMI**: Equated Monthly Installment - fixed monthly payment
    - **Principal**: The original loan amount
    - **Interest**: Cost of borrowing money
    - **Prepayment**: Additional payment towards loan principal
    - **Amortization**: Gradual reduction of loan through payments
    
    ### 🚀 Getting Started:
    1. Enter your loan details in the sidebar
    2. Configure your prepayment strategy
    3. Click "Calculate & Analyze" to see results
    4. Explore interactive charts and detailed schedules
    
    **👈 Start by entering your loan parameters in the sidebar!**
    """)
    
    # Sample calculation showcase
    st.markdown("---")
    st.subheader("💡 Sample Calculation Preview")
    st.info("""
    **Example**: ₹74,99,000 loan at 8.5% for 32 years
    - **Monthly EMI**: ₹57,891
    - **With ₹29,700 monthly + ₹50,000 quarterly prepayments**:
      - Interest savings: ~₹45,00,000+
      - Time saved: ~16+ years
      - Total prepayments: ~₹71,00,000
    """)
