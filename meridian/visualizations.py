"""
Visualization Module for Meridian M&A Platform
Professional charts and visualizations using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

# Professional color scheme
COLORS = {
    'primary': '#1e3a8a',      # Dark blue
    'secondary': '#3b82f6',    # Bright blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Orange
    'danger': '#ef4444',       # Red
    'neutral': '#6b7280',      # Gray
    'light': '#f3f4f6',        # Light gray
    'dark': '#1f2937'          # Dark gray
}

def create_screening_funnel(funnel_data: Dict, title: str = "M&A Target Screening Funnel") -> go.Figure:
    """Create funnel chart showing screening process"""
    
    stages = list(funnel_data.keys())
    values = list(funnel_data.values())
    
    # Calculate retention rates
    retention_rates = [100]
    for i in range(1, len(values)):
        if values[0] > 0:
            retention_rates.append(values[i] / values[0] * 100)
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.85,
        marker={
            "color": [COLORS['dark'], COLORS['primary'], COLORS['secondary'], 
                     COLORS['success'], COLORS['warning'], COLORS['danger']],
            "line": {"width": 2, "color": "white"}
        },
        connector={"line": {"color": COLORS['neutral'], "width": 2}}
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['dark']}
        },
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif'}
    )
    
    return fig

def create_strategic_fit_radar(
    scores: Dict,
    company_name: str = "Target Company"
) -> go.Figure:
    """Create radar chart for strategic fit analysis"""
    
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Close the radar chart
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    
    # Add the trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Strategic Fit',
        fillcolor=COLORS['secondary'] + '40',  # Add transparency
        line=dict(color=COLORS['primary'], width=2)
    ))
    
    # Add benchmark line at 70
    benchmark = [70] * len(categories)
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=categories,
        name='Benchmark',
        line=dict(color=COLORS['warning'], width=1, dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20
            )
        ),
        showlegend=True,
        title={
            'text': f"Strategic Fit Analysis - {company_name}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_valuation_football_field(
    valuations: Dict,
    current_value: float,
    company_name: str = "Target Company"
) -> go.Figure:
    """Create football field chart for valuation ranges"""
    
    fig = go.Figure()
    
    # Sort valuations by mean value
    sorted_methods = sorted(valuations.items(), 
                           key=lambda x: x[1].get('value', current_value))
    
    y_labels = []
    for i, (method, vals) in enumerate(sorted_methods):
        y_labels.append(method)
        
        if 'value_range' in vals:
            # Add range bar
            min_val = vals['value_range']['min']
            max_val = vals['value_range']['max']
            mid_val = vals['value']
            
            # Range
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[i, i],
                mode='lines',
                line=dict(color=COLORS['neutral'], width=20),
                showlegend=False,
                hovertemplate=f"{method}<br>Range: ${min_val/1e6:.1f}M - ${max_val/1e6:.1f}M"
            ))
            
            # Midpoint
            fig.add_trace(go.Scatter(
                x=[mid_val],
                y=[i],
                mode='markers',
                marker=dict(color=COLORS['primary'], size=12, symbol='diamond'),
                showlegend=False,
                hovertemplate=f"{method}<br>Midpoint: ${mid_val/1e6:.1f}M"
            ))
        else:
            # Single value
            fig.add_trace(go.Scatter(
                x=[vals.get('value', current_value)],
                y=[i],
                mode='markers',
                marker=dict(color=COLORS['secondary'], size=10),
                showlegend=False,
                hovertemplate=f"{method}<br>Value: ${vals.get('value', current_value)/1e6:.1f}M"
            ))
    
    # Add current trading value line
    fig.add_vline(
        x=current_value,
        line_dash="dash",
        line_color=COLORS['danger'],
        annotation_text="Current Value"
    )
    
    fig.update_layout(
        title={
            'text': f"Valuation Analysis - {company_name}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        xaxis_title="Enterprise Value",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(y_labels))),
            ticktext=y_labels
        ),
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickformat='$,.0f',
            showgrid=True,
            gridcolor=COLORS['light']
        )
    )
    
    return fig

def create_target_scatter(
    df: pd.DataFrame,
    x_col: str = 'revenue_growth_yoy',
    y_col: str = 'ebitda_margin',
    size_col: str = 'revenue_ttm',
    color_col: str = 'total_score',
    title: str = "M&A Target Strategic Positioning"
) -> go.Figure:
    """Create scatter plot of acquisition targets"""
    
    # Prepare data
    plot_df = df.copy()
    plot_df['size_scaled'] = plot_df[size_col] / 1e6  # Convert to millions
    
    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        size='size_scaled',
        color=color_col,
        hover_data={
            'name': True,
            'industry': True,
            'revenue_ttm': ':$,.0f',
            'implied_revenue_multiple': ':.1f',
            x_col: ':.1%',
            y_col: ':.1%',
            color_col: ':.1f',
            'size_scaled': False
        },
        color_continuous_scale='RdYlGn',
        labels={
            x_col: 'Revenue Growth (YoY)',
            y_col: 'EBITDA Margin',
            color_col: 'Strategic Score',
            'size_scaled': 'Revenue ($M)'
        },
        title=title
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS['neutral'], opacity=0.5)
    fig.add_vline(x=0.25, line_dash="dash", line_color=COLORS['neutral'], opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(
        x=0.6, y=0.3,
        text="High Growth<br>Leaders",
        showarrow=False,
        font=dict(size=12, color=COLORS['success']),
        opacity=0.7
    )
    
    fig.add_annotation(
        x=0.05, y=0.3,
        text="Profitable<br>Stable",
        showarrow=False,
        font=dict(size=12, color=COLORS['primary']),
        opacity=0.7
    )
    
    fig.add_annotation(
        x=0.6, y=-0.1,
        text="High Growth<br>Unprofitable",
        showarrow=False,
        font=dict(size=12, color=COLORS['warning']),
        opacity=0.7
    )
    
    fig.add_annotation(
        x=0.05, y=-0.1,
        text="Turnaround<br>Candidates",
        showarrow=False,
        font=dict(size=12, color=COLORS['danger']),
        opacity=0.7
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white'),
            opacity=0.8
        )
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif'},
        xaxis=dict(
            tickformat='.0%',
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        yaxis=dict(
            tickformat='.0%',
            showgrid=True,
            gridcolor=COLORS['light']
        )
    )
    
    return fig

def create_score_breakdown(
    scores: Dict,
    company_name: str = "Target Company"
) -> go.Figure:
    """Create horizontal bar chart showing score components"""
    
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Color code based on score
    colors = []
    for v in values:
        if v >= 80:
            colors.append(COLORS['success'])
        elif v >= 60:
            colors.append(COLORS['primary'])
        elif v >= 40:
            colors.append(COLORS['warning'])
        else:
            colors.append(COLORS['danger'])
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:.0f}" for v in values],
        textposition='outside'
    ))
    
    # Add target line at 70
    fig.add_vline(
        x=70,
        line_dash="dash",
        line_color=COLORS['neutral'],
        annotation_text="Target"
    )
    
    fig.update_layout(
        title={
            'text': f"Score Breakdown - {company_name}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        xaxis_title="Score",
        xaxis=dict(range=[0, 105]),
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    
    return fig

def create_industry_heatmap(
    df: pd.DataFrame,
    metric: str = 'total_score'
) -> go.Figure:
    """Create heatmap of targets by industry and size"""
    
    # Create size buckets
    df['size_bucket'] = pd.cut(
        df['revenue_ttm'],
        bins=[0, 10e6, 50e6, 100e6, 500e6, float('inf')],
        labels=['<$10M', '$10-50M', '$50-100M', '$100-500M', '>$500M']
    )
    
    # Pivot table
    pivot = df.pivot_table(
        values=metric,
        index='industry',
        columns='size_bucket',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=np.round(pivot.values, 1),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title=metric.replace('_', ' ').title())
    ))
    
    fig.update_layout(
        title={
            'text': "Target Heatmap by Industry and Size",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        xaxis_title="Company Size",
        yaxis_title="Industry",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_synergy_waterfall(
    synergies: Dict,
    title: str = "Projected Synergy Value"
) -> go.Figure:
    """Create waterfall chart showing synergy buildup"""
    
    # Prepare data
    categories = []
    values = []
    
    # Revenue synergies
    for key, value in synergies.get('revenue_synergies', {}).items():
        categories.append(key.replace('_', ' ').title())
        values.append(value / 1e6)  # Convert to millions
    
    # Cost synergies
    for key, value in synergies.get('cost_synergies', {}).items():
        categories.append(key.replace('_', ' ').title())
        values.append(value / 1e6)
    
    # Add total
    categories.append("Total Annual Synergies")
    values.append(None)  # Will be calculated
    
    fig = go.Figure(go.Waterfall(
        name="Synergies",
        orientation="v",
        measure=["relative"] * (len(values) - 1) + ["total"],
        x=categories,
        textposition="outside",
        text=[f"${v:.1f}M" if v else "" for v in values],
        y=values,
        connector={"line": {"color": COLORS['neutral']}},
        increasing={"marker": {"color": COLORS['success']}},
        decreasing={"marker": {"color": COLORS['danger']}},
        totals={"marker": {"color": COLORS['primary']}}
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        yaxis_title="Value ($M)",
        showlegend=False,
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_deal_timeline(
    milestones: List[Dict]
) -> go.Figure:
    """Create Gantt chart for deal timeline"""
    
    df = pd.DataFrame(milestones)
    
    fig = px.timeline(
        df,
        x_start="start",
        x_end="end",
        y="task",
        color="phase",
        color_discrete_map={
            'Preparation': COLORS['primary'],
            'Due Diligence': COLORS['warning'],
            'Negotiation': COLORS['secondary'],
            'Integration': COLORS['success']
        }
    )
    
    fig.update_layout(
        title={
            'text': "Acquisition Timeline",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['dark']}
        },
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Timeline",
        yaxis_title=""
    )
    
    return fig

def create_executive_dashboard(
    screening_results: pd.DataFrame,
    top_n: int = 10
) -> go.Figure:
    """Create comprehensive executive dashboard"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Top Targets by Score',
            'Industry Distribution',
            'Valuation vs Growth',
            'Risk Assessment'
        ),
        specs=[
            [{"type": "bar"}, {"type": "pie"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ]
    )
    
    top_targets = screening_results.head(top_n)
    
    # 1. Top targets bar chart
    fig.add_trace(
        go.Bar(
            x=top_targets['total_score'],
            y=top_targets['name'],
            orientation='h',
            marker_color=COLORS['primary'],
            text=top_targets['total_score'].round(1),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # 2. Industry pie chart
    industry_counts = screening_results['industry'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=industry_counts.index,
            values=industry_counts.values,
            hole=0.3
        ),
        row=1, col=2
    )
    
    # 3. Valuation vs Growth scatter
    fig.add_trace(
        go.Scatter(
            x=top_targets['revenue_growth_yoy'],
            y=top_targets['implied_revenue_multiple'],
            mode='markers+text',
            marker=dict(
                size=top_targets['revenue_ttm'] / 5e6,
                color=top_targets['total_score'],
                colorscale='RdYlGn',
                showscale=True
            ),
            text=top_targets['name'],
            textposition='top center'
        ),
        row=2, col=1
    )
    
    # 4. Risk distribution
    risk_categories = pd.cut(
        screening_results['risk_score'],
        bins=[0, 30, 60, 100],
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )
    risk_counts = risk_categories.value_counts()
    
    fig.add_trace(
        go.Bar(
            x=risk_counts.index,
            y=risk_counts.values,
            marker_color=[COLORS['success'], COLORS['warning'], COLORS['danger']],
            text=risk_counts.values,
            textposition='outside'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title={
            'text': "M&A Intelligence Dashboard",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['dark']}
        },
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Score", row=1, col=1)
    fig.update_xaxes(title_text="Revenue Growth", tickformat='.0%', row=2, col=1)
    fig.update_yaxes(title_text="Revenue Multiple", row=2, col=1)
    fig.update_xaxes(title_text="Risk Category", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)
    
    return fig
