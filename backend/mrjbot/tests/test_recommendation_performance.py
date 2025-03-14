from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import time
import random

from ..models.recommendation import UserUsagePattern, PlanRecommendation
from ..models.subscription import Plan, Subscription
from ..services.recommendation import RecommendationManager

User = get_user_model()

class RecommendationPerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create test users
        cls.users = []
        for i in range(100):  # Create 100 test users
            user = User.objects.create_user(
                username=f'testuser{i}',
                password='testpass123'
            )
            cls.users.append(user)

        # Create test plans
        cls.plans = []
        traffic_options = [50, 100, 200, 500]  # GB
        price_options = [100000, 180000, 300000, 500000]  # Toman
        locations = ['IR', 'TR', 'DE', 'NL', 'FR', 'US', 'GB', 'JP']
        
        for i in range(10):  # Create 10 different plans
            available_locs = random.sample(locations, random.randint(3, len(locations)))
            plan = Plan.objects.create(
                name=f'Plan{i}',
                monthly_traffic=random.choice(traffic_options),
                price=random.choice(price_options),
                is_active=True,
                available_locations=available_locs
            )
            cls.plans.append(plan)

        # Create subscriptions with varying usage patterns
        for user in cls.users:
            plan = random.choice(cls.plans)
            Subscription.objects.create(
                user=user,
                plan=plan,
                status='ACTIVE',
                daily_traffic=random.uniform(0.5, 5.0),
                connection_stability=random.uniform(80, 100),
                server_country=random.choice(plan.available_locations)
            )

    def test_bulk_pattern_analysis_performance(self):
        """Test performance of analyzing patterns for multiple users"""
        start_time = time.time()
        
        for user in self.users[:10]:  # Test with first 10 users
            pattern = RecommendationManager.analyze_usage_pattern(user)
            self.assertIsNotNone(pattern)
        
        duration = time.time() - start_time
        self.assertLess(duration, 2.0)  # Should take less than 2 seconds for 10 users
        
        # Test bulk analysis
        start_time = time.time()
        for user in self.users:  # Test all users
            pattern = RecommendationManager.analyze_usage_pattern(user)
            self.assertIsNotNone(pattern)
        
        duration = time.time() - start_time
        self.assertLess(duration, 15.0)  # Should take less than 15 seconds for 100 users

    def test_recommendation_generation_performance(self):
        """Test performance of generating recommendations"""
        # First, create usage patterns
        for user in self.users:
            UserUsagePattern.objects.create(
                user=user,
                avg_daily_traffic=random.uniform(0.5, 5.0),
                peak_hours_usage={str(h): random.randint(0, 20) for h in range(24)},
                preferred_locations=random.sample(['IR', 'TR', 'DE', 'NL'], 2),
                connection_stability=random.uniform(80, 100),
                usage_frequency=random.randint(15, 30)
            )

        # Test single user recommendation performance
        start_time = time.time()
        recommendations = RecommendationManager.generate_recommendations(self.users[0])
        duration = time.time() - start_time
        self.assertLess(duration, 1.0)  # Should take less than 1 second for single user
        
        # Test bulk recommendation performance
        start_time = time.time()
        for user in self.users[:10]:  # Test with first 10 users
            recommendations = RecommendationManager.generate_recommendations(user)
        duration = time.time() - start_time
        self.assertLess(duration, 5.0)  # Should take less than 5 seconds for 10 users

    def test_recommendation_retrieval_performance(self):
        """Test performance of retrieving recommendations"""
        # Create test recommendations
        for user in self.users:
            for _ in range(3):  # 3 recommendations per user
                PlanRecommendation.objects.create(
                    user=user,
                    recommended_plan=random.choice(self.plans),
                    current_plan=random.choice(self.plans),
                    confidence_score=random.uniform(0.6, 1.0),
                    reasons=['Test reason'],
                    expires_at=timezone.now() + timedelta(days=random.randint(-5, 5))
                )

        # Test single user retrieval performance
        start_time = time.time()
        recommendations = RecommendationManager.get_user_recommendations(self.users[0])
        duration = time.time() - start_time
        self.assertLess(duration, 0.1)  # Should take less than 0.1 seconds
        
        # Test bulk retrieval performance
        start_time = time.time()
        for user in self.users:
            recommendations = RecommendationManager.get_user_recommendations(user)
        duration = time.time() - start_time
        self.assertLess(duration, 2.0)  # Should take less than 2 seconds for all users 