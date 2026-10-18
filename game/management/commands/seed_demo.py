"""Populate an invented question bank; no original database is read."""

from django.core.management.base import BaseCommand
from django.db import transaction
from game.models import Question


class Command(BaseCommand):
    help = "Add 20 invented arithmetic questions without creating users or games."

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        for level in range(1, 5):
            for n in range(1, 6):
                answer = level * 10 + n
                _, new = Question.objects.get_or_create(
                    level=level,
                    text=f"What is {level*10} + {n}?",
                    defaults={
                        "answer_1": str(answer),
                        "answer_2": str(answer + 1),
                        "answer_3": str(answer - 1),
                        "answer_4": str(answer + 2),
                        "correct_answer": 1,
                    },
                )
                created += new
        self.stdout.write(
            self.style.SUCCESS(
                f"Added {created} demo questions. No participant records were imported."
            )
        )
