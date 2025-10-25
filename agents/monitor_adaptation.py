"""
Monitor & Adaptation Agent - Tracks outcomes and suggests improvements
"""
import json
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_wrapper import LocalLLM

load_dotenv()


class MonitorAdaptationAgent:
    """Agent responsible for monitoring delivery outcomes and adaptive learning"""
    
    def __init__(self, temperature=0.4):
        """
        Initialize monitor and adaptation agent
        
        Args:
            temperature: LLM temperature (slightly higher for recommendations)
        """
        self.llm = LocalLLM(temperature=temperature)
    
    def analyze_delivery_outcomes(self, delivery_plan, actual_outcomes, allocations):
        """
        Analyze delivery outcomes and identify gaps
        
        Args:
            delivery_plan: Planned delivery routes and schedule
            actual_outcomes: Actual delivery results (simulated or real)
            allocations: Original resource allocations
            
        Returns:
            Analysis with recommendations
        """
        print(f"\n📊 Analyzing delivery outcomes for {len(actual_outcomes)} zones...")
        
        # Calculate success metrics
        fully_delivered = [o for o in actual_outcomes if o['delivered_percentage'] >= 95]
        partially_delivered = [o for o in actual_outcomes if 75 <= o['delivered_percentage'] < 95]
        under_delivered = [o for o in actual_outcomes if o['delivered_percentage'] < 75]
        
        # Identify challenges
        challenges_encountered = {}
        for outcome in actual_outcomes:
            challenge = outcome.get('challenges', 'none')
            if challenge != 'none':
                challenges_encountered[challenge] = challenges_encountered.get(challenge, 0) + 1
        
        prompt = f"""You are a humanitarian operations monitoring and evaluation specialist.
Analyze delivery outcomes and provide actionable recommendations for improvement.

PLANNED DELIVERY:
- Routes planned: {len(delivery_plan.get('routes', []))}
- Zones targeted: {len(allocations)}
- Total delivery time planned: {delivery_plan.get('total_delivery_time_hours', 0)} hours

ACTUAL OUTCOMES:
{json.dumps(actual_outcomes, indent=2)}

PERFORMANCE METRICS:
- Fully delivered (≥95%): {len(fully_delivered)} zones
- Partially delivered (75-94%): {len(partially_delivered)} zones
- Under-delivered (<75%): {len(under_delivered)} zones

CHALLENGES ENCOUNTERED:
{json.dumps(challenges_encountered, indent=2)}

ANALYSIS REQUIRED:
1. Calculate overall success rate and identify bottlenecks
2. Determine which zones need follow-up deliveries
3. Identify systemic issues (weather, roads, security, etc.)
4. Recommend process improvements for next cycle
5. Suggest priority adjustments based on actual outcomes

Return ONLY valid JSON in this exact format:
{{
  "overall_success_rate": 85.5,
  "zones_fully_served": ["Z01", "Z02"],
  "zones_partially_served": ["Z03"],
  "zones_requiring_followup": ["Z04"],
  "critical_gaps": [
    {{
      "zone_id": "Z04",
      "gap_description": "Only 60% delivered due to road conditions",
      "urgency": "high",
      "recommended_action": "Arrange helicopter delivery or wait for road repair"
    }}
  ],
  "challenges_identified": [
    {{
      "challenge_type": "weather_delay",
      "zones_affected": 2,
      "impact": "Added 2 hours to delivery time",
      "mitigation": "Start deliveries earlier in the day"
    }}
  ],
  "performance_insights": "Brief analysis of what went well and what didn't",
  "recommendations_next_cycle": [
    "recommendation 1",
    "recommendation 2",
    "recommendation 3"
  ],
  "priority_adjustments": "Suggested changes to zone priorities for next cycle",
  "resource_reallocation_needed": {{
    "zones": ["Z04"],
    "resources_needed": {{"food_packages": 500, "water_liters": 2000}},
    "reason": "Shortfall from partial delivery"
  }}
}}

Do not include any text before or after the JSON."""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response.content)
            
            print(f"✓ Analysis complete")
            print(f"  Success Rate: {analysis['overall_success_rate']:.1f}%")
            print(f"  Zones Fully Served: {len(analysis['zones_fully_served'])}")
            print(f"  Follow-up Required: {len(analysis['zones_requiring_followup'])}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response was: {response.content}")
            return self._create_fallback_analysis(actual_outcomes, allocations)
    
    def _create_fallback_analysis(self, actual_outcomes, allocations):
        """Create basic analysis if AI fails"""
        print("⚠️  Using fallback analysis...")
        
        fully_served = [o['zone_id'] for o in actual_outcomes if o['delivered_percentage'] >= 95]
        partially_served = [o['zone_id'] for o in actual_outcomes if 75 <= o['delivered_percentage'] < 95]
        followup_needed = [o['zone_id'] for o in actual_outcomes if o['delivered_percentage'] < 75]
        
        avg_delivery = sum(o['delivered_percentage'] for o in actual_outcomes) / len(actual_outcomes)
        
        return {
            'overall_success_rate': round(avg_delivery, 1),
            'zones_fully_served': fully_served,
            'zones_partially_served': partially_served,
            'zones_requiring_followup': followup_needed,
            'critical_gaps': [],
            'challenges_identified': [],
            'performance_insights': 'Fallback analysis generated',
            'recommendations_next_cycle': ['Review delivery constraints', 'Improve route planning'],
            'priority_adjustments': 'Increase focus on under-served zones',
            'resource_reallocation_needed': {
                'zones': followup_needed,
                'resources_needed': {},
                'reason': 'Follow-up delivery required'
            }
        }
    
    def track_historical_performance(self, current_cycle, previous_cycles):
        """
        Track performance trends across multiple cycles
        
        Args:
            current_cycle: Current cycle results
            previous_cycles: List of previous cycle results
            
        Returns:
            Trend analysis
        """
        if not previous_cycles:
            return {
                'trend': 'first_cycle',
                'message': 'No historical data available yet'
            }
        
        current_rate = current_cycle.get('overall_success_rate', 0)
        previous_rates = [c.get('overall_success_rate', 0) for c in previous_cycles]
        avg_previous = sum(previous_rates) / len(previous_rates)
        
        improvement = current_rate - avg_previous
        
        trend_analysis = {
            'current_success_rate': current_rate,
            'average_previous_rate': round(avg_previous, 1),
            'improvement_percentage': round(improvement, 1),
            'trend': 'improving' if improvement > 5 else 'declining' if improvement < -5 else 'stable',
            'total_cycles_completed': len(previous_cycles) + 1,
            'best_performing_cycle': max(previous_cycles + [current_cycle], 
                                        key=lambda x: x.get('overall_success_rate', 0))
        }
        
        return trend_analysis
    
    def generate_lessons_learned(self, analysis):
        """Generate lessons learned document from analysis"""
        lessons = {
            'successes': [],
            'challenges': [],
            'best_practices': [],
            'areas_for_improvement': []
        }
        
        # Extract successes
        if analysis['overall_success_rate'] >= 80:
            lessons['successes'].append(f"Achieved {analysis['overall_success_rate']:.1f}% success rate")
        
        if len(analysis['zones_fully_served']) > 0:
            lessons['successes'].append(f"Successfully served {len(analysis['zones_fully_served'])} zones completely")
        
        # Extract challenges
        for challenge in analysis.get('challenges_identified', []):
            lessons['challenges'].append(
                f"{challenge['challenge_type']}: {challenge['impact']}"
            )
        
        # Best practices from recommendations
        for rec in analysis.get('recommendations_next_cycle', [])[:3]:
            lessons['best_practices'].append(rec)
        
        # Areas for improvement
        if analysis.get('zones_requiring_followup'):
            lessons['areas_for_improvement'].append(
                f"Follow-up needed for {len(analysis['zones_requiring_followup'])} zones"
            )
        
        return lessons


