from __future__ import annotations
import argparse, asyncio, json, sys
from .backend import DeveloperModeBackend, HelperError

def parser():
    p=argparse.ArgumentParser(description="Reveal the iOS Developer Mode setting over USB.")
    group=p.add_mutually_exclusive_group(); group.add_argument("--list",action="store_true");group.add_argument("--status",action="store_true");group.add_argument("--reveal",action="store_true");group.add_argument("--self-test",action="store_true")
    p.add_argument("--device",help="Exact USB device ID returned by --list")
    p.add_argument("--timeout",type=float,default=20.0)
    p.add_argument("--output",help="Write JSON result to this file (useful for the windowed executable)")
    return p

def emit(args, payload, *, error=False):
    rendered=json.dumps(payload,ensure_ascii=False)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(rendered+"\n",encoding="utf-8")
    else:
        stream=sys.stderr if error else sys.stdout
        if stream is not None: print(rendered,file=stream)

async def run(args):
    if args.self_test:
        from .selftest import checks
        ok,detail=await checks();result={"ok":ok,"checks":detail,"device_access":False}
        emit(args,result);return 0 if ok else 3
    backend=DeveloperModeBackend(timeout=max(1,min(args.timeout,120)))
    if args.list:
        devices=await backend.devices();emit(args,{"devices":[{"id":d.id,"label":d.label,"transport":"USB"} for d in devices]});return 0
    if args.status or args.reveal:
        device=await backend.select(args.device)
        if args.reveal:
            await backend.reveal(device.id);emit(args,{"ok":True,"revealed":True,"enabled":None,"status":"unverified","next":"On the device, open Settings > Privacy & Security > Developer Mode. Enable it, restart, and confirm if needed; use --status afterward to verify."})
        else: emit(args,{"ok":True,"enabled":await backend.status(device.id)})
        return 0
    from .gui import launch
    launch();return 0

def main():
    args=parser().parse_args()
    try:return asyncio.run(run(args))
    except HelperError as exc:emit(args,{"ok":False,"error":str(exc)},error=True);return 2

if __name__=="__main__":raise SystemExit(main())
