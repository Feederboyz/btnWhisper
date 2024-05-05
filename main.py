import sys
from btnWhisper import BtnWhisper
from PyQt5.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot


class ModifyHotkeyDialog(QDialog):
    emit_modified_hotkey = pyqtSignal(str)

    def __init__(self, my_app):
        super(ModifyHotkeyDialog, self).__init__()
        self.my_app = my_app
        self.key_sequence = QKeySequence()
        self.setWindowTitle("Modify hotkey")
        self.resize(200, 100)
        self.init_ui()
        self.grabKeyboard()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("按鍵組合將顯示在這裡", self)
        layout.addWidget(self.label)
        confirm_button = QPushButton("Confirm", self)
        confirm_button.clicked.connect(self.confirm)
        self.emit_modified_hotkey.connect(self.my_app.btn_whisper.set_recording_hotkey)
        layout.addWidget(confirm_button)
        self.setLayout(layout)

    def confirm(self):
        print("Confirming key sequence:", self.key_sequence.toString())
        self.releaseKeyboard()
        self.emit_modified_hotkey.emit(self.key_sequence.toString())
        self.hide()

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            modifiers = event.modifiers()
            ctrl = modifiers & Qt.ControlModifier
            shift = modifiers & Qt.ShiftModifier
            alt = modifiers & Qt.AltModifier
            key = (
                event.key()
                if event.key() != Qt.Key_Control and event.key() != Qt.Key_Shift
                else None
            )

            text = "{}{}{}{}{}{}{}".format(
                "ctrl" if ctrl else "",
                "+" if ctrl and (alt or shift or key) else "",
                "alt" if alt else "",
                "+" if alt and (shift or key) else "",
                "shift" if shift else "",
                "+" if shift and key else "",
                chr(key).lower() if key and key <= 255 else "",
            )
            self.key_sequence = QKeySequence(text)
            self.label.setText(text)

    def closeEvent(self, event):
        """Reimplement the close event to hide the window instead of closing it."""
        event.ignore()
        self.hide()


class MySystemTrayIcon(QSystemTrayIcon):
    def __init__(self, my_app, icon, parent=None):
        super(MySystemTrayIcon, self).__init__(icon, parent)
        self.my_app = my_app
        self.setToolTip("Button Whisper")
        self.menu = self.create_tray_menu()
        self.setContextMenu(self.menu)
        self.show()

    def create_tray_menu(self):

        def open_modify_hotkey_dialog():
            dialog = ModifyHotkeyDialog(self.my_app)
            dialog.exec_()

        menu = QMenu()
        modify_hotkey_action = menu.addAction("Modify hotkey")
        modify_hotkey_action.triggered.connect(open_modify_hotkey_dialog)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit_app)
        return menu

    def quit_app(self):
        self.my_app.btn_whisper.delete_sound_file()
        self.my_app.quit()


class MyApp:
    def __init__(self):
        print("Initializing...")
        self.btn_whisper = BtnWhisper()
        self.app = QApplication(sys.argv)
        self.tray_icon = MySystemTrayIcon(self, QIcon("images/32x32.png"))
        print("Start")

    def run(self):
        self.app.exec_()

    def quit(self):
        self.app.quit()


if __name__ == "__main__":
    my_app = MyApp()
    my_app.run()
