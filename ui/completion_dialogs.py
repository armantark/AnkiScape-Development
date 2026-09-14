"""The shared Level Up and Slayer completion dialog surface."""


def show_completion_dialog(
    dialog,
    icon_path: str | None,
    *,
    title: str,
    message: str,
    message_object_name: str,
    transition: str | None = None,
    wrap_message: bool = False,
) -> None:
    from aqt.qt import (  # type: ignore
        QLabel,
        QPixmap,
        QPushButton,
        Qt,
        QVBoxLayout,
    )

    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(380, 200)
    layout = QVBoxLayout()

    if icon_path:
        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(icon_path).scaled(
                64,
                64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    message_label = QLabel(message)
    message_label.setObjectName(message_object_name)
    message_label.setWordWrap(wrap_message)
    message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(message_label)
    if transition is not None:
        transition_label = QLabel(transition)
        transition_label.setObjectName("levelUpTransition")
        transition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: palette(text);"
        )
        layout.addWidget(transition_label)

    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
    dialog.setLayout(layout)
    dialog.exec()
