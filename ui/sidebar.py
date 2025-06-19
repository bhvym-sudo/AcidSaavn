from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"

class SideBar(QFrame):
    def __init__(self):
        super().__init__()
        self.is_expanded = False
        self.setFixedWidth(60)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {RICH_BLACK};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 20, 5, 20)
        self.main_layout.setSpacing(15)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.home_container = QHBoxLayout()
        self.home_container.setSpacing(10)
        self.home_container.setAlignment(Qt.AlignLeft)
        
        self.home_btn = QPushButton("⌂")
        self.home_btn.setFixedSize(50, 50)
        self.home_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CHARCOAL};
                border: none;
                border-radius: 25px;
                color: white;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {PAYNES_GRAY};
            }}
            QPushButton:pressed {{
                background-color: {CERULEAN};
            }}
        """)
        self.home_btn.setCheckable(True)
        self.home_container.addWidget(self.home_btn)
        
        self.home_text = QLabel("Home")
        self.home_text.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.home_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.home_text.hide()  # Initially hidden
        self.home_container.addWidget(self.home_text)
        self.home_container.addStretch()

        self.search_container = QHBoxLayout()
        self.search_container.setSpacing(10)
        self.search_container.setAlignment(Qt.AlignLeft)
        
        self.search_btn = QPushButton("⚲")
        self.search_btn.setFixedSize(50, 50)
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CHARCOAL};
                border: none;
                border-radius: 25px;
                color: white;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {PAYNES_GRAY};
            }}
            QPushButton:pressed {{
                background-color: {CERULEAN};
            }}
        """)
        self.search_btn.setCheckable(True)
        self.search_container.addWidget(self.search_btn)
        
        self.search_text = QLabel("Search")
        self.search_text.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.search_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.search_text.hide()  # Initially hidden
        self.search_container.addWidget(self.search_text)
        self.search_container.addStretch()


        self.main_layout.addLayout(self.home_container)
        self.main_layout.addLayout(self.search_container)
        self.main_layout.addStretch()


        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(300)
        self.width_animation.setEasingCurve(QEasingCurve.InOutQuad)



    def toggle_expand(self):
        """Toggle the sidebar expand/collapse state"""
        self.is_expanded = not self.is_expanded
        
        # Animate width
        self.animation.setStartValue(self.width())
        target_width = 200 if self.is_expanded else 60
        self.animation.setEndValue(target_width)
        
        self.width_animation.setStartValue(self.width())
        self.width_animation.setEndValue(target_width)
        
        # Update fixed width
        if self.is_expanded:
            self.setFixedWidth(200)
            # Show text labels
            self.home_text.show()
            self.search_text.show()
        else:
            self.setFixedWidth(60)
            # Hide text labels
            self.home_text.hide()
            self.search_text.hide()
        
        # Start animations
        self.animation.start()
        self.width_animation.start()