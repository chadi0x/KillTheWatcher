# ==============================
# Project: VMInducer - Mask Like a Machine
# Author: Chadi
# Description: Make your Windows look like a VM to fool malware.
# ==============================

import os
import json
import platform
import subprocess
import winreg
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

try:
    import wmi
except ImportError:
    subprocess.check_call(["python", "-m", "pip", "install", "wmi"])
    import wmi

BACKUP_DIR = "vm_backup"
BACKUP_FILE = os.path.join(BACKUP_DIR, "original_info.json")

# Utilities

def create_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def save_backup(data):
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_backup():
    if not os.path.exists(BACKUP_FILE):
        messagebox.showerror("Error", "No backup file found.")
        return None
    with open(BACKUP_FILE, "r") as f:
        return json.load(f)

def get_system_info():
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "node": platform.node(),
        "processor": platform.processor(),
        "bios_version": get_registry_value(r"HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion"),
        "system_manufacturer": get_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemManufacturer"),
        "system_product_name": get_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemProductName"),
        "mac": get_mac_address()
    }
    return info

def get_registry_value(path, name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        value, _ = winreg.QueryValueEx(key, name)
        return value
    except Exception as e:
        return str(e)

def set_registry_value(path, name, value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        print(f"[+] Set {name} in {path} to {value}")
    except Exception as e:
        print(f"[!] Failed to set {name} in {path}: {e}")

def get_mac_address():
    c = wmi.WMI()
    for iface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        return iface.MACAddress
    return "Unknown"

def spoof_mac(vm_type):
    macs = {
        "VMware": "00:05:69:12:34:56",
        "VirtualBox": "08:00:27:12:34:56",
        "QEMU": "52:54:00:12:34:56"
    }
    target_mac = macs.get(vm_type)
    if not target_mac:
        return

    try:
        adapter = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)[0]
        adapter.SetMACAddress(target_mac)
        print(f"[+] MAC address spoofed to {target_mac}")
    except Exception as e:
        print(f"[!] Failed to spoof MAC: {e}")

# Spoofing functions

def fake_vm_info(vm_type):
    print("[*] Saving original system info...")
    create_backup_dir()
    original_info = get_system_info()
    save_backup(original_info)

    print(f"[*] Spoofing VM-like information ({vm_type})...")

    if vm_type == "VMware":
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemManufacturer", "VMware, Inc.")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemProductName", "VMware Virtual Platform")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion", "VMW71.00V.123456")
    elif vm_type == "VirtualBox":
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemManufacturer", "innotek GmbH")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemProductName", "VirtualBox")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion", "VBOX1234")
    elif vm_type == "QEMU":
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemManufacturer", "QEMU")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemProductName", "Standard PC (Q35 + ICH9, 2009)")
        set_registry_value(r"HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion", "QEMU1234")

    spoof_mac(vm_type)
    messagebox.showinfo("Done", "Spoofing complete. Reboot may be required.")

# Restoration function

def restore_original_info():
    print("[*] Restoring original system information...")
    backup = load_backup()
    if backup is None:
        return

    set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemManufacturer", backup.get("system_manufacturer", ""))
    set_registry_value(r"HARDWARE\\DESCRIPTION\\System\\BIOS", "SystemProductName", backup.get("system_product_name", ""))
    set_registry_value(r"HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion", backup.get("bios_version", ""))
    messagebox.showinfo("Restoration", "Original system info restored. Reboot may be required.")

# GUI

def launch_gui():
    window = tk.Tk()
    window.title("VMInducer - Spoof Defense")
    window.geometry("400x250")

    tk.Label(window, text="Select Action:", font=("Arial", 14)).pack(pady=10)

    def spoof(vm_type):
        fake_vm_info(vm_type)

    tk.Button(window, text="Fake as VMware", width=30, command=lambda: spoof("VMware")).pack(pady=5)
    tk.Button(window, text="Fake as VirtualBox", width=30, command=lambda: spoof("VirtualBox")).pack(pady=5)
    tk.Button(window, text="Fake as QEMU", width=30, command=lambda: spoof("QEMU")).pack(pady=5)
    tk.Button(window, text="Restore Original Info", width=30, command=restore_original_info).pack(pady=20)

    window.mainloop()

if __name__ == '__main__':
    launch_gui()

