# TECHTON ⚡
> Enterprise Active Directory Stress Testing & Load Analysis Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Docker-orange.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

**Techton** is a CLI-based stress testing tool designed to rigorously test Active Directory (AD) infrastructure. It simulates real-world authentication storms (e.g., morning boot storms) to identify CPU bottlenecks, memory leaks, and network latency issues before they impact production.

## 🚀 Features

*   **Auto-Pilot Mode:** Automatically calculates optimal Ramp-Up time and Test Duration based on user count.
*   **Real-Time Dashboard:** Monitor Throughput, Latency, and Error Rates directly from the terminal.
*   **History Manager:** Keeps track of all previous tests with Pass/Fail status.
*   **Detailed Reporting:** Generates comprehensive HTML reports (graphs, tables) for post-mortem analysis.
*   **Safety First:** "Kill Switch" mechanism ensures no sensitive credential files are left behind.

## 📋 Prerequisites

*   **Linux OS** (Ubuntu, Debian, CentOS, Kali, etc.)
*   **Docker** (Must be installed and running)

## 📦 Installation

Clone the repository and run the install script:

```bash
git clone https://github.com/YOUR_USERNAME/techton.git
cd techton
./install.sh
```

After installation, you can run Techton from anywhere:

```bash
techton
```

## 🛠️ Usage

1.  Select **[1] Start New Stress Test**.
2.  Enter Target IP and Credentials (User DN).
3.  Set the number of **Users (Threads)**.
4.  Techton will calculate the safe ramp-up time. Press Enter to launch.
5.  Watch the Live Dashboard.
6.  Analyze the recommendation at the end (PASS/WARN/FAIL).

## ⚠️ Disclaimer

This tool is for **Authorized Testing Only**. Using this tool on networks or servers without permission is illegal. The authors are not responsible for any damage caused by misuse.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
