import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from chatbot.models import ChatSession

# It's good practice to have a logger for management commands
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Deletes chat sessions and associated messages older than 7 days.'

    def handle(self, *args, **options):
        """
        The main logic of the management command.
        """
        self.stdout.write(self.style.NOTICE('Starting cleanup of old chat sessions...'))

        # Calculate the cutoff date for deletion
        cutoff_date = timezone.now() - timedelta(days=7)

        # Filter and delete old chat sessions
        # The related messages will be deleted automatically due to the CASCADE policy
        # specified in the ForeignKey of the ChatMessage model.
        try:
            old_sessions = ChatSession.objects.filter(created_at__lt=cutoff_date)
            session_count = old_sessions.count()

            if session_count > 0:
                old_sessions.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {session_count} old chat session(s).'))
            else:
                self.stdout.write(self.style.SUCCESS('No old chat sessions to delete.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred during cleanup: {e}'))
            logger.error(f'Error in cleanup_chats command: {e}', exc_info=True)

        self.stdout.write(self.style.NOTICE('Cleanup process finished.'))
