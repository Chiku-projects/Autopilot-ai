from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QListWidget, QMessageBox
)
from PySide6.QtCore import QTimer

from api_client import create_task, get_task, confirm_task, cancel_task


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPilot AI")
        self.resize(480, 420)
        self.current_task_id = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("What should I do?"))

        input_row = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.run_command)
        input_row.addWidget(self.command_input)
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_command)
        input_row.addWidget(run_btn)
        layout.addLayout(input_row)

        self.status_label = QLabel("Status: idle")
        layout.addWidget(self.status_label)

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.clicked.connect(self.stop_task)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_status)
        self.timer.setInterval(1000)

    def run_command(self):
        goal = self.command_input.text().strip()
        if not goal:
            return
        self.history_list.clear()
        self.current_task_id = create_task(goal)
        self.stop_btn.setEnabled(True)
        self.timer.start()

    def stop_task(self):
        if self.current_task_id:
            cancel_task(self.current_task_id)

    def poll_status(self):
        if not self.current_task_id:
            return
        data = get_task(self.current_task_id)
        self.status_label.setText(f"Status: {data['status']}")

        self.history_list.clear()
        for step in data["history"]:
            mark = "OK" if step["success"] else "FAIL"
            self.history_list.addItem(f"{mark} {step['action']}({step['arguments']})")

        if data["status"] == "awaiting_confirmation" and data["pending_step"]:
            step = data["pending_step"]
            reply = QMessageBox.question(
                self, "AutoPilot wants to:",
                f"{step['action']}({step['arguments']})\nReason: {step['reason']}\n\nAllow?",
                QMessageBox.Yes | QMessageBox.No,
            )
            confirm_task(self.current_task_id, reply == QMessageBox.Yes)

        if data["status"] in ("completed", "failed", "cancelled", "timeout", "max_steps_exceeded"):
            self.timer.stop()
            self.stop_btn.setEnabled(False)