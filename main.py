import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPalette, QColor, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GUI.main_window import MainWindow


def create_splash_pixmap() -> QPixmap:
    pixmap = QPixmap(600, 350)
    pixmap.fill(QColor("#0a0a0f"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    font = QFont("Arial", 28, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "Like Math But Not Math")
    font.setPointSize(14);
    font.setBold(False)
    painter.setFont(font)
    painter.setPen(QColor("#aaaaaa"))
    painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignCenter, "Theory of Computation · FUE CS Dept")
    painter.end()
    return pixmap


def set_dark_theme(app: QApplication):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1a1a24"))
    palette.setColor(QPalette.WindowText, QColor("#e8e8f0"))
    palette.setColor(QPalette.Base, QColor("#111118"))
    palette.setColor(QPalette.AlternateBase, QColor("#1a1a24"))
    palette.setColor(QPalette.Text, QColor("#e8e8f0"))
    palette.setColor(QPalette.Button, QColor("#2a2a38"))
    palette.setColor(QPalette.ButtonText, QColor("#e8e8f0"))
    palette.setColor(QPalette.Highlight, QColor("#7c6af7"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Link, QColor("#7c6af7"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#555566"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#555566"))
    app.setPalette(palette)

    # Stylesheet from original request
    stylesheet = """
        QPushButton { background-color: #7c6af7; color: white; border-radius: 8px; padding: 8px 16px; border: none; }
        QPushButton:hover { background-color: #6658d4; }
        QPushButton:pressed { background-color: #5548b4; }
        QPushButton:disabled { background-color: #2a2a38; color: #555566; }
        QTextEdit, QLineEdit, QSpinBox { background-color: #111118; color: #e8e8f0; border: 1px solid #2a2a38; border-radius: 6px; padding: 6px; }
        QComboBox { background-color: #111118; color: #e8e8f0; border: 1px solid #2a2a38; border-radius: 6px; padding: 6px; }
        QComboBox::drop-down { border-left: 1px solid #2a2a38; }
        QTabWidget::pane { border: 1px solid #2a2a38; background-color: #111118; }
        QTabBar::tab { background: #1a1a24; color: #e8e8f0; padding: 8px 16px; border: 1px solid #2a2a38; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #111118; border-bottom: 2px solid #7c6af7; }
        QTabBar::tab:hover:!selected { background: #2a2a38; }
        QScrollBar:vertical { border: none; background: #111118; width: 8px; }
        QScrollBar::handle:vertical { background: #7c6af7; min-height: 20px; border-radius: 4px; }
        QScrollBar:horizontal { border: none; background: #111118; height: 8px; }
        QScrollBar::handle:horizontal { background: #7c6af7; min-width: 20px; border-radius: 4px; }
    """
    app.setStyleSheet(stylesheet)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Like Math But Not Math")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Future University Egypt")
    set_dark_theme(app)

    splash = QSplashScreen(create_splash_pixmap(), Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    time.sleep(3)  # Splash screen duration

    window = MainWindow()
    window.showMaximized()
    splash.finish(window)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()