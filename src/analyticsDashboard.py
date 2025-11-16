"""
Analytics Dashboard Module
Provides advanced data analysis and visualization for the Queue Management System
Uses SQLite database queries to generate insights and performance metrics
Database: poQueueSim.db
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os

class QueueAnalyticsDashboard:
    """
    Advanced analytics dashboard for queue management system.
    Performs SQL queries on the database and generates visualizations.
    """
    
    def __init__(self, db_path='poQueueSim.db'):
        """Initialize connection to SQLite database"""
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✓ Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"✗ Database connection error: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    # ==================== ANALYTICS FEATURE 1 ====================
    def get_performance_trends(self, days=30):
        """
        Analyze performance trends over time
        Returns: DataFrame with daily statistics
        """
        query = f"""
        SELECT 
            DATE(recorded_date) as date,
            AVG(queue_length) as avg_queue_length,
            COUNT(*) as total_events,
            SUM(CASE WHEN event_type = 'arrival' THEN 1 ELSE 0 END) as arrivals,
            SUM(CASE WHEN event_type = 'service_complete' THEN 1 ELSE 0 END) as completions
        FROM events
        WHERE recorded_date >= date('now', '-{days} days')
        GROUP BY DATE(recorded_date)
        ORDER BY date
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            print(f"Error in get_performance_trends: {e}")
            return pd.DataFrame()
    
    def plot_performance_trends(self, days=30):
        """Create interactive line chart of performance over time"""
        df = self.get_performance_trends(days)
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available. Run simulations to generate data.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title=f"Queue Performance Trends - Last {days} Days")
            return fig
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Average Queue Length Over Time', 'Daily Customer Volume'),
            vertical_spacing=0.15
        )
        
        # Plot 1: Queue length trend
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['avg_queue_length'], 
                name='Avg Queue Length',
                line=dict(color='#667eea', width=3)
            ),
            row=1, col=1
        )
        
        # Plot 2: Customer volume
        fig.add_trace(
            go.Bar(
                x=df['date'], 
                y=df['arrivals'], 
                name='Arrivals',
                marker_color='#48bb78'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(
                x=df['date'], 
                y=df['completions'], 
                name='Served',
                marker_color='#4299e1'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=700,
            title_text=f"Queue Performance Trends - Last {days} Days",
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Avg Queue Length", row=1, col=1)
        fig.update_yaxes(title_text="Number of Customers", row=2, col=1)
        
        return fig
    
    # ==================== ANALYTICS FEATURE 2 ====================
    def get_hourly_demand(self):
        """
        Analyze customer arrival patterns by hour and day of week
        Returns: DataFrame with hourly demand statistics
        """
        query = """
        SELECT 
            CASE strftime('%w', datetime(timestamp, 'unixepoch'))
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END as day_of_week,
            strftime('%H', datetime(timestamp, 'unixepoch')) as hour_of_day,
            COUNT(*) as arrival_count,
            AVG(queue_length) as avg_queue
        FROM events
        WHERE event_type = 'arrival'
        GROUP BY day_of_week, hour_of_day
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error in get_hourly_demand: {e}")
            return pd.DataFrame()
    
    def plot_hourly_heatmap(self):
        """Create heatmap showing demand by day and hour"""
        df = self.get_hourly_demand()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hourly data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title='Customer Arrival Heatmap by Day and Hour')
            return fig
        
        # Pivot data for heatmap
        heatmap_data = df.pivot(
            index='day_of_week', 
            columns='hour_of_day', 
            values='arrival_count'
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Reds',
            text=heatmap_data.values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Arrivals")
        ))
        
        fig.update_layout(
            title='Customer Arrival Heatmap by Day and Hour',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=500,
            width=900
        )
        
        return fig
    
    # ==================== ANALYTICS FEATURE 3 ====================
    def get_strategy_comparison(self):
        """
        Compare performance of different dispatch strategies
        Returns: DataFrame with strategy metrics
        """
        query = """
        SELECT 
            sr.dispatch_strategy,
            COUNT(sr.run_id) as num_simulations,
            ROUND(AVG(r.avg_wait_time), 2) as mean_wait_time,
            ROUND(MIN(r.avg_wait_time), 2) as best_wait_time,
            ROUND(MAX(r.avg_wait_time), 2) as worst_wait_time,
            ROUND(AVG(r.server_utilization) * 100, 1) as avg_utilization_pct,
            ROUND(AVG(r.abandonment_rate) * 100, 2) as avg_abandonment_pct,
            ROUND(AVG(r.customers_served), 0) as avg_throughput
        FROM simulation_runs sr
        JOIN results r ON sr.run_id = r.run_id
        GROUP BY sr.dispatch_strategy
        ORDER BY mean_wait_time ASC
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error in get_strategy_comparison: {e}")
            return pd.DataFrame()
    
    def plot_strategy_comparison(self):
        """Create grouped bar chart comparing dispatch strategies"""
        df = self.get_strategy_comparison()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No simulation data available. Run simulations with different strategies.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title='Dispatch Strategy Performance Comparison')
            return fig
        
        fig = go.Figure()
        
        # Add bars for each metric
        fig.add_trace(go.Bar(
            name='Avg Wait Time (min)',
            x=df['dispatch_strategy'],
            y=df['mean_wait_time'],
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name='Utilization (%)',
            x=df['dispatch_strategy'],
            y=df['avg_utilization_pct'],
            marker_color='#48bb78'
        ))
        
        fig.add_trace(go.Bar(
            name='Abandonment (%)',
            x=df['dispatch_strategy'],
            y=df['avg_abandonment_pct'],
            marker_color='#f56565'
        ))
        
        fig.update_layout(
            title='Dispatch Strategy Performance Comparison',
            xaxis_title='Strategy',
            yaxis_title='Value',
            barmode='group',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    # ==================== ANALYTICS FEATURE 4 ====================
    def get_server_utilization_analysis(self):
        """
        Analyze server utilization vs wait time trade-off
        Returns: DataFrame with server count analysis
        """
        query = """
        SELECT 
            sr.num_servers,
            COUNT(*) as scenarios_tested,
            ROUND(AVG(r.server_utilization) * 100, 1) as avg_utilization_pct,
            ROUND(AVG(r.avg_wait_time), 2) as avg_wait_minutes,
            ROUND(AVG(r.customers_served), 0) as avg_throughput
        FROM simulation_runs sr
        JOIN results r ON sr.run_id = r.run_id
        GROUP BY sr.num_servers
        ORDER BY sr.num_servers
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error in get_server_utilization_analysis: {e}")
            return pd.DataFrame()
    
    def plot_utilization_vs_wait(self):
        """Create scatter plot showing utilization vs wait time trade-off"""
        df = self.get_server_utilization_analysis()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No utilization data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title='Server Utilization vs Wait Time Trade-off')
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['avg_utilization_pct'],
            y=df['avg_wait_minutes'],
            mode='markers+text',
            marker=dict(
                size=df['num_servers'] * 15,
                color=df['num_servers'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Servers")
            ),
            text=df['num_servers'].astype(str) + ' servers',
            textposition='top center'
        ))
        
        # Add target zone
        fig.add_shape(
            type="rect",
            x0=70, y0=0, x1=85, y1=5,
            fillcolor="lightgreen", 
            opacity=0.2,
            line_width=0
        )
        
        fig.add_annotation(
            x=77.5, y=2.5,
            text="Optimal Zone<br>70-85% util<br><5 min wait",
            showarrow=False,
            font=dict(size=10)
        )
        
        fig.update_layout(
            title='Server Utilization vs Wait Time Trade-off',
            xaxis_title='Server Utilization (%)',
            yaxis_title='Average Wait Time (minutes)',
            height=500,
            width=700
        )
        
        return fig
    
    # ==================== ANALYTICS FEATURE 5 ====================
    def get_wait_time_distribution(self):
        """
        Analyze distribution of customer wait times
        Returns: Dictionary with percentile statistics
        """
        query = """
        WITH wait_times AS (
            SELECT 
                (service_start.timestamp - arrival.timestamp) / 60.0 as wait_minutes
            FROM events arrival
            JOIN events service_start 
                ON arrival.customer_id = service_start.customer_id
            WHERE arrival.event_type = 'arrival'
                AND service_start.event_type = 'service_start'
        )
        SELECT 
            COUNT(*) as total_customers,
            ROUND(AVG(wait_minutes), 2) as mean_wait,
            ROUND(MIN(wait_minutes), 2) as min_wait,
            ROUND(MAX(wait_minutes), 2) as max_wait,
            ROUND(SUM(CASE WHEN wait_minutes < 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_under_3min,
            ROUND(SUM(CASE WHEN wait_minutes < 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_under_5min,
            ROUND(SUM(CASE WHEN wait_minutes < 10 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_under_10min
        FROM wait_times
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df.to_dict('records')[0] if not df.empty else {}
        except Exception as e:
            print(f"Error in get_wait_time_distribution: {e}")
            return {}
    
    def plot_wait_time_histogram(self):
        """Create histogram of wait time distribution"""
        query = """
        SELECT 
            (service_start.timestamp - arrival.timestamp) / 60.0 as wait_minutes
        FROM events arrival
        JOIN events service_start 
            ON arrival.customer_id = service_start.customer_id
        WHERE arrival.event_type = 'arrival'
            AND service_start.event_type = 'service_start'
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"Error in plot_wait_time_histogram: {e}")
            df = pd.DataFrame()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No wait time data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title='Customer Wait Time Distribution')
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df['wait_minutes'],
            nbinsx=30,
            marker_color='#667eea',
            opacity=0.7
        ))
        
        # Add percentile lines
        if len(df) > 0:
            p95 = df['wait_minutes'].quantile(0.95)
            fig.add_vline(
                x=p95, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"95th percentile: {p95:.1f} min"
            )
            
            fig.add_vline(
                x=5, 
                line_dash="dash", 
                line_color="green",
                annotation_text="Target: 5 min"
            )
        
        fig.update_layout(
            title='Customer Wait Time Distribution',
            xaxis_title='Wait Time (minutes)',
            yaxis_title='Number of Customers',
            height=500,
            showlegend=False
        )
        
        return fig
    
    # ==================== KPI DASHBOARD ====================
    def get_kpi_summary(self):
        """
        Calculate key performance indicators
        Returns: Dictionary with KPIs and status
        """
        kpis = {}
        
        try:
            # KPI 1: Average Wait Time
            query = "SELECT AVG(avg_wait_time) FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                avg_wait = result.iloc[0, 0]
                kpis['avg_wait_time'] = {
                    'value': round(avg_wait, 2),
                    'target': 5.0,
                    'status': 'GOOD' if avg_wait < 5 else 'WARNING' if avg_wait < 7 else 'CRITICAL',
                    'unit': 'min'
                }
            
            # KPI 2: Server Utilization
            query = "SELECT AVG(server_utilization) * 100 FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                utilization = result.iloc[0, 0]
                kpis['server_utilization'] = {
                    'value': round(utilization, 1),
                    'target': '70-85',
                    'status': 'OPTIMAL' if 70 <= utilization <= 85 else 'MONITOR',
                    'unit': '%'
                }
            
            # KPI 3: Abandonment Rate
            query = "SELECT AVG(abandonment_rate) * 100 FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                abandonment = result.iloc[0, 0]
                kpis['abandonment_rate'] = {
                    'value': round(abandonment, 2),
                    'target': 5.0,
                    'status': 'EXCELLENT' if abandonment < 2 else 'GOOD' if abandonment < 5 else 'WARNING',
                    'unit': '%'
                }
            
            # KPI 4: Total Customers Served
            query = "SELECT SUM(customers_served) FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                kpis['total_served'] = {
                    'value': int(result.iloc[0, 0]),
                    'unit': 'customers'
                }
        except Exception as e:
            print(f"Error calculating KPIs: {e}")
        
        return kpis
    
    def print_kpi_summary(self):
        """Print formatted KPI dashboard to console"""
        kpis = self.get_kpi_summary()
        
        if not kpis:
            print("\n⚠ No KPI data available. Run simulations first.")
            return
        
        print("\n" + "="*60)
        print(" "*15 + "KEY PERFORMANCE INDICATORS")
        print("="*60)
        
        for kpi_name, kpi_data in kpis.items():
            name_display = kpi_name.replace('_', ' ').title()
            value = kpi_data['value']
            unit = kpi_data.get('unit', '')
            status = kpi_data.get('status', '')
            target = kpi_data.get('target', '')
            
            status_symbol = {
                'EXCELLENT': '✓✓',
                'OPTIMAL': '✓✓',
                'GOOD': '✓ ',
                'MONITOR': '⚠ ',
                'WARNING': '⚠⚠',
                'CRITICAL': '✗✗'
            }.get(status, '')
            
            print(f"\n{name_display:25} {value:8} {unit:10} ", end='')
            if target:
                print(f"(Target: {target}) {status_symbol} {status}", end='')
            print()
        
        print("="*60 + "\n")
    
    # ==================== EXPORT FUNCTIONS ====================
    def export_all_analytics(self, output_dir='analytics_output'):
        """
        Generate all analytics visualizations and save to HTML files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📊 Generating analytics dashboard...")
        
        # Generate all visualizations
        figs = {
            'performance_trends': self.plot_performance_trends(),
            'hourly_heatmap': self.plot_hourly_heatmap(),
            'strategy_comparison': self.plot_strategy_comparison(),
            'utilization_analysis': self.plot_utilization_vs_wait(),
            'wait_distribution': self.plot_wait_time_histogram()
        }
        
        # Save each figure
        for name, fig in figs.items():
            filepath = os.path.join(output_dir, f'{name}.html')
            fig.write_html(filepath)
            print(f"✓ Saved: {filepath}")
        
        print(f"\n✓ Analytics dashboard complete!")
        print(f"📁 Output directory: {output_dir}/")


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Initialize dashboard
    dashboard = QueueAnalyticsDashboard('poQueueSim.db')
    
    # Print KPI summary to console
    dashboard.print_kpi_summary()
    
    # Generate and export all analytics
    dashboard.export_all_analytics()
    
    # Close database connection
    dashboard.close()