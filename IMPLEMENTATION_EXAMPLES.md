# Real-Time AWS Database - Implementation Code Examples

## 1. Connection Pooling Implementation

### Create `src/db_pool.py`
```python
"""
db_pool.py
Database connection pooling implementation
"""

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from config import AWS_RDS_CONFIG, USE_AWS

class DatabasePool:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_engine(cls, pool_size=10, max_overflow=20):
        """Get or create connection pool engine"""
        if cls._pool is None:
            engine_type = AWS_RDS_CONFIG.get("engine", "postgres")
            
            if engine_type == "postgres":
                url = f"postgresql://{AWS_RDS_CONFIG['user']}:{AWS_RDS_CONFIG['password']}@{AWS_RDS_CONFIG['host']}:{AWS_RDS_CONFIG['port']}/{AWS_RDS_CONFIG['database']}"
            else:
                url = f"mysql+pymysql://{AWS_RDS_CONFIG['user']}:{AWS_RDS_CONFIG['password']}@{AWS_RDS_CONFIG['host']}:{AWS_RDS_CONFIG['port']}/{AWS_RDS_CONFIG['database']}"
            
            cls._pool = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle after 1 hour
            )
        
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        engine = cls.get_engine()
        return engine.connect()
    
    @classmethod
    def close_pool(cls):
        """Close all connections in pool"""
        if cls._pool:
            cls._pool.dispose()
            cls._pool = None

# Usage:
# conn = DatabasePool().get_connection()
# result = conn.execute("SELECT .....")
# conn.close()
```

---

## 2. Async Operations Implementation

### Create `src/db_async.py`
```python
"""
db_async.py
Async database operations
"""

import asyncio
import asyncpg
from config import AWS_RDS_CONFIG
from typing import List, Dict, Any

class AsyncDatabasePool:
    _pool = None
    
    @classmethod
    async def init_pool(cls, min_size=10, max_size=20):
        """Initialize async connection pool"""
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                user=AWS_RDS_CONFIG['user'],
                password=AWS_RDS_CONFIG['password'],
                database=AWS_RDS_CONFIG['database'],
                host=AWS_RDS_CONFIG['host'],
                port=AWS_RDS_CONFIG['port'],
                min_size=min_size,
                max_size=max_size,
            )
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        """Close async pool"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
    
    @classmethod
    async def fetch_one(cls, query: str, *args) -> Dict[str, Any]:
        """Fetch single row"""
        pool = await cls.init_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    @classmethod
    async def fetch_all(cls, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        pool = await cls.init_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    @classmethod
    async def insert_metric(cls, resource_id: str, metric_name: str, 
                           metric_value: float, timestamp: str) -> None:
        """Insert metric asynchronously"""
        query = """
            INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
            VALUES ($1, $2, $3, $4)
        """
        pool = await cls.init_pool()
        async with pool.acquire() as conn:
            await conn.execute(query, resource_id, metric_name, metric_value, timestamp)
    
    @classmethod
    async def batch_insert_metrics(cls, metrics: List[Dict]) -> None:
        """Batch insert multiple metrics"""
        pool = await cls.init_pool()
        async with pool.acquire() as conn:
            # Use executemany for better performance
            await conn.executemany(
                """
                INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
                VALUES ($1, $2, $3, $4)
                """,
                [(m['resource_id'], m['metric_name'], m['metric_value'], m['timestamp']) 
                 for m in metrics]
            )

# Usage:
# async def collect_metrics():
#     metrics = [...]
#     await AsyncDatabasePool.batch_insert_metrics(metrics)
```

---

## 3. DynamoDB Implementation

