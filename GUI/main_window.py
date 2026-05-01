import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QLabel, QLineEdit,
    QTabWidget, QListWidget, QSpinBox, QSplitter, QAction, QMessageBox,
    QFormLayout, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
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
        'String Generator': 'ab\nba\nabb\nbba'
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Like Math But Not Math")
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
        about_action.triggered.connect(lambda: QMessageBox.about(self, "About", "Like Math But Not Math v1.0"))
        help_menu.addAction(about_action)

    def setup_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.type_combo = QComboBox()
        # Add NFA to the list, we will use DFA builder for it too (or just keep it simple)
        self.type_combo.addItems(['Regular Expression', 'DFA', 'NFA', 'CFG (Regular)', 'String Generator'])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        self.input_stack = QWidget()
        self.input_stack_layout = QVBoxLayout(self.input_stack)
        self.input_stack_layout.setContentsMargins(0, 0, 0, 0)
        
        # Simple text input for Regex and Strings
        self.text_input_widget = QWidget()
        text_layout = QVBoxLayout(self.text_input_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        self.input_edit = QTextEdit()
        text_layout.addWidget(self.input_edit)
        
        # Structured input for DFA/NFA
        self.fa_input_widget = QWidget()
        fa_layout = QVBoxLayout(self.fa_input_widget)
        fa_layout.setContentsMargins(0, 0, 0, 0)
        
        fa_form = QFormLayout()
        self.fa_states_input = QLineEdit()
        self.fa_states_input.setPlaceholderText("q0, q1, q2")
        self.fa_alphabet_input = QLineEdit()
        self.fa_alphabet_input.setPlaceholderText("a, b")
        self.fa_start_input = QLineEdit()
        self.fa_start_input.setPlaceholderText("q0")
        self.fa_accept_input = QLineEdit()
        self.fa_accept_input.setPlaceholderText("q2")
        
        fa_form.addRow("States:", self.fa_states_input)
        fa_form.addRow("Alphabet:", self.fa_alphabet_input)
        fa_form.addRow("Start:", self.fa_start_input)
        fa_form.addRow("Accept:", self.fa_accept_input)
        
        self.fa_transitions_table = QTableWidget(0, 3)
        self.fa_transitions_table.setHorizontalHeaderLabels(["State", "Symbol", "Next State"])
        self.fa_transitions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        btn_layout = QHBoxLayout()
        self.add_trans_btn = QPushButton("Add Transition")
        self.add_trans_btn.clicked.connect(self.add_fa_transition)
        self.del_trans_btn = QPushButton("Remove Transition")
        self.del_trans_btn.clicked.connect(self.remove_fa_transition)
        btn_layout.addWidget(self.add_trans_btn)
        btn_layout.addWidget(self.del_trans_btn)
        
        fa_layout.addLayout(fa_form)
        fa_layout.addWidget(QLabel("Transitions:"))
        fa_layout.addWidget(self.fa_transitions_table)
        fa_layout.addLayout(btn_layout)
        
        # Structured input for CFG
        self.cfg_input_widget = QWidget()
        cfg_layout = QVBoxLayout(self.cfg_input_widget)
        cfg_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cfg_productions_table = QTableWidget(0, 2)
        self.cfg_productions_table.setHorizontalHeaderLabels(["Variable", "Production (e.g. aS | b)"])
        self.cfg_productions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        cfg_btn_layout = QHBoxLayout()
        self.add_prod_btn = QPushButton("Add Production")
        self.add_prod_btn.clicked.connect(self.add_cfg_production)
        self.del_prod_btn = QPushButton("Remove Production")
        self.del_prod_btn.clicked.connect(self.remove_cfg_production)
        cfg_btn_layout.addWidget(self.add_prod_btn)
        cfg_btn_layout.addWidget(self.del_prod_btn)
        
        cfg_layout.addWidget(QLabel("Productions:"))
        cfg_layout.addWidget(self.cfg_productions_table)
        cfg_layout.addLayout(cfg_btn_layout)
        
        self.input_stack_layout.addWidget(self.text_input_widget)
        self.input_stack_layout.addWidget(self.fa_input_widget)
        self.input_stack_layout.addWidget(self.cfg_input_widget)

        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.on_convert)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff6b6b;")
        self.error_label.setWordWrap(True)
        
        left_layout.addWidget(QLabel("Input Type:"))
        left_layout.addWidget(self.type_combo)
        left_layout.addWidget(self.input_stack)
        left_layout.addWidget(self.convert_btn)
        left_layout.addWidget(self.error_label)
        left_widget.setMaximumWidth(400)
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
        self.regex_output = QTextEdit()
        self.regex_output.setReadOnly(True)
        self.cfg_output = QTextEdit()
        self.cfg_output.setReadOnly(True)
        self.english_output = QTextEdit()
        self.english_output.setReadOnly(True)
        self.tabs.addTab(self.regex_output, "Regex")
        self.tabs.addTab(self.cfg_output, "CFG")
        self.tabs.addTab(self.create_strings_tab(), "Strings")
        self.tabs.addTab(self.english_output, "English")
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(right_widget)

        main_splitter.setSizes([350, 450, 400])

    def add_fa_transition(self, state="", symbol="", next_state=""):
        row = self.fa_transitions_table.rowCount()
        self.fa_transitions_table.insertRow(row)
        if state or symbol or next_state:
            self.fa_transitions_table.setItem(row, 0, QTableWidgetItem(state))
            self.fa_transitions_table.setItem(row, 1, QTableWidgetItem(symbol))
            self.fa_transitions_table.setItem(row, 2, QTableWidgetItem(next_state))

    def remove_fa_transition(self):
        row = self.fa_transitions_table.currentRow()
        if row >= 0:
            self.fa_transitions_table.removeRow(row)
        elif self.fa_transitions_table.rowCount() > 0:
            self.fa_transitions_table.removeRow(self.fa_transitions_table.rowCount() - 1)

    def add_cfg_production(self, var="", prod=""):
        row = self.cfg_productions_table.rowCount()
        self.cfg_productions_table.insertRow(row)
        if var or prod:
            self.cfg_productions_table.setItem(row, 0, QTableWidgetItem(var))
            self.cfg_productions_table.setItem(row, 1, QTableWidgetItem(prod))

    def remove_cfg_production(self):
        row = self.cfg_productions_table.currentRow()
        if row >= 0:
            self.cfg_productions_table.removeRow(row)
        elif self.cfg_productions_table.rowCount() > 0:
            self.cfg_productions_table.removeRow(self.cfg_productions_table.rowCount() - 1)

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

    def clear_fa_table(self):
        while self.fa_transitions_table.rowCount() > 0:
            self.fa_transitions_table.removeRow(0)
            
    def clear_cfg_table(self):
        while self.cfg_productions_table.rowCount() > 0:
            self.cfg_productions_table.removeRow(0)

    def on_type_changed(self):
        name = self.type_combo.currentText()
        if name in ['Regular Expression', 'String Generator']:
            self.text_input_widget.setVisible(True)
            self.fa_input_widget.setVisible(False)
            self.cfg_input_widget.setVisible(False)
            self.input_edit.setPlainText(self.PLACEHOLDERS.get(name, ''))
            
        elif name == 'DFA':
            self.text_input_widget.setVisible(False)
            self.fa_input_widget.setVisible(True)
            self.cfg_input_widget.setVisible(False)
            
            self.fa_states_input.setText("q0, q1, q2")
            self.fa_alphabet_input.setText("a, b")
            self.fa_start_input.setText("q0")
            self.fa_accept_input.setText("q2")
            
            self.clear_fa_table()
            self.add_fa_transition("q0", "a", "q1")
            self.add_fa_transition("q1", "b", "q2")
            
        elif name == 'NFA':
            self.text_input_widget.setVisible(False)
            self.fa_input_widget.setVisible(True)
            self.cfg_input_widget.setVisible(False)
            
            self.fa_states_input.setText("q0, q1")
            self.fa_alphabet_input.setText("a, b")
            self.fa_start_input.setText("q0")
            self.fa_accept_input.setText("q1")
            
            self.clear_fa_table()
            self.add_fa_transition("q0", "a", "q0,q1")
            self.add_fa_transition("q0", "b", "q0")

        elif name == 'CFG (Regular)':
            self.text_input_widget.setVisible(False)
            self.fa_input_widget.setVisible(False)
            self.cfg_input_widget.setVisible(True)
            
            self.clear_cfg_table()
            self.add_cfg_production("S", "aS | bA | ε")
            self.add_cfg_production("A", "bA | b")

    def get_fa_text(self):
        lines = []
        lines.append(f"states: {self.fa_states_input.text()}")
        lines.append(f"alphabet: {self.fa_alphabet_input.text()}")
        lines.append(f"start: {self.fa_start_input.text()}")
        lines.append(f"accept: {self.fa_accept_input.text()}")
        lines.append("transitions:")
        for row in range(self.fa_transitions_table.rowCount()):
            state_item = self.fa_transitions_table.item(row, 0)
            symbol_item = self.fa_transitions_table.item(row, 1)
            next_state_item = self.fa_transitions_table.item(row, 2)
            
            state = state_item.text() if state_item else ""
            symbol = symbol_item.text() if symbol_item else ""
            next_state = next_state_item.text() if next_state_item else ""
            
            if state and symbol and next_state:
                lines.append(f"  {state},{symbol} -> {next_state}")
        return "\n".join(lines)

    def get_cfg_text(self):
        lines = []
        for row in range(self.cfg_productions_table.rowCount()):
            var_item = self.cfg_productions_table.item(row, 0)
            prod_item = self.cfg_productions_table.item(row, 1)
            
            var = var_item.text() if var_item else ""
            prod = prod_item.text() if prod_item else ""
            
            if var and prod:
                lines.append(f"{var} -> {prod}")
        return "\n".join(lines)

    def on_convert(self):
        type_map = {
            'regular expression': 'regex', 'dfa': 'dfa', 'nfa': 'nfa',
            'cfg (regular)': 'cfg', 'string generator': 'strings'
        }
        current_type = self.type_combo.currentText()
        key = type_map.get(current_type.lower(), 'regex')
        
        input_text = ""
        if current_type in ['Regular Expression', 'String Generator']:
            input_text = self.input_edit.toPlainText().strip()
        elif current_type in ['DFA', 'NFA']:
            input_text = self.get_fa_text()
        elif current_type == 'CFG (Regular)':
            input_text = self.get_cfg_text()
            
        if not input_text.strip():
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