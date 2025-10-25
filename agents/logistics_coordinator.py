"""
Logistics Coordinator Agent - Plans optimal delivery routes and schedules
"""
import json
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_wrapper import LocalLLM

load_dotenv()


class LogisticsCoordinatorAgent:
    """Agent responsible for delivery route optimization and scheduling"""
    
    def __init__(self, temperature=0.3):
        """
        Initialize logistics coordinator agent
        
        Args:
            temperature: LLM temperature for planning
        """
        self.llm = LocalLLM(temperature=temperature)
    
    def plan_delivery_routes(self, allocations, zones_df):
        """
        Plan optimal delivery routes for allocated resources
        
        Args:
            allocations: List of resource allocations per zone
            zones_df: DataFrame with zone logistics information
            
        Returns:
            Dictionary with delivery routes and schedule
        """
        print(f"\n🚚 Planning delivery logistics for {len(allocations)} zones...")
        
        # Extract relevant logistics data for allocated zones
        allocated_zone_ids = [alloc['zone_id'] for alloc in allocations]
        zone_logistics = zones_df[zones_df['zone_id'].isin(allocated_zone_ids)][
            ['zone_id', 'zone_name', 'distance_from_depot', 'road_condition', 
             'accessibility', 'security_level', 'population']
        ].to_dict('records')
        
        prompt = f"""You are an expert logistics coordinator for humanitarian aid operations.
Plan efficient delivery routes considering real-world constraints.

RESOURCE ALLOCATIONS TO DELIVER:
{json.dumps(allocations, indent=2)}

ZONE LOGISTICS DATA:
{json.dumps(zone_logistics, indent=2)}

LOGISTICS CONSTRAINTS:
- Each vehicle can carry approximately 3000 kg of mixed supplies
- Average speed: 40 km/h on good roads, 25 km/h on fair roads, 15 km/h on poor roads
- Loading time at depot: 1 hour
- Unloading time per zone: 30-45 minutes depending on accessibility
- Security concerns may require escorts (adds 15 minutes per zone)
- Maximum 8 hours driving per day per vehicle
- Priority zones should be visited first

ROUTE PLANNING OBJECTIVES:
1. Minimize total delivery time
2. Prioritize highest-priority zones (visit first)
3. Group nearby zones on same route when possible
4. Account for road conditions and accessibility
5. Ensure security protocols for risk zones

Return ONLY valid JSON in this exact format:
{{
  "routes": [
    {{
      "route_id": 1,
      "vehicle_number": 1,
      "zones_sequence": ["Z01", "Z03"],
      "zone_names": ["Sector A", "Sector C"],
      "total_distance_km": 25.5,
      "estimated_time_hours": 4.5,
      "road_conditions": "mostly good, some fair",
      "special_requirements": "security escort for Z03",
      "delivery_notes": "Priority route - serve highest need zones first"
    }}
  ],
  "total_vehicles_needed": 2,
  "total_delivery_time_hours": 8.5,
  "estimated_completion": "Day 1",
  "logistics_summary": "Brief overview of logistics plan",
  "potential_challenges": ["challenge1", "challenge2"]
}}

Do not include any text before or after the JSON."""

        try:
            response = self.llm.invoke(prompt)
            delivery_plan = json.loads(response.content)
            
            print(f"✓ Created {len(delivery_plan['routes'])} delivery routes")
            print(f"  Total vehicles needed: {delivery_plan['total_vehicles_needed']}")
            print(f"  Estimated completion: {delivery_plan['estimated_completion']}")
            
            return delivery_plan
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response was: {response.content}")
            return self._create_fallback_route_plan(allocations, zone_logistics)
    
    def _create_fallback_route_plan(self, allocations, zone_logistics):
        """Create simple route plan if AI fails"""
        print("⚠️  Using fallback route planning...")
        
        routes = []
        zones_per_route = 3  # Simple grouping
        
        for i in range(0, len(allocations), zones_per_route):
            route_zones = allocations[i:i + zones_per_route]
            zone_ids = [z['zone_id'] for z in route_zones]
            
            # Calculate simple estimates
            total_distance = sum(
                next((zl['distance_from_depot'] for zl in zone_logistics 
                      if zl['zone_id'] == zid), 10)
                for zid in zone_ids
            )
            
            route = {
                'route_id': len(routes) + 1,
                'vehicle_number': len(routes) + 1,
                'zones_sequence': zone_ids,
                'total_distance_km': round(total_distance, 1),
                'estimated_time_hours': round(total_distance / 30 + 2, 1),
                'delivery_notes': 'Standard delivery route'
            }
            routes.append(route)
        
        return {
            'routes': routes,
            'total_vehicles_needed': len(routes),
            'total_delivery_time_hours': sum(r['estimated_time_hours'] for r in routes),
            'estimated_completion': 'Day 1-2',
            'logistics_summary': 'Fallback routing plan',
            'potential_challenges': ['Weather dependent', 'Road conditions']
        }
    
    def optimize_vehicle_loading(self, route, allocations):
        """
        Optimize vehicle loading for a specific route
        
        Args:
            route: Route information
            allocations: Resource allocations for zones in route
            
        Returns:
            Loading plan with weight distribution
        """
        route_zones = route['zones_sequence']
        route_allocations = [a for a in allocations if a['zone_id'] in route_zones]
        
        # Approximate weights (in kg)
        weights = {
            'food_packages': 0.5,      # per package
            'water_liters': 1.0,       # per liter
            'medical_kits': 2.0,       # per kit
            'shelter_materials': 15.0, # per unit
            'blankets': 1.5,           # per blanket
            'hygiene_kits': 3.0        # per kit
        }
        
        loading_plan = []
        total_weight = 0
        
        for alloc in route_allocations:
            zone_weight = 0
            zone_items = {}
            
            for resource_type, quantity in alloc.items():
                if resource_type in weights and isinstance(quantity, (int, float)):
                    item_weight = quantity * weights[resource_type]
                    zone_weight += item_weight
                    zone_items[resource_type] = {
                        'quantity': quantity,
                        'weight_kg': round(item_weight, 1)
                    }
            
            total_weight += zone_weight
            loading_plan.append({
                'zone_id': alloc['zone_id'],
                'zone_name': alloc.get('zone_name', 'Unknown'),
                'items': zone_items,
                'total_weight_kg': round(zone_weight, 1)
            })
        
        return {
            'route_id': route['route_id'],
            'loading_sequence': loading_plan,
            'total_weight_kg': round(total_weight, 1),
            'capacity_used_percent': round((total_weight / 3000) * 100, 1),
            'weight_status': 'OK' if total_weight <= 3000 else 'OVERWEIGHT'
        }
    
    def generate_delivery_schedule(self, delivery_plan):
        """Generate detailed time-based delivery schedule"""
        schedule = []
        current_time = 8.0  # Start at 8:00 AM
        
        for route in delivery_plan['routes']:
            route_schedule = {
                'route_id': route['route_id'],
                'start_time': f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
                'zones': [],
                'end_time': None
            }
            
            time_offset = 0
            for i, zone_id in enumerate(route['zones_sequence']):
                zone_time = current_time + time_offset
                
                zone_schedule = {
                    'sequence': i + 1,
                    'zone_id': zone_id,
                    'arrival_time': f"{int(zone_time):02d}:{int((zone_time % 1) * 60):02d}",
                    'unloading_duration_minutes': 30,
                    'departure_time': f"{int(zone_time + 0.5):02d}:{int(((zone_time + 0.5) % 1) * 60):02d}"
                }
                
                route_schedule['zones'].append(zone_schedule)
                time_offset += 1.0  # 1 hour per zone (travel + unload)
            
            route_schedule['end_time'] = f"{int(current_time + time_offset):02d}:{int(((current_time + time_offset) % 1) * 60):02d}"
            schedule.append(route_schedule)
            
            current_time += time_offset + 0.5  # Add buffer between routes
        
        return schedule


