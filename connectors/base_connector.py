"""Abstract base class for prop firm connectors."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class ConnectorConfigError(Exception):
    """Raised when connector configuration is invalid or missing."""
    pass


@dataclass
class ConnectorResult:
    """Result of a connector operation."""
    status: str  # SUCCESS, FAILED, RETRY, SKIPPED
    external_order_id: Optional[str] = None
    raw_request: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BasePropConnector(ABC):
    """Abstract base class for prop firm connectors."""
    
    def __init__(self, firm_code: str, config: Dict[str, Any]):
        self.firm_code = firm_code
        self.config = config
    
    @abstractmethod
    def authenticate(self) -> ConnectorResult:
        """Authenticate with the prop firm API."""
        pass
    
    @abstractmethod
    def place_order(self, order_payload: Dict[str, Any]) -> ConnectorResult:
        """Place an order with the prop firm."""
        pass
    
    @abstractmethod
    def get_order_status(self, external_order_id: str) -> ConnectorResult:
        """Get the status of an existing order."""
        pass
    
    @abstractmethod
    def cancel_order(self, external_order_id: str) -> ConnectorResult:
        """Cancel an existing order."""
        pass
    
    def supports_symbol(self, symbol: str) -> bool:
        """Check if the connector supports trading the given symbol."""
        supported_symbols = self.config.get('supported_symbols', ['NQ', 'ES', 'YM', 'RTY'])
        return symbol in supported_symbols
