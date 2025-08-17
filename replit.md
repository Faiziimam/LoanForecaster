# Overview

This is a comprehensive loan prepayment calculator and amortization analyzer built with Streamlit. The application helps users analyze loan scenarios, calculate EMIs, generate detailed amortization schedules, and evaluate the financial impact of various prepayment strategies. It provides interactive visualizations and export capabilities to help users make informed decisions about loan prepayments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar for input parameters
- **Visualization**: Plotly for interactive charts and graphs including:
  - Principal vs interest payment breakdowns
  - Loan balance progression over time
  - Comparison charts for different prepayment scenarios
- **User Interface**: Clean, intuitive interface with sidebar controls and main content area
- **State Management**: Streamlit session state for maintaining calculator instances and computed data

## Backend Architecture
- **Core Logic**: Object-oriented design with `LoanCalculator` class as the main computation engine
- **Calculation Methods**: 
  - Standard EMI formula implementation
  - Comprehensive amortization schedule generation
  - Support for multiple prepayment strategies (monthly and quarterly)
- **Data Processing**: Pandas DataFrames for structured data manipulation and analysis
- **Mathematical Operations**: NumPy for efficient numerical computations

## Data Management
- **Data Structures**: Dictionary-based records for amortization schedules
- **Export Functionality**: CSV export capabilities through utility functions
- **Data Formatting**: Custom currency formatting with Indian numbering system support
- **Comparison Analysis**: Built-in savings calculation between different loan scenarios

## Key Features
- **EMI Calculation**: Standard loan EMI computation using financial formulas
- **Amortization Scheduling**: Detailed month-by-month loan breakdown
- **Prepayment Analysis**: Support for various prepayment strategies
- **Interest Savings Calculation**: Comprehensive savings analysis between scenarios
- **Interactive Visualizations**: Multiple chart types for data analysis
- **Export Capabilities**: Data export to CSV format

# External Dependencies

## Python Libraries
- **streamlit**: Web application framework for the user interface
- **pandas**: Data manipulation and analysis library
- **numpy**: Numerical computing library for mathematical operations
- **plotly.express**: High-level plotting interface for interactive visualizations
- **plotly.graph_objects**: Low-level plotting interface for custom charts
- **plotly.subplots**: Subplot creation for complex chart layouts

## Data Processing
- **io**: Built-in Python module for handling data streams and file operations
- **typing**: Type hinting support for better code documentation and IDE support

## File Structure
- **app.py**: Main Streamlit application entry point
- **loan_calculator.py**: Core loan calculation logic and amortization engine
- **utils.py**: Utility functions for formatting, calculations, and data export