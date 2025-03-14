import os
from typing import List, Optional
import openai
from datetime import datetime
from django.conf import settings
from celery import shared_task

class AIContentGenerator:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key

    async def generate_promotional_post(self, topic: str, language: str = "fa") -> str:
        """Generate promotional content for Telegram channel"""
        prompt = self._get_promotional_prompt(topic, language)
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative marketing expert for a VPN service."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content

    def _get_promotional_prompt(self, topic: str, language: str) -> str:
        prompts = {
            "new_features": {
                "fa": "یک پست تبلیغاتی جذاب برای ویژگی‌های جدید سرویس VPN ما بنویسید. از ایموجی استفاده کنید و لحن دوستانه داشته باشید.",
                "en": "Write an engaging promotional post about our VPN service's new features. Use emojis and maintain a friendly tone."
            },
            "special_offer": {
                "fa": "یک پیشنهاد ویژه برای کاربران VPN با تخفیف و مزایای خاص بنویسید. از ایموجی استفاده کنید و احساس فوریت ایجاد کنید.",
                "en": "Write a special VPN offer with discounts and benefits. Use emojis and create urgency."
            },
            "tech_news": {
                "fa": "یک خبر تکنولوژی مرتبط با امنیت و VPN بنویسید. از ایموجی استفاده کنید و به زبان ساده توضیح دهید.",
                "en": "Write a tech news piece related to security and VPN. Use emojis and explain in simple terms."
            }
        }
        return prompts.get(topic, {}).get(language, prompts["new_features"]["fa"])

    @shared_task
    def schedule_content_generation(self):
        """Schedule content generation for different topics"""
        topics = ["new_features", "special_offer", "tech_news"]
        languages = ["fa", "en"]
        
        for topic in topics:
            for lang in languages:
                content = self.generate_promotional_post(topic, lang)
                self._save_content(content, topic, lang)

    def _save_content(self, content: str, topic: str, language: str):
        """Save generated content to database"""
        from mrjbot.models import AIContent
        
        AIContent.objects.create(
            content=content,
            topic=topic,
            language=language,
            status="pending",
            created_at=datetime.now()
        ) 