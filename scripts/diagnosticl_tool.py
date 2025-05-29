import sqlite3
import json
import datetime
import os
from typing import Dict, List

class DiagnosticTool:
    def __init__(self, db_file: str="hardware.db", config_file: str = "/config/diagnostic_config.json", log_file = "/logs/activity.log"):
        self._db = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._config = json.load_config(config_file)
        self.create_tables()
        self.log_activity("System", "Initialized Diagnostic Tool")

    def log_activity(self, technician: str, action: str) -> None:
        """Log diagnostic tool activity"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] Technician: {technician} | Action: {action}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)

    
    def load_config(self, config_file: str) -> Dict:
        """Load hardware types and diagnostic threshold from config file"""
        if not os.path.exists(config_file):
            default_config = {
                "hardware_types": ["Server", "Switch", "Storage", "Disk"],
                "diagnostic_thresholds": {
                    "max_temperature_celsius": 40,
                    "max_cpu_usage_percentage": 90,
                    "max_memory_usage_percentage": 85
                }
            }
            with open(config_file, 'w') as file:
                json.dump(default_config, file)
            self.log_activity("System", f"Created default config file: {config_file}")
            return default_config
        with open(config_file, "r") as file:
            config = json.load(file)
            self.log_activity("System", f"Loaded config file: {config_file}")
            return config
        
    def create_tables(self) -> None:
        """Create SQLite tables for hardware and diagnostic"""
        self.cursor.execute( '''
            CREATE TABLE IF NOT EXISTS hardware (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                serial_number TEXT UNIQUE,
                location TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                hardware_id INTEGER,
                technician TEXT,
                timestamp TEXT,
                temperature_celsius REAL,
                cpu_usage_precent REAL,
                memory_usage_percent REAL,
                issue_detected TEXT,
                FOREIGN KEY (hardware_id) REFERENCES hardware(id)
            )
        ''')
        self.conn.commit()
        self.log_activity("System", "Initialized database tables")


    def add_hardware(self, hardware_type: str, serial_number: str, location: str, technician: str) -> None:
        """Add a new hardware entry"""
        if hardware_type not in self.config['hardware_types']:
            error_message = (f"Hardware type {hardware_type} is not supported. Choose from {self.config['hardware_types']}")
            self.log_activity(technician, f"Failed to add hardware: {error_msg}")
            raise ValueError(error_message)
        try:
            self.cursor.execute(
             "INSERT INTO hardware (type, serial_number, location) VALUES (?,?,?)",
                [hardware_type, serial_number, location]
            )
            self.conn.commit()
            self.log_activity(technician, f"Added hardware: {hardware_type}, Serial: {serial_number}, Location: {location}")
        except sqlite3.IntegrityError:
            error_message = f"Hardware with serial number {serial_number} already exists."
            self.log_activity(technician, f"Failed to add hardware: {error_msg}")
            raise ValueError(error_message)
        
    def log_diagnostic(self, serial_number: str, technician: str, temperature: float, cpu_usage: float, memory_usage: float) -> None:
        """Log diagnostic data for hardware device"""
        self.cursor.execute("SELECT id FROM hardware WHERE serial_number = ?", (serial_number,))
        hardware_id = self.cursor.fetchone()
        if not hardware_id:
            error_message = f"Hardware with serial number {serial_number} not found."
            self.log_activity(technician, f"Failed to log diagnostic data: {error_msg}")
            raise ValueError(error_message)
        
        issue = self.check_issues(temperature, cpu_usage, memory_usage)
        self.cursor.execute('''
            INSERT INTO diagnostics (hardware_id, technician, temperature, cpu_usage, memory_usage, issue) 
            VALUES (?,?,?,?,?,?)''', (hardware_id[0], technician, temperature, cpu_usage, memory_usage, issue)
        )
        self.conn.commit()
        self.log_activity(technician, f"Logged diagnostic for Serial: {serial_number}, Issue: {issue}")

    def check_issue(self, temperature: float, cpu_usage: float, memory_usage: float) -> str:
        """Check hardware issues"""
        issues = []
        if temperature > self.config["diagnostic_threshold"]["max_temperature_celsius"]:
            issues.append(f"Temperature exceeds {self.config['diagnostic_threshold']['max_temperature_celsius']}°C")
        if cpu_usage > self.config["diagnostic_threshold"]["max_cpu_usage"]:
            issues.append(f"CPU usage exceeds {self.config["diagnostic_threshold"]["max_cpu_usage"]}%")
        if memory_usage > self.config["diagnostic_threshold"]["max_memory_usage"]:
            issues.append(f"Memory usage exceeds {self.config['diagnostic_threshold']['max_memory_usage']}MB")
        return ", ".join(issues) if issues else "No issue detected"
    
    def generate_diagnostic_report(self, serial_number: str = None, technician: str = "System") -> Dict:
        """Generate a report for all or specific hardware"""
        query = "SELECT h.serial_number, h.type, h.location, d.technician, d.timestamp, d.temperature_celsius, "\
                "d.cpu_usage_percent, d.memory_usage_percent, d.issue_detected FROM hardware as h JOIN diagnostics as d ON h.id = d.hardware_id"
        params = ()
        if serial_number:
            query += " WHERE h.serial_number =?"
            params = (serial_number,)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        report = {
            "total_diagnostics": len(rows),
            "diagnostics": [
                {
                    "serial_number": row[0],
                    "type": row[1],
                    "location": row[2],
                    "technician": row[3],
                    "timestamp": row[4],
                    "temperature_celsius": row[5],
                    "cpu_usage_percent": row[6],
                    "memory_usage_percent": row[7],
                    "issue_detected": row[8]
                } for row in rows
            ],
            "issue_summary": self._summarize_issues(rows)
        }
        self.log_activity(technician, f"Generated diagnostic report for {'all hardware' if not serial_number else f'Serial: {serial_number}'}")
        return report
    def _summarize_issues(self, rows: List) -> Dict:
        """Summarize issues detected in diagnostics."""
        issue_counts = {"Temperature": 0, "CPU": 0, "Memory": 0, "No issues": 0}
        for row in rows:
            issue = row[8]
            if "Temperature" in issue:
                issue_counts["Temperature"] += 1
            if "CPU" in issue:
                issue_counts["CPU"] += 1
            if "Memory" in issue:
                issue_counts["Memory"] += 1
            if issue == "No issues detected":
                issue_counts["No issues"] += 1
        return issue_counts

    def suggest_escalations(self, technician: str = "System") -> List[str]:
        """Suggest escalations based on diagnostic issues."""
        report = self.generate_diagnostic_report(technician=technician)
        escalations = []
        for diagnostic in report["diagnostics"]:
            if diagnostic["issue_detected"] != "No issues detected":
                escalations.append(
                    f"Escalate: Hardware {diagnostic['serial_number']} ({diagnostic['type']}) "
                    f"at {diagnostic['location']} - Issue: {diagnostic['issue_detected']}"
                )
        self.log_activity(technician, f"Suggested escalations: {len(escalations)} issues found")
        return escalations

    def __del__(self):
        """Close database connection."""
        self.conn.close()
        self.log_activity("System", "Closed DataCenterDiagnosticTool")

def main():
    tool = DataCenterDiagnosticTool()
    while True:
        print("\nData Center Diagnostic Tool")
        print("1. Add Hardware")
        print("2. Log Diagnostic")
        print("3. Generate Diagnostic Report")
        print("4. Suggest Escalations")
        print("5. Exit")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            technician = input("Enter technician name: ")
            hardware_type = input(f"Enter hardware type {tool.config['hardware_types']}: ")
            serial_number = input("Enter serial number: ")
            location = input("Enter location (e.g., Rack 1A): ")
            try:
                tool.add_hardware(hardware_type, serial_number, location, technician)
                print("Hardware added successfully!")
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == "2":
            technician = input("Enter technician name: ")
            serial_number = input("Enter hardware serial number: ")
            temperature = float(input("Enter temperature (°C): "))
            cpu_usage = float(input("Enter CPU usage (%): "))
            memory_usage = float(input("Enter memory usage (%): "))
            try:
                tool.log_diagnostic(serial_number, technician, temperature, cpu_usage, memory_usage)
                print("Diagnostic logged successfully!")
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == "3":
            technician = input("Enter technician name: ")
            serial_number = input("Enter serial number for specific report (or press Enter for all): ")
            report = tool.generate_diagnostic_report(serial_number if serial_number else None, technician)
            print("\nDiagnostic Report:")
            print(f"Total Diagnostics: {report['total_diagnostics']}")
            print("Issue Summary:", report["issue_summary"])
            for diag in report["diagnostics"]:
                print(f"\n- Serial: {diag['serial_number']}, Type: {diag['type']}, Location: {diag['location']}")
                print(f"  Technician: {diag['technician']}, Time: {diag['timestamp']}")
                print(f"  Temp: {diag['temperature_celsius']}°C, CPU: {diag['cpu_usage_percent']}%, "
                      f"Memory: {diag['memory_usage_percent']}%")
                print(f"  Issue: {diag['issue_detected']}")
        elif choice == "4":
            technician = input("Enter technician name: ")
            escalations = tool.suggest_escalations(technician)
            print("\nEscalation Suggestions:")
            for escalation in escalations:
                print(f"- {escalation}")
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()


