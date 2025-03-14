"""
Zarinpal payment gateway integration for the V2Ray Telegram bot.

This module provides functions for creating and verifying payments using the Zarinpal API.
"""

import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Zarinpal API configuration
MERCHANT_ID = "YOUR-MERCHANT-ID"  # Replace with actual merchant ID
SANDBOX = True  # Set to False in production

# API endpoints
if SANDBOX:
    CREATE_URL = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    VERIFY_URL = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
    PAYMENT_URL = "https://sandbox.zarinpal.com/pg/StartPay/{}"
else:
    CREATE_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
    VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    PAYMENT_URL = "https://zarinpal.com/pg/StartPay/{}"

def create_payment(amount: int, user_id: int) -> Optional[str]:
    """
    Create a new payment request.
    
    Args:
        amount: Payment amount in Tomans
        user_id: Telegram user ID
        
    Returns:
        Payment URL if successful, None otherwise
    """
    try:
        # Convert amount to Rials (Zarinpal uses Rials)
        amount_rials = amount * 10
        
        # Prepare request data
        data = {
            "MerchantID": MERCHANT_ID,
            "Amount": amount_rials,
            "Description": f"V2Ray account payment - User {user_id}",
            "CallbackURL": "YOUR-CALLBACK-URL",  # Replace with actual callback URL
            "Metadata": {
                "user_id": user_id,
                "amount": amount
            }
        }
        
        # Send request to Zarinpal
        response = requests.post(CREATE_URL, json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get("Status") == 100:
            authority = result.get("Authority")
            return PAYMENT_URL.format(authority)
        else:
            logger.error(f"Failed to create Zarinpal payment: {result}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating Zarinpal payment: {e}")
        return None

def verify_payment(authority: str) -> bool:
    """
    Verify a payment using its authority code.
    
    Args:
        authority: Payment authority code
        
    Returns:
        True if payment is verified, False otherwise
    """
    try:
        # Prepare verification data
        data = {
            "MerchantID": MERCHANT_ID,
            "Authority": authority
        }
        
        # Send verification request
        response = requests.post(VERIFY_URL, json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get("Status") == 100:
            return True
        else:
            logger.error(f"Payment verification failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return False 