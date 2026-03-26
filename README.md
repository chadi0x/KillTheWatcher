<div align="center">
  
# 🕳️ KillTheWatcher v3.0

**Deceive Malware. Defend with Illusion.**  
*Developed with ❤️ by [chadi0x](https://github.com/chadi0x)*

![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)
![UI](https://img.shields.io/badge/UI-CustomTkinter-green)
<img width="847" height="627" alt="Screenshot 2026-03-26 at 05 29 25" src="https://github.com/user-attachments/assets/6d23b9d8-44c9-4b06-a866-0984b7b1815e" />

</div>

---

## 🧠 The Idea Behind the Tool

While researching major cyberattacks and advanced malware behavior, a powerful pattern emerged:  
Most high-level, evasive malware **checks if it's running inside a Virtual Machine (VM)**. If it detects it's in a sandbox, it will **shut down, delete itself, or go completely silent** — a tactic used to avoid being analyzed by cybersecurity teams and antivirus labs.

> ❗ **What if we reversed the trap?**  
> What if we could **spoof a real, physical machine to appear like an isolated VM**?

By creating a fake virtual environment signature on your system, you can **trick malware into thinking it's being watched**, forcing it to abort its execution. This isn't just theory — it gives you real defensive leverage against stealth-based and sandboxing-aware malware.

---

## 🔥 What's New in v3.0 (Massive Upgrade)

The entire tool has been rewritten from the ground up for maximum deception and a stunning user experience.

- **🎨 Modern Dark-Mode GUI**: Redesigned from scratch 
- **🛡️ Pseudo-Analysis Guards**: Emulates the presence of actively running analysis tools (like `wireshark.exe`, `procmon.exe`, `x64dbg.exe`) in the background. If malware sees these processes, it instantly self-terminates.
- **🧬 CPU Virtualization Spoofing**: Tricks the system registry into reporting an `Intel(R) Xeon(R) CPU E5-2673 v4 @ 2.30GHz` processor commonly found in server-side sandboxes.
- **🪞 Fake VM Artifact Generator**: Drops dummy files and folders (like `vmtoolsd.exe` and `VBoxService.exe`) natively into system directories to trip up malware path-checking algorithms.
- **🔄 Auto-Dependency Installer**: Missing dependencies? `KillTheWatcher` now seamlessly installs `customtkinter` and `wmi` in the background on its first run!

---

## 💡 Core Arsenal & Capabilities

- 🧟 **Spoofs Core VM Indicators** (VMware, VirtualBox, QEMU, Hyper-V)
- 🧬 **Spoofs CPU Name & MAC Addresses**
- 🪞 **Mimics Sandbox Artifacts & Drops Dummy Files**
- 🛡️ **Generates Fake Analysis Processes** (Wireshark, x64dbg, Procmon)
- 🖥️ **Changes System Hostname**
- 🔄 **Automated Backup and Restoration** of original system info
- 📝 **Live Activity Routing** with a built-in Console Dashboard

---

## 🚀 Installation & Usage

### ⚙️ Requirements
- **Python 3.7+**
- **Windows** (for full registry/process manipulation)
- **Administrator Privileges** (Required for the shield to fully embed itself)

### 📥 Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/chadi0x/KillTheWatcher.git
   cd KillTheWatcher
   ```

2. **Run the Script**
   ```bash
   python KillTheWatcher.py
   ```
   *(The script will automatically grab dependencies and request Admin rights if needed)*

### 🛡️ First-Time Workflow
1. Run the application.
2. Select your target virtualization platform (e.g., VMware, VirtualBox).
3. Toggle on your extra shields (CPU Spoofing, Fake Artifacts, Process Guards).
4. Click **🛡️ Apply Mask**.
5. *A backup of your original system info will be created automatically.*
6. **Reboot your system** to ensure all network and hostname changes take effect!

### 🔄 Restoration
- Open the tool again and click **🔄 Restore System**.
- Wait for the success log, and reboot to return your PC to its completely native, original state.

---

## 📋 Supported VM Platforms

| Platform | Manufacturer | MAC Prefix | Hostname Example |
|----------|--------------|-----------|-------------------|
| **VMware** | VMware, Inc. | `00:05:69` | `VMWARE-WEB-01` |
| **VirtualBox**| innotek GmbH | `08:00:27` | `VBOX-SYSTEM` |
| **QEMU** | QEMU | `52:54:00` | `QEMU-MACHINE` |
| **Hyper-V** | Microsoft Corp | `00:15:5D` | `HYPERV-VM` |

---

## ⚠️ Known Limitations
- **Non-Windows Systems**: Full registry-based spoofing only works on Windows. MacOS/Linux are supported but functionally limited.
- **MAC Spoofing Constraints**: Some modern Wi-Fi adapters natively reject manual MAC address spoofing via WMI.
- **Persistence**: Windows Updates may occasionally reset some registry values, requiring you to re-apply the mask.

---

## 🤝 Contributing
Found a bug, have a feature request, or want to add a new spoofing vector? Feel free to open an issue or submit a pull request!

---

## 📛 Disclaimer
- This tool is built for **educational and research purposes only.**
- Use responsibly and legally. The author is not responsible for any misuse of this tool.
- Always back up your system before running aggressive registry tools.

---

## 📄 License & Credits
- Released under the **MIT License**.
- Developed by **[chadi0x](https://github.com/chadi0x)** — *Analyzing the dark to build tools that protect.*
