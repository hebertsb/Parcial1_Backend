from django.test import SimpleTestCase

from core.utils.plate_ocr import PlateOCRService


class NormalizePlateTests(SimpleTestCase):
    def test_accepts_three_or_four_digits(self):
        self.assertEqual(PlateOCRService._normalize_plate('123ABC'), '123ABC')
        self.assertEqual(PlateOCRService._normalize_plate('1234ABC'), '1234ABC')

    def test_corrects_common_digit_confusions(self):
        self.assertEqual(PlateOCRService._normalize_plate('12OABC'), '120ABC')
        self.assertEqual(PlateOCRService._normalize_plate('I23ABC'), '123ABC')

    def test_corrects_common_letter_confusions(self):
        self.assertEqual(PlateOCRService._normalize_plate('1234AB8'), '1234ABB')

    def test_rejects_invalid_lengths(self):
        self.assertIsNone(PlateOCRService._normalize_plate('12ABCD'))
        self.assertIsNone(PlateOCRService._normalize_plate('1234567'))