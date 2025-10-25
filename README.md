# Web Activity Tracker with LLM Agent System

A Flask-based web application that combines traditional web activity tracking with an intelligent LLM-powered agent system. Users can ask natural language questions about their data and get intelligent responses.

## Features

- **MySQL Database**: Simple data storage with proper indexing
- **Flask REST API**: Clean and well-documented API endpoints
- **LLM Agent System**: Natural language to SQL query generation
- **Security Guards**: Multi-layer security for query validation
- **Jinja2 Templates**: Flexible prompt management system
- **HuggingFace Integration**: Powered by HuggingFace LLM models
- **Local Configuration**: Simple environment-based configuration

## Architecture

```
User Question → LLM Agent → SQL Query → Database → Results → LLM → Natural Response
```

### Core Components

- **Prompt Manager**: Handles Jinja2 template rendering
- **Security Guards**: Validates SQL queries and responses
- **LLM Agent**: Processes natural language and generates SQL
- **Database Manager**: Safe database operations
- **API Endpoints**: RESTful interface for agent interaction

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+ or MariaDB 10.3+
- HuggingFace API token
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
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

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

5. **Set up database**
   ```bash
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://127.0.0.1:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=web_activity_db
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306

# Flask Configuration
SECRET_KEY=local-development-key

# HuggingFace LLM Configuration
HUGGINGFACE_TOKEN_API=your_huggingface_token
HUGGINGFACE_MODEL=openai/gpt-oss-120b

# GitHub API Configuration (optional)
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
```

## API Endpoints

### System Endpoints
- `GET /` - System information
- `GET /api/health` - Basic health check
- `GET /api/status` - System status

### Agent Endpoints
- `POST /api/agent/ask` - Ask natural language questions
- `POST /api/agent/validate-query` - Validate SQL queries
- `GET /api/agent/health` - Agent health check
- `GET /api/agent/info` - Agent information
- `GET /api/agent/examples` - Query examples

### Traditional API Endpoints
- `POST /api/store_web_activity` - Store web activity data
- `GET /api/get_activity` - Get activity data
- `GET /api/get_user_stats` - Get user statistics
- `POST /api/store_github_activity` - Store GitHub activity
- `GET /api/get_github_activity` - Get GitHub activity
- `GET /api/get_github_stats` - Get GitHub statistics

## Usage Examples

### Natural Language Queries

```bash
# Ask a question about web activity
curl -X POST http://127.0.0.1:5000/api/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show my web activity for today",
    "user_id": 1
  }'

# Ask about GitHub activity
curl -X POST http://127.0.0.1:5000/api/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much time did I spend on social media this week?",
    "user_id": 1
  }'

# Ask about repository activity
curl -X POST http://127.0.0.1:5000/api/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are my most active GitHub repositories?",
    "user_id": 1
  }'
```

### Traditional API Usage

```bash
# Store web activity
curl -X POST http://127.0.0.1:5000/api/store_web_activity \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "website_name": "github.com",
    "time_spent": 30,
    "activity_date": "2024-10-25"
  }'

# Get daily activity
curl "http://127.0.0.1:5000/api/get_activity?user_id=1&date=2024-10-25"
```

## Project Structure

```
Group---K/
├── main.py                    # Main application entry point
├── app.py                     # Original Flask application
├── config.py                  # Configuration management
├── setup_database.py          # Database setup script
├── requirements.txt           # Python dependencies
├── env.example               # Environment template
├── README.md                 # This file
├── agents/                   # LLM Agent System
│   ├── core/                # Core agent components
│   │   ├── prompt_manager.py # Jinja2 template management
│   │   └── llm_agent.py     # Main LLM agent
│   ├── guards/              # Security components
│   │   └── security_guards.py # Query and response validation
│   └── prompts/             # Jinja2 templates
│       ├── sql_generation.j2    # SQL generation prompts
│       ├── response_formatting.j2 # Response formatting prompts
│       └── query_validation.j2   # Query validation prompts
└── backend/                 # Backend components
    ├── database/            # Database management
    │   └── db_manager.py    # Database operations
    └── api/                 # API endpoints
        └── agent_endpoints.py # Agent API endpoints
```

## Security Features

### Multi-Layer Security

1. **Query Validation**: Blocks dangerous SQL operations
2. **User ID Filtering**: Ensures all queries include user_id filtering
3. **LLM Validation**: Additional AI-powered query validation
4. **Response Sanitization**: Cleans LLM responses for security
5. **Input Validation**: Validates all user inputs

### Blocked Operations

- DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
- System table access
- Multiple statement execution
- Non-standard SQL keywords (in high security mode)

## Database Schema

### web_activity Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT PRIMARY KEY | Auto-incrementing primary key |
| user_id | INT NOT NULL | User identifier |
| website_name | VARCHAR(255) NOT NULL | Name of the website |
| time_spent | INT NOT NULL | Time spent in minutes |
| activity_date | DATE NOT NULL | Date of the activity |
| created_at | TIMESTAMP | Record creation timestamp |

### github_activity Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT PRIMARY KEY | Auto-incrementing primary key |
| user_id | INT NOT NULL | User identifier |
| github_username | VARCHAR(255) NOT NULL | GitHub username |
| activity_type | ENUM | Type of activity (commit, pull_request, issue, push, repository) |
| repository_name | VARCHAR(255) | Repository name |
| activity_description | TEXT | Description of the activity |
| commit_count | INT DEFAULT 0 | Number of commits |
| activity_date | DATE NOT NULL | Date of the activity |
| created_at | TIMESTAMP | Record creation timestamp |

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `405` - Method Not Allowed
- `500` - Internal Server Error

## Development

### Running the Application

```bash
# Start the full system
python main.py

# Start only the basic API (without agent)
python app.py
```

### Testing the Agent

```bash
# Test agent health
curl http://127.0.0.1:5000/api/agent/health

# Get agent information
curl http://127.0.0.1:5000/api/agent/info

# Get query examples
curl http://127.0.0.1:5000/api/agent/examples
```

## Support

For issues and questions, please create an issue in the repository.
