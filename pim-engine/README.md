# PIM Execution Engine

A revolutionary runtime engine that directly executes Platform Independent Models (PIM) without code generation.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
cd pim-engine

# Copy environment variables
cp .env.example .env

# Start the engine
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f pim-engine
```

The engine will be available at:
- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health
- Debug UI: http://localhost:8001/debug/ui
- Adminer (DB UI): http://localhost:8080

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Python path
export PYTHONPATH=$PWD/src

# Run the engine
python src/main.py
```

## 📝 Creating PIM Models

### YAML Format

Create a model in `models/` directory:

```yaml
# models/product_management.yaml
domain: product-management
version: 1.0.0

entities:
  - name: Product
    attributes:
      name:
        type: string
        required: true
      price:
        type: float
        required: true
      stock:
        type: integer
        default: 0

services:
  - name: ProductService
    methods:
      - name: createProduct
        parameters:
          productData: Product
```

### Markdown Format

The engine also supports PIM models in Markdown format (Chinese):

```markdown
# 产品管理 (PIM)

## 领域对象

### 产品 (Product)
**属性**：
- 名称：产品的名称
- 价格：产品的销售价格
- 库存：当前库存数量
```

## 🔧 API Usage

Once a model is loaded, the engine automatically generates REST APIs:

### Entity CRUD Operations

```bash
# Create
curl -X POST http://localhost:8001/api/v1/user-management/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Read
curl http://localhost:8001/api/v1/user-management/users/{id}

# Update
curl -X PUT http://localhost:8001/api/v1/user-management/users/{id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe"}'

# Delete
curl -X DELETE http://localhost:8001/api/v1/user-management/users/{id}

# List
curl http://localhost:8001/api/v1/user-management/users?skip=0&limit=10
```

### Service Method Calls

```bash
# Execute service method
curl -X POST http://localhost:8001/api/v1/user-management/user/registeruser \
  -H "Content-Type: application/json" \
  -d '{"userData": {"name": "John", "email": "john@example.com"}}'
```

## 🎯 Core Features

### 1. Dynamic Model Loading
- Hot reload support - models update without restart
- Multiple format support (YAML, Markdown)
- Automatic validation

### 2. Automatic API Generation
- RESTful CRUD endpoints
- Service method endpoints
- OpenAPI documentation
- Type validation with Pydantic

### 3. Business Rule Engine
- Natural language rule support
- Simple rule compilation for performance
- LLM integration ready

### 4. Flow Engine
- Execute business processes defined in flowcharts
- Step-by-step execution
- Debug support with callbacks

### 5. Data Engine
- Dynamic table creation
- Type mapping
- Relationship handling
- Transaction support

### 6. Flow Debugger
- Web-based debugging interface
- Real-time flow visualization
- Step-by-step execution monitoring
- WebSocket-based live updates
- Variable inspection

## 📊 Engine Management

### Load a Model

```bash
curl -X POST http://localhost:8001/engine/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_name": "user_management"}'
```

### List Loaded Models

```bash
curl http://localhost:8001/engine/models
```

### Check Engine Status

```bash
curl http://localhost:8001/engine/status
```

## 🔍 Monitoring & Debugging

### Health Check

```bash
curl http://localhost:8001/health
```

### Flow Debugging

1. Open http://localhost:8001/debug/ui in your browser
2. Select a flow from the dropdown
3. Click "Create Debug Session"
4. Click "Start Execution" to begin
5. Watch the flow execute in real-time with:
   - Step-by-step visualization
   - Variable monitoring
   - Execution timing
   - State tracking

### Debug Session API

```bash
# Create debug session
curl -X POST http://localhost:8001/debug/session/create?flow_name=UserService.registerUser

# Start flow execution
curl -X POST http://localhost:8001/debug/session/{session_id}/start \
  -H "Content-Type: application/json" \
  -d '{"userData": {"name": "Test", "email": "test@example.com"}}'

# Get session status
curl http://localhost:8001/debug/session/{session_id}
```

## 🛠️ Configuration

Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `HOT_RELOAD`: Enable model hot reloading
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LLM_API_KEY`: Optional LLM API key for advanced rule processing

## 📁 Project Structure

```
pim-engine/
├── src/
│   ├── core/          # Engine core
│   ├── loaders/       # Model loaders
│   ├── engines/       # Execution engines
│   ├── api/           # API generation
│   └── utils/         # Utilities
├── models/            # PIM model files
├── tests/             # Test suite
├── docker/            # Docker configurations
└── docs/              # Documentation
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🎉 What's Next?

- GraphQL support
- WebSocket subscriptions
- Distributed deployment
- Plugin system
- Visual model designer

---

**Remember**: With PIM Engine, your models ARE your application! 🚀