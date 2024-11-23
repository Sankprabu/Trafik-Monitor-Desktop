from PyQt6.QtWidgets import QDialog, QVBoxLayout, QSpinBox, QComboBox, QLabel, QPushButton
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 250, 200)
        self.layout = QVBoxLayout()

        # Interval Update
        self.interval_label = QLabel("Update Interval (seconds):")
        self.layout.addWidget(self.interval_label)
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setRange(1, 60)  # 1 to 60 seconds
        self.interval_spinbox.setValue(1)  # Default: 1 second
        self.layout.addWidget(self.interval_spinbox)

        # Theme selection
        self.theme_label = QLabel("Choose Theme:")
        self.layout.addWidget(self.theme_label)
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        self.layout.addWidget(self.theme_combo)

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_settings(self):
        """Save the selected settings and return to the main window."""
        update_interval = self.interval_spinbox.value()
        selected_theme = self.theme_combo.currentText()
        
        # Emit signals or directly pass data to the main window
        self.accept()  # Close the dialog
        
        # Print the chosen settings (or update the main window)
        print(f"Interval: {update_interval}, Theme: {selected_theme}")
        
        # Return the selected settings
        return update_interval, selected_theme
