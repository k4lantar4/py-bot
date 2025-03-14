from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class ServerLocation(models.Model):
    """Model for managing VPN server locations"""
    
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("maintenance", _("Maintenance")),
        ("inactive", _("Inactive")),
        ("overloaded", _("Overloaded")),
    ]

    name = models.CharField(_("Name"), max_length=100)  # e.g., "MoonVpn-France-1000-1"
    country = models.CharField(_("Country"), max_length=50)  # e.g., "France"
    city = models.CharField(_("City"), max_length=50, blank=True)  # e.g., "Paris"
    capacity = models.IntegerField(
        _("Capacity"), 
        validators=[MinValueValidator(1), MaxValueValidator(10000)]
    )
    current_load = models.IntegerField(_("Current Load"), default=0)
    status = models.CharField(
        _("Status"), 
        max_length=20, 
        choices=STATUS_CHOICES,
        default="active"
    )
    
    # Server details
    ip_address = models.GenericIPAddressField(_("IP Address"))
    port = models.IntegerField(_("Port"))
    panel_url = models.URLField(_("Panel URL"))
    panel_type = models.CharField(
        _("Panel Type"),
        max_length=20,
        choices=[("3x-ui", "3x-UI"), ("x-ui", "X-UI")],
        default="3x-ui"
    )
    
    # Performance metrics
    latency = models.FloatField(_("Latency (ms)"), default=0)
    uptime = models.FloatField(_("Uptime %"), default=100)
    bandwidth_usage = models.FloatField(_("Bandwidth Usage %"), default=0)
    
    # Load balancing
    weight = models.IntegerField(
        _("Load Balancing Weight"),
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    max_connections = models.IntegerField(_("Max Connections"), default=1000)
    
    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    last_checked = models.DateTimeField(_("Last Checked"), auto_now=True)

    class Meta:
        verbose_name = _("Server Location")
        verbose_name_plural = _("Server Locations")
        ordering = ["country", "name"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    def update_load(self, connections: int):
        """Update server load based on current connections"""
        self.current_load = connections
        if connections >= self.max_connections:
            self.status = "overloaded"
        elif self.status == "overloaded" and connections < self.max_connections:
            self.status = "active"
        self.save()

    def update_metrics(self, latency: float, uptime: float, bandwidth: float):
        """Update server performance metrics"""
        self.latency = latency
        self.uptime = uptime
        self.bandwidth_usage = bandwidth
        self.save()

    @property
    def load_percentage(self) -> float:
        """Calculate current load percentage"""
        return (self.current_load / self.max_connections) * 100

    @property
    def is_available(self) -> bool:
        """Check if server is available for new connections"""
        return (
            self.status == "active" and
            self.current_load < self.max_connections and
            self.uptime >= 95
        )

class LocationGroup(models.Model):
    """Group of server locations for load balancing"""
    
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    locations = models.ManyToManyField(
        ServerLocation,
        related_name="groups",
        verbose_name=_("Locations")
    )
    is_active = models.BooleanField(_("Active"), default=True)
    
    # Load balancing strategy
    STRATEGY_CHOICES = [
        ("round_robin", _("Round Robin")),
        ("least_connections", _("Least Connections")),
        ("weighted", _("Weighted")),
        ("latency", _("Best Latency")),
    ]
    
    strategy = models.CharField(
        _("Load Balancing Strategy"),
        max_length=20,
        choices=STRATEGY_CHOICES,
        default="least_connections"
    )
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Location Group")
        verbose_name_plural = _("Location Groups")

    def __str__(self):
        return self.name

    def get_next_server(self) -> ServerLocation:
        """Get next available server based on strategy"""
        available_servers = [s for s in self.locations.all() if s.is_available]
        
        if not available_servers:
            raise ValueError("No available servers in group")
            
        if self.strategy == "round_robin":
            return available_servers[0]  # Simple round-robin
        elif self.strategy == "least_connections":
            return min(available_servers, key=lambda s: s.current_load)
        elif self.strategy == "weighted":
            # Weighted random selection based on server weights
            total_weight = sum(s.weight for s in available_servers)
            import random
            r = random.uniform(0, total_weight)
            upto = 0
            for server in available_servers:
                upto += server.weight
                if upto >= r:
                    return server
        else:  # Best latency
            return min(available_servers, key=lambda s: s.latency) 