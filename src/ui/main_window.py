# -*- coding: utf-8 -*-
"""
Main installer window - wizard-style multi-step UI.
"""

import os
import sys

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from src import config
from src.api.github import get_download_url, get_versions_with_lyte_exe
from src.installer_logic import get_default_install_dir, install
from src.ui.theme import get_stylesheet


class InstallWorker(QThread):
    """Background thread for installation."""
    progress = Signal(str, int, int)
    log_line = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, install_dir, version, install_vlc, add_start_menu, add_desktop, uninstaller_path):
        super().__init__()
        self.install_dir = install_dir
        self.version = version
        self.install_vlc = install_vlc
        self.add_start_menu = add_start_menu
        self.add_desktop = add_desktop
        self.uninstaller_path = uninstaller_path

    def run(self):
        try:
            url = get_download_url(self.version)
            app_icon_path = config.get_app_icon_path()
            install(
                self.install_dir,
                url,
                self.install_vlc,
                self.add_start_menu,
                self.add_desktop,
                self.uninstaller_path,
                app_icon_path,
                lambda msg, cur, tot: self.progress.emit(msg, cur, tot),
                lambda line: self.log_line.emit(line),
            )
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LYTE Setup")
        self.setMinimumSize(560, 420)
        self.setStyleSheet(get_stylesheet())

        # State
        self.versions: list[tuple[str, str]] = []
        self.selected_version = "latest"
        self.install_dir = get_default_install_dir()
        self.install_vlc = True
        self.add_start_menu = True
        self.add_desktop = True
        self.worker: InstallWorker | None = None

        # Icon
        icon_path = config.get_install_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 8, 24, 24)

        # Header image (banner at top)
        header_path = config.get_header_path()
        if header_path and os.path.isfile(header_path):
            header_label = QLabel()
            pixmap = QPixmap(header_path)
            if not pixmap.isNull():
                header_label.setPixmap(pixmap.scaledToWidth(512, Qt.TransformationMode.SmoothTransformation))
                header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(header_label)

        self.stack = QStackedWidget()
        self.stack.setObjectName("stack")

        # Build pages
        self._add_welcome_page()
        self._add_version_page()
        self._add_directory_page()
        self._add_components_page()
        self._add_shortcuts_page()
        self._add_progress_page()
        self._add_finish_page()

        layout.addWidget(self.stack)

        # Separator line above buttons
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #465a46; max-height: 1px;")
        layout.addWidget(separator)

        # Buttons: Back left, Next and Cancel right-aligned
        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self._go_back)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self._go_next)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        btn_layout.addSpacing(8)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.current_page = 0
        self._update_buttons()

    def _add_welcome_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Welcome to LYTE Setup")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("This wizard will guide you through the installation of LYTE.\n\nClick Next to continue.")
        desc.setProperty("class", "secondary")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addStretch()
        self.stack.addWidget(w)

    def _add_version_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Select LYTE Version")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("Choose which LYTE release to download. The latest version is recommended for most users.")
        desc.setProperty("class", "secondary")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(280)
        self.version_combo.currentIndexChanged.connect(self._on_version_changed)
        layout.addWidget(self.version_combo)
        self.download_link_label = QLabel()
        self.download_link_label.setProperty("class", "secondary")
        self.download_link_label.setWordWrap(True)
        self.download_link_label.setOpenExternalLinks(True)
        layout.addWidget(self.download_link_label)
        releases_link = QLabel(
            '<a href="https://github.com/StroepWafel/LYTE/releases">View all releases on GitHub</a>'
        )
        releases_link.setProperty("class", "secondary")
        releases_link.setOpenExternalLinks(True)
        layout.addWidget(releases_link)
        layout.addStretch()
        self.stack.addWidget(w)

    def _add_directory_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Choose Install Location")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("Select the folder where LYTE will be installed.")
        desc.setProperty("class", "secondary")
        layout.addWidget(desc)
        row = QGridLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.install_dir)
        self.dir_edit.textChanged.connect(lambda t: setattr(self, "install_dir", t))
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_dir)
        row.addWidget(QLabel("Directory:"), 0, 0)
        row.addWidget(self.dir_edit, 0, 1)
        row.addWidget(browse_btn, 0, 2)
        layout.addLayout(row)
        layout.addStretch()
        self.stack.addWidget(w)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Install Directory", self.install_dir)
        if d:
            self.install_dir = d
            self.dir_edit.setText(d)

    def _add_components_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Select Components")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("Choose which additional components you want to install with LYTE.")
        desc.setProperty("class", "secondary")
        layout.addWidget(desc)
        self.vlc_check = QCheckBox("VLC Media Player (playback support; needs ~60MB free space)")
        self.vlc_check.setChecked(True)
        self.vlc_check.toggled.connect(lambda v: setattr(self, "install_vlc", v))
        layout.addWidget(self.vlc_check)
        layout.addStretch()
        self.stack.addWidget(w)

    def _add_shortcuts_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Choose Shortcuts")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("Select where you would like shortcuts to be created.")
        desc.setProperty("class", "secondary")
        layout.addWidget(desc)
        self.start_menu_check = QCheckBox("Create Start Menu shortcut")
        self.start_menu_check.setChecked(True)
        self.start_menu_check.toggled.connect(lambda v: setattr(self, "add_start_menu", v))
        layout.addWidget(self.start_menu_check)
        self.desktop_check = QCheckBox("Create Desktop shortcut")
        self.desktop_check.setChecked(True)
        self.desktop_check.toggled.connect(lambda v: setattr(self, "add_desktop", v))
        layout.addWidget(self.desktop_check)
        layout.addStretch()
        self.stack.addWidget(w)

    def _add_progress_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Installing...")
        title.setProperty("class", "title")
        layout.addWidget(title)
        ps_note = QLabel("Note: A PowerShell window may briefly flash during installation when creating shortcuts—this is normal.")
        ps_note.setProperty("class", "secondary")
        ps_note.setWordWrap(True)
        layout.addWidget(ps_note)
        self.progress_label = QLabel("Preparing...")
        self.progress_label.setProperty("class", "secondary")
        layout.addWidget(self.progress_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        log_label = QLabel("Log:")
        log_label.setProperty("class", "secondary")
        layout.addWidget(log_label)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(120)
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #232323;
                color: #dcdcdc;
                border: 1px solid #465a46;
                border-radius: 8px;
                padding: 8px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.log_text)
        layout.addStretch()
        self.stack.addWidget(w)

    def _add_finish_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("Installation Complete")
        title.setProperty("class", "title")
        layout.addWidget(title)
        desc = QLabel("LYTE has been successfully installed on your computer.\n\nClick Finish to exit the setup wizard.")
        desc.setProperty("class", "secondary")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        self.launch_check = QCheckBox("Launch LYTE")
        self.launch_check.setChecked(True)
        layout.addWidget(self.launch_check)
        layout.addStretch()
        self.stack.addWidget(w)

    def _update_buttons(self):
        n = self.stack.count()
        self.back_btn.setVisible(self.current_page > 0 and self.current_page != 5)
        if self.current_page == 0:
            self.next_btn.setText("Next")
        elif self.current_page == 4:
            self.next_btn.setText("Install")
        elif self.current_page == 5:
            self.back_btn.setVisible(False)
            self.next_btn.setVisible(False)
            self.cancel_btn.setText("Close")
        elif self.current_page == 6:
            self.next_btn.setText("Finish")
            self.back_btn.setVisible(False)
        else:
            self.next_btn.setText("Next")
        self.cancel_btn.setVisible(self.current_page not in (5, 6))

    def _go_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.setCurrentIndex(self.current_page)
            self._update_buttons()

    def _go_next(self):
        if self.current_page == 0:
            self.current_page = 1
            self.stack.setCurrentIndex(1)
            self._load_versions()
        elif self.current_page == 1:
            idx = self.version_combo.currentIndex()
            if idx >= 0 and self.versions:
                self.selected_version = self.versions[idx][1]
            self.current_page = 2
            self.stack.setCurrentIndex(2)
        elif self.current_page == 2:
            self.install_dir = self.dir_edit.text().strip() or get_default_install_dir()
            self.current_page = 3
            self.stack.setCurrentIndex(3)
        elif self.current_page == 3:
            self.install_vlc = self.vlc_check.isChecked()
            self.current_page = 4
            self.stack.setCurrentIndex(4)
        elif self.current_page == 4:
            self.add_start_menu = self.start_menu_check.isChecked()
            self.add_desktop = self.desktop_check.isChecked()
            self._start_install()
        elif self.current_page == 6:
            if self.launch_check.isChecked():
                lyte_exe = os.path.join(self.install_dir, "LYTE.exe")
                if os.path.isfile(lyte_exe):
                    os.startfile(lyte_exe)
            QApplication.quit()
        self._update_buttons()

    def _on_version_changed(self):
        """Update the download link when version selection changes."""
        if not self.versions:
            self.download_link_label.setText("")
            return
        idx = self.version_combo.currentIndex()
        if idx < 0:
            return
        tag = self.versions[idx][1]
        url = get_download_url(tag)
        self.download_link_label.setText(f'Download: <a href="{url}">{url}</a>')

    def _load_versions(self):
        try:
            self.versions = get_versions_with_lyte_exe()
            self.version_combo.clear()
            for display, tag in self.versions:
                self.version_combo.addItem(display, tag)
            if self.versions:
                self.version_combo.setCurrentIndex(0)
                self._on_version_changed()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to fetch versions: {e}\n\nPlease check your internet connection and try again.",
            )
            self.current_page = 0
            self.stack.setCurrentIndex(0)

    def _start_install(self):
        self.current_page = 5
        self.stack.setCurrentIndex(5)
        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self._update_buttons()

        # Resolve uninstaller path (bundled in installer or same dir when dev)
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
            uninstaller_path = os.path.join(base, "Uninstall LYTE.exe")
        else:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            uninstaller_path = os.path.join(base, "dist", "Uninstall LYTE.exe")
        if not os.path.isfile(uninstaller_path):
            QMessageBox.critical(
                self,
                "Error",
                "Uninstaller not found. Please rebuild the installer.",
            )
            self.next_btn.setEnabled(True)
            self.back_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.current_page = 4
            self.stack.setCurrentIndex(4)
            return

        self.log_text.clear()
        self.worker = InstallWorker(
            self.install_dir,
            self.selected_version,
            self.install_vlc,
            self.add_start_menu,
            self.add_desktop,
            uninstaller_path,
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.log_line.connect(self._on_log_line)
        self.worker.finished.connect(self._on_install_finished)
        self.worker.start()

    def _on_progress(self, msg: str, cur: int, tot: int):
        self.progress_label.setText(msg)
        if tot > 0:
            self.progress_bar.setValue(int(100 * cur / tot))

    def _on_log_line(self, line: str):
        self.log_text.appendPlainText(line)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_install_finished(self, success: bool, err: str):
        self.next_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        if success:
            self.current_page = 6
            self.stack.setCurrentIndex(6)
            self.next_btn.setVisible(True)
            self.next_btn.setText("Finish")
        else:
            QMessageBox.critical(self, "Installation Failed", f"An error occurred:\n\n{err}")
            self.current_page = 4
            self.stack.setCurrentIndex(4)
            self.back_btn.setEnabled(True)
        self._update_buttons()

    def _cancel(self):
        if self.current_page == 5 and self.worker and self.worker.isRunning():
            return  # Don't allow cancel during install
        QApplication.quit()
