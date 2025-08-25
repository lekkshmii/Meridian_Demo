"""
Synthetic Data Generator for Meridian Demo
Generates realistic M&A target companies and deal history
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
import hashlib

class SyntheticDataGenerator:
    """Generate realistic synthetic M&A data for demos"""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with seed for reproducibility"""
        np.random.seed(seed)
        random.seed(seed)
        
        # Industry templates for realistic companies
        self.industry_profiles = {
            'SaaS': {
                'revenue_multiple': (4, 12),
                'growth_rate': (0.15, 0.80),
                'ebitda_margin': (-0.10, 0.25),
                'keywords': ['cloud', 'platform', 'automation', 'AI', 'analytics', 'workflow'],
                'sub_industries': ['CRM', 'ERP', 'HRM', 'Marketing Tech', 'DevOps', 'Security']
            },
            'Fintech': {
                'revenue_multiple': (3, 8),
                'growth_rate': (0.20, 0.60),
                'ebitda_margin': (0.05, 0.30),
                'keywords': ['payments', 'banking', 'crypto', 'lending', 'insurance', 'wealth'],
                'sub_industries': ['Payments', 'Banking-as-a-Service', 'Crypto', 'Lending', 'InsurTech', 'WealthTech']
            },
            'Healthcare IT': {
                'revenue_multiple': (2, 6),
                'growth_rate': (0.10, 0.40),
                'ebitda_margin': (0.10, 0.35),
                'keywords': ['EMR', 'telehealth', 'diagnostics', 'pharma', 'clinical', 'patient'],
                'sub_industries': ['Telehealth', 'EMR/EHR', 'Medical Devices', 'Diagnostics', 'Pharma Tech', 'Patient Engagement']
            },
            'Cybersecurity': {
                'revenue_multiple': (5, 15),
                'growth_rate': (0.25, 0.70),
                'ebitda_margin': (0.00, 0.20),
                'keywords': ['security', 'threat', 'identity', 'cloud', 'zero-trust', 'encryption'],
                'sub_industries': ['Network Security', 'Cloud Security', 'Identity Management', 'Threat Intelligence', 'Data Protection']
            },
            'Data & Analytics': {
                'revenue_multiple': (4, 10),
                'growth_rate': (0.20, 0.50),
                'ebitda_margin': (0.05, 0.25),
                'keywords': ['data', 'analytics', 'BI', 'visualization', 'lake', 'warehouse'],
                'sub_industries': ['Business Intelligence', 'Data Infrastructure', 'Analytics Platform', 'Data Governance', 'ML Ops']
            }
        }
        
        self.company_prefixes = {
            'SaaS': ['Cloud', 'Data', 'Apex', 'Vertex', 'Quantum', 'Neural', 'Synth', 'Vector', 'Matrix', 'Nexus'],
            'Fintech': ['Pay', 'Fin', 'Capital', 'Wealth', 'Trust', 'Secure', 'Prime', 'Vault', 'Ledger', 'Block'],
            'Healthcare IT': ['Med', 'Health', 'Care', 'Bio', 'Life', 'Vital', 'Clinical', 'Patient', 'Cure', 'Heal'],
            'Cybersecurity': ['Shield', 'Guard', 'Secure', 'Protect', 'Cyber', 'Fort', 'Safe', 'Lock', 'Defense', 'Sentinel'],
            'Data & Analytics': ['Insight', 'Vision', 'Intel', 'Smart', 'Wise', 'Clear', 'Deep', 'Meta', 'Info', 'Know']
        }
        
        self.company_suffixes = ['Technologies', 'Solutions', 'Systems', 'AI', 'Labs', 
                                 'Digital', 'Cloud', 'Analytics', 'Software', 'Platform',
                                 'Tech', 'Works', 'Hub', 'Pro', 'Plus']
        
        self.cities = [
            ('San Francisco', 'CA'), ('New York', 'NY'), ('Austin', 'TX'), 
            ('Boston', 'MA'), ('Seattle', 'WA'), ('Denver', 'CO'),
            ('Chicago', 'IL'), ('Los Angeles', 'CA'), ('Miami', 'FL'),
            ('Atlanta', 'GA'), ('Phoenix', 'AZ'), ('Portland', 'OR'),
            ('San Diego', 'CA'), ('Dallas', 'TX'), ('Washington', 'DC'),
            ('Raleigh', 'NC'), ('Nashville', 'TN'), ('Salt Lake City', 'UT')
        ]
        
    def generate_company_universe(self, n: int = 5000) -> pd.DataFrame:
        """Generate a universe of realistic M&A target companies"""
        companies = []
        
        for i in range(n):
            industry = random.choice(list(self.industry_profiles.keys()))
            profile = self.industry_profiles[industry]
            
            # Generate base metrics with realistic distributions
            revenue = np.random.lognormal(17.5, 1.3)  # Log-normal distribution
            revenue = max(5_000_000, min(revenue, 1_000_000_000))  # Bound between 5M-1B
            
            # Industry-specific characteristics
            growth = np.random.uniform(*profile['growth_rate'])
            
            # Add some variance to make it realistic
            if random.random() < 0.1:  # 10% are high flyers
                growth *= 1.5
            elif random.random() < 0.1:  # 10% are struggling
                growth *= 0.5
            
            ebitda_margin = np.random.normal(np.mean(profile['ebitda_margin']), 0.08)
            revenue_multiple = np.random.uniform(*profile['revenue_multiple'])
            
            # Create realistic company
            company = {
                'company_id': f"COMP_{str(i).zfill(5)}",
                'name': self._generate_company_name(industry),
                'industry': industry,
                'sub_industry': random.choice(profile['sub_industries']),
                'founded_year': 2024 - np.random.poisson(8),  # Average 8 years old
                'headquarters': self._generate_location(),
                'employees': int(revenue / np.random.uniform(120_000, 350_000)),
                'website': self._generate_website(self._generate_company_name(industry)),
                
                # Financials
                'revenue_ttm': revenue,
                'revenue_growth_yoy': growth,
                'revenue_growth_3y_cagr': growth * np.random.uniform(0.8, 1.2),
                'ebitda': revenue * ebitda_margin,
                'ebitda_margin': ebitda_margin,
                'gross_margin': ebitda_margin + np.random.uniform(0.25, 0.45),
                'operating_margin': ebitda_margin - np.random.uniform(0.02, 0.08),
                'debt_to_equity': max(0, np.random.normal(0.4, 0.25)),
                'cash_balance': revenue * np.random.uniform(0.1, 0.5),
                'burn_rate_monthly': revenue / 12 * np.random.uniform(0.08, 0.15) if ebitda_margin < 0 else 0,
                
                # Valuation
                'enterprise_value': revenue * revenue_multiple,
                'implied_revenue_multiple': revenue_multiple,
                'implied_ebitda_multiple': revenue_multiple / max(0.01, ebitda_margin) if ebitda_margin > 0 else None,
                'last_funding_round': random.choice(['Series A', 'Series B', 'Series C', 'Series D', 'Private', 'Bootstrapped']),
                'valuation_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                
                # Strategic metrics
                'customer_count': int(np.random.lognormal(6, 1.5)),
                'customer_concentration': np.random.beta(2, 5),  # Usually low
                'nps_score': np.random.normal(35, 20),
                'market_share': np.random.beta(2, 10),
                'tech_stack_modernity': np.random.uniform(0.4, 0.95),
                'product_market_fit': random.choice(['Strong', 'Good', 'Developing', 'Early']),
                'competitive_position': random.choice(['Leader', 'Challenger', 'Follower', 'Niche']),
                
                # M&A readiness indicators
                'has_audited_financials': random.random() > 0.3,
                'management_staying': random.random() > 0.4,
                'clean_cap_table': random.random() > 0.5,
                'proprietary_tech': random.random() > 0.6,
                'regulatory_issues': random.random() < 0.1,  # 10% have issues
                'litigation_pending': random.random() < 0.05,  # 5% have litigation
                
                # Hidden gems and special flags
                'is_undervalued': random.random() > 0.95,  # 5% are hidden gems
                'is_distressed': random.random() < 0.03,  # 3% are distressed
                'acquisition_interest': random.choice(['High', 'Medium', 'Low', 'None']),
                'strategic_value': random.choice(['Transformational', 'High', 'Medium', 'Low']),
            }
            
            # Adjust valuation for special cases
            if company['is_undervalued']:
                discount = np.random.uniform(0.4, 0.7)
                company['enterprise_value'] *= discount
                company['implied_revenue_multiple'] *= discount
                company['notes'] = "Undervalued due to market conditions"
            
            if company['is_distressed']:
                discount = np.random.uniform(0.3, 0.6)
                company['enterprise_value'] *= discount
                company['implied_revenue_multiple'] *= discount
                company['notes'] = "Distressed sale opportunity"
                company['ebitda_margin'] = -abs(company['ebitda_margin'])
                company['ebitda'] = company['revenue_ttm'] * company['ebitda_margin']
            
            companies.append(company)
        
        df = pd.DataFrame(companies)
        
        # Add some correlations to make data more realistic
        # High growth companies tend to have lower margins
        high_growth = df['revenue_growth_yoy'] > 0.5
        df.loc[high_growth, 'ebitda_margin'] -= 0.1
        
        # Older companies tend to be more profitable
        older = df['founded_year'] < 2015
        df.loc[older, 'ebitda_margin'] += 0.05
        
        return df
    
    def _generate_company_name(self, industry: str) -> str:
        """Generate believable company names"""
        prefix = random.choice(self.company_prefixes.get(industry, ['Tech', 'Global', 'Next']))
        
        # Sometimes add a modifier
        if random.random() < 0.3:
            modifiers = ['X', 'Pro', 'Max', 'Plus', 'One', 'Core', 'Prime', 'Edge']
            prefix = prefix + random.choice(modifiers)
        
        suffix = random.choice(self.company_suffixes)
        
        # Sometimes use .io or similar
        if random.random() < 0.15 and industry in ['SaaS', 'Data & Analytics']:
            return f"{prefix}.io"
        
        return f"{prefix} {suffix}"
    
    def _generate_location(self) -> str:
        """Generate realistic headquarters location"""
        city, state = random.choice(self.cities)
        return f"{city}, {state}"
    
    def _generate_website(self, company_name: str) -> str:
        """Generate website URL from company name"""
        # Clean the company name for URL
        url_name = company_name.lower().replace(' ', '').replace('.io', '')
        
        # Add appropriate TLD
        if '.io' in company_name.lower():
            return f"https://{url_name}.io"
        elif random.random() < 0.3:
            return f"https://{url_name}.ai"
        else:
            return f"https://{url_name}.com"
    
    def _get_sub_industry(self, industry: str) -> str:
        """Get sub-industry for a given industry"""
        return random.choice(self.industry_profiles[industry]['sub_industries'])
    
    def generate_deal_history(self, n: int = 500) -> pd.DataFrame:
        """Generate historical M&A transactions for pattern learning"""
        deals = []
        
        industries = list(self.industry_profiles.keys())
        
        for i in range(n):
            acquirer_industry = random.choice(industries)
            target_industry = random.choice(industries)
            
            # Same industry deals are more common
            if random.random() < 0.6:
                target_industry = acquirer_industry
            
            deal = {
                'deal_id': f"DEAL_{str(i).zfill(4)}",
                'announcement_date': datetime.now() - timedelta(days=random.randint(30, 1095)),
                'closing_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                
                # Acquirer details
                'acquirer_name': self._generate_company_name(acquirer_industry),
                'acquirer_industry': acquirer_industry,
                'acquirer_revenue': np.random.lognormal(20, 1),
                'acquirer_market_cap': np.random.lognormal(21, 1.2),
                
                # Target details
                'target_name': self._generate_company_name(target_industry),
                'target_industry': target_industry,
                'target_revenue': np.random.lognormal(18, 1),
                'target_employees': random.randint(50, 5000),
                
                # Deal details
                'deal_value': np.random.lognormal(19, 1.2),
                'revenue_multiple_paid': np.random.uniform(2, 15),
                'premium_paid': np.random.uniform(0.1, 0.5),  # 10-50% premium
                'payment_type': random.choice(['Cash', 'Stock', 'Mixed']),
                'deal_type': random.choice(['Acquisition', 'Merger', 'Asset Purchase']),
                
                # Outcomes
                'deal_success': random.random() > 0.25,  # 75% success rate
                'integration_months': np.random.poisson(14),
                'synergy_realized': np.random.uniform(0.6, 1.4) if random.random() > 0.3 else 0,
                'revenue_retention': np.random.uniform(0.85, 1.05),
                
                # Strategic details
                'strategic_rationale': random.choice([
                    'Market expansion', 'Technology acquisition', 'Talent acquisition',
                    'Vertical integration', 'Geographic expansion', 'Product expansion',
                    'Cost synergies', 'Customer base expansion', 'Competitive consolidation'
                ]),
                'integration_difficulty': random.choice(['Low', 'Medium', 'High']),
                'cultural_fit_score': np.random.uniform(0.3, 0.9),
            }
            
            # Add some realistic correlations
            if deal['strategic_rationale'] == 'Talent acquisition':
                deal['deal_value'] = deal['target_employees'] * np.random.uniform(500_000, 2_000_000)
            
            if deal['payment_type'] == 'Cash':
                deal['premium_paid'] *= 1.2  # Cash deals typically pay higher premiums
            
            deals.append(deal)
        
        return pd.DataFrame(deals)
    
    def generate_market_comparables(self, industry: str, n: int = 20) -> pd.DataFrame:
        """Generate comparable public companies for valuation"""
        comparables = []
        
        profile = self.industry_profiles[industry]
        
        for i in range(n):
            comp = {
                'ticker': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 4))),
                'company_name': self._generate_company_name(industry),
                'market_cap': np.random.lognormal(21, 1.5),
                'enterprise_value': np.random.lognormal(21, 1.5),
                'revenue_ttm': np.random.lognormal(19, 1.3),
                'ebitda_ttm': np.random.lognormal(18, 1.5),
                'revenue_growth': np.random.uniform(*profile['growth_rate']),
                'ebitda_margin': np.random.normal(np.mean(profile['ebitda_margin']), 0.1),
                'ev_revenue': np.random.uniform(*profile['revenue_multiple']),
                'ev_ebitda': np.random.uniform(8, 25),
                'pe_ratio': np.random.uniform(15, 50),
                'price_to_book': np.random.uniform(2, 10),
            }
            
            # Ensure consistency
            comp['ev_revenue'] = comp['enterprise_value'] / comp['revenue_ttm']
            if comp['ebitda_ttm'] > 0:
                comp['ev_ebitda'] = comp['enterprise_value'] / comp['ebitda_ttm']
            
            comparables.append(comp)
        
        return pd.DataFrame(comparables)
    
    def save_all_data(self, output_dir: str = "data"):
        """Generate and save all synthetic datasets"""
        import os
        
        print("Generating synthetic data...")
        
        # Generate main datasets
        companies = self.generate_company_universe(5000)
        deals = self.generate_deal_history(500)
        
        # Generate comparables for each industry
        comparables = {}
        for industry in self.industry_profiles.keys():
            comparables[industry] = self.generate_market_comparables(industry, 30)
        
        # Save to parquet files
        companies.to_parquet(f"{output_dir}/synthetic_universe.parquet", index=False)
        deals.to_parquet(f"{output_dir}/historical_deals.parquet", index=False)
        
        # Save comparables
        for industry, df in comparables.items():
            safe_name = industry.replace(' ', '_').replace('&', 'and')
            df.to_parquet(f"{output_dir}/comparables_{safe_name}.parquet", index=False)
        
        print(f"✓ Generated {len(companies):,} companies")
        print(f"✓ Generated {len(deals):,} historical deals")
        print(f"✓ Generated comparables for {len(comparables)} industries")
        print(f"✓ All data saved to {output_dir}/")
        
        return companies, deals, comparables

if __name__ == "__main__":
    # Generate all synthetic data
    generator = SyntheticDataGenerator()
    companies, deals, comparables = generator.save_all_data()
    
    # Print sample statistics
    print("\nSample Statistics:")
    print("-" * 50)
    print(f"Revenue range: ${companies['revenue_ttm'].min():,.0f} - ${companies['revenue_ttm'].max():,.0f}")
    print(f"Average growth rate: {companies['revenue_growth_yoy'].mean():.1%}")
    print(f"Profitable companies: {(companies['ebitda'] > 0).sum():,} ({(companies['ebitda'] > 0).mean():.1%})")
    print(f"Undervalued targets: {companies['is_undervalued'].sum()}")
    print(f"Distressed opportunities: {companies['is_distressed'].sum()}")
