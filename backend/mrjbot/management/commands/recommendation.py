from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ...models.recommendation import PlanRecommendation
from ...services.recommendation import RecommendationManager

User = get_user_model()

class Command(BaseCommand):
    help = 'Manage plan recommendations'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')

        # Generate recommendations
        generate_parser = subparsers.add_parser('generate', help='Generate recommendations')
        generate_parser.add_argument('username', type=str, help='Username')

        # List recommendations
        list_parser = subparsers.add_parser('list', help='List recommendations')
        list_parser.add_argument('username', type=str, help='Username')
        list_parser.add_argument('--all', action='store_true', help='Show all recommendations')

        # Record feedback
        feedback_parser = subparsers.add_parser('feedback', help='Record recommendation feedback')
        feedback_parser.add_argument('recommendation_id', type=int, help='Recommendation ID')
        feedback_parser.add_argument('--helpful', type=bool, help='Was recommendation helpful')
        feedback_parser.add_argument('--feedback', type=str, help='Feedback text')

        # Analyze usage
        analyze_parser = subparsers.add_parser('analyze', help='Analyze user usage pattern')
        analyze_parser.add_argument('username', type=str, help='Username')

    def handle(self, *args, **options):
        action = options['action']
        try:
            if action == 'generate':
                self._handle_generate(options)
            elif action == 'list':
                self._handle_list(options)
            elif action == 'feedback':
                self._handle_feedback(options)
            elif action == 'analyze':
                self._handle_analyze(options)
            else:
                raise CommandError('Invalid action')
        except Exception as e:
            raise CommandError(str(e))

    def _handle_generate(self, options):
        """Handle recommendation generation"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        recommendations = RecommendationManager.generate_recommendations(user)
        
        if not recommendations:
            self.stdout.write('No recommendations generated')
            return

        self.stdout.write(self.style.SUCCESS(
            f'Generated {len(recommendations)} recommendations:'
        ))
        for rec in recommendations:
            self.stdout.write(
                f'- {rec.recommended_plan.name} '
                f'(confidence: {rec.confidence_score:.2f})'
            )
            for reason in rec.reasons:
                self.stdout.write(f'  • {reason}')

    def _handle_list(self, options):
        """Handle recommendation listing"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        recommendations = RecommendationManager.get_user_recommendations(
            user,
            active_only=not options['all']
        )

        if not recommendations:
            self.stdout.write('No recommendations found')
            return

        self.stdout.write(f'Recommendations for {user.username}:')
        for rec in recommendations:
            status = '✅' if rec.is_accepted else '❌'
            self.stdout.write(
                f'{status} {rec.recommended_plan.name} '
                f'(confidence: {rec.confidence_score:.2f})'
            )
            if rec.feedback:
                helpful = '👍' if rec.feedback.is_helpful else '👎'
                self.stdout.write(f'  Feedback: {helpful}')

    def _handle_feedback(self, options):
        """Handle feedback recording"""
        try:
            recommendation = PlanRecommendation.objects.get(
                id=options['recommendation_id']
            )
        except PlanRecommendation.DoesNotExist:
            raise CommandError('Recommendation not found')

        feedback = RecommendationManager.record_feedback(
            recommendation=recommendation,
            is_helpful=options['helpful'],
            feedback_text=options.get('feedback')
        )

        self.stdout.write(self.style.SUCCESS(
            'Successfully recorded feedback'
        ))

    def _handle_analyze(self, options):
        """Handle usage pattern analysis"""
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User not found')

        pattern = RecommendationManager.analyze_usage_pattern(user)
        if not pattern:
            self.stdout.write('No usage data available')
            return

        self.stdout.write(f'Usage pattern for {user.username}:')
        self.stdout.write(f'Average daily traffic: {pattern.avg_daily_traffic:.2f} GB')
        self.stdout.write(f'Usage frequency: {pattern.usage_frequency} days/month')
        self.stdout.write(f'Connection stability: {pattern.connection_stability:.1f}%')
        
        if pattern.preferred_locations:
            self.stdout.write('Preferred locations:')
            for location in pattern.preferred_locations:
                self.stdout.write(f'  • {location}')

        peak_hour = max(pattern.peak_hours_usage.items(),
                       key=lambda x: int(x[1]))[0]
        self.stdout.write(f'Peak usage hour: {peak_hour}:00') 