if __name__ == "__main__":
    # Test the agent
    from data.settlement_data import SettlementSimulator
    from agents.needs_assessment import NeedsAssessmentAgent
    from agents.resource_allocation import ResourceAllocationAgent
    
    sim = SettlementSimulator(num_zones=8)
    needs_agent = NeedsAssessmentAgent()
    alloc_agent = ResourceAllocationAgent()
    logistics_agent = LogisticsCoordinatorAgent()
    
    # Get assessments and allocations
    assessments = needs_agent.assess_all_zones(sim.zones)
    resources = sim.get_available_resources('normal')
    allocations = alloc_agent.allocate_resources(assessments, resources, max_zones=6)
    
    # Plan logistics
    delivery_plan = logistics_agent.plan_delivery_routes(allocations, sim.zones)
    
    print("\n" + "="*60)
    print("DELIVERY ROUTES:")
    print("="*60)
    for route in delivery_plan['routes']:
        print(f"\nRoute {route['route_id']}:")
        print(f"  Zones: {' → '.join(route['zones_sequence'])}")
        print(f"  Distance: {route['total_distance_km']} km")
        print(f"  Time: {route['estimated_time_hours']} hours")
    
    # Test vehicle loading
    if delivery_plan['routes']:
        loading = logistics_agent.optimize_vehicle_loading(
            delivery_plan['routes'][0], 
            allocations
        )
        print(f"\n📦 Vehicle Loading for Route 1:")
        print(f"  Total Weight: {loading['total_weight_kg']} kg")
        print(f"  Capacity Used: {loading['capacity_used_percent']}%")