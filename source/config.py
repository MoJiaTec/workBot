# config.py
import os
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Agent configuration"""
    # Claude settings
    claude_command: str = "claude-internal"
    max_iterations: int = 5  # Maximum tool call iterations
    timeout: int = 30  # Command timeout in seconds
    
    # Model parameters
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Debug settings
    debug: bool = False
    log_file: str = "agent.log"
    
    # Tool settings
    tool_timeout: int = 10  # Individual tool timeout
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            claude_command=os.getenv("CLAUDE_COMMAND", "claude-internal"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "5")),
            timeout=int(os.getenv("TIMEOUT", "30")),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )

# Default configuration
config = AgentConfig()
