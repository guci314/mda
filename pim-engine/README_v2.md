# PIM Engine v2.0 - Multi-Process Architecture

## Overview

PIM Engine v2.0 introduces a revolutionary multi-process architecture where:
- **Models**: PIM definitions loaded from YAML/Markdown files
- **Instances**: Independent FastAPI processes running specific models
- Each instance has its own port, database, and complete isolation

## Architecture

```
Master Controller (Port 8000)
├── Model Management API
│   ├── Load/unload models
│   └── List loaded models
└── Instance Management API
    ├── Create/stop instances
    ├── Port allocation
    └── Health monitoring

Instance 1 (Port 8001)    Instance 2 (Port 8002)    Instance N (Port 800X)
├── FastAPI Server        ├── FastAPI Server        ├── FastAPI Server
├── SQLite Database       ├── SQLite Database       ├── SQLite Database
└── Complete Isolation    └── Complete Isolation    └── Complete Isolation
```

## Quick Start

### 1. Install Dependencies
```bash
cd pim-engine
pip install -r requirements.txt
```

### 2. Start Master Controller
```bash
cd src
python main.py
# Or use the script:
./start_master.sh
```

### 3. Load a Model
```bash
# Load user_management model
curl -X POST http://localhost:8000/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_name": "user_management"}'
```

### 4. Create an Instance
```bash
# Create production instance
curl -X POST http://localhost:8000/instances \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "user_management",
    "instance_id": "user_prod",
    "port": 8001
  }'
```

### 5. Access the Instance
```bash
# Check instance health
curl http://localhost:8001/health

# View API documentation
open http://localhost:8001/docs

# Use the API
curl http://localhost:8001/api/v1/users
```

## API Reference

### Model Management API

#### List Models
```http
GET /models
```

#### Load Model
```http
POST /models/load
{
  "model_name": "string"
}
```

#### Get Model Details
```http
GET /models/{model_name}
```

#### Unload Model
```http
DELETE /models/{model_name}
```

### Instance Management API

#### List Instances
```http
GET /instances
GET /instances?model=user_management  # Filter by model
```

#### Create Instance
```http
POST /instances
{
  "model_name": "string",
  "instance_id": "string",  // Optional
  "port": 8001,            // Optional
  "config": {}             // Optional
}
```

#### Get Instance Details
```http
GET /instances/{instance_id}
```

#### Stop Instance
```http
DELETE /instances/{instance_id}
```

#### Check Instance Health
```http
GET /instances/{instance_id}/health
```

## Features

### 1. Complete Isolation
- Each instance runs in a separate process
- Independent databases (SQLite by default)
- No shared state between instances

### 2. Dynamic Port Allocation
- Automatic port assignment (8001-8999)
- Manual port specification supported
- Port conflict detection

### 3. Multi-Instance Support
- Run multiple instances of the same model
- Different configurations per instance
- Independent scaling

### 4. Health Monitoring
- Automatic health checks
- Process monitoring
- Graceful shutdown

## Example Scenarios

### Scenario 1: Development and Production
```bash
# Load model
curl -X POST http://localhost:8000/models/load \
  -d '{"model_name": "order_management"}'

# Create production instance
curl -X POST http://localhost:8000/instances \
  -d '{"model_name": "order_management", "instance_id": "orders_prod", "port": 8001}'

# Create development instance
curl -X POST http://localhost:8000/instances \
  -d '{"model_name": "order_management", "instance_id": "orders_dev", "port": 8002}'
```

### Scenario 2: Load Balancing
```bash
# Create multiple instances for load balancing
for i in {1..3}; do
  curl -X POST http://localhost:8000/instances \
    -d "{\"model_name\": \"user_management\", \"instance_id\": \"user_lb_$i\"}"
done
```

## Directory Structure

```
pim-engine/
├── instances/              # Instance data
│   ├── user_prod/
│   │   ├── config.json    # Instance configuration
│   │   └── database.db    # Instance database
│   └── user_test/
│       ├── config.json
│       └── database.db
├── logs/                   # Instance logs
│   ├── master.log
│   ├── user_prod.log
│   └── user_test.log
└── models/                 # PIM model files
    ├── user_management.yaml
    └── order_management.yaml
```

## Testing

Run the test script to verify the setup:
```bash
cd ..  # Go to mda directory
python test_multiprocess.py
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i:8000

# Kill process
kill -9 <PID>
```

### Instance Won't Start
- Check logs in `logs/` directory
- Verify model file exists
- Check port availability
- Ensure database permissions

### Model Not Found
- Check file exists in `models/` directory
- Verify file extension (.yaml, .yml, or .md)
- Check file permissions

## Migration from v1.0

The v2.0 architecture is completely new and doesn't require backward compatibility:
1. Stop the old single-process engine
2. Start the new master controller
3. Load models and create instances as needed
4. Update client applications to use instance-specific ports

## Performance

- **Startup Time**: ~1-3 seconds per instance
- **Memory**: ~50-100MB per instance
- **CPU**: Scales linearly with instances
- **Isolation**: Complete process isolation

## Future Enhancements

- [ ] Docker support for instances
- [ ] Kubernetes deployment
- [ ] Instance auto-scaling
- [ ] Distributed architecture
- [ ] Web UI for management