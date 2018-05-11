from datetime import timedelta as td
from unittest import TestCase
from hc.front.templatetags.hc_extras import hc_duration


class HcExtrasTestCase(TestCase):

    def test_hc_duration_works(self):
        samples = [
            (60, "1 minute"),
            (3600, "1 hour"),
            (604800, "1 week"),
            (2592000, "1 month"),
            (31104000, "1 year"),
        ]

        for seconds, expected_result in samples:
            result = hc_duration(td(seconds=seconds))
            self.assertEqual(result, expected_result)
