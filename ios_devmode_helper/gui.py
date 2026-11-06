from __future__ import annotations
import asyncio, queue, threading, tkinter as tk
from tkinter import ttk
from .backend import DeveloperModeBackend, HelperError

class Window:
    def __init__(self, root: tk.Tk):
        self.root=root; self.backend=DeveloperModeBackend(); self.devices=[]; self.generation=0
        root.title("iOS Developer Mode Helper"); root.geometry("540x420"); root.minsize(500,390)
        root.protocol("WM_DELETE_WINDOW",self.close)
        style=ttk.Style(); style.configure("Title.TLabel",font=("Segoe UI",16,"bold")); style.configure("Hint.TLabel",foreground="#555")
        pane=ttk.Frame(root,padding=22); pane.pack(fill="both",expand=True)
        ttk.Label(pane,text="iOS Developer Mode Helper",style="Title.TLabel").pack(anchor="w")
        ttk.Label(pane,text="Connect an unlocked, trusted iPhone or iPad using USB.",style="Hint.TLabel").pack(anchor="w",pady=(4,18))
        row=ttk.Frame(pane); row.pack(fill="x")
        self.choice=tk.StringVar(); self.combo=ttk.Combobox(row,textvariable=self.choice,state="readonly")
        self.combo.pack(side="left",fill="x",expand=True); self.combo.bind("<<ComboboxSelected>>",lambda _e:self.selection_changed())
        self.refresh=ttk.Button(row,text="Refresh",command=self.load_devices); self.refresh.pack(side="left",padx=(8,0))
        actions=ttk.Frame(pane); actions.pack(fill="x",pady=14)
        self.status_button=ttk.Button(actions,text="Check status",command=self.check_status,state="disabled"); self.status_button.pack(side="left")
        self.reveal_button=ttk.Button(actions,text="Reveal setting",command=self.reveal,state="disabled"); self.reveal_button.pack(side="left",padx=8)
        self.state=tk.StringVar(value="Looking for USB devices…")
        ttk.Label(pane,textvariable=self.state,wraplength=490).pack(anchor="w",pady=(2,12))
        box=ttk.LabelFrame(pane,text="After Reveal setting succeeds",padding=12); box.pack(fill="both",expand=True)
        ttk.Label(box,text="1. On the device, open Settings > Privacy & Security.\n2. Open Developer Mode and turn it on.\n3. Allow the restart.\n4. Unlock the device and confirm Developer Mode.\n\nReveal only makes the switch visible. It does not enable Developer Mode.",wraplength=460,justify="left").pack(anchor="w")
        self.q=queue.Queue(); root.after(75,self.drain); self.load_devices()

    def selected_id(self):
        index=self.combo.current(); return self.devices[index].id if 0 <= index < len(self.devices) else None
    def selection_changed(self): self.update_buttons(False)
    def update_buttons(self,busy):
        selected=self.selected_id() is not None
        self.combo.configure(state="disabled" if busy else "readonly")
        self.refresh.configure(state="disabled" if busy else "normal")
        for b in (self.status_button,self.reveal_button): b.configure(state="disabled" if busy or not selected else "normal")
    def submit(self, operation, success):
        self.generation+=1; token=self.generation; self.update_buttons(True)
        def worker():
            try: result=asyncio.run(operation()); self.q.put((token,success,result,None))
            except Exception as exc: self.q.put((token,success,None,exc))
        threading.Thread(target=worker,daemon=True).start()
    def drain(self):
        try:
            while True:
                token,success,result,error=self.q.get_nowait()
                if token != self.generation: continue
                self.update_buttons(False)
                if error: self.state.set(str(error) if isinstance(error,HelperError) else "The operation failed. Reconnect the device and try again.")
                else: success(result)
        except queue.Empty: pass
        if self.root.winfo_exists(): self.root.after(75,self.drain)
    def load_devices(self):
        self.state.set("Looking for USB devices…"); self.devices=[]; self.combo.configure(values=[]); self.choice.set("")
        def done(devices):
            self.devices=devices; self.combo.configure(values=[d.label for d in devices])
            if len(devices)==1: self.combo.current(0); self.state.set("One USB device found. Unlock and trust it before continuing.")
            elif len(devices)>1: self.state.set("Multiple USB devices found. Select the intended device.")
            else: self.state.set("No USB iPhone or iPad found. Check the cable and Apple device drivers.")
            self.update_buttons(False)
        self.submit(self.backend.devices,done)
    def check_status(self):
        device_id=self.selected_id()
        if not device_id:return
        self.state.set("Checking Developer Mode status…")
        self.submit(lambda:self.backend.status(device_id),lambda enabled:self.state.set("Developer Mode is enabled." if enabled else "Developer Mode is currently disabled."))
    def reveal(self):
        device_id=self.selected_id()
        if not device_id:return
        self.state.set("Requesting the Developer Mode setting…")
        self.submit(lambda:self.backend.reveal(device_id),lambda _result:self.state.set("The setting is available. Complete the steps below if needed, then use Check status to verify."))
    def close(self): self.generation+=1; self.root.destroy()

def launch():
    root=tk.Tk(); Window(root); root.mainloop()
