# 3x-UI Integration Guide

This guide explains how our system integrates with multiple 3x-UI panels for managing V2Ray accounts.

## Introduction to 3x-UI

[3x-UI](https://github.com/MHSanaei/3x-ui) is a popular web panel for managing V2Ray servers. It provides a user-friendly interface and API for creating, managing, and monitoring V2Ray accounts.

Our system connects to one or more 3x-UI panels to:
1. Create new V2Ray accounts
2. Manage existing accounts
3. Monitor traffic usage
4. Track account expiration
5. Generate connection configurations

## API Integration

### Authentication

Our system authenticates with 3x-UI panels using session-based authentication:

1. **Login**: We send a POST request to the login endpoint with admin credentials
2. **Session Management**: We store session cookies securely in our database
3. **Session Renewal**: We automatically renew sessions before they expire

### Configuration

To configure 3x-UI panel integration:

1. Add panel details in the `.env` file:
   ```
   XUI_PANEL_URL=http://your-panel-url
   XUI_PANEL_USERNAME=admin
   XUI_PANEL_PASSWORD=your_secure_password
   ```

2. For multiple panels, configure them through the admin dashboard:
   - Go to "Panel Management" in the admin dashboard
   - Add each panel with its URL, username, and password
   - Set panel priority for account creation

### API Endpoints Used

Our system uses the following 3x-UI API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/login` | Authentication |
| `/panel/api/inbounds` | Get list of inbounds |
| `/panel/api/inbounds/add` | Create a new inbound |
| `/panel/api/inbounds/update/:id` | Update an existing inbound |
| `/panel/api/inbounds/del/:id` | Delete an inbound |
| `/panel/api/inbounds/getClientTraffics/:id` | Get client traffic stats |
| `/panel/api/inbounds/addClient` | Add a client to an inbound |
| `/panel/api/inbounds/delClient/:id/:clientId` | Remove a client |
| `/panel/api/server/status` | Get server status information |

### Account Creation Flow

When a user purchases a new account:

1. The system selects an appropriate 3x-UI panel based on:
   - Panel priority
   - Server load
   - Available capacity

2. The system selects an inbound on the panel based on:
   - Protocol requested (VMess, VLESS, Trojan, etc.)
   - Server location preference
   - Load balancing

3. A unique client is created with:
   - Random UUID
   - Email based on username
   - Traffic and expiry limits as per the plan

4. The configuration is generated and delivered to the user

### Traffic Synchronization

Our system regularly synchronizes traffic data from all connected panels:

1. Scheduled job runs every 15 minutes
2. Fetches traffic data for all clients across all panels
3. Updates the local database with current usage
4. Checks for accounts that have reached traffic limits
5. Notifies users about accounts approaching limits

### Error Handling

The integration includes robust error handling:

1. **Connection Issues**:
   - Automatic retry with exponential backoff
   - Fallback to alternative panels when available
   - Alert administrators about persistent failures

2. **Authentication Failures**:
   - Automatic session renewal
   - Credential validation check
   - Secure storage of credentials

3. **API Changes**:
   - Version checking
   - Flexible response parsing
   - Adaptation to API updates

## Administration

Administrators can manage 3x-UI panel integration through:

1. **Panel Dashboard**:
   - View all connected panels
   - Monitor panel status
   - See load distribution

2. **Panel Settings**:
   - Add/remove panels
   - Update credentials
   - Configure load balancing

3. **Troubleshooting Tools**:
   - Test panel connectivity
   - View API response logs
   - Force resynchronization

## Troubleshooting

Common issues and solutions:

1. **Panel Connection Failures**:
   - Verify panel URL is accessible
   - Check credentials are correct
   - Ensure no firewall blocking connections

2. **Account Creation Issues**:
   - Verify inbound exists and is properly configured
   - Check if panel has reached capacity
   - Ensure required protocols are enabled

3. **Traffic Data Discrepancies**:
   - Force a manual synchronization
   - Check time synchronization between servers
   - Verify database integrity

## Security Considerations

Important security aspects of our integration:

1. Credentials are stored encrypted in the database
2. All API communications use HTTPS when available
3. Session cookies are securely stored
4. IP-based access restrictions can be configured
5. Regular session rotation prevents unauthorized access 