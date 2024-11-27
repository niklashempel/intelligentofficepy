import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy(self, mock_object: Mock):
        mock_object.side_effect = [True, True, False, True]
        sut = IntelligentOffice()
        self.assertTrue(sut.check_quadrant_occupancy(sut.INFRARED_PIN1))
        self.assertTrue(sut.check_quadrant_occupancy(sut.INFRARED_PIN2))
        self.assertFalse(sut.check_quadrant_occupancy(sut.INFRARED_PIN3))
        self.assertTrue(sut.check_quadrant_occupancy(sut.INFRARED_PIN4))