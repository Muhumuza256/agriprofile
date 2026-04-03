import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.models import User, UserRole
from .factories import UserFactory, AdminFactory, SupervisorFactory, PartnerFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def field_agent(db):
    return UserFactory(role=UserRole.FIELD_AGENT, password='testpass123')


@pytest.fixture
def admin_user(db):
    return AdminFactory(password='testpass123')


@pytest.fixture
def supervisor(db):
    return SupervisorFactory(password='testpass123')


@pytest.fixture
def partner(db):
    return PartnerFactory(password='testpass123')


@pytest.mark.django_db
class TestAuthentication:
    def test_login_returns_jwt_tokens(self, client, field_agent):
        response = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'testpass123',
        })
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_token_contains_role(self, client, field_agent):
        response = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'testpass123',
        })
        import jwt
        payload = jwt.decode(
            response.data['access'],
            options={"verify_signature": False}
        )
        assert payload['role'] == UserRole.FIELD_AGENT

    def test_invalid_credentials_returns_401(self, client, field_agent):
        response = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'wrongpassword',
        })
        assert response.status_code == 401

    def test_me_endpoint_returns_user_data(self, client, field_agent):
        login = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'testpass123',
        })
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = client.get('/api/auth/me/')
        assert response.status_code == 200
        assert response.data['role'] == UserRole.FIELD_AGENT

    def test_unauthenticated_request_returns_401(self, client):
        response = client.get('/api/auth/me/')
        assert response.status_code == 401

    def test_logout_blacklists_refresh_token(self, client, field_agent):
        login = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'testpass123',
        })
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        logout_response = client.post('/api/auth/logout/', {
            'refresh': login.data['refresh']
        })
        assert logout_response.status_code == 200

        # Reusing blacklisted refresh token should fail
        refresh_response = client.post('/api/auth/refresh/', {
            'refresh': login.data['refresh']
        })
        assert refresh_response.status_code == 401


@pytest.mark.django_db
class TestUserPermissions:
    def test_system_admin_can_create_users(self, client, admin_user):
        login = client.post('/api/auth/login/', {
            'username': admin_user.username,
            'password': 'testpass123',
        })
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = client.post('/api/users/', {
            'username': 'newagent',
            'email': 'newagent@test.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'role': UserRole.FIELD_AGENT,
            'password': 'securepass123',
            'confirm_password': 'securepass123',
        })
        assert response.status_code == 201

    def test_field_agent_cannot_create_users(self, client, field_agent):
        login = client.post('/api/auth/login/', {
            'username': field_agent.username,
            'password': 'testpass123',
        })
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = client.post('/api/users/', {
            'username': 'anotheruser',
            'role': UserRole.FIELD_AGENT,
            'password': 'testpass123',
            'confirm_password': 'testpass123',
        })
        assert response.status_code == 403

    def test_user_list_requires_authentication(self, client):
        response = client.get('/api/users/')
        assert response.status_code == 401
