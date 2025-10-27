graph TB
    %% Main Orchestrator
    subgraph Orchestrator["Main Orchestrator"]
        LLM_AGENT["LLMDatabaseAgent<br/>process_question()"]
    end
    
    %% Specialized Agents - Code Execution Flow
    subgraph Agents["Specialized Agents - Code Execution Flow"]
        SCHEMA_AGENT["SchemaAwarenessAgent<br/>get_database_schema()<br/>Tool: MySQL Database"]
        SQL_AGENT["SQLGenerationAgent<br/>generate_sql_query()<br/>Tools: Gemini LLM + Schema Info"]
        QUERY_AGENT["QueryExecutionAgent<br/>execute_query()<br/>Tool: MySQL Database"]
        RESPONSE_AGENT["ResponseFormattingAgent<br/>format_response()<br/>Tool: Gemini LLM"]
    end
    
    %% External Tools Integration
    subgraph Tools["External Tools"]
        GEMINI["Google Gemini 2.5 Pro<br/>ChatGoogleGenerativeAI"]
        MYSQL["MySQL Database<br/>PyMySQL Driver"]
        LANGSMITH["LangSmith Tracing<br/>@traceable decorators"]
    end
    
    %% Security Guards - Validation Points
    subgraph Security["Security Guards - Validation Points"]
        QUERY_GUARD["QuerySecurityGuard<br/>validate_query()<br/>Checks: Dangerous keywords, user_id filtering"]
        RESPONSE_GUARD["ResponseSecurityGuard<br/>validate_response()<br/>Checks: Script injection, malicious content"]
    end

    %% Code Flow and Agent Interactions
    LLM_AGENT --> SCHEMA_AGENT
    SCHEMA_AGENT --> SQL_AGENT
    SQL_AGENT --> QUERY_AGENT
    QUERY_AGENT --> RESPONSE_AGENT

    %% Tools Integration - Flow to External Tools
    SCHEMA_AGENT --> MYSQL
    SQL_AGENT --> GEMINI
    QUERY_AGENT --> MYSQL
    RESPONSE_AGENT --> GEMINI
    LLM_AGENT --> LANGSMITH

    %% Security Guards Validation Flow
    SQL_AGENT --> QUERY_GUARD
    QUERY_AGENT --> QUERY_GUARD
    RESPONSE_AGENT --> RESPONSE_GUARD

    %% Styling for Better Clarity
    classDef orchestrator fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef agents fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef tools fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef security fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    
    class LLM_AGENT orchestrator
    class SCHEMA_AGENT,SQL_AGENT,QUERY_AGENT,RESPONSE_AGENT agents
    class GEMINI,MYSQL,LANGSMITH tools
    class QUERY_GUARD,RESPONSE_GUARD security