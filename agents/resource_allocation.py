"""
Resource Allocation Agent - Optimizes distribution of available resources
"""
import json
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_wrapper import LocalLLM

load_dotenv()


class ResourceAllocationAgent:
    """Agent responsible for optimal resource allocation across zones"""
    
    def __init__(self, temperature=0.2):
        """
        Initialize resource allocation agent
        
        Args:
            temperature: LLM temperature (lower for more deterministic allocation)
        """
        self.llm = LocalLLM(temperature=temperature)
    
    def allocate_resources(self, prioritized_zones, available_resources, max_zones=8):
        """
        Create optimal allocation plan for resources
        
        Args:
            prioritized_zones: List of zones sorted by priority
            available_resources: Dictionary of available resources
            max_zones: Maximum number of zones to serve in this cycle
            
        Returns:
            List of allocation plans for each zone
        """
        print(f"\n📦 Allocating resources to top {max_zones} priority zones...")
        
        # Focus on top priority zones
        target_zones = prioritized_zones[:max_zones]
        
        prompt = f"""You are a resource allocation optimizer for humanitarian aid distribution.
Your goal is to save the most lives and reduce suffering by optimally distributing limited resources.

TOP PRIORITY ZONES (in order of urgency):
{json.dumps(target_zones, indent=2)}

AVAILABLE RESOURCES:
{json.dumps(available_resources, indent=2)}

ALLOCATION RULES:
1. Highest priority zones MUST receive resources first
2. Critical needs (food, water, medical) take precedence
3. Ensure you don't exceed available resources
4. Each zone should get resources proportional to population and need severity
5. Reserve 10% of resources for emergencies
6. Consider vulnerable populations (children, elderly, pregnant women)

RESOURCE GUIDELINES:
- Food packages: ~2 per person per week
- Water liters: ~15 per person per day  
- Medical kits: 1 per 50 people with medical needs
- Shelter materials: Based on damage level
- Hygiene kits: 1 per 10 people

Return ONLY valid JSON array of allocations:
[
  {{
    "zone_id": "Z01",
    "zone_name": "Sector A",
    "priority_score": 85.5,
    "food_packages": 1200,
    "water_liters": 8000,
    "medical_kits": 45,
    "shelter_materials": 20,
    "blankets": 300,
    "hygiene_kits": 150,
    "justification": "Brief reason for this allocation"
  }}
]

Ensure allocations don't exceed 90% of available resources (reserve 10% for emergencies).
Do not include any text before or after the JSON array."""

        try:
            response = self.llm.invoke(prompt)
            allocations = json.loads(response.content)
            
            # Validate allocations
            validated = self._validate_allocations(allocations, available_resources)
            
            print(f"✓ Allocated resources to {len(validated)} zones")
            self._print_allocation_summary(validated, available_resources)
            
            return validated
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response was: {response.content}")
            return self._create_fallback_allocation(target_zones, available_resources)
    
    def _validate_allocations(self, allocations, available_resources):
        """Validate that allocations don't exceed available resources"""
        # Calculate totals
        totals = {}
        for alloc in allocations:
            for resource_type in available_resources.keys():
                if resource_type in alloc and resource_type not in ['vehicles_available', 'personnel_available', 'budget_usd']:
                    totals[resource_type] = totals.get(resource_type, 0) + alloc[resource_type]
        
        # Check for overallocation
        overallocated = []
        for resource_type, total in totals.items():
            available = available_resources.get(resource_type, 0)
            if total > available:
                overallocated.append(f"{resource_type}: {total} > {available}")
        
        if overallocated:
            print(f"⚠️  Warning: Overallocation detected for: {', '.join(overallocated)}")
            # Scale down proportionally
            for resource_type in available_resources.keys():
                if resource_type in totals and totals[resource_type] > available_resources[resource_type]:
                    scale_factor = available_resources[resource_type] / totals[resource_type]
                    for alloc in allocations:
                        if resource_type in alloc:
                            alloc[resource_type] = int(alloc[resource_type] * scale_factor)
        
        return allocations
    
    def _create_fallback_allocation(self, zones, available_resources):
        """Create simple proportional allocation if AI fails"""
        print("⚠️  Using fallback allocation strategy...")
        
        allocations = []
        num_zones = len(zones)
        
        for i, zone in enumerate(zones):
            # Simple proportional allocation
            proportion = (num_zones - i) / sum(range(1, num_zones + 1))
            
            alloc = {
                'zone_id': zone['zone_id'],
                'zone_name': zone.get('zone_name', 'Unknown'),
                'priority_score': zone['priority_score'],
                'food_packages': int(available_resources.get('food_packages', 0) * proportion * 0.9),
                'water_liters': int(available_resources.get('water_liters', 0) * proportion * 0.9),
                'medical_kits': int(available_resources.get('medical_kits', 0) * proportion * 0.9),
                'shelter_materials': int(available_resources.get('shelter_materials', 0) * proportion * 0.9),
                'justification': f'Proportional allocation based on priority rank {i+1}'
            }
            allocations.append(alloc)
        
        return allocations
    
    def _print_allocation_summary(self, allocations, available_resources):
        """Print summary of resource allocation"""
        print("\n   Resource Allocation Summary:")
        
        for resource in ['food_packages', 'water_liters', 'medical_kits', 'shelter_materials']:
            if resource in available_resources:
                total_allocated = sum(a.get(resource, 0) for a in allocations)
                available = available_resources[resource]
                percentage = (total_allocated / available * 100) if available > 0 else 0
                print(f"   • {resource}: {total_allocated:,} / {available:,} ({percentage:.1f}%)")
    
    def calculate_coverage(self, allocations, zones_df):
        """Calculate what percentage of needs are being met"""
        coverage_stats = {
            'zones_served': len(allocations),
            'total_zones': len(zones_df),
            'population_served': 0,
            'total_population': zones_df['population'].sum(),
        }
        
        for alloc in allocations:
            zone_data = zones_df[zones_df['zone_id'] == alloc['zone_id']]
            if not zone_data.empty:
                coverage_stats['population_served'] += zone_data.iloc[0]['population']
        
        coverage_stats['coverage_percentage'] = (
            coverage_stats['population_served'] / coverage_stats['total_population'] * 100
        )
        
        return coverage_stats


if __name__ == "__main__":
    # Test the agent
    from data.settlement_data import SettlementSimulator
    from agents.needs_assessment import NeedsAssessmentAgent
    
    sim = SettlementSimulator(num_zones=8)
    needs_agent = NeedsAssessmentAgent()
    alloc_agent = ResourceAllocationAgent()
    
    # Assess needs
    assessments = needs_agent.assess_all_zones(sim.zones)
    
    # Allocate resources
    resources = sim.get_available_resources('normal')
    allocations = alloc_agent.allocate_resources(assessments, resources, max_zones=5)
    
    print("\n" + "="*60)
    print("ALLOCATION RESULTS:")
    print("="*60)
    for alloc in allocations:
        print(f"\n{alloc['zone_name']} ({alloc['zone_id']}):")
        print(f"  Food: {alloc['food_packages']:,} packages")
        print(f"  Water: {alloc['water_liters']:,} liters")
        print(f"  Medical: {alloc['medical_kits']} kits")