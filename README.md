# DataCenterDiagnosticTool

A Python-based tool for Microsoft Senior Data Center Technicians to manage hardware diagnostics, track issues, generate reports, suggest escalations, and log activities for compliance and auditing in data center operations.

## Overview
The **DataCenterDiagnosticTool** is designed to support data center technicians in performing and documenting hardware diagnostics, troubleshooting, and process adherence. It provides a command-line interface to:
- Register and manage hardware (e.g., servers, switches, storage, racks).
- Log diagnostic data (temperature, CPU usage, memory usage) and detect issues based on configurable thresholds.
- Generate detailed diagnostic reports for specific or all hardware.
- Suggest escalations for hardware issues requiring further action.
- Log all activities (e.g., hardware additions, diagnostics, reports) to an audit trail for compliance and process improvement.

This tool aligns with the responsibilities of a Senior Data Center Technician, including expertise in diagnostics, adherence to standards, escalation protocols, and mentoring others through clear documentation.

## Features
- **Hardware Management**: Add and track hardware with type, serial number, and location.
- **Diagnostic Logging**: Record diagnostic data (temperature, CPU, memory) and automatically detect issues against predefined thresholds.
- **Reporting**: Generate detailed reports summarizing diagnostics and issue trends.
- **Escalation Suggestions**: Identify hardware issues requiring escalation to management or specialists.
- **Activity Logging**: Record all actions (including errors) in `activity.log` with timestamps and technician details for compliance and auditing.
- **Persistent Storage**: Use a SQLite database (`hardware.db`) to store hardware and diagnostic data.
- **Configurable**: Customize hardware types and diagnostic thresholds via `diagnostic_config.json`.

## Setup
1. **Clone the Repository**:
````
   git clone https://github.com/<your-username>/DataCenterDiagnosticTool.git
   cd DataCenterDiagnosticTool
````
2. **Install Dependencies**: Ensure Python 3.6+ is installed, then install required packages:
````
    pip install -r requirements.txt
````
3. **Run the script**:
````
    python datacenter_diagnostic_tool.py
````

## Usage
The tool provides a command-line interface with the following options:

- **Add Hardware**: Register new hardware with type, serial number, location, and technician name.
- **Log Diagnostic**: Record diagnostic data (temperature, CPU usage, memory usage) for specific hardware, including technician details.
- **Generate Diagnostic Report**: View detailed reports for all hardware or a specific serial number, including issue summaries.
- **Suggest Escalations**: Identify hardware issues requiring escalation to management or specialists.
- **Exit**: Close the application.#
