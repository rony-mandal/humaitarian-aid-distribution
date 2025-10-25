"""
Settlement data simulator for refugee camp scenarios
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SettlementSimulator:
    """Simulates realistic refugee settlement data"""
    
    def __init__(self, num_zones=10, seed=42):
        """
        Initialize settlement simulator
        
        Args:
            num_zones: Number of zones in the settlement
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.num_zones = num_zones
        self.zones = self.generate_zones()
        
    def generate_zones(self):
        """Generate realistic refugee settlement zones with various needs"""
        zones = []
        
        for i in range(self.num_zones):
            population = np.random.randint(500, 3000)
            
            zone = {
                'zone_id': f'Z{i+1:02d}',
                'zone_name': f'Sector {chr(65+i)}',  # A, B, C, etc.
                'population': population,
                'children_ratio': round(np.random.uniform(0.30, 0.50), 2),
                'elderly_ratio': round(np.random.uniform(0.05, 0.15), 2),
                'pregnant_women': np.random.randint(10, 50),
                'chronic_illness_cases': np.random.randint(20, 100),
                
                # Need indicators (0-1 scale, higher = more shortage)
                'food_shortage': round(np.random.uniform(0.3, 0.95), 2),
                'water_shortage': round(np.random.uniform(0.2, 0.85), 2),
                'medical_severity': round(np.random.uniform(0.2, 0.90), 2),
                'shelter_damage': round(np.random.uniform(0.1, 0.70), 2),
                'sanitation_need': round(np.random.uniform(0.3, 0.80), 2),
                
                # Logistics data
                'distance_from_depot': round(np.random.uniform(1.0, 20.0), 1),  # km
                'road_condition': np.random.choice(['good', 'fair', 'poor'], p=[0.3, 0.4, 0.3]),
                'accessibility': np.random.choice(['easy', 'moderate', 'difficult'], p=[0.4, 0.4, 0.2]),
                'security_level': np.random.choice(['safe', 'caution', 'risk'], p=[0.6, 0.3, 0.1]),
                
                # Historical data
                'last_aid_received_days': np.random.randint(1, 30),
                'previous_aid_satisfaction': round(np.random.uniform(0.5, 0.95), 2),
                
                # Coordinates (simulated)
                'latitude': round(np.random.uniform(30.0, 35.0), 4),
                'longitude': round(np.random.uniform(40.0, 45.0), 4),
            }
            zones.append(zone)
        
        return pd.DataFrame(zones)
    
    def get_available_resources(self, scenario='normal'):
        """
        Simulate available resources at distribution center
        
        Args:
            scenario: 'abundant', 'normal', or 'scarce'
        """
        multipliers = {
            'abundant': 1.5,
            'normal': 1.0,
            'scarce': 0.6
        }
        mult = multipliers.get(scenario, 1.0)
        
        return {
            'food_packages': int(np.random.randint(5000, 15000) * mult),
            'water_liters': int(np.random.randint(10000, 30000) * mult),
            'medical_kits': int(np.random.randint(200, 800) * mult),
            'shelter_materials': int(np.random.randint(100, 500) * mult),
            'blankets': int(np.random.randint(1000, 3000) * mult),
            'hygiene_kits': int(np.random.randint(500, 1500) * mult),
            'vehicles_available': np.random.randint(5, 12),
            'personnel_available': np.random.randint(20, 50),
            'budget_usd': int(np.random.randint(50000, 150000) * mult)
        }
    
    def get_zone_by_id(self, zone_id):
        """Get specific zone data by ID"""
        return self.zones[self.zones['zone_id'] == zone_id].iloc[0].to_dict()
    
    def update_zone_after_delivery(self, zone_id, delivered_resources):
        """Update zone status after aid delivery"""
        idx = self.zones[self.zones['zone_id'] == zone_id].index[0]
        
        # Reduce shortage indicators based on delivered resources
        if 'food_packages' in delivered_resources:
            self.zones.at[idx, 'food_shortage'] *= 0.5
        if 'water_liters' in delivered_resources:
            self.zones.at[idx, 'water_shortage'] *= 0.5
        if 'medical_kits' in delivered_resources:
            self.zones.at[idx, 'medical_severity'] *= 0.6
        
        # Update last aid received
        self.zones.at[idx, 'last_aid_received_days'] = 0
    
    def export_to_csv(self, filename='outputs/settlement_data.csv'):
        """Export zone data to CSV"""
        self.zones.to_csv(filename, index=False)
        print(f"✓ Zone data exported to {filename}")
    
    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "="*60)
        print("SETTLEMENT DATA SUMMARY")
        print("="*60)
        print(f"Total Zones: {len(self.zones)}")
        print(f"Total Population: {self.zones['population'].sum():,}")
        print(f"Average Food Shortage: {self.zones['food_shortage'].mean():.2f}")
        print(f"Average Water Shortage: {self.zones['water_shortage'].mean():.2f}")
        print(f"Zones with High Medical Need (>0.7): {len(self.zones[self.zones['medical_severity'] > 0.7])}")
        print(f"Difficult Access Zones: {len(self.zones[self.zones['accessibility'] == 'difficult'])}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test the simulator
    sim = SettlementSimulator(num_zones=10)
    sim.print_summary()
    print("\nSample Zone Data:")
    print(sim.zones.head(3))
    
    print("\nAvailable Resources:")
    resources = sim.get_available_resources('normal')
    for key, value in resources.items():
        print(f"  {key}: {value}")