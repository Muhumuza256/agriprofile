import factory
from factory.django import DjangoModelFactory
from apps.groups.models import FarmerGroup, GroupType, GroupLoanHistory
from apps.accounts.tests.factories import UserFactory


class FarmerGroupFactory(DjangoModelFactory):
    class Meta:
        model = FarmerGroup

    name            = factory.Sequence(lambda n: f'Bunyoro Farmers Group {n}')
    group_type      = GroupType.VSLA
    village         = factory.Faker('city')
    parish          = factory.Faker('city')
    sub_county      = factory.Faker('city')
    district        = 'Kampala'
    chairperson_name  = factory.Faker('name')
    chairperson_phone = factory.Faker('phone_number')
    registered_by   = factory.SubFactory(UserFactory)
    is_approved     = False
    is_registered   = False


class ApprovedGroupFactory(FarmerGroupFactory):
    is_approved = True


class GroupLoanHistoryFactory(DjangoModelFactory):
    class Meta:
        model = GroupLoanHistory

    group           = factory.SubFactory(FarmerGroupFactory)
    institution     = 'Centenary Bank Uganda'
    loan_amount_ugx = factory.Faker('pydecimal', left_digits=8, right_digits=2, positive=True)
    loan_date       = factory.Faker('date_object')
    purpose         = 'Input purchase'
    status          = 'repaid'
