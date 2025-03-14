from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class AIContent(models.Model):
    TOPIC_CHOICES = [
        ("new_features", _("New Features")),
        ("special_offer", _("Special Offer")),
        ("tech_news", _("Tech News")),
    ]
    
    STATUS_CHOICES = [
        ("pending", _("Pending Review")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("published", _("Published")),
    ]
    
    content = models.TextField(_("Content"))
    topic = models.CharField(_("Topic"), max_length=50, choices=TOPIC_CHOICES)
    language = models.CharField(_("Language"), max_length=2, choices=[("fa", "Persian"), ("en", "English")])
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    
    approved_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_contents"
    )
    
    telegram_message_id = models.CharField(_("Telegram Message ID"), max_length=50, null=True, blank=True)
    performance_metrics = models.JSONField(_("Performance Metrics"), default=dict, blank=True)
    
    class Meta:
        verbose_name = _("AI Content")
        verbose_name_plural = _("AI Contents")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.get_topic_display()} - {self.language} - {self.status}"
    
    def approve(self, user):
        """Approve content for publishing"""
        self.status = "approved"
        self.approved_by = user
        self.save()
    
    def publish_to_telegram(self):
        """Publish content to Telegram channel"""
        from mrjbot.services.telegram import send_channel_message
        
        if self.status != "approved":
            raise ValueError("Content must be approved before publishing")
        
        message_id = send_channel_message(self.content)
        self.telegram_message_id = message_id
        self.status = "published"
        self.published_at = timezone.now()
        self.save()
    
    def update_metrics(self, views: int = 0, reactions: int = 0):
        """Update content performance metrics"""
        self.performance_metrics.update({
            "views": views,
            "reactions": reactions,
            "last_updated": timezone.now().isoformat()
        })
        self.save() 