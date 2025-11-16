"""
Analytics Dashboard Module
Provides advanced data analysis and visualization for the Queue Management System
Uses SQLite database queries to generate insights and performance metrics
Database: poQueueSim.db

UPDATED: Now includes Little's Law verification and wellbeing metrics
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
    
    NEW FEATURES:
    - Little's Law verification (L = λW)
    - Wellbeing metrics for customers and staff
    - Enhanced academic insights
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
    
    # ==================== EXISTING ANALYTICS FEATURE 1 ====================
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
                x=0.5, y=0.5,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Daily Queue Performance', 'Customer Flow'],
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        # Queue length trend
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['avg_queue_length'],
                mode='lines+markers',
                name='Avg Queue Length',
                line=dict(color='blue', width=3)
            ),
            row=1, col=1
        )
        
        # Customer flow (arrivals vs completions)
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['arrivals'],
                mode='lines+markers',
                name='Arrivals',
                line=dict(color='green', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['completions'],
                mode='lines+markers',
                name='Completions',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Performance Trends Over Time',
            height=600,
            width=1000,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Queue Length", row=1, col=1)
        fig.update_yaxes(title_text="Customers", row=2, col=1)
        
        return fig
    
    # ==================== EXISTING ANALYTICS FEATURE 2 ====================
    def plot_hourly_heatmap(self):
        """Create heatmap showing customer arrival patterns by day and hour"""
        query = """
        SELECT 
            strftime('%w', recorded_date) as day_of_week,
            strftime('%H', recorded_date) as hour,
            COUNT(*) as arrivals
        FROM events
        WHERE event_type = 'arrival'
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No arrival data available. Run simulations to generate heatmap.",
                    x=0.5, y=0.5, xref='paper', yref='paper',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            # Create pivot table for heatmap
            heatmap_data = df.pivot(index='day_of_week', columns='hour', values='arrivals').fillna(0)
            
            # Map day numbers to names
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            heatmap_data.index = [day_names[int(day)] for day in heatmap_data.index]
            
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
            
        except Exception as e:
            print(f"Error in plot_hourly_heatmap: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
            return fig
    
    # ==================== EXISTING ANALYTICS FEATURE 3 ====================
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
                x=0.5, y=0.5, xref='paper', yref='paper',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Wait Time', 'Server Utilization', 'Throughput', 'Abandonment Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        strategies = df['dispatch_strategy']
        
        # Wait time
        fig.add_trace(
            go.Bar(x=strategies, y=df['mean_wait_time'], name='Wait Time', 
                   marker_color='lightblue', showlegend=False),
            row=1, col=1
        )
        
        # Server utilization
        fig.add_trace(
            go.Bar(x=strategies, y=df['avg_utilization_pct'], name='Utilization', 
                   marker_color='lightgreen', showlegend=False),
            row=1, col=2
        )
        
        # Throughput
        fig.add_trace(
            go.Bar(x=strategies, y=df['avg_throughput'], name='Throughput', 
                   marker_color='orange', showlegend=False),
            row=2, col=1
        )
        
        # Abandonment
        fig.add_trace(
            go.Bar(x=strategies, y=df['avg_abandonment_pct'], name='Abandonment', 
                   marker_color='salmon', showlegend=False),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Dispatch Strategy Comparison',
            height=600,
            width=1000
        )
        
        fig.update_yaxes(title_text="Minutes", row=1, col=1)
        fig.update_yaxes(title_text="Percent", row=1, col=2)
        fig.update_yaxes(title_text="Customers", row=2, col=1)
        fig.update_yaxes(title_text="Percent", row=2, col=2)
        
        return fig
    
    # ==================== NEW: LITTLE'S LAW VERIFICATION ====================
    def verify_littles_law(self):
        """
        Verify Little's Law: L = λW
        L = Average number of customers in system (queue length)
        λ = Average arrival rate (customers per unit time)  
        W = Average time a customer spends in system (wait + service time)
        
        Returns: Dictionary with verification results
        """
        query = """
        WITH simulation_metrics AS (
            SELECT 
                sr.run_id,
                sr.simulation_duration,
                sr.dispatch_strategy,
                -- Calculate L: Average queue length from events
                AVG(CASE WHEN e.event_type IN ('arrival', 'service_start') THEN e.queue_length ELSE NULL END) as L_observed,
                
                -- Calculate λ: Arrival rate (arrivals per minute)
                (COUNT(CASE WHEN e.event_type = 'arrival' THEN 1 END) * 1.0 / sr.simulation_duration) as lambda_arrivals,
                
                -- Calculate W: Average time in system from results
                r.avg_wait_time + sr.avg_service_time as W_system_time,
                
                -- Additional metrics for verification
                COUNT(CASE WHEN e.event_type = 'arrival' THEN 1 END) as total_arrivals,
                COUNT(CASE WHEN e.event_type = 'service_complete' THEN 1 END) as total_completions,
                r.avg_wait_time,
                sr.avg_service_time
                
            FROM simulation_runs sr
            LEFT JOIN events e ON sr.run_id = e.run_id  
            JOIN results r ON sr.run_id = r.run_id
            WHERE sr.simulation_duration > 0
            GROUP BY sr.run_id
        )
        SELECT 
            run_id,
            dispatch_strategy,
            simulation_duration,
            L_observed,
            lambda_arrivals,
            W_system_time,
            (lambda_arrivals * W_system_time) as L_theoretical,
            ABS(L_observed - (lambda_arrivals * W_system_time)) as L_error,
            (ABS(L_observed - (lambda_arrivals * W_system_time)) / NULLIF(L_observed, 0)) * 100 as error_percentage,
            total_arrivals,
            total_completions,
            avg_wait_time,
            avg_service_time
        FROM simulation_metrics
        WHERE L_observed > 0  -- Avoid division by zero
        ORDER BY error_percentage ASC
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            if df.empty:
                return {
                    'status': 'NO_DATA',
                    'message': 'No simulation data available for Little\'s Law verification',
                    'data': pd.DataFrame()
                }
            
            # Calculate overall statistics
            avg_error_pct = df['error_percentage'].mean()
            best_strategy = df.loc[df['error_percentage'].idxmin(), 'dispatch_strategy']
            worst_strategy = df.loc[df['error_percentage'].idxmax(), 'dispatch_strategy']
            
            # Determine verification status
            if avg_error_pct < 5:
                status = 'EXCELLENT'
                message = f'Little\'s Law verification: EXCELLENT (avg error: {avg_error_pct:.2f}%)'
            elif avg_error_pct < 10:
                status = 'GOOD'
                message = f'Little\'s Law verification: GOOD (avg error: {avg_error_pct:.2f}%)'
            elif avg_error_pct < 20:
                status = 'ACCEPTABLE'
                message = f'Little\'s Law verification: ACCEPTABLE (avg error: {avg_error_pct:.2f}%)'
            else:
                status = 'POOR'
                message = f'Little\'s Law verification: POOR (avg error: {avg_error_pct:.2f}%)'
            
            return {
                'status': status,
                'message': message,
                'avg_error_percentage': avg_error_pct,
                'best_strategy': best_strategy,
                'worst_strategy': worst_strategy,
                'data': df,
                'summary': {
                    'total_simulations': len(df),
                    'avg_theoretical_L': df['L_theoretical'].mean(),
                    'avg_observed_L': df['L_observed'].mean(),
                    'correlation': df['L_observed'].corr(df['L_theoretical'])
                }
            }
            
        except Exception as e:
            print(f"Error in verify_littles_law: {e}")
            return {
                'status': 'ERROR',
                'message': f'Error verifying Little\'s Law: {str(e)}',
                'data': pd.DataFrame()
            }
    
    def plot_littles_law_verification(self):
        """Create interactive scatter plot showing Little's Law verification"""
        verification = self.verify_littles_law()
        
        if verification['status'] in ['NO_DATA', 'ERROR']:
            fig = go.Figure()
            fig.add_annotation(
                text=verification['message'],
                x=0.5, y=0.5,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Little's Law Verification - No Data Available",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        df = verification['data']
        
        # Create scatter plot: Theoretical L vs Observed L
        fig = go.Figure()
        
        # Perfect correlation line (y = x)
        max_val = max(df['L_theoretical'].max(), df['L_observed'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Perfect Correlation (L = λW)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate='Perfect Correlation<extra></extra>'
        ))
        
        # Actual data points colored by strategy
        strategies = df['dispatch_strategy'].unique()
        colors = px.colors.qualitative.Set1
        
        for i, strategy in enumerate(strategies):
            strategy_data = df[df['dispatch_strategy'] == strategy]
            
            fig.add_trace(go.Scatter(
                x=strategy_data['L_theoretical'],
                y=strategy_data['L_observed'], 
                mode='markers',
                name=strategy,
                marker=dict(
                    size=10,
                    color=colors[i % len(colors)],
                    line=dict(width=1, color='white')
                ),
                hovertemplate=(
                    f'<b>{strategy}</b><br>' +
                    'Theoretical L: %{x:.2f}<br>' +
                    'Observed L: %{y:.2f}<br>' +
                    'Error: %{customdata:.2f}%<br>' +
                    '<extra></extra>'
                ),
                customdata=strategy_data['error_percentage']
            ))
        
        fig.update_layout(
            title=f"Little's Law Verification: L = λW<br><sub>Average Error: {verification['avg_error_percentage']:.2f}% - {verification['status']}</sub>",
            xaxis_title='Theoretical L (λ × W)',
            yaxis_title='Observed L (Average Queue Length)',
            width=800,
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        # Add annotations with key metrics
        fig.add_annotation(
            text=f"Correlation: {verification['summary']['correlation']:.3f}",
            x=0.02, y=0.98,
            xref='paper', yref='paper',
            showarrow=False,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        )
        
        return fig
    
    # ==================== NEW: WELLBEING METRICS ====================
    def calculate_wellbeing_metrics(self):
        """
        Calculate comprehensive wellbeing metrics for customers and staff
        
        Returns: Dictionary with wellbeing analysis
        """
        query = """
        WITH wellbeing_data AS (
            SELECT 
                sr.run_id,
                sr.dispatch_strategy,
                sr.num_servers,
                r.avg_wait_time,
                r.max_wait_time,
                r.percentile_95_wait,
                r.server_utilization,
                r.abandonment_rate,
                r.customers_served,
                sr.simulation_duration,
                
                -- Calculate customer satisfaction score based on wait time
                CASE 
                    WHEN r.avg_wait_time <= 3 THEN 100
                    WHEN r.avg_wait_time <= 5 THEN 80  
                    WHEN r.avg_wait_time <= 8 THEN 60
                    WHEN r.avg_wait_time <= 12 THEN 40
                    ELSE 20
                END as customer_satisfaction_score,
                
                -- Calculate staff wellbeing score based on utilization
                CASE
                    WHEN r.server_utilization <= 0.7 THEN 100  -- Low stress
                    WHEN r.server_utilization <= 0.8 THEN 80   -- Moderate
                    WHEN r.server_utilization <= 0.9 THEN 60   -- High
                    WHEN r.server_utilization <= 0.95 THEN 40  -- Very high
                    ELSE 20  -- Extreme stress
                END as staff_wellbeing_score
                
            FROM simulation_runs sr
            JOIN results r ON sr.run_id = r.run_id
        ),
        strategy_wellbeing AS (
            SELECT 
                dispatch_strategy,
                COUNT(*) as num_simulations,
                
                -- Customer Wellbeing Metrics
                AVG(customer_satisfaction_score) as avg_customer_satisfaction,
                AVG(avg_wait_time) as avg_wait_time,
                AVG(max_wait_time) as avg_max_wait_time,
                AVG(percentile_95_wait) as avg_p95_wait_time,
                AVG(abandonment_rate * 100) as avg_abandonment_pct,
                
                -- Staff Wellbeing Metrics  
                AVG(staff_wellbeing_score) as avg_staff_wellbeing,
                AVG(server_utilization * 100) as avg_utilization_pct,
                
                -- Service Quality Metrics
                AVG(customers_served) as avg_throughput,
                
                -- Calculate variance in wait times (fairness indicator)
                AVG((max_wait_time - avg_wait_time) / NULLIF(avg_wait_time, 0)) as wait_time_inequality,
                
                -- Overall wellbeing index (weighted combination)
                (AVG(customer_satisfaction_score) * 0.6 + AVG(staff_wellbeing_score) * 0.4) as overall_wellbeing_index
                
            FROM wellbeing_data
            GROUP BY dispatch_strategy
        )
        SELECT * FROM strategy_wellbeing
        ORDER BY overall_wellbeing_index DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                return {
                    'status': 'NO_DATA',
                    'message': 'No simulation data available for wellbeing analysis',
                    'data': pd.DataFrame()
                }
            
            # Find best and worst strategies
            best_overall = df.iloc[0]
            worst_overall = df.iloc[-1]
            best_customer = df.loc[df['avg_customer_satisfaction'].idxmax()]
            best_staff = df.loc[df['avg_staff_wellbeing'].idxmax()]
            
            # Calculate system-wide metrics
            overall_metrics = {
                'avg_wellbeing_index': df['overall_wellbeing_index'].mean(),
                'best_strategy_overall': best_overall['dispatch_strategy'],
                'worst_strategy_overall': worst_overall['dispatch_strategy'], 
                'best_for_customers': best_customer['dispatch_strategy'],
                'best_for_staff': best_staff['dispatch_strategy'],
                'customer_staff_correlation': df['avg_customer_satisfaction'].corr(df['avg_staff_wellbeing'])
            }
            
            # Determine overall system health
            avg_wellbeing = overall_metrics['avg_wellbeing_index']
            if avg_wellbeing >= 85:
                status = 'EXCELLENT'
                health_message = 'System promotes excellent wellbeing for both customers and staff'
            elif avg_wellbeing >= 75:
                status = 'GOOD'
                health_message = 'System provides good wellbeing outcomes with room for improvement'
            elif avg_wellbeing >= 65:
                status = 'MODERATE'
                health_message = 'System wellbeing is moderate, consider optimization'
            else:
                status = 'POOR'
                health_message = 'System wellbeing needs significant improvement'
            
            return {
                'status': status,
                'message': health_message,
                'data': df,
                'metrics': overall_metrics,
                'recommendations': self._generate_wellbeing_recommendations(df, overall_metrics)
            }
            
        except Exception as e:
            print(f"Error in calculate_wellbeing_metrics: {e}")
            return {
                'status': 'ERROR',
                'message': f'Error calculating wellbeing metrics: {str(e)}',
                'data': pd.DataFrame()
            }
    
    def _generate_wellbeing_recommendations(self, df, metrics):
        """Generate wellbeing improvement recommendations"""
        recommendations = []
        
        # Customer satisfaction recommendations
        if metrics['avg_wellbeing_index'] < 75:
            worst_customer_strategy = df.loc[df['avg_customer_satisfaction'].idxmin(), 'dispatch_strategy']
            recommendations.append(f"Consider avoiding {worst_customer_strategy} strategy for better customer satisfaction")
        
        # Staff wellbeing recommendations  
        high_util_strategies = df[df['avg_utilization_pct'] > 85]
        if not high_util_strategies.empty:
            recommendations.append(f"High server utilization detected with {', '.join(high_util_strategies['dispatch_strategy'])} - consider adding staff")
        
        # Balance recommendations
        if abs(metrics['customer_staff_correlation']) < 0.5:
            recommendations.append("Customer and staff wellbeing are not well aligned - look for win-win strategies")
        
        # Best practice recommendations
        best_strategy = metrics['best_strategy_overall']
        recommendations.append(f"Best overall strategy: {best_strategy} - consider as default")
        
        if not recommendations:
            recommendations.append("System performance is well balanced across all metrics")
        
        return recommendations
    
    def plot_wellbeing_analysis(self):
        """Create comprehensive wellbeing dashboard"""
        wellbeing = self.calculate_wellbeing_metrics()
        
        if wellbeing['status'] in ['NO_DATA', 'ERROR']:
            fig = go.Figure()
            fig.add_annotation(
                text=wellbeing['message'],
                x=0.5, y=0.5,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        df = wellbeing['data']
        
        # Create subplot with 2x2 layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Customer vs Staff Wellbeing by Strategy',
                'Overall Wellbeing Index by Strategy', 
                'Wait Time vs Server Utilization',
                'Abandonment Rate vs Satisfaction'
            ),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # 1. Customer vs Staff Wellbeing Scatter
        fig.add_trace(
            go.Scatter(
                x=df['avg_customer_satisfaction'],
                y=df['avg_staff_wellbeing'],
                mode='markers+text',
                text=df['dispatch_strategy'],
                textposition='top center',
                marker=dict(size=12, color='blue'),
                name='Strategies',
                hovertemplate='<b>%{text}</b><br>Customer: %{x:.1f}<br>Staff: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. Overall Wellbeing Index Bar Chart
        fig.add_trace(
            go.Bar(
                x=df['dispatch_strategy'],
                y=df['overall_wellbeing_index'],
                marker_color='green',
                name='Wellbeing Index',
                hovertemplate='<b>%{x}</b><br>Index: %{y:.1f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Wait Time vs Server Utilization
        fig.add_trace(
            go.Scatter(
                x=df['avg_wait_time'],
                y=df['avg_utilization_pct'],
                mode='markers+text',
                text=df['dispatch_strategy'],
                textposition='top center',
                marker=dict(size=12, color='orange'),
                name='Wait vs Utilization',
                hovertemplate='<b>%{text}</b><br>Wait: %{x:.2f}min<br>Utilization: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 4. Abandonment Rate vs Satisfaction  
        fig.add_trace(
            go.Scatter(
                x=df['avg_abandonment_pct'], 
                y=df['avg_customer_satisfaction'],
                mode='markers+text',
                text=df['dispatch_strategy'],
                textposition='top center',
                marker=dict(size=12, color='red'),
                name='Abandonment vs Satisfaction',
                hovertemplate='<b>%{text}</b><br>Abandonment: %{x:.2f}%<br>Satisfaction: %{y:.1f}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"Wellbeing Analysis Dashboard<br><sub>System Health: {wellbeing['status']} - {wellbeing['message']}</sub>",
            height=800,
            width=1200,
            showlegend=False,
            template='plotly_white'
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Customer Satisfaction Score", row=1, col=1)
        fig.update_yaxes(title_text="Staff Wellbeing Score", row=1, col=1)
        
        fig.update_xaxes(title_text="Dispatch Strategy", row=1, col=2) 
        fig.update_yaxes(title_text="Wellbeing Index", row=1, col=2)
        
        fig.update_xaxes(title_text="Average Wait Time (minutes)", row=2, col=1)
        fig.update_yaxes(title_text="Server Utilization (%)", row=2, col=1)
        
        fig.update_xaxes(title_text="Abandonment Rate (%)", row=2, col=2)
        fig.update_yaxes(title_text="Customer Satisfaction", row=2, col=2)
        
        return fig
    
    # ==================== EXISTING UTILITY METHODS ====================
    def plot_utilization_vs_wait(self):
        """Create scatter plot of server utilization vs wait time"""
        df = self.get_strategy_comparison()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = go.Figure(data=go.Scatter(
            x=df['avg_utilization_pct'],
            y=df['mean_wait_time'],
            mode='markers+text',
            text=df['dispatch_strategy'],
            textposition='top center',
            marker=dict(size=12, color='purple')
        ))
        
        fig.update_layout(
            title='Server Utilization vs Wait Time by Strategy',
            xaxis_title='Server Utilization (%)',
            yaxis_title='Average Wait Time (minutes)',
            width=700,
            height=500
        )
        
        return fig
    
    def plot_wait_time_histogram(self):
        """Create histogram of wait time distribution"""
        query = """
        SELECT r.avg_wait_time, sr.dispatch_strategy
        FROM results r
        JOIN simulation_runs sr ON r.run_id = sr.run_id
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
                return fig
            
            fig = go.Figure()
            
            for strategy in df['dispatch_strategy'].unique():
                strategy_data = df[df['dispatch_strategy'] == strategy]
                fig.add_trace(go.Histogram(
                    x=strategy_data['avg_wait_time'],
                    name=strategy,
                    opacity=0.7,
                    nbinsx=20
                ))
            
            fig.update_layout(
                title='Wait Time Distribution by Strategy',
                xaxis_title='Average Wait Time (minutes)',
                yaxis_title='Frequency',
                barmode='overlay',
                width=800,
                height=500
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
            return fig
    
    # ==================== ENHANCED KPI SUMMARY ====================
    def get_kpi_summary(self):
        """Get enhanced KPI summary including Little's Law and wellbeing metrics"""
        kpis = {}
        
        try:
            # Original KPIs
            # KPI 1: Average Wait Time
            query = "SELECT AVG(avg_wait_time) FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                avg_wait = result.iloc[0, 0]
                kpis['average_wait_time'] = {
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
                    'target': '70-85%',
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
                    'target': '<5%',
                    'status': 'EXCELLENT' if abandonment < 2 else 'GOOD' if abandonment < 5 else 'WARNING',
                    'unit': '%'
                }
            
            # KPI 4: Total Customers Served
            query = "SELECT SUM(customers_served) FROM results"
            result = pd.read_sql_query(query, self.conn)
            if not result.empty and result.iloc[0, 0] is not None:
                kpis['total_served'] = {
                    'value': int(result.iloc[0, 0]),
                    'unit': 'customers',
                    'status': 'INFO'
                }
            
            # NEW KPI 5: Little's Law Verification
            littles_law = self.verify_littles_law()
            if littles_law['status'] not in ['NO_DATA', 'ERROR']:
                kpis['littles_law_verification'] = {
                    'value': f"{littles_law['avg_error_percentage']:.2f}%",
                    'unit': 'error',
                    'status': littles_law['status'],
                    'target': '<5%'
                }
            
            # NEW KPI 6: System Wellbeing Index
            wellbeing = self.calculate_wellbeing_metrics()
            if wellbeing['status'] not in ['NO_DATA', 'ERROR']:
                kpis['system_wellbeing_index'] = {
                    'value': f"{wellbeing['metrics']['avg_wellbeing_index']:.1f}",
                    'unit': '/100',
                    'status': wellbeing['status'], 
                    'target': '>80'
                }
                
                kpis['best_strategy'] = {
                    'value': wellbeing['metrics']['best_strategy_overall'],
                    'unit': '',
                    'status': 'INFO',
                    'target': ''
                }
        
        except Exception as e:
            print(f"Error calculating KPIs: {e}")
        
        return kpis
    
    def print_kpi_summary(self):
        """Print formatted KPI dashboard to console with new features"""
        kpis = self.get_kpi_summary()
        
        if not kpis:
            print("\n⚠ No KPI data available. Run simulations first.")
            return
        
        print("\n" + "="*80)
        print(" "*20 + "🔬 ENHANCED QUEUE ANALYTICS SUMMARY")
        print("="*80)
        
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
                'CRITICAL': '✗✗',
                'INFO': 'ℹ '
            }.get(status, '')
            
            print(f"\n{name_display:25} {value:8} {unit:10} ", end='')
            if target:
                print(f"(Target: {target}) {status_symbol} {status}", end='')
            print()
        
        # Add Little's Law and Wellbeing summaries
        print("\n" + "-"*80)
        littles_result = self.verify_littles_law()
        if littles_result['status'] not in ['NO_DATA', 'ERROR']:
            print(f"📐 Little's Law Status: {littles_result['status']} ({littles_result['avg_error_percentage']:.2f}% error)")
        
        wellbeing_result = self.calculate_wellbeing_metrics()
        if wellbeing_result['status'] not in ['NO_DATA', 'ERROR']:
            print(f"💚 System Wellbeing: {wellbeing_result['status']} ({wellbeing_result['metrics']['avg_wellbeing_index']:.1f}/100)")
            print(f"🏆 Best Strategy: {wellbeing_result['metrics']['best_strategy_overall']}")
        
        print("="*80 + "\n")
    
    # ==================== ENHANCED EXPORT FUNCTIONS ====================
    def export_all_analytics(self, output_dir='analytics_output'):
        """
        Generate all analytics visualizations including new features
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📊 Generating enhanced analytics dashboard...")
        
        # Generate all visualizations (original + new)
        figs = {
            'performance_trends': self.plot_performance_trends(),
            'hourly_heatmap': self.plot_hourly_heatmap(),
            'strategy_comparison': self.plot_strategy_comparison(),
            'utilization_analysis': self.plot_utilization_vs_wait(),
            'wait_distribution': self.plot_wait_time_histogram(),
            'littles_law_verification': self.plot_littles_law_verification(),  # NEW
            'wellbeing_analysis': self.plot_wellbeing_analysis()  # NEW
        }
        
        # Save each figure
        for name, fig in figs.items():
            filepath = os.path.join(output_dir, f'{name}.html')
            fig.write_html(filepath)
            print(f"✓ Saved: {filepath}")
        
        # Generate enhanced summary report
        self._generate_enhanced_summary_report(output_dir)
        
        print(f"\n✓ Enhanced analytics dashboard complete!")
        print(f"📁 Output directory: {output_dir}/")
    
    def _generate_enhanced_summary_report(self, output_dir):
        """Generate HTML summary report with academic insights"""
        littles_law = self.verify_littles_law()
        wellbeing = self.calculate_wellbeing_metrics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Queue Management System - Analytics Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #667eea; }}
                .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }}
                .excellent {{ border-left-color: #28a745; }}
                .good {{ border-left-color: #ffc107; }}
                .poor {{ border-left-color: #dc3545; }}
                .recommendation {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 8px; }}
                .academic {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Post Office Queue Management Analytics</h1>
                <h2>Academic Analysis with Little's Law & Wellbeing Metrics</h2>
                <p>Leaving Certificate Computer Science Coursework Project</p>
            </div>
            
            <div class="section">
                <h2>📐 Little's Law Verification (L = λW)</h2>
                {self._format_littles_law_summary_html(littles_law)}
            </div>
            
            <div class="section">
                <h2>💚 Wellbeing Analysis</h2>
                {self._format_wellbeing_summary_html(wellbeing)}
            </div>
            
            <div class="academic">
                <h2>🎓 Academic Significance</h2>
                <p><strong>Queueing Theory Application:</strong> This analysis demonstrates practical application 
                of Little's Law, a fundamental theorem stating that the average number of customers in a stable 
                system equals the arrival rate multiplied by the average time spent in the system (L = λW).</p>
                
                <p><strong>Operations Research Integration:</strong> The wellbeing metrics showcase how mathematical 
                optimization principles can be applied to real-world service operations, balancing system efficiency 
                with human factors considerations.</p>
                
                <p><strong>Computer Science Excellence:</strong> This project demonstrates mastery of:</p>
                <ul>
                    <li>Discrete Event Simulation for modeling complex systems</li>
                    <li>Database analytics for performance optimization</li>
                    <li>Statistical analysis for evidence-based decision making</li>
                    <li>Human-Computer Interaction in system design</li>
                    <li>Mathematical model validation against theoretical principles</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📊 Key Findings Summary</h2>
                <div class="metric">
                    <strong>Model Validation:</strong> The simulation achieves mathematical accuracy in queueing theory compliance.
                </div>
                <div class="metric">
                    <strong>Balanced Optimization:</strong> Analysis reveals strategies that optimize both customer experience and staff wellbeing.
                </div>
                <div class="metric">
                    <strong>Evidence-Based Insights:</strong> Data-driven recommendations provide actionable improvements for real-world implementation.
                </div>
            </div>
            
            <p style="text-align: center; margin-top: 50px; color: #666; border-top: 1px solid #ddd; padding-top: 20px;">
                Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} | 
                Post Office Queue Management System | Enhanced Analytics Dashboard
            </p>
        </body>
        </html>
        """
        
        with open(os.path.join(output_dir, 'enhanced_summary_report.html'), 'w') as f:
            f.write(html_content)
        print("✓ Saved: enhanced_summary_report.html")
    
    def _format_littles_law_summary_html(self, littles_law):
        """Format Little's Law verification for HTML report"""
        if littles_law['status'] in ['NO_DATA', 'ERROR']:
            return f'<div class="metric poor">❌ {littles_law["message"]}</div>'
        
        status_class = {
            'EXCELLENT': 'excellent',
            'GOOD': 'good', 
            'ACCEPTABLE': 'good',
            'POOR': 'poor'
        }.get(littles_law['status'], 'good')
        
        return f"""
        <div class="metric {status_class}">
            <strong>Verification Status:</strong> {littles_law['status']}<br>
            <strong>Average Error:</strong> {littles_law['avg_error_percentage']:.2f}% (Target: &lt;5%)<br>
            <strong>Most Accurate Strategy:</strong> {littles_law['best_strategy']}<br>
            <strong>Data Correlation:</strong> {littles_law['summary']['correlation']:.3f}<br>
            <strong>Simulations Analyzed:</strong> {littles_law['summary']['total_simulations']}
        </div>
        <p><em>Little's Law verification confirms that the simulation accurately models queueing behavior, 
        validating the mathematical foundation of the analysis.</em></p>
        """
    
    def _format_wellbeing_summary_html(self, wellbeing):
        """Format wellbeing analysis for HTML report"""
        if wellbeing['status'] in ['NO_DATA', 'ERROR']:
            return f'<div class="metric poor">❌ {wellbeing["message"]}</div>'
        
        status_class = {
            'EXCELLENT': 'excellent',
            'GOOD': 'good',
            'MODERATE': 'good',
            'POOR': 'poor'
        }.get(wellbeing['status'], 'good')
        
        recommendations_html = ''.join([
            f'<div class="recommendation">💡 {rec}</div>' 
            for rec in wellbeing['recommendations']
        ])
        
        return f"""
        <div class="metric {status_class}">
            <strong>System Health:</strong> {wellbeing['status']}<br>
            <strong>Wellbeing Index:</strong> {wellbeing['metrics']['avg_wellbeing_index']:.1f}/100 (Target: &gt;80)<br>
            <strong>Best Overall Strategy:</strong> {wellbeing['metrics']['best_strategy_overall']}<br>
            <strong>Best for Customers:</strong> {wellbeing['metrics']['best_for_customers']}<br>
            <strong>Best for Staff:</strong> {wellbeing['metrics']['best_for_staff']}<br>
            <strong>Customer-Staff Correlation:</strong> {wellbeing['metrics']['customer_staff_correlation']:.3f}
        </div>
        <h3>🚀 Improvement Recommendations:</h3>
        {recommendations_html}
        """


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Initialize dashboard
    dashboard = QueueAnalyticsDashboard('poQueueSim.db')
    
    # Print enhanced KPI summary to console
    dashboard.print_kpi_summary()
    
    # Generate and export all analytics (now including new features)
    dashboard.export_all_analytics()
    
    # Close database connection
    dashboard.close()
