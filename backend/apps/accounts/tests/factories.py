import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import User, UserRole


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@agriprofile.test')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = UserRole.FIELD_AGENT
    phone = factory.Faker('phone_number')
    district = factory.Faker('city')
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'testpass123')
        manager = cls._get_manager(model_class)
        user = manager.create_user(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminFactory(UserFactory):
    role = UserRole.SYSTEM_ADMIN
    username = factory.Sequence(lambda n: f'admin_{n}')


class SupervisorFactory(UserFactory):
    role = UserRole.SUPERVISOR
    username = factory.Sequence(lambda n: f'supervisor_{n}')


class PartnerFactory(UserFactory):
    role = UserRole.PARTNER_USER
    username = factory.Sequence(lambda n: f'partner_{n}')
    organisation = factory.Faker('company')
