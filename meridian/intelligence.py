"""
Intelligence Analyzer for Meridian M&A Platform
Simulates AI-powered strategic analysis and report generation
"""

import pandas as pd
import numpy as np
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class IntelligenceAnalyzer:
    """
    Simulates AI analysis with realistic outputs
    No actual API calls - all synthetic for demo
    """
    
    def __init__(self):
        """Initialize analysis templates and patterns"""
        
        self.analysis_templates = {
            'strategic_fit': {
                'technology_synergy': (60, 95),
                'market_overlap': (40, 85),
                'cultural_alignment': (50, 80),
                'integration_complexity': (30, 70),
                'revenue_synergy': (20, 60),
                'operational_efficiency': (40, 75)
            }
        }
        
        self.insight_templates = {
            'high_tech_synergy': [
                "Strong technology complementarity identified. Target's {tech} could accelerate acquirer's product roadmap by 12-18 months.",
                "Target's proprietary {platform} platform aligns perfectly with acquirer's technology stack, enabling immediate integration.",
                "Significant IP portfolio overlap suggests strong R&D synergies and reduced development costs."
            ],
            'market_opportunity': [
                "Combined entity would control {pct}% market share, creating dominant position in {segment}.",
                "Target's customer base presents {value}M in immediate cross-sell opportunities.",
                "Geographic complementarity enables expansion into {regions} new markets without channel conflict."
            ],
            'financial_benefit': [
                "Identified ${amount}M in annual cost synergies through operational consolidation.",
                "Revenue synergies estimated at ${rev}M annually through expanded product portfolio.",
                "Combined procurement power could reduce COGS by {pct}%, improving margins significantly."
            ],
            'risk_factors': [
                "Integration complexity moderate due to different technology platforms.",
                "Customer overlap of {pct}% may result in some revenue cannibalization.",
                "Regulatory approval required in {markets} jurisdictions, extending timeline."
            ]
        }
        
        self.recommendation_criteria = {
            'STRONG BUY': 80,
            'BUY': 70,
            'EVALUATE': 55,
            'MONITOR': 40,
            'PASS': 0
        }
    
    def analyze_strategic_fit(
        self,
        acquirer: Dict,
        target: Dict,
        analysis_depth: str = 'comprehensive'
    ) -> Dict[str, Any]:
        """
        Simulate strategic fit analysis with realistic processing delay
        """
        
        # Simulate processing time
        if analysis_depth == 'comprehensive':
            time.sleep(random.uniform(1.5, 2.5))
        else:
            time.sleep(random.uniform(0.5, 1.0))
        
        scores = {}
        insights = []
        
        # Generate scores based on company characteristics
        for dimension, (min_score, max_score) in self.analysis_templates['strategic_fit'].items():
            base_score = random.uniform(min_score, max_score)
            
            # Adjust based on company attributes
            if dimension == 'technology_synergy':
                if target.get('proprietary_tech'):
                    base_score += 10
                if target.get('tech_stack_modernity', 0) > 0.7:
                    base_score += 5
                if acquirer.get('industry') == target.get('industry'):
                    base_score += 5
                    
            elif dimension == 'market_overlap':
                if acquirer.get('industry') == target.get('industry'):
                    base_score += 15
                if acquirer.get('sub_industry') == target.get('sub_industry'):
                    base_score += 10
                    
            elif dimension == 'cultural_alignment':
                # Simulated based on company age and size
                age_diff = abs(acquirer.get('founded_year', 2015) - target.get('founded_year', 2015))
                if age_diff < 3:
                    base_score += 10
                    
            elif dimension == 'integration_complexity':
                # Lower is better for complexity
                if target.get('clean_cap_table'):
                    base_score -= 10  # Less complex
                if target.get('management_staying'):
                    base_score -= 10
                if not target.get('regulatory_issues'):
                    base_score -= 5
                    
            scores[dimension] = min(100, max(0, base_score))
        
        # Generate contextual insights
        overall_score = sum(scores.values()) / len(scores)
        
        # Technology insights
        if scores['technology_synergy'] > 80:
            tech_options = ['AI/ML capabilities', 'cloud infrastructure', 'data platform']
            platform_options = ['SaaS', 'API', 'analytics']
            insight = random.choice(self.insight_templates['high_tech_synergy'])
            insight = insight.format(
                tech=random.choice(tech_options),
                platform=random.choice(platform_options)
            )
            insights.append(insight)
        
        # Market insights
        if scores['market_overlap'] > 70:
            insight = random.choice(self.insight_templates['market_opportunity'])
            insight = insight.format(
                pct=random.randint(25, 45),
                segment=target.get('sub_industry', 'enterprise software'),
                value=random.randint(10, 50),
                regions=random.randint(3, 8)
            )
            insights.append(insight)
        
        # Financial insights
        if scores['revenue_synergy'] > 60:
            insight = random.choice(self.insight_templates['financial_benefit'])
            insight = insight.format(
                amount=random.randint(5, 25),
                rev=random.randint(10, 40),
                pct=random.randint(3, 8)
            )
            insights.append(insight)
        
        # Risk insights
        if scores['integration_complexity'] > 50:
            insight = random.choice(self.insight_templates['risk_factors'])
            insight = insight.format(
                pct=random.randint(15, 35),
                markets=random.randint(2, 5)
            )
            insights.append(insight)
        
        # Generate recommendation
        recommendation = 'EVALUATE'
        for rec, threshold in self.recommendation_criteria.items():
            if overall_score >= threshold:
                recommendation = rec
                break
        
        # Add specific action items
        action_items = self._generate_action_items(scores, target)
        
        return {
            'scores': scores,
            'overall_fit': overall_score,
            'insights': insights,
            'recommendation': recommendation,
            'action_items': action_items,
            'analysis_timestamp': datetime.now(),
            'confidence': random.uniform(0.82, 0.95),
            'analysis_depth': analysis_depth
        }
    
    def _generate_action_items(self, scores: Dict, target: Dict) -> List[str]:
        """Generate specific action items based on analysis"""
        
        actions = []
        
        if scores['overall_fit'] > 75:
            actions.append("Schedule management presentation within 2 weeks")
            actions.append("Initiate preliminary due diligence on technology stack")
            actions.append("Engage investment banker for valuation opinion")
        elif scores['overall_fit'] > 60:
            actions.append("Conduct deeper market analysis on customer overlap")
            actions.append("Schedule informal meeting with target management")
            actions.append("Review recent financial performance and projections")
        else:
            actions.append("Monitor target for improved financial metrics")
            actions.append("Re-evaluate in 6 months if strategic priorities align")
        
        if target.get('is_undervalued'):
            actions.insert(0, "URGENT: Target is undervalued - accelerate engagement")
        
        if target.get('is_distressed'):
            actions.insert(0, "Consider distressed acquisition structure")
        
        return actions
    
    def generate_executive_summary(
        self,
        screening_results: pd.DataFrame,
        include_recommendations: bool = True
    ) -> str:
        """Generate professional executive summary"""
        
        # Simulate processing
        time.sleep(0.5)
        
        top_targets = screening_results.head(10)
        
        # Calculate key statistics
        total_screened = len(screening_results)
        high_priority = len(screening_results[screening_results['total_score'] > 80])
        avg_revenue = screening_results['revenue_ttm'].mean()
        avg_growth = screening_results['revenue_growth_yoy'].mean()
        undervalued = screening_results['is_undervalued'].sum()
        
        summary = f"""
================================================================================
                    MERIDIAN M&A INTELLIGENCE REPORT
================================================================================
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Analysis Type: Strategic Acquisition Screening
Confidence Level: High (94.2%)

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Meridian's AI-powered screening has identified {high_priority} high-priority 
acquisition targets from a universe of {total_screened:,} companies. The analysis 
reveals significant value creation opportunities with several targets trading 
below intrinsic value.

KEY FINDINGS
--------------------------------------------------------------------------------
► Top Acquisition Candidate: {top_targets.iloc[0]['name']}
  • Strategic Score: {top_targets.iloc[0]['strategic_score']:.1f}/100
  • Valuation: {top_targets.iloc[0]['implied_revenue_multiple']:.1f}x revenue (below industry median)
  • Revenue: ${top_targets.iloc[0]['revenue_ttm']:,.0f}
  • Growth Rate: {top_targets.iloc[0]['revenue_growth_yoy']:.1%} YoY
  • Recommendation: {top_targets.iloc[0]['recommendation']}

► Portfolio Overview:
  • Immediate Action Required: {len(screening_results[screening_results['category'] == 'Immediate Action'])} targets
  • Priority Opportunities: {len(screening_results[screening_results['category'] == 'Priority'])} targets
  • Undervalued Assets Identified: {undervalued} companies
  • Average Target Growth Rate: {avg_growth:.1%}
  • Average Target Size: ${avg_revenue:,.0f}

► Market Dynamics:
  • Sector Focus: {', '.join(screening_results['industry'].value_counts().head(3).index)}
  • Geographic Concentration: {screening_results['headquarters'].str.split(',').str[-1].value_counts().index[0].strip()}
  • Valuation Environment: {"Favorable - multiple compression creating opportunities" if undervalued > 5 else "Neutral - fair valuations prevailing"}

STRATEGIC INSIGHTS
--------------------------------------------------------------------------------
1. VALUE CREATION OPPORTUNITY
   Analysis indicates {undervalued} targets trading at significant discounts to 
   intrinsic value, presenting immediate arbitrage opportunities. Market 
   dislocation in the {top_targets.iloc[0]['industry']} sector particularly acute.

2. CONSOLIDATION POTENTIAL
   {len(screening_results[screening_results['revenue_ttm'] < 50_000_000])} targets 
   under $50M revenue present roll-up opportunity with projected 30-40% cost 
   synergies through operational integration.

3. TECHNOLOGY ACQUISITION
   {len(screening_results[screening_results['proprietary_tech'] == True])} targets 
   possess proprietary technology that could accelerate product roadmap by 12-18 
   months, justifying premium valuations.

TOP 5 ACQUISITION TARGETS
--------------------------------------------------------------------------------"""
        
        for i, row in top_targets.head(5).iterrows():
            rank = row['rank']
            summary += f"""
{rank}. {row['name']} | {row['industry']} | {row['sub_industry']}
   Revenue: ${row['revenue_ttm']:,.0f} | Growth: {row['revenue_growth_yoy']:.1%}
   Valuation: {row['implied_revenue_multiple']:.1f}x | Score: {row['total_score']:.1f}
   Status: {row['recommendation']}
"""
        
        if include_recommendations:
            summary += """
RECOMMENDED ACTIONS
--------------------------------------------------------------------------------
IMMEDIATE (This Week):
  ✓ Initiate contact with top 3 targets through investment banking channels
  ✓ Conduct preliminary technology due diligence on {0}
  ✓ Prepare NDAs and initial IOI templates

SHORT-TERM (Next 30 Days):
  ✓ Complete management meetings with priority targets
  ✓ Engage third-party valuation firm for fairness opinion
  ✓ Develop integration thesis and synergy models

MEDIUM-TERM (Next Quarter):
  ✓ Submit LOIs for selected targets
  ✓ Initiate comprehensive due diligence process
  ✓ Secure financing commitments if required
""".format(top_targets.iloc[0]['name'])
        
        summary += """
RISK ASSESSMENT
--------------------------------------------------------------------------------
• Market Risk: MODERATE - Valuation multiples may expand if rates decline
• Integration Risk: LOW - Most targets have clean structures and willing management
• Regulatory Risk: LOW - No significant antitrust concerns identified
• Financial Risk: MODERATE - Some targets have elevated leverage requiring refinancing

METHODOLOGY & CONFIDENCE
--------------------------------------------------------------------------------
This analysis leveraged Meridian's proprietary AI engine, analyzing 47 strategic
fit factors across financial, operational, and market dimensions. Machine learning
models trained on 10,000+ historical M&A transactions with 94% predictive accuracy.

================================================================================
                           END OF REPORT
================================================================================
"""
        
        return summary
    
    def generate_target_dossier(self, company: pd.Series) -> Dict:
        """Generate detailed target company dossier"""
        
        # Simulate processing
        time.sleep(0.3)
        
        dossier = {
            'company_overview': {
                'name': company['name'],
                'industry': company['industry'],
                'sub_industry': company['sub_industry'],
                'founded': company['founded_year'],
                'headquarters': company['headquarters'],
                'website': company.get('website', 'N/A'),
                'employees': company['employees']
            },
            
            'financial_summary': {
                'revenue_ttm': company['revenue_ttm'],
                'revenue_growth': company['revenue_growth_yoy'],
                'ebitda': company.get('ebitda', 0),
                'ebitda_margin': company.get('ebitda_margin', 0),
                'gross_margin': company.get('gross_margin', 0),
                'debt_to_equity': company.get('debt_to_equity', 0),
                'cash_balance': company.get('cash_balance', 0)
            },
            
            'valuation_metrics': {
                'enterprise_value': company['enterprise_value'],
                'ev_revenue': company['implied_revenue_multiple'],
                'last_round': company.get('last_funding_round', 'N/A'),
                'valuation_date': company['valuation_date']
            },
            
            'strategic_assessment': {
                'market_position': company.get('competitive_position', 'Follower'),
                'product_market_fit': company.get('product_market_fit', 'Developing'),
                'customer_concentration': company.get('customer_concentration', 0),
                'nps_score': company.get('nps_score', 0),
                'tech_stack_modernity': company.get('tech_stack_modernity', 0)
            },
            
            'acquisition_readiness': {
                'audited_financials': company.get('has_audited_financials', False),
                'management_retention': company.get('management_staying', False),
                'clean_cap_table': company.get('clean_cap_table', False),
                'proprietary_tech': company.get('proprietary_tech', False),
                'regulatory_issues': company.get('regulatory_issues', False),
                'litigation_pending': company.get('litigation_pending', False)
            },
            
            'swot_analysis': self._generate_swot(company),
            
            'key_risks': self._identify_key_risks(company),
            
            'integration_considerations': self._assess_integration(company)
        }
        
        return dossier
    
    def _generate_swot(self, company: pd.Series) -> Dict:
        """Generate SWOT analysis"""
        
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # Strengths
        if company['revenue_growth_yoy'] > 0.3:
            swot['strengths'].append("High growth rate exceeding market average")
        if company.get('proprietary_tech'):
            swot['strengths'].append("Proprietary technology creating competitive moat")
        if company.get('nps_score', 0) > 50:
            swot['strengths'].append("Exceptional customer satisfaction (NPS > 50)")
        if company.get('ebitda_margin', 0) > 0.2:
            swot['strengths'].append("Strong profitability margins")
        
        # Weaknesses
        if company.get('customer_concentration', 0) > 0.3:
            swot['weaknesses'].append("High customer concentration risk")
        if company.get('debt_to_equity', 0) > 1:
            swot['weaknesses'].append("Elevated leverage requiring refinancing")
        if not company.get('has_audited_financials'):
            swot['weaknesses'].append("Lack of audited financials")
        if company.get('ebitda_margin', 0) < 0:
            swot['weaknesses'].append("Currently unprofitable")
        
        # Opportunities
        swot['opportunities'].append(f"Expand into adjacent {company['industry']} segments")
        swot['opportunities'].append("International market expansion potential")
        if company.get('is_undervalued'):
            swot['opportunities'].append("Significant valuation upside potential")
        swot['opportunities'].append("Cross-selling opportunities post-acquisition")
        
        # Threats
        swot['threats'].append("Competitive pressure from larger players")
        if company.get('regulatory_issues'):
            swot['threats'].append("Pending regulatory challenges")
        swot['threats'].append("Technology disruption risk")
        if company['founded_year'] > 2018:
            swot['threats'].append("Limited operating history")
        
        return swot
    
    def _identify_key_risks(self, company: pd.Series) -> List[Dict]:
        """Identify and categorize key risks"""
        
        risks = []
        
        # Financial risks
        if company.get('ebitda_margin', 0) < 0:
            risks.append({
                'type': 'Financial',
                'severity': 'High',
                'description': 'Company currently unprofitable, requiring additional investment',
                'mitigation': 'Implement cost reduction program post-acquisition'
            })
        
        if company.get('debt_to_equity', 0) > 1:
            risks.append({
                'type': 'Financial',
                'severity': 'Medium',
                'description': 'High leverage may limit financial flexibility',
                'mitigation': 'Refinance debt as part of acquisition structure'
            })
        
        # Operational risks
        if company.get('customer_concentration', 0) > 0.3:
            risks.append({
                'type': 'Operational',
                'severity': 'High',
                'description': 'Customer concentration creates revenue vulnerability',
                'mitigation': 'Diversify customer base through cross-selling'
            })
        
        if not company.get('management_staying'):
            risks.append({
                'type': 'Operational',
                'severity': 'Medium',
                'description': 'Management departure risk post-acquisition',
                'mitigation': 'Implement retention bonuses and earnout structure'
            })
        
        # Legal/Regulatory risks
        if company.get('regulatory_issues'):
            risks.append({
                'type': 'Regulatory',
                'severity': 'High',
                'description': 'Ongoing regulatory compliance issues',
                'mitigation': 'Conduct thorough regulatory due diligence'
            })
        
        if company.get('litigation_pending'):
            risks.append({
                'type': 'Legal',
                'severity': 'Medium',
                'description': 'Pending litigation may impact valuation',
                'mitigation': 'Escrow portion of purchase price pending resolution'
            })
        
        return risks
    
    def _assess_integration(self, company: pd.Series) -> Dict:
        """Assess integration complexity and timeline"""
        
        # Calculate integration score
        complexity_score = 0
        
        if not company.get('clean_cap_table'):
            complexity_score += 20
        if not company.get('management_staying'):
            complexity_score += 25
        if company.get('regulatory_issues'):
            complexity_score += 20
        if company['employees'] > 500:
            complexity_score += 15
        if not company.get('has_audited_financials'):
            complexity_score += 20
        
        # Determine complexity level
        if complexity_score < 30:
            complexity = 'Low'
            timeline = '3-6 months'
        elif complexity_score < 60:
            complexity = 'Medium'
            timeline = '6-12 months'
        else:
            complexity = 'High'
            timeline = '12-18 months'
        
        return {
            'complexity_level': complexity,
            'integration_timeline': timeline,
            'complexity_score': complexity_score,
            'key_workstreams': [
                'Technology platform integration',
                'Sales force alignment',
                'Finance and accounting consolidation',
                'HR and culture integration',
                'Legal entity rationalization',
                'Customer communication and retention'
            ],
            'critical_first_100_days': [
                'Retain key employees',
                'Communicate with major customers',
                'Integrate financial reporting',
                'Align sales compensation',
                'Consolidate vendor contracts'
            ]
        }
    
    def generate_deal_comparison(
        self,
        targets: pd.DataFrame,
        max_targets: int = 5
    ) -> pd.DataFrame:
        """Generate side-by-side comparison of multiple targets"""
        
        # Limit to top targets
        comparison_targets = targets.head(max_targets)
        
        # Create comparison matrix
        comparison_data = []
        
        for _, target in comparison_targets.iterrows():
            comparison_data.append({
                'Company': target['name'],
                'Industry': target['industry'],
                'Revenue': f"${target['revenue_ttm']/1e6:.1f}M",
                'Growth': f"{target['revenue_growth_yoy']:.1%}",
                'EBITDA Margin': f"{target.get('ebitda_margin', 0):.1%}",
                'Valuation': f"{target['implied_revenue_multiple']:.1f}x",
                'Employees': target['employees'],
                'Strategic Score': f"{target.get('strategic_score', 0):.0f}",
                'Valuation Score': f"{target.get('valuation_score', 0):.0f}",
                'Risk Score': f"{target.get('risk_score', 0):.0f}",
                'Total Score': f"{target.get('total_score', 0):.1f}",
                'Category': target.get('category', 'N/A'),
                'Recommendation': target.get('recommendation', 'N/A')
            })
        
        return pd.DataFrame(comparison_data)
