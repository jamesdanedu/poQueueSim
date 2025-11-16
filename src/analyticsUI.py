"""
Analytics UI Module (UPDATED)
PyQt5 Analytics Window with Little's Law verification and wellbeing metrics
Embeds the enhanced analytics dashboard into the queue management UI
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QTextEdit,
                             QScrollArea, QGroupBox, QGridLayout, QMessageBox,
                             QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import os
import tempfile
from analyticsDashboard import QueueAnalyticsDashboard  # Updated dashboard


class AnalyticsWindow(QMainWindow):
    """
    Analytics Dashboard Window for Queue Management System
    NOW INCLUDES: Little's Law verification and wellbeing metrics
    """
    
    def __init__(self, db_path='queue_analysis.db', parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.dashboard = None
        self.temp_dir = tempfile.mkdtemp()
        
        self.init_ui()
        self.load_analytics()
    
    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle('📊 Queue Analytics Dashboard')
        self.setGeometry(100, 100, 1400, 900)
        
        # Enhanced styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #e9ecef;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #adb5bd;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #495057;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Enhanced header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget for different analytics views
        self.tabs = QTabWidget()
        
        # Create all tabs (existing + new)
        self.create_kpi_tab()
        self.create_trends_tab()
        self.create_strategy_tab()
        self.create_littles_law_tab()      # NEW TAB
        self.create_wellbeing_tab()        # NEW TAB
        self.create_advanced_insights_tab() # NEW TAB
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage('Enhanced analytics dashboard ready')
        self.statusBar().setStyleSheet("background-color: #e9ecef; padding: 5px;")
    
    def create_header(self):
        """Create enhanced header with controls"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Title section
        title_layout = QVBoxLayout()
        
        title_label = QLabel('📊 Queue Analytics Dashboard')
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel('Performance Analysis • Little\'s Law Verification • Wellbeing Metrics')
        subtitle_label.setStyleSheet("color: #e3f2fd; font-size: 14px;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Control buttons
        controls_layout = QVBoxLayout()
        
        refresh_btn = QPushButton('🔄 Refresh Analytics')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid rgba(255,255,255,0.3);
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
        """)
        refresh_btn.clicked.connect(self.load_analytics)
        controls_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('📈 Export Report')
        export_btn.setStyleSheet(refresh_btn.styleSheet())
        export_btn.clicked.connect(self.export_analytics)
        controls_layout.addWidget(export_btn)
        
        header_layout.addLayout(controls_layout)
        
        return header_frame
    
    def create_kpi_tab(self):
        """Create enhanced KPI overview tab"""
        kpi_widget = QWidget()
        kpi_layout = QVBoxLayout(kpi_widget)
        
        # Add summary info
        summary_label = QLabel("📊 <b>Key Performance Indicators</b><br>Essential metrics including new academic insights")
        summary_label.setStyleSheet("background: #e3f2fd; padding: 15px; border-radius: 6px; margin-bottom: 15px;")
        summary_label.setWordWrap(True)
        kpi_layout.addWidget(summary_label)
        
        # Create scrollable area for KPIs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        self.kpi_grid = QGridLayout(scroll_widget)
        self.kpi_grid.setSpacing(15)
        
        scroll_area.setWidget(scroll_widget)
        kpi_layout.addWidget(scroll_area)
        
        self.tabs.addTab(kpi_widget, '📈 KPI Overview')
    
    def create_trends_tab(self):
        """Create performance trends tab"""
        trends_widget = QWidget()
        trends_layout = QVBoxLayout(trends_widget)
        
        # Info panel
        info_label = QLabel("📈 <b>Performance Trends</b><br>Analysis of queue performance over time")
        info_label.setStyleSheet("background: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 15px;")
        info_label.setWordWrap(True)
        trends_layout.addWidget(info_label)
        
        # Charts container
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        
        self.trends_view = QWebEngineView()
        charts_layout.addWidget(self.trends_view)
        
        self.demand_view = QWebEngineView()
        charts_layout.addWidget(self.demand_view)
        
        trends_layout.addWidget(charts_widget)
        
        self.tabs.addTab(trends_widget, '📈 Performance Trends')
    
    def create_strategy_tab(self):
        """Create strategy comparison tab"""
        strategy_widget = QWidget()
        strategy_layout = QVBoxLayout(strategy_widget)
        
        # Info panel
        info_label = QLabel("⚖️ <b>Strategy Comparison</b><br>Compare dispatch strategies across multiple metrics")
        info_label.setStyleSheet("background: #fff3cd; padding: 15px; border-radius: 6px; margin-bottom: 15px;")
        info_label.setWordWrap(True)
        strategy_layout.addWidget(info_label)
        
        self.strategy_view = QWebEngineView()
        strategy_layout.addWidget(self.strategy_view)
        
        self.tabs.addTab(strategy_widget, '⚖️ Strategy Analysis')
    
    def create_littles_law_tab(self):
        """Create Little's Law verification tab (NEW)"""
        littles_widget = QWidget()
        littles_layout = QVBoxLayout(littles_widget)
        
        # Theory explanation
        theory_group = QGroupBox("📐 Little's Law: L = λW")
        theory_layout = QVBoxLayout(theory_group)
        
        theory_label = QLabel("""
        <b>Little's Law</b> is a fundamental theorem in queueing theory:<br><br>
        <b>L = λW</b>, where:<br>
        • <b>L</b> = Average number of customers in the system (queue length)<br>
        • <b>λ</b> = Average arrival rate (customers per unit time)<br>
        • <b>W</b> = Average time a customer spends in the system<br><br>
        <em>This verification checks how well our simulation follows this theoretical relationship.</em>
        """)
        theory_label.setStyleSheet("background: #f8f9fa; padding: 15px; border-radius: 6px; line-height: 1.4;")
        theory_label.setWordWrap(True)
        theory_layout.addWidget(theory_label)
        
        littles_layout.addWidget(theory_group)
        
        # Results summary
        self.littles_results_label = QLabel("Loading Little's Law verification...")
        self.littles_results_label.setStyleSheet("""
            background: #d4edda; 
            border: 1px solid #c3e6cb; 
            border-radius: 6px; 
            padding: 15px;
            font-size: 14px;
        """)
        self.littles_results_label.setWordWrap(True)
        littles_layout.addWidget(self.littles_results_label)
        
        # Verification chart
        self.littles_view = QWebEngineView()
        self.littles_view.setMinimumHeight(500)
        littles_layout.addWidget(self.littles_view)
        
        self.tabs.addTab(littles_widget, '📐 Little\'s Law')
    
    def create_wellbeing_tab(self):
        """Create wellbeing metrics tab (NEW)"""
        wellbeing_widget = QWidget()
        wellbeing_layout = QVBoxLayout(wellbeing_widget)
        
        # Explanation panel
        explanation_group = QGroupBox("💚 Wellbeing Analysis Framework")
        explanation_layout = QVBoxLayout(explanation_group)
        
        explanation_label = QLabel("""
        <b>Customer Wellbeing:</b> Based on wait times and service quality<br>
        <b>Staff Wellbeing:</b> Based on server utilization and workload balance<br>
        <b>System Health:</b> Combined metric balancing both customer and staff outcomes<br><br>
        <em>This analysis helps identify dispatch strategies that optimize both efficiency and human experience.</em>
        """)
        explanation_label.setStyleSheet("background: #e8f5e8; padding: 15px; border-radius: 6px; line-height: 1.4;")
        explanation_label.setWordWrap(True)
        explanation_layout.addWidget(explanation_label)
        
        wellbeing_layout.addWidget(explanation_group)
        
        # Wellbeing summary
        self.wellbeing_summary_label = QLabel("Loading wellbeing analysis...")
        self.wellbeing_summary_label.setStyleSheet("""
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 15px;
            font-size: 14px;
        """)
        self.wellbeing_summary_label.setWordWrap(True)
        wellbeing_layout.addWidget(self.wellbeing_summary_label)
        
        # Recommendations panel
        self.recommendations_group = QGroupBox("🚀 Wellbeing Improvement Recommendations")
        self.recommendations_layout = QVBoxLayout(self.recommendations_group)
        wellbeing_layout.addWidget(self.recommendations_group)
        
        # Wellbeing analysis chart
        self.wellbeing_view = QWebEngineView()
        self.wellbeing_view.setMinimumHeight(600)
        wellbeing_layout.addWidget(self.wellbeing_view)
        
        self.tabs.addTab(wellbeing_widget, '💚 Wellbeing Metrics')
    
    def create_advanced_insights_tab(self):
        """Create advanced insights and academic analysis tab (NEW)"""
        insights_widget = QWidget()
        insights_layout = QVBoxLayout(insights_widget)
        
        # Academic insights
        academic_group = QGroupBox("🎓 Academic & Theoretical Insights")
        academic_layout = QVBoxLayout(academic_group)
        
        academic_text = QTextEdit()
        academic_text.setMaximumHeight(200)
        academic_text.setStyleSheet("""
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            font-family: 'Courier New', monospace;
        """)
        academic_text.setPlainText("""
QUEUEING THEORY APPLICATION:

1. Little's Law Verification demonstrates that our simulation accurately models 
   real-world queueing behavior, validating the mathematical foundation.

2. The wellbeing metrics showcase Operations Research principles applied to 
   human-centered service optimization.

3. Strategy comparison reveals trade-offs between efficiency (throughput) 
   and fairness (wait time distribution).

COMPUTER SCIENCE RELEVANCE:

• Discrete Event Simulation modeling real-world systems
• Database analytics for performance optimization  
• Human-Computer Interaction considerations in system design
• Statistical analysis for evidence-based decision making

This project demonstrates advanced CS concepts: simulation, data analysis, 
mathematical modeling, and human-centered system design.
        """)
        academic_layout.addWidget(academic_text)
        
        insights_layout.addWidget(academic_group)
        
        # Performance summary
        performance_group = QGroupBox("📊 System Performance Summary")
        performance_layout = QVBoxLayout(performance_group)
        
        self.performance_summary_label = QLabel("Loading performance summary...")
        self.performance_summary_label.setStyleSheet("""
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 6px;
            padding: 15px;
            font-size: 14px;
        """)
        self.performance_summary_label.setWordWrap(True)
        performance_layout.addWidget(self.performance_summary_label)
        
        insights_layout.addWidget(performance_group)
        
        # Additional analytics charts
        self.util_view = QWebEngineView()
        self.util_view.setMaximumHeight(400)
        insights_layout.addWidget(self.util_view)
        
        self.wait_view = QWebEngineView()
        self.wait_view.setMaximumHeight(400)
        insights_layout.addWidget(self.wait_view)
        
        insights_layout.addStretch()
        
        self.tabs.addTab(insights_widget, '🎓 Advanced Insights')
    
    def create_kpi_card(self, kpi_name, kpi_data):
        """Create enhanced KPI display card"""
        card = QGroupBox()
        card_layout = QVBoxLayout(card)
        
        # Status color mapping
        status_colors = {
            'EXCELLENT': '#28a745',
            'OPTIMAL': '#28a745', 
            'GOOD': '#17a2b8',
            'MONITOR': '#ffc107',
            'WARNING': '#fd7e14',
            'CRITICAL': '#dc3545',
            'INFO': '#6f42c1'
        }
        
        status_color = status_colors.get(kpi_data.get('status', 'INFO'), '#6c757d')
        
        card.setStyleSheet(f"""
            QGroupBox {{
                background: white;
                border: 2px solid {status_color};
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
                max-width: 300px;
                min-height: 120px;
            }}
            QGroupBox::title {{
                color: {status_color};
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        
        # KPI name as title
        card.setTitle(kpi_name.replace('_', ' ').title())
        
        # Value display
        value_label = QLabel(f"{kpi_data['value']} {kpi_data.get('unit', '')}")
        value_label.setStyleSheet(f"color: {status_color}; font-size: 28px; font-weight: bold; margin: 10px 0;")
        value_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(value_label)
        
        # Status and target
        details_layout = QHBoxLayout()
        
        if kpi_data.get('status'):
            status_label = QLabel(kpi_data['status'])
            status_label.setStyleSheet(f"background: {status_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 10px;")
            details_layout.addWidget(status_label)
        
        details_layout.addStretch()
        
        if kpi_data.get('target'):
            target_label = QLabel(f"Target: {kpi_data['target']}")
            target_label.setStyleSheet("font-size: 10px; color: #6c757d;")
            details_layout.addWidget(target_label)
        
        card_layout.addLayout(details_layout)
        
        return card
    
    def load_analytics(self):
        """Load all analytics data including new features"""
        try:
            self.statusBar().showMessage('🔄 Loading analytics...')
            
            # Initialize dashboard
            self.dashboard = QueueAnalyticsDashboard(self.db_path)
            
            # Load all analytics
            self.load_kpis()
            self.load_trends()
            self.load_strategy_analysis()
            self.load_littles_law_analysis()     # NEW
            self.load_wellbeing_analysis()       # NEW
            self.load_advanced_insights()        # NEW
            
            self.statusBar().showMessage('✅ Analytics loaded successfully')
            
        except Exception as e:
            self.statusBar().showMessage(f'❌ Error loading analytics: {str(e)}')
            QMessageBox.warning(self, 'Error', f'Failed to load analytics:\n{str(e)}')
    
    def load_kpis(self):
        """Load and display enhanced KPI cards"""
        # Clear existing KPIs
        for i in reversed(range(self.kpi_grid.count())): 
            widget = self.kpi_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Get enhanced KPI data
        kpis = self.dashboard.get_kpi_summary()
        
        # Create KPI cards
        row = 0
        col = 0
        for kpi_name, kpi_data in kpis.items():
            kpi_card = self.create_kpi_card(kpi_name, kpi_data)
            self.kpi_grid.addWidget(kpi_card, row, col)
            
            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1
    
    def load_trends(self):
        """Load performance trends charts"""
        try:
            # Performance trends
            fig = self.dashboard.plot_performance_trends()
            html_file = os.path.join(self.temp_dir, 'trends.html')
            fig.write_html(html_file)
            self.trends_view.setUrl(QUrl.fromLocalFile(html_file))
            
            # Hourly demand heatmap
            fig = self.dashboard.plot_hourly_heatmap()
            html_file = os.path.join(self.temp_dir, 'demand.html')
            fig.write_html(html_file)
            self.demand_view.setUrl(QUrl.fromLocalFile(html_file))
            
        except Exception as e:
            print(f"Error loading trends: {e}")
    
    def load_strategy_analysis(self):
        """Load strategy comparison analysis"""
        try:
            fig = self.dashboard.plot_strategy_comparison()
            html_file = os.path.join(self.temp_dir, 'strategy.html')
            fig.write_html(html_file)
            self.strategy_view.setUrl(QUrl.fromLocalFile(html_file))
            
        except Exception as e:
            print(f"Error loading strategy analysis: {e}")
    
    def load_littles_law_analysis(self):
        """Load Little's Law verification analysis (NEW)"""
        try:
            verification = self.dashboard.verify_littles_law()
            
            # Update results label
            if verification['status'] in ['NO_DATA', 'ERROR']:
                self.littles_results_label.setText(f"⚠️ {verification['message']}")
                self.littles_results_label.setStyleSheet("""
                    background: #f8d7da; border: 1px solid #f5c6cb; 
                    border-radius: 6px; padding: 15px; font-size: 14px;
                """)
            else:
                status_emoji = {'EXCELLENT': '🎯', 'GOOD': '✅', 'ACCEPTABLE': '⚠️', 'POOR': '❌'}
                emoji = status_emoji.get(verification['status'], '📊')
                
                self.littles_results_label.setText(f"""
                {emoji} <b>Little's Law Verification: {verification['status']}</b><br>
                📊 Average Error: {verification['avg_error_percentage']:.2f}%<br>
                🏆 Most Accurate Strategy: {verification['best_strategy']}<br>
                📈 Data Correlation: {verification['summary']['correlation']:.3f}<br>
                📋 Simulations Analyzed: {verification['summary']['total_simulations']}
                """)
            
            # Generate and load visualization
            fig = self.dashboard.plot_littles_law_verification()
            html_path = os.path.join(self.temp_dir, 'littles_law.html')
            fig.write_html(html_path)
            self.littles_view.load(QUrl.fromLocalFile(html_path))
            
        except Exception as e:
            self.littles_results_label.setText(f"❌ Error loading Little's Law analysis: {str(e)}")
    
    def load_wellbeing_analysis(self):
        """Load wellbeing metrics analysis (NEW)"""
        try:
            wellbeing = self.dashboard.calculate_wellbeing_metrics()
            
            if wellbeing['status'] in ['NO_DATA', 'ERROR']:
                self.wellbeing_summary_label.setText(f"⚠️ {wellbeing['message']}")
                return
            
            # Update summary
            status_emoji = {'EXCELLENT': '🌟', 'GOOD': '👍', 'MODERATE': '⚠️', 'POOR': '🚨'}
            emoji = status_emoji.get(wellbeing['status'], '📊')
            
            self.wellbeing_summary_label.setText(f"""
            {emoji} <b>System Wellbeing: {wellbeing['status']}</b><br>
            📊 Wellbeing Index: {wellbeing['metrics']['avg_wellbeing_index']:.1f}/100<br>
            🏆 Best Overall Strategy: {wellbeing['metrics']['best_strategy_overall']}<br>
            👥 Best for Customers: {wellbeing['metrics']['best_for_customers']}<br>
            🧑‍💼 Best for Staff: {wellbeing['metrics']['best_for_staff']}<br>
            🔗 Customer-Staff Correlation: {wellbeing['metrics']['customer_staff_correlation']:.3f}
            """)
            
            # Update recommendations
            for i in reversed(range(self.recommendations_layout.count())):
                widget = self.recommendations_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            for rec in wellbeing['recommendations']:
                rec_label = QLabel(f"💡 {rec}")
                rec_label.setStyleSheet("""
                    background: #e8f5e8; border: 1px solid #c3e6cb; 
                    border-radius: 4px; padding: 8px; margin: 2px;
                """)
                rec_label.setWordWrap(True)
                self.recommendations_layout.addWidget(rec_label)
            
            # Generate visualization
            fig = self.dashboard.plot_wellbeing_analysis()
            html_path = os.path.join(self.temp_dir, 'wellbeing.html')
            fig.write_html(html_path)
            self.wellbeing_view.load(QUrl.fromLocalFile(html_path))
            
        except Exception as e:
            self.wellbeing_summary_label.setText(f"❌ Error loading wellbeing analysis: {str(e)}")
    
    def load_advanced_insights(self):
        """Load advanced insights analytics (NEW)"""
        try:
            # Load performance summary
            kpis = self.dashboard.get_kpi_summary()
            
            summary_text = """
            <b>📊 System Performance Overview:</b><br>
            """
            
            if 'average_wait_time' in kpis:
                summary_text += f"⏱️ Average Wait Time: {kpis['average_wait_time']['value']} {kpis['average_wait_time']['unit']}<br>"
            
            if 'server_utilization' in kpis:
                summary_text += f"⚙️ Server Utilization: {kpis['server_utilization']['value']} {kpis['server_utilization']['unit']}<br>"
            
            if 'littles_law_verification' in kpis:
                summary_text += f"📐 Little's Law Error: {kpis['littles_law_verification']['value']}<br>"
            
            if 'system_wellbeing_index' in kpis:
                summary_text += f"💚 Wellbeing Index: {kpis['system_wellbeing_index']['value']}/100<br>"
            
            summary_text += "<br><i>These metrics demonstrate the system's effectiveness across multiple dimensions.</i>"
            
            self.performance_summary_label.setText(summary_text)
            
            # Load additional charts
            fig = self.dashboard.plot_utilization_vs_wait()
            html_file = os.path.join(self.temp_dir, 'utilization.html')
            fig.write_html(html_file)
            self.util_view.setUrl(QUrl.fromLocalFile(html_file))
            
            fig = self.dashboard.plot_wait_time_histogram()
            html_file = os.path.join(self.temp_dir, 'waittime.html')
            fig.write_html(html_file)
            self.wait_view.setUrl(QUrl.fromLocalFile(html_file))
            
        except Exception as e:
            self.performance_summary_label.setText(f"❌ Error loading advanced insights: {str(e)}")
    
    def export_analytics(self):
        """Export analytics report including new features"""
        try:
            self.statusBar().showMessage('📊 Exporting analytics report...')
            
            output_dir = 'analytics_export'
            self.dashboard.export_all_analytics(output_dir)
            
            QMessageBox.information(
                self,
                'Export Complete',
                f'Analytics exported to: {output_dir}/\n\n' +
                'Files generated:\n' +
                '• performance_trends.html\n' +
                '• strategy_comparison.html\n' +
                '• littles_law_verification.html\n' +
                '• wellbeing_analysis.html\n' +
                '• enhanced_summary_report.html\n\n' +
                'Open enhanced_summary_report.html to view the complete analysis.'
            )
            
            self.statusBar().showMessage('✅ Analytics export complete')
            
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to export analytics:\n{str(e)}')
            self.statusBar().showMessage('❌ Export failed')
    
    def closeEvent(self, event):
        """Clean up when window is closed"""
        if self.dashboard:
            self.dashboard.close()
        
        # Clean up temp files
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        
        super().closeEvent(event)


# ==================== INTEGRATION HELPER ====================
def add_analytics_to_main_ui(main_window):
    """
    Function to add analytics button to existing main UI
    Call this from your mainGui.py to integrate the analytics
    """
    
    # Add analytics button to toolbar/menu
    if hasattr(main_window, 'toolbar'):
        analytics_btn = QPushButton('📊 Analytics Dashboard')
        analytics_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%);
            }
        """)
        analytics_btn.clicked.connect(lambda: open_analytics_window(main_window))
        main_window.toolbar.addWidget(analytics_btn)


def open_analytics_window(parent, db_path='queue_analysis.db'):
    """Open the analytics window"""
    analytics_window = AnalyticsWindow(db_path, parent)
    analytics_window.show()
    return analytics_window


def export_analytics_quick(parent, db_path='queue_analysis.db'):
    """Quick export analytics without opening window"""
    try:
        dashboard = QueueAnalyticsDashboard(db_path)
        dashboard.export_all_analytics('analytics_output')
        dashboard.close()
        
        QMessageBox.information(
            parent,
            'Export Complete',
            'Analytics exported to: analytics_output/\n\nOpen enhanced_summary_report.html to view.'
        )
    except Exception as e:
        QMessageBox.critical(parent, 'Export Error', f'Failed to export:\n{str(e)}')


# ==================== STANDALONE EXECUTION ====================
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Open analytics window directly
    window = AnalyticsWindow('queue_analysis.db')
    window.show()
    
    sys.exit(app.exec_())
