from django.test.utils import override_settings
from django.test import TestCase

from private_sharing.models import OnSiteDataRequestProject
from private_sharing.testing import DirectSharingMixin

from .models import DataType


@override_settings(SSLIFY_DISABLE=True)
class DataTypeTests(DirectSharingMixin, TestCase):
    """
    Tests for datatypes
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = OnSiteDataRequestProject.objects.get(slug="abc-2")
        dt_0 = DataType(name="asdf", description="asdf")
        dt_0.save()
        dt_1 = DataType(name="asdf child", description="asdf child")
        dt_1.parent = dt_0
        dt_1.save()
        dt_2 = DataType(name="qwerty", description="qwerty")
        dt_2.save()

    def test_datatypes_api_endpoint(self):
        response = self.client.get("/api/data-management/datatypes/")
        self.assertEqual(response.status_code, 200)
        json = response.json()
        results = json["results"]
        asdf_id = DataType.objects.get(name="asdf").id
        for result in results:
            if result["name"] == "asdf child":
                if result["parent"] == asdf_id:
                    return
        raise
