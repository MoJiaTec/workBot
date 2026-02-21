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
    tool_type: str = "builtin"  # builtin | skill | mcp

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
        type_icon = {"builtin": "🔧", "skill": "📦", "mcp": "🔌"}.get(tool.tool_type, "🔧")
        logger.info(f"Registered tool [{tool.tool_type}]: {tool.name}")
        logger.debug(f"{type_icon} [{tool.tool_type.upper()}] {tool.name}")

    def auto_discover(self, project_root: str = None) -> int:
        """
        Auto-discover and register all skills and MCP tools.

        Scans the skills/ directory for SKILL.md metadata and reads
        mcp/config.json to find MCP server tools, then registers them all.

        Args:
            project_root: Root directory of the project. Defaults to the
                          parent directory of the core/ folder.

        Returns:
            Number of tools successfully registered.
        """
        if project_root is None:
            # core/ -> project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        try:
            from discovery import AutoDiscovery
        except ImportError:
            # Fallback: add core dir to path
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from discovery import AutoDiscovery

        discovery = AutoDiscovery(project_root)
        tool_defs = discovery.discover_all()

        registered = 0
        for tool_name, description, func in tool_defs:
            if func is None:
                logger.warning(f"[AutoDiscover] Skipping '{tool_name}': no callable found")
                continue
            if tool_name in self.tools:
                logger.debug(f"[AutoDiscover] Tool '{tool_name}' already registered, skipping")
                continue
            # Infer tool type from name prefix
            if tool_name.startswith("mcp_"):
                t_type = "mcp"
            else:
                t_type = "skill"
            self.register_tool(Tool(name=tool_name, description=description, func=func, tool_type=t_type))
            registered += 1

        logger.info(f"[AutoDiscover] Registered {registered}/{len(tool_defs)} discovered tools")
        return registered
        
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
    
    def execute_tool(self, tool_call: Dict, call_index: int = 0) -> str:
        """Execute a tool call"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("params", {})
        
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            print(f"\n❌ [Tool #{call_index}] Unknown tool: {tool_name}")
            return error_msg
        
        tool = self.tools[tool_name]
        type_icon = {"builtin": "🔧", "skill": "📦", "mcp": "🔌"}.get(tool.tool_type, "🔧")
        type_label = tool.tool_type.upper()

        # Print tool invocation header
        index_label = f" #{call_index}" if call_index else ""
        print(f"\n{type_icon} [Tool{index_label}] [{type_label}] {tool_name}")
        if params:
            param_items = list(params.items())
            for i, (k, v) in enumerate(param_items):
                v_str = str(v)
                preview = v_str[:100] + "..." if len(v_str) > 100 else v_str
                connector = "└─" if i == len(param_items) - 1 else "├─"
                print(f"     {connector} {k}: {preview}")

        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        try:
            result = self.tools[tool_name].func(**params)
            result_str = str(result)
            preview = result_str[:150] + "..." if len(result_str) > 150 else result_str
            print(f"     └─ ✅ Result: {preview}")
            logger.info(f"Tool {tool_name} executed successfully")
            return result_str
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            print(f"     └─ ❌ Error: {e}")
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
        print(f"\n{'─' * 50}")
        print(f"📥 User: {user_input}")
        print(f"{'─' * 50}")

        context = ""
        iteration = 0
        tool_call_count = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")
            print(f"\n💭 [Step {iteration}/{max_iterations}] Thinking...")

            # Call Claude
            response = self.call_claude(user_input, context)

            # Print reasoning (everything before TOOL_CALL line, if any)
            reasoning = re.split(r'TOOL_CALL:', response)[0].strip()
            if reasoning:
                print(f"\n🧠 [Reasoning]")
                for line in reasoning.splitlines():
                    if line.strip():
                        print(f"   {line}")

            # Check for tool call
            tool_call = self._parse_tool_call(response)
            
            if tool_call:
                tool_call_count += 1
                # Execute tool
                tool_result = self.execute_tool(tool_call, call_index=tool_call_count)
                
                # Add to context for next iteration
                context += f"\n\nTool '{tool_call.get('tool')}' returned:\n{tool_result}\n"
                
                # Continue loop to let Claude process the result
                continue
            else:
                # No tool call, this is the final answer
                logger.info("Agent completed successfully")
                print(f"\n{'─' * 50}")
                print(f"✅ [Done] Completed in {iteration} step(s), {tool_call_count} tool call(s)")
                print(f"{'─' * 50}")
                return response
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        print(f"\n{'─' * 50}")
        print(f"⚠️  [Done] Max iterations ({max_iterations}) reached, {tool_call_count} tool call(s)")
        print(f"{'─' * 50}")
        return response + "\n\n(Note: Maximum iterations reached)"