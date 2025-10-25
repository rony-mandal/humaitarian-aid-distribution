"""
Visualization utilities for humanitarian AI system
Creates interactive dashboards and charts using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import numpy as np


class HumanitarianDashboard:
    """Creates interactive visualizations for system results"""
    
    def __init__(self, results_data):
        """
        Initialize dashboard with cycle results
        
        Args:
            results_data: Dictionary or JSON file path with cycle results
        """
        if isinstance(results_data, str):
            with open(results_data, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = results_data
    
    def create_comprehensive_dashboard(self, output_file='outputs/dashboard.html'):
        """Create comprehensive multi-panel dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Zone Priority Scores',
                'Resource Allocation Distribution',
                'Delivery Success by Zone',
                'Resource Type Breakdown',
                'Challenges Encountered',
                'Population Coverage'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'pie'}],
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'pie'}, {'type': 'indicator'}]
            ],
            row_heights=[0.35, 0.35, 0.30]
        )
        
        # Extract data
        zones_data = self.data['needs_assessment']['prioritized_zones'][:10]
        allocations = self.data['resource_allocation']['allocations']
        outcomes = self.data['delivery_outcomes']['actual_results']
        performance = self.data['performance_metrics']
        
        # 1. Priority Scores Bar Chart
        zone_ids = [z['zone_id'] for z in zones_data]
        priorities = [z['priority_score'] for z in zones_data]
        
        fig.add_trace(
            go.Bar(
                x=zone_ids,
                y=priorities,
                marker_color='indianred',
                name='Priority Score',
                text=[f"{p:.0f}" for p in priorities],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Priority: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. Resource Distribution Pie Chart
        resource_totals = {}
        for alloc in allocations:
            for key, value in alloc.items():
                if key not in ['zone_id', 'zone_name', 'priority_score', 'justification'] and isinstance(value, (int, float)):
                    resource_totals[key] = resource_totals.get(key, 0) + value
        
        fig.add_trace(
            go.Pie(
                labels=list(resource_totals.keys()),
                values=list(resource_totals.values()),
                hole=0.3,
                marker=dict(colors=px.colors.qualitative.Set3),
                hovertemplate='<b>%{label}</b><br>Quantity: %{value:,}<br>Percentage: %{percent}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Delivery Success Bar Chart
        outcome_zones = [o['zone_id'] for o in outcomes]
        success_rates = [o['delivered_percentage'] for o in outcomes]
        colors = ['green' if s >= 95 else 'orange' if s >= 75 else 'red' for s in success_rates]
        
        fig.add_trace(
            go.Bar(
                x=outcome_zones,
                y=success_rates,
                marker_color=colors,
                name='Delivery Success',
                text=[f"{s:.0f}%" for s in success_rates],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Delivered: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 4. Resource Type Breakdown
        resource_names = list(resource_totals.keys())[:5]
        resource_values = [resource_totals[name] for name in resource_names]
        
        fig.add_trace(
            go.Bar(
                x=resource_names,
                y=resource_values,
                marker_color='lightseagreen',
                name='Resources',
                text=[f"{v:,.0f}" for v in resource_values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Quantity: %{y:,}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # 5. Challenges Pie Chart
        challenges = {}
        for outcome in outcomes:
            challenge = outcome.get('challenges', 'none')
            challenges[challenge] = challenges.get(challenge, 0) + 1
        
        fig.add_trace(
            go.Pie(
                labels=list(challenges.keys()),
                values=list(challenges.values()),
                hole=0.3,
                marker=dict(colors=px.colors.qualitative.Pastel),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            ),
            row=3, col=1
        )
        
        # 6. Success Rate Indicator
        success_rate = performance['success_rate']
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                title={'text': "Overall Success Rate"},
                delta={'reference': 85},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "lightblue"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=3, col=2
        )
        
        # Update layout
        cycle_num = self.data.get('cycle_number', 1)
        fig.update_layout(
            title_text=f"Humanitarian AI System - Cycle #{cycle_num} Dashboard",
            title_font_size=20,
            showlegend=False,
            height=1200,
            template='plotly_white'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Zone ID", row=1, col=1)
        fig.update_yaxes(title_text="Priority Score", row=1, col=1)
        
        fig.update_xaxes(title_text="Zone ID", row=2, col=1)
        fig.update_yaxes(title_text="Delivery %", row=2, col=1)
        
        fig.update_xaxes(title_text="Resource Type", row=2, col=2)
        fig.update_yaxes(title_text="Quantity", row=2, col=2)
        
        # Save dashboard
        fig.write_html(output_file)
        print(f"✓ Dashboard saved to: {output_file}")
        
        return fig
    
    def create_route_map(self, output_file='outputs/route_map.html'):
        """Create delivery route visualization"""
        
        zones_data = pd.DataFrame(self.data['settlement_data']['zones_data'])
        delivery_plan = self.data['logistics_plan']['delivery_plan']
        
        # Create scatter map
        fig = go.Figure()
        
        # Add all zones
        fig.add_trace(go.Scattergeo(
            lon=zones_data['longitude'],
            lat=zones_data['latitude'],
            text=zones_data['zone_name'],
            mode='markers+text',
            marker=dict(
                size=zones_data['population'] / 100,
                color='lightblue',
                line=dict(width=1, color='darkblue')
            ),
            textposition="top center",
            name='Settlement Zones'
        ))
        
        # Add depot
        depot_lon = zones_data['longitude'].mean()
        depot_lat = zones_data['latitude'].mean()
        
        fig.add_trace(go.Scattergeo(
            lon=[depot_lon],
            lat=[depot_lat],
            text=['Distribution Center'],
            mode='markers+text',
            marker=dict(size=20, color='red', symbol='square'),
            textposition="top center",
            name='Depot'
        ))
        
        # Add routes
        colors = px.colors.qualitative.Set1
        for i, route in enumerate(delivery_plan['routes']):
            route_zones = route['zones_sequence']
            route_zone_data = zones_data[zones_data['zone_id'].isin(route_zones)]
            
            # Create route line
            lons = [depot_lon] + list(route_zone_data['longitude']) + [depot_lon]
            lats = [depot_lat] + list(route_zone_data['latitude']) + [depot_lat]
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                line=dict(width=2, color=colors[i % len(colors)]),
                name=f'Route {route["route_id"]}'
            ))
        
        fig.update_layout(
            title='Delivery Route Map',
            geo=dict(
                projection_type='mercator',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                center=dict(lon=depot_lon, lat=depot_lat),
                projection_scale=50
            ),
            height=700
        )
        
        fig.write_html(output_file)
        print(f"✓ Route map saved to: {output_file}")
        
        return fig
    
    def create_performance_timeline(self, multiple_cycles, output_file='outputs/timeline.html'):
        """Create performance timeline across multiple cycles"""
        
        if not isinstance(multiple_cycles, list):
            multiple_cycles = [multiple_cycles]
        
        cycles = [c['cycle_number'] for c in multiple_cycles]
        success_rates = [c['performance_metrics']['success_rate'] for c in multiple_cycles]
        populations = [c['performance_metrics']['population_served'] for c in multiple_cycles]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Success Rate Over Time', 'Population Served Over Time')
        )
        
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=success_rates,
                mode='lines+markers',
                name='Success Rate',
                line=dict(color='green', width=3),
                marker=dict(size=10)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=cycles,
                y=populations,
                name='Population',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Cycle Number", row=2, col=1)
        fig.update_yaxes(title_text="Success Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Population Served", row=2, col=1)
        
        fig.update_layout(
            title_text="Performance Timeline",
            height=800,
            showlegend=False
        )
        
        fig.write_html(output_file)
        print(f"✓ Timeline saved to: {output_file}")
        
        return fig


def visualize_results(results_file_or_data, create_all=True):
    """
    Convenience function to create all visualizations
    
    Args:
        results_file_or_data: Path to JSON file or results dictionary
        create_all: Create all available visualizations
    """
    dashboard = HumanitarianDashboard(results_file_or_data)
    
    visualizations = []
    
    if create_all:
        print("\n📊 Creating visualizations...")
        visualizations.append(dashboard.create_comprehensive_dashboard())
        visualizations.append(dashboard.create_route_map())
    
    return visualizations


if __name__ == "__main__":
    # Test visualization with sample data
    print("Visualization module loaded successfully!")
    print("Use visualize_results(results_data) to create dashboards")