# ==============================
# Project: KillTheWatcher - Mask Like a Machine v3.0
# Author: Chadi0x (Upgraded)
# Description: Make your system look like a VM to fool malware (Windows/Cross-platform)
# UI: Modern CustomTkinter Dashboard
# ==============================

import os
import json
import platform
import subprocess
import sys
import socket
import tempfile
import shutil
import time
import uuid
import ctypes
import threading
from datetime import datetime
from pathlib import Path

# Auto-install dependencies if missing
def install_dependencies():
    packages = []
    try:
        import customtkinter
    except ImportError:
        packages.append("customtkinter")
    
    if platform.system() == "Windows":
        try:
            import wmi
        except ImportError:
            packages.append("wmi")
            
    if packages:
        print("[*] Installing required packages... This may take a moment.")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages + ["--quiet"])

install_dependencies()

import customtkinter as ctk
from tkinter import messagebox

if platform.system() == "Windows":
    import winreg
    import wmi

PLATFORM_OS = platform.system()
IS_WINDOWS = PLATFORM_OS == "Windows"

BACKUP_DIR = "vm_backup"
BACKUP_FILE = os.path.join(BACKUP_DIR, "original_info.json")
LOG_FILE = os.path.join(BACKUP_DIR, "spoof_log.txt")

# Dummy processes we can spawn
FAKE_PROCESSES = ["wireshark", "procmon", "x64dbg", "fiddler", "ollydbg", "vboxservice", "vmtoolsd"]

class Logger:
    def __init__(self, text_widget=None):
        self.text_widget = text_widget
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
        if self.text_widget:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", log_entry + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

logger = Logger()

def is_admin():
    if IS_WINDOWS:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

# ----- SYSTEM INFO & REGISTRY -----

def get_registry_value(path, name):
    if not IS_WINDOWS: return None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except:
        return None

def set_registry_value(path, name, value):
    if not IS_WINDOWS: return False
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logger.log(f"[!] Failed to set {name}: {e}")
        return False

def get_system_info():
    info = {
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat()
    }
    if IS_WINDOWS:
        info.update({
            "bios_version": get_registry_value(r"HARDWARE\DESCRIPTION\System", "SystemBiosVersion"),
            "system_manufacturer": get_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer"),
            "system_product_name": get_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName"),
            "cpu_name": get_registry_value(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString")
        })
        try:
            c = wmi.WMI()
            for iface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                info["mac"] = iface.MACAddress
                break
        except:
            info["mac"] = "00:00:00:00:00:00"
    return info

def save_backup(data):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=4)
    logger.log("Backup saved successfully.")

def load_backup():
    if not os.path.exists(BACKUP_FILE):
        return None
    with open(BACKUP_FILE, "r") as f:
        return json.load(f)

# ----- SPOOFING FUNCTIONS -----

def spoof_mac(target_mac):
    if not IS_WINDOWS: return False
    try:
        adapter = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)[0]
        adapter.SetMACAddress(target_mac)
        return True
    except Exception as e:
        logger.log(f"[!] Failed MAC Spoofing: {e}")
        return False

