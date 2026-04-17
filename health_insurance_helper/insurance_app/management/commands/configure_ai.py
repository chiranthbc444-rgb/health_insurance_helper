from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Configure OpenAI API key for AI chatbot functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--key',
            type=str,
            help='OpenAI API key to set',
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show current API key status',
        )

    def handle(self, *args, **options):
        settings_file = os.path.join(settings.BASE_DIR, 'insurance_project', 'settings.py')

        if options['show']:
            current_key = getattr(settings, 'OPENAI_API_KEY', 'Not set')
            if current_key == 'your-openai-api-key-here':
                self.stdout.write(self.style.WARNING('OpenAI API key is set to placeholder value'))
            elif current_key and current_key != 'your-openai-api-key-here':
                self.stdout.write(self.style.SUCCESS('OpenAI API key is configured'))
            else:
                self.stdout.write(self.style.ERROR('OpenAI API key is not set'))
            return

        if options['key']:
            api_key = options['key']

            # Read current settings
            with open(settings_file, 'r') as f:
                content = f.read()

            # Replace the placeholder
            old_line = "OPENAI_API_KEY = 'your-openai-api-key-here'  # Replace with actual key"
            new_line = f"OPENAI_API_KEY = '{api_key}'  # Replace with actual key"

            if old_line in content:
                content = content.replace(old_line, new_line)

                # Write back to file
                with open(settings_file, 'w') as f:
                    f.write(content)

                self.stdout.write(self.style.SUCCESS('OpenAI API key configured successfully!'))
                self.stdout.write('Please restart the Django server for changes to take effect.')
            else:
                self.stdout.write(self.style.ERROR('Could not find API key placeholder in settings.py'))
        else:
            self.stdout.write(self.style.WARNING('Usage:'))
            self.stdout.write('  python manage.py configure_ai --key YOUR_API_KEY')
            self.stdout.write('  python manage.py configure_ai --show')