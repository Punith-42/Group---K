# 🤖 Web Activity Agent System - Streamlit Frontend

A beautiful, interactive web application for querying your web activity and GitHub data using natural language.

## 🚀 Features

### 💬 **Interactive Chat Interface**
- Ask questions in natural language
- Real-time responses from LLM agents
- Chat history with persistent conversation
- Example questions for quick start

### 📊 **Rich Data Visualization**
- Interactive data tables
- Automatic chart generation
- Statistical summaries
- Categorical data analysis

### 🔍 **Query Transparency**
- View generated SQL queries
- See which agents were used
- Execution timestamps and metadata
- Error handling with helpful messages

### 🛡️ **Security & Safety**
- User isolation (user_id filtering)
- SQL injection protection
- Query validation and sanitization
- Safe UNION operations

## 🎯 **Example Questions You Can Ask**

### **Web Activity Queries:**
- "How much time did I spend on YouTube today?"
- "What are my most visited websites this week?"
- "Show my browsing activity for yesterday"
- "Which websites did I spend the most time on?"

### **GitHub Activity Queries:**
- "How many commits did I make this month?"
- "What are my most active repositories?"
- "Show my GitHub activity for the past 5 days"
- "Which repositories have I been working on recently?"

### **Cross-Platform Queries (UNION):**
- "Show all my activity from both web and GitHub today"
- "What are my most active platforms overall?"
- "Compare my GitHub commits vs web browsing time"
- "Show all my repositories and websites I've been active on"

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│   FastAPI        │───▶│   LLM Agents    │
│   Frontend      │    │   Backend        │    │   (Multi-Agent) │
│   (Port 8501)   │    │   (Port 5000)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   MySQL        │
         │                       │              │   Database      │
         │                       │              │                 │
         │                       └──────────────▶│                 │
         │                                       └─────────────────┘
         │
         ▼
┌─────────────────┐
│   LangSmith     │
│   Tracing       │
│   (Optional)    │
└─────────────────┘
```

## 🚀 **Quick Start**

### **1. Start the FastAPI Backend**
```bash
# Option 1: Using the startup script
python main_fastapi.py

# Option 2: Using uvicorn directly
uvicorn main_fastapi:app --host 127.0.0.1 --port 5000 --reload
```

### **2. Start the Streamlit Frontend**
```bash
# Option 1: Using the startup script
python start_streamlit.py

# Option 2: Using streamlit directly
streamlit run streamlit_app.py --server.port 8501
```

### **3. Access the Application**
- **Streamlit App**: http://localhost:8501
- **FastAPI Docs**: http://127.0.0.1:5000/docs
- **API Health**: http://127.0.0.1:5000/api/agent/health

## 🎨 **User Interface**

### **Main Chat Interface**
- Clean, modern design with chat bubbles
- User questions in blue bubbles
- Agent responses in purple bubbles
- Real-time typing indicators

### **Sidebar Features**
- System health status
- Example questions (clickable)
- User ID configuration
- Clear chat history button

### **Results Display**
- Structured data tables
- Automatic visualizations
- SQL query transparency
- Error handling with helpful messages

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
DB_PASSWORD=your_mysql_password

# Optional
LANGSMITH_API_KEY=your_langsmith_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
API_HOST=127.0.0.1
API_PORT=5000
```

### **Streamlit Configuration**
The app uses `.streamlit/config.toml` for configuration:
- Custom theme colors
- Server settings
- Browser behavior

## 📊 **Data Visualization Features**

### **Automatic Charts**
- Bar charts for categorical data
- Statistical summaries for numeric data
- Value counts for text data
- Time-series data handling

### **Interactive Tables**
- Sortable columns
- Searchable data
- Export capabilities
- Responsive design

## 🛡️ **Security Features**

### **Query Security**
- User ID filtering (mandatory)
- SQL injection protection
- Dangerous keyword blocking
- UNION query validation

### **Data Privacy**
- User isolation
- No cross-user data access
- Secure parameter handling
- Input validation

## 🔍 **Debugging & Monitoring**

### **LangSmith Integration**
- Full query tracing
- Agent performance monitoring
- Error tracking
- Cost analysis

### **Error Handling**
- Graceful error messages
- Detailed error logging
- Fallback responses
- User-friendly notifications

## 📱 **Responsive Design**

- Mobile-friendly interface
- Adaptive layouts
- Touch-friendly controls
- Cross-browser compatibility

## 🎯 **Use Cases**

### **Personal Analytics**
- Track web browsing habits
- Monitor GitHub activity
- Analyze time spent on different platforms
- Identify productivity patterns

### **Data Exploration**
- Discover data patterns
- Generate insights
- Create custom reports
- Export data for analysis

### **Learning & Development**
- Understand SQL query generation
- Learn about LLM agents
- Explore database schemas
- Practice natural language queries

## 🚀 **Performance**

- **Fast Response Times**: Optimized API calls
- **Efficient Caching**: Streamlit session state
- **Scalable Architecture**: Microservices design
- **Real-time Updates**: Live chat interface

## 🔧 **Troubleshooting**

### **Common Issues**

1. **"System Offline" Error**
   - Ensure FastAPI server is running on port 5000
   - Check database connection
   - Verify environment variables

2. **"API Error" Messages**
   - Check network connectivity
   - Verify API endpoint URLs
   - Review server logs

3. **Empty Results**
   - Verify user_id in database
   - Check date ranges
   - Review query examples

### **Debug Mode**
Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 📈 **Future Enhancements**

- [ ] Real-time data streaming
- [ ] Advanced visualizations (Plotly)
- [ ] Export to PDF/Excel
- [ ] Custom dashboard creation
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] Caching layer
- [ ] Mobile app version

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

---

**🎉 Enjoy exploring your data with natural language queries!**
