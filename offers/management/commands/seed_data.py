from django.core.management.base import BaseCommand
from offers.models import Category, Level, Format, Status


class Command(BaseCommand):
    help = "Populate database with default categories, levels, formats, and statuses"

    def handle(self, *args, **options):
        categories = [
            ("Programming", "Software development, web and mobile apps, databases"),
            ("Design", "UI/UX, graphic design, 3D modeling, illustration"),
            ("Languages", "Foreign languages and linguistics"),
            ("Marketing", "Digital marketing, SEO, SMM, copywriting"),
            ("Music", "Musical instruments, vocal, sound production"),
            ("Photography", "Photo shooting, editing, composition"),
            ("Business", "Management, entrepreneurship, finance"),
            ("Mathematics", "Higher mathematics, statistics, algebra"),
            ("Other", "Other skills and hobbies"),
        ]
        levels = ["Beginner", "Intermediate", "Advanced"]
        formats = ["Online", "Offline"]
        statuses = ["Draft", "Pending", "Published", "Rejected"]

        for name, desc in categories:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Category: {name}"))

        for name in levels:
            lvl, created = Level.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Level: {name}"))

        for name in formats:
            fmt, created = Format.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Format: {name}"))

        for name in statuses:
            st, created = Status.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Status: {name}"))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
