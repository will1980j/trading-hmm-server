"""Prop firm connector registry."""
from .base_connector import BasePropConnector, ConnectorConfigError, ConnectorResult
from .ftmo_connector import FTMOConnector
from .apex_connector import ApexConnector

CONNECTOR_REGISTRY = {
    "FTMO": FTMOConnector,
    "APEX": ApexConnector
}
