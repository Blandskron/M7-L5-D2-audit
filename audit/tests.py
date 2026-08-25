from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import AuditLog


class AuditQueriesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        AuditLog.objects.create(user="ana", action="login", severity="ERROR", message="failed login")
        AuditLog.objects.create(user="bruno", action="export", severity="INFO", message="daily export")
        call_command("install_audit_procedures", verbosity=0)

    def test_orm_filters_and_annotations_are_rendered(self):
        response = self.client.get(reverse("audit:logs_orm"), {"user": "ana", "severity": "ERROR"})
        self.assertContains(response, "ana")
        self.assertNotContains(response, "bruno")
        self.assertContains(response, "ERROR: 1")

    def test_raw_sql_maps_rows_to_model(self):
        response = self.client.get(reverse("audit:logs_sql"), {"severity": "ERROR", "days": 365})
        self.assertContains(response, "failed login")

    def test_crud_sql_is_post_only_and_leaves_existing_rows_intact(self):
        url = reverse("audit:logs_crud_sql")
        self.assertEqual(self.client.get(url).status_code, 200)
        original_count = AuditLog.objects.count()
        response = self.client.post(url, follow=True)
        self.assertContains(response, "INSERT, UPDATE y DELETE")
        self.assertEqual(AuditLog.objects.count(), original_count)

    def test_procedure_call_creates_audit_record_and_returns_summary(self):
        response = self.client.get(reverse("audit:logs_procedure"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AuditLog.objects.filter(user="procedure-demo").exists())
