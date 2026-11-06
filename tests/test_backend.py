import asyncio, unittest
from unittest.mock import AsyncMock, patch
from pymobiledevice3.lockdown import DeviceClass
from ios_devmode_helper.backend import DeveloperModeBackend, PymobiledeviceAdapter, MultipleDevicesError, NoDeviceError, HelperError
from ios_devmode_helper.selftest import Fake

class BackendTests(unittest.IsolatedAsyncioTestCase):
    async def adapter_client(self,device_class,version):
        client=unittest.mock.Mock()
        client.device_class=device_class;client.product_version=version
        client.get_developer_mode_status=AsyncMock(return_value=False);client.close=AsyncMock()
        with patch("pymobiledevice3.lockdown.create_using_usbmux",new=AsyncMock(return_value=client)):
            try: result=await PymobiledeviceAdapter().status("fixture")
            except Exception as exc: result=exc
        return result,client

    async def test_real_device_class_enum_and_close(self):
        for kind in (DeviceClass.IPHONE,DeviceClass.IPAD):
            result,client=await self.adapter_client(kind,"16.0")
            self.assertIs(result,False);client.close.assert_awaited_once()
        for kind,version in ((DeviceClass.APPLE_TV,"17.0"),(DeviceClass.IPHONE,"15.7")):
            result,client=await self.adapter_client(kind,version)
            self.assertIsInstance(result,HelperError);client.close.assert_awaited_once()

    async def test_no_device(self):
        with self.assertRaises(NoDeviceError): await DeveloperModeBackend(Fake(())).select(None)
    async def test_multiple_requires_exact_selection(self):
        backend=DeveloperModeBackend(Fake(("one","two")))
        with self.assertRaises(MultipleDevicesError): await backend.select(None)
        self.assertEqual((await backend.select("two")).id,"two")
    async def test_reveal_does_not_report_enabled(self):
        fake=Fake(enabled=False); backend=DeveloperModeBackend(fake)
        await backend.reveal("fixture-a")
        self.assertFalse(await backend.status("fixture-a"));self.assertEqual(fake.revealed,["fixture-a"])
    async def test_timeout_is_friendly(self):
        with self.assertRaisesRegex(HelperError,"did not respond"):
            await DeveloperModeBackend(Fake(delay=.05),timeout=.001).status("fixture-a")
