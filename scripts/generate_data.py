"""
Generate all synthetic data for Meridian demo
Run this script first to create the data files
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meridian.synthetic_data import SyntheticDataGenerator
import pandas as pd

def main():
    print("="*60)
    print("MERIDIAN DATA GENERATION")
    print("="*60)
    
    # Initialize generator
    generator = SyntheticDataGenerator(seed=42)
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    print("\nGenerating synthetic data...")
    print("-"*40)
    
    # Generate main company universe
    print("Creating company universe...")
    companies = generator.generate_company_universe(5000)
    companies.to_parquet(os.path.join(data_dir, 'synthetic_universe.parquet'), index=False)
    print(f"✓ Generated {len(companies):,} companies")
    
    # Generate historical deals
    print("Creating historical M&A transactions...")
    deals = generator.generate_deal_history(500)
    deals.to_parquet(os.path.join(data_dir, 'historical_deals.parquet'), index=False)
    print(f"✓ Generated {len(deals):,} historical deals")
    
    # Generate comparables for each industry
    print("Creating comparable company data...")
    for industry in generator.industry_profiles.keys():
        comparables = generator.generate_market_comparables(industry, 30)
        safe_name = industry.replace(' ', '_').replace('&', 'and')
        comparables.to_parquet(os.path.join(data_dir, f'comparables_{safe_name}.parquet'), index=False)
        print(f"✓ Generated {len(comparables)} comparables for {industry}")
    
    print("\n" + "="*60)
    print("DATA GENERATION COMPLETE")
    print("="*60)
    
    # Display statistics
    print("\nDataset Statistics:")
    print("-"*40)
    print(f"Companies: {len(companies):,}")
    print(f"Industries: {companies['industry'].nunique()}")
    print(f"Revenue Range: ${companies['revenue_ttm'].min():,.0f} - ${companies['revenue_ttm'].max():,.0f}")
    print(f"Average Growth: {companies['revenue_growth_yoy'].mean():.1%}")
    print(f"Profitable: {(companies['ebitda'] > 0).mean():.1%}")
    print(f"Undervalued: {companies['is_undervalued'].sum()}")
    print(f"Distressed: {companies['is_distressed'].sum()}")
    
    print(f"\nAll data saved to: {data_dir}")
    print("\nYou can now run the Jupyter notebooks for demos.")

if __name__ == "__main__":
    main()