### Create `src/dynamodb_utils.py`
```python
"""
dynamodb_utils.py
AWS DynamoDB operations
"""

import boto3
from typing import Dict, List, Any
from datetime import datetime
from config import AWS_REGION

class DynamoDBMetrics:
    def __init__(self, table_name: str = "CloudMetrics"):
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def create_table(self):
        """Create DynamoDB table with Streams enabled"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'resource_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'resource_id', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',  # On-demand pricing
                StreamSpecification={
                    'StreamViewType': 'NEW_AND_OLD_IMAGES',  # Enable Streams
                }
            )
            table.wait_until_exists()
            print(f"✅ DynamoDB table {self.table_name} created")
            return table
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            print(f"⚠️  Table {self.table_name} already exists")
            return self.table
    
    def put_metric(self, resource_id: str, metric_name: str, 
                   metric_value: float, timestamp: str = None):
        """Insert single metric"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        item = {
            'resource_id': resource_id,
            'timestamp': timestamp,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'ttl': int(datetime.utcnow().timestamp()) + 86400 * 30  # 30 days
        }
        
        self.table.put_item(Item=item)
        return item
    
    def batch_write_metrics(self, metrics: List[Dict[str, Any]]):
        """Batch write multiple metrics efficiently"""
        with self.table.batch_writer(
            batch_size=25,
            overwrite_by_pkeys=['resource_id', 'timestamp']
        ) as batch:
            for metric in metrics:
                if 'timestamp' not in metric:
                    metric['timestamp'] = datetime.utcnow().isoformat()
                
                batch.put_item(Item=metric)
    
    def get_metrics(self, resource_id: str, start_time: str, end_time: str):
        """Query metrics for resource in time range"""
        from boto3.dynamodb.conditions import Key, Attr
        
        response = self.table.query(
            KeyConditionExpression=Key('resource_id').eq(resource_id) &
                                   Key('timestamp').between(start_time, end_time)
        )
        
        return response.get('Items', [])
    
    def enable_ttl(self):
        """Enable TTL to auto-delete old metrics"""
        try:
            self.dynamodb.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    'AttributeName': 'ttl',
                    'Enabled': True
                }
            )
            print("✅ TTL enabled for old metrics")
        except Exception as e:
            print(f"⚠️  TTL error: {e}")

# Usage:
# db = DynamoDBMetrics()
# db.create_table()
# db.put_metric("res-001", "cpu", 42.5)
```

---

## 4. WebSocket Server Implementation

### Create `src/websocket_server.py`
```python
"""
websocket_server.py
WebSocket server for real-time metric updates
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Track connected clients
connected_clients = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✅ Client connected: {request.sid}")
    connected_clients[request.sid] = {'timestamp': datetime.now()}
    emit('response', {'message': 'Connected to metrics server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {request.sid}")
    if request.sid in connected_clients:
        del connected_clients[request.sid]

@socketio.on('subscribe_metrics')
def handle_subscribe(data):
    """Subscribe to metrics for specific resource"""
    resource_id = data.get('resource_id')
    room = f"metrics_{resource_id}"
    join_room(room)
    print(f"📊 Client subscribed to {resource_id}")
    emit('subscribed', {'resource_id': resource_id})

@socketio.on('unsubscribe_metrics')
def handle_unsubscribe(data):
    """Unsubscribe from metrics"""
    resource_id = data.get('resource_id')
    room = f"metrics_{resource_id}"
    leave_room(room)
    print(f"📊 Client unsubscribed from {resource_id}")

def broadcast_metric_update(resource_id: str, metric_data: dict):
    """Broadcast metric update to all subscribers"""
    room = f"metrics_{resource_id}"
    socketio.emit('metric_update', metric_data, room=room)
    print(f"📡 Broadcast to {room}: {metric_data}")

# Usage in metric collection:
# from websocket_server import broadcast_metric_update
# 
# def insert_metric(resource_id, metric_name, value, timestamp):
#     # Insert to database
#     db.insert(...)
#     # Broadcast to WebSocket clients
#     broadcast_metric_update(resource_id, {
#         'metric_name': metric_name,
#         'value': value,
#         'timestamp': timestamp
#     })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

---

## 5. DynamoDB Streams Consumer

### Create `src/dynamodb_streams.py`
```python
"""
dynamodb_streams.py
Consume DynamoDB Streams for real-time updates
"""

import boto3
import json
from typing import Callable
from websocket_server import broadcast_metric_update

