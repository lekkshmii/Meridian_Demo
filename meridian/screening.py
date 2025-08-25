"""
Screening Engine for Meridian M&A Platform
Multi-criteria filtering and scoring of acquisition targets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ScreeningEngine:
    """Advanced M&A target screening with multi-dimensional scoring"""
    
    def __init__(self, company_universe: pd.DataFrame):
        """Initialize with company universe data"""
        self.universe = company_universe
        self.screening_history = []
        self.last_results = None
        
        # Industry median multiples for valuation comparison
        self._calculate_industry_benchmarks()
    
    def _calculate_industry_benchmarks(self):
        """Calculate industry benchmarks for relative valuation"""
        self.industry_medians = self.universe.groupby('industry').agg({
            'implied_revenue_multiple': 'median',
            'revenue_growth_yoy': 'median',
            'ebitda_margin': 'median',
            'debt_to_equity': 'median'
        }).to_dict('index')
    
    def screen(
        self,
        # Financial criteria
        min_revenue: float = 0,
        max_revenue: float = float('inf'),
        min_growth: float = 0,
        max_growth: float = float('inf'),
        min_ebitda_margin: float = -float('inf'),
        max_ebitda_margin: float = float('inf'),
        
        # Industry and geography
        industries: Optional[List[str]] = None,
        sub_industries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        
        # Valuation criteria
        max_revenue_multiple: float = float('inf'),
        max_debt_ratio: float = float('inf'),
        
        # Strategic criteria
        require_profitability: bool = False,
        require_audited_financials: bool = False,
        exclude_distressed: bool = True,
        
        # Scoring weights
        weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Comprehensive screening with multi-stage filtering
        Returns scored and ranked targets
        """
        
        # Default weights if not provided
        if weights is None:
            weights = {
                'strategic': 0.35,
                'valuation': 0.35,
                'financial': 0.20,
                'risk': 0.10
            }
        
        # Start with full universe
        results = self.universe.copy()
        initial_count = len(results)
        
        # Track filtering funnel for reporting
        funnel = {'initial': initial_count}
        
        # === Stage 1: Hard Filters ===
        
        # Revenue filter
        results = results[
            (results['revenue_ttm'] >= min_revenue) & 
            (results['revenue_ttm'] <= max_revenue)
        ]
        funnel['revenue_filter'] = len(results)
        
        # Growth filter
        results = results[
            (results['revenue_growth_yoy'] >= min_growth) &
            (results['revenue_growth_yoy'] <= max_growth)
        ]
        funnel['growth_filter'] = len(results)
        
        # Profitability filters
        if require_profitability:
            results = results[results['ebitda'] > 0]
            funnel['profitable_only'] = len(results)
        else:
            results = results[results['ebitda_margin'] >= min_ebitda_margin]
            results = results[results['ebitda_margin'] <= max_ebitda_margin]
            funnel['margin_filter'] = len(results)
        
        # Industry filter
        if industries:
            results = results[results['industry'].isin(industries)]
            funnel['industry_filter'] = len(results)
        
        if sub_industries:
            results = results[results['sub_industry'].isin(sub_industries)]
            funnel['sub_industry_filter'] = len(results)
        
        # Location filter
        if locations:
            results = results[results['headquarters'].str.contains('|'.join(locations), case=False, na=False)]
            funnel['location_filter'] = len(results)
        
        # Valuation filter
        results = results[results['implied_revenue_multiple'] <= max_revenue_multiple]
        funnel['valuation_filter'] = len(results)
        
        # Debt filter
        results = results[results['debt_to_equity'] <= max_debt_ratio]
        funnel['debt_filter'] = len(results)
        
        # Quality filters
        if require_audited_financials:
            results = results[results['has_audited_financials'] == True]
            funnel['audited_financials'] = len(results)
        
        if exclude_distressed:
            results = results[results['is_distressed'] == False]
            funnel['exclude_distressed'] = len(results)
        
        # === Stage 2: Scoring ===
        
        # Calculate component scores
        results['strategic_score'] = self._calculate_strategic_score(results)
        results['valuation_score'] = self._calculate_valuation_score(results)
        results['financial_score'] = self._calculate_financial_score(results)
        results['risk_score'] = self._calculate_risk_score(results)
        
        # Calculate weighted total score
        results['total_score'] = (
            results['strategic_score'] * weights['strategic'] +
            results['valuation_score'] * weights['valuation'] +
            results['financial_score'] * weights['financial'] +
            (100 - results['risk_score']) * weights['risk']  # Invert risk score
        )
        
        # Add scoring components
        results['score_components'] = results.apply(
            lambda row: {
                'strategic': row['strategic_score'],
                'valuation': row['valuation_score'],
                'financial': row['financial_score'],
                'risk': row['risk_score']
            }, axis=1
        )
        
        # === Stage 3: Ranking and Categorization ===
        
        # Sort by total score
        results = results.sort_values('total_score', ascending=False)
        
        # Add rank
        results['rank'] = range(1, len(results) + 1)
        
        # Categorize targets
        results['category'] = pd.cut(
            results['total_score'],
            bins=[0, 50, 70, 85, 100],
            labels=['Monitor', 'Opportunistic', 'Priority', 'Immediate Action']
        )
        
        # Add acquisition recommendation
        results['recommendation'] = results.apply(self._generate_recommendation, axis=1)
        
        # === Stage 4: Save Results ===
        
        # Store screening metadata
        self.last_results = results
        self.screening_history.append({
            'timestamp': datetime.now(),
            'criteria': {
                'min_revenue': min_revenue,
                'max_revenue': max_revenue,
                'min_growth': min_growth,
                'industries': industries,
                'require_profitability': require_profitability
            },
            'funnel': funnel,
            'results_count': len(results),
            'top_score': results['total_score'].max() if len(results) > 0 else 0
        })
        
        return results
    
    def _calculate_strategic_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate strategic fit score (0-100)"""
        score = pd.Series(0.0, index=df.index)
        
        # Growth potential (30 points)
        growth_percentile = df['revenue_growth_yoy'].rank(pct=True)
        score += growth_percentile * 30
        
        # Market position (20 points)
        market_share_percentile = df['market_share'].rank(pct=True)
        score += market_share_percentile * 20
        
        # Technology advantage (20 points)
        tech_score = df['tech_stack_modernity'] * 10
        tech_score += df['proprietary_tech'].astype(int) * 10
        score += tech_score
        
        # Customer metrics (15 points)
        # Normalize NPS score (-100 to 100) to 0-1
        nps_normalized = (df['nps_score'] + 100) / 200
        score += nps_normalized * 10
        
        # Lower customer concentration is better
        score += (1 - df['customer_concentration']) * 5
        
        # Product-market fit (15 points)
        pmf_scores = {
            'Strong': 15,
            'Good': 10,
            'Developing': 5,
            'Early': 2
        }
        score += df['product_market_fit'].map(pmf_scores).fillna(0)
        
        return np.clip(score, 0, 100)
    
    def _calculate_valuation_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate valuation attractiveness score (0-100)"""
        score = pd.Series(0.0, index=df.index)
        
        # Compare to industry medians
        for idx, row in df.iterrows():
            industry = row['industry']
            if industry in self.industry_medians:
                median_multiple = self.industry_medians[industry]['implied_revenue_multiple']
                
                # Calculate discount/premium to median
                if pd.notna(row['implied_revenue_multiple']) and median_multiple > 0:
                    discount = (median_multiple - row['implied_revenue_multiple']) / median_multiple
                    
                    # Positive score for discounts, negative for premiums
                    if discount > 0:
                        # Max 50 points for 50%+ discount
                        score.loc[idx] += min(50, discount * 100)
                    else:
                        # Penalty for premium valuations
                        score.loc[idx] += max(-20, discount * 40)
        
        # Bonus for identified undervalued companies (30 points)
        score += df['is_undervalued'].astype(int) * 30
        
        # Bonus for distressed sales (20 points)
        score += df['is_distressed'].astype(int) * 20
        
        # Adjust for absolute valuation levels
        # Lower absolute multiples get bonus points
        multiple_bonus = pd.Series(0.0, index=df.index)
        multiple_bonus[df['implied_revenue_multiple'] < 3] = 10
        multiple_bonus[df['implied_revenue_multiple'] < 2] = 20
        score += multiple_bonus
        
        return np.clip(score, 0, 100)
    
    def _calculate_financial_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate financial health score (0-100)"""
        score = pd.Series(0.0, index=df.index)
        
        # Profitability (40 points)
        # EBITDA margin percentile
        margin_percentile = df['ebitda_margin'].rank(pct=True)
        score += margin_percentile * 20
        
        # Absolute profitability bonus
        score += (df['ebitda'] > 0).astype(int) * 10
        score += (df['ebitda_margin'] > 0.2).astype(int) * 10
        
        # Growth consistency (30 points)
        # 3-year CAGR vs 1-year growth
        growth_consistency = 1 - abs(df['revenue_growth_3y_cagr'] - df['revenue_growth_yoy']) / df['revenue_growth_yoy'].clip(lower=0.01)
        score += growth_consistency.clip(0, 1) * 30
        
        # Capital efficiency (30 points)
        # Lower debt is better
        debt_score = (1 - df['debt_to_equity'].clip(0, 1)) * 15
        score += debt_score
        
        # Cash position
        cash_score = (df['cash_balance'] / df['revenue_ttm']).clip(0, 0.5) * 30
        score += cash_score
        
        return np.clip(score, 0, 100)
    
    def _calculate_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate risk score (0-100, higher is riskier)"""
        risk = pd.Series(0.0, index=df.index)
        
        # Customer concentration risk (25 points)
        risk += df['customer_concentration'] * 25
        
        # Financial risk (25 points)
        # High debt
        risk += df['debt_to_equity'].clip(0, 2) / 2 * 15
        
        # Negative margins
        risk += (df['ebitda_margin'] < 0).astype(int) * 10
        
        # Integration risk (25 points)
        risk += (~df['management_staying']).astype(int) * 10
        risk += (~df['clean_cap_table']).astype(int) * 10
        risk += (~df['has_audited_financials']).astype(int) * 5
        
        # Legal/regulatory risk (25 points)
        risk += df['regulatory_issues'].astype(int) * 15
        risk += df['litigation_pending'].astype(int) * 10
        
        return np.clip(risk, 0, 100)
    
    def _generate_recommendation(self, row: pd.Series) -> str:
        """Generate specific acquisition recommendation"""
        
        if row['total_score'] >= 85:
            if row['is_undervalued']:
                return "IMMEDIATE ACTION - Undervalued target with strong fundamentals"
            elif row['revenue_growth_yoy'] > 0.5:
                return "IMMEDIATE ACTION - High growth target in strategic segment"
            else:
                return "IMMEDIATE ACTION - Premium target meets all criteria"
        
        elif row['total_score'] >= 70:
            if row['valuation_score'] > 80:
                return "PRIORITY - Attractive valuation, initiate discussions"
            elif row['strategic_score'] > 80:
                return "PRIORITY - Strong strategic fit, explore synergies"
            else:
                return "PRIORITY - Balanced opportunity across metrics"
        
        elif row['total_score'] >= 50:
            if row['is_distressed']:
                return "OPPORTUNISTIC - Distressed asset, negotiate aggressively"
            elif row['risk_score'] > 60:
                return "OPPORTUNISTIC - Higher risk, requires due diligence"
            else:
                return "OPPORTUNISTIC - Monitor for improved conditions"
        
        else:
            return "MONITOR - Does not meet current acquisition criteria"
    
    def get_screening_summary(self) -> Dict:
        """Get summary statistics of last screening"""
        if self.last_results is None:
            return {}
        
        results = self.last_results
        
        return {
            'total_targets': len(results),
            'immediate_action': len(results[results['category'] == 'Immediate Action']),
            'priority': len(results[results['category'] == 'Priority']),
            'average_score': results['total_score'].mean(),
            'top_target': results.iloc[0]['name'] if len(results) > 0 else None,
            'undervalued_count': results['is_undervalued'].sum(),
            'avg_revenue': results['revenue_ttm'].mean(),
            'avg_growth': results['revenue_growth_yoy'].mean(),
            'profitable_pct': (results['ebitda'] > 0).mean()
        }
    
    def export_results(self, top_n: int = 50, filename: str = None) -> pd.DataFrame:
        """Export screening results to Excel"""
        if self.last_results is None:
            return pd.DataFrame()
        
        # Select key columns for export
        export_columns = [
            'rank', 'name', 'industry', 'sub_industry', 'headquarters',
            'revenue_ttm', 'revenue_growth_yoy', 'ebitda_margin',
            'implied_revenue_multiple', 'enterprise_value',
            'total_score', 'category', 'recommendation',
            'strategic_score', 'valuation_score', 'financial_score', 'risk_score'
        ]
        
        export_df = self.last_results[export_columns].head(top_n)
        
        # Format financial columns
        export_df['revenue_ttm'] = export_df['revenue_ttm'].apply(lambda x: f"${x:,.0f}")
        export_df['enterprise_value'] = export_df['enterprise_value'].apply(lambda x: f"${x:,.0f}")
        export_df['revenue_growth_yoy'] = export_df['revenue_growth_yoy'].apply(lambda x: f"{x:.1%}")
        export_df['ebitda_margin'] = export_df['ebitda_margin'].apply(lambda x: f"{x:.1%}")
        
        if filename:
            export_df.to_excel(filename, index=False)
            print(f"Results exported to {filename}")
        
        return export_df
