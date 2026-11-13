import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from ios_devmode_helper.backend import PymobiledeviceAdapter, friendly_error, HelperError


class PlatformSupportTests(unittest.IsolatedAsyncioTestCase):
    async def test_usb_filter_is_preserved(self):
        devices = [SimpleNamespace(serial="fixture-usb")]
        with patch("pymobiledevice3.usbmux.select_devices_by_connection_type", new=AsyncMock(return_value=devices)) as select:
            self.assertEqual(await PymobiledeviceAdapter().list_usb(), ["fixture-usb"])
            select.assert_awaited_once_with(connection_type="USB")

    async def test_platform_specific_transport_guidance(self):
        for system, expected in (("linux", "usbmuxd"), ("win32", "Apple Devices")):
            with patch("ios_devmode_helper.backend.sys.platform", system):
                self.assertIn(expected, friendly_error(RuntimeError("usbmux unavailable")))

    async def test_pairing_error_is_not_misreported_as_missing_daemon(self):
        self.assertIn("tap Trust", friendly_error(RuntimeError("usbmuxd has no pair record")))

    async def test_missing_display_is_actionable(self):
        from ios_devmode_helper import gui
        with patch.object(gui.tk, "Tk", side_effect=gui.tk.TclError("no display")):
            with self.assertRaisesRegex(HelperError, "--list"):
                gui.launch()
