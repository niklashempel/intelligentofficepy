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

    def test_check_quadrant_occupancy_raises_error_with_wrong_pin(self):
        sut = IntelligentOffice()
        with self.assertRaises(IntelligentOfficeError):
            sut.check_quadrant_occupancy(sut.LED_PIN)

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_open(self, mock_servo: Mock, mock_rtc: Mock):
        date = datetime(2024, 11, 25, 8)
        mock_rtc.return_value = date
        sut = IntelligentOffice()
        sut.manage_blinds_based_on_time()
        self.assertTrue(sut.blinds_open)
        mock_servo.assert_called_once_with(12)

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_before_8(self, mock_servo: Mock, mock_rtc: Mock):
        date = datetime(2024, 11, 25, 7)
        mock_rtc.return_value = date
        sut = IntelligentOffice()
        sut.manage_blinds_based_on_time()
        self.assertFalse(sut.blinds_open)
        mock_servo.assert_not_called()


    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_close(self, mock_servo: Mock, mock_rtc: Mock):
        date = datetime(2024, 11, 25, 20)
        mock_rtc.return_value = date
        sut = IntelligentOffice()
        sut.manage_blinds_based_on_time()
        self.assertFalse(sut.blinds_open)
        mock_servo.assert_called_once_with(2)

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_after_20(self, mock_servo: Mock, mock_rtc: Mock):
        date = datetime(2024, 11, 25, 21)
        mock_rtc.return_value = date
        sut = IntelligentOffice()
        sut.manage_blinds_based_on_time()
        self.assertFalse(sut.blinds_open)
        mock_servo.assert_not_called()

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_do_nothing_on_weekend(self, mock_servo: Mock, mock_rtc: Mock):
        date = datetime(2024, 11, 24, 8)
        mock_rtc.return_value = date
        sut = IntelligentOffice()
        sut.manage_blinds_based_on_time()
        self.assertFalse(sut.blinds_open)
        mock_servo.assert_not_called()