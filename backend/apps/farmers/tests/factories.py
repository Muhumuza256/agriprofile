import factory
from factory.django import DjangoModelFactory
from apps.farmers.models import FarmerProfile, FarmerAsset, FarmerCrop
from apps.groups.tests.factories import FarmerGroupFactory
from apps.accounts.tests.factories import UserFactory


class FarmerProfileFactory(DjangoModelFactory):
    class Meta:
        model = FarmerProfile

    group         = factory.SubFactory(FarmerGroupFactory)
    full_name     = factory.Faker('name')
    national_id   = factory.Sequence(lambda n: f'CM{n:09d}')
    gender        = 'female'
    primary_phone = factory.Faker('phone_number')
    village       = factory.Faker('city')
    parish        = factory.Faker('city')
    sub_county    = factory.Faker('city')
    district      = 'Kampala'
    next_of_kin_name  = factory.Faker('name')
    next_of_kin_phone = factory.Faker('phone_number')
    household_size    = 4
    dependants        = 2
    working_age_adults = 2
    farm_labour_available = 2
    field_agent       = factory.SubFactory(UserFactory)
    submission_status = 'pending'
    is_active         = True


class FarmerAssetFactory(DjangoModelFactory):
    class Meta:
        model = FarmerAsset

    farmer                = factory.SubFactory(FarmerProfileFactory)
    owns_hand_tools       = True
    has_storage_structure = False
    cattle_count          = 2


class FarmerCropFactory(DjangoModelFactory):
    class Meta:
        model = FarmerCrop

    farmer                   = factory.SubFactory(FarmerProfileFactory)
    crop_name                = 'Maize'
    crop_category            = 'both'
    season                   = 'season_a'
    planting_month           = 3
    harvest_month            = 7
    acreage                  = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=1, max_value=5)
    seed_source              = 'certified'
    uses_inputs              = True
    expected_yield_kg_per_acre = 1200
    sell_to                  = 'local_market'
    seasons_farmed           = 2
    post_harvest_loss_pct    = 15
