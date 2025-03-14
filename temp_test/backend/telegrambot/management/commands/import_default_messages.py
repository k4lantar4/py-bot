import os
from django.core.management.base import BaseCommand
from telegram.models import TelegramMessage
from telegram.default_messages import default_messages

class Command(BaseCommand):
    help = 'Import default Telegram messages into the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing messages',
        )
    
    def handle(self, *args, **options):
        overwrite = options['overwrite']
        count_created = 0
        count_updated = 0
        count_skipped = 0
        
        for name, translations in default_messages.items():
            for lang_code, content in translations.items():
                # Check if message already exists
                try:
                    message = TelegramMessage.objects.get(name=name, language_code=lang_code)
                    
                    # Update if overwrite flag is set
                    if overwrite:
                        message.content = content
                        message.save()
                        count_updated += 1
                        self.stdout.write(self.style.WARNING(f"Updated message: {name} ({lang_code})"))
                    else:
                        count_skipped += 1
                        self.stdout.write(self.style.WARNING(f"Skipped existing message: {name} ({lang_code})"))
                        
                except TelegramMessage.DoesNotExist:
                    # Create new message
                    TelegramMessage.objects.create(
                        name=name,
                        content=content,
                        language_code=lang_code
                    )
                    count_created += 1
                    self.stdout.write(self.style.SUCCESS(f"Created message: {name} ({lang_code})"))
        
        self.stdout.write(self.style.SUCCESS(f"Import complete. Created: {count_created}, Updated: {count_updated}, Skipped: {count_skipped}")) 