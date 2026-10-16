"""Bank item right-click menu and its private helpers."""

from dataclasses import dataclass
from typing import Callable

try:
    from aqt.qt import QInputDialog, QMenu, QMessageBox, QWidget  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from ..core.constants import EQUIPMENT_ITEM_DATA, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA
from ..data.flash_powder_factory_data import ROGUE_KIT_OUTPUTS
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_TELEPORT_TABLETS_BY_ITEM
from ..data.impling_jar_data import IMPLING_JAR_DATA
from ..data.pack_data import ITEM_PACK_DATA
from ..data.trouble_brewing_data import TROUBLE_BREWING_RUMS_BY_ITEM
from ..logic.treasure_trails_logic import treasure_trails_view_pure
from ..logic.trouble_brewing_logic import trouble_brewing_view_pure
from ..logic_pure.logic_pure import can_equip_item_pure, full_urn_teleport_info_pure


@dataclass(frozen=True)
class BankMenuContext:
    player_data: dict
    bank_frame: "QWidget"
    on_treasure_trails_command: Callable | None
    on_attach_tool: Callable | None
    add_cooking_gauntlet_conversion_action: Callable
    on_equip_item: Callable | None
    on_consume_item: Callable | None
    on_drink_trouble_brewing_rum: Callable | None
    on_use_great_orb_project_teleport_tablet: Callable | None
    on_open_item_pack: Callable | None
    on_open_impling_jar: Callable | None
    on_convert_rogue_kit: Callable | None
    on_teleport_training_urn: Callable | None
    carried_mode_state: dict
    on_set_carried_layout_quantity: Callable | None
    prompt_set_pack_quantity: Callable
    on_discard_item: Callable | None
    bank_layout_state: dict
    bank_item_visible_order: Callable
    move_bank_item_by_step: Callable
    drop_item_on_tab: Callable
    drop_item_on_new_tab: Callable
    full_urn_tooltip: Callable
    refresh_equipment_views: Callable
    is_equippable_item: Callable[[str], bool]


def _toolbelt_attachment(ctx: BankMenuContext, item_name: str):
    """(slot label, already attached) for a Bank tool, or None if it is not one.

    The Inferno adze belongs to both families, so it reads as "Tool" and is
    only "attached" once every family holds it.
    """
    toolbelt = ctx.player_data.get("toolbelt", {}) or {}
    labels: list[str] = []
    attached: list[bool] = []
    for skill_id, slot_label, tool_data in (
        ("mining", "Pickaxe", MINING_PICKAXE_DATA),
        ("woodcutting", "Hatchet", WOODCUTTING_AXE_DATA),
    ):
        bound_ids = toolbelt.get(skill_id) or ()
        for tool_id, spec in tool_data.items():
            if spec.get("status", "implemented") != "implemented":
                continue
            if str(spec.get("display_name", tool_id)) != item_name:
                continue
            labels.append(slot_label)
            attached.append(tool_id in bound_ids)
            break
    if not labels:
        return None
    return labels[0] if len(labels) == 1 else "Tool", all(attached)


