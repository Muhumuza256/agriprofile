from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class UserRole(models.TextChoices):
    SYSTEM_ADMIN = 'system_admin', 'System Administrator'
    FIELD_AGENT  = 'field_agent',  'Field Agent'
    SUPERVISOR   = 'supervisor',   'Field Supervisor'
    ANALYST      = 'analyst',      'Data Analyst'
    PARTNER_USER = 'partner_user', 'Partner Institution User'
    EXECUTIVE    = 'executive',    'Executive'


class User(AbstractUser):
    """
    Custom user model. All authentication goes through this model.
    Role determines API permission scope across the platform.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role            = models.CharField(max_length=20, choices=UserRole.choices)
    phone           = models.CharField(max_length=20, blank=True)
    district        = models.CharField(max_length=100, blank=True)
    organisation    = models.CharField(max_length=200, blank=True)
    is_active       = models.BooleanField(default=True)
    last_sync       = models.DateTimeField(null=True, blank=True)  # for field agents
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_field_agent(self):
        return self.role == UserRole.FIELD_AGENT

    @property
    def is_partner(self):
        return self.role == UserRole.PARTNER_USER

    @property
    def is_supervisor_or_above(self):
        return self.role in [
            UserRole.SUPERVISOR, UserRole.SYSTEM_ADMIN, UserRole.EXECUTIVE
        ]
