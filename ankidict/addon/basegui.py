# -*- coding: utf-8 -*-

# PyQt library
from aqt.qt import *
import aqt.qt as QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit
from addon import macm_parser_css
from addon import collection
from libdict import macmillan
import re
import datetime
from addon.collection import get_plugin


def tostr(a):
    if a is None:
        return ""
    else:
        return a


class DictWindow(QWidget):
    def __init__(self):
        super(DictWindow, self).__init__()
        def conf_btn(btn):
            btn.setMaximumWidth(60)
            btn.setStyleSheet("font-weight: bold; font-family: monospace")
        self.search_input = QLineEdit("")
        self.search_button = QPushButton("SEARCH")
        self.prev_button = QPushButton("<-")
        self.next_button = QPushButton("->")
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.prev_button.setMaximumWidth(66)
        self.next_button.setMaximumWidth(66)
        self.wordlist_button = QPushButton("WORDLIST")
        self.settings_button = QPushButton("SETTINGS")
        conf_btn(self.prev_button)
        conf_btn(self.next_button)
        #conf_btn(self.search_button)
        #conf_btn(self.wordlist_button)
        #conf_btn(self.settings_button)

    def init_finalize(self):
        self.head_hbox = QHBoxLayout()
        self.head_hbox.addWidget(self.prev_button)
        self.head_hbox.addWidget(self.next_button)
        self.head_hbox.addWidget(self.search_input)
        self.head_hbox.addWidget(self.search_button)
        self.head_hbox.addWidget(self.wordlist_button)
        self.head_hbox.addWidget(self.settings_button)
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addLayout(self.head_hbox)
        self.main_vbox.addWidget(self.current_view)
        self.setLayout(self.main_vbox)
        self.resize(800,600)
        self.setWindowTitle('Macmillan Dictionary')

    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            # Selecting the search input field
            self.search_input.setFocus()
            self.search_input.setText("")


class DictEntryView(QWidget):
    def __init__(self):
        super(DictEntryView, self).__init__()

        self.left_scroll = QScrollArea()
        self.right_scroll = QScrollArea()
        self.left_widget = QWidget()
        self.right_widget = QWidget()
        self.left_vbox = QVBoxLayout()
        self.right_vbox = QVBoxLayout()
        self.main_hbox = QHBoxLayout()

    def add_sense_widget(self, w):
        self.left_vbox.addWidget(w)

    def add_link(self, link, callback):
        title = tostr(link.key)
        href = link.url
        btn = QLabel('<a href="related" style="text-decoration: none; color: black;"><strong>' + title + "</strong></a>")
        btn.linkActivated.connect(callback)
        btn.show()
        btn.setWordWrap(True)
        def make_line():
            fr = QFrame()
            #fr.setStyleSheet("background-color: white;");
            fr.setFrameShape(QFrame.HLine)
            fr.setFrameShadow(QFrame.Sunken)
            fr.setLineWidth(2)
            #fr.setMidLineWidth(1)
            return fr
        self.right_vbox.addWidget(btn)
        self.right_vbox.addWidget(make_line())

    def init_finalize(self):
        self.left_scroll.setWidgetResizable(True)
        self.right_scroll.setWidgetResizable(True)
        self.left_widget.setLayout(self.left_vbox)
        self.right_widget.setLayout(self.right_vbox)
        self.left_widget.show()
        self.right_widget.show()
        self.left_scroll.setWidget(self.left_widget)
        self.right_scroll.setWidget(self.right_widget)
        self.right_scroll.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # TODO: potem i tak to będą jakieś labelsy, więc się będą zawijać i będzie dobrze
        self.right_scroll.setMaximumWidth(get_plugin().config.related_defs_panel_width)
        self.left_column = QVBoxLayout()
        self.left_column.addWidget(self.left_scroll)
        self.left_column.addWidget(self.examples_widget)
        self.main_hbox.addLayout(self.left_column)
        self.main_hbox.addWidget(self.right_scroll)
        self.setLayout(self.main_hbox)


