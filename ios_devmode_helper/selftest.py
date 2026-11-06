from __future__ import annotations
import asyncio, tkinter
from .backend import DeveloperModeBackend, MultipleDevicesError, HelperError

class Fake:
    def __init__(self,ids=("fixture-a",),enabled=False,delay=0): self.ids=list(ids);self.enabled=enabled;self.delay=delay;self.revealed=[]
    async def list_usb(self): return self.ids
    async def status(self,device_id): await asyncio.sleep(self.delay);return self.enabled
    async def reveal(self,device_id): self.revealed.append(device_id)

async def checks():
    from pymobiledevice3 import usbmux
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.services.amfi import AmfiService
    if not callable(usbmux.select_devices_by_connection_type) or not callable(create_using_usbmux) or not AmfiService:
        return False,"runtime imports unavailable"
    multi=DeveloperModeBackend(Fake(("a","b")))
    try: await multi.select(None); return False,"multiple devices were auto-selected"
    except MultipleDevicesError: pass
    fake=Fake(enabled=False); backend=DeveloperModeBackend(fake)
    if await backend.status("fixture-a"): return False,"false status changed"
    await backend.reveal("fixture-a")
    if fake.revealed != ["fixture-a"] or await backend.status("fixture-a"): return False,"reveal was treated as enable"
    try: await DeveloperModeBackend(Fake(delay=.05),timeout=.001).status("fixture-a"); return False,"timeout was not bounded"
    except HelperError: pass
    return True,"backend, timeout, tkinter import"

def run_self_test():
    ok,detail=asyncio.run(checks());return {"ok":ok,"checks":detail,"device_access":False}
