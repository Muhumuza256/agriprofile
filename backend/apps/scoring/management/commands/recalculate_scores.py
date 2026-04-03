from django.core.management.base import BaseCommand
from apps.farmers.models import FarmerProfile
from apps.scoring.engine import ACSEngine


class Command(BaseCommand):
    help = 'Recalculate ACS scores for approved farmers'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Recalculate all approved farmers')
        parser.add_argument('--farmer', type=str, help='Recalculate a specific farmer UUID')

    def handle(self, *args, **options):
        if options['farmer']:
            qs = FarmerProfile.objects.filter(id=options['farmer'])
        elif options['all']:
            qs = FarmerProfile.objects.filter(is_active=True, submission_status='approved')
        else:
            self.stderr.write('Specify --all or --farmer <uuid>')
            return

        count = 0
        for farmer in qs:
            try:
                ACSEngine(farmer).calculate_and_save()
                count += 1
                self.stdout.write(f'  Scored: {farmer.full_name}')
            except Exception as e:
                self.stderr.write(f'  ERROR {farmer.full_name}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Recalculated {count} scores.'))