def spoof_hostname(hostname):
    if not IS_WINDOWS: return False
    try:
        subprocess.run(["powershell", "-Command", f"Rename-Computer -NewName '{hostname}' -Force"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        logger.log(f"[!] Failed Hostname Spoofing: {e}")
        return False

def create_fake_vm_artifacts():
    if not IS_WINDOWS: return False
    paths = [
        r"C:\Program Files\VMware\VMware Tools",
        r"C:\Program Files\Oracle\VirtualBox Guest Additions"
    ]
    files = [
        r"C:\Program Files\VMware\VMware Tools\vmtoolsd.exe",
        r"C:\Program Files\Oracle\VirtualBox Guest Additions\VBoxService.exe"
    ]
    try:
        for p in paths:
            if not os.path.exists(p):
                os.makedirs(p)
        for f in files:
            with open(f, "w") as dummy:
                dummy.write("MZ fake executable")
        logger.log("[+] Fake VM artifacts created.")
        return True
    except Exception as e:
        logger.log(f"[!] Failed to create VM artifacts: {e}")
        return False

def clean_fake_vm_artifacts():
    if not IS_WINDOWS: return
    paths = [
        r"C:\Program Files\VMware",
        r"C:\Program Files\Oracle"
    ]
    for p in paths:
        try:
            if os.path.exists(p):
                shutil.rmtree(p)
        except Exception as e:
            logger.log(f"[!] Failed to clean {p}: {e}")

spawned_processes = []

def spawn_fake_analysis_tools():
    if not IS_WINDOWS: return False
    temp_dir = tempfile.gettempdir()
    for proc in FAKE_PROCESSES:
        exe_path = os.path.join(temp_dir, f"{proc}.exe")
        try:
            # Copy pythonw.exe to fake process name
            # So looking at task manager reveals "wireshark.exe", "x64dbg.exe"
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            shutil.copy(python_exe, exe_path)
            
            # Create a dummy script that just sleeps
            script_path = os.path.join(temp_dir, f"{proc}_dummy.py")
            with open(script_path, "w") as f:
                f.write("import time\nwhile True: time.sleep(10)")
            
            # Start process
            p = subprocess.Popen([exe_path, script_path], creationflags=subprocess.CREATE_NO_WINDOW)
            spawned_processes.append((p, exe_path, script_path))
            logger.log(f"[+] Started fake process: {proc}.exe")
        except Exception as e:
            logger.log(f"[!] Failed to start {proc}.exe: {e}")
    return True

def kill_fake_analysis_tools():
    for p, exe_path, script_path in spawned_processes:
        try:
            p.terminate()
            time.sleep(0.5)
            if os.path.exists(exe_path): os.remove(exe_path)
            if os.path.exists(script_path): os.remove(script_path)
        except:
            pass
    spawned_processes.clear()
    logger.log("[+] Killed all fake analysis processes.")

def do_spoof(vm_type, do_cpu, do_artifacts, do_procs):
    logger.log(f"[*] Starting Spoofing Process for {vm_type}...")
    
    backup = load_backup()
    if not backup:
        save_backup(get_system_info())
    
    if vm_type == "VMware":
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer", "VMware, Inc.")
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName", "VMware Virtual Platform")
        set_registry_value(r"HARDWARE\DESCRIPTION\System", "SystemBiosVersion", "VMW71.00V.123456")
        spoof_mac("00:05:69:12:34:56")
        spoof_hostname("VMWARE-SYS-01")
    elif vm_type == "VirtualBox":
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer", "innotek GmbH")
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName", "VirtualBox")
        set_registry_value(r"HARDWARE\DESCRIPTION\System", "SystemBiosVersion", "VBOX1234")
        spoof_mac("08:00:27:12:34:56")
        spoof_hostname("VBOX-MACHINE")
    elif vm_type == "HyperV":
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer", "Microsoft Corporation")
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName", "Virtual Machine")
        set_registry_value(r"HARDWARE\DESCRIPTION\System", "SystemBiosVersion", "VRTL1234")
        spoof_mac("00:15:5D:12:34:56")
        spoof_hostname("HYPERV-SYS")
        
    if do_cpu:
        set_registry_value(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString", "Intel(R) Xeon(R) CPU E5-2673 v4 @ 2.30GHz")
        logger.log("[+] CPU Name Spoofed.")
        
    if do_artifacts:
        create_fake_vm_artifacts()
        
    if do_procs:
        spawn_fake_analysis_tools()
        
    logger.log(f"[★★★] System successfully masked as {vm_type}!")
    messagebox.showinfo("Success", "Spoofing complete. Some changes (MAC/Hostname) may require a reboot.")

def do_restore():
    logger.log("[*] Restoring Original System Information...")
    backup = load_backup()
    if not backup:
        logger.log("[!] No backup found to restore.")
        return
        
    if IS_WINDOWS:
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer", backup.get("system_manufacturer", ""))
        set_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName", backup.get("system_product_name", ""))
        set_registry_value(r"HARDWARE\DESCRIPTION\System", "SystemBiosVersion", backup.get("bios_version", ""))
        set_registry_value(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString", backup.get("cpu_name", ""))
        
        spoof_hostname(backup.get("hostname", "DESKTOP-RESTORED"))
        
    clean_fake_vm_artifacts()
    kill_fake_analysis_tools()
    
    logger.log("[★★★] System restored successfully!")
    messagebox.showinfo("Success", "Restoration complete. A reboot is recommended.")


# ----- GUI APPLICATION -----

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class KillTheWatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🕳️ KillTheWatcher v3.0 - Advanced Spoofing System")
        self.geometry("850x600")
        self.resizable(False, False)
        
        # Grid layout Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        
        logger.text_widget = self.log_console
        
        if not is_admin() and IS_WINDOWS:
            logger.log("[WARNING] Running without Administrator privileges. Many features will fail.")
            messagebox.showwarning("Admin Required", "Please run this application as Administrator for full functionality.")
        else:
            logger.log("[SUCCESS] Running with administrative privileges.")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="☢️ KillTheWatcher", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00FFAA")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.subtitle = ctk.CTkLabel(self.sidebar_frame, text="Mask Like a Machine", font=ctk.CTkFont(size=12, slant="italic"))
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 30))

        self.btn_spoof = ctk.CTkButton(self.sidebar_frame, text="🛡️ Apply Mask", command=self.apply_spoof, fg_color="#8B0000", hover_color="#A52A2A")
        self.btn_spoof.grid(row=2, column=0, padx=20, pady=10)

        self.btn_restore = ctk.CTkButton(self.sidebar_frame, text="🔄 Restore System", command=self.restore_system)
        self.btn_restore.grid(row=3, column=0, padx=20, pady=10)

        self.btn_backup = ctk.CTkButton(self.sidebar_frame, text="📋 View Original Data", command=self.view_backup)
        self.btn_backup.grid(row=4, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FFAA")
        self.status_label.grid(row=6, column=0, padx=20, pady=(20, 5), sticky="s")

        self.dev_label = ctk.CTkLabel(self.sidebar_frame, text="Developed by chadi0x", font=ctk.CTkFont(size=11, slant="italic"), text_color="#888888")
        self.dev_label.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="s")

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Settings Panel
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.settings_frame.grid_columnconfigure(1, weight=1)
        
        self.settings_title = ctk.CTkLabel(self.settings_frame, text="⯈ Spoofing Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        self.settings_title.grid(row=0, column=0, columnspan=2, sticky="w")

        # System Info Box
        info = get_system_info()
        admin_txt = "Yes" if is_admin() else "No (Needs Admin)"
        sys_txt = f"OS: {PLATFORM_OS}\nHost: {info['hostname']}\nAdmin Configured: {admin_txt}"
        self.sys_info_lbl = ctk.CTkLabel(self.settings_frame, text=sys_txt, justify="left", fg_color="#2b2b2b", corner_radius=6, padx=15, pady=15)
        self.sys_info_lbl.grid(row=1, column=0, sticky="nw", pady=(15, 0), padx=(0, 20))

        # Right side toggles
        self.toggles_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.toggles_frame.grid(row=1, column=1, sticky="nw", pady=(15, 0))

        self.vm_label = ctk.CTkLabel(self.toggles_frame, text="Target VM Environment:")
        self.vm_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.vm_combo = ctk.CTkComboBox(self.toggles_frame, values=["VMware", "VirtualBox", "HyperV"])
        self.vm_combo.grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.switch_cpu = ctk.CTkSwitch(self.toggles_frame, text="Spoof CPU Name (Xeon Virtual)")
        self.switch_cpu.select()
        self.switch_cpu.grid(row=2, column=0, sticky="w", pady=5)

        self.switch_artifacts = ctk.CTkSwitch(self.toggles_frame, text="Drop Fake VM Directories")
        self.switch_artifacts.select()
        self.switch_artifacts.grid(row=3, column=0, sticky="w", pady=5)
        
        self.switch_procs = ctk.CTkSwitch(self.toggles_frame, text="Run Fake Analysis Tools")
        self.switch_procs.select()
        self.switch_procs.grid(row=4, column=0, sticky="w", pady=5)

        # Console
        self.console_label = ctk.CTkLabel(self.main_frame, text="⯈ Live Activity Log", font=ctk.CTkFont(size=16, weight="bold"))
        self.console_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.log_console = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), text_color="#00FFAA", fg_color="#121212")
        self.log_console.grid(row=2, column=0, sticky="nsew")
        self.log_console.configure(state="disabled")

    def apply_spoof(self):
        if not is_admin() and IS_WINDOWS:
            messagebox.showerror("Error", "Admin privileges required.")
            return
            
        vm_type = self.vm_combo.get()
        do_cpu = self.switch_cpu.get()
        do_artifacts = self.switch_artifacts.get()
        do_procs = self.switch_procs.get()
        
        self.status_label.configure(text="Status: Spoofing...", text_color="yellow")
        threading.Thread(target=self._spoof_worker, args=(vm_type, do_cpu, do_artifacts, do_procs), daemon=True).start()

    def _spoof_worker(self, vm_type, do_cpu, do_artifacts, do_procs):
        do_spoof(vm_type, do_cpu, do_artifacts, do_procs)
        self.status_label.configure(text="Status: Spoofed (Masked)", text_color="#00FFAA")

    def restore_system(self):
        if not is_admin() and IS_WINDOWS:
            messagebox.showerror("Error", "Admin privileges required.")
            return
            
        self.status_label.configure(text="Status: Restoring...", text_color="yellow")
        threading.Thread(target=self._restore_worker, daemon=True).start()
        
    def _restore_worker(self):
        do_restore()
        self.status_label.configure(text="Status: Restored", text_color="#00FFAA")

    def view_backup(self):
        backup = load_backup()
        if not backup:
            messagebox.showinfo("Backup", "No backup found.")
            return
            
        win = ctk.CTkToplevel(self)
        win.title("Original System Info Backup")
        win.geometry("500x400")
        
        txt = ctk.CTkTextbox(win, font=("Consolas", 12))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("0.0", json.dumps(backup, indent=4))
        txt.configure(state="disabled")


if __name__ == "__main__":
    if IS_WINDOWS and not is_admin():
        response = messagebox.askyesno(
            "Admin Rights Required",
            "KillTheWatcher works best with Administrator privileges.\n\n"
            "Would you like to restart with admin rights?"
        )
        if response:
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()
            except:
                pass
                
    app = KillTheWatcherApp()
    app.mainloop()
