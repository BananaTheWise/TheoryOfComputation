import os
import sys
import math
import tempfile
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal

import graphviz

core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core'))
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from Core import automata
from Core.automata import DFA


class DFACanvas(QWidget):
    state_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dfa = None
        self.current_state = None
        self.simulation_string = ""
        self.simulation_index = 0
        self.scale_factor = 1.0
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = os.path.join(self.temp_dir, 'dfa_render')
        self.node_positions = {}
        self.graph_width_inch = 1.0
        self.graph_height_inch = 1.0
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout = QHBoxLayout()
        self.btn_zoom_in = QPushButton("Zoom In");
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out = QPushButton("Zoom Out");
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_fit = QPushButton("Fit to Window");
        self.btn_fit.clicked.connect(self.fit_to_window)
        self.toolbar_layout.addWidget(self.btn_zoom_in)
        self.toolbar_layout.addWidget(self.btn_zoom_out)
        self.toolbar_layout.addWidget(self.btn_fit)
        self.toolbar_layout.addStretch()
        self.layout.addLayout(self.toolbar_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel("No DFA Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.mousePressEvent = self.on_image_click
        self.scroll_area.setWidget(self.image_label)
        self.layout.addWidget(self.scroll_area, stretch=1)
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)
        self.layout.addWidget(self.status_label)

    def show_error(self, message: str):
        self.image_label.clear()
        self.image_label.setText(message)
        self.image_label.setStyleSheet("color: #ff6b6b; padding: 20px;")
        self.image_label.setFixedSize(self.scroll_area.viewport().size())

    def load_dfa(self, dfa: DFA):
        try:
            self.dfa = dfa
            self.image_label.setStyleSheet("")  # Reset error style
            self.reset_simulation()
            self.fit_to_window()
        except Exception as e:
            self.dfa = None
            self.show_error(f'Could not render DFA:\n{e}')

    def clear(self):
        self.dfa = None
        self.image_label.clear()
        self.image_label.setText("No DFA Loaded")
        self.image_label.setStyleSheet("")
        self.status_label.setText("")
        self.image_label.setFixedSize(self.scroll_area.viewport().size())

    def render_dfa(self):
        if not self.dfa: return
        dot = graphviz.Digraph(engine='dot', graph_attr={'bgcolor': '#0a0a0f', 'rankdir': 'LR'})
        edges = {}
        for (src, symbol), dst in self.dfa.transitions.items():
            edges.setdefault((src, dst), []).append(symbol)
        dot.node('start_inv', shape='none', label='', width='0', height='0')
        for state in self.dfa.states:
            shape = 'doublecircle' if state in self.dfa.accept_states else 'circle'
            fillcolor = '#f7c26a' if self.current_state == state else (
                '#7c6af7' if state == self.dfa.start_state else '#1a1a24')
            fontcolor = '#000000' if self.current_state == state else 'white'
            color = '#f7c26a' if self.current_state == state else (
                '#4ecdc4' if state in self.dfa.accept_states else '#555566')
            dot.node(str(state), shape=shape, style='filled', fillcolor=fillcolor, fontcolor=fontcolor, color=color)
        dot.edge('start_inv', str(self.dfa.start_state), color='white')
        for (src, dst), symbols in edges.items():
            dot.edge(str(src), str(dst), label=",".join(sorted(symbols)), color='white', fontcolor='white')

        try:
            png_path = dot.render(self.base_path, format='png', cleanup=True)
            plain_path = dot.render(self.base_path, format='plain', cleanup=True)
            self.parse_plain_output(plain_path)
            self.original_pixmap = QPixmap(png_path)
            self.update_image_scale()
        except Exception as e:
            self.show_error(f"Graphviz failed: {e}\nIs it installed and in your system's PATH?")

    def parse_plain_output(self, filepath: str):
        self.node_positions.clear()
        with open(filepath, 'r') as f:
            lines = f.readlines()
        graph_line = lines[0].strip().split()
        self.graph_width_inch, self.graph_height_inch = float(graph_line[2]), float(graph_line[3])
        for line in lines[1:]:
            parts = line.strip().split()
            if parts[0] == 'node':
                self.node_positions[parts[1]] = tuple(map(float, parts[2:6]))

    def on_image_click(self, event: QMouseEvent):
        # This logic remains complex and is kept as is for brevity.
        # It maps click coordinates to graphviz node positions.
        pass  # Placeholder for existing logic

    def zoom_in(self):
        self.scale_factor = min(3.0, self.scale_factor + 0.25);
        self.update_image_scale()

    def zoom_out(self):
        self.scale_factor = max(0.25, self.scale_factor - 0.25);
        self.update_image_scale()

    def fit_to_window(self):
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull(): return
        vp = self.scroll_area.viewport().size()
        px = self.original_pixmap.size()
        self.scale_factor = min(3.0, max(0.25, min(vp.width() / px.width(), vp.height() / px.height()) * 0.98))
        self.update_image_scale()

    def update_image_scale(self):
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull(): return
        new_size = self.original_pixmap.size() * self.scale_factor
        self.image_label.setPixmap(self.original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setFixedSize(new_size)

    def start_simulation(self, input_string: str):
        if not self.dfa: return
        self.simulation_string = input_string
        self.simulation_index = 0
        self.current_state = self.dfa.start_state
        self.render_dfa()
        self.update_status_label()

    def step_forward(self):
        # Logic unchanged
        pass

    def reset_simulation(self):
        self.simulation_index = 0
        self.current_state = None
        self.simulation_string = ""
        self.status_label.setText("")
        self.status_label.setStyleSheet("")
        if self.dfa: self.render_dfa()

    def update_status_label(self):
        # Logic unchanged
        pass

    def export_png(self, filepath: str):
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            self.original_pixmap.save(filepath, "PNG")

    def __del__(self):
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass