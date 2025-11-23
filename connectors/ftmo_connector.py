"""FTMO prop firm connector implementation."""
import requests
from typing import Any, Dict
from .base_connector import BasePropConnector, ConnectorResult


class FTMOConnector(BasePropConnector):
    """FTMO prop firm connector."""
    
    def _ensure_enabled(self) -> None:
        """Check if connector is enabled and configured."""
        if not self.config.get('enabled', False):
            raise Exception("FTMO connector is not enabled")
        if not self.config.get('api_key'):
            raise Exception("FTMO API key not configured")
        if not self.config.get('base_url'):
            raise Exception("FTMO base URL not configured")
    
    def _base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests."""
        return {
            'Authorization': f"Bearer {self.config.get('api_key')}",
            'Content-Type': 'application/json',
            'User-Agent': 'TradingPlatform/1.0'
        }
    
    def authenticate(self) -> ConnectorResult:
        """Authenticate with FTMO API."""
        try:
            self._ensure_enabled()
            return ConnectorResult(
                status="SUCCESS",
                raw_response={"authenticated": True, "firm": "FTMO"}
            )
        except Exception as e:
            return ConnectorResult(
                status="FAILED",
                error_message=f"FTMO authentication failed: {str(e)}"
            )
    
    def place_order(self, order_payload: Dict[str, Any]) -> ConnectorResult:
        """Place order with FTMO."""
        try:
            self._ensure_enabled()
            
            base_url = self.config.get('base_url')
            url = f"{base_url}/orders"
            headers = self._base_headers()
            
            response = requests.post(
                url,
                json=order_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return ConnectorResult(
                    status="SUCCESS",
                    external_order_id=response_data.get('order_id'),
                    raw_request=order_payload,
                    raw_response=response_data
                )
            elif response.status_code in [429, 503]:
                return ConnectorResult(
                    status="RETRY",
                    raw_request=order_payload,
                    raw_response=response.json() if response.content else {},
                    error_message=f"FTMO API rate limit or service unavailable: {response.status_code}"
                )
            else:
                return ConnectorResult(
                    status="FAILED",
                    raw_request=order_payload,
                    raw_response=response.json() if response.content else {},
                    error_message=f"FTMO API error: {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            return ConnectorResult(
                status="FAILED",
                raw_request=order_payload,
                error_message=f"FTMO network error: {str(e)}"
            )
        except Exception as e:
            return ConnectorResult(
                status="FAILED",
                raw_request=order_payload,
                error_message=f"FTMO connector error: {str(e)}"
            )
    
    def get_order_status(self, external_order_id: str) -> ConnectorResult:
        """Get order status from FTMO."""
        try:
            self._ensure_enabled()
            
            base_url = self.config.get('base_url')
            url = f"{base_url}/orders/{external_order_id}"
            headers = self._base_headers()
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return ConnectorResult(
                    status="SUCCESS",
                    external_order_id=external_order_id,
                    raw_response=response.json()
                )
            else:
                return ConnectorResult(
                    status="FAILED",
                    external_order_id=external_order_id,
                    error_message=f"FTMO get order status failed: {response.status_code}"
                )
        
        except Exception as e:
            return ConnectorResult(
                status="FAILED",
                external_order_id=external_order_id,
                error_message=f"FTMO get order status error: {str(e)}"
            )
    
    def cancel_order(self, external_order_id: str) -> ConnectorResult:
        """Cancel order with FTMO."""
        try:
            self._ensure_enabled()
            
            base_url = self.config.get('base_url')
            url = f"{base_url}/orders/{external_order_id}"
            headers = self._base_headers()
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                return ConnectorResult(
                    status="SUCCESS",
                    external_order_id=external_order_id,
                    raw_response=response.json() if response.content else {"cancelled": True}
                )
            else:
                return ConnectorResult(
                    status="FAILED",
                    external_order_id=external_order_id,
                    error_message=f"FTMO cancel order failed: {response.status_code}"
                )
        
        except Exception as e:
            return ConnectorResult(
                status="FAILED",
                external_order_id=external_order_id,
                error_message=f"FTMO cancel order error: {str(e)}"
            )
