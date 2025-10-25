"""
Prompt Manager for LLM Agent System.
Handles loading and rendering Jinja2 templates for different agent tasks.
"""

import os
import json
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages Jinja2 prompt templates for the LLM agent system."""
    
    def __init__(self, prompts_dir: str = "agents/prompts"):
        """Initialize the prompt manager.
        
        Args:
            prompts_dir: Directory containing Jinja2 template files
        """
        self.prompts_dir = prompts_dir
        self.env = Environment(
            loader=FileSystemLoader(prompts_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Cache for loaded templates
        self._template_cache = {}
        
        logger.info(f"PromptManager initialized with templates from: {prompts_dir}")
    
    def load_template(self, template_name: str):
        """Load a Jinja2 template.
        
        Args:
            template_name: Name of the template file (without .j2 extension)
            
        Returns:
            Jinja2 Template object
        """
        if template_name not in self._template_cache:
            try:
                template_path = f"{template_name}.j2"
                self._template_cache[template_name] = self.env.get_template(template_path)
                logger.debug(f"Loaded template: {template_path}")
            except Exception as e:
                logger.error(f"Failed to load template {template_name}: {e}")
                raise
        
        return self._template_cache[template_name]
    
    def render_sql_generation_prompt(self, question: str, user_id: int, current_date: str = None, schema_info: str = None) -> str:
        """Render the SQL generation prompt.
        
        Args:
            question: User's natural language question
            user_id: User ID for security filtering
            current_date: Current date (defaults to today)
            schema_info: Database schema information
            
        Returns:
            Rendered prompt string
        """
        from datetime import datetime
        
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        template = self.load_template("sql_generation")
        
        context = {
            "question": question,
            "user_id": user_id,
            "current_date": current_date,
            "schema_info": schema_info or "Database schema information not available"
        }
        
        return template.render(**context)
    
    def render_response_formatting_prompt(self, question: str, row_count: int, has_data: bool, columns: list, data_summary: dict, data_preview: str) -> str:
        """Render the response formatting prompt.
        
        Args:
            question: Original user question
            row_count: Number of rows returned
            has_data: Whether data was found
            columns: List of column names
            data_summary: Summary of the data
            data_preview: Preview of the actual data
            
        Returns:
            Rendered prompt string
        """
        template = self.load_template("response_formatting")
        
        context = {
            "question": question,
            "row_count": row_count,
            "has_data": has_data,
            "columns": columns,
            "data_summary": json.dumps(data_summary, indent=2) if data_summary else "No summary available",
            "data_preview": data_preview
        }
        
        return template.render(**context)
    
    def render_query_validation_prompt(self, sql_query: str) -> str:
        """Render the query validation prompt.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Rendered prompt string
        """
        template = self.load_template("query_validation")
        
        context = {
            "sql_query": sql_query
        }
        
        return template.render(**context)
    
    def render_query_execution_validation_prompt(self, sql_query: str) -> str:
        """Render the query execution validation prompt.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Rendered prompt string
        """
        template = self.load_template("query_execution_validation")
        
        context = {
            "sql_query": sql_query
        }
        
        return template.render(**context)
    
    def get_available_templates(self) -> list:
        """Get list of available template files.
        
        Returns:
            List of template names (without .j2 extension)
        """
        if not os.path.exists(self.prompts_dir):
            return []
        
        templates = []
        for file in os.listdir(self.prompts_dir):
            if file.endswith('.j2'):
                templates.append(file[:-3])  # Remove .j2 extension
        
        return templates
    
    def reload_templates(self):
        """Reload all templates from disk."""
        self._template_cache.clear()
        self.env = Environment(
            loader=FileSystemLoader(self.prompts_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        logger.info("Templates reloaded from disk")
