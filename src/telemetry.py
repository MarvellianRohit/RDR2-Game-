import os
import time
import csv

class TelemetryTracker:
    def __init__(self):
        self.data = [] # List of (timestamp, dt, entities, mem_mb, qt_nodes)
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        print("[Telemetry] System initialized.")

    def record_frame(self, dt, entity_count, mem_bytes, qt_nodes):
        """Records a snapshot of current performance metrics."""
        timestamp = time.time()
        mem_mb = mem_bytes / (1024 * 1024)
        fps = 1.0 / dt if dt > 0 else 0
        self.data.append({
            "Timestamp": f"{timestamp:.3f}",
            "Framerate": f"{fps:.2f}",
            "Active_Entities": entity_count,
            "Memory_MB": f"{mem_mb:.3f}",
            "Active_Quadtree_Nodes": qt_nodes
        })

    def export_session_data(self):
        """Exports the recorded data to a CSV file."""
        if not self.data:
            print("[Telemetry] No data to export.")
            return

        filename = f"session_{int(time.time())}.csv"
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            keys = self.data[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.data)
            print(f"[Telemetry] Session data exported to: {filepath} ({len(self.data)} frames recorded)")
        except Exception as e:
            print(f"[Telemetry] Failed to export data: {e}")
