"""
Valuation Engine for Meridian M&A Platform
DCF, Comparables, and Precedent Transaction Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import optimize

class ValuationEngine:
    """Comprehensive valuation analysis for M&A targets"""
    
    def __init__(self, risk_free_rate: float = 0.045, market_premium: float = 0.08):
        """Initialize valuation parameters"""
        self.risk_free_rate = risk_free_rate
        self.market_premium = market_premium
        
        # Industry-specific parameters
        self.industry_betas = {
            'SaaS': 1.3,
            'Fintech': 1.2,
            'Healthcare IT': 1.0,
            'Cybersecurity': 1.4,
            'Data & Analytics': 1.25
        }
        
        self.terminal_growth_rates = {
            'SaaS': 0.03,
            'Fintech': 0.025,
            'Healthcare IT': 0.025,
            'Cybersecurity': 0.035,
            'Data & Analytics': 0.03
        }
    
    def comprehensive_valuation(
        self,
        company: pd.Series,
        comparables: pd.DataFrame = None,
        precedent_deals: pd.DataFrame = None
    ) -> Dict:
        """
        Perform comprehensive valuation using multiple methodologies
        """
        
        valuation_results = {
            'company_name': company['name'],
            'current_ev': company['enterprise_value'],
            'methodologies': {}
        }
        
        # 1. DCF Valuation
        dcf_result = self.dcf_valuation(company)
        valuation_results['methodologies']['dcf'] = dcf_result
        
        # 2. Comparable Company Analysis
        if comparables is not None and len(comparables) > 0:
            comp_result = self.comparable_company_analysis(company, comparables)
            valuation_results['methodologies']['comparables'] = comp_result
        
        # 3. Precedent Transaction Analysis
        if precedent_deals is not None and len(precedent_deals) > 0:
            precedent_result = self.precedent_transaction_analysis(company, precedent_deals)
            valuation_results['methodologies']['precedent'] = precedent_result
        
        # 4. Calculate valuation range
        all_values = []
        for method_name, method_result in valuation_results['methodologies'].items():
            if 'value' in method_result:
                all_values.append(method_result['value'])
        
        if all_values:
            valuation_results['valuation_range'] = {
                'min': min(all_values),
                'max': max(all_values),
                'mean': np.mean(all_values),
                'median': np.median(all_values)
            }
            
            # Calculate upside/downside
            current_ev = company['enterprise_value']
            valuation_results['implied_return'] = {
                'min': (valuation_results['valuation_range']['min'] / current_ev - 1),
                'max': (valuation_results['valuation_range']['max'] / current_ev - 1),
                'median': (valuation_results['valuation_range']['median'] / current_ev - 1)
            }
        
        return valuation_results
    
    def dcf_valuation(self, company: pd.Series, projection_years: int = 5) -> Dict:
        """
        Discounted Cash Flow valuation
        """
        
        # Get company-specific parameters
        industry = company.get('industry', 'SaaS')
        beta = self.industry_betas.get(industry, 1.2)
        terminal_growth = self.terminal_growth_rates.get(industry, 0.03)
        
        # Calculate WACC
        cost_of_equity = self.risk_free_rate + beta * self.market_premium
        
        # Simplified WACC (assuming no debt for simplicity in demo)
        debt_ratio = company.get('debt_to_equity', 0) / (1 + company.get('debt_to_equity', 0))
        equity_ratio = 1 - debt_ratio
        cost_of_debt = 0.05  # Assumed
        tax_rate = 0.21  # US corporate tax rate
        
        wacc = (equity_ratio * cost_of_equity + 
                debt_ratio * cost_of_debt * (1 - tax_rate))
        
        # Project cash flows
        revenue = company['revenue_ttm']
        growth_rate = company['revenue_growth_yoy']
        ebitda_margin = company.get('ebitda_margin', 0.15)
        
        # Gradual growth decay
        growth_decay = 0.9  # Growth rate decays by 10% per year
        
        cash_flows = []
        for year in range(1, projection_years + 1):
            # Project revenue with decaying growth
            revenue = revenue * (1 + growth_rate)
            growth_rate = growth_rate * growth_decay
            
            # Calculate free cash flow (simplified)
            ebitda = revenue * ebitda_margin
            tax = ebitda * tax_rate
            capex = revenue * 0.05  # 5% of revenue
            nwc_change = revenue * 0.02  # 2% of revenue
            
            fcf = ebitda * (1 - tax_rate) - capex - nwc_change
            cash_flows.append(fcf)
        
        # Calculate present value of cash flows
        pv_cash_flows = sum([cf / (1 + wacc)**i for i, cf in enumerate(cash_flows, 1)])
        
        # Terminal value
        terminal_fcf = cash_flows[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / (1 + wacc)**projection_years
        
        # Enterprise value
        enterprise_value = pv_cash_flows + pv_terminal
        
        return {
            'value': enterprise_value,
            'wacc': wacc,
            'terminal_growth': terminal_growth,
            'projected_cash_flows': cash_flows,
            'terminal_value': terminal_value,
            'pv_cash_flows': pv_cash_flows,
            'pv_terminal': pv_terminal,
            'assumptions': {
                'beta': beta,
                'cost_of_equity': cost_of_equity,
                'projection_years': projection_years,
                'initial_growth': company['revenue_growth_yoy'],
                'ebitda_margin': ebitda_margin
            }
        }
    
    def comparable_company_analysis(
        self,
        company: pd.Series,
        comparables: pd.DataFrame
    ) -> Dict:
        """
        Valuation based on comparable public companies
        """
        
        # Filter comparables to same industry if possible
        industry_comps = comparables[comparables.get('industry', '') == company.get('industry', '')]
        if len(industry_comps) < 3:
            industry_comps = comparables  # Use all if not enough industry matches
        
        # Calculate relevant multiples
        multiples = {
            'EV/Revenue': [],
            'EV/EBITDA': [],
            'P/E': []
        }
        
        # EV/Revenue multiple
        if 'ev_revenue' in industry_comps.columns:
            ev_revenue = industry_comps['ev_revenue'].dropna()
            if len(ev_revenue) > 0:
                # Remove outliers using IQR
                q1, q3 = ev_revenue.quantile([0.25, 0.75])
                iqr = q3 - q1
                filtered = ev_revenue[(ev_revenue >= q1 - 1.5*iqr) & (ev_revenue <= q3 + 1.5*iqr)]
                
                multiples['EV/Revenue'] = {
                    'median': filtered.median(),
                    'mean': filtered.mean(),
                    '25th_percentile': filtered.quantile(0.25),
                    '75th_percentile': filtered.quantile(0.75)
                }
        
        # EV/EBITDA multiple (only if company is profitable)
        if company.get('ebitda', 0) > 0 and 'ev_ebitda' in industry_comps.columns:
            ev_ebitda = industry_comps['ev_ebitda'].dropna()
            ev_ebitda = ev_ebitda[ev_ebitda > 0]  # Only positive multiples
            
            if len(ev_ebitda) > 0:
                q1, q3 = ev_ebitda.quantile([0.25, 0.75])
                iqr = q3 - q1
                filtered = ev_ebitda[(ev_ebitda >= q1 - 1.5*iqr) & (ev_ebitda <= q3 + 1.5*iqr)]
                
                multiples['EV/EBITDA'] = {
                    'median': filtered.median(),
                    'mean': filtered.mean(),
                    '25th_percentile': filtered.quantile(0.25),
                    '75th_percentile': filtered.quantile(0.75)
                }
        
        # Calculate implied valuations
        valuations = []
        
        # EV based on revenue multiple
        if 'EV/Revenue' in multiples and multiples['EV/Revenue']:
            implied_ev = company['revenue_ttm'] * multiples['EV/Revenue']['median']
            valuations.append(implied_ev)
        
        # EV based on EBITDA multiple
        if 'EV/EBITDA' in multiples and multiples['EV/EBITDA'] and company.get('ebitda', 0) > 0:
            implied_ev = company['ebitda'] * multiples['EV/EBITDA']['median']
            valuations.append(implied_ev)
        
        # Return results
        if valuations:
            return {
                'value': np.median(valuations),
                'value_range': {
                    'min': min(valuations),
                    'max': max(valuations)
                },
                'multiples_used': multiples,
                'comparable_companies': len(industry_comps),
                'methodology': 'Comparable Company Analysis'
            }
        else:
            return {
                'value': company['enterprise_value'],  # Default to current
                'note': 'Insufficient comparable data',
                'methodology': 'Comparable Company Analysis'
            }
    
    def precedent_transaction_analysis(
        self,
        company: pd.Series,
        precedent_deals: pd.DataFrame
    ) -> Dict:
        """
        Valuation based on precedent M&A transactions
        """
        
        # Filter relevant deals
        relevant_deals = precedent_deals.copy()
        
        # Filter by industry if possible
        if 'target_industry' in relevant_deals.columns:
            industry_deals = relevant_deals[relevant_deals['target_industry'] == company.get('industry', '')]
            if len(industry_deals) >= 5:
                relevant_deals = industry_deals
        
        # Filter by size (within 0.2x to 5x of target revenue)
        if 'target_revenue' in relevant_deals.columns:
            size_min = company['revenue_ttm'] * 0.2
            size_max = company['revenue_ttm'] * 5
            relevant_deals = relevant_deals[
                (relevant_deals['target_revenue'] >= size_min) &
                (relevant_deals['target_revenue'] <= size_max)
            ]
        
        # Filter by recency (last 2 years)
        if 'announcement_date' in relevant_deals.columns:
            recent_cutoff = pd.Timestamp.now() - pd.Timedelta(days=730)
            relevant_deals['announcement_date'] = pd.to_datetime(relevant_deals['announcement_date'])
            relevant_deals = relevant_deals[relevant_deals['announcement_date'] >= recent_cutoff]
        
        if len(relevant_deals) < 3:
            return {
                'value': company['enterprise_value'],
                'note': 'Insufficient precedent transactions',
                'methodology': 'Precedent Transaction Analysis'
            }
        
        # Calculate multiples paid
        if 'revenue_multiple_paid' in relevant_deals.columns:
            multiples = relevant_deals['revenue_multiple_paid'].dropna()
            
            # Remove outliers
            q1, q3 = multiples.quantile([0.25, 0.75])
            iqr = q3 - q1
            filtered = multiples[(multiples >= q1 - 1.5*iqr) & (multiples <= q3 + 1.5*iqr)]
            
            if len(filtered) > 0:
                # Apply premium for control
                control_premium = 1.25  # 25% control premium
                
                median_multiple = filtered.median()
                implied_value = company['revenue_ttm'] * median_multiple * control_premium
                
                return {
                    'value': implied_value,
                    'multiple_paid': median_multiple,
                    'control_premium': control_premium - 1,
                    'precedent_deals_analyzed': len(filtered),
                    'value_range': {
                        'min': company['revenue_ttm'] * filtered.quantile(0.25) * control_premium,
                        'max': company['revenue_ttm'] * filtered.quantile(0.75) * control_premium
                    },
                    'methodology': 'Precedent Transaction Analysis'
                }
        
        return {
            'value': company['enterprise_value'],
            'note': 'Unable to calculate precedent multiples',
            'methodology': 'Precedent Transaction Analysis'
        }
    
    def synergy_analysis(
        self,
        acquirer: pd.Series,
        target: pd.Series,
        integration_years: int = 3
    ) -> Dict:
        """
        Estimate potential synergies from acquisition
        """
        
        synergies = {
            'revenue_synergies': {},
            'cost_synergies': {},
            'total_value': 0
        }
        
        # Revenue synergies
        # Cross-selling opportunity
        cross_sell_rate = 0.15  # 15% of customers buy both products
        avg_revenue_per_customer = target['revenue_ttm'] / max(target.get('customer_count', 1000), 1)
        cross_sell_value = acquirer.get('customer_count', 5000) * cross_sell_rate * avg_revenue_per_customer
        
        synergies['revenue_synergies']['cross_selling'] = cross_sell_value
        
        # Market expansion
        if acquirer.get('industry') == target.get('industry'):
            market_expansion = target['revenue_ttm'] * 0.1  # 10% revenue growth from expanded reach
        else:
            market_expansion = target['revenue_ttm'] * 0.05  # 5% for different industries
        
        synergies['revenue_synergies']['market_expansion'] = market_expansion
        
        # Cost synergies
        # Overhead reduction (eliminate duplicate functions)
        overhead_savings = min(acquirer['revenue_ttm'], target['revenue_ttm']) * 0.03  # 3% of smaller company
        synergies['cost_synergies']['overhead_reduction'] = overhead_savings
        
        # Technology consolidation
        tech_savings = (acquirer['revenue_ttm'] + target['revenue_ttm']) * 0.01  # 1% from tech consolidation
        synergies['cost_synergies']['technology'] = tech_savings
        
        # Supply chain optimization
        if acquirer.get('industry') == target.get('industry'):
            supply_chain_savings = target['revenue_ttm'] * 0.02  # 2% from better terms
            synergies['cost_synergies']['supply_chain'] = supply_chain_savings
        
        # Calculate NPV of synergies
        total_annual_synergy = (
            sum(synergies['revenue_synergies'].values()) +
            sum(synergies['cost_synergies'].values())
        )
        
        # Assume synergies phase in over integration period
        discount_rate = 0.10  # 10% discount rate
        synergy_npv = 0
        
        for year in range(1, integration_years + 1):
            # Synergies phase in: 30% year 1, 60% year 2, 100% year 3+
            if year == 1:
                annual_synergy = total_annual_synergy * 0.3
            elif year == 2:
                annual_synergy = total_annual_synergy * 0.6
            else:
                annual_synergy = total_annual_synergy
            
            synergy_npv += annual_synergy / (1 + discount_rate)**year
        
        # Terminal value of synergies
        terminal_synergy = total_annual_synergy / (discount_rate - 0.02)  # 2% perpetual growth
        terminal_pv = terminal_synergy / (1 + discount_rate)**integration_years
        
        synergies['total_value'] = synergy_npv + terminal_pv
        synergies['annual_run_rate'] = total_annual_synergy
        synergies['integration_years'] = integration_years
        synergies['npv'] = synergy_npv
        synergies['terminal_value'] = terminal_pv
        
        return synergies
    
    def calculate_returns(
        self,
        purchase_price: float,
        target: pd.Series,
        exit_multiple: float = None,
        holding_period: int = 5
    ) -> Dict:
        """
        Calculate expected returns from acquisition
        """
        
        if exit_multiple is None:
            exit_multiple = target['implied_revenue_multiple']
        
        # Project target metrics at exit
        revenue_at_exit = target['revenue_ttm'] * (1 + target['revenue_growth_yoy'])**holding_period
        
        # Assume margin improvement
        current_margin = target.get('ebitda_margin', 0.15)
        improved_margin = min(current_margin + 0.05, 0.25)  # 5% improvement, capped at 25%
        ebitda_at_exit = revenue_at_exit * improved_margin
        
        # Exit value
        exit_value = revenue_at_exit * exit_multiple
        
        # Calculate returns
        total_return = exit_value / purchase_price - 1
        irr = (exit_value / purchase_price)**(1/holding_period) - 1
        
        # Money multiple
        money_multiple = exit_value / purchase_price
        
        return {
            'purchase_price': purchase_price,
            'exit_value': exit_value,
            'total_return': total_return,
            'irr': irr,
            'money_multiple': money_multiple,
            'holding_period': holding_period,
            'exit_assumptions': {
                'revenue_at_exit': revenue_at_exit,
                'ebitda_at_exit': ebitda_at_exit,
                'exit_multiple': exit_multiple,
                'margin_at_exit': improved_margin
            }
        }
