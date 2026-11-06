"""USB-only pymobiledevice3 backend for Developer Mode reveal/status."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Protocol

DEFAULT_TIMEOUT = 20.0

class HelperError(RuntimeError): pass
class NoDeviceError(HelperError): pass
class MultipleDevicesError(HelperError): pass
class DeviceNotFoundError(HelperError): pass

@dataclass(frozen=True)
class Device:
    id: str
    label: str

class Adapter(Protocol):
    async def list_usb(self) -> list[str]: ...
    async def status(self, device_id: str) -> bool: ...
    async def reveal(self, device_id: str) -> None: ...

class PymobiledeviceAdapter:
    def __init__(self, pair_timeout: float = 15.0): self.pair_timeout=pair_timeout

    async def list_usb(self) -> list[str]:
        from pymobiledevice3 import usbmux
        return [d.serial for d in await usbmux.select_devices_by_connection_type(connection_type="USB")]

    async def _with_lockdown(self, device_id: str, operation):
        from pymobiledevice3.lockdown import create_using_usbmux
        client = await create_using_usbmux(serial=device_id, connection_type="USB", autopair=True,
                                            pair_timeout=self.pair_timeout)
        try:
            raw_device_class=getattr(client.device_class,"value",client.device_class)
            device_class=str(raw_device_class or "").lower()
            try: major=int(str(client.product_version).split(".",1)[0])
            except (TypeError,ValueError): major=0
            if device_class not in {"iphone","ipad"} or major < 16:
                raise HelperError("Developer Mode reveal requires an iPhone or iPad running iOS/iPadOS 16 or later.")
            return await operation(client)
        finally:
            await client.close()

    async def status(self, device_id: str) -> bool:
        return bool(await self._with_lockdown(device_id, lambda client: client.get_developer_mode_status()))

    async def reveal(self, device_id: str) -> None:
        from pymobiledevice3.services.amfi import AmfiService
        await self._with_lockdown(device_id, lambda client: AmfiService(client).reveal_developer_mode_option_in_ui())

class DeveloperModeBackend:
    def __init__(self, adapter: Adapter | None = None, timeout: float = DEFAULT_TIMEOUT):
        self.adapter = adapter or PymobiledeviceAdapter(pair_timeout=min(timeout,15.0))
        self.timeout = timeout

    async def _bounded(self, awaitable):
        try:
            return await asyncio.wait_for(awaitable, self.timeout)
        except asyncio.TimeoutError as exc:
            raise HelperError("The device did not respond in time. Reconnect the USB cable and try again.") from exc
        except HelperError:
            raise
        except Exception as exc:
            raise HelperError(friendly_error(exc)) from exc

    async def devices(self) -> list[Device]:
        ids = await self._bounded(self.adapter.list_usb())
        return [Device(value, f"USB device {i + 1} (…{value[-4:]})") for i, value in enumerate(ids)]

    async def select(self, device_id: str | None) -> Device:
        devices = await self.devices()
        if device_id:
            found = next((d for d in devices if d.id == device_id), None)
            if found is None: raise DeviceNotFoundError("The selected USB device is no longer connected.")
            return found
        if not devices: raise NoDeviceError("No USB iPhone or iPad was found.")
        if len(devices) > 1: raise MultipleDevicesError("More than one USB device is connected. Select one explicitly.")
        return devices[0]

    async def status(self, device_id: str) -> bool:
        await self.select(device_id)
        return await self._bounded(self.adapter.status(device_id))

    async def reveal(self, device_id: str) -> None:
        await self.select(device_id)
        await self._bounded(self.adapter.reveal(device_id))

def friendly_error(exc: Exception) -> str:
    name = type(exc).__name__.lower(); text = str(exc).lower()
    if "usbmux" in name or "usbmux" in text: return "Apple device support is unavailable. Install or repair Apple Devices/iTunes drivers, then reconnect the device."
    if "passcode" in name or "passcode" in text: return "The device passcode prevents this operation. Use the manual Settings steps; do not remove your passcode."
    if "passwordprotected" in name or "locked" in name or "locked" in text: return "Unlock the device and try again."
    if "pair" in name or "trust" in text: return "Unlock the device, tap Trust on the device, then try again."
    if "connection" in name or "disconnect" in text or "brokenpipe" in name: return "The USB device disconnected. Reconnect it and try again."
    if "amfi" in name or "developer" in name: return "This iOS version or device did not accept the Developer Mode request."
    if "mux" in name or "service" in text: return "Apple device support is unavailable. Install or repair Apple Devices/iTunes drivers, then reconnect the device."
    return "The operation failed. Unlock and trust the USB device, reconnect it, and try again."
