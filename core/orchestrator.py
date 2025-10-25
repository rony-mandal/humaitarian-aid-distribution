"""
Main Orchestrator - Coordinates all agents in the humanitarian AI system
"""
from agents.needs_assessment import NeedsAssessmentAgent
from agents.resource_allocation import ResourceAllocationAgent
from agents.logistics_coordinator import LogisticsCoordinatorAgent
from agents.monitor_adaptation import MonitorAdaptationAgent
from data.settlement_data import SettlementSimulator
import json
import numpy as np
from datetime import datetime
import os


class HumanitarianAIOrchestrator:
    """
    Main orchestrator that coordinates all agents in the multi-agent system
    for humanitarian crisis management and aid distribution optimization
    """
    
    def __init__(self, num_zones=10, resource_scenario='normal'):
        """
        Initialize the orchestrator with all agents
        
        Args:
            num_zones: Number of settlement zones to simulate
            resource_scenario: 'abundant', 'normal', or 'scarce'
        """
        print("\n" + "="*70)
        print("INITIALIZING HUMANITARIAN AI SYSTEM")
        print("="*70)
        
        # Initialize data simulator
        self.simulator = SettlementSimulator(num_zones=num_zones)
        self.resource_scenario = resource_scenario
        
        # Initialize all agents
        print("\n🤖 Initializing AI Agents...")
        self.needs_agent = NeedsAssessmentAgent()
        print("  ✓ Needs Assessment Agent ready")
        
        self.allocation_agent = ResourceAllocationAgent()
        print("  ✓ Resource Allocation Agent ready")
        
        self.logistics_agent = LogisticsCoordinatorAgent()
        print("  ✓ Logistics Coordinator Agent ready")
        
        self.monitor_agent = MonitorAdaptationAgent()
        print("  ✓ Monitor & Adaptation Agent ready")
        
        # Storage for historical data
        self.cycle_history = []
        
        print("\n✓ System initialization complete!\n")
    
    def run_distribution_cycle(self, cycle_number=1, max_zones_to_serve=8):
        """
        Execute one complete aid distribution cycle
        
        Args:
            cycle_number: Current cycle number
            max_zones_to_serve: Maximum zones to serve in this cycle
            
        Returns:
            Complete cycle results
        """
        print("\n" + "="*70)
        print(f"DISTRIBUTION CYCLE #{cycle_number}")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        cycle_start_time = datetime.now()
        
        # PHASE 1: Load Current Settlement Data
        print("\n" + "-"*70)
        print("PHASE 1: SETTLEMENT DATA COLLECTION")
        print("-"*70)
        zones = self.simulator.zones
        resources = self.simulator.get_available_resources(self.resource_scenario)
        
        print(f"✓ Loaded {len(zones)} settlement zones")
        print(f"✓ Total population: {zones['population'].sum():,}")
        print(f"\nAvailable Resources:")
        for resource, amount in resources.items():
            if resource not in ['vehicles_available', 'personnel_available', 'budget_usd']:
                print(f"  • {resource}: {amount:,}")
        
        # PHASE 2: Needs Assessment
        print("\n" + "-"*70)
        print("PHASE 2: NEEDS ASSESSMENT")
        print("-"*70)
        prioritized_zones = self.needs_agent.assess_all_zones(zones)
        needs_report = self.needs_agent.generate_needs_report(prioritized_zones)
        
        print(f"\nAssessment Summary:")
        print(f"  • Critical zones (score ≥75): {needs_report['critical_zones']}")
        print(f"  • High priority zones (score 60-74): {needs_report['high_priority_zones']}")
        print(f"  • Average priority score: {needs_report['average_priority_score']:.1f}/100")
        print(f"\nTop 5 Priority Zones:")
        for i, zone in enumerate(prioritized_zones[:5], 1):
            print(f"  {i}. {zone['zone_name']} ({zone['zone_id']}): {zone['priority_score']:.1f}")
            print(f"     Critical needs: {', '.join(zone['critical_needs'][:3])}")
        
        # PHASE 3: Resource Allocation
        print("\n" + "-"*70)
        print("PHASE 3: RESOURCE ALLOCATION OPTIMIZATION")
        print("-"*70)
        allocations = self.allocation_agent.allocate_resources(
            prioritized_zones, 
            resources, 
            max_zones=max_zones_to_serve
        )
        
        coverage = self.allocation_agent.calculate_coverage(allocations, zones)
        print(f"\nAllocation Coverage:")
        print(f"  • Zones served: {coverage['zones_served']}/{coverage['total_zones']}")
        print(f"  • Population covered: {coverage['population_served']:,}/{coverage['total_population']:,}")
        print(f"  • Coverage rate: {coverage['coverage_percentage']:.1f}%")
        
        # PHASE 4: Logistics Planning
        print("\n" + "-"*70)
        print("PHASE 4: LOGISTICS & ROUTE PLANNING")
        print("-"*70)
        delivery_plan = self.logistics_agent.plan_delivery_routes(allocations, zones)
        
        print(f"\nDelivery Plan:")
        print(f"  • Routes created: {len(delivery_plan['routes'])}")
        print(f"  • Vehicles required: {delivery_plan['total_vehicles_needed']}")
        print(f"  • Total delivery time: {delivery_plan['total_delivery_time_hours']:.1f} hours")
        print(f"  • Estimated completion: {delivery_plan['estimated_completion']}")
        
        # Display route details
        for route in delivery_plan['routes']:
            print(f"\n  Route {route['route_id']}:")
            print(f"    Zones: {' → '.join(route.get('zone_names', route['zones_sequence']))}")
            print(f"    Distance: {route.get('total_distance_km', 'N/A')} km")
            print(f"    Time: {route.get('estimated_time_hours', 'N/A')} hours")
        
        # Generate delivery schedule
        schedule = self.logistics_agent.generate_delivery_schedule(delivery_plan)
        
        # PHASE 5: Simulate Delivery & Monitor
        print("\n" + "-"*70)
        print("PHASE 5: DELIVERY EXECUTION & MONITORING")
        print("-"*70)
        print("Simulating delivery execution...")
        actual_outcomes = self._simulate_delivery_execution(allocations)
        
        # Analyze outcomes
        analysis = self.monitor_agent.analyze_delivery_outcomes(
            delivery_plan, 
            actual_outcomes, 
            allocations
        )
        
        print(f"\nDelivery Results:")
        print(f"  • Overall success rate: {analysis['overall_success_rate']:.1f}%")
        print(f"  • Zones fully served: {len(analysis['zones_fully_served'])}")
        print(f"  • Zones partially served: {len(analysis['zones_partially_served'])}")
        print(f"  • Follow-up required: {len(analysis['zones_requiring_followup'])}")
        
        if analysis.get('challenges_identified'):
            print(f"\nChallenges Encountered:")
            for challenge in analysis['challenges_identified'][:3]:
                print(f"  • {challenge.get('challenge_type', 'Unknown')}: {challenge.get('impact', 'N/A')}")
        
        print(f"\nKey Recommendations:")
        for i, rec in enumerate(analysis.get('recommendations_next_cycle', [])[:3], 1):
            print(f"  {i}. {rec}")
        
        # PHASE 6: Compile Complete Results
        cycle_end_time = datetime.now()
        cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
        
        complete_results = {
            'cycle_number': cycle_number,
            'timestamp': cycle_start_time.isoformat(),
            'duration_seconds': cycle_duration,
            'resource_scenario': self.resource_scenario,
            
            'settlement_data': {
                'total_zones': len(zones),
                'total_population': int(zones['population'].sum()),
                'zones_data': zones.to_dict('records')
            },
            
            'available_resources': resources,
            
            'needs_assessment': {
                'prioritized_zones': prioritized_zones,
                'report': needs_report
            },
            
            'resource_allocation': {
                'allocations': allocations,
                'coverage': coverage
            },
            
            'logistics_plan': {
                'delivery_plan': delivery_plan,
                'schedule': schedule
            },
            
            'delivery_outcomes': {
                'actual_results': actual_outcomes,
                'analysis': analysis
            },
            
            'performance_metrics': {
                'zones_served': len(allocations),
                'success_rate': analysis['overall_success_rate'],
                'population_served': coverage['population_served'],
                'coverage_percentage': coverage['coverage_percentage']
            }
        }
        
        # Store in history
        self.cycle_history.append(complete_results)
        
        # Display final summary
        print("\n" + "="*70)
        print(f"CYCLE #{cycle_number} COMPLETE")
        print("="*70)
        print(f"Duration: {cycle_duration:.1f} seconds")
        print(f"Success Rate: {analysis['overall_success_rate']:.1f}%")
        print(f"Population Served: {coverage['population_served']:,}")
        print("="*70 + "\n")
        
        return complete_results
    
    def _simulate_delivery_execution(self, allocations):
        """
        Simulate actual delivery with realistic variations
        
        Args:
            allocations: Planned resource allocations
            
        Returns:
            List of actual delivery outcomes
        """
        outcomes = []
        
        for alloc in allocations:
            # Simulate delivery success with realistic factors
            base_success = np.random.uniform(0.85, 1.0)
            
            # Random challenges that might occur
            challenges = ['none', 'weather_delay', 'road_conditions', 'security_concern', 'vehicle_breakdown']
            challenge_probs = [0.65, 0.15, 0.10, 0.07, 0.03]
            challenge = np.random.choice(challenges, p=challenge_probs)
            
            # Adjust success rate based on challenge
            if challenge == 'weather_delay':
                success_rate = base_success * 0.95
            elif challenge == 'road_conditions':
                success_rate = base_success * 0.85
            elif challenge == 'security_concern':
                success_rate = base_success * 0.80
            elif challenge == 'vehicle_breakdown':
                success_rate = base_success * 0.75
            else:
                success_rate = base_success
            
            outcome = {
                'zone_id': alloc['zone_id'],
                'zone_name': alloc.get('zone_name', 'Unknown'),
                'planned_delivery': {
                    key: alloc[key] for key in alloc.keys() 
                    if key not in ['zone_id', 'zone_name', 'priority_score', 'justification']
                },
                'delivered_percentage': round(success_rate * 100, 1),
                'challenges': challenge,
                'delivery_status': 'complete' if success_rate >= 0.95 else 'partial' if success_rate >= 0.75 else 'incomplete'
            }
            outcomes.append(outcome)
        
        return outcomes
    
    def save_results(self, results, output_dir='outputs'):
    
        import numpy as np
    
        def convert_numpy(obj):
            """Convert numpy types to Python native types"""
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        os.makedirs(output_dir, exist_ok=True)
        
        cycle_num = results['cycle_number']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{output_dir}/cycle_{cycle_num}_{timestamp}.json'
        
        # Convert numpy types before saving
        results_clean = convert_numpy(results)
        
        with open(filename, 'w') as f:
            json.dump(results_clean, f, indent=2)
        
        print(f"✓ Results saved to: {filename}")
        return filename
    
    def run_multiple_cycles(self, num_cycles=3, max_zones_per_cycle=8):
        """
        Run multiple distribution cycles
        
        Args:
            num_cycles: Number of cycles to run
            max_zones_per_cycle: Max zones to serve per cycle
            
        Returns:
            List of all cycle results
        """
        print("\n" + "="*70)
        print(f"RUNNING {num_cycles} DISTRIBUTION CYCLES")
        print("="*70)
        
        all_results = []
        
        for cycle in range(1, num_cycles + 1):
            results = self.run_distribution_cycle(
                cycle_number=cycle,
                max_zones_to_serve=max_zones_per_cycle
            )
            
            # Save results
            self.save_results(results)
            
            all_results.append(results)
            
            # Analyze trends if not first cycle
            if cycle > 1:
                trends = self.monitor_agent.track_historical_performance(
                    results['delivery_outcomes']['analysis'],
                    [r['delivery_outcomes']['analysis'] for r in all_results[:-1]]
                )
                
                print(f"\n📈 Performance Trend: {trends['trend'].upper()}")
                print(f"   Improvement: {trends['improvement_percentage']:+.1f}%\n")
            
            # Brief pause between cycles
            if cycle < num_cycles:
                print("\n⏸️  Preparing for next cycle...\n")
        
        return all_results
    
    def generate_summary_report(self):
        """Generate summary report across all cycles"""
        if not self.cycle_history:
            return "No cycles completed yet"
        
        total_cycles = len(self.cycle_history)
        avg_success = np.mean([
            c['performance_metrics']['success_rate'] 
            for c in self.cycle_history
        ])
        total_population_served = sum([
            c['performance_metrics']['population_served'] 
            for c in self.cycle_history
        ])
        
        report = {
            'total_cycles_completed': total_cycles,
            'average_success_rate': round(avg_success, 1),
            'total_population_served': total_population_served,
            'best_cycle': max(self.cycle_history, 
                             key=lambda x: x['performance_metrics']['success_rate']),
            'summary': f"Completed {total_cycles} cycles with {avg_success:.1f}% average success rate"
        }
        
        return report


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = HumanitarianAIOrchestrator(num_zones=10, resource_scenario='normal')
    
    # Run a single cycle
    results = orchestrator.run_distribution_cycle(cycle_number=1, max_zones_to_serve=6)
    
    # Save results
    orchestrator.save_results(results)
    
    print("\n" + "="*70)
    print("ORCHESTRATOR TEST COMPLETE")
    print("="*70)