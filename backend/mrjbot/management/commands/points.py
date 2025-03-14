from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...models.points import PointsConfig, Reward
from ...services.points import PointsManager

User = get_user_model()

class Command(BaseCommand):
    help = 'Manage user points and rewards'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')

        # Award points
        award_parser = subparsers.add_parser('award', help='Award points to a user')
        award_parser.add_argument('username', type=str, help='Username')
        award_parser.add_argument('points', type=int, help='Number of points')
        award_parser.add_argument('--action', type=str, help='Action identifier')
        award_parser.add_argument('--description', type=str, help='Description')
        award_parser.add_argument('--reference', type=str, help='Reference')

        # Deduct points
        deduct_parser = subparsers.add_parser('deduct', help='Deduct points from a user')
        deduct_parser.add_argument('username', type=str, help='Username')
        deduct_parser.add_argument('points', type=int, help='Number of points')
        deduct_parser.add_argument('reason', type=str, help='Reason for deduction')

        # Create reward
        create_parser = subparsers.add_parser('create-reward', help='Create a new reward')
        create_parser.add_argument('name', type=str, help='Reward name')
        create_parser.add_argument('description', type=str, help='Reward description')
        create_parser.add_argument('points', type=int, help='Points required')
        create_parser.add_argument('--type', type=str, choices=['DISCOUNT', 'TRAFFIC', 'TIME', 'VIP', 'CUSTOM'],
                                 default='CUSTOM', help='Reward type')
        create_parser.add_argument('--quantity', type=int, help='Available quantity')
        create_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        create_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
        create_parser.add_argument('--data', type=str, help='JSON data for reward')

        # List rewards
        list_parser = subparsers.add_parser('list-rewards', help='List available rewards')
        list_parser.add_argument('--active-only', action='store_true', help='Show only active rewards')

        # Show user points
        show_parser = subparsers.add_parser('show', help='Show user points')
        show_parser.add_argument('username', type=str, help='Username')

        # Configure points
        config_parser = subparsers.add_parser('configure', help='Configure points for actions')
        config_parser.add_argument('action', type=str, help='Action identifier')
        config_parser.add_argument('points', type=int, help='Points for action')
        config_parser.add_argument('description', type=str, help='Description')
        config_parser.add_argument('--cooldown', type=int, help='Cooldown in minutes')
        config_parser.add_argument('--max-daily', type=int, help='Maximum daily points')

    def handle(self, *args, **options):
        action = options['action']
        try:
            if action == 'award':
                self._handle_award(options)
            elif action == 'deduct':
                self._handle_deduct(options)
            elif action == 'create-reward':
                self._handle_create_reward(options)
            elif action == 'list-rewards':
                self._handle_list_rewards(options)
            elif action == 'show':
                self._handle_show(options)
            elif action == 'configure':
                self._handle_configure(options)
            else:
                raise CommandError('Invalid action')
        except Exception as e:
            raise CommandError(str(e))

    def _handle_award(self, options):
        """Handle points award"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        transaction = PointsManager.award_points(
            user=user,
            points=options['points'],
            action=options.get('action', 'manual_award'),
            description=options.get('description'),
            reference=options.get('reference')
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully awarded {transaction.points} points to {user.username}'
        ))

    def _handle_deduct(self, options):
        """Handle points deduction"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        transaction = PointsManager.deduct_points(
            user=user,
            points=options['points'],
            reason=options['reason']
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deducted {transaction.points} points from {user.username}'
        ))

    def _handle_create_reward(self, options):
        """Handle reward creation"""
        try:
            import json
            reward_data = json.loads(options.get('data', '{}'))
        except json.JSONDecodeError:
            raise CommandError('Invalid JSON data')

        start_date = None
        if options.get('start_date'):
            try:
                start_date = timezone.datetime.strptime(
                    options['start_date'], '%Y-%m-%d'
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                raise CommandError('Invalid start date format. Use YYYY-MM-DD')

        end_date = None
        if options.get('end_date'):
            try:
                end_date = timezone.datetime.strptime(
                    options['end_date'], '%Y-%m-%d'
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                raise CommandError('Invalid end date format. Use YYYY-MM-DD')

        reward = Reward.objects.create(
            name=options['name'],
            description=options['description'],
            points_required=options['points'],
            reward_type=options['type'],
            quantity_available=options.get('quantity'),
            start_date=start_date,
            end_date=end_date,
            reward_data=reward_data
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created reward "{reward.name}"'
        ))

    def _handle_list_rewards(self, options):
        """Handle rewards listing"""
        rewards = Reward.objects.all()
        if options.get('active_only'):
            rewards = rewards.filter(is_active=True)

        self.stdout.write('Available rewards:')
        for reward in rewards:
            status = '✅' if reward.is_available() else '❌'
            quantity = reward.quantity_available or 'unlimited'
            self.stdout.write(
                f'{status} {reward.name} ({reward.points_required} points) - '
                f'Type: {reward.reward_type}, Quantity: {quantity}'
            )

    def _handle_show(self, options):
        """Handle showing user points"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        summary = PointsManager.get_user_points_summary(user)
        self.stdout.write(f'Points summary for {user.username}:')
        self.stdout.write(f'Current balance: {summary["current_balance"]} points')
        self.stdout.write(f'Total earned: {summary["total_earned"]} points')
        self.stdout.write(f'Total spent: {summary["total_spent"]} points')
        self.stdout.write(f'Expiring soon: {summary["expiring_soon"]} points')
        
        if summary['recent_transactions']:
            self.stdout.write('\nRecent transactions:')
            for t in summary['recent_transactions']:
                self.stdout.write(
                    f'- {t["type"]}: {t["points"]} points - {t["description"]} '
                    f'({t["date"].strftime("%Y-%m-%d %H:%M")})'
                )

    def _handle_configure(self, options):
        """Handle points configuration"""
        config, created = PointsConfig.objects.update_or_create(
            action=options['action'],
            defaults={
                'points': options['points'],
                'description': options['description'],
                'cooldown_minutes': options.get('cooldown', 0),
                'max_daily': options.get('max_daily')
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully {"created" if created else "updated"} points configuration '
            f'for action "{config.action}"'
        )) 