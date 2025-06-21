#!/usr/bin/env python3
"""
Kafka Producer - Data Generator
Generates sample data and sends it to Kafka topics
"""

import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataGenerator:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """Initialize the data generator with Kafka producer"""
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Sample data templates
        self.user_ids = [f"user_{i:03d}" for i in range(1, 101)]
        self.product_ids = [f"prod_{i:03d}" for i in range(1, 51)]
        self.categories = ['electronics', 'clothing', 'books', 'home', 'sports']
        self.payment_methods = ['credit_card', 'debit_card', 'paypal', 'cash']
        
    def generate_user_activity(self):
        """Generate user activity data"""
        user_id = random.choice(self.user_ids)
        activity_type = random.choice(['login', 'logout', 'page_view', 'search', 'purchase'])
        
        data = {
            'user_id': user_id,
            'activity_type': activity_type,
            'timestamp': datetime.now().isoformat(),
            'session_id': f"session_{random.randint(1000, 9999)}",
            'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if activity_type == 'page_view':
            data['page_url'] = f"/products/{random.choice(self.product_ids)}"
        elif activity_type == 'search':
            data['search_query'] = random.choice(['laptop', 'phone', 'shoes', 'book', 'headphones'])
        elif activity_type == 'purchase':
            data['product_id'] = random.choice(self.product_ids)
            data['amount'] = round(random.uniform(10.0, 500.0), 2)
            
        return data
    
    def generate_sales_data(self):
        """Generate sales transaction data"""
        data = {
            'transaction_id': f"txn_{random.randint(100000, 999999)}",
            'user_id': random.choice(self.user_ids),
            'product_id': random.choice(self.product_ids),
            'quantity': random.randint(1, 5),
            'unit_price': round(random.uniform(10.0, 200.0), 2),
            'total_amount': 0,
            'payment_method': random.choice(self.payment_methods),
            'timestamp': datetime.now().isoformat(),
            'store_id': f"store_{random.randint(1, 10)}",
            'category': random.choice(self.categories)
        }
        
        data['total_amount'] = round(data['quantity'] * data['unit_price'], 2)
        return data
    
    def generate_inventory_data(self):
        """Generate inventory update data"""
        data = {
            'product_id': random.choice(self.product_ids),
            'current_stock': random.randint(0, 100),
            'reorder_level': random.randint(5, 20),
            'last_updated': datetime.now().isoformat(),
            'warehouse_id': f"warehouse_{random.randint(1, 5)}",
            'category': random.choice(self.categories)
        }
        
        # Add stock status
        if data['current_stock'] <= data['reorder_level']:
            data['status'] = 'low_stock'
        elif data['current_stock'] == 0:
            data['status'] = 'out_of_stock'
        else:
            data['status'] = 'in_stock'
            
        return data
    
    def send_to_kafka(self, topic, data, key=None):
        """Send data to Kafka topic"""
        try:
            future = self.producer.send(topic, value=data, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to {topic} [partition: {record_metadata.partition}, offset: {record_metadata.offset}]")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False
    
    def run(self, duration_minutes=5, interval_seconds=1):
        """Run the data generator for specified duration"""
        logger.info(f"Starting data generator for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Generate and send user activity data
                user_activity = self.generate_user_activity()
                self.send_to_kafka('user_activity', user_activity, key=user_activity['user_id'])
                
                # Generate and send sales data (less frequent)
                if random.random() < 0.3:  # 30% chance
                    sales_data = self.generate_sales_data()
                    self.send_to_kafka('sales', sales_data, key=sales_data['transaction_id'])
                
                # Generate and send inventory data (even less frequent)
                if random.random() < 0.1:  # 10% chance
                    inventory_data = self.generate_inventory_data()
                    self.send_to_kafka('inventory', inventory_data, key=inventory_data['product_id'])
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Data generation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in data generation: {e}")
                time.sleep(interval_seconds)
        
        self.producer.flush()
        self.producer.close()
        logger.info("Data generation completed")

def main():
    """Main function to run the data generator"""
    generator = DataGenerator()
    
    # Run for 5 minutes by default, sending data every second
    generator.run(duration_minutes=5, interval_seconds=1)

if __name__ == "__main__":
    main() 