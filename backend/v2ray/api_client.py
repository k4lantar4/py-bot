import requests
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import Inbound, Client, SyncLog, ClientConfig
from main.models import Server, Subscription

logger = logging.getLogger(__name__)

class ThreeXUIClient:
    """Client for interacting with 3x-UI API"""
    
    def __init__(self, server):
        """Initialize the client with a server instance"""
        self.server = server
        self.base_url = server.url.rstrip('/')
        self.username = server.username
        self.password = server.password
        self.session = requests.Session()
        self.timeout = getattr(settings, 'THREEXUI_API_TIMEOUT', 30)
        self.session_expiry = getattr(settings, 'THREEXUI_SESSION_EXPIRY', 3600)
    
    def _handle_response(self, response):
        """Handle API response and check for errors"""
        try:
            response.raise_for_status()
            data = response.json()
            if data.get('success') is False:
                logger.error(f"API error: {data.get('msg')}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            return None
    
    def login(self):
        """Login to 3x-UI panel and store session cookie"""
        # Check if we already have a valid session
        if self.server.is_session_valid():
            # Load existing session cookie
            self.session.cookies.update(json.loads(self.server.session_cookie))
            return True
        
        # Login to get a new session
        try:
            url = f"{self.base_url}/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            response = self.session.post(url, json=data, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                # Store session cookie
                self.server.session_cookie = json.dumps(dict(self.session.cookies))
                self.server.session_expiry = timezone.now() + timedelta(seconds=self.session_expiry)
                self.server.save()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def get_inbounds(self):
        """Get all inbounds from the panel"""
        if not self.login():
            return None
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.get(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return result.get('obj', [])
            
            return None
        except Exception as e:
            logger.error(f"Get inbounds error: {str(e)}")
            return None
    
    def get_inbound(self, inbound_id):
        """Get a specific inbound by ID"""
        if not self.login():
            return None
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/get/{inbound_id}"
            response = self.session.get(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return result.get('obj')
            
            return None
        except Exception as e:
            logger.error(f"Get inbound error: {str(e)}")
            return None
    
    def add_client(self, inbound_id, email, traffic_limit_gb=0, expiry_time=None):
        """Add a client to an inbound"""
        if not self.login():
            return None
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            # Convert traffic limit from GB to bytes
            traffic_limit = traffic_limit_gb * 1024 * 1024 * 1024 if traffic_limit_gb > 0 else 0
            
            # Format expiry time
            expiry_time_str = None
            if expiry_time:
                expiry_time_str = int(expiry_time.timestamp() * 1000)
            
            data = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [
                        {
                            "email": email,
                            "enable": True,
                            "expiryTime": expiry_time_str,
                            "total": traffic_limit
                        }
                    ]
                })
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Add client error: {str(e)}")
            return False
    
    def remove_client(self, inbound_id, email):
        """Remove a client from an inbound"""
        if not self.login():
            return False
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/delClient/{inbound_id}/{email}"
            response = self.session.post(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Remove client error: {str(e)}")
            return False
    
    def update_client_traffic(self, inbound_id, email, traffic_limit_gb):
        """Update a client's traffic limit"""
        if not self.login():
            return False
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/updateClientTraffic/{inbound_id}/{email}"
            
            # Convert traffic limit from GB to bytes
            traffic_limit = traffic_limit_gb * 1024 * 1024 * 1024 if traffic_limit_gb > 0 else 0
            
            data = {
                "traffic": traffic_limit
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Update client traffic error: {str(e)}")
            return False
    
    def update_client_expiry(self, inbound_id, email, expiry_time):
        """Update a client's expiry time"""
        if not self.login():
            return False
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/updateClientExpiryTime/{inbound_id}/{email}"
            
            # Format expiry time
            expiry_time_str = int(expiry_time.timestamp() * 1000)
            
            data = {
                "expiryTime": expiry_time_str
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Update client expiry error: {str(e)}")
            return False
    
    def get_client_traffic(self, email):
        """Get a client's traffic usage"""
        if not self.login():
            return None
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/getClientTraffic/{email}"
            response = self.session.get(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return result.get('obj')
            
            return None
        except Exception as e:
            logger.error(f"Get client traffic error: {str(e)}")
            return None
    
    def reset_client_traffic(self, inbound_id, email):
        """Reset a client's traffic usage"""
        if not self.login():
            return False
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/resetClientTraffic/{inbound_id}/{email}"
            response = self.session.post(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Reset client traffic error: {str(e)}")
            return False
    
    def get_client_url(self, inbound_id, email):
        """Get a client's connection URL"""
        if not self.login():
            return None
        
        try:
            url = f"{self.base_url}/panel/api/inbounds/getClientUrl/{inbound_id}/{email}"
            response = self.session.get(url, timeout=self.timeout)
            result = self._handle_response(response)
            
            if result and result.get('success'):
                return result.get('obj')
            
            return None
        except Exception as e:
            logger.error(f"Get client URL error: {str(e)}")
            return None


def sync_server(server_id):
    """Sync a server's inbounds and clients with the database"""
    try:
        server = Server.objects.get(id=server_id, is_active=True)
        client = ThreeXUIClient(server)
        
        # Get all inbounds from the panel
        inbounds_data = client.get_inbounds()
        if inbounds_data is None:
            # Create a failed sync log
            SyncLog.objects.create(
                server=server,
                status='failed',
                message="Failed to get inbounds from the panel",
            )
            return False
        
        # Track sync status
        success_count = 0
        failed_count = 0
        details = {
            'inbounds_synced': 0,
            'clients_synced': 0,
            'errors': []
        }
        
        # Process each inbound
        for inbound_data in inbounds_data:
            try:
                inbound_id = inbound_data.get('id')
                
                # Get or create inbound
                inbound, created = Inbound.objects.update_or_create(
                    server=server,
                    inbound_id=inbound_id,
                    defaults={
                        'protocol': inbound_data.get('protocol', ''),
                        'tag': inbound_data.get('remark', ''),
                        'port': inbound_data.get('port', 0),
                        'network': inbound_data.get('network', ''),
                        'enable': inbound_data.get('enable', True),
                        'listen': inbound_data.get('listen', ''),
                        'total': inbound_data.get('total', 0),
                        'remark': inbound_data.get('remark', ''),
                        'up': inbound_data.get('up', 0),
                        'down': inbound_data.get('down', 0),
                        'settings': inbound_data.get('settings', {}),
                        'stream_settings': inbound_data.get('streamSettings', {}),
                        'sniffing': inbound_data.get('sniffing', {}),
                    }
                )
                
                # Process clients
                if 'clientStats' in inbound_data:
                    for client_data in inbound_data['clientStats']:
                        try:
                            email = client_data.get('email', '')
                            
                            # Get or create client
                            client_obj, client_created = Client.objects.update_or_create(
                                inbound=inbound,
                                email=email,
                                defaults={
                                    'client_id': client_data.get('id', ''),
                                    'enable': client_data.get('enable', True),
                                    'total': client_data.get('total', 0),
                                    'up': client_data.get('up', 0),
                                    'down': client_data.get('down', 0),
                                    'expiry_time': datetime.fromtimestamp(client_data.get('expiryTime', 0) / 1000) if client_data.get('expiryTime', 0) > 0 else None,
                                }
                            )
                            
                            # Get client URL and create config
                            client_url = client.get_client_url(inbound_id, email)
                            if client_url:
                                ClientConfig.objects.update_or_create(
                                    client=client_obj,
                                    defaults={
                                        'vmess_link': client_url.get('vmess', ''),
                                        'vless_link': client_url.get('vless', ''),
                                        'trojan_link': client_url.get('trojan', ''),
                                        'shadowsocks_link': client_url.get('shadowsocks', ''),
                                        'subscription_url': client_url.get('subscription', ''),
                                        'qrcode_data': client_url.get('qrcode', ''),
                                    }
                                )
                            
                            details['clients_synced'] += 1
                            success_count += 1
                        except Exception as e:
                            failed_count += 1
                            details['errors'].append(f"Error syncing client {email}: {str(e)}")
                            logger.error(f"Error syncing client {email}: {str(e)}")
                
                details['inbounds_synced'] += 1
                success_count += 1
            except Exception as e:
                failed_count += 1
                details['errors'].append(f"Error syncing inbound {inbound_id}: {str(e)}")
                logger.error(f"Error syncing inbound {inbound_id}: {str(e)}")
        
        # Create sync log
        status = 'success'
        if failed_count > 0:
            status = 'partial' if success_count > 0 else 'failed'
        
        SyncLog.objects.create(
            server=server,
            status=status,
            message=f"Synced {details['inbounds_synced']} inbounds and {details['clients_synced']} clients",
            details=details,
        )
        
        return status == 'success'
    except Server.DoesNotExist:
        logger.error(f"Server with ID {server_id} does not exist or is not active")
        return False
    except Exception as e:
        logger.error(f"Error syncing server {server_id}: {str(e)}")
        return False


def create_client(subscription_id):
    """Create a client in 3x-UI for a subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        server = subscription.server
        client = ThreeXUIClient(server)
        
        # Get inbound details
        inbound = Inbound.objects.filter(server=server, protocol=subscription.plan.protocol).first()
        if not inbound:
            logger.error(f"No inbound found for server {server.id} with protocol {subscription.plan.protocol}")
            return False
        
        # Create client in 3x-UI
        email = f"{subscription.user.username}_{subscription.id}@v2ray.bot"
        traffic_limit_gb = subscription.data_limit_gb
        expiry_time = subscription.end_date
        
        result = client.add_client(inbound.inbound_id, email, traffic_limit_gb, expiry_time)
        if not result:
            logger.error(f"Failed to create client for subscription {subscription_id}")
            return False
        
        # Get client URL
        client_url = client.get_client_url(inbound.inbound_id, email)
        if not client_url:
            logger.error(f"Failed to get client URL for subscription {subscription_id}")
            return False
        
        # Create client in database
        client_obj = Client.objects.create(
            inbound=inbound,
            email=email,
            client_id=email,  # Use email as client ID for now
            enable=True,
            expiry_time=expiry_time,
            total=traffic_limit_gb * 1024 * 1024 * 1024 if traffic_limit_gb > 0 else 0,
            up=0,
            down=0,
        )
        
        # Create client config
        ClientConfig.objects.create(
            client=client_obj,
            vmess_link=client_url.get('vmess', ''),
            vless_link=client_url.get('vless', ''),
            trojan_link=client_url.get('trojan', ''),
            shadowsocks_link=client_url.get('shadowsocks', ''),
            subscription_url=client_url.get('subscription', ''),
            qrcode_data=client_url.get('qrcode', ''),
        )
        
        # Update subscription with client info
        subscription.inbound_id = inbound.inbound_id
        subscription.client_email = email
        subscription.client_config = client_url
        subscription.save()
        
        return True
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error creating client for subscription {subscription_id}: {str(e)}")
        return False


def delete_client(subscription_id):
    """Delete a client in 3x-UI for a subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        if not subscription.inbound_id or not subscription.client_email:
            logger.error(f"Subscription {subscription_id} has no inbound ID or client email")
            return False
        
        server = subscription.server
        client = ThreeXUIClient(server)
        
        # Delete client in 3x-UI
        result = client.remove_client(subscription.inbound_id, subscription.client_email)
        if not result:
            logger.error(f"Failed to delete client for subscription {subscription_id}")
            return False
        
        # Delete client in database
        Client.objects.filter(
            inbound__server=server,
            inbound__inbound_id=subscription.inbound_id,
            email=subscription.client_email
        ).delete()
        
        # Update subscription
        subscription.inbound_id = None
        subscription.client_email = None
        subscription.client_config = None
        subscription.save()
        
        return True
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error deleting client for subscription {subscription_id}: {str(e)}")
        return False


def update_client_traffic(subscription_id, traffic_limit_gb):
    """Update a client's traffic limit in 3x-UI"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        if not subscription.inbound_id or not subscription.client_email:
            logger.error(f"Subscription {subscription_id} has no inbound ID or client email")
            return False
        
        server = subscription.server
        client = ThreeXUIClient(server)
        
        # Update client in 3x-UI
        result = client.update_client_traffic(subscription.inbound_id, subscription.client_email, traffic_limit_gb)
        if not result:
            logger.error(f"Failed to update client traffic for subscription {subscription_id}")
            return False
        
        # Update client in database
        Client.objects.filter(
            inbound__server=server,
            inbound__inbound_id=subscription.inbound_id,
            email=subscription.client_email
        ).update(
            total=traffic_limit_gb * 1024 * 1024 * 1024 if traffic_limit_gb > 0 else 0
        )
        
        # Update subscription
        subscription.data_limit_gb = traffic_limit_gb
        subscription.save()
        
        return True
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error updating client traffic for subscription {subscription_id}: {str(e)}")
        return False


def update_client_expiry(subscription_id, expiry_time):
    """Update a client's expiry time in 3x-UI"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        if not subscription.inbound_id or not subscription.client_email:
            logger.error(f"Subscription {subscription_id} has no inbound ID or client email")
            return False
        
        server = subscription.server
        client = ThreeXUIClient(server)
        
        # Update client in 3x-UI
        result = client.update_client_expiry(subscription.inbound_id, subscription.client_email, expiry_time)
        if not result:
            logger.error(f"Failed to update client expiry for subscription {subscription_id}")
            return False
        
        # Update client in database
        Client.objects.filter(
            inbound__server=server,
            inbound__inbound_id=subscription.inbound_id,
            email=subscription.client_email
        ).update(
            expiry_time=expiry_time
        )
        
        # Update subscription
        subscription.end_date = expiry_time
        subscription.save()
        
        return True
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error updating client expiry for subscription {subscription_id}: {str(e)}")
        return False


def reset_client_traffic(subscription_id):
    """Reset a client's traffic usage in 3x-UI"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        if not subscription.inbound_id or not subscription.client_email:
            logger.error(f"Subscription {subscription_id} has no inbound ID or client email")
            return False
        
        server = subscription.server
        client = ThreeXUIClient(server)
        
        # Reset client in 3x-UI
        result = client.reset_client_traffic(subscription.inbound_id, subscription.client_email)
        if not result:
            logger.error(f"Failed to reset client traffic for subscription {subscription_id}")
            return False
        
        # Update client in database
        Client.objects.filter(
            inbound__server=server,
            inbound__inbound_id=subscription.inbound_id,
            email=subscription.client_email
        ).update(
            up=0,
            down=0
        )
        
        # Update subscription
        subscription.data_usage_gb = 0
        subscription.save()
        
        return True
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Error resetting client traffic for subscription {subscription_id}: {str(e)}")
        return False 