def _add_start_trail(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    trail_view = treasure_trails_view_pure(ctx.player_data)
    clue_row = next(
        (row for row in trail_view["clue_rows"] if row["item"] == item_name),
        None,
    )
    if clue_row is not None:
        start_trail_action = menu.addAction("Start trail")
        start_trail_action.setObjectName("startTreasureTrailAction")
        start_trail_action.setData(clue_row["tier"])
        start_trail_action.setEnabled(
            bool(clue_row["can_start_from_bank"])
            and ctx.on_treasure_trails_command is not None
        )
        locked_reason = str(
            clue_row["locked_reason"] or clue_row["bank_start_locked_reason"]
        )
        if locked_reason:
            start_trail_action.setToolTip(locked_reason)

        def _do_start_trail(_checked: bool = False) -> None:
            if ctx.on_treasure_trails_command is None:
                return
            result = ctx.on_treasure_trails_command(
                "start_from_bank", {"tier": clue_row["tier"]}
            ) or {}
            if result.get("ok"):
                ctx.refresh_equipment_views()

        start_trail_action.triggered.connect(_do_start_trail)
        menu.addSeparator()


def _add_toolbelt_attachment(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    tool_attachment = _toolbelt_attachment(ctx, item_name)
    if tool_attachment is not None:
        slot_label, attached = tool_attachment
        attach_action = menu.addAction(
            f"{slot_label} attached"
            if attached
            else f"Attach {item_name} to toolbelt"
        )
        attach_action.setObjectName("attachToolbeltAction")
        attach_action.setEnabled(not attached and ctx.on_attach_tool is not None)
        if attached:
            attach_action.setToolTip("This tool is already attached.")

        def _do_attach(_checked: bool = False) -> None:
            if ctx.on_attach_tool is None:
                return
            if ctx.on_attach_tool(item_name):
                ctx.refresh_equipment_views(refresh_visible_skill=True)

        attach_action.triggered.connect(_do_attach)
        menu.addSeparator()


def _add_equip(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    if ctx.is_equippable_item(item_name):
        ok, reason = can_equip_item_pure(item_name, EQUIPMENT_ITEM_DATA, ctx.player_data)
        action = menu.addAction("Equip" if ok else f"Equip ({reason})")
        action.setEnabled(bool(ok) and ctx.on_equip_item is not None)
        if not ok and reason:
            action.setToolTip(reason)

        def _do_equip(_checked: bool = False) -> None:
            if ctx.on_equip_item is None:
                return
            if ctx.on_equip_item(item_name):
                ctx.refresh_equipment_views()

        action.triggered.connect(_do_equip)
        menu.addSeparator()


def _add_consumable(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    try:
        from ..core.constants import CONSUMABLE_DATA  # type: ignore
    except Exception:
        CONSUMABLE_DATA = {}
    if item_name in CONSUMABLE_DATA:
        verb = str(CONSUMABLE_DATA[item_name].get("verb", "Drink"))
        consume_action = menu.addAction(f"{verb} {item_name}")
        consume_action.setEnabled(amount > 0 and ctx.on_consume_item is not None)

        def _do_consume(_checked: bool = False) -> None:
            if ctx.on_consume_item is None:
                return
            result = ctx.on_consume_item(item_name)
            if result:
                ctx.refresh_equipment_views()
                message = str(result.get("message", ""))
                if message:
                    QMessageBox.information(ctx.bank_frame, item_name, message)

        consume_action.triggered.connect(_do_consume)
        menu.addSeparator()


def _add_trouble_brewing_rum(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    trouble_rum = TROUBLE_BREWING_RUMS_BY_ITEM.get(item_name)
    if trouble_rum is not None:
        rum_action = menu.addAction(f"Drink {item_name}")
        rum_action.setObjectName("drinkTroubleBrewingRumAction")
        rum_blocked = bool(trouble_brewing_view_pure(ctx.player_data)["active"])
        rum_action.setEnabled(
            amount > 0
            and not rum_blocked
            and ctx.on_drink_trouble_brewing_rum is not None
        )
        rum_action.setToolTip(
            "Finish or leave the current Trouble Brewing game first."
            if rum_blocked
            else f"Teleport to {trouble_rum.teleport_destination}. Consumes one bottle."
        )

        def _do_rum(_checked: bool = False) -> None:
            if ctx.on_drink_trouble_brewing_rum is None:
                return
            result = ctx.on_drink_trouble_brewing_rum(item_name)
            if result:
                ctx.refresh_equipment_views(refresh_visible_skill=True)

        rum_action.triggered.connect(_do_rum)
        menu.addSeparator()


def _add_runecrafting_tablet(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    teleport_tablet = GREAT_ORB_PROJECT_TELEPORT_TABLETS_BY_ITEM.get(
        item_name
    )
    if teleport_tablet is not None:
        tablet_action = menu.addAction(f"Break {item_name}")
        tablet_action.setObjectName("breakRunecraftingTeleportTabletAction")
        tablet_action.setEnabled(
            amount > 0
            and ctx.on_use_great_orb_project_teleport_tablet is not None
        )
        tablet_action.setToolTip(
            f"Teleport to {teleport_tablet['destination']}."
            + (
                " The next matching Runecrafting route skips its outbound leg."
                if teleport_tablet["altar_id"]
                else ""
            )
        )

        def _do_tablet(_checked: bool = False) -> None:
            if ctx.on_use_great_orb_project_teleport_tablet is None:
                return
            result = ctx.on_use_great_orb_project_teleport_tablet(item_name)
            if result:
                ctx.refresh_equipment_views(refresh_visible_skill=True)

        tablet_action.triggered.connect(_do_tablet)
        menu.addSeparator()


def _add_item_pack(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    if item_name in ITEM_PACK_DATA:
        content_item = str(ITEM_PACK_DATA[item_name]["content_item"])
        per_pack = int(ITEM_PACK_DATA[item_name]["content_quantity"])
        open_action = menu.addAction(f"Open {item_name}")
        open_action.setEnabled(amount > 0 and ctx.on_open_item_pack is not None)
        open_action.setToolTip(f"Receive {per_pack:,} {content_item}.")

        def _do_open(_checked: bool = False, open_all: bool = False) -> None:
            if ctx.on_open_item_pack is None:
                return
            if ctx.on_open_item_pack(item_name, open_all):
                ctx.refresh_equipment_views()

        open_action.triggered.connect(_do_open)
        if amount > 1:
            open_all_action = menu.addAction(f"Open all ({amount})")
            open_all_action.setEnabled(ctx.on_open_item_pack is not None)
            open_all_action.setToolTip(f"Receive {amount * per_pack:,} {content_item}.")
            open_all_action.triggered.connect(lambda _checked=False: _do_open(open_all=True))
        menu.addSeparator()


def _add_impling_jar(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    if item_name in IMPLING_JAR_DATA:
        loot_action = menu.addAction(f"Loot {item_name}")
        loot_action.setObjectName("lootImplingJarAction")
        loot_action.setEnabled(amount > 0 and ctx.on_open_impling_jar is not None)
        loot_action.setToolTip("Break the jar and receive one reward from its loot table.")

        def _do_loot(_checked: bool = False) -> None:
            if ctx.on_open_impling_jar is None:
                return
            result = ctx.on_open_impling_jar(item_name)
            if result:
                ctx.refresh_equipment_views()
                message = str(result.get("message", ""))
                if message:
                    QMessageBox.information(ctx.bank_frame, item_name, message)

        loot_action.triggered.connect(_do_loot)
        menu.addSeparator()


def _add_rogue_kit(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    if item_name == "Rogue kit":
        convert_menu = menu.addMenu("Convert Rogue kit to")
        convert_menu.setEnabled(
            amount > 0 and ctx.on_convert_rogue_kit is not None
        )
        for output_item in ROGUE_KIT_OUTPUTS:
            convert_action = convert_menu.addAction(output_item)
            convert_action.setObjectName(
                "rogueKit" + output_item.replace(" ", "") + "Action"
            )

            def _do_convert(
                _checked: bool = False,
                chosen_item: str = output_item,
            ) -> None:
                if ctx.on_convert_rogue_kit is None:
                    return
                if ctx.on_convert_rogue_kit(chosen_item):
                    ctx.refresh_equipment_views()

            convert_action.triggered.connect(_do_convert)
        menu.addSeparator()


def _add_urn_teleport(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    urn_info = full_urn_teleport_info_pure(ctx.player_data, item_name)
    if urn_info is not None:
        teleport_action = menu.addAction("Teleport urn")
        teleport_action.setObjectName("teleportTrainingUrnAction")
        teleport_action.setData(urn_info["urn_id"])
        teleport_action.setToolTip(ctx.full_urn_tooltip(urn_info))
        teleport_action.setEnabled(bool(urn_info["eligible"]) and ctx.on_teleport_training_urn is not None)

        def _do_teleport(_checked: bool = False, urn_id=str(urn_info["urn_id"])) -> None:
            if ctx.on_teleport_training_urn is None:
                return
            if ctx.on_teleport_training_urn(urn_id):
                ctx.refresh_equipment_views(refresh_visible_skill=True)

        teleport_action.triggered.connect(_do_teleport)
        menu.addSeparator()


def _add_carried_quantity(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    if ctx.carried_mode_state["advanced"] and ctx.on_set_carried_layout_quantity is not None:
        set_layout_action = menu.addAction("Set carried quantity…")
        set_layout_action.triggered.connect(
            lambda _checked=False, name=item_name: ctx.prompt_set_pack_quantity(name, ctx.bank_frame)
        )
        menu.addSeparator()


def _add_discard(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    amount = int((ctx.player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

    discard_action = menu.addAction("Discard X…")
    discard_action.setEnabled(amount > 0 and ctx.on_discard_item is not None)
    discard_action.setToolTip(f"Choose how many of the {amount} in your Bank to discard.")

    def _do_discard(_checked: bool = False) -> None:
        if ctx.on_discard_item is None:
            return
        quantity, ok = QInputDialog.getInt(
            ctx.bank_frame,
            "Discard from Bank",
            f"{item_name} quantity:",
            amount,
            1,
            amount,
            1,
        )
        if ok and ctx.on_discard_item(item_name, quantity):
            ctx.refresh_equipment_views()

    discard_action.triggered.connect(_do_discard)


def _add_bank_organization(menu: "QMenu", ctx: BankMenuContext, item_name: str) -> None:
    layout_state = ctx.bank_layout_state["value"]
    saved_row = layout_state["items"].get(item_name)
    if isinstance(saved_row, dict):
        menu.addSeparator()
        organize_menu = menu.addMenu("Organize")
        organize_menu.setObjectName("bankOrganizeMenu")
        manual = layout_state["sort_mode"] == "manual"
        tab_id = str(saved_row["tab_id"])
        visible_names = ctx.bank_item_visible_order(item_name)
        visible_index = visible_names.index(item_name)
        move_earlier = organize_menu.addAction("Move earlier")
        move_earlier.setEnabled(manual and visible_index > 0)
        move_earlier.triggered.connect(
            lambda _checked=False: ctx.move_bank_item_by_step(item_name, -1)
        )
        move_later = organize_menu.addAction("Move later")
        move_later.setEnabled(manual and visible_index < len(visible_names) - 1)
        move_later.triggered.connect(
            lambda _checked=False: ctx.move_bank_item_by_step(item_name, 1)
        )
        organize_menu.addSeparator()
        for tab in layout_state["tabs"]:
            destination_tab_id = str(tab["id"])
            if destination_tab_id == tab_id:
                continue
            move_to = organize_menu.addAction(f"Move to {tab['name']}")
            move_to.triggered.connect(
                lambda _checked=False, target=destination_tab_id: ctx.drop_item_on_tab(
                    item_name, target
                )
            )
        move_new = organize_menu.addAction("Move to new tab")
        move_new.triggered.connect(
            lambda _checked=False: ctx.drop_item_on_new_tab(item_name)
        )


def build_bank_item_menu(ctx: BankMenuContext, item_name: str) -> "QMenu":
    """Build the Bank row menu without opening a native popup."""
    menu = QMenu(ctx.bank_frame)
    menu.setToolTipsVisible(True)
    _add_start_trail(menu, ctx, item_name)
    _add_toolbelt_attachment(menu, ctx, item_name)
    ctx.add_cooking_gauntlet_conversion_action(
        menu,
        item_name,
        "convertCookingGauntletsAction",
        ctx.bank_frame,
    )

    _add_equip(menu, ctx, item_name)
    _add_consumable(menu, ctx, item_name)
    _add_trouble_brewing_rum(menu, ctx, item_name)
    _add_runecrafting_tablet(menu, ctx, item_name)
    _add_item_pack(menu, ctx, item_name)
    _add_impling_jar(menu, ctx, item_name)
    _add_rogue_kit(menu, ctx, item_name)
    _add_urn_teleport(menu, ctx, item_name)
    _add_carried_quantity(menu, ctx, item_name)
    _add_discard(menu, ctx, item_name)
    _add_bank_organization(menu, ctx, item_name)
    return menu
