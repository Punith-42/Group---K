# Enhanced SQL Agent System

A sophisticated multi-agent system for converting natural language questions into SQL queries and providing intelligent responses. This system uses specialized agents for different tasks, ensuring better accuracy, security, and user experience.

## 🚀 Key Features

- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Database Schema Awareness**: Dynamic schema discovery and integration
- **Enhanced Security**: Multi-layer security validation
- **Intelligent Response Formatting**: Context-aware natural language responses
- **Comprehensive Error Handling**: User-friendly error messages
- **RESTful API**: Easy integration with web applications

## 🏗️ Architecture

The system consists of four specialized agents orchestrated by a main LLM agent:

### 1. Schema Awareness Agent (`SchemaAwarenessAgent`)
- **Purpose**: Provides database schema information to other agents
- **Capabilities**:
  - Dynamic schema discovery
  - Table and column information retrieval
  - Query example generation
  - Schema validation
  - Schema formatting for LLM consumption

### 2. SQL Generation Agent (`SQLGenerationAgent`)
- **Purpose**: Converts natural language questions into SQL queries
- **Capabilities**:
  - Schema-aware SQL generation
  - Security rule enforcement
  - Query pattern recognition
  - Parameterized query generation
  - SQL validation

### 3. Query Execution Agent (`QueryExecutionAgent`)
- **Purpose**: Safely executes SQL queries and handles database operations
- **Capabilities**:
  - Safe query execution
  - Security validation
  - Query syntax testing
  - Result processing
  - Multi-query execution
  - Query statistics

### 4. Response Formatting Agent (`ResponseFormattingAgent`)
- **Purpose**: Converts query results into natural language responses
- **Capabilities**:
  - Natural language response generation
  - Data summarization
  - Error response formatting
  - Empty results handling
  - Security validation
  - Context-aware responses

### 5. Main LLM Agent (`LLMDatabaseAgent`)
- **Purpose**: Orchestrates all specialized agents
- **Capabilities**:
  - Agent coordination
  - Error handling
  - Response aggregation
  - System monitoring

## 📁 Project Structure

```
agents/
├── core/
│   ├── llm_agent.py              # Main orchestration agent
│   ├── schema_agent.py           # Database schema awareness
│   ├── sql_agent.py              # SQL generation
│   ├── query_execution_agent.py  # Query execution
│   ├── response_formatting_agent.py # Response formatting
│   └── prompt_manager.py         # Template management
├── guards/
│   └── security_guards.py        # Security validation
└── prompts/
    ├── sql_generation.j2         # SQL generation templates
    ├── response_formatting.j2     # Response formatting templates
    ├── query_validation.j2       # Query validation templates
    └── query_execution_validation.j2 # Execution validation templates
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL database
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Group---K
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python setup_database.py
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=web_activity_tracker
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# API Configuration
API_HOST=127.0.0.1
API_PORT=5000
```

## 🚀 Usage

### Starting the Application

```bash
python main.py
```

The application will start on `http://127.0.0.1:5000`

### API Endpoints

#### 1. Ask a Question
```bash
curl -X POST http://127.0.0.1:5000/api/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show my web activity for today", "user_id": 1}'
```

#### 2. Validate SQL Query
```bash
curl -X POST http://127.0.0.1:5000/api/agent/validate-query \
  -H "Content-Type: application/json" \
  -d '{"sql_query": "SELECT * FROM web_activity WHERE user_id = %s", "user_id": 1}'
```

#### 3. Get Agent Information
```bash
curl http://127.0.0.1:5000/api/agent/info
```

#### 4. Get Query Examples
```bash
curl http://127.0.0.1:5000/api/agent/examples
```

#### 5. Health Check
```bash
curl http://127.0.0.1:5000/api/agent/health
```

### Example Questions

The system can handle various types of questions:

- **Time-based queries**: "Show my activity today", "What did I do this week?"
- **Aggregation queries**: "How much time did I spend on social media?"
- **Repository queries**: "What are my most active GitHub repositories?"
- **Comparison queries**: "Compare my activity this month vs last month"

## 🧪 Testing

### Run Tests
```bash
python test_enhanced_sql_agent.py
```

### Test Individual Components
```python
from agents.core.schema_agent import SchemaAwarenessAgent
from agents.core.sql_agent import SQLGenerationAgent

# Test schema agent
schema_agent = SchemaAwarenessAgent()
schema = schema_agent.get_database_schema()

# Test SQL generation
sql_agent = SQLGenerationAgent("your_openai_api_key")
sql_query = sql_agent.generate_sql_query("Show my activity today", user_id=1)
```

## 🔒 Security Features

### Multi-Layer Security
1. **Query Validation**: Syntax and structure validation
2. **Security Guards**: Block dangerous operations
3. **User Isolation**: Enforce user_id filtering
4. **Response Sanitization**: Clean output responses
5. **Parameterized Queries**: Prevent SQL injection

### Blocked Operations
- `DROP`, `DELETE`, `UPDATE`, `INSERT`
- `ALTER`, `CREATE`, `TRUNCATE`
- System table access
- Multi-statement queries
- Queries without user_id filtering

## 📊 Performance & Monitoring

### Agent Status Monitoring
```bash
curl http://127.0.0.1:5000/api/status
```

### Database Connection Testing
The system automatically tests database connections and reports status.

### Logging
Comprehensive logging is available for debugging and monitoring:
- Agent initialization
- Query generation
- Query execution
- Error handling
- Performance metrics

## 🔧 Configuration

### Model Configuration
You can configure different OpenAI models:
```python
# In .env file
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

### Security Levels
Adjust security levels in `agents/guards/security_guards.py`:
```python
class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

## 🐛 Troubleshooting

### Common Issues

1. **"Agent not initialized"**
   - Check if `OPENAI_API_KEY` is set
   - Verify database connection

2. **"Failed to generate SQL query"**
   - Check database schema
   - Verify question format
   - Review OpenAI API limits

3. **"Database connection failed"**
   - Verify database credentials
   - Check database server status
   - Ensure database exists

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

## 🎯 Key Improvements Made

### Enhanced Database Awareness
- **Dynamic Schema Discovery**: The system now automatically discovers database schema
- **Schema Integration**: SQL generation uses actual database structure
- **Query Examples**: Provides relevant examples based on actual schema

### Specialized Agent Architecture
- **Separation of Concerns**: Each agent has a specific role
- **Better Error Handling**: Specialized error handling for each component
- **Improved Maintainability**: Easier to modify and extend individual components

### Enhanced Security
- **Multi-Layer Validation**: Multiple security checks at different levels
- **Query Syntax Testing**: Validates SQL syntax before execution
- **Response Sanitization**: Cleans output to prevent security issues

### Better User Experience
- **Context-Aware Responses**: Responses are tailored to the specific question
- **Intelligent Error Messages**: User-friendly error messages
- **Empty Results Handling**: Proper handling when no data is found

### Improved Performance
- **Caching**: Schema information is cached for better performance
- **Parallel Processing**: Agents can work independently
- **Optimized Queries**: Better SQL generation with schema awareness
