"""
seed_google — Creates the Site record and Google SocialApp template record
required for django-allauth Google OAuth to function.

Run this command AFTER following GOOGLE_SIGNIN.md setup instructions.
Then update the SocialApp record in Django admin with your real credentials.

Usage:
    python manage.py seed_google
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Seeds the Site record and Google SocialApp template record for OAuth. "
        "Run after following GOOGLE_SIGNIN.md. Then update credentials in /admin/."
    )

    def handle(self, *args: object, **options: object) -> None:
        self._seed_site()
        self._seed_social_app()
        self.stdout.write(self.style.SUCCESS("\nGoogle OAuth seeding complete."))
        self.stdout.write(
            "Next step: go to /admin/socialaccount/socialapp/ and update the\n"
            "Google SocialApp record with your real Client ID and Secret Key.\n"
            "See GOOGLE_SIGNIN.md for full instructions."
        )

    def _seed_site(self) -> None:
        from django.contrib.sites.models import Site

        site, created = Site.objects.update_or_create(
            id=1,
            defaults={
                "domain": "127.0.0.1:8000",
                "name": "xtudio",
            },
        )
        label = "Created" if created else "Updated"
        self.stdout.write(f"  {label}: Site record → domain=127.0.0.1:8000, name=xtudio")

    def _seed_social_app(self) -> None:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        site = Site.objects.get(id=1)

        app, created = SocialApp.objects.get_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": "your-google-client-id",
                "secret": "your-google-client-secret",
                "key": "",
            },
        )

        # Ensure the site is linked
        if site not in app.sites.all():
            app.sites.add(site)

        label = "Created" if created else "Found"
        self.stdout.write(f"  {label}: Google SocialApp template record")
        if created:
            self.stdout.write(
                "  ⚠  Placeholder credentials used — update with real values in /admin/"
            )
