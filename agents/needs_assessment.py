"""
Needs Assessment Agent - Analyzes settlement zones and prioritizes needs
"""
import json
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_wrapper import LocalLLM

load_dotenv()


class NeedsAssessmentAgent:
    """Agent responsible for assessing humanitarian needs and setting priorities"""
    
    def __init__(self, temperature=0.3):
        """
        Initialize the needs assessment agent
        
        Args:
            temperature: LLM temperature for responses
        """
        self.llm = LocalLLM(temperature=temperature)
        
    def assess_zone_priority(self, zone_data):
        """
        Assess priority score for a single zone
        
        Args:
            zone_data: Dictionary containing zone information
            
        Returns:
            Dictionary with priority score, critical needs, and reasoning
        """
        prompt = f"""You are an expert humanitarian needs assessment specialist working for the UN. 
Analyze this refugee settlement zone and calculate a priority score from 0-100 (100 = most urgent).

ZONE DATA:
{json.dumps(zone_data, indent=2)}

ASSESSMENT CRITERIA:
1. Vulnerable populations (children, elderly, pregnant women, chronic illness) - 25 points
2. Critical shortages (food, water, medical) - 35 points  
3. Time since last aid received - 20 points
4. Population size and density - 10 points
5. Shelter and sanitation conditions - 10 points

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "priority_score": <number between 0-100>,
  "critical_needs": ["need1", "need2", "need3"],
  "vulnerability_score": <number 0-25>,
  "shortage_score": <number 0-35>,
  "time_score": <number 0-20>,
  "reasoning": "2-3 sentence explanation of priority level"
}}

Do not include any text before or after the JSON."""

        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            result['zone_id'] = zone_data.get('zone_id', 'Unknown')
            result['zone_name'] = zone_data.get('zone_name', 'Unknown')
            return result
        except json.JSONDecodeError as e:
            print(f"JSON decode error for zone {zone_data.get('zone_id')}: {e}")
            print(f"Response was: {response.content}")
            # Return default assessment
            return {
                'zone_id': zone_data.get('zone_id', 'Unknown'),
                'zone_name': zone_data.get('zone_name', 'Unknown'),
                'priority_score': 50,
                'critical_needs': ['food', 'water'],
                'vulnerability_score': 12,
                'shortage_score': 18,
                'time_score': 10,
                'reasoning': 'Default assessment due to processing error'
            }
    
    def assess_all_zones(self, zones_df):
        """
        Assess all zones and return prioritized list
        
        Args:
            zones_df: Pandas DataFrame with zone data
            
        Returns:
            List of assessments sorted by priority (highest first)
        """
        print(f"\n🔍 Assessing needs for {len(zones_df)} zones...")
        
        assessments = []
        for idx, zone in zones_df.iterrows():
            zone_dict = zone.to_dict()
            assessment = self.assess_zone_priority(zone_dict)
            assessments.append(assessment)
            
            # Progress indicator
            if (idx + 1) % 3 == 0 or (idx + 1) == len(zones_df):
                print(f"   Assessed {idx + 1}/{len(zones_df)} zones...")
        
        # Sort by priority score (descending)
        sorted_assessments = sorted(
            assessments, 
            key=lambda x: x['priority_score'], 
            reverse=True
        )
        
        print(f"✓ Assessment complete. Highest priority: {sorted_assessments[0]['zone_id']} "
              f"(score: {sorted_assessments[0]['priority_score']:.1f})")
        
        return sorted_assessments
    
    def identify_critical_zones(self, assessments, threshold=75):
        """
        Identify zones requiring immediate attention
        
        Args:
            assessments: List of zone assessments
            threshold: Priority score threshold for critical classification
            
        Returns:
            List of critical zones
        """
        critical = [a for a in assessments if a['priority_score'] >= threshold]
        return critical
    
    def generate_needs_report(self, assessments):
        """Generate summary report of needs assessment"""
        total_zones = len(assessments)
        critical_zones = len([a for a in assessments if a['priority_score'] >= 75])
        high_priority = len([a for a in assessments if 60 <= a['priority_score'] < 75])
        
        # Count critical needs
        all_needs = []
        for assessment in assessments:
            all_needs.extend(assessment.get('critical_needs', []))
        
        from collections import Counter
        needs_count = Counter(all_needs)
        
        report = {
            'total_zones_assessed': total_zones,
            'critical_zones': critical_zones,
            'high_priority_zones': high_priority,
            'average_priority_score': sum(a['priority_score'] for a in assessments) / total_zones,
            'most_common_needs': dict(needs_count.most_common(5)),
            'top_5_priority_zones': [
                {
                    'zone_id': a['zone_id'],
                    'zone_name': a['zone_name'],
                    'priority_score': a['priority_score']
                }
                for a in assessments[:5]
            ]
        }
        
        return report


if __name__ == "__main__":
    # Test the agent
    from data.settlement_data import SettlementSimulator
    
    sim = SettlementSimulator(num_zones=5)
    agent = NeedsAssessmentAgent()
    
    assessments = agent.assess_all_zones(sim.zones)
    
    print("\n" + "="*60)
    print("TOP 3 PRIORITY ZONES:")
    print("="*60)
    for i, assessment in enumerate(assessments[:3], 1):
        print(f"\n{i}. {assessment['zone_name']} ({assessment['zone_id']})")
        print(f"   Priority Score: {assessment['priority_score']:.1f}/100")
        print(f"   Critical Needs: {', '.join(assessment['critical_needs'])}")
        print(f"   Reasoning: {assessment['reasoning']}")