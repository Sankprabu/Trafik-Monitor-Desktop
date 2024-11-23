from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMenu
from PyQt6.QtGui import QAction, QContextMenuEvent
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSystemTrayIcon
from pyqtgraph import PlotWidget, mkPen
import psutil
import os
import sys
import win32com.client
import pyqtgraph as pg
from settings_dialog import SettingsDialog


class TrafikMonitorDesktop(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(150, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.9)

        self.set_default_position()

        self.layout = QVBoxLayout()

        # Tambahkan grafik (tapi sembunyikan saat pertama kali dibuka)
        self.graph_widget = pg.PlotWidget(self)
        self.graph_widget.setBackground("#2E3440")
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)

        pen = pg.mkPen(color="#88C0D0", width=2)
        self.download_line = self.graph_widget.plot([], [], pen=pen, name="Download")
        self.upload_line = self.graph_widget.plot([], [], pen=pg.mkPen(color="#A3BE8C", width=2), name="Upload")

        self.time_data = list(range(60))  # Last 60 seconds
        self.download_data = [0] * 60
        self.upload_data = [0] * 60

        # Tambahkan grafik ke layout, tetapi sembunyikan dulu
        self.layout.addWidget(self.graph_widget)
        self.graph_widget.hide()  # Sembunyikan grafik saat pertama kali tampil

        # Tambahkan label di bawah grafik
        self.label_download = QLabel("Download: - KB/s", self)
        self.label_upload = QLabel("Upload: - KB/s", self)

        self.layout.addWidget(self.label_download)
        self.layout.addWidget(self.label_upload)

        self.setLayout(self.layout)

        self.offset = None

        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                border-radius: 10px;
            }
            QLabel {
                color: #D8DEE9;
                font-size: 16px;
                font-family: Arial, sans-serif;
            }
        """)
        self.initial_graph_position = self.graph_widget.pos()

        self.stat_awal = psutil.net_io_counters()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_trafik)
        self.timer.start(1000)

        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip("Traffic Monitor")
        self.tray_icon.activated.connect(self.restore_from_tray)

        # Tray menu

        tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)  # Menampilkan dialog pengaturan
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(show_action)
        tray_menu.addAction(settings_action)  # Menambahkan opsi pengaturan
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def set_default_position(self):
        """Set the app's default position at the bottom-right corner of the desktop."""
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.width() - self.width() - 10
        y = screen_geometry.height() - self.height() - 30
        self.move(x, y)

    def update_trafik(self):
        """Update download and upload speed, and the graph."""
        try:
            stat_akhir = psutil.net_io_counters()
            download_speed = (stat_akhir.bytes_recv - self.stat_awal.bytes_recv) / 1024  # KB/s
            upload_speed = (stat_akhir.bytes_sent - self.stat_awal.bytes_sent) / 1024  # KB/s

            # Update label teks
            self.label_download.setText(f"Download: {download_speed:.2f} KB/s")
            self.label_upload.setText(f"Upload: {upload_speed:.2f} KB/s")

            # Update data grafik
            self.download_data = self.download_data[1:] + [download_speed]
            self.upload_data = self.upload_data[1:] + [upload_speed]

            self.download_line.setData(self.time_data, self.download_data)
            self.upload_line.setData(self.time_data, self.upload_data)

            # Update statistik awal
            self.stat_awal = stat_akhir
        except Exception as e:
        # Gagal memperbarui statistik (misalnya, jika aplikasi ditutup)
            print(f"Terjadi kesalahan: {e}")

    def restore_from_tray(self, reason):
        """Restore the application from the tray to the screen."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.graph_widget.move(self.initial_graph_position)

    def exit_application(self):
        """Exit the application."""
        self.timer.stop()  # Menghentikan timer
        QApplication.quit()  # Menghentikan aplikasi

    def closeEvent(self, event):
        """Hide the application to tray when closed."""
        self.timer.stop()  # Menghentikan timer ketika aplikasi ditutup
        self.hide()  # Menyembunyikan aplikasi ke tray
        #event.ignore()  # Menjaga aplikasi tetap berjalan

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Show context menu on right-click of the widget."""
        menu = QMenu(self)
        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.hide)
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)

        menu.addAction(minimize_action)
        menu.addAction(close_action)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseDoubleClickEvent(self, event):
        """Tampilkan atau sembunyikan grafik saat double-click."""
        if self.graph_widget.isVisible():
            self.graph_widget.hide()  # Sembunyikan grafik
            self.graph_widget.move(self.initial_graph_position)
        else:
            self.graph_widget.show()  # Tampilkan grafik
            self.graph_widget.move(self.initial_graph_position)

    def show_settings_dialog(self):
        """Menampilkan dialog pengaturan."""
        settings_dialog = SettingsDialog()
        settings_dialog.exec()  # Menampilkan dialog pengaturan
        
        # Setelah pengaturan disimpan, Anda dapat melakukan aksi lebih lanjut
        # Misalnya memperbarui interval timer atau tema aplikasi
        update_interval = settings_dialog.interval_spinbox.value()
        self.timer.setInterval(update_interval * 1000)  # Ubah interval timer sesuai pengaturan
        selected_theme = settings_dialog.theme_combo.currentText()
        self.change_theme(selected_theme)

    def change_theme(self, theme):
        """Ubah tema aplikasi."""
        if theme == "Dark":
            self.setStyleSheet("QWidget { background-color: #2E3440; color: white; }")
        elif theme == "Light":
            self.setStyleSheet("QWidget { background-color: white; color: black; }")

def add_to_startup():
    """Add the application to Windows startup."""
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_folder, "TrafficMonitor.lnk")

    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = sys.executable
        shortcut.WorkingDirectory = os.path.dirname(sys.executable)
        shortcut.IconLocation = sys.executable
        shortcut.save()

    
if __name__ == "__main__":
    add_to_startup()
    app = QApplication([])
    window = TrafikMonitorDesktop()
    window.show()
    app.exec()