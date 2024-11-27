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

    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_on(self, mock_led: Mock, mock_ambient_sensor: Mock, mock_check_quadrant_occupancy: Mock):
        mock_check_quadrant_occupancy.return_value = True
        mock_ambient_sensor.return_value = 499
        sut = IntelligentOffice()
        sut.manage_light_level()
        self.assertTrue(sut.light_on)
        mock_led.assert_called_with(sut.LED_PIN, True)

    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_off(self, mock_led: Mock, mock_ambient_sensor: Mock, mock_check_quadrant_occupancy: Mock):
        mock_check_quadrant_occupancy.return_value = True
        mock_ambient_sensor.return_value = 551
        sut = IntelligentOffice()
        sut.manage_light_level()
        self.assertFalse(sut.light_on)
        mock_led.assert_called_with(sut.LED_PIN, False)

    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_do_nothing(self, mock_led: Mock, mock_ambient_sensor: Mock, mock_check_quadrant_occupancy: Mock):
        mock_check_quadrant_occupancy.return_value = True
        mock_ambient_sensor.side_effect = [500, 550]
        sut = IntelligentOffice()
        sut.manage_light_level()
        sut.manage_light_level()
        self.assertFalse(sut.light_on)
        mock_led.assert_not_called()

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_off_after_last_worker(self, mock_led: Mock, mock_check_quadrant_occupancy: Mock, mock_ambient_sensor: Mock):
        mock_ambient_sensor.return_value = 499
        mock_check_quadrant_occupancy.side_effect = [False, False, False, False]
        sut = IntelligentOffice()
        sut.manage_light_level()
        self.assertFalse(sut.light_on)
        mock_led.assert_called_once_with(sut.LED_PIN, False)
    