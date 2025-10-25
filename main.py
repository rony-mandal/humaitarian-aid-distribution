"""
Main entry point for Humanitarian AI Crisis Management System
Run this file to execute the complete multi-agent system
"""
from core.orchestrator import HumanitarianAIOrchestrator
from utils.visualization import visualize_results
import sys
import os


def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║       HUMANITARIAN AI CRISIS MANAGEMENT SYSTEM                   ║
    ║       Agentic AI for Optimizing Aid Distribution                 ║
    ║                                                                  ║
    ║       Multi-Agent System for Refugee Settlement Management       ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main execution function"""
    
    print_banner()
    
    # Configuration
    NUM_ZONES = 10              # Number of settlement zones
    RESOURCE_SCENARIO = 'normal'  # 'abundant', 'normal', or 'scarce'
    MAX_ZONES_PER_CYCLE = 7     # Maximum zones to serve per cycle
    NUM_CYCLES = 1              # Number of distribution cycles to run
    
    print("\n📋 SYSTEM CONFIGURATION")
    print("="*70)
    print(f"  Settlement Zones: {NUM_ZONES}")
    print(f"  Resource Scenario: {RESOURCE_SCENARIO}")
    print(f"  Max Zones per Cycle: {MAX_ZONES_PER_CYCLE}")
    print(f"  Number of Cycles: {NUM_CYCLES}")
    print("="*70)
    
    try:
        # Initialize orchestrator
        orchestrator = HumanitarianAIOrchestrator(
            num_zones=NUM_ZONES,
            resource_scenario=RESOURCE_SCENARIO
        )
        
        if NUM_CYCLES == 1:
            # Run single cycle
            results = orchestrator.run_distribution_cycle(
                cycle_number=1,
                max_zones_to_serve=MAX_ZONES_PER_CYCLE
            )
            
            # Save results
            results_file = orchestrator.save_results(results)
            
            # Create visualizations
            print("\n📊 Generating visualizations...")
            visualize_results(results_file, create_all=True)
            
        else:
            # Run multiple cycles
            all_results = orchestrator.run_multiple_cycles(
                num_cycles=NUM_CYCLES,
                max_zones_per_cycle=MAX_ZONES_PER_CYCLE
            )
            
            # Generate summary report
            summary = orchestrator.generate_summary_report()
            print("\n" + "="*70)
            print("MULTI-CYCLE SUMMARY REPORT")
            print("="*70)
            print(f"Total Cycles: {summary['total_cycles_completed']}")
            print(f"Average Success Rate: {summary['average_success_rate']}%")
            print(f"Total Population Served: {summary['total_population_served']:,}")
            print(f"Best Cycle: #{summary['best_cycle']['cycle_number']} "
                  f"({summary['best_cycle']['performance_metrics']['success_rate']:.1f}%)")
            print("="*70)
            
            # Create visualizations for the latest cycle
            print("\n📊 Generating visualizations for latest cycle...")
            latest_results_file = orchestrator.save_results(all_results[-1])
            visualize_results(latest_results_file, create_all=True)
            
            # Create performance timeline
            from utils.visualization import HumanitarianDashboard
            dashboard = HumanitarianDashboard(all_results[0])
            dashboard.create_performance_timeline(all_results)
        
        # Final success message
        print("\n" + "="*70)
        print("✓ SYSTEM EXECUTION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\n📁 Output Files:")
        print("  • Cycle results: outputs/cycle_*.json")
        print("  • Dashboard: outputs/dashboard.html")
        print("  • Route map: outputs/route_map.html")
        if NUM_CYCLES > 1:
            print("  • Timeline: outputs/timeline.html")
        print("\n💡 Open HTML files in your browser to view interactive visualizations")
        print("="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())