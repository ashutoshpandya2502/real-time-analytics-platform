#!/usr/bin/env python3
"""
Streamlit Dashboard - Real-time Data Visualization
Dashboard for monitoring Kafka pipeline data and metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import json

# Page configuration
st.set_page_config(
    page_title="Kafka Data Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class Dashboard:
    def __init__(self, mongo_uri='mongodb://localhost:27017/'):
        """Initialize dashboard with MongoDB connection"""
        self.mongo_uri = mongo_uri
        self.client = MongoClient(mongo_uri)
        self.db = self.client['kafka_pipeline']
        
    def get_recent_data(self, collection_name, minutes=60):
        """Get recent data from MongoDB collection"""
        try:
            collection = self.db[collection_name]
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            if collection_name == 'raw_data':
                cursor = collection.find({
                    'timestamp': {'$gte': cutoff_time}
                }).sort('timestamp', -1)
            else:
                cursor = collection.find({
                    'timestamp': {'$gte': cutoff_time}
                }).sort('timestamp', -1)
                
            return list(cursor)
        except Exception as e:
            st.error(f"Error fetching data from {collection_name}: {e}")
            return []
    
    def create_user_activity_chart(self, data):
        """Create user activity visualization"""
        if not data:
            return None
            
        # Extract user activity data
        activity_data = []
        for doc in data:
            if doc.get('topic') == 'user_activity':
                activity = doc['data']['activity_type']
                activity_data.append(activity)
        
        if not activity_data:
            return None
            
        # Count activities
        activity_counts = pd.Series(activity_data).value_counts()
        
        # Create pie chart
        fig = px.pie(
            values=activity_counts.values,
            names=activity_counts.index,
            title="User Activity Distribution (Last Hour)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        return fig
    
    def create_sales_chart(self, data):
        """Create sales visualization"""
        if not data:
            return None
            
        # Extract sales data
        sales_data = []
        for doc in data:
            if doc.get('topic') == 'sales':
                sales_data.append({
                    'timestamp': doc['data']['timestamp'],
                    'amount': doc['data']['total_amount'],
                    'category': doc['data']['category']
                })
        
        if not sales_data:
            return None
            
        df = pd.DataFrame(sales_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sales by category
        fig = px.bar(
            df.groupby('category')['amount'].sum().reset_index(),
            x='category',
            y='amount',
            title="Sales by Category (Last Hour)",
            color='category',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        return fig
    
    def create_sales_timeline(self, data):
        """Create sales timeline chart"""
        if not data:
            return None
            
        # Extract sales data
        sales_data = []
        for doc in data:
            if doc.get('topic') == 'sales':
                sales_data.append({
                    'timestamp': doc['data']['timestamp'],
                    'amount': doc['data']['total_amount']
                })
        
        if not sales_data:
            return None
            
        df = pd.DataFrame(sales_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Group by minute for timeline
        df['minute'] = df['timestamp'].dt.floor('min')
        timeline_data = df.groupby('minute')['amount'].sum().reset_index()
        
        fig = px.line(
            timeline_data,
            x='minute',
            y='amount',
            title="Sales Timeline (Last Hour)",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Sales Amount ($)"
        )
        
        return fig
    
    def create_inventory_alerts(self, data):
        """Create inventory alerts visualization"""
        if not data:
            return None
            
        # Extract inventory data
        inventory_data = []
        for doc in data:
            if doc.get('topic') == 'inventory':
                inventory_data.append({
                    'product_id': doc['data']['product_id'],
                    'status': doc['data']['status'],
                    'current_stock': doc['data']['current_stock'],
                    'warehouse_id': doc['data']['warehouse_id']
                })
        
        if not inventory_data:
            return None
            
        df = pd.DataFrame(inventory_data)
        
        # Filter for alerts only
        alerts_df = df[df['status'].isin(['low_stock', 'out_of_stock'])]
        
        if alerts_df.empty:
            return None
            
        fig = px.scatter(
            alerts_df,
            x='product_id',
            y='current_stock',
            color='status',
            size='current_stock',
            hover_data=['warehouse_id'],
            title="Inventory Alerts (Last Hour)",
            color_discrete_map={
                'low_stock': 'orange',
                'out_of_stock': 'red'
            }
        )
        
        return fig
    
    def display_metrics(self, data):
        """Display key metrics"""
        if not data:
            return
            
        # Calculate metrics
        total_messages = len(data)
        user_activities = len([d for d in data if d.get('topic') == 'user_activity'])
        sales = len([d for d in data if d.get('topic') == 'sales'])
        inventory_updates = len([d for d in data if d.get('topic') == 'inventory'])
        
        # Calculate total sales
        total_sales = 0
        for doc in data:
            if doc.get('topic') == 'sales':
                total_sales += doc['data']['total_amount']
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Messages", total_messages)
        
        with col2:
            st.metric("User Activities", user_activities)
        
        with col3:
            st.metric("Sales Transactions", sales)
        
        with col4:
            st.metric("Inventory Updates", inventory_updates)
        
        with col5:
            st.metric("Total Sales ($)", f"${total_sales:,.2f}")
    
    def run(self):
        """Run the dashboard"""
        st.title("📊 Kafka Data Pipeline Dashboard")
        st.markdown("Real-time monitoring of data pipeline metrics and analytics")
        
        # Sidebar
        st.sidebar.header("Dashboard Controls")
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)
        
        if st.sidebar.button("Refresh Now"):
            st.rerun()
        
        # Main content
        try:
            # Get recent data
            raw_data = self.get_recent_data('raw_data', minutes=60)
            
            # Display metrics
            st.header("📈 Key Metrics (Last Hour)")
            self.display_metrics(raw_data)
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 User Activity")
                activity_chart = self.create_user_activity_chart(raw_data)
                if activity_chart:
                    st.plotly_chart(activity_chart, use_container_width=True)
                else:
                    st.info("No user activity data available")
                
                st.subheader("💰 Sales by Category")
                sales_chart = self.create_sales_chart(raw_data)
                if sales_chart:
                    st.plotly_chart(sales_chart, use_container_width=True)
                else:
                    st.info("No sales data available")
            
            with col2:
                st.subheader("📈 Sales Timeline")
                timeline_chart = self.create_sales_timeline(raw_data)
                if timeline_chart:
                    st.plotly_chart(timeline_chart, use_container_width=True)
                else:
                    st.info("No sales timeline data available")
                
                st.subheader("⚠️ Inventory Alerts")
                alerts_chart = self.create_inventory_alerts(raw_data)
                if alerts_chart:
                    st.plotly_chart(alerts_chart, use_container_width=True)
                else:
                    st.info("No inventory alerts available")
            
            # Recent data table
            st.header("📋 Recent Data")
            if raw_data:
                # Create a simplified table
                table_data = []
                for doc in raw_data[:20]:  # Show last 20 records
                    table_data.append({
                        'Topic': doc.get('topic', 'N/A'),
                        'Timestamp': doc.get('timestamp', 'N/A'),
                        'Key Info': self.extract_key_info(doc)
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent data available")
            
            # Auto-refresh
            time.sleep(refresh_interval)
            st.rerun()
            
        except Exception as e:
            st.error(f"Error running dashboard: {e}")
            st.info("Please ensure MongoDB is running and contains data")
    
    def extract_key_info(self, doc):
        """Extract key information from document for display"""
        try:
            data = doc.get('data', {})
            topic = doc.get('topic', '')
            
            if topic == 'user_activity':
                return f"User: {data.get('user_id', 'N/A')} - {data.get('activity_type', 'N/A')}"
            elif topic == 'sales':
                return f"Transaction: {data.get('transaction_id', 'N/A')} - ${data.get('total_amount', 0)}"
            elif topic == 'inventory':
                return f"Product: {data.get('product_id', 'N/A')} - {data.get('status', 'N/A')}"
            else:
                return "Unknown data type"
        except:
            return "Error extracting info"

def main():
    """Main function to run the dashboard"""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 