class SenseWidget(QWidget):
    def format_definition_html(self):
        wyn = ""
        if self.sense.style_level != "" and self.sense.style_level != None:
            wyn += "<i>"+self.sense.style_level+"</i>"
        return wyn + self.sense.definition

    def extract_keys(self):
        if self.sense.original_key is None:
            keys = []
        else:
            keys = [s.strip() for s in self.sense.original_key.split("|")]
        return keys

    def format_key_html(self):
        keys = self.extract_keys()
        return "<strong>"+(" </strong ><i> or </i><strong> ".join(keys))+"</strong>"

    def format_erased_definition_html(self):
        wyn = ""
        if self.sense.style_level != "" and self.sense.style_level != None:
            wyn += "<i>"+self.sense.style_level+"</i>"
        tmp_def = self.sense.definition
        keys = self.extract_keys()
        for i in keys:
            tmp_def = " ____ ".join(tmp_def.split(i))
        return wyn + tmp_def

    def __init__(self):
        super(SenseWidget, self).__init__()
        self.main_vbox = QVBoxLayout()
        self.def_hbox = QHBoxLayout()
        
        self.main_vbox.setMargin(0)
        self.def_hbox.setMargin(0)
        self.main_vbox.setSpacing(0)
        self.def_hbox.setSpacing(0)
        
        tmplabel = QLabel(self.format_key_html() + "  ---  " + self.format_definition_html())
        tmplabel.setWordWrap(True)
        tmplabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        #tmplabel.setScaledContents(True)
        tmplabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.main_vbox.addWidget(tmplabel)
        self.add_btn = QPushButton("ADD")
        self.add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.examples_to_hide = []
        #self.main_vbox.addLayout(self.def_hbox)

    def add_example(self, example, callback):
        key = example.original_key
        ex = example.content
        tmp = '<a href="example" style="'+get_plugin().config.example_style+'"><i>'
        if key:
            tmp += "<b> "+key+" </b>"
        tmp += ex
        tmp += "</i></a>"
        tmplabel = QLabel(tmp)
        tmplabel.setWordWrap(True)
        tmplabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        tmplabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        tmplabel.linkActivated.connect(callback)
        self.examples_to_hide.append(tmplabel)

    def init_finalize(self):
        self.examples_all = self.examples_to_hide
        self.examples_to_hide = self.examples_to_hide[(get_plugin().config.max_examples_per_sense):]
        def make_frame():
            fr = QFrame()
            fr.setStyleSheet("background-color: white;");
            fr.setFrameShape(QFrame.Box)
            fr.setFrameShadow(QFrame.Raised)
            fr.setLineWidth(2)
            fr.setMidLineWidth(2)
            return fr
        def make_hidden_examples():
            w = QWidget()
            w.onLeaveEvent = lambda e: None
            if self.examples_all == []:
                return w
            w.setMouseTracking(True)
            lab = QLabel('<a href="example" style="'+get_plugin().config.example_style+'"><b> ... ... ... </b></a>')
            lab.hide()
            layout = QVBoxLayout()
            for i in self.examples_all:
                layout.addWidget(i)
            layout.setMargin(2)
            layout.addWidget(lab)
            w.setLayout(layout)
            def onEnterEvent(event):
                # here showing examples (takie onHover)
                for i in self.examples_to_hide:
                    i.show()
                lab.hide()
            def onLeaveEvent(event):
                # here hiding examples (takie onUnHover)
                for i in self.examples_to_hide:
                    i.hide()
                if self.examples_to_hide != []:
                    lab.show()
            def mouseMoveEvent(event):
                if event.x() < get_plugin().config.examples_hover_area_width :
                    onEnterEvent(event)
                else:
                    onLeaveEvent(event)
            #w.enterEvent = onEnterEvent
            #w.leaveEvent = onLeaveEvent
            w.mouseMoveEvent = mouseMoveEvent
            w.onLeaveEvent = onLeaveEvent
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            onLeaveEvent(None)
            w.show()
            return w
        self.hidden_examples = make_hidden_examples()
        self.main_vbox.addWidget(self.hidden_examples)
        frame = make_frame()
        frame.setLayout(self.main_vbox)
        self.def_hbox.addWidget(frame)
        self.def_hbox.addWidget(self.add_btn)
        
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        self.setLayout(self.def_hbox)
        