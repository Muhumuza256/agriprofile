import django
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    pass


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(db):
    """APIClient pre-authenticated as a field agent."""
    from rest_framework.test import APIClient
    from apps.accounts.tests.factories import UserFactory
    from apps.accounts.models import UserRole
    client = APIClient()
    user = UserFactory(role=UserRole.FIELD_AGENT, password='testpass123')
    client.force_authenticate(user=user)
    client._user = user
    return client


@pytest.fixture
def admin_client(db):
    """APIClient pre-authenticated as a system admin."""
    from rest_framework.test import APIClient
    from apps.accounts.tests.factories import AdminFactory
    client = APIClient()
    user = AdminFactory(password='testpass123')
    client.force_authenticate(user=user)
    client._user = user
    return client


@pytest.fixture
def supervisor_client(db):
    from rest_framework.test import APIClient
    from apps.accounts.tests.factories import SupervisorFactory
    client = APIClient()
    user = SupervisorFactory(password='testpass123')
    client.force_authenticate(user=user)
    client._user = user
    return client