class DynamoDBStreamsConsumer:
    def __init__(self, table_name: str, stream_view_type: str = "NEW_AND_OLD_IMAGES"):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.streams_client = boto3.client('dynamodbstreams')
        self.table_name = table_name
        self.stream_view_type = stream_view_type
    
    def get_stream_arn(self):
        """Get DynamoDB Stream ARN from table"""
        table_description = self.dynamodb.meta.client.describe_table(
            TableName=self.table_name
        )
        stream_arn = table_description['Table'].get('LatestStreamArn')
        return stream_arn
    
    def start_consuming(self):
        """Start consuming stream records"""
        stream_arn = self.get_stream_arn()
        if not stream_arn:
            print("❌ DynamoDB Stream not enabled for table")
            return
        
        # Get stream description
        response = self.streams_client.describe_stream(StreamArn=stream_arn)
        shards = response['StreamDescription']['Shards']
        
        print(f"📊 Starting to consume {len(shards)} shard(s)")
        
        for shard in shards:
            shard_id = shard['ShardId']
            self._consume_shard(stream_arn, shard_id)
    
    def _consume_shard(self, stream_arn: str, shard_id: str, iterator_type: str = "TRIM_HORIZON"):
        """Consume records from a specific shard"""
        # Get shard iterator
        response = self.streams_client.get_shard_iterator(
            StreamArn=stream_arn,
            ShardId=shard_id,
            ShardIteratorType=iterator_type  # TRIM_HORIZON = from start
        )
        
        iterator = response.get('ShardIterator')
        
        while iterator:
            try:
                # Get records
                response = self.streams_client.get_records(
                    ShardIterator=iterator,
                    Limit=100
                )
                
                for record in response['Records']:
                    self._handle_record(record)
                
                iterator = response.get('NextShardIterator')
                
            except Exception as e:
                print(f"❌ Error consuming shard: {e}")
                break
    
    def _handle_record(self, record: dict):
        """Handle individual stream record"""
        event_name = record['eventName']  # INSERT, MODIFY, DELETE
        dynamodb = record['dynamodb']
        
        if event_name == 'INSERT':
            self._handle_insert(dynamodb)
        elif event_name == 'MODIFY':
            self._handle_modify(dynamodb)
        elif event_name == 'DELETE':
            self._handle_delete(dynamodb)
    
    def _handle_insert(self, dynamodb_data: dict):
        """Handle INSERT event"""
        new_image = dynamodb_data.get('NewImage', {})
        
        # Convert DynamoDB format to regular dict
        metric = {
            'resource_id': new_image.get('resource_id', {}).get('S'),
            'metric_name': new_image.get('metric_name', {}).get('S'),
            'metric_value': float(new_image.get('metric_value', {}).get('N', 0)),
            'timestamp': new_image.get('timestamp', {}).get('S'),
        }
        
        # Broadcast to WebSocket clients
        broadcast_metric_update(metric['resource_id'], metric)
        print(f"✅ INSERT: {metric}")
    
    def _handle_modify(self, dynamodb_data: dict):
        """Handle MODIFY event"""
        new_image = dynamodb_data.get('NewImage', {})
        
        metric = {
            'resource_id': new_image.get('resource_id', {}).get('S'),
            'metric_name': new_image.get('metric_name', {}).get('S'),
            'metric_value': float(new_image.get('metric_value', {}).get('N', 0)),
            'timestamp': new_image.get('timestamp', {}).get('S'),
        }
        
        broadcast_metric_update(metric['resource_id'], metric)
        print(f"📝 MODIFY: {metric}")
    
    def _handle_delete(self, dynamodb_data: dict):
        """Handle DELETE event"""
        old_image = dynamodb_data.get('OldImage', {})
        
        resource_id = old_image.get('resource_id', {}).get('S')
        print(f"🗑️  DELETE: {resource_id}")
        
        broadcast_metric_update(resource_id, {'deleted': True})

# Usage in separate process/Lambda:
# consumer = DynamoDBStreamsConsumer('CloudMetrics')
# consumer.start_consuming()
```

---

## 6. Retry Handler

### Create `src/retry_handler.py`
```python
"""
retry_handler.py
Retry logic with exponential backoff
"""

import time
import functools
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(max_attempts: int = 3, backoff_factor: float = 2, 
                       base_delay: float = 1):
    """Decorator for retrying failed operations with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    
                    if attempt < max_attempts:
                        delay = base_delay * (backoff_factor ** (attempt - 1))
                        logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
            
            raise last_exception
        return wrapper
    return decorator

# Usage:
# @retry_with_backoff(max_attempts=3, backoff_factor=2, base_delay=1)
# def fetch_cloudwatch_metrics(instance_id):
#     # This will retry up to 3 times with exponential backoff
#     return client.get_metric_statistics(...) 
```

---

## 7. Updated Config

### Update `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

# ... existing code ...

# Real-Time Settings
REALTIME_MODE = os.getenv("REALTIME_MODE", "False").lower() == "true"

# DynamoDB Configuration
USE_DYNAMODB = os.getenv("USE_DYNAMODB", "False").lower() == "true"
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "CloudMetrics")

# Connection Pooling
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))

# WebSocket
WEBSOCKET_ENABLED = os.getenv("WEBSOCKET_ENABLED", "False").lower() == "true"
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 5000))

# Async Settings
ENABLE_ASYNC = os.getenv("ENABLE_ASYNC", "False").lower() == "true"

# Retry Settings
RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", 3))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", 2))
```

---

## Next Steps

1. Install new dependencies: `pip install -r requirements.txt`
2. Add new environment variables to `.env`
3. Copy these code examples to your project
4. Test each module individually
5. Integrate into existing code gradually
6. Run comprehensive tests

This provides a solid foundation for real-time AWS database operations!
