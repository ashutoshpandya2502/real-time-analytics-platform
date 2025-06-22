#!/usr/bin/env python3
"""
Real-Time Analytics Platform Startup Script
Helper script to start all components of the real-time analytics platform
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import kafka
        print("✅ kafka-python installed")
    except ImportError:
        print("❌ kafka-python not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import pymongo
        print("✅ pymongo installed")
    except ImportError:
        print("❌ pymongo not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import streamlit
        print("✅ streamlit installed")
    except ImportError:
        print("❌ streamlit not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import pandas
        print("✅ pandas installed")
    except ImportError:
        print("❌ pandas not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import plotly
        print("✅ plotly installed")
    except ImportError:
        print("❌ plotly not found. Run: pip install -r requirements.txt")
        return False
    
    return True

def check_services():
    """Check if Kafka and MongoDB are running"""
    print("\n🔍 Checking services...")
    
    # Check MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB is running")
        client.close()
    except Exception as e:
        print("❌ MongoDB is not running. Please start MongoDB first.")
        print("   Ubuntu/Debian: sudo systemctl start mongodb")
        print("   macOS: brew services start mongodb-community")
        print("   Windows: Start MongoDB service")
        return False
    
    # Check Kafka (basic check)
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'], request_timeout_ms=2000)
        producer.close()
        print("✅ Kafka is running")
    except Exception as e:
        print("❌ Kafka is not running. Please start Kafka first.")
        print("   Download Kafka and run:")
        print("   bin/zookeeper-server-start.sh config/zookeeper.properties &")
        print("   bin/kafka-server-start.sh config/server.properties &")
        return False
    
    return True

def start_consumer():
    """Start the Kafka consumer"""
    print("\n🚀 Starting Kafka consumer...")
    try:
        process = subprocess.Popen([sys.executable, 'kafka_consumer.py'])
        print(f"✅ Consumer started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Failed to start consumer: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("\n🚀 Starting Streamlit dashboard...")
    try:
        process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'dashboard.py'])
        print(f"✅ Dashboard started with PID: {process.pid}")
        print("📊 Dashboard will be available at: http://localhost:8501")
        return process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def start_producer():
    """Start the data generator"""
    print("\n🚀 Starting data generator...")
    try:
        process = subprocess.Popen([sys.executable, 'data_generator.py'])
        print(f"✅ Producer started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Failed to start producer: {e}")
        return None

def main():
    """Main function to start the platform"""
    print("🎯 Real-Time Analytics Platform Startup")
    print("=" * 45)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        sys.exit(1)
    
    # Check services
    if not check_services():
        print("\n❌ Please start required services first.")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting platform components...")
    
    # Start components
    processes = []
    
    # Start consumer first
    consumer_process = start_consumer()
    if consumer_process:
        processes.append(('Consumer', consumer_process))
        time.sleep(2)  # Give consumer time to start
    
    # Start dashboard
    dashboard_process = start_dashboard()
    if dashboard_process:
        processes.append(('Dashboard', dashboard_process))
        time.sleep(2)  # Give dashboard time to start
    
    # Start producer last
    producer_process = start_producer()
    if producer_process:
        processes.append(('Producer', producer_process))
    
    if not processes:
        print("\n❌ Failed to start any components.")
        sys.exit(1)
    
    print("\n🎉 Real-Time Analytics Platform started successfully!")
    print("\n📋 Running components:")
    for name, process in processes:
        print(f"   - {name}: PID {process.pid}")
    
    print("\n📊 Access points:")
    print("   - Dashboard: http://localhost:8501")
    print("   - Kafka: localhost:9092")
    print("   - MongoDB: localhost:27017")
    
    print("\n⏹️  Press Ctrl+C to stop all components...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n⚠️  {name} process has stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping platform components...")
        
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("\n👋 Platform stopped. Goodbye!")

if __name__ == "__main__":
    main() 