# agent.py
import os
import json
import subprocess
import re
import logging
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description
        }

class SimpleAgent:
    def __init__(self, config=None):
        self.tools: Dict[str, Tool] = {}
        self.conversation_history = []
        self.config = config
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), 
                "prompts", 
                "system_prompt.md"
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load system prompt: {e}")
            return "You are a helpful AI assistant with access to tools."
        
    def register_tool(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        
    def _build_tools_description(self) -> str:
        """Build formatted tools description"""
        return "\n".join([
            f"- {t.name}: {t.description}" 
            for t in self.tools.values()
        ])
        
    def call_claude(self, prompt: str, context: str = "") -> str:
        """Call Claude via command line"""
        tools_desc = self._build_tools_description()
        
        # Format system prompt with tools
        system = self.system_prompt.replace("{tools_description}", tools_desc)
        
        # Build full prompt
        if context:
            full_prompt = f"{system}\n\n{context}\n\nUser: {prompt}"
        else:
            full_prompt = f"{system}\n\nUser: {prompt}"
        
        logger.debug(f"Calling Claude with prompt length: {len(full_prompt)}")
        
        try:
            # Call claude-internal
            cmd = ["claude-internal", "-p", full_prompt]
            
            timeout = self.config.timeout if self.config else 30
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Claude command failed: {result.stderr}")
                return f"Error calling Claude: {result.stderr}"
            
            response = result.stdout.strip()
            logger.debug(f"Claude response length: {len(response)}")
            return response
            
        except subprocess.TimeoutExpired:
            logger.error("Claude command timed out")
            return "Error: Claude command timed out"
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return f"Error: {str(e)}"
    
    def execute_tool(self, tool_call: Dict) -> str:
        """Execute a tool call"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("params", {})
        
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return error_msg
        
        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        try:
            result = self.tools[tool_name].func(**params)
            logger.info(f"Tool {tool_name} executed successfully")
            return str(result)
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Parse tool call from response"""
        # Look for TOOL_CALL: {...}
        match = re.search(r'TOOL_CALL:\s*(\{.*?\})', response, re.DOTALL)
        if match:
            try:
                tool_call = json.loads(match.group(1))
                return tool_call
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool call JSON: {e}")
                return None
        return None
    
    def run(self, user_input: str, max_iterations: int = None) -> str:
        """Run agent with tool calling loop"""
        if max_iterations is None:
            max_iterations = self.config.max_iterations if self.config else 5
        
        logger.info(f"Starting agent run with input: {user_input[:100]}...")
        
        context = ""
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")
            
            # Call Claude
            response = self.call_claude(user_input, context)
            
            # Check for tool call
            tool_call = self._parse_tool_call(response)
            
            if tool_call:
                # Execute tool
                tool_result = self.execute_tool(tool_call)
                
                # Add to context for next iteration
                context += f"\n\nTool '{tool_call.get('tool')}' returned:\n{tool_result}\n"
                
                # Continue loop to let Claude process the result
                continue
            else:
                # No tool call, return response
                logger.info("Agent completed successfully")
                return response
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return response + "\n\n(Note: Maximum iterations reached)"