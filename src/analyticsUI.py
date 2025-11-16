"""
PyQt5 Analytics Window
Embeds the analytics dashboard into the main queue management UI
Can be opened from the main window with a button/menu action
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QTextEdit,
                             QScrollArea, QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QFont
import os
import tempfile
from analyticsDashboard import QueueAnalyticsDashboard


class AnalyticsWindow(QMainWindow):
    """
    Analytics Dashboard Window for Queue Management System
    Displays interactive charts and KPIs in a PyQt5 window
    """
    
    def __init__(self, db_path='queue_analysis.db', parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.dashboard = None
        self.temp_dir = tempfile.mkdtemp()
        
        self.init_ui()
        self.load_analytics()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Queue Analytics Dashboard')
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget for different analytics views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #667eea;
                color: white;
            }
        """)
        
        # Create tabs
        self.create_kpi_tab()
        self.create_trends_tab()
        self.create_demand_tab()
        self.create_strategy_tab()
        self.create_utilization_tab()
        self.create_waittime_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Footer with action buttons
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        # Status bar
        self.statusBar().showMessage('Ready to load analytics')
    
    def create_header(self):
        """Create header section with title and refresh button"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #667eea, stop:1 #764ba2);
            color: white;
            border-radius: 8px;
            padding: 10px;
        """)
        
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = QLabel('📊 Queue Management Analytics Dashboard')
        title_font = QFont('Arial', 18, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton('🔄 Refresh Data')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: white;
                color: #667eea;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        refresh_btn.clicked.connect(self.load_analytics)
        header_layout.addWidget(refresh_btn)
        
        return header_widget
    
    def create_footer(self):
        """Create footer with action buttons"""
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        
        # Export button
        export_btn = QPushButton('💾 Export All Analytics')
        export_btn.clicked.connect(self.export_analytics)
        footer_layout.addWidget(export_btn)
        
        # Open in browser button
        browser_btn = QPushButton('🌐 Open in Browser')
        browser_btn.clicked.connect(self.open_in_browser)
        footer_layout.addWidget(browser_btn)
        
        footer_layout.addStretch()
        
        # Close button
        close_btn = QPushButton('✖ Close')
        close_btn.clicked.connect(self.close)
        footer_layout.addWidget(close_btn)
        
        return footer_widget
    
    def create_kpi_tab(self):
        """Create KPI summary tab"""
        kpi_widget = QWidget()
        kpi_layout = QVBoxLayout(kpi_widget)
        
        # Title
        title = QLabel('Key Performance Indicators')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet('color: #667eea; margin: 10px;')
        kpi_layout.addWidget(title)
        
        # KPI Grid
        self.kpi_grid = QGridLayout()
        kpi_layout.addLayout(self.kpi_grid)
        
        kpi_layout.addStretch()
        
        self.tabs.addTab(kpi_widget, '📊 KPI Summary')
    
    def create_trends_tab(self):
        """Create performance trends tab with embedded chart"""
        trends_widget = QWidget()
        trends_layout = QVBoxLayout(trends_widget)
        
        # Web view for Plotly chart
        self.trends_view = QWebEngineView()
        trends_layout.addWidget(self.trends_view)
        
        self.tabs.addTab(trends_widget, '📈 Performance Trends')
    
    def create_demand_tab(self):
        """Create hourly demand heatmap tab"""
        demand_widget = QWidget()
        demand_layout = QVBoxLayout(demand_widget)
        
        self.demand_view = QWebEngineView()
        demand_layout.addWidget(self.demand_view)
        
        self.tabs.addTab(demand_widget, '🔥 Hourly Demand')
    
    def create_strategy_tab(self):
        """Create strategy comparison tab"""
        strategy_widget = QWidget()
        strategy_layout = QVBoxLayout(strategy_widget)
        
        self.strategy_view = QWebEngineView()
        strategy_layout.addWidget(self.strategy_view)
        
        self.tabs.addTab(strategy_widget, '⚖️ Strategy Comparison')
    
    def create_utilization_tab(self):
        """Create server utilization analysis tab"""
        util_widget = QWidget()
        util_layout = QVBoxLayout(util_widget)
        
        self.util_view = QWebEngineView()
        util_layout.addWidget(self.util_view)
        
        self.tabs.addTab(util_widget, '⚙️ Server Utilization')
    
    def create_waittime_tab(self):
        """Create wait time distribution tab"""
        wait_widget = QWidget()
        wait_layout = QVBoxLayout(wait_widget)
        
        self.wait_view = QWebEngineView()
        wait_layout.addWidget(self.wait_view)
        
        self.tabs.addTab(wait_widget, '⏱️ Wait Times')
    
    def load_analytics(self):
        """Load analytics data from database and display"""
        try:
            self.statusBar().showMessage('Loading analytics data...')
            
            # Initialize dashboard
            self.dashboard = QueueAnalyticsDashboard(self.db_path)
            
            # Load KPIs
            self.load_kpis()
            
            # Generate and load charts
            self.load_charts()
            
            self.statusBar().showMessage('Analytics loaded successfully ✓')
            
        except Exception as e:
            self.statusBar().showMessage(f'Error loading analytics: {str(e)}')
            QMessageBox.warning(self, 'Error', f'Failed to load analytics:\n{str(e)}')
    
    def load_kpis(self):
        """Load and display KPI cards"""
        # Clear existing KPIs
        for i in reversed(range(self.kpi_grid.count())): 
            self.kpi_grid.itemAt(i).widget().setParent(None)
        
        # Get KPI data
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
    
    def create_kpi_card(self, name, data):
        """Create a single KPI card widget"""
        card = QGroupBox()
        
        # Style based on status
        status = data.get('status', '')
        color_map = {
            'EXCELLENT': '#48bb78',
            'OPTIMAL': '#48bb78',
            'GOOD': '#4299e1',
            'MONITOR': '#ed8936',
            'WARNING': '#f56565',
            'CRITICAL': '#c53030'
        }
        color = color_map.get(status, '#667eea')
        
        card.setStyleSheet(f"""
            QGroupBox {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 {color}, stop:1 {color}dd);
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # KPI Name
        name_label = QLabel(name.replace('_', ' ').title())
        name_label.setFont(QFont('Arial', 12, QFont.Bold))
        name_label.setStyleSheet('color: white;')
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # KPI Value
        value_label = QLabel(f"{data['value']}{data.get('unit', '')}")
        value_label.setFont(QFont('Arial', 32, QFont.Bold))
        value_label.setStyleSheet('color: white;')
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Target (if exists)
        if 'target' in data:
            target_label = QLabel(f"Target: {data['target']}")
            target_label.setFont(QFont('Arial', 10))
            target_label.setStyleSheet('color: white;')
            target_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(target_label)
        
        # Status
        if status:
            status_label = QLabel(status)
            status_label.setFont(QFont('Arial', 11, QFont.Bold))
            status_label.setStyleSheet('color: white; background: rgba(0,0,0,0.2); padding: 5px; border-radius: 5px;')
            status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(status_label)
        
        card.setMinimumHeight(180)
        return card
    
    def load_charts(self):
        """Generate and load all charts"""
        try:
            # Performance Trends
            fig = self.dashboard.plot_performance_trends()
            html_file = os.path.join(self.temp_dir, 'trends.html')
            fig.write_html(html_file)
            self.trends_view.setUrl(QUrl.fromLocalFile(html_file))
            
            # Hourly Demand
            fig = self.dashboard.plot_hourly_heatmap()
            html_file = os.path.join(self.temp_dir, 'demand.html')
            fig.write_html(html_file)
            self.demand_view.setUrl(QUrl.fromLocalFile(html_file))
            
            # Strategy Comparison
            fig = self.dashboard.plot_strategy_comparison()
            html_file = os.path.join(self.temp_dir, 'strategy.html')
            fig.write_html(html_file)
            self.strategy_view.setUrl(QUrl.fromLocalFile(html_file))
            
            # Server Utilization
            fig = self.dashboard.plot_utilization_vs_wait()
            html_file = os.path.join(self.temp_dir, 'utilization.html')
            fig.write_html(html_file)
            self.util_view.setUrl(QUrl.fromLocalFile(html_file))
            
            # Wait Time Distribution
            fig = self.dashboard.plot_wait_time_histogram()
            html_file = os.path.join(self.temp_dir, 'waittime.html')
            fig.write_html(html_file)
            self.wait_view.setUrl(QUrl.fromLocalFile(html_file))
            
        except Exception as e:
            print(f"Error loading charts: {e}")
    
    def export_analytics(self):
        """Export all analytics to permanent files"""
        try:
            self.dashboard.export_all_analytics('analytics_output')
            QMessageBox.information(
                self, 
                'Export Complete',
                'Analytics exported successfully!\n\nLocation: analytics_output/\n\nOpen master_dashboard.html to view all analytics.'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to export:\n{str(e)}')
    
    def open_in_browser(self):
        """Open master dashboard in web browser"""
        try:
            import webbrowser
            dashboard_path = os.path.join(self.temp_dir, 'dashboard.html')
            
            # Generate master dashboard
            self.dashboard.export_all_analytics(self.temp_dir)
            webbrowser.open(f'file://{dashboard_path}')
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open browser:\n{str(e)}')
    
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
        
        event.accept()


# ==================== INTEGRATION WITH MAIN UI ====================

def add_analytics_to_main_ui(main_window):
    """
    Function to add analytics button/menu to existing main UI
    
    Usage in your main.py:
        from analytics_ui import add_analytics_to_main_ui
        add_analytics_to_main_ui(self)  # 'self' is your main window
    """
    
    # Option 1: Add to menu bar
    if hasattr(main_window, 'menuBar'):
        analytics_menu = main_window.menuBar().addMenu('Analytics')
        
        open_dashboard_action = analytics_menu.addAction('📊 Open Analytics Dashboard')
        open_dashboard_action.triggered.connect(lambda: open_analytics_window(main_window))
        
        export_action = analytics_menu.addAction('💾 Export Analytics Report')
        export_action.triggered.connect(lambda: export_analytics_quick(main_window))
    
    # Option 2: Add button to toolbar/layout
    if hasattr(main_window, 'toolbar'):
        analytics_btn = QPushButton('📊 Analytics')
        analytics_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #764ba2;
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
            'Analytics exported to: analytics_output/\n\nOpen master_dashboard.html to view.'
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