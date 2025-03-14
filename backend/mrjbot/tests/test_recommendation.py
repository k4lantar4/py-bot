from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

from ..models.recommendation import UserUsagePattern, PlanRecommendation, RecommendationFeedback
from ..models.subscription import Plan, Subscription
from ..services.recommendation import RecommendationManager

User = get_user_model()

class RecommendationTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test plans
        self.basic_plan = Plan.objects.create(
            name='Basic',
            monthly_traffic=50,  # 50GB
            price=100000,
            is_active=True,
            available_locations=['IR', 'TR', 'DE']
        )
        
        self.premium_plan = Plan.objects.create(
            name='Premium',
            monthly_traffic=100,  # 100GB
            price=180000,
            is_active=True,
            available_locations=['IR', 'TR', 'DE', 'NL', 'FR']
        )
        
        # Create test subscription
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            status='ACTIVE',
            daily_traffic=1.5,  # 1.5GB daily average
            connection_stability=95,
            server_country='IR'
        )

    def test_analyze_usage_pattern(self):
        """Test usage pattern analysis"""
        pattern = RecommendationManager.analyze_usage_pattern(self.user)
        
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.user, self.user)
        self.assertGreaterEqual(pattern.avg_daily_traffic, 0)
        self.assertIsInstance(pattern.peak_hours_usage, dict)
        self.assertIsInstance(pattern.preferred_locations, list)
        self.assertGreaterEqual(pattern.connection_stability, 0)
        self.assertLessEqual(pattern.connection_stability, 100)

    def test_generate_recommendations(self):
        """Test recommendation generation"""
        recommendations = RecommendationManager.generate_recommendations(self.user)
        
        self.assertIsInstance(recommendations, list)
        if recommendations:  # If recommendations were generated
            recommendation = recommendations[0]
            self.assertIsInstance(recommendation, PlanRecommendation)
            self.assertEqual(recommendation.user, self.user)
            self.assertIsNotNone(recommendation.confidence_score)
            self.assertIsInstance(recommendation.reasons, list)
            self.assertFalse(recommendation.is_accepted)

    def test_calculate_plan_fit(self):
        """Test plan fit calculation"""
        pattern = UserUsagePattern.objects.create(
            user=self.user,
            avg_daily_traffic=1.5,
            peak_hours_usage={'12': 10, '13': 15},
            preferred_locations=['IR', 'TR'],
            connection_stability=95,
            usage_frequency=25
        )
        
        score, reasons = RecommendationManager._calculate_plan_fit(pattern, self.premium_plan)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        self.assertIsInstance(reasons, list)
        self.assertTrue(len(reasons) > 0)

    def test_record_feedback(self):
        """Test recommendation feedback recording"""
        recommendation = PlanRecommendation.objects.create(
            user=self.user,
            recommended_plan=self.premium_plan,
            current_plan=self.basic_plan,
            confidence_score=0.85,
            reasons=['Good value', 'More locations'],
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        feedback = RecommendationManager.record_feedback(
            recommendation=recommendation,
            is_helpful=True,
            feedback_text='Great suggestion!'
        )
        
        self.assertIsInstance(feedback, RecommendationFeedback)
        self.assertEqual(feedback.recommendation, recommendation)
        self.assertTrue(feedback.is_helpful)
        self.assertEqual(feedback.feedback_text, 'Great suggestion!')

    def test_get_user_recommendations(self):
        """Test retrieving user recommendations"""
        # Create some test recommendations
        active_rec = PlanRecommendation.objects.create(
            user=self.user,
            recommended_plan=self.premium_plan,
            current_plan=self.basic_plan,
            confidence_score=0.85,
            reasons=['Good value'],
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        expired_rec = PlanRecommendation.objects.create(
            user=self.user,
            recommended_plan=self.premium_plan,
            current_plan=self.basic_plan,
            confidence_score=0.75,
            reasons=['More traffic'],
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Test active only recommendations
        active_recommendations = RecommendationManager.get_user_recommendations(
            self.user,
            active_only=True
        )
        self.assertEqual(len(active_recommendations), 1)
        self.assertEqual(active_recommendations[0], active_rec)
        
        # Test all recommendations
        all_recommendations = RecommendationManager.get_user_recommendations(
            self.user,
            active_only=False
        )
        self.assertEqual(len(all_recommendations), 2) 