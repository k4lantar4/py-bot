import requests
import json
import logging
from django.conf import settings
from django.utils import timezone
from .models import Transaction, ZarinpalPayment

logger = logging.getLogger(__name__)

class ZarinpalGateway:
    """Zarinpal payment gateway integration"""
    
    def __init__(self):
        """Initialize the Zarinpal gateway"""
        self.merchant_id = settings.ZARINPAL_MERCHANT
        self.sandbox = settings.ZARINPAL_SANDBOX
        self.callback_url = settings.ZARINPAL_CALLBACK_URL
        
        # Set API endpoints based on sandbox mode
        if self.sandbox:
            self.request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
            self.verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
            self.payment_url = "https://sandbox.zarinpal.com/pg/StartPay/"
        else:
            self.request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
            self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
            self.payment_url = "https://www.zarinpal.com/pg/StartPay/"
    
    def request_payment(self, transaction_id, amount, description, email=None, mobile=None):
        """Request a payment from Zarinpal"""
        try:
            # Get transaction
            transaction = Transaction.objects.get(id=transaction_id)
            
            # Convert amount from Toman to Rial (Zarinpal uses Rial)
            amount_rial = int(amount * 10)
            
            # Prepare request data
            data = {
                "merchant_id": self.merchant_id,
                "amount": amount_rial,
                "description": description,
                "callback_url": self.callback_url,
            }
            
            # Add optional parameters if provided
            if email:
                data["email"] = email
            if mobile:
                data["mobile"] = mobile
            
            # Make request to Zarinpal
            response = requests.post(self.request_url, json=data, timeout=10)
            result = response.json()
            
            if self.sandbox:
                # Sandbox response format
                if result.get("Status") == 100:
                    authority = result.get("Authority")
                    payment_url = f"{self.payment_url}{authority}"
                    
                    # Create Zarinpal payment record
                    zarinpal_payment = ZarinpalPayment.objects.create(
                        transaction=transaction,
                        authority=authority,
                        status='pending',
                        payment_url=payment_url
                    )
                    
                    return {
                        "success": True,
                        "authority": authority,
                        "payment_url": payment_url
                    }
                else:
                    error_code = result.get("Status")
                    error_message = self._get_error_message(error_code)
                    logger.error(f"Zarinpal payment request failed: {error_message} (Code: {error_code})")
                    
                    return {
                        "success": False,
                        "error_code": error_code,
                        "error_message": error_message
                    }
            else:
                # Production response format
                if result.get("data", {}).get("code") == 100:
                    authority = result.get("data", {}).get("authority")
                    payment_url = f"{self.payment_url}{authority}"
                    
                    # Create Zarinpal payment record
                    zarinpal_payment = ZarinpalPayment.objects.create(
                        transaction=transaction,
                        authority=authority,
                        status='pending',
                        payment_url=payment_url
                    )
                    
                    return {
                        "success": True,
                        "authority": authority,
                        "payment_url": payment_url
                    }
                else:
                    error_code = result.get("errors", {}).get("code")
                    error_message = result.get("errors", {}).get("message", "Unknown error")
                    logger.error(f"Zarinpal payment request failed: {error_message} (Code: {error_code})")
                    
                    return {
                        "success": False,
                        "error_code": error_code,
                        "error_message": error_message
                    }
        except Transaction.DoesNotExist:
            logger.error(f"Transaction with ID {transaction_id} does not exist")
            return {
                "success": False,
                "error_message": "Transaction not found"
            }
        except Exception as e:
            logger.error(f"Error requesting Zarinpal payment: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def verify_payment(self, authority, amount):
        """Verify a payment with Zarinpal"""
        try:
            # Get Zarinpal payment
            zarinpal_payment = ZarinpalPayment.objects.get(authority=authority)
            transaction = zarinpal_payment.transaction
            
            # Convert amount from Toman to Rial (Zarinpal uses Rial)
            amount_rial = int(amount * 10)
            
            # Prepare verification data
            data = {
                "merchant_id": self.merchant_id,
                "authority": authority,
                "amount": amount_rial
            }
            
            # Make request to Zarinpal
            response = requests.post(self.verify_url, json=data, timeout=10)
            result = response.json()
            
            if self.sandbox:
                # Sandbox response format
                if result.get("Status") == 100:
                    ref_id = result.get("RefID")
                    
                    # Update Zarinpal payment record
                    zarinpal_payment.ref_id = ref_id
                    zarinpal_payment.status = 'verified'
                    zarinpal_payment.save()
                    
                    # Update transaction
                    transaction.status = 'completed'
                    transaction.transaction_id = ref_id
                    transaction.transaction_data = result
                    transaction.save()
                    
                    return {
                        "success": True,
                        "ref_id": ref_id,
                        "transaction_id": transaction.id
                    }
                else:
                    error_code = result.get("Status")
                    error_message = self._get_error_message(error_code)
                    logger.error(f"Zarinpal payment verification failed: {error_message} (Code: {error_code})")
                    
                    # Update Zarinpal payment record
                    zarinpal_payment.status = 'failed'
                    zarinpal_payment.save()
                    
                    # Update transaction
                    transaction.status = 'failed'
                    transaction.transaction_data = result
                    transaction.save()
                    
                    return {
                        "success": False,
                        "error_code": error_code,
                        "error_message": error_message
                    }
            else:
                # Production response format
                if result.get("data", {}).get("code") == 100:
                    ref_id = result.get("data", {}).get("ref_id")
                    
                    # Update Zarinpal payment record
                    zarinpal_payment.ref_id = ref_id
                    zarinpal_payment.status = 'verified'
                    zarinpal_payment.save()
                    
                    # Update transaction
                    transaction.status = 'completed'
                    transaction.transaction_id = ref_id
                    transaction.transaction_data = result
                    transaction.save()
                    
                    return {
                        "success": True,
                        "ref_id": ref_id,
                        "transaction_id": transaction.id
                    }
                else:
                    error_code = result.get("errors", {}).get("code")
                    error_message = result.get("errors", {}).get("message", "Unknown error")
                    logger.error(f"Zarinpal payment verification failed: {error_message} (Code: {error_code})")
                    
                    # Update Zarinpal payment record
                    zarinpal_payment.status = 'failed'
                    zarinpal_payment.save()
                    
                    # Update transaction
                    transaction.status = 'failed'
                    transaction.transaction_data = result
                    transaction.save()
                    
                    return {
                        "success": False,
                        "error_code": error_code,
                        "error_message": error_message
                    }
        except ZarinpalPayment.DoesNotExist:
            logger.error(f"Zarinpal payment with authority {authority} does not exist")
            return {
                "success": False,
                "error_message": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Error verifying Zarinpal payment: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def _get_error_message(self, error_code):
        """Get error message for Zarinpal error code"""
        error_messages = {
            -1: "Information submitted is incomplete.",
            -2: "Merchant ID or IP address is not correct.",
            -3: "Amount should be above 1,000 Rial.",
            -4: "Approved level of Merchant ID is lower than the silver.",
            -11: "Request not found.",
            -12: "Edit request not possible.",
            -21: "Financial operations for this transaction was not found.",
            -22: "Transaction is unsuccessful.",
            -33: "Transaction amount does not match the payment amount.",
            -34: "Limit of transaction division has been reached.",
            -40: "There is no access to the method.",
            -41: "Additional data format is invalid.",
            -42: "Initiator IP or Merchant ID is invalid.",
            -54: "Request archived.",
            100: "Operation was successful.",
            101: "Operation was successful but verification operation on this transaction has already been done."
        }
        
        return error_messages.get(error_code, "Unknown error") 