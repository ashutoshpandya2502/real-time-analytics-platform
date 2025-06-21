# Kafka Data Pipeline Solution

A real-time data pipeline solution using Apache Kafka, MongoDB, and Streamlit for data ingestion, processing, aggregation, and visualization.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Generator│    │   Kafka Cluster │    │  Data Processor │    │   MongoDB       │
│   (Producer)    │───▶│   (Broker)      │───▶│   (Consumer)    │───▶│   (NoSQL DB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                                              │
                                │                                              │
                                ▼                                              ▼
                       ┌─────────────────┐                          ┌─────────────────┐
                       │   Streamlit     │                          │   Real-time     │
                       │   Dashboard     │                          │   Aggregations  │
                       └─────────────────┘                          └─────────────────┘
```

### Components:

1. **Data Generator (`data_generator.py`)**: Kafka producer that generates sample data
2. **Data Processor (`kafka_consumer.py`)**: Kafka consumer with real-time aggregation
3. **Dashboard (`dashboard.py`)**: Streamlit web application for visualization
4. **MongoDB**: NoSQL database for storing raw data and aggregations

## 🎯 Design Decisions

### Why MongoDB?

1. **Schema Flexibility**: MongoDB's document-based structure allows storing different data types without predefined schemas
2. **Real-time Analytics**: Excellent performance for real-time aggregations and queries
3. **Scalability**: Horizontal scaling capabilities for handling large data volumes
4. **JSON Native**: Natural fit for JSON data from Kafka
5. **Aggregation Pipeline**: Powerful aggregation framework for complex analytics

### Alternative Considerations:

- **PostgreSQL**: Would require predefined schemas and migrations
- **Redis**: Limited persistence and complex data structures
- **Elasticsearch**: Overkill for this use case, better for search-heavy applications

### Kafka Topics:

- `user_activity`: User interactions (login, logout, page views, searches, purchases)
- `sales`: Sales transaction data
- `inventory`: Inventory updates and stock levels

## 📊 Data Schema

### User Activity Data
```json
{
  "user_id": "user_001",
  "activity_type": "purchase",
  "timestamp": "2024-01-15T10:30:00",
  "session_id": "session_1234",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "product_id": "prod_001",
  "amount": 149.99
}
```

### Sales Data
```json
{
  "transaction_id": "txn_123456",
  "user_id": "user_001",
  "product_id": "prod_001",
  "quantity": 2,
  "unit_price": 74.99,
  "total_amount": 149.98,
  "payment_method": "credit_card",
  "timestamp": "2024-01-15T10:30:00",
  "store_id": "store_01",
  "category": "electronics"
}
```

### Inventory Data
```json
{
  "product_id": "prod_001",
  "current_stock": 15,
  "reorder_level": 10,
  "last_updated": "2024-01-15T10:30:00",
  "warehouse_id": "warehouse_01",
  "category": "electronics",
  "status": "in_stock"
}
```

### MongoDB Collections:

1. **raw_data**: Stores all incoming data with metadata
2. **aggregated_data**: Stores real-time aggregations
3. **real_time_metrics**: Stores current metrics and alerts

## 🚀 Run Instructions

### Prerequisites

1. **Python 3.8+**
2. **Apache Kafka** (local or cloud)
3. **MongoDB** (local or cloud)
4. **Java 8+** (for Kafka)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd kafka-data-pipeline
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🪟 Windows 11 Specific Setup

### 1. Install Java 8+
- Download from: https://adoptium.net/
- Choose "Eclipse Temurin" 
- Select Windows x64
- Run the installer

### 2. Install MongoDB for Windows
```bash
# Option 1: Download from MongoDB website
# Go to: https://www.mongodb.com/try/download/community
# Download "Windows x64" version and run installer

# Option 2: Using Chocolatey (if installed)
choco install mongodb

# Option 3: Using winget
winget install MongoDB.Server
```

### 3. Start MongoDB Service
```bash
# Start MongoDB service
net start MongoDB

# Or start manually from MongoDB installation directory
"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe"
```

### 4. Install and Start Kafka

#### Option A: Using Docker (Recommended for Windows)
```bash
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop/

# Start Kafka using Docker Compose
docker-compose up -d

# This will start:
# - Zookeeper on port 2181
# - Kafka on port 9092
# - Kafka UI on port 8081
```

#### Option B: Using WSL2
```bash
# Install WSL2
wsl --install

# In WSL2 Ubuntu terminal:
sudo apt update
sudo apt install openjdk-8-jdk

# Download Kafka
wget https://downloads.apache.org/kafka/3.5.1/kafka_2.13-3.5.1.tgz
tar -xzf kafka_2.13-3.5.1.tgz
cd kafka_2.13-3.5.1

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Start Kafka
bin/kafka-server-start.sh config/server.properties &

# Create topics
bin/kafka-topics.sh --create --topic user_activity --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --topic sales --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --topic inventory --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 5. Running the Pipeline on Windows

#### Option 1: Use Windows Batch File (Easiest)
```bash
# Double-click or run:
start_pipeline_windows.bat
```

#### Option 2: Manual Start
```bash
# Terminal 1: Start consumer
python kafka_consumer.py

# Terminal 2: Start dashboard
streamlit run dashboard.py

# Terminal 3: Start data generator
python data_generator.py
```

#### Option 3: Use Python Startup Script
```bash
python start_pipeline.py
```

## 🐧 Linux/macOS Setup

### Install and start Kafka:
```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.5.1/kafka_2.13-3.5.1.tgz
tar -xzf kafka_2.13-3.5.1.tgz
cd kafka_2.13-3.5.1

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Start Kafka
bin/kafka-server-start.sh config/server.properties &

# Create topics
bin/kafka-topics.sh --create --topic user_activity --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --topic sales --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --topic inventory --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Install and start MongoDB:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# macOS
brew install mongodb-community
brew services start mongodb-community
```

### Access Points

- **Dashboard**: http://localhost:8501
- **Kafka**: localhost:9092
- **MongoDB**: localhost:27017
- **Kafka UI** (Docker): http://localhost:8081

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=data_processor_group

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=kafka_pipeline

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL=30
```

### Customization

1. **Data Generation**: Modify `data_generator.py` to change data patterns
2. **Processing Logic**: Update `kafka_consumer.py` for custom aggregations
3. **Visualizations**: Customize `dashboard.py` for different charts

## 📈 Features

### Real-time Processing
- Stream processing with Kafka
- In-memory aggregations
- Real-time alerts for inventory issues

### Data Visualization
- Interactive charts with Plotly
- Real-time metrics dashboard
- Historical data analysis

### Scalability
- Horizontal scaling with Kafka partitions
- MongoDB sharding support
- Microservices architecture ready

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Error:**
   - Ensure Kafka is running on localhost:9092
   - Check if topics are created
   - For Docker: `docker-compose ps` to check container status

2. **MongoDB Connection Error:**
   - Verify MongoDB is running on localhost:27017
   - Check authentication if enabled
   - Windows: Check if MongoDB service is started

3. **Dashboard Not Loading:**
   - Ensure all dependencies are installed
   - Check if MongoDB contains data
   - Windows: Check firewall settings

### Windows-Specific Issues

1. **Port Already in Use:**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :9092
   
   # Kill the process if needed
   taskkill /PID <PID> /F
   ```

2. **Docker Issues:**
   - Ensure Docker Desktop is running
   - Check WSL2 integration is enabled
   - Restart Docker Desktop if needed

3. **Python Path Issues:**
   - Ensure Python is in PATH
   - Use `python -m pip` instead of `pip` if needed

### Logs

- Check console output for detailed error messages
- MongoDB logs: Check MongoDB installation directory
- Kafka logs: Check Kafka installation directory or Docker logs
- Docker logs: `docker-compose logs`

## 📝 API Documentation

### Kafka Topics

| Topic | Description | Key | Value Schema |
|-------|-------------|-----|--------------|
| user_activity | User interactions | user_id | UserActivity |
| sales | Sales transactions | transaction_id | Sales |
| inventory | Inventory updates | product_id | Inventory |

### MongoDB Collections

| Collection | Purpose | Indexes |
|------------|---------|---------|
| raw_data | Raw incoming data | timestamp, topic |
| aggregated_data | Real-time aggregations | timestamp, type |
| real_time_metrics | Current metrics | timestamp |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details 