if __name__ == "__main__":
    # Test the agent
    import numpy as np
    
    monitor_agent = MonitorAdaptationAgent()
    
    # Simulate delivery outcomes
    simulated_outcomes = [
        {'zone_id': 'Z01', 'delivered_percentage': 98, 'challenges': 'none'},
        {'zone_id': 'Z02', 'delivered_percentage': 85, 'challenges': 'weather_delay'},
        {'zone_id': 'Z03', 'delivered_percentage': 65, 'challenges': 'road_conditions'},
        {'zone_id': 'Z04', 'delivered_percentage': 92, 'challenges': 'none'},
    ]
    
    simulated_plan = {
        'routes': [{'route_id': 1}, {'route_id': 2}],
        'total_delivery_time_hours': 8
    }
    
    simulated_allocations = [
        {'zone_id': f'Z0{i}', 'food_packages': 1000} 
        for i in range(1, 5)
    ]
    
    # Analyze outcomes
    analysis = monitor_agent.analyze_delivery_outcomes(
        simulated_plan, 
        simulated_outcomes, 
        simulated_allocations
    )
    
    print("\n" + "="*60)
    print("OUTCOME ANALYSIS:")
    print("="*60)
    print(f"Success Rate: {analysis['overall_success_rate']}%")
    print(f"\nRecommendations:")
    for i, rec in enumerate(analysis.get('recommendations_next_cycle', []), 1):
        print(f"  {i}. {rec}")
    
    # Generate lessons learned
    lessons = monitor_agent.generate_lessons_learned(analysis)
    print(f"\n📚 Lessons Learned:")
    print(f"  Successes: {len(lessons['successes'])}")
    print(f"  Challenges: {len(lessons['challenges'])}")