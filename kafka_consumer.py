#!/usr/bin/env python3
"""
Kafka Consumer - Data Processor
Consumes data from Kafka topics, performs aggregations, and writes to MongoDB
"""

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, kafka_servers=['localhost:9092'], mongo_uri='mongodb://localhost:27017/'):
        """Initialize the data processor"""
        self.kafka_servers = kafka_servers
        self.mongo_uri = mongo_uri
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            'user_activity', 'sales', 'inventory',
            bootstrap_servers=kafka_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            auto_offset_reset='earliest',
            group_id='data_processor_group'
        )
        
        # Initialize MongoDB connection
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['kafka_pipeline']
        
        # Collections
        self.raw_data_collection = self.db['raw_data']
        self.aggregated_data_collection = self.db['aggregated_data']
        self.real_time_metrics_collection = self.db['real_time_metrics']
        
        # In-memory aggregations (for real-time processing)
        self.user_activity_counts = defaultdict(int)
        self.sales_by_category = defaultdict(float)
        self.sales_by_hour = defaultdict(float)
        self.inventory_alerts = deque(maxlen=100)
        
        # Threading
        self.running = False
        self.aggregation_thread = None
        
    def process_user_activity(self, data):
        """Process user activity data"""
        try:
            # Store raw data
            data['processed_at'] = datetime.now().isoformat()
            self.raw_data_collection.insert_one({
                'topic': 'user_activity',
                'data': data,
                'timestamp': datetime.now()
            })
            
            # Update real-time metrics
            self.user_activity_counts[data['activity_type']] += 1
            
            # Log significant activities
            if data['activity_type'] == 'purchase':
                logger.info(f"Purchase detected: User {data['user_id']} spent ${data.get('amount', 0)}")
                
        except Exception as e:
            logger.error(f"Error processing user activity: {e}")
    
    def process_sales_data(self, data):
        """Process sales data"""
        try:
            # Store raw data
            data['processed_at'] = datetime.now().isoformat()
            self.raw_data_collection.insert_one({
                'topic': 'sales',
                'data': data,
                'timestamp': datetime.now()
            })
            
            # Update aggregations
            category = data['category']
            self.sales_by_category[category] += data['total_amount']
            
            # Sales by hour
            timestamp = datetime.fromisoformat(data['timestamp'])
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            self.sales_by_hour[hour_key] += data['total_amount']
            
            logger.info(f"Sales transaction: {data['transaction_id']} - ${data['total_amount']}")
            
        except Exception as e:
            logger.error(f"Error processing sales data: {e}")
    
    def process_inventory_data(self, data):
        """Process inventory data"""
        try:
            # Store raw data
            data['processed_at'] = datetime.now().isoformat()
            self.raw_data_collection.insert_one({
                'topic': 'inventory',
                'data': data,
                'timestamp': datetime.now()
            })
            
            # Check for inventory alerts
            if data['status'] in ['low_stock', 'out_of_stock']:
                alert = {
                    'product_id': data['product_id'],
                    'status': data['status'],
                    'current_stock': data['current_stock'],
                    'reorder_level': data['reorder_level'],
                    'timestamp': datetime.now().isoformat(),
                    'warehouse_id': data['warehouse_id']
                }
                self.inventory_alerts.append(alert)
                logger.warning(f"Inventory alert: {data['product_id']} - {data['status']}")
                
        except Exception as e:
            logger.error(f"Error processing inventory data: {e}")
    
    def store_aggregated_data(self):
        """Store aggregated data to MongoDB"""
        try:
            # Store user activity summary
            activity_summary = {
                'type': 'user_activity_summary',
                'timestamp': datetime.now(),
                'data': dict(self.user_activity_counts),
                'period': 'realtime'
            }
            self.aggregated_data_collection.insert_one(activity_summary)
            
            # Store sales summary
            sales_summary = {
                'type': 'sales_summary',
                'timestamp': datetime.now(),
                'data': {
                    'by_category': dict(self.sales_by_category),
                    'by_hour': dict(self.sales_by_hour)
                },
                'period': 'realtime'
            }
            self.aggregated_data_collection.insert_one(sales_summary)
            
            # Store inventory alerts
            if self.inventory_alerts:
                alerts_summary = {
                    'type': 'inventory_alerts',
                    'timestamp': datetime.now(),
                    'alerts': list(self.inventory_alerts),
                    'count': len(self.inventory_alerts)
                }
                self.aggregated_data_collection.insert_one(alerts_summary)
                
        except PyMongoError as e:
            logger.error(f"Error storing aggregated data: {e}")
    
    def run_aggregation_loop(self):
        """Run aggregation loop in separate thread"""
        while self.running:
            try:
                self.store_aggregated_data()
                time.sleep(30)  # Store aggregations every 30 seconds
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")
                time.sleep(30)
    
    def start(self):
        """Start the data processor"""
        logger.info("Starting Kafka consumer and data processor...")
        self.running = True
        
        # Start aggregation thread
        self.aggregation_thread = threading.Thread(target=self.run_aggregation_loop)
        self.aggregation_thread.start()
        
        try:
            for message in self.consumer:
                try:
                    topic = message.topic
                    data = message.value
                    key = message.key
                    
                    logger.info(f"Received message from {topic}: {key}")
                    
                    # Process based on topic
                    if topic == 'user_activity':
                        self.process_user_activity(data)
                    elif topic == 'sales':
                        self.process_sales_data(data)
                    elif topic == 'inventory':
                        self.process_inventory_data(data)
                    else:
                        logger.warning(f"Unknown topic: {topic}")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Stopping data processor...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the data processor"""
        self.running = False
        
        if self.aggregation_thread:
            self.aggregation_thread.join()
        
        self.consumer.close()
        self.mongo_client.close()
        logger.info("Data processor stopped")

def main():
    """Main function to run the data processor"""
    processor = DataProcessor()
    processor.start()

if __name__ == "__main__":
    main()
