from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Manually trigger weather fetch for farm plots'

    def add_arguments(self, parser):
        parser.add_argument('--all-plots', action='store_true', help='Fetch for all active plots')
        parser.add_argument('--plot', type=str, help='Fetch for a specific plot UUID')

    def handle(self, *args, **options):
        from apps.weather.tasks import fetch_weather_for_plot, fetch_weather_for_all_active_plots

        if options['plot']:
            result = fetch_weather_for_plot(options['plot'])
            self.stdout.write(str(result))
        elif options['all_plots']:
            result = fetch_weather_for_all_active_plots()
            self.stdout.write(self.style.SUCCESS(f"Queued weather fetch for {result['queued']} plots."))
        else:
            self.stderr.write('Specify --all-plots or --plot <uuid>')
