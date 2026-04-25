import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QLabel, QLineEdit,
    QTabWidget, QListWidget, QSpinBox, QSplitter, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from Core.enumerator import enumerate_strings
from controller import convert
from GUI.dfa_canvas import DFACanvas


class ConvertWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, input_type, input_text):
        super().__init__()
        self.input_type = input_type
        self.input_text = input_text

    def run(self):
        result = convert(self.input_type, self.input_text)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    PLACEHOLDERS = {
        'Regular Expression': '(a|b)*abb',
        'DFA': 'states: q0,q1,q2\nalphabet: a,b\nstart: q0\naccept: q2\ntransitions:\n  q0,a -> q1\n  q1,b -> q2',
        'NFA': 'states: q0,q1\nalphabet: a,b\nstart: q0\naccept: q1\ntransitions:\n  q0,a -> q0,q1\n  q0,b -> q0',
        'CFG (Regular)': 'S -> aS | bA | ε\nA -> bA | b',
        'String Generator': 'ab\nba\nabb\nbba'
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formal Language Converter")
        self.resize(1200, 800)
        self._current_dfa = None
        self.setup_menu()
        self.setup_ui()
        self.on_type_changed()

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: QMessageBox.about(self, "About", "Formal Language Converter v1.0"))
        help_menu.addAction(about_action)

    def setup_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.PLACEHOLDERS.keys())
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.input_edit = QTextEdit()
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.on_convert)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff6b6b;")
        self.error_label.setWordWrap(True)
        left_layout.addWidget(QLabel("Input Type:"))
        left_layout.addWidget(self.type_combo)
        left_layout.addWidget(self.input_edit)
        left_layout.addWidget(self.convert_btn)
        left_layout.addWidget(self.error_label)
        left_widget.setMaximumWidth(350)
        main_splitter.addWidget(left_widget)

        # Center Panel
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        self.dfa_canvas = DFACanvas()
        sim_layout = QHBoxLayout()
        self.simulate_input = QLineEdit()
        self.simulate_input.setPlaceholderText("Enter string to simulate...")
        self.simulate_btn = QPushButton("Simulate")
        self.simulate_btn.clicked.connect(self.on_simulate)
        sim_layout.addWidget(self.simulate_input)
        sim_layout.addWidget(self.simulate_btn)
        center_layout.addWidget(self.dfa_canvas, stretch=1)
        center_layout.addLayout(sim_layout)
        main_splitter.addWidget(center_widget)

        # Right Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.tabs = QTabWidget()
        self.regex_output = QTextEdit();
        self.regex_output.setReadOnly(True)
        self.cfg_output = QTextEdit();
        self.cfg_output.setReadOnly(True)
        self.english_output = QTextEdit();
        self.english_output.setReadOnly(True)
        self.tabs.addTab(self.regex_output, "Regex")
        self.tabs.addTab(self.cfg_output, "CFG")
        self.tabs.addTab(self.create_strings_tab(), "Strings")
        self.tabs.addTab(self.english_output, "English")
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(right_widget)

        main_splitter.setSizes([300, 500, 400])

    def create_strings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Max Length:"))
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(1, 20)
        self.length_spinbox.setValue(6)
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.on_generate_strings)
        controls.addWidget(self.length_spinbox)
        controls.addWidget(self.generate_btn)
        self.strings_list = QListWidget()
        layout.addLayout(controls)
        layout.addWidget(self.strings_list)
        return tab

    def on_type_changed(self):
        name = self.type_combo.currentText()
        self.input_edit.setPlaceholderText(self.PLACEHOLDERS.get(name, ''))

    def on_convert(self):
        type_map = {
            'regular expression': 'regex', 'dfa': 'dfa', 'nfa': 'nfa',
            'cfg (regular)': 'cfg', 'string generator': 'strings'
        }
        key = type_map.get(self.type_combo.currentText().lower(), 'regex')
        input_text = self.input_edit.toPlainText().strip()
        if not input_text:
            self.error_label.setText('Input is required.')
            return
        self.error_label.setText('')
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText('Converting...')
        self.worker = ConvertWorker(key, input_text)
        self.worker.finished.connect(self.on_convert_done)
        self.worker.start()

    def on_convert_done(self, result):
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText('Convert')
        if result['error']:
            self.error_label.setText(f"Error: {result['error']}")
            self.dfa_canvas.clear()
            self._current_dfa = None
            return

        self._current_dfa = result['dfa']
        if self._current_dfa:
            self.dfa_canvas.load_dfa(self._current_dfa)

        self.regex_output.setPlainText(result['regex'])
        self.cfg_output.setPlainText(self.format_cfg(result['cfg']))
        self.english_output.setPlainText(result['english'])
        self.update_strings_list(result['strings'])

    def on_simulate(self):
        if not self._current_dfa:
            QMessageBox.warning(self, "Warning", "No DFA is loaded to simulate.")
            return
        self.dfa_canvas.start_simulation(self.simulate_input.text())

    def on_generate_strings(self):
        if not self._current_dfa:
            QMessageBox.warning(self, "Warning", "No DFA is loaded to generate strings from.")
            return
        max_len = self.length_spinbox.value()
        strings = enumerate_strings(self._current_dfa, max_len)
        self.update_strings_list(strings)

    def update_strings_list(self, strings):
        self.strings_list.clear()
        if not strings and self._current_dfa and self._current_dfa.start_state in self._current_dfa.accept_states:
            self.strings_list.addItem('ε (empty string)')
        for s in strings:
            display = f'"{s}"' if s else 'ε (empty string)'
            self.strings_list.addItem(display)

    def format_cfg(self, cfg: dict) -> str:
        if not cfg or not cfg.get('productions'): return ''
        lines = []
        start_var = cfg.get('start')
        # Print start variable first
        if start_var in cfg['productions']:
            prods = cfg['productions'][start_var]
            rhs = ' | '.join(p if p else 'ε' for p in prods)
            lines.append(f'{start_var} → {rhs}')
        # Print other variables
        for var, prods in sorted(cfg['productions'].items()):
            if var == start_var: continue
            rhs = ' | '.join(p if p else 'ε' for p in prods)
            lines.append(f'{var} → {rhs}')
        return '\n'.join(lines)