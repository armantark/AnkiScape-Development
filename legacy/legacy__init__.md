# __init__.py

from .constants import *
from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
import json
import random
import os
import datetime
import random

global card_turned, exp_awarded, answer_shown

answer_shown = False
card_turned = False
exp_awarded = False

current_skill = "None"

def show_review_popup():
    if mw.col.get_config("ankiscape_hide_review_popup", False):
        return

    dialog = QDialog(mw)
    dialog.setWindowTitle("AnkiScape - Enjoying the add-on?")
    layout = QVBoxLayout()

    message = QLabel(
        "If you're enjoying AnkiScape, please consider leaving a review. Your feedback helps others discover the add-on!")
    layout.addWidget(message)

    review_button = QPushButton("Leave a Review")
    review_button.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://ankiweb.net/shared/review/1808450369")))
    layout.addWidget(review_button)

    hide_checkbox = QCheckBox("Don't show this message again")
    layout.addWidget(hide_checkbox)

    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.accept)
    layout.addWidget(close_button)

    dialog.setLayout(layout)

    if dialog.exec():
        if hide_checkbox.isChecked():
            mw.col.set_config("ankiscape_hide_review_popup", True)
            mw.col.save()


# Classes
class ExpPopup(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: rgba(70, 130, 180, 200);
            color: white;
            border-radius: 10px;
            padding: 5px;
            font-weight: bold;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

    def show_exp(self, exp):
        self.setText(f"+{exp} XP")
        self.adjustSize()
        self.show()
        self.move(self.parent().width() - self.width() - 20, self.parent().height() - 100)

        # Fade-out animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(2000)  # 2 seconds
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.finished.connect(self.hide)

        # Float-up animation
        self.float_animation = QPropertyAnimation(self, b"pos")
        self.float_animation.setDuration(2000)  # 2 seconds
        start_pos = self.pos()
        end_pos = start_pos - QPoint(0, 50)  # Move 50 pixels up
        self.float_animation.setStartValue(start_pos)
        self.float_animation.setEndValue(end_pos)
        self.float_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start animations
        self.fade_animation.start()
        self.float_animation.start()


# Helper functions
def save_player_data():
    mw.col.set_config("ankiscape_player_data", player_data)
    mw.col.set_config("ankiscape_current_skill", current_skill)

def load_player_data():
    global player_data, current_skill

    # Define default_values at the beginning of the function
    default_values = {
        "mining_level": 1,
        "woodcutting_level": 1,
        "smithing_level": 1,
        "crafting_level": 1,
        "mining_exp": 0,
        "woodcutting_exp": 0,
        "smithing_exp": 0,
        "crafting_exp": 0,
        "current_craft": "None",
        "current_ore": "Rune essence",
        "current_tree": "Tree",
        "current_bar": "Bronze bar",
        "inventory": {ore: 0 for ore in ORE_DATA},
        "progress_to_next": 0,
        "completed_achievements": [],
    }

    loaded_data = mw.col.get_config("ankiscape_player_data")
    if loaded_data:
        if "smithing_level" not in loaded_data:
            loaded_data["smithing_level"] = 1
            loaded_data["smithing_exp"] = 0
            loaded_data["current_bar"] = "Bronze bar"

        # Check if the loaded data is using the old format
        if "total_exp" in loaded_data:
            # Migrate the old format to the new format
            loaded_data["mining_exp"] = loaded_data.pop("total_exp")
            loaded_data["woodcutting_exp"] = 0

        # Ensure all new fields are present with default values
        for key, value in default_values.items():
            if key not in loaded_data:
                loaded_data[key] = value

        player_data = loaded_data
    else:
        # If no data is loaded, initialize with default values
        player_data = default_values

    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    update_menu_visibility()

def get_exp_to_next_level():
    current_level = player_data["mining_level"]
    if current_level >= 99:
        return 0
    return EXP_TABLE[current_level] - player_data["total_exp"]


def level_up_check(skill):
    if skill == "Mining":
        while player_data["mining_level"] < 99 and player_data["mining_exp"] >= EXP_TABLE[player_data["mining_level"]]:
            player_data["mining_level"] += 1
            show_level_up_dialog("Mining")
    elif skill == "Woodcutting":
        while player_data["woodcutting_level"] < 99 and player_data["woodcutting_exp"] >= EXP_TABLE[player_data["woodcutting_level"]]:
            player_data["woodcutting_level"] += 1
            show_level_up_dialog("Woodcutting")
    elif skill == "Smithing":
        while player_data["smithing_level"] < 99 and player_data["smithing_exp"] >= EXP_TABLE[player_data["smithing_level"]]:
            player_data["smithing_level"] += 1
            show_level_up_dialog("Smithing")
    elif skill == "Crafting":
        while player_data["crafting_level"] < 99 and player_data["crafting_exp"] >= EXP_TABLE[player_data["crafting_level"]]:
            player_data["crafting_level"] += 1
            show_level_up_dialog("Crafting")

def check_achievements():
    for achievement, data in ACHIEVEMENTS.items():
        if achievement not in player_data["completed_achievements"] and data["condition"](player_data):
            player_data["completed_achievements"].append(achievement)
            show_achievement_dialog(achievement, data)

# UI functions

def initialize_skill():
    global current_skill
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    update_menu_visibility()


def show_skill_selection():
    global current_skill
    dialog = QDialog(mw)
    dialog.setWindowTitle("Skill Selection")
    layout = QVBoxLayout()

    # Dropdown menu
    skill_combo = QComboBox()
    skill_combo.addItems(["None", "Mining", "Woodcutting", "Smithing", "Crafting"])
    skill_combo.setCurrentText(current_skill)
    layout.addWidget(skill_combo)

    # Add a warning label
    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red;")
    layout.addWidget(warning_label)

    def update_warning():
        if skill_combo.currentText() == "Smithing" and not can_smelt_any_bar():
            warning_label.setText("You don't have enough ores to smelt any bars. Mine some ores first!")
            save_button.setEnabled(False)
        else:
            warning_label.setText("")
            save_button.setEnabled(True)

    skill_combo.currentTextChanged.connect(update_warning)

    # Buttons
    button_layout = QHBoxLayout()
    cancel_button = QPushButton("Cancel")
    save_button = QPushButton("Save")

    cancel_button.clicked.connect(dialog.reject)
    save_button.clicked.connect(lambda: save_skill(skill_combo.currentText(), dialog))

    button_layout.addWidget(cancel_button)
    button_layout.addWidget(save_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    update_warning()
    dialog.exec()

def save_skill(skill, dialog):
    global current_skill
    if skill == "Smithing" and not can_smelt_any_bar():
        QMessageBox.warning(dialog, "No Ores Available",
                            "You don't have enough ores to smelt any bars. Mine some ores first!")
    else:
        current_skill = skill
        update_menu_visibility()
        dialog.accept()

def update_menu_visibility():
    global current_skill
    ore_selection_action.setVisible(current_skill == "Mining")
    tree_selection_action.setVisible(current_skill == "Woodcutting")
    bar_selection_action.setVisible(current_skill == "Smithing")
    craft_selection_action.setVisible(current_skill == "Crafting")
    stats_action.setVisible(current_skill in ["Mining", "Woodcutting", "Smithing", "Crafting"])
    achievements_action.setVisible(current_skill in ["Mining", "Woodcutting", "Smithing", "Crafting"])

def show_achievement_dialog(achievement, data):
    dialog = QDialog(mw)
    dialog.setWindowTitle("Achievement Unlocked!")
    dialog.setFixedSize(400, 200)
    layout = QVBoxLayout()

    # Achievement icon (you may want to add custom icons for each achievement)
    icon_label = QLabel()
    icon_path = os.path.join(current_dir, "icon", "achievement_icon.png")
    pixmap = QPixmap(icon_path)
    icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
    layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Achievement name and description
    name_label = QLabel(achievement)
    name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
    layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)

    desc_label = QLabel(data["description"])
    desc_label.setStyleSheet("font-size: 14px;")
    layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Difficulty
    diff_label = QLabel(f"Difficulty: {data['difficulty']}")
    diff_label.setStyleSheet("font-style: italic;")
    layout.addWidget(diff_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # OK button
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

    dialog.setLayout(layout)
    dialog.exec()

def show_level_up_dialog(skill):
    level = player_data[f"{skill.lower()}_level"]
    dialog = QDialog(mw)
    dialog.setWindowTitle("Level Up!")
    dialog.setFixedSize(375, 200)
    layout = QVBoxLayout()

    # Update the text to use the skill parameter
    icon_text_layout = QHBoxLayout()
    icon_label = QLabel()
    icon_path = os.path.join(current_dir, "icon", f"{skill}_icon.png")
    pixmap = QPixmap(icon_path)
    icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
    icon_text_layout.addWidget(icon_label)

    text_label = QLabel(f"Congratulations!\nYou've advanced a {skill.capitalize()} level!")
    text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    text_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    icon_text_layout.addWidget(text_label)
    layout.addLayout(icon_text_layout)

    level_label = QLabel(f"Your {skill.capitalize()} level is now {level}")
    level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    level_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
    layout.addWidget(level_label)

    # ... (rest of the function remains the same)

    # Add a decorative line
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    layout.addWidget(line)

    # Add OK button
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    ok_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 5px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

    dialog.setLayout(layout)
    dialog.exec()

def show_craft_selection():
    dialog = QDialog(mw)
    dialog.setWindowTitle("Craft Selection")
    dialog.setMinimumWidth(400)
    dialog.setMinimumHeight(500)  # Set a minimum height for the dialog

    layout = QVBoxLayout()

    title_label = QLabel("Select Item to Craft")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Create a scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("border: none;")

    # Create a widget to hold the grid layout
    scroll_content = QWidget()
    grid_layout = QGridLayout(scroll_content)
    grid_layout.setSpacing(10)

    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for item, data in CRAFTING_DATA.items():
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)

        # Item image
        item_image = QLabel()
        pixmap = QPixmap(CRAFTED_ITEM_IMAGES.get(item, ""))
        item_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        item_layout.addWidget(item_image, alignment=Qt.AlignmentFlag.AlignCenter)

        # Item name and level
        item_info = QLabel(f"{item}\nLevel: {data['level']}")
        item_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(item_info)

        # Radio button for selection
        radio_button = QRadioButton()
        radio_button.setChecked(item == player_data.get("current_craft", "None"))

        # Check if player meets level and material requirements
        if data["level"] > player_data["crafting_level"] or not has_crafting_materials(item):
            radio_button.setEnabled(False)
            item_widget.setStyleSheet("color: gray;")

        button_group.addButton(radio_button)
        radio_button.item_name = item
        item_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(item_widget, row, col)
        col += 1
        if col > 2:  # 3 items per row
            col = 0
            row += 1

    # Set the scroll content
    scroll_area.setWidget(scroll_content)

    # Add the scroll area to the main layout
    layout.addWidget(scroll_area)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            player_data["current_craft"] = selected_button.item_name
            save_player_data()

def has_crafting_materials(item):
    requirements = CRAFTING_DATA[item]["requirements"]
    for material, amount in requirements.items():
        if material == "Soft clay":
            if player_data["inventory"].get("Soft clay", 0) < amount:
                return False
        elif player_data["inventory"].get(material, 0) < amount:
            return False
    return True

def on_crafting_answer():
    item = player_data["current_craft"]
    item_data = CRAFTING_DATA[item]

    # Check if player has required materials
    if not has_crafting_materials(item):
        show_error_message("Insufficient materials", f"You don't have enough materials to craft {item}.")
        return

    # Special handling for Soft clay
    if item == "Soft clay":
        if create_soft_clay():
            exp_gained = item_data["exp"]
            player_data["crafting_exp"] += exp_gained
            level_up_check("Crafting")
            check_achievements()
            save_player_data()
            if hasattr(mw, 'exp_popup'):
                mw.exp_popup.show_exp(exp_gained)
            else:
                mw.exp_popup = ExpPopup(mw)
                mw.exp_popup.show_exp(exp_gained)
        else:
            show_error_message("Insufficient materials", "You don't have enough Clay to create Soft clay.")
        return

    # Deduct materials from inventory
    for material, amount in item_data["requirements"].items():
        if not safe_deduct_from_inventory(material, amount):
            show_error_message("Insufficient materials", f"You don't have enough {material} to craft {item}.")
            return

    # Add crafted item to inventory
    player_data["inventory"][item] = player_data["inventory"].get(item, 0) + 1

    # Award experience
    exp_gained = item_data["exp"]
    player_data["crafting_exp"] += exp_gained
    level_up_check("Crafting")

    # Show experience popup
    if hasattr(mw, 'exp_popup'):
        mw.exp_popup.show_exp(exp_gained)
    else:
        mw.exp_popup = ExpPopup(mw)
        mw.exp_popup.show_exp(exp_gained)

    check_achievements()
    save_player_data()

def show_bar_selection():
    dialog = QDialog(mw)
    dialog.setWindowTitle("Bar Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    title_label = QLabel("Select Bar to Smelt")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for bar_name, bar_data in BAR_DATA.items():
        bar_widget = QWidget()
        bar_layout = QVBoxLayout(bar_widget)

        # Bar image
        bar_image = QLabel()
        pixmap = QPixmap(BAR_IMAGES[bar_name])
        bar_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        bar_layout.addWidget(bar_image, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bar name and level
        bar_info = QLabel(f"{bar_name}\nLevel: {bar_data['level']}")
        bar_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_layout.addWidget(bar_info)

        # Radio button for selection
        radio_button = QRadioButton()
        radio_button.setChecked(bar_name == player_data.get("current_bar", ""))

        if 'smithing_level' not in player_data:
            player_data['smithing_level'] = 1  # Set a default value

        if bar_data["level"] > player_data["smithing_level"]:
            radio_button.setEnabled(False)
            bar_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.bar_name = bar_name
        bar_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(bar_widget, row, col)
        col += 1
        if col > 2:
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            player_data["current_bar"] = selected_button.bar_name
            save_player_data()


def show_tree_selection():
    dialog = QDialog(mw)
    dialog.setWindowTitle("Tree Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    # Add a title label
    title_label = QLabel("Select Tree to Cut")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Create a grid layout for tree selection
    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for tree_name, tree_data in TREE_DATA.items():
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)

        # Tree image
        tree_image = QLabel()
        pixmap = QPixmap(TREE_IMAGES[tree_name])
        tree_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        tree_layout.addWidget(tree_image, alignment=Qt.AlignmentFlag.AlignCenter)

        # Tree name and level
        tree_info = QLabel(f"{tree_name}\nLevel: {tree_data['level']}")
        tree_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tree_layout.addWidget(tree_info)

        # Radio button for selection
        radio_button = QRadioButton()
        radio_button.setChecked(tree_name == player_data.get("current_tree", ""))
        if tree_data["level"] > player_data["woodcutting_level"]:
            radio_button.setEnabled(False)
            tree_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.tree_name = tree_name  # Store tree name as an attribute
        tree_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(tree_widget, row, col)
        col += 1
        if col > 2:  # 3 items per row
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    # Buttons
    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            player_data["current_tree"] = selected_button.tree_name
            save_player_data()

def show_ore_selection():
    dialog = QDialog(mw)
    dialog.setWindowTitle("Ore Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    # Add a title label
    title_label = QLabel("Select Ore to Mine")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Create a grid layout for ore selection
    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)  # Create a button group to ensure only one selection

    for ore, data in ORE_DATA.items():
        ore_widget = QWidget()
        ore_layout = QVBoxLayout(ore_widget)

        # Ore image
        ore_image = QLabel()
        pixmap = QPixmap(ORE_IMAGES[ore])
        ore_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        ore_layout.addWidget(ore_image, alignment=Qt.AlignmentFlag.AlignCenter)

        # Ore name and level
        ore_info = QLabel(f"{ore}\nLevel: {data['level']}")
        ore_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ore_layout.addWidget(ore_info)

        # Radio button for selection
        radio_button = QRadioButton()
        radio_button.setChecked(ore == player_data["current_ore"])
        if data["level"] > player_data["mining_level"]:
            radio_button.setEnabled(False)
            ore_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.ore_name = ore  # Store ore name as an attribute
        ore_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(ore_widget, row, col)
        col += 1
        if col > 2:  # 3 items per row
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    # Buttons
    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            player_data["current_ore"] = selected_button.ore_name
            save_player_data()

def show_stats():
    try:
        dialog = QDialog(mw)
        dialog.setWindowTitle("AnkiScape Stats")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(700)

        # Use Anki's built-in CSS classes for theme compatibility
        dialog.setStyleSheet("""
            QDialog { background-color: @CANVAS; }
            QLabel { color: @TEXT; }
            QTabWidget::pane { border: 1px solid @BORDER; background-color: @CANVAS; border-radius: 5px; }
            QTabBar::tab { background-color: @BUTTON; color: @TEXT; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: @CANVAS; border-bottom: 2px solid @ACCENT; }
            QTabBar::tab:hover { background-color: @HOVER; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Current Status
        status_label = QLabel(f"Current Skill: {current_skill}")
        status_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: @ACCENT;
            padding: 10px;
            background-color: @CANVAS;
            border-radius: 5px;
        """)
        main_layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        tabs = QTabWidget()

        # Function to create a styled QLabel
        def create_label(text, is_header=False):
            label = QLabel(text)
            if is_header:
                label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: @ACCENT;
                    margin-top: 15px;
                    margin-bottom: 10px;
                """)
            else:
                label.setStyleSheet("font-size: 14px;")
            return label

        # Function to create a tab for each skill
        def create_skill_tab(skill_name):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("border: none;")
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)
            scroll_layout.setContentsMargins(20, 20, 20, 20)

            # Skill Stats
            scroll_layout.addWidget(create_label(f"{skill_name} Stats", True))
            stats_layout = QGridLayout()
            stats_layout.setColumnStretch(1, 1)
            stats_layout.setHorizontalSpacing(15)
            stats_layout.setVerticalSpacing(10)

            level = player_data.get(f'{skill_name.lower()}_level', 1)
            exp = round(player_data.get(f'{skill_name.lower()}_exp', 0), 1)

            stats_layout.addWidget(create_label(f"{skill_name} Level:"), 0, 0)
            stats_layout.addWidget(create_label(str(level), True), 0, 1)
            stats_layout.addWidget(create_label("Total Experience:"), 1, 0)
            stats_layout.addWidget(create_label(f"{exp:,}", True), 1, 1)

            if level < 99:
                exp_to_next = round(max(0, EXP_TABLE[level] - exp), 1)
                stats_layout.addWidget(create_label("Experience to Next Level:"), 2, 0)
                stats_layout.addWidget(create_label(f"{exp_to_next:,}", True), 2, 1)

            # Add level progress bar
            progress_bar = QProgressBar()
            progress_percentage = (exp - EXP_TABLE[level - 1]) / (EXP_TABLE[level] - EXP_TABLE[level - 1]) * 100
            progress_bar.setValue(int(progress_percentage))
            progress_bar.setFormat("")
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid @BORDER;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: @ACCENT;
                    border-radius: 5px;
                }
            """)
            stats_layout.addWidget(create_label("Level Progress:"), 3, 0)
            stats_layout.addWidget(progress_bar, 3, 1)

            scroll_layout.addLayout(stats_layout)

            # Skill Inventory
            scroll_layout.addWidget(create_label(f"{skill_name} Inventory", True))
            inventory_layout = QGridLayout()
            inventory_layout.setColumnStretch(1, 1)
            inventory_layout.setHorizontalSpacing(15)
            inventory_layout.setVerticalSpacing(10)

            row = 0
            for item, amount in player_data.get('inventory', {}).items():
                if (skill_name == "Mining" and (item in ORE_DATA or item in GEM_DATA)) or \
                   (skill_name == "Woodcutting" and item in TREE_DATA) or \
                   (skill_name == "Smithing" and item in BAR_DATA) or \
                   (skill_name == "Crafting" and item in CRAFTING_DATA):
                    # Item image
                    item_image = QLabel()
                    pixmap = QPixmap(ORE_IMAGES.get(item) or TREE_IMAGES.get(item) or BAR_IMAGES.get(item) or GEM_IMAGES.get(item) or CRAFTED_ITEM_IMAGES.get(item))
                    item_image.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
                    inventory_layout.addWidget(item_image, row, 0)

                    # Item name and amount
                    inventory_layout.addWidget(create_label(item), row, 1)
                    inventory_layout.addWidget(create_label(str(amount), True), row, 2)
                    row += 1

            scroll_layout.addLayout(inventory_layout)

            scroll_content.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_content)
            tab_layout.addWidget(scroll_area)
            tab.setLayout(tab_layout)
            return tab

        # Create tabs for each skill
        tabs.addTab(create_skill_tab("Mining"), "Mining")
        tabs.addTab(create_skill_tab("Woodcutting"), "Woodcutting")
        tabs.addTab(create_skill_tab("Smithing"), "Smithing")
        tabs.addTab(create_skill_tab("Crafting"), "Crafting")

        main_layout.addWidget(tabs)
        dialog.setLayout(main_layout)
        dialog.exec()

    except Exception as e:
        print(f"Error in show_stats: {str(e)}")
        import traceback
        traceback.print_exc()


def show_achievements():
    dialog = QDialog(mw)
    dialog.setWindowTitle("Achievements")
    dialog.setMinimumWidth(700)
    dialog.setMinimumHeight(500)

    # Set a clean, light background
    dialog.setStyleSheet("""
        QDialog {
            background-color: #f5f5f5;
        }
    """)

    layout = QVBoxLayout()

    # Title with a more subtle style
    title_label = QLabel("Achievements")
    title_label.setStyleSheet("""
        font-size: 28px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 20px;
    """)
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Create tabs for different difficulty levels
    tabs = QTabWidget()
    tabs.setStyleSheet("""
        QTabWidget::pane {
            border: none;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        QTabBar::tab:hover {
            background-color: #d0d0d0;
        }
    """)

    difficulties = ["Easy", "Moderate", "Difficult", "Very Challenging"]

    for difficulty in difficulties:
        tab = QWidget()
        tab_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for achievement, data in ACHIEVEMENTS.items():
            if data["difficulty"] == difficulty:
                achievement_widget = QWidget()
                achievement_layout = QHBoxLayout()

                # Achievement icon
                icon_label = QLabel()
                icon_path = os.path.join(current_dir, "icon", f"{achievement.lower().replace(' ', '_')}.png")
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                else:
                    pixmap = QPixmap(os.path.join(current_dir, "icon", "achievement_icon.png"))
                icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
                achievement_layout.addWidget(icon_label)

                # Achievement info
                info_widget = QWidget()
                info_layout = QVBoxLayout()
                name_label = QLabel(achievement)
                name_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 16px;")
                desc_label = QLabel(data["description"])
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #666666; font-size: 14px;")
                info_layout.addWidget(name_label)
                info_layout.addWidget(desc_label)
                info_widget.setLayout(info_layout)
                achievement_layout.addWidget(info_widget, stretch=1)

                # Achievement status
                completed = achievement in player_data["completed_achievements"]
                status_label = QLabel("✓" if completed else "")
                status_label.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
                achievement_layout.addWidget(status_label)

                achievement_widget.setLayout(achievement_layout)
                achievement_widget.setStyleSheet(f"""
                    background-color: {'#e8f5e9' if completed else 'white'};
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 8px;
                """)

                scroll_layout.addWidget(achievement_widget)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        tabs.addTab(tab, difficulty)

    layout.addWidget(tabs)

    # Add a progress summary with a cleaner style
    completed_count = len(player_data['completed_achievements'])
    total_count = len(ACHIEVEMENTS)
    progress_percentage = (completed_count / total_count) * 100
    progress_label = QLabel(f"Completed: {completed_count}/{total_count} ({progress_percentage:.1f}%)")
    progress_label.setStyleSheet("""
        font-size: 18px;
        margin-top: 20px;
        color: #333333;
    """)
    layout.addWidget(progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Add a progress bar with a more subtle design
    progress_bar = QProgressBar()
    progress_bar.setValue(int(progress_percentage))
    progress_bar.setTextVisible(False)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: none;
            background-color: #e0e0e0;
            border-radius: 4px;
            height: 8px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
    """)
    layout.addWidget(progress_bar)

    dialog.setLayout(layout)
    dialog.exec()


# UI
def create_menu():
    global menu, ore_selection_action, tree_selection_action, bar_selection_action, craft_selection_action, stats_action, achievements_action
    menu = QMenu("AnkiScape", mw)
    mw.form.menubar.addMenu(menu)

    skill_selection_action = menu.addAction("Skill Selection")
    skill_selection_action.triggered.connect(show_skill_selection)

    # Add Ore Selection, Tree Selection, Stats, and Achievements (initially hidden)
    ore_selection_action = menu.addAction("Ore Selection")
    ore_selection_action.triggered.connect(show_ore_selection)
    ore_selection_action.setVisible(False)

    tree_selection_action = menu.addAction("Tree Selection")
    tree_selection_action.triggered.connect(show_tree_selection)
    tree_selection_action.setVisible(False)

    bar_selection_action = menu.addAction("Bar Selection")
    bar_selection_action.triggered.connect(show_bar_selection)
    bar_selection_action.setVisible(False)

    craft_selection_action = menu.addAction("Craft Selection")
    craft_selection_action.triggered.connect(show_craft_selection)
    craft_selection_action.setVisible(False)

    stats_action = menu.addAction("Stats")
    stats_action.triggered.connect(show_stats)
    stats_action.setVisible(False)

    achievements_action = menu.addAction("Achievements")
    achievements_action.triggered.connect(show_achievements)
    achievements_action.setVisible(False)


# Main functionality

def on_smithing_answer():
    bar = player_data["current_bar"]
    bar_data = BAR_DATA[bar]
    player_level = player_data["smithing_level"]

    if player_level < bar_data["level"]:
        show_error_message("Insufficient level", f"You need level {bar_data['level']} Smithing to smelt {bar}.")
        return

    # Check if player has required ores
    for ore, amount in bar_data["ore_required"].items():
        if player_data["inventory"].get(ore, 0) < amount:
            show_error_message("Insufficient ore", f"You need {amount} {ore} to smelt {bar}.")
            return

    # Deduct ores from inventory
    for ore, amount in bar_data["ore_required"].items():
        player_data["inventory"][ore] -= amount

    # Add bar to inventory
    player_data["inventory"][bar] = player_data["inventory"].get(bar, 0) + 1

    # Award experience
    exp_gained = bar_data["exp"]
    player_data["smithing_exp"] += exp_gained
    level_up_check("Smithing")
    check_achievements()
    save_player_data()

    # Show experience popup
    if hasattr(mw, 'exp_popup'):
        mw.exp_popup.show_exp(exp_gained)
    else:
        mw.exp_popup = ExpPopup(mw)
        mw.exp_popup.show_exp(exp_gained)


def on_woodcutting_answer():
    tree = player_data["current_tree"]
    tree_data = TREE_DATA[tree]
    player_level = player_data["woodcutting_level"]

    # Calculate woodcutting probability
    woodcutting_probability = calculate_woodcutting_probability(player_level, tree_data["probability"])

    # Check if woodcutting is successful
    if random.random() < woodcutting_probability:
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += 1

        exp_gained = tree_data["exp"]
        player_data["woodcutting_exp"] += exp_gained
        player_data["inventory"][tree] = player_data["inventory"].get(tree, 0) + 1
        level_up_check("Woodcutting")

        check_achievements()
        save_player_data()

        # Show experience popup
        if hasattr(mw, 'exp_popup'):
            mw.exp_popup.show_exp(exp_gained)
        else:
            mw.exp_popup = ExpPopup(mw)
            mw.exp_popup.show_exp(exp_gained)


def calculate_woodcutting_probability(player_level, tree_probability):
    level_bonus = player_level * LEVEL_BONUS_FACTOR
    return min(BASE_WOODCUTTING_PROBABILITY + level_bonus, 0.95) * tree_probability


def calculate_mining_probability(player_level, ore_probability):
    level_bonus = player_level * LEVEL_BONUS_FACTOR
    return min(BASE_MINING_PROBABILITY + level_bonus, 0.95) * ore_probability


def on_good_answer():
    global current_skill, exp_awarded
    if exp_awarded:
        return
    if current_skill == "Mining":
        ore = player_data["current_ore"]
        ore_data = ORE_DATA[ore]
        player_level = player_data["mining_level"]

        # Calculate mining probability
        mining_probability = calculate_mining_probability(player_level, ore_data["probability"])

        # Check if mining is successful
        if random.random() < mining_probability:
            if "ores_mined_today" not in player_data:
                player_data["ores_mined_today"] = 0
            player_data["ores_mined_today"] += 1

            exp_gained = ore_data["exp"]
            player_data["mining_exp"] += exp_gained
            player_data["inventory"][ore] = player_data["inventory"].get(ore, 0) + 1

            # Check for gem mining (1/256 chance)
            if random.random() < 1 / 256:
                gem = roll_gem()
                if gem:
                    player_data["inventory"][gem] = player_data["inventory"].get(gem, 0) + 1
                    exp_gained += GEM_DATA[gem]["exp"]
                    player_data["mining_exp"] += GEM_DATA[gem]["exp"]

            level_up_check("Mining")
            check_achievements()
            save_player_data()

            # Show experience popup
            if hasattr(mw, 'exp_popup'):
                mw.exp_popup.show_exp(exp_gained)
            else:
                mw.exp_popup = ExpPopup(mw)
                mw.exp_popup.show_exp(exp_gained)

    elif current_skill == "Woodcutting":
        on_woodcutting_answer()

    elif current_skill == "Smithing":
        on_smithing_answer()

    elif current_skill == "Crafting":
        on_crafting_answer()

    exp_awarded = True


def roll_gem():
    roll = random.random()
    cumulative_prob = 0
    for gem, data in GEM_DATA.items():
        cumulative_prob += data["probability"]
        if roll < cumulative_prob:
            return gem
    return None


def on_answer_card(self, ease, _old):
    global card_turned, exp_awarded, answer_shown
    if ease > 1 and current_skill in ["Mining", "Woodcutting",
                                      "Smithing", "Crafting"] and card_turned and not exp_awarded and answer_shown:
        on_good_answer()
        exp_awarded = True
    card_turned = False
    answer_shown = False  # Reset for the next card
    return _old(self, ease)


def on_card_did_show(card):
    global card_turned, exp_awarded, answer_shown
    card_turned = True
    exp_awarded = False
    answer_shown = False


def on_show_answer(reviewer):
    global answer_shown
    answer_shown = True


def show_error_message(title, message):
    error_dialog = QMessageBox(mw)
    error_dialog.setIcon(QMessageBox.Icon.Warning)
    error_dialog.setWindowTitle(title)
    error_dialog.setText(message)
    error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_dialog.exec()


def can_smelt_any_bar():
    for bar, data in BAR_DATA.items():
        if player_data["smithing_level"] >= data["level"]:
            if all(player_data["inventory"].get(ore, 0) >= amount for ore, amount in data["ore_required"].items()):
                return True
    return False

def create_soft_clay():
    if player_data["inventory"].get("Clay", 0) > 0:
        player_data["inventory"]["Clay"] -= 1
        player_data["inventory"]["Soft clay"] = player_data["inventory"].get("Soft clay", 0) + 1
        return True
    return False

def safe_deduct_from_inventory(item, amount):
    current_amount = player_data["inventory"].get(item, 0)
    if current_amount >= amount:
        player_data["inventory"][item] = current_amount - amount
        return True
    return False

# Initialization and hooks
def initialize_exp_popup():
    mw.exp_popup = ExpPopup(mw)


# Set up hooks
addHook("profileLoaded", load_player_data)
addHook("profileLoaded", initialize_exp_popup)
addHook("profileLoaded", initialize_skill)
addHook("profileLoaded", show_review_popup)

gui_hooks.reviewer_did_show_question.append(on_card_did_show)
gui_hooks.reviewer_did_show_answer.append(on_card_did_show)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)

Reviewer._answerCard = wrap(Reviewer._answerCard, on_answer_card, "around")

# Initialize menu
create_menu()
