from datetime import datetime, timezone, timedelta
from django.core.management.base import BaseCommand
from config.db import get_db

class Command(BaseCommand):
    help = 'Run daily job updates: expire past deadlines and notify upcoming interviews'

    def handle(self, *args, **options):
        db = get_db()
        now = datetime.now(timezone.utc)

        self.stdout.write("Starting daily job updates...")

        # 1. Expire jobs
        expired_result = db.jobs.update_many(
            {'status': 'active', 'deadline': {'$lt': now}},
            {'$set': {'status': 'expired'}}
        )
        self.stdout.write(self.style.SUCCESS(f'Expired {expired_result.modified_count} jobs past their deadline.'))

        # 2. Upcoming Interview Notifications
        tomorrow_start = now + timedelta(days=1)
        tomorrow_start = tomorrow_start.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)

        interviews = list(db.interviews.find({
            'date': {'$gte': tomorrow_start, '$lt': tomorrow_end}
        }))

        notif_count = 0
        for iv in interviews:
            existing_notif = db.notifications.find_one({
                'user_id': iv['user_id'],
                'type': 'interview_reminder',
                'interview_id': str(iv['_id'])
            })

            if not existing_notif:
                role = iv.get('role', 'Unknown Role')
                company = iv.get('company', 'Unknown Company')
                time_str = iv.get('time', '')
                time_clause = f" at {time_str}" if time_str else ""
                
                db.notifications.insert_one({
                    'user_id': iv['user_id'],
                    'title': 'Upcoming Interview Reminder',
                    'message': f'Reminder: You have an interview for {role} at {company} tomorrow{time_clause}.',
                    'type': 'interview_reminder',
                    'interview_id': str(iv['_id']),
                    'is_read': False,
                    'created_at': now
                })
                notif_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Created {notif_count} interview reminders for tomorrow.'))
        self.stdout.write(self.style.SUCCESS("Daily job updates completed successfully."))
