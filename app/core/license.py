"""
Paksa AI Assistant - License Management

Handles software licensing and validation.
Copyright © 2025 Paksa IT Solutions (www.paksa.com.pk)
"""
import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import logging

from app.core.hardware import get_hardware_id

logger = logging.getLogger(__name__)

class LicenseError(Exception):
    """Base exception for license-related errors"""
    pass

class LicenseManager:
    """Manages software licensing and validation"""
    
    def __init__(self, license_key: str = None):
        """Initialize the license manager"""
        self.license_key = license_key or os.getenv("LICENSE_KEY")
        self.license_data = None
        
        # Load license data if key is provided
        if self.license_key:
            self.license_data = self._validate_license(self.license_key)
    
    def _generate_license_id(self, customer_name: str) -> str:
        """Generate a unique license ID"""
        seed = f"{customer_name}-{datetime.utcnow().isoformat()}-{uuid.uuid4()}"
        return hashlib.sha256(seed.encode()).hexdigest()
    
    def _get_hardware_signature(self) -> str:
        """Generate a hardware signature for the current machine"""
        hardware_id = get_hardware_id()
        return hashlib.sha256(hardware_id.encode()).hexdigest()
    
    def generate_license(
        self,
        customer_name: str,
        customer_email: str,
        expiry_days: int = 365,
        max_users: int = 1,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a new software license
        
        Args:
            customer_name: Name of the customer
            customer_email: Customer's email address
            expiry_days: Number of days until license expires
            max_users: Maximum number of users allowed
            features: Dictionary of feature flags and limits
            
        Returns:
            Dictionary containing license data
        """
        if not features:
            features = {
                "ai_chat": True,
                "voice_support": False,
                "api_access": False,
                "max_requests_per_day": 1000,
            }
        
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=expiry_days)
        
        license_data = {
            "license_id": self._generate_license_id(customer_name),
            "customer_name": customer_name,
            "customer_email": customer_email,
            "issue_date": now.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "max_users": max_users,
            "features": features,
            "hardware_bound": True,
            "hardware_signature": self._get_hardware_signature(),
            "version": "1.0.0",
        }
        
        # Sign the license data
        license_data["signature"] = self._sign_license(license_data)
        
        return license_data
    
    def _sign_license(self, license_data: Dict[str, Any]) -> str:
        """Generate a signature for the license data"""
        # Create a copy of the data without the signature if it exists
        data = license_data.copy()
        data.pop("signature", None)
        
        # Convert to a consistent string representation
        data_str = json.dumps(data, sort_keys=True)
        
        # Generate a signature using SHA-256
        secret = os.getenv("LICENSE_SECRET", "your-secret-key-here")
        signature = hashlib.sha256(f"{data_str}{secret}".encode()).hexdigest()
        
        return signature
    
    def _validate_license(self, license_key: str) -> Dict[str, Any]:
        """
        Validate a license key and return the license data if valid
        
        Args:
            license_key: The license key to validate
            
        Returns:
            Dictionary containing the license data if valid
            
        Raises:
            LicenseError: If the license is invalid or expired
        """
        try:
            # In a real implementation, this would verify the license with a license server
            # For now, we'll just validate the format
            if not license_key or not isinstance(license_key, str):
                raise LicenseError("Invalid license key format")
            
            # Here you would typically verify the license with your license server
            # For demonstration, we'll just return a mock response
            return {
                "valid": True,
                "message": "License is valid",
                "expiry_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "features": {
                    "ai_chat": True,
                    "voice_support": False,
                    "api_access": True,
                }
            }
            
        except Exception as e:
            logger.error(f"License validation failed: {str(e)}")
            raise LicenseError(f"License validation failed: {str(e)}")
    
    def check_license(self) -> Tuple[bool, str]:
        """
        Check if the current license is valid
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not self.license_key:
            return False, "No license key provided"
        
        try:
            license_data = self._validate_license(self.license_key)
            
            # Check if license is expired
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            if datetime.utcnow() > expiry_date:
                return False, "License has expired"
                
            # Check hardware binding if enabled
            if license_data.get("hardware_bound", False):
                current_signature = self._get_hardware_signature()
                if current_signature != license_data.get("hardware_signature"):
                    return False, "License is not valid for this hardware"
            
            return True, "License is valid"
            
        except LicenseError as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Error checking license: {str(e)}")
            return False, f"Error checking license: {str(e)}"

# Global license manager instance
license_manager = LicenseManager()

def validate_license() -> Tuple[bool, str]:
    """
    Validate the current license
    
    Returns:
        Tuple of (is_valid, message)
    """
    return license_manager.check_license()

def get_license_features() -> dict:
    """
    Get the features enabled by the current license
    
    Returns:
        Dictionary of features and their status
    """
    if license_manager.license_data:
        return license_manager.license_data.get("features", {})
    return {}

def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a specific feature is enabled by the current license
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        True if the feature is enabled, False otherwise
    """
    features = get_license_features()
    return features.get(feature_name, False)
