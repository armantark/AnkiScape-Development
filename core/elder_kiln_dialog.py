"""Opens The Elder Kiln's hatching exercise as a modal child of Anki's main window."""


def present_elder_kiln_hatching(command, observation):
    """Block until the player closes the exercise; the command callback does the play."""
    from ..ui.elder_kiln_hatching_dialog import ElderKilnHatchingDialog

    try:
        from aqt import mw  # type: ignore
    except ImportError:
        mw = None
    ElderKilnHatchingDialog(command, observation, parent=mw).exec()
