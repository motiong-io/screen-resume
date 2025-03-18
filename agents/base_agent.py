from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseAgent(ABC):
    """Base class for all agents in the resume screening system."""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process the input data and return results."""
        pass
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate the input data before processing."""
        pass 