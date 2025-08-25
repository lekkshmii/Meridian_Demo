"""
Meridian M&A Intelligence Platform
Interactive Dashboard using Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meridian import ScreeningEngine, ValuationEngine, IntelligenceAnalyzer
from meridian.visualizations import *

# Page configuration
st.set_page_config(
    page_title="Meridian M&A Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        color: #1e3a8a;
    }
    .stMetric {
        background-color: #f3f4f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'screening_results' not in st.session_state:
    st.session_state.screening_results = None
if 'selected_target' not in st.session_state:
    st.session_state.selected_target = None

# Load data
@st.cache_data
def load_data():
    """Load company universe data"""
    data_path = 'data/synthetic_universe.parquet'
    if os.path.exists(data_path):
        return pd.read_parquet(data_path)
    else:
        st.error("Data not found. Please run scripts/generate_data.py first.")
        return pd.DataFrame()

# Main app
def main():
    # Header
    st.title("Meridian M&A Intelligence Platform")
    st.markdown("**AI-Powered Target Screening & Strategic Analysis**")
    st.markdown("---")
    
    # Load data
    companies = load_data()
    
    if companies.empty:
        st.stop()
    
    # Initialize engines
    screener = ScreeningEngine(companies)
    analyzer = IntelligenceAnalyzer()
    valuation_engine = ValuationEngine()
    
    # Sidebar - Screening Criteria
    with st.sidebar:
        st.header("Screening Criteria")
        
        # Revenue range
        st.subheader("Revenue Range")
        col1, col2 = st.columns(2)
        with col1:
            min_revenue = st.number_input(
                "Min ($M)",
                min_value=0,
                max_value=1000,
                value=20,
                step=10
            ) * 1_000_000
        with col2:
            max_revenue = st.number_input(
                "Max ($M)",
                min_value=0,
                max_value=1000,
                value=200,
                step=10
            ) * 1_000_000
        
        # Growth rate
        st.subheader("Growth Rate")
        min_growth = st.slider(
            "Minimum Growth (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5
        ) / 100
        
        # Industries
        st.subheader("Industries")
        all_industries = companies['industry'].unique()
        selected_industries = st.multiselect(
            "Select Industries",
            options=all_industries,
            default=['SaaS', 'Fintech']
        )
        
        # Profitability
        st.subheader("Financial Criteria")
        require_profitability = st.checkbox("Profitable Only", value=False)
        exclude_distressed = st.checkbox("Exclude Distressed", value=True)
        
        # EBITDA margin
        if not require_profitability:
            min_ebitda = st.slider(
                "Min EBITDA Margin (%)",
                min_value=-20,
                max_value=20,
                value=-5,
                step=5
            ) / 100
        else:
            min_ebitda = 0
        
        # Run screening button
        if st.button("Run Screening", type="primary", use_container_width=True):
            with st.spinner("Analyzing targets..."):
                results = screener.screen(
                    min_revenue=min_revenue,
                    max_revenue=max_revenue,
                    min_growth=min_growth,
                    min_ebitda_margin=min_ebitda,
                    industries=selected_industries,
                    require_profitability=require_profitability,
                    exclude_distressed=exclude_distressed
                )
                st.session_state.screening_results = results
                st.success(f"Found {len(results)} targets!")
    
    # Main content area
    if st.session_state.screening_results is not None:
        results = st.session_state.screening_results
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview",
            "Top Targets",
            "Analysis",
            "Valuation",
            "Report"
        ])
        
        with tab1:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Targets",
                    f"{len(results):,}",
                    f"From {len(companies):,} screened"
                )
            
            with col2:
                immediate = len(results[results['category'] == 'Immediate Action'])
                st.metric(
                    "Immediate Action",
                    immediate,
                    "High priority"
                )
            
            with col3:
                avg_score = results['total_score'].mean()
                st.metric(
                    "Average Score",
                    f"{avg_score:.1f}",
                    "Out of 100"
                )
            
            with col4:
                undervalued = results['is_undervalued'].sum()
                st.metric(
                    "Undervalued",
                    undervalued,
                    "Hidden gems"
                )
            
            # Screening funnel
            st.subheader("Screening Funnel")
            if screener.screening_history:
                funnel_data = screener.screening_history[-1]['funnel']
                fig = create_screening_funnel(funnel_data)
                st.plotly_chart(fig, use_container_width=True)
            
            # Industry distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Industry Distribution")
                industry_counts = results['industry'].value_counts()
                fig = px.pie(
                    values=industry_counts.values,
                    names=industry_counts.index,
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Risk Distribution")
                risk_bins = pd.cut(
                    results['risk_score'],
                    bins=[0, 30, 60, 100],
                    labels=['Low', 'Medium', 'High']
                )
                risk_counts = risk_bins.value_counts()
                fig = px.bar(
                    x=risk_counts.index,
                    y=risk_counts.values,
                    color=risk_counts.index,
                    color_discrete_map={
                        'Low': '#10b981',
                        'Medium': '#f59e0b',
                        'High': '#ef4444'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Top Acquisition Targets")
            
            # Number of targets to show
            n_targets = st.slider("Number of targets to display", 5, 50, 10)
            top_targets = results.head(n_targets)
            
            # Strategic positioning chart
            fig = create_target_scatter(
                top_targets,
                title="Strategic Positioning Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Target table
            st.subheader("Target Details")
            
            # Format display columns
            display_cols = [
                'rank', 'name', 'industry', 'revenue_ttm',
                'revenue_growth_yoy', 'ebitda_margin',
                'total_score', 'category'
            ]
            
            display_df = top_targets[display_cols].copy()
            display_df['revenue_ttm'] = display_df['revenue_ttm'].apply(lambda x: f"${x/1e6:.1f}M")
            display_df['revenue_growth_yoy'] = display_df['revenue_growth_yoy'].apply(lambda x: f"{x:.1%}")
            display_df['ebitda_margin'] = display_df['ebitda_margin'].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )
            
            # Select target for deep dive
            target_names = top_targets['name'].tolist()
            selected_name = st.selectbox(
                "Select target for detailed analysis",
                options=target_names
            )
            
            if selected_name:
                st.session_state.selected_target = top_targets[
                    top_targets['name'] == selected_name
                ].iloc[0]
        
        with tab3:
            if st.session_state.selected_target is not None:
                target = st.session_state.selected_target
                
                st.subheader(f"Strategic Analysis: {target['name']}")
                
                # Company overview
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Industry", target['industry'])
                    st.metric("Employees", f"{target['employees']:,}")
                
                with col2:
                    st.metric("Revenue", f"${target['revenue_ttm']/1e6:.1f}M")
                    st.metric("Growth", f"{target['revenue_growth_yoy']:.1%}")
                
                with col3:
                    st.metric("EBITDA Margin", f"{target['ebitda_margin']:.1%}")
                    st.metric("Score", f"{target['total_score']:.1f}")
                
                # AI Analysis
                st.subheader("AI-Powered Strategic Fit")
                
                if st.button("Run AI Analysis"):
                    with st.spinner("Analyzing strategic fit..."):
                        # Mock acquirer
                        acquirer = {
                            'industry': 'SaaS',
                            'revenue': 500_000_000,
                            'founded_year': 2010
                        }
                        
                        analysis = analyzer.analyze_strategic_fit(
                            acquirer,
                            target.to_dict()
                        )
                        
                        # Display radar chart
                        fig = create_strategic_fit_radar(
                            analysis['scores'],
                            target['name']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display insights
                        st.subheader("Key Insights")
                        for insight in analysis['insights']:
                            st.info(insight)
                        
                        # Recommendation
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Recommendation", analysis['recommendation'])
                        with col2:
                            st.metric("Confidence", f"{analysis['confidence']:.1%}")
            else:
                st.info("Please select a target from the Top Targets tab")
        
        with tab4:
            if st.session_state.selected_target is not None:
                target = st.session_state.selected_target
                
                st.subheader(f"Valuation Analysis: {target['name']}")
                
                # Current valuation
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Enterprise Value",
                        f"${target['enterprise_value']/1e6:.1f}M"
                    )
                
                with col2:
                    st.metric(
                        "Revenue Multiple",
                        f"{target['implied_revenue_multiple']:.1f}x"
                    )
                
                with col3:
                    if target['is_undervalued']:
                        st.success("UNDERVALUED")
                    else:
                        st.info("Fair Value")
                
                # Run valuation
                if st.button("Run Valuation Analysis"):
                    with st.spinner("Calculating valuations..."):
                        # Perform DCF
                        dcf_result = valuation_engine.dcf_valuation(target)
                        
                        st.subheader("DCF Valuation")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                "DCF Value",
                                f"${dcf_result['value']/1e6:.1f}M"
                            )
                            st.metric(
                                "Implied Return",
                                f"{(dcf_result['value']/target['enterprise_value'] - 1):.1%}"
                            )
                        
                        with col2:
                            st.metric("WACC", f"{dcf_result['wacc']:.1%}")
                            st.metric(
                                "Terminal Growth",
                                f"{dcf_result['terminal_growth']:.1%}"
                            )
                        
                        # Valuation summary
                        valuations = {
                            'DCF': {'value': dcf_result['value']},
                            'Current Market': {'value': target['enterprise_value']}
                        }
                        
                        fig = create_valuation_football_field(
                            valuations,
                            target['enterprise_value'],
                            target['name']
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select a target from the Top Targets tab")
        
        with tab5:
            st.subheader("Executive Report")
            
            if st.button("Generate Executive Report"):
                with st.spinner("Generating report..."):
                    report = analyzer.generate_executive_summary(
                        results,
                        include_recommendations=True
                    )
                    
                    # Display report
                    st.text_area(
                        "Report Output",
                        report,
                        height=600
                    )
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"meridian_report_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            
            # Export to Excel
            st.subheader("Export Results")
            
            if st.button("Export to Excel"):
                # Create Excel file
                export_df = results.head(50)
                excel_file = "meridian_results.xlsx"
                export_df.to_excel(excel_file, index=False)
                
                with open(excel_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Excel",
                        data=f,
                        file_name=excel_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    else:
        # No results yet
        st.info("👈 Configure screening criteria in the sidebar and click 'Run Screening' to begin")
        
        # Show sample statistics
        st.subheader("Universe Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", f"{len(companies):,}")
        
        with col2:
            st.metric("Industries", companies['industry'].nunique())
        
        with col3:
            avg_revenue = companies['revenue_ttm'].mean()
            st.metric("Avg Revenue", f"${avg_revenue/1e6:.1f}M")
        
        with col4:
            profitable_pct = (companies['ebitda'] > 0).mean()
            st.metric("Profitable", f"{profitable_pct:.1%}")

if __name__ == "__main__":
    main()
