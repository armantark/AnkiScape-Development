"""ui_tab_shop.py - the main menu's Shop tab.

Built on first show by ``show_main_menu``: the shop browse list alone renders a
view model for every source-backed shop, which nobody needs until the tab is
clicked. See ui_menu_ctx.MainMenuCtx for the contract.
"""
from typing import Optional

try:
    from aqt.qt import (  # type: ignore
        Qt,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSize,
        QSpinBox,
        QTabWidget,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..data.shop_data import SHOP_DATA, SHOP_SERVICES, SHOP_VENDOR_ACTIONS
from ..logic.shop_logic import (
    apply_shop_buy_pure,
    apply_shop_sell_pure,
    apply_shop_service_pure,
    apply_shop_vendor_action_pure,
    preview_shop_buy_pure,
    preview_shop_sell_pure,
    preview_shop_service_pure,
    preview_shop_vendor_action_pure,
    search_shop_catalog_pure,
    shop_history_rows_pure,
    shop_view_model_pure,
    shop_view_models_pure,
)
from ..logic.cape_logic import cape_view_pure
from .ui import (
    CatalogFilterBar,
    _clear_layout,
    _item_icon_path,
    _pixel_item_icon,
    dim_text_color,
    dim_text_css,
)


def build_shop_tab(ctx) -> "QWidget":
    """Return the Shop page."""
    player_data = ctx.player_data
    dialog = ctx.dialog
    on_check_achievements = ctx.on_check_achievements
    on_save_player_data = ctx.on_save_player_data
    reward_shop_source_root = ctx.ensure_reward_shop_sources()

    # ---- Shop tab ---------------------------------------------------------
    # Frontend boundary: the tab is deliberately thin. It renders backend view
    # models and calls preview/apply APIs; it does not calculate prices, sell
    # policy, stock behavior, service eligibility, or hidden reward-shop state.
    shop_tab = QWidget()
    shop_tab.setObjectName("shopTab")
    shop_layout = QVBoxLayout(shop_tab)
    shop_layout.setContentsMargins(12, 12, 12, 12)
    shop_layout.setSpacing(8)

    shop_filter_bar = CatalogFilterBar(
        placeholder="Search shops or items",
        search_object_name="shopSearchInput",
    )
    shop_filter_bar.summary_label.setVisible(False)
    shop_search = shop_filter_bar.search_input
    shop_layout.addWidget(shop_filter_bar)

    browser = QWidget()
    browser_layout = QHBoxLayout(browser)
    browser_layout.setContentsMargins(0, 0, 0, 0)
    browser_layout.setSpacing(8)

    def _selector_column(title: str, object_name: str) -> tuple[QWidget, QListWidget]:
        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)
        column_layout.setSpacing(4)
        heading = QLabel(title)
        heading.setStyleSheet("font-weight: 600; color: palette(text);")
        column_layout.addWidget(heading)
        selector = QListWidget()
        selector.setObjectName(object_name)
        # Max height is managed by _sync_shop_detail_visibility: full height
        # while browsing, compact while a detail panel is open.
        selector.setMinimumHeight(116)
        selector.setIconSize(QSize(24, 24))
        selector.setAlternatingRowColors(True)
        selector.setStyleSheet(
            "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
            " background: palette(base); color: palette(text); padding: 3px; }"
            " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
            " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
        )
        column_layout.addWidget(selector, 1)
        return column, selector

    normal_shops_column, shop_selector = _selector_column(
        "Shops and service providers", "shopSelectionList"
    )
    reward_shops_column, reward_selector = _selector_column(
        "Activity, minigame and D&D rewards", "rewardShopTargetList"
    )
    browser_layout.addWidget(normal_shops_column, 1)
    browser_layout.addWidget(reward_shops_column, 1)
    shop_layout.addWidget(browser, 1)

    shop_placeholder = QLabel(
        "Choose a normal shop on the left or a reward shop on the right."
    )
    shop_placeholder.setObjectName("shopDetailPlaceholder")
    shop_placeholder.setStyleSheet(f"color: {dim_text_css(shop_placeholder)}; padding: 2px;")
    shop_layout.addWidget(shop_placeholder)

    shop_shell = QWidget()
    shop_shell.setObjectName("shopDetailShell")
    shop_shell.setStyleSheet(
        "QWidget#shopDetailShell { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); }"
    )
    shop_shell_layout = QVBoxLayout(shop_shell)
    shop_shell_layout.setContentsMargins(10, 8, 10, 10)
    shop_shell_layout.setSpacing(8)

    shop_header = QWidget()
    shop_header_layout = QHBoxLayout(shop_header)
    shop_header_layout.setContentsMargins(0, 0, 0, 0)
    shop_header_layout.setSpacing(8)
    shop_title = QLabel("Select a shop")
    shop_title.setObjectName("shopDetailTitle")
    shop_title.setStyleSheet("font-size: 14px; font-weight: 700; color: palette(text);")
    shop_meta = QLabel("")
    shop_meta.setObjectName("shopDetailMeta")
    shop_meta.setStyleSheet(f"color: {dim_text_css(shop_meta)};")
    shop_collapse_btn = QToolButton()
    shop_collapse_btn.setObjectName("shopDetailCollapseButton")
    shop_collapse_btn.setText("Close ✕")
    shop_collapse_btn.setToolTip("Collapse this shop panel and return to the shop list")
    shop_collapse_btn.setStyleSheet(
        "QToolButton { border: 1px solid palette(mid); border-radius: 6px;"
        " padding: 2px 8px; color: palette(text); background: transparent; }"
        " QToolButton:hover { border-color: #4CAF50; }"
    )
    shop_header_layout.addWidget(shop_title, 1)
    shop_header_layout.addWidget(shop_meta)
    shop_header_layout.addWidget(shop_collapse_btn)
    shop_shell_layout.addWidget(shop_header)

    shop_mode_tabs = QTabWidget()
    shop_mode_tabs.setObjectName("shopModeTabs")
    shop_mode_tabs.setDocumentMode(True)

    buy_page = QWidget()
    buy_layout = QVBoxLayout(buy_page)
    buy_layout.setContentsMargins(0, 0, 0, 0)
    buy_layout.setSpacing(6)
    stock_scroll = QScrollArea()
    stock_scroll.setObjectName("shopStockScroll")
    stock_scroll.setWidgetResizable(True)
    # One full tile row is the hard floor (short Anki windows must compress
    # gracefully, never overlap); taller dialogs stretch to show more rows.
    stock_scroll.setMinimumHeight(86)
    stock_scroll.setStyleSheet("QScrollArea#shopStockScroll { border: 1px solid palette(mid); border-radius: 8px; }")
    stock_content = QWidget()
    stock_grid = QGridLayout(stock_content)
    stock_grid.setContentsMargins(6, 6, 6, 6)
    stock_grid.setSpacing(6)
    # Pack tiles top-left instead of letting the grid center/stretch them
    # across leftover space (which produced floating tiles and huge gaps).
    # Column 6 and row 199 are virtual stretch-only cells past any real tile.
    stock_grid.setColumnStretch(6, 1)
    stock_grid.setRowStretch(199, 1)
    stock_scroll.setWidget(stock_content)
    buy_layout.addWidget(stock_scroll, 1)
    shop_mode_tabs.addTab(buy_page, "Buy Items")

    sell_page = QWidget()
    sell_layout = QVBoxLayout(sell_page)
    sell_layout.setContentsMargins(0, 0, 0, 0)
    sell_layout.setSpacing(6)
    sell_hint = QLabel("Select an item from your bank to sell to this shop.")
    sell_hint.setObjectName("shopSellHint")
    sell_hint.setStyleSheet(f"color: {dim_text_css(sell_hint)};")
    sell_layout.addWidget(sell_hint)
    sell_inventory = QListWidget()
    sell_inventory.setObjectName("shopSellInventoryList")
    sell_inventory.setIconSize(QSize(24, 24))
    sell_inventory.setAlternatingRowColors(True)
    sell_inventory.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
    )
    sell_layout.addWidget(sell_inventory, 1)
    shop_mode_tabs.addTab(sell_page, "Sell Items")
    shop_shell_layout.addWidget(shop_mode_tabs, 4)

    transaction_panel = QWidget()
    transaction_panel.setObjectName("shopTransactionPanel")
    transaction_panel.setStyleSheet(
        "QWidget#shopTransactionPanel { border: 1px solid palette(mid); border-radius: 8px;"
        " background: rgba(255,255,255,0.03); }"
    )
    transaction_layout = QVBoxLayout(transaction_panel)
    transaction_layout.setContentsMargins(8, 6, 8, 8)
    transaction_layout.setSpacing(5)
    shop_selected_label = QLabel("Select an item")
    shop_selected_label.setObjectName("shopSelectedItemLabel")
    shop_selected_label.setStyleSheet("font-weight: 600; color: palette(text);")
    transaction_layout.addWidget(shop_selected_label)
    quantity_row = QWidget()
    quantity_layout = QHBoxLayout(quantity_row)
    quantity_layout.setContentsMargins(0, 0, 0, 0)
    quantity_layout.setSpacing(5)
    quantity_layout.addWidget(QLabel("Qty:"))
    shop_quantity_buttons = {}
    for amount in (1, 5, 10, 50):
        btn = QPushButton(str(amount))
        btn.setObjectName(f"shopQty{amount}Button")
        btn.setMaximumWidth(44)
        shop_quantity_buttons[amount] = btn
        quantity_layout.addWidget(btn)
    shop_custom_qty = QSpinBox()
    shop_custom_qty.setObjectName("shopCustomQuantitySpin")
    shop_custom_qty.setRange(1, 999999)
    shop_custom_qty.setValue(1)
    shop_custom_qty.setMaximumWidth(92)
    quantity_layout.addWidget(shop_custom_qty)
    shop_all_qty = QPushButton("All")
    shop_all_qty.setObjectName("shopQtyAllButton")
    shop_all_qty.setMaximumWidth(50)
    quantity_layout.addWidget(shop_all_qty)
    quantity_layout.addStretch(1)
    shop_action_btn = QPushButton("Buy")
    shop_action_btn.setObjectName("shopTransactionButton")
    quantity_layout.addWidget(shop_action_btn)
    transaction_layout.addWidget(quantity_row)
    shop_preview_label = QLabel("Preview unavailable")
    shop_preview_label.setObjectName("shopPreviewLabel")
    shop_preview_label.setWordWrap(True)
    shop_preview_label.setStyleSheet(f"color: {dim_text_css(shop_preview_label)};")
    transaction_layout.addWidget(shop_preview_label)
    shop_shell_layout.addWidget(transaction_panel)

    # Services and vendor actions are not ordinary stock rows; frame them as
    # their own panel so they read as a separate section, not trailing widgets.
    services_panel = QWidget()
    services_panel.setObjectName("shopServicesPanel")
    services_panel.setStyleSheet(
        "QWidget#shopServicesPanel { border: 1px solid palette(mid); border-radius: 8px;"
        " background: rgba(255,255,255,0.03); }"
    )
    services_panel_layout = QVBoxLayout(services_panel)
    services_panel_layout.setContentsMargins(8, 6, 8, 8)
    services_panel_layout.setSpacing(5)
    # Hug the content: in provider mode this panel is the only section, and
    # without a cap it stretches and floats its rows mid-air.
    services_panel.setMaximumHeight(190)
    services_header = QLabel("Services")
    services_header.setObjectName("shopServicesHeader")
    services_header.setStyleSheet("font-weight: 600; color: palette(text);")
    services_panel_layout.addWidget(services_header)
    service_row = QWidget()
    service_row_layout = QHBoxLayout(service_row)
    service_row_layout.setContentsMargins(0, 0, 0, 0)
    service_row_layout.setSpacing(8)
    service_list = QListWidget()
    service_list.setObjectName("shopServiceList")
    service_list.setMaximumHeight(96)
    service_list.setIconSize(QSize(24, 24))
    service_list.setAlternatingRowColors(True)
    service_list.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
    )
    service_row_layout.addWidget(service_list, 1)
    service_controls = QWidget()
    service_controls_layout = QVBoxLayout(service_controls)
    service_controls_layout.setContentsMargins(0, 0, 0, 0)
    service_controls_layout.setSpacing(5)
    service_qty = QSpinBox()
    service_qty.setObjectName("shopServiceQuantitySpin")
    service_qty.setRange(1, 999999)
    service_qty.setValue(1)
    # Vendor actions are one interaction per use (dialogue parity, owner
    # decision 2026-07-07); the backend clamps quantity to 1, so the spinner
    # is hidden until a genuinely batchable instant service exists.
    service_qty.setVisible(False)
    service_controls_layout.addWidget(service_qty)
    service_use_btn = QPushButton("Use")
    service_use_btn.setObjectName("shopServiceUseButton")
    service_controls_layout.addWidget(service_use_btn)
    service_controls_layout.addStretch(1)
    service_row_layout.addWidget(service_controls)
    services_panel_layout.addWidget(service_row)
    service_preview = QLabel("")
    service_preview.setObjectName("shopServicePreviewLabel")
    service_preview.setWordWrap(True)
    service_preview.setStyleSheet(f"color: {dim_text_css(service_preview)};")
    services_panel_layout.addWidget(service_preview)
    shop_shell_layout.addWidget(services_panel)

    # Reward shops: the named exchanges that used to sit as loose buttons on
    # skill panels. Each relay row forwards its payload to the owning skill's
    # command unchanged; the tab renders what the skill's rules allow and
    # reports the skill's message. Named buyers (Simon Templeton) are their own
    # subsection so a sale names who is buying.
    agility_rewards_panel = QWidget()
    agility_rewards_panel.setObjectName("shopAgilityRewardsPanel")
    agility_rewards_panel.setStyleSheet(
        "QWidget#shopAgilityRewardsPanel { border: 1px solid palette(mid); border-radius: 8px;"
        " background: rgba(255,255,255,0.03); }"
    )
    agility_rewards_layout = QVBoxLayout(agility_rewards_panel)
    agility_rewards_layout.setContentsMargins(8, 6, 8, 8)
    agility_rewards_layout.setSpacing(5)
    agility_rewards_header = QLabel("Agility reward shops")
    agility_rewards_header.setStyleSheet("font-weight: 600; color: palette(text);")
    agility_rewards_layout.addWidget(agility_rewards_header)

    def _agility_section(
        title: str, object_name: str
    ) -> tuple[QWidget, QGridLayout]:
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(5)
        label = QLabel(title)
        label.setObjectName(object_name)
        label.setStyleSheet(f"color: {dim_text_css(label)};")
        section_layout.addWidget(label)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(5)
        section_layout.addWidget(grid_widget)
        agility_rewards_layout.addWidget(section)
        return section, grid

    brimhaven_section, brimhaven_grid = _agility_section(
        "Brimhaven Agility Arena · Pirate Jackie the Fruit",
        "shopBrimhavenSectionLabel",
    )
    agile_section, agile_grid = _agility_section(
        "Advanced courses · the Agile worker",
        "shopAgileSectionLabel",
    )
    cape_section, cape_grid = _agility_section(
        "Capes of Accomplishment and Distinction · the skill masters",
        "shopAgilityCapeSectionLabel",
    )
    buyers_section, buyers_grid = _agility_section(
        "Agility Pyramid · Simon Templeton",
        "shopNamedBuyersSectionLabel",
    )
    agility_feedback_label = QLabel("")
    agility_feedback_label.setObjectName("shopAgilityRewardStatus")
    agility_feedback_label.setWordWrap(True)
    agility_feedback_label.setStyleSheet(
        f"color: {dim_text_css(agility_feedback_label)};"
    )
    agility_feedback_label.setVisible(False)
    agility_rewards_layout.addWidget(agility_feedback_label)

    reward_target_panel = QWidget()
    reward_target_panel.setObjectName("rewardShopTargetPanel")
    reward_target_layout = QHBoxLayout(reward_target_panel)
    reward_target_layout.setContentsMargins(0, 0, 0, 0)
    reward_target_layout.setSpacing(8)

    reward_target_scroll = QScrollArea()
    reward_target_scroll.setObjectName("rewardShopInterfaceScroll")
    reward_target_scroll.setWidgetResizable(True)
    reward_target_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    reward_target_body = QWidget()
    reward_target_content_layout = QVBoxLayout(reward_target_body)
    reward_target_content_layout.setContentsMargins(0, 0, 0, 0)
    reward_target_content_layout.setSpacing(8)
    reward_target_content_layout.addWidget(agility_rewards_panel)
    reward_target_content_layout.addStretch(1)
    reward_target_scroll.setWidget(reward_target_body)
    reward_target_layout.addWidget(reward_target_scroll, 3)

    reward_inventory_panel = QWidget()
    reward_inventory_panel.setObjectName("rewardShopInventoryPanel")
    reward_inventory_panel.setStyleSheet(
        "QWidget#rewardShopInventoryPanel { border: 1px solid palette(mid);"
        " border-radius: 8px; background: rgba(255,255,255,0.03); }"
    )
    reward_inventory_layout = QVBoxLayout(reward_inventory_panel)
    reward_inventory_layout.setContentsMargins(8, 6, 8, 8)
    reward_inventory_layout.setSpacing(5)
    reward_inventory_heading = QLabel("Inventory")
    reward_inventory_heading.setStyleSheet("font-weight: 600; color: palette(text);")
    reward_inventory_layout.addWidget(reward_inventory_heading)
    reward_inventory = QListWidget()
    reward_inventory.setObjectName("rewardShopInventoryList")
    reward_inventory.setIconSize(QSize(24, 24))
    reward_inventory.setAlternatingRowColors(True)
    reward_inventory.setMinimumWidth(220)
    reward_inventory.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
    )
    reward_inventory_layout.addWidget(reward_inventory, 1)
    reward_target_layout.addWidget(reward_inventory_panel, 2)
    shop_shell_layout.addWidget(reward_target_panel, 5)

    reward_pages: list[QWidget] = []
    reward_targets = [
        {
            "id": "brimhaven_tickets",
            "display_name": "Brimhaven tickets · Pirate Jackie the Fruit",
            "kind": "agility",
            "section": brimhaven_section,
        },
        {
            "id": "agile_worker",
            "display_name": "Advanced courses · the Agile worker",
            "kind": "agility",
            "section": agile_section,
        },
        {
            "id": "skill_masters",
            "display_name": "Skillcapes · the skill masters",
            "kind": "agility",
            "section": cape_section,
        },
        {
            "id": "simon_templeton",
            "display_name": "Agility Pyramid · Simon Templeton",
            "kind": "agility",
            "section": buyers_section,
        },
    ]

    external_reward_targets = (
        ("big_chinchompa", "Big Chinchompa rewards", ("bigChinchompaRewardShop",)),
        ("fist_of_guthix", "Fist of Guthix · Reggie", ("fistOfGuthixShop",)),
        ("vinesweeper", "Vinesweeper · Mrs Winkin", ("vinesweeperRewardShop",)),
        ("flash_powder_factory", "Flash Powder Factory", ("flashPowderFactoryRewards",)),
        ("fish_flingers", "Fish Flingers reward shop", ("fishFlingersRewardShop",)),
        ("great_orb_project", "Great Orb Project · Wizard Elriss", ("greatOrbProjectShop",)),
        ("trouble_brewing", "Trouble Brewing rewards", ("troubleBrewingRewardShop",)),
        ("castle_wars", "Castle Wars ticket shop", ("castleWarsShopButton",)),
        ("soul_wars", "Soul Wars rewards", ("soulWarsRewardShop",)),
        ("stealing_creation", "Stealing Creation reward tools", ("stealingCreationRewardShop",)),
        ("dungeoneering", "Dungeoneering rewards trader", ("dungeoneeringRewardTraderRow", "dungeoneeringRewardDetail")),
        ("crucible", "The Crucible · Trophy bones", ("crucibleRewardShop",)),
        ("mobilising_armies", "Mobilising Armies · Officer Tower", ("mobilisingArmiesRewardShop",)),
        # The Arena's goal combo lives in its plan grid, so the Shop re-homes
        # the two reward controls on their own rather than the whole row.
        ("mage_training_arena", "Mage Training Arena rewards", ("mageTrainingArenaGoalCombo", "mageTrainingArenaPurchaseButton")),
    )
    for target_id, display_name, object_names in external_reward_targets:
        source_widgets = [
            reward_shop_source_root.findChild(QWidget, object_name)
            for object_name in object_names
        ]
        if any(widget is None for widget in source_widgets):
            continue
        page = QWidget()
        page.setObjectName(f"rewardShopPage_{target_id}")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(6)
        for source_widget in source_widgets:
            source_widget.setParent(page)
            source_widget.setVisible(True)
            page_layout.addWidget(source_widget)
        page_layout.addStretch(1)
        page.setVisible(False)
        reward_target_content_layout.insertWidget(
            reward_target_content_layout.count() - 1, page
        )
        reward_pages.append(page)
        reward_targets.append(
            {
                "id": target_id,
                "display_name": display_name,
                "kind": "external",
                "page": page,
            }
        )

    history_header = QWidget()
    history_header_layout = QHBoxLayout(history_header)
    history_header_layout.setContentsMargins(0, 0, 0, 0)
    history_header_layout.setSpacing(8)
    history_label = QLabel("Recent Shop Activity")
    history_label.setStyleSheet("font-weight: 600; color: palette(text);")
    global_history_btn = QPushButton("Global recent")
    global_history_btn.setObjectName("shopGlobalHistoryButton")
    global_history_btn.setCheckable(True)
    history_header_layout.addWidget(history_label)
    history_header_layout.addStretch(1)
    history_header_layout.addWidget(global_history_btn)
    shop_shell_layout.addWidget(history_header)
    local_history = QListWidget()
    local_history.setObjectName("shopLocalHistoryList")
    local_history.setMaximumHeight(44)
    local_history.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 4px 6px; }"
    )
    global_history = QListWidget()
    global_history.setObjectName("shopGlobalHistoryList")
    global_history.setMaximumHeight(44)
    global_history.setVisible(False)
    global_history.setStyleSheet(local_history.styleSheet())
    shop_shell_layout.addWidget(local_history)
    shop_shell_layout.addWidget(global_history)

    shop_toast = QLabel("")
    shop_toast.setObjectName("shopToastLabel")
    shop_toast.setWordWrap(True)
    shop_toast.setStyleSheet("color: #4CAF50; font-weight: 600;")
    shop_toast.setVisible(False)

    # Below the fixed-height stock/services area, the shell's remaining
    # sections (transaction, reward shops, history) must survive a ~560pt
    # dialog: they scroll as one body instead of compressing to zero. The
    # stretch inside the scroll body keeps them top-aligned (dominant in
    # provider mode, where the stretchy sections are hidden).
    shop_lower_scroll = QScrollArea()
    shop_lower_scroll.setObjectName("shopLowerScroll")
    shop_lower_scroll.setWidgetResizable(True)
    shop_lower_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    shop_lower_body = QWidget()
    shop_lower_layout = QVBoxLayout(shop_lower_body)
    shop_lower_layout.setContentsMargins(0, 0, 0, 0)
    shop_lower_layout.setSpacing(8)
    for widget in (
        transaction_panel,
        history_header,
        local_history,
        global_history,
        shop_toast,
    ):
        shop_shell_layout.removeWidget(widget)
        shop_lower_layout.addWidget(widget)
    shop_lower_layout.addStretch(1)
    shop_lower_scroll.setWidget(shop_lower_body)
    shop_shell_layout.addWidget(shop_lower_scroll, 2)
    shop_layout.addWidget(shop_shell, 3)

    shop_state = {
        "shop_id": "",
        "row_id": "",
        "sell_item": "",
        # Selected service/vendor provider (Ellis, Bartender, ...). Providers
        # are their own selector entries because the backend attaches services
        # to NPC providers, not to any shop.
        "provider": "",
        "reward_target": "",
        "service_kind": "",
        "service_id": "",
    }

    def _safe_object_suffix(value: str) -> str:
        return "".join(ch if ch.isalnum() else "_" for ch in value)[:80]

    def _humanize_display(value: object, fallback: str = "") -> str:
        text = str(value or fallback).replace("_", " ").strip()
        # Only the first character changes case: backend ids are snake_case but
        # human fallbacks may carry proper nouns that .capitalize() would eat.
        return text[:1].upper() + text[1:]

    def _visible_shop_defs() -> list:
        return [
            shop for shop in SHOP_DATA.values()
            if shop.get("visibility") != "hidden"
        ]

    def _shop_live_row_count(shop: dict) -> int:
        return sum(
            1 for row in shop.get("stock", [])
            if shop.get("visibility") == "visible" and row.get("disposition") == "live"
        )

    def _shop_selector_sort_key(shop: dict) -> tuple:
        return (
            _shop_live_row_count(shop) == 0,
            shop.get("visibility") != "visible",
            str(shop.get("display_name", "")),
        )

    def _sync_shop_detail_visibility(detail_open: bool) -> None:
        # Browse-first: the shop list owns the tab until a shop is opened, and
        # gets its height back when the detail panel is collapsed.
        shop_shell.setVisible(detail_open)
        shop_placeholder.setVisible(not detail_open)
        maximum = 104 if detail_open else 16777215
        shop_selector.setMaximumHeight(maximum)
        reward_selector.setMaximumHeight(maximum)

    def _visible_service_defs() -> list:
        rows = []
        for service in SHOP_SERVICES.values():
            if service.get("visibility") == "visible":
                rows.append(("service", service))
        for action in SHOP_VENDOR_ACTIONS.values():
            if action.get("visibility") == "visible":
                rows.append(("vendor_action", action))
        return rows

    def _format_shop_price(value, currency_name: str) -> str:
        if value is None:
            return "N/A"
        try:
            amount = int(value)
        except (TypeError, ValueError):
            return "N/A"
        return f"{amount:,} {currency_name}"

    def _inventory_count_for_ui(item_name: str) -> int:
        inventory = player_data.get("inventory", {}) or {}
        try:
            return max(0, int(inventory.get(item_name, 0) or 0))
        except (TypeError, ValueError):
            return 0

    def _format_requirement_rows(rows: list) -> str:
        parts = []
        for row in rows[:3]:
            if not isinstance(row, dict):
                continue
            item_name = str(row.get("item_name", "Item"))
            owned = int(row.get("owned_quantity", 0) or 0)
            required = int(row.get("required_quantity", 0) or 0)
            parts.append(
                f"{item_name}: {owned:,} owned, {required:,} needed"
            )
        return "; ".join(parts)

    def _preview_denial_text(preview: dict, fallback: str = "") -> str:
        reason = str(preview.get("reason") or fallback or "unavailable")
        if reason == "insufficient_currency":
            currency = str(preview.get("currency_item_name", "Coins"))
            required = int(preview.get("required_currency", 0) or 0)
            owned = int(preview.get("currency_owned", 0) or 0)
            return f"Need {required:,} {currency}, you have {owned:,}."
        if reason == "missing_item":
            item_name = str(preview.get("item_name", "item"))
            owned = int(preview.get("owned_quantity", 0) or 0)
            return f"You have {owned:,} x {item_name}."
        if reason == "missing_requirements":
            missing = preview.get("missing_requirements", [])
            detail = _format_requirement_rows(missing if isinstance(missing, list) else [])
            return f"Missing requirements: {detail}." if detail else "Missing requirements."
        if reason == "skill_level":
            skill_id = _humanize_display(preview.get("skill_id"), "skill")
            required = int(preview.get("required_level", 1) or 1)
            current = int(preview.get("current_level", 1) or 1)
            return f"Requires {required} {skill_id}; you have {current}."
        if reason == "no_potions_to_decant":
            return "You have no vial potions that Bob can consolidate."
        if reason == "missing_decant_vials":
            required = int(preview.get("required_vials", 0) or 0)
            owned = int(preview.get("owned_vials", 0) or 0)
            dose = int(preview.get("target_dose", 0) or 0)
            return f"Decanting to {dose} doses needs {required:,} empty vial(s); you have {owned:,}."
        if reason == "unsupported_decant_dose":
            return "Bob can decant vial potions to 2, 3, or 4 doses."
        if reason == "missing_empty_potion_flask":
            return "Teplin needs at least one empty Potion flask."
        if reason == "insufficient_flask_doses":
            return (
                "You do not have six doses in 1–4 dose vials or partial "
                "flasks for Teplin to fill a flask."
            )
        if reason == "no_partial_flasks_to_decant":
            return "You have no 1–4 dose potion flasks for Teplin to decant."
        return _humanize_display(fallback or reason, "Unavailable")

    def _service_icon_item_name(row: dict) -> str:
        icon_item_name = row.get("icon_item_name")
        if isinstance(icon_item_name, str) and _item_icon_path(icon_item_name):
            return icon_item_name
        for key in ("outputs", "inputs"):
            for item in row.get(key, []):
                item_name = item.get("item_name")
                if isinstance(item_name, str) and _item_icon_path(item_name):
                    return item_name
        return ""

    def _set_list_item_icon(item: QListWidgetItem, item_name: str) -> None:
        icon = _pixel_item_icon(item_name, 24)
        if icon is not None:
            item.setIcon(icon)

    def _populate_reward_inventory() -> None:
        reward_inventory.clear()
        inventory = player_data.get("inventory", {}) or {}
        rows = [
            (name, int(quantity or 0))
            for name, quantity in sorted(inventory.items())
            if isinstance(name, str) and int(quantity or 0) > 0
        ]
        if not rows:
            empty = QListWidgetItem("Your inventory is empty.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            reward_inventory.addItem(empty)
            return
        for item_name, quantity in rows:
            item = QListWidgetItem(f"{item_name} x{quantity:,}")
            _set_list_item_icon(item, item_name)
            reward_inventory.addItem(item)

    # Re-homed reward controls run their own command, so the Shop only has to
    # re-read the inventory the purchase just changed.
    for page in reward_pages:
        for button in page.findChildren(QPushButton):
            button.clicked.connect(lambda _checked=False: _populate_reward_inventory())

    def _replace_player_data(new_data: dict) -> None:
        player_data.clear()
        player_data.update(new_data)

    def _persist_shop_state() -> None:
        if on_check_achievements is not None:
            on_check_achievements(player_data)
        if on_save_player_data is None:
            return
        try:
            on_save_player_data()
        except Exception:
            pass

    def _refresh_shop_views() -> None:
        reward_shop_source_root._ankiscape_refresh_reward_shops()
        _populate_shop_selector()
        _populate_reward_selector()
        _render_shop_detail()
        _populate_sell_inventory()
        _populate_shop_history()
        _populate_agility_reward_shops()

    def _refresh_after_shop_mutation(message: str) -> None:
        shop_toast.setText(message)
        shop_toast.setVisible(bool(message))
        _refresh_shop_views()
        try:
            ctx.refresh("gear")
        except Exception:
            pass

    def _shop_view() -> dict:
        # No default shop: until the user clicks a shop, there is no detail
        # view. An invalid/stale id degrades to the browse state rather than
        # silently swapping in a different shop.
        shop_id = shop_state["shop_id"]
        if not shop_id or all(shop.get("id") != shop_id for shop in _visible_shop_defs()):
            shop_state["shop_id"] = ""
            return {"exists": False, "rows": []}
        return shop_view_model_pure(player_data, shop_id)

    def _selected_buy_row(view: dict | None = None) -> Optional[dict]:
        view = view if view is not None else _shop_view()
        rows = view.get("rows", []) if isinstance(view, dict) else []
        if not rows:
            return None
        row = next((candidate for candidate in rows if candidate.get("id") == shop_state["row_id"]), None)
        if row is None:
            row = rows[0]
            shop_state["row_id"] = row.get("id", "")
        return row

    def _stock_tile_text(row: dict, currency_name: str) -> str:
        return str(row.get("item_name", "Item"))

    def _shop_row_tooltip(row: dict, currency_name: str) -> str:
        parts = [str(row.get("item_name", "Item"))]
        stock = f"{int(row.get('current_quantity', 0) or 0):,}/{int(row.get('default_quantity', 0) or 0):,}"
        parts.append(f"Stock: {stock}")
        parts.append(f"Buy: {_format_shop_price(row.get('buy_price'), currency_name)}")
        parts.append(f"Sell: {_format_shop_price(row.get('sell_price'), currency_name)}")
        if row.get("lock_reason"):
            parts.append(f"Locked: {_humanize_display(row.get('lock_reason'))}")
        if row.get("price_source"):
            parts.append(str(row.get("price_source")))
        if row.get("source"):
            parts.append(str(row.get("source")))
        return "\n".join(parts)

    def _render_stock_grid() -> None:
        _clear_layout(stock_grid)
        view = _shop_view()
        rows = view.get("rows", []) if view.get("exists") else []
        if not rows:
            empty = QLabel("No stock rows available.")
            empty.setStyleSheet(f"color: {dim_text_css(empty)};")
            stock_grid.addWidget(empty, 0, 0)
            return
        currency_name = str(view.get("currency_item_name", "Coins"))
        selected_row_id = shop_state["row_id"]
        for index, row in enumerate(rows):
            row_id = str(row.get("id", ""))
            btn = QToolButton()
            btn.setText(_stock_tile_text(row, currency_name))
            btn.setObjectName(f"shopStockTile_{_safe_object_suffix(row_id)}")
            btn.setProperty("shopRowId", row_id)
            btn.setMinimumSize(104, 66)
            icon = _pixel_item_icon(str(row.get("item_name", "")), 32)
            if icon is not None:
                btn.setIcon(icon)
                btn.setIconSize(QSize(32, 32))
            if hasattr(btn, "setToolButtonStyle"):
                try:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # type: ignore[attr-defined]
                except Exception:
                    pass
            btn.setCheckable(True)
            btn.setChecked(row_id == selected_row_id)
            btn.setToolTip(_shop_row_tooltip(row, currency_name))
            border = "#4CAF50" if row_id == selected_row_id else "palette(mid)"
            foreground = dim_text_css(btn) if row.get("lock_reason") else "palette(text)"
            btn.setStyleSheet(
                f"QToolButton {{ text-align: center; padding: 5px; border: 1px solid {border};"
                f" border-radius: 6px; color: {foreground}; background: rgba(255,255,255,0.03); }}"
                " QToolButton:hover { border-color: #4CAF50; }"
            )
            btn.clicked.connect(lambda _=False, rid=row_id: _select_stock_row(rid))
            stock_grid.addWidget(btn, index // 6, index % 6)

    def _select_stock_row(row_id: str) -> None:
        shop_state["row_id"] = row_id
        _render_stock_grid()
        _refresh_transaction_panel()

    def _populate_sell_inventory() -> None:
        current = shop_state.get("sell_item", "")
        sell_inventory.clear()
        inventory = player_data.get("inventory", {}) or {}
        items = [
            (name, int(amount or 0))
            for name, amount in sorted(inventory.items())
            if isinstance(name, str) and int(amount or 0) > 0
        ]
        if not items:
            empty = QListWidgetItem("Your bank has no sellable items.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            sell_inventory.addItem(empty)
            shop_state["sell_item"] = ""
            return
        selected_item = current if any(name == current for name, _amount in items) else items[0][0]
        shop_state["sell_item"] = selected_item
        for name, amount in items:
            item = QListWidgetItem(f"{name} x{amount:,}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            _set_list_item_icon(item, name)
            sell_inventory.addItem(item)
            if name == selected_item:
                sell_inventory.setCurrentItem(item)

    def _set_quantity(value: int) -> None:
        shop_custom_qty.blockSignals(True)
        shop_custom_qty.setValue(max(1, min(999999, int(value))))
        shop_custom_qty.blockSignals(False)
        _refresh_transaction_panel()

    def _set_all_quantity() -> None:
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row()
            if row is not None:
                _set_quantity(max(1, int(row.get("current_quantity", 1) or 1)))
                return
        else:
            item_name = shop_state.get("sell_item", "")
            if item_name:
                _set_quantity(max(1, _inventory_count_for_ui(item_name)))

    def _refresh_transaction_panel() -> None:
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        qty = int(shop_custom_qty.value())
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row(view)
            if row is None:
                shop_selected_label.setText("Select an item")
                shop_preview_label.setText("No stock row selected.")
                shop_action_btn.setText("Buy")
                shop_action_btn.setEnabled(False)
                return
            item_name = str(row.get("item_name", "Item"))
            price = _format_shop_price(row.get("buy_price"), str(view.get("currency_item_name", "Coins")))
            stock = f"{int(row.get('current_quantity', 0) or 0):,}/{int(row.get('default_quantity', 0) or 0):,}"
            shop_selected_label.setText(f"{item_name} · Stock {stock} · Buy {price}")
            preview = preview_shop_buy_pure(player_data, shop_id, str(row.get("id", "")), qty)
            if preview.get("allowed"):
                amount = int(preview.get("quantity", qty) or qty)
                total = int(preview.get("total_price", 0) or 0)
                currency = str(preview.get("currency_item_name", view.get("currency_item_name", "Coins")))
                owned_currency = int(preview.get("currency_owned", _inventory_count_for_ui(currency)) or 0)
                suffix = " (clamped)" if preview.get("clamped") else ""
                shop_preview_label.setText(f"Buy {amount:,} x {item_name} for {total:,} {currency}. You have {owned_currency:,} {currency}.{suffix}")
                shop_action_btn.setText(f"Buy {amount:,}")
                shop_action_btn.setEnabled(True)
            else:
                shop_preview_label.setText(_preview_denial_text(preview, str(row.get("lock_reason", ""))))
                shop_action_btn.setText("Buy")
                shop_action_btn.setEnabled(False)
        else:
            item_name = shop_state.get("sell_item", "")
            shop_action_btn.setText("Sell")
            if not item_name:
                shop_selected_label.setText("Select an item")
                shop_preview_label.setText("No bank item selected.")
                shop_action_btn.setEnabled(False)
                return
            owned = _inventory_count_for_ui(item_name)
            shop_selected_label.setText(f"{item_name} · You have {owned:,}")
            preview = preview_shop_sell_pure(player_data, shop_id, item_name, qty)
            if preview.get("allowed"):
                amount = int(preview.get("quantity", qty) or qty)
                total = int(preview.get("total_price", 0) or 0)
                currency = str(preview.get("currency_item_name", view.get("currency_item_name", "Coins")))
                owned = int(preview.get("owned_quantity", _inventory_count_for_ui(item_name)) or 0)
                suffix = " (clamped)" if preview.get("clamped") else ""
                shop_preview_label.setText(f"Sell {amount:,} x {item_name} for {total:,} {currency}. You have {owned:,} x {item_name}.{suffix}")
                shop_action_btn.setText(f"Sell {amount:,}")
                shop_action_btn.setEnabled(True)
            else:
                shop_preview_label.setText(_preview_denial_text(preview))
                shop_action_btn.setEnabled(False)

    def _confirm_wilderness_purchase(view: dict) -> bool:
        # Owner-declared ambush risk: confirm once per session before buying
        # in the Wilderness (same precedent as dangerous combat targets).
        if not view.get("wilderness") or shop_state.get("wilderness_confirmed"):
            return True
        answer = QMessageBox.question(
            dialog,
            "Wilderness purchase",
            "This shop is in the Wilderness: every 28 items bought risks an"
            " ambush that can kill you. Buy here anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        shop_state["wilderness_confirmed"] = True
        return True

    def _ambush_toast_suffix(result: dict) -> str:
        ambush = result.get("wilderness_ambush") or {}
        if not ambush.get("triggered"):
            return ""
        if ambush.get("died"):
            return " You were ambushed and killed — your gear is in a grave!"
        return f" You were ambushed for {int(ambush.get('damage', 0) or 0)} damage!"

    def _apply_shop_transaction() -> None:
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        qty = int(shop_custom_qty.value())
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row(view)
            if row is None:
                return
            if not _confirm_wilderness_purchase(view):
                return
            new_data, result = apply_shop_buy_pure(player_data, shop_id, str(row.get("id", "")), qty)
            if not result.get("allowed"):
                _refresh_transaction_panel()
                return
            _replace_player_data(new_data)
            _persist_shop_state()
            _refresh_after_shop_mutation(
                f"Bought {int(result.get('quantity', 0) or 0):,} x {result.get('item_name', row.get('item_name', 'item'))}."
                + _ambush_toast_suffix(result)
            )
        else:
            item_name = shop_state.get("sell_item", "")
            if not item_name:
                return
            new_data, result = apply_shop_sell_pure(player_data, shop_id, item_name, qty)
            if not result.get("allowed"):
                _refresh_transaction_panel()
                return
            _replace_player_data(new_data)
            _persist_shop_state()
            _refresh_after_shop_mutation(f"Sold {int(result.get('quantity', 0) or 0):,} x {item_name}.")

    def _service_text(kind: str, row: dict) -> str:
        label = "Service" if kind == "service" else "Vendor"
        provider = str(row.get("provider", ""))
        price = (
            "Free"
            if int(row.get("price", 0) or 0) == 0
            else _format_shop_price(
                row.get("price", 0),
                str(row.get("currency_item_name", "Coins")),
            )
        )
        inputs = ", ".join(
            f"{item.get('quantity', 1)} × {item.get('item_name')}"
            for item in row.get("inputs", [])[:2]
        )
        outputs = ", ".join(
            f"{item.get('quantity', 1)} × {item.get('item_name')}"
            for item in row.get("outputs", [])[:2]
        )
        right = f" → {outputs}" if outputs else ""
        cost_parts = [
            part for part in (inputs, price) if part and part != "Free"
        ]
        cost = " + ".join(cost_parts) if cost_parts else "Free"
        provider_selected = bool(shop_state.get("provider"))
        prefix = "" if provider_selected else f"{label}: "
        provider_suffix = "" if provider_selected else f" · {provider}"
        display_name = row.get("display_name") or _humanize_display(row.get("id"))
        return f"{prefix}{display_name}{provider_suffix} · {cost}{right}"

    def _populate_services() -> None:
        current_id = shop_state.get("service_id", "")
        service_list.clear()
        rows = _visible_service_defs()
        provider = shop_state.get("provider", "")
        if provider:
            rows = [(kind, row) for kind, row in rows if str(row.get("provider", "")) == provider]
        if not rows:
            empty = QListWidgetItem("No live services or vendor actions.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            service_list.addItem(empty)
            return
        selected = current_id if any(row.get("id") == current_id for _kind, row in rows) else rows[0][1].get("id", "")
        shop_state["service_id"] = str(selected)
        for kind, row in rows:
            item = QListWidgetItem(_service_text(kind, row))
            item.setData(Qt.ItemDataRole.UserRole, {"kind": kind, "id": row.get("id", "")})
            _set_list_item_icon(item, _service_icon_item_name(row))
            service_list.addItem(item)
            if row.get("id") == selected:
                shop_state["service_kind"] = kind
                service_list.setCurrentItem(item)
        _refresh_service_preview()

    def _selected_service_def() -> tuple[str, Optional[dict]]:
        kind = shop_state.get("service_kind", "")
        service_id = shop_state.get("service_id", "")
        if kind == "service":
            return kind, SHOP_SERVICES.get(service_id)
        if kind == "vendor_action":
            return kind, SHOP_VENDOR_ACTIONS.get(service_id)
        return "", None

    def _refresh_service_preview() -> None:
        kind, row = _selected_service_def()
        if row is None:
            service_qty.setProperty("serviceRowId", "")
            service_preview.setText("Select a service or vendor action.")
            service_use_btn.setEnabled(False)
            return
        row_id = str(row.get("id", ""))
        row_changed = service_qty.property("serviceRowId") != row_id
        action_type = row.get("action_type")
        is_decant = action_type == "decant_potions_to_dose"
        has_quantity = bool(row.get("batchable", False))
        service_qty.blockSignals(True)
        if is_decant:
            if service_qty.minimum() != 2 or service_qty.maximum() != 4:
                service_qty.setRange(2, 4)
            if row_changed:
                service_qty.setValue(int(row.get("default_target_dose", 4) or 4))
            service_qty.setPrefix("Dose ")
            service_qty.setVisible(True)
        else:
            service_qty.setPrefix("")
            service_qty.setRange(1, 999999)
            if row_changed:
                service_qty.setValue(1)
            service_qty.setVisible(has_quantity)
        service_qty.setProperty("serviceRowId", row_id)
        service_qty.blockSignals(False)
        qty = int(service_qty.value())
        if kind == "service":
            preview = preview_shop_service_pure(player_data, str(row.get("id", "")), qty)
        else:
            preview = preview_shop_vendor_action_pure(player_data, str(row.get("id", "")), qty)
        if preview.get("allowed"):
            if preview.get("family_count") is not None:
                family_count = int(preview.get("family_count", 0) or 0)
                total_doses = int(preview.get("total_doses", 0) or 0)
                if action_type == "fill_potion_flasks":
                    flasks_created = int(preview.get("flasks_created", 0) or 0)
                    returned_vials = int(preview.get("returned_vials", 0) or 0)
                    destroyed_flasks = int(preview.get("destroyed_flasks", 0) or 0)
                    detail_parts = []
                    if returned_vials:
                        detail_parts.append(
                            f"{returned_vials:,} empty "
                            f"vial{'s' if returned_vials != 1 else ''} returned"
                        )
                    if destroyed_flasks:
                        detail_parts.append(
                            f"{destroyed_flasks:,} emptied partial "
                            f"flask{'s' if destroyed_flasks != 1 else ''} destroyed"
                        )
                    detail = (
                        f" {'; '.join(detail_parts)}."
                        if detail_parts
                        else ""
                    )
                    service_preview.setText(
                        f"Teplin will fill {flasks_created:,} empty Potion "
                        f"flask{'s' if flasks_created != 1 else ''} with "
                        f"{total_doses:,} doses from {family_count:,} potion "
                        f"type{'s' if family_count != 1 else ''} for free.{detail}"
                    )
                    service_use_btn.setEnabled(True)
                    return
                if action_type == "decant_flasks_to_vials":
                    destroyed_flasks = int(preview.get("destroyed_flasks", 0) or 0)
                    created_vials = int(preview.get("created_vials", 0) or 0)
                    service_preview.setText(
                        f"Teplin will transfer {total_doses:,} doses across "
                        f"{family_count:,} potion "
                        f"type{'s' if family_count != 1 else ''} into "
                        f"{created_vials:,} vial"
                        f"{'s' if created_vials != 1 else ''} for free, "
                        f"destroying {destroyed_flasks:,} emptied "
                        f"flask{'s' if destroyed_flasks != 1 else ''}."
                    )
                    service_use_btn.setEnabled(True)
                    return
                target_dose = int(preview.get("target_dose", 4) or 4)
                returned_vials = int(preview.get("returned_vials", 0) or 0)
                required_vials = int(preview.get("required_vials", 0) or 0)
                vial_suffix = f" Bob returns {returned_vials:,} empty vial(s)." if returned_vials else ""
                if required_vials:
                    vial_suffix = f" This uses {required_vials:,} empty vial(s)."
                service_preview.setText(
                    f"Bob will consolidate {total_doses:,} doses across "
                    f"{family_count:,} potion type(s) into {target_dose}-dose vials "
                    f"for free.{vial_suffix}"
                )
                service_use_btn.setEnabled(True)
                return
            amount = int(preview.get("quantity", qty) or qty)
            total = int(preview.get("total_price", 0) or 0)
            currency = str(preview.get("currency_item_name", row.get("currency_item_name", "Coins")))
            suffix = " (clamped)" if preview.get("clamped") else ""
            requirements = (
                preview.get("requirements", [])
                if isinstance(preview.get("requirements"), list)
                else []
            )
            requirement_text = _format_requirement_rows(
                [
                    requirement
                    for requirement in requirements
                    if requirement.get("kind") != "currency"
                ]
            )
            requirement_suffix = f" {requirement_text}." if requirement_text else ""
            repetitions = "once" if amount == 1 else f"{amount:,} times"
            cost = "free" if total == 0 else f"{total:,} {currency}"
            display_name = row.get("display_name") or _humanize_display(row.get("id"))
            service_preview.setText(
                f"{display_name} {repetitions} "
                f"for {cost}.{requirement_suffix}{suffix}"
            )
            service_use_btn.setEnabled(True)
        else:
            service_preview.setText(_preview_denial_text(preview, str(row.get("lock_reason", ""))))
            service_use_btn.setEnabled(False)

    def _apply_service_transaction() -> None:
        kind, row = _selected_service_def()
        if row is None:
            return
        qty = int(service_qty.value())
        if kind == "service":
            new_data, result = apply_shop_service_pure(player_data, str(row.get("id", "")), qty)
        else:
            new_data, result = apply_shop_vendor_action_pure(player_data, str(row.get("id", "")), qty)
        if not result.get("allowed"):
            _refresh_service_preview()
            return
        _replace_player_data(new_data)
        _persist_shop_state()
        display_name = row.get("display_name") or _humanize_display(
            row.get("id"), "vendor action"
        )
        amount = int(result.get("quantity", 0) or 0)
        suffix = (
            f" {amount:,} times."
            if row.get("batchable") and amount != 1
            else "."
        )
        _refresh_after_shop_mutation(f"Used {display_name}{suffix}")
        _refresh_service_preview()

    def _run_agility_reward_command(action_id: str, payload: dict) -> None:
        on_agility_command = getattr(ctx, "on_agility_command", None)
        if on_agility_command is None:
            return
        result = on_agility_command(action_id, payload) or {}
        message = str(result.get("message", ""))
        agility_feedback_label.setText(message)
        agility_feedback_label.setVisible(bool(message))
        _refresh_shop_views()
        try:
            ctx.refresh("gear")
        except Exception:
            pass

    def _add_relay_button(
        grid: "QGridLayout",
        index: int,
        label: str,
        action_id: str,
        payload: dict,
        object_name: str,
        icon_item: str = "",
    ) -> None:
        button = QPushButton(label)
        button.setObjectName(object_name)
        button.setEnabled(getattr(ctx, "on_agility_command", None) is not None)
        if icon_item:
            icon = _pixel_item_icon(icon_item, 24)
            if icon is not None:
                button.setIcon(icon)
        button.clicked.connect(
            lambda _=False, aid=action_id, body=dict(payload): _run_agility_reward_command(aid, body)
        )
        grid.addWidget(button, index // 3, index % 3)

    on_diary_command = getattr(ctx, "on_achievement_diary_command", None)

    def _add_cape_button(grid: "QGridLayout", index: int, row: dict) -> None:
        button = QPushButton(f"{row['name']} · {row['price']:,} coins")
        button.setObjectName(f"shopCapeButton_{row['cape_id']}")
        button.setEnabled(bool(row["can_buy"]) and on_diary_command is not None)
        button.setToolTip(row["reason"] or f"Buy from {row['master']}")
        icon = _pixel_item_icon(row["name"], 20)
        if icon is not None:
            button.setIcon(icon)
        button.clicked.connect(
            lambda _=False, cape_id=row["cape_id"]: _run_cape_purchase(cape_id)
        )
        grid.addWidget(button, index // 3, index % 3)

    def _run_cape_purchase(cape_id: str) -> None:
        if on_diary_command is None:
            return
        result = on_diary_command("purchase_cape", {"cape_id": cape_id}) or {}
        message = str(result.get("message", ""))
        agility_feedback_label.setText(message)
        agility_feedback_label.setVisible(bool(message))
        _refresh_shop_views()
        try:
            ctx.refresh("gear")
        except Exception:
            pass

    def _populate_agility_reward_shops() -> None:
        for grid in (brimhaven_grid, agile_grid, cape_grid, buyers_grid):
            _clear_layout(grid)
        index = 0
        for tickets in (1, 10, 25, 100, 1000):
            suffix = "ticket" if tickets == 1 else "tickets"
            _add_relay_button(
                brimhaven_grid,
                index,
                f"Redeem {tickets} {suffix} for XP",
                "redeem_brimhaven_xp",
                {"tickets": tickets},
                "shopBrimhavenRedeemXpButton",
                "Agility arena ticket",
            )
            index += 1
        for tickets, item_name in (
            (3, "Toadflax"),
            (5, "Wergali"),
            (10, "Snapdragon"),
            (800, "Pirate's hook"),
        ):
            _add_relay_button(
                brimhaven_grid,
                index,
                f"{item_name} ({tickets} tickets)",
                "redeem_brimhaven_item",
                {"tickets": tickets},
                "shopBrimhavenRedeemItemButton",
                "Agility arena ticket",
            )
            index += 1
        for index, piece in enumerate(("Agile top", "Agile legs")):
            _add_relay_button(
                agile_grid,
                index,
                f"Claim {piece}",
                "claim_agile_piece",
                {"piece": piece},
                "shopAgileClaimButton",
                piece,
            )
        # Every row, price, label and enable comes from `cape_view_pure`; the
        # panel decides nothing about who may buy what. Agility keeps the relay
        # button it has always had — `purchase_agility_cape` is an alias that
        # now delegates to the same shared purchase, so this is one rule with
        # two entry points rather than two rules.
        _add_relay_button(
            cape_grid,
            0,
            "Agility cape · 99,000 coins",
            "purchase_agility_cape",
            {},
            "shopAgilityCapeButton",
            "Agility cape",
        )
        capes = cape_view_pure(player_data)
        rows = [
            row
            for row in capes["skillcapes"]
            if row["show_in_shop"] and row["cape_id"] != "agility"
        ]
        rows.extend(capes["distinctions"])
        for index, row in enumerate(rows, start=1):
            _add_cape_button(cape_grid, index, row)
        _add_relay_button(
            buyers_grid,
            0,
            "Pyramid top · 1,000 coins",
            "sell_pyramid_top",
            {"count": 1},
            "shopSimonTempletonSellButton",
            "Pyramid top",
        )

    def _populate_shop_history() -> None:
        local_history.clear()
        global_history.clear()
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        local_rows = shop_history_rows_pure(player_data, shop_id=shop_id, limit=4)
        global_rows = shop_history_rows_pure(player_data, limit=8)
        if not local_rows:
            empty = QListWidgetItem("No recent activity for this shop.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            local_history.addItem(empty)
        else:
            for event in local_rows:
                display = event.get("display") or _humanize_display(
                    event.get("event_id"), "Shop event"
                )
                local_history.addItem(QListWidgetItem(str(display)))
        if not global_rows:
            empty = QListWidgetItem("No global shop activity yet.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            global_history.addItem(empty)
        else:
            for event in global_rows:
                display = event.get("display") or _humanize_display(
                    event.get("event_id"), "Shop event"
                )
                global_history.addItem(QListWidgetItem(str(display)))

    def _set_shop_detail_mode(mode: str) -> None:
        # Normal shops, providers and reward targets share the shell, but never
        # advertise one another's controls. Reward interfaces own the right-hand
        # target list and always render beside the player's live inventory.
        is_shop = mode == "shop"
        is_provider = mode == "provider"
        is_reward = mode == "reward"
        shop_mode_tabs.setVisible(is_shop)
        transaction_panel.setVisible(is_shop)
        history_header.setVisible(is_shop)
        local_history.setVisible(is_shop)
        reward_target_panel.setVisible(is_reward)
        if not is_shop:
            global_history.setVisible(False)
            global_history_btn.setChecked(False)
        services_panel.setVisible(is_provider)

    def _render_shop_detail() -> None:
        target_id = shop_state.get("reward_target", "")
        if target_id:
            target = next(
                (row for row in reward_targets if row["id"] == target_id), None
            )
            if target is None:
                shop_state["reward_target"] = ""
                _sync_shop_detail_visibility(False)
                return
            _sync_shop_detail_visibility(True)
            _set_shop_detail_mode("reward")
            display_name = str(target["display_name"])
            shop_title.setText(display_name)
            shop_meta.setText("Reward shop · inventory shown alongside")
            for section in (
                brimhaven_section,
                agile_section,
                cape_section,
                buyers_section,
            ):
                section.setVisible(False)
            for page in reward_pages:
                page.setVisible(False)
            if target["kind"] == "agility":
                agility_rewards_panel.setVisible(True)
                agility_rewards_header.setText(display_name)
                target["section"].setVisible(True)
            else:
                agility_rewards_panel.setVisible(False)
                target["page"].setVisible(True)
            _populate_reward_inventory()
            return
        provider = shop_state.get("provider", "")
        if provider:
            provider_rows = [
                (kind, row)
                for kind, row in _visible_service_defs()
                if str(row.get("provider", "")) == provider
            ]
            if not provider_rows:
                shop_state["provider"] = ""
                _sync_shop_detail_visibility(False)
                return
            _sync_shop_detail_visibility(True)
            _set_shop_detail_mode("provider")
            shop_title.setText(provider)
            location = next(
                (str(row.get("location", "")) for _kind, row in provider_rows if row.get("location")),
                "",
            )
            shop_meta.setText(location)
            _populate_services()
            return
        view = _shop_view()
        if not view.get("exists"):
            shop_state["row_id"] = ""
            _sync_shop_detail_visibility(False)
            return
        _sync_shop_detail_visibility(True)
        _set_shop_detail_mode("shop")
        shop_title.setText(str(view.get("display_name", "NPC shop")))
        currency_name = str(view.get("currency_item_name", "Coins"))
        meta_parts = [f"{currency_name}: {_inventory_count_for_ui(currency_name):,} owned"]
        if view.get("wilderness"):
            meta_parts.append("Wilderness — you can be attacked")
        if view.get("general_store"):
            meta_parts.append("General store")
        if view.get("lock_reason"):
            meta_parts.append(_humanize_display(view.get("lock_reason")))
        shop_meta.setText(" · ".join(meta_parts))
        if not shop_state["row_id"] and view.get("rows"):
            shop_state["row_id"] = str(view["rows"][0].get("id", ""))
        _render_stock_grid()
        _populate_sell_inventory()
        _refresh_transaction_panel()
        _populate_shop_history()

    def _shop_selector_label_from_result(result: dict) -> str:
        kind = result.get("kind")
        if kind == "stock":
            price = _format_shop_price(result.get("buy_price"), "Coins")
            stock = f"{int(result.get('current_quantity', 0) or 0):,}/{int(result.get('default_quantity', 0) or 0):,}"
            lock = (
                f" · {_humanize_display(result.get('lock_reason'))}"
                if result.get("lock_reason")
                else ""
            )
            return f"{result.get('item_name')} · {result.get('shop_name')} · Stock {stock} · {price}{lock}"
        label = "Service" if kind == "service" else "Vendor"
        lock = (
            f" · {_humanize_display(result.get('lock_reason'))}"
            if result.get("lock_reason")
            else ""
        )
        price = int(result.get("price", 0) or 0)
        cost = (
            "Free"
            if price == 0
            else f"{price:,} {result.get('currency_item_name', 'Coins')}"
        )
        return (
            f"{label}: {result.get('display_name')} · "
            f"{result.get('provider')} · {cost}{lock}"
        )

    def _populate_shop_selector() -> None:
        current_shop_id = shop_state.get("shop_id", "")
        query = shop_search.text().strip()
        shop_selector.clear()
        if query:
            results = search_shop_catalog_pure(player_data, query, include_locked=True, include_hidden=False, limit=80).get("results", [])
            if results:
                selected_item = None
                for result in results:
                    item = QListWidgetItem(_shop_selector_label_from_result(result))
                    item.setData(Qt.ItemDataRole.UserRole, dict(result))
                    if result.get("kind") == "stock":
                        _set_list_item_icon(item, str(result.get("item_name", "")))
                    elif result.get("kind") in {"service", "vendor_action"}:
                        source = SHOP_SERVICES if result.get("kind") == "service" else SHOP_VENDOR_ACTIONS
                        service_row = source.get(str(result.get("id", "")), {})
                        _set_list_item_icon(item, _service_icon_item_name(service_row))
                    if result.get("visibility") == "visible_locked" or result.get("lock_reason"):
                        item.setForeground(dim_text_color(shop_selector))
                    shop_selector.addItem(item)
                    if result.get("kind") == "stock" and result.get("shop_id") == current_shop_id and selected_item is None:
                        selected_item = item
                if selected_item is not None:
                    shop_selector.blockSignals(True)
                    shop_selector.setCurrentItem(selected_item)
                    shop_selector.blockSignals(False)
                return
            empty = QListWidgetItem("No visible shop stock, service, or vendor action matches this search.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            shop_selector.addItem(empty)
            return
        visible = sorted(_visible_shop_defs(), key=_shop_selector_sort_key)
        selector_views = shop_view_models_pure(
            player_data, [str(shop.get("id", "")) for shop in visible]
        )
        for shop in visible:
            view = selector_views[str(shop.get("id", ""))]
            rows = view.get("rows", [])
            live_count = sum(1 for row in rows if row.get("can_buy"))
            locked_count = sum(1 for row in rows if row.get("lock_reason"))
            suffix = []
            if live_count:
                suffix.append(f"{live_count} live")
            if locked_count:
                suffix.append(f"{locked_count} locked")
            if shop.get("general_store"):
                suffix.append("general store")
            if shop.get("lock_reason"):
                suffix.append(_humanize_display(shop.get("lock_reason")))
            display_name = shop.get("display_name") or _humanize_display(shop.get("id"))
            label = f"{display_name} · " + (
                " · ".join(suffix) if suffix else "read-only"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, {"kind": "shop", "shop_id": shop.get("id", "")})
            icon_name = next(
                (
                    str(row.get("item_name", ""))
                    for row in rows
                    if _item_icon_path(str(row.get("item_name", "")))
                ),
                "",
            )
            _set_list_item_icon(item, icon_name)
            if shop.get("visibility") != "visible":
                item.setForeground(dim_text_color(shop_selector))
            shop_selector.addItem(item)
            if shop.get("id") == current_shop_id:
                shop_selector.blockSignals(True)
                shop_selector.setCurrentItem(item)
                shop_selector.blockSignals(False)
        # Service/vendor providers browse as their own entries after the shops;
        # the backend ties services to NPC providers, not shops.
        providers: dict = {}
        for kind, row in _visible_service_defs():
            providers.setdefault(str(row.get("provider", "")), []).append((kind, row))
        current_provider = shop_state.get("provider", "")
        for provider in sorted(name for name in providers if name):
            provider_rows = providers[provider]
            location = next(
                (str(row.get("location", "")) for _kind, row in provider_rows if row.get("location")),
                "",
            )
            count = len(provider_rows)
            parts = [provider]
            if location:
                parts.append(location)
            parts.append(f"{count} service{'s' if count != 1 else ''}")
            item = QListWidgetItem(" · ".join(parts))
            item.setData(Qt.ItemDataRole.UserRole, {"kind": "provider", "provider": provider})
            icon_name = next(
                (
                    _service_icon_item_name(row)
                    for _kind, row in provider_rows
                    if _service_icon_item_name(row)
                ),
                "",
            )
            _set_list_item_icon(item, icon_name)
            shop_selector.addItem(item)
            if provider == current_provider:
                shop_selector.blockSignals(True)
                shop_selector.setCurrentItem(item)
                shop_selector.blockSignals(False)

    def _populate_reward_selector() -> None:
        current_target = shop_state.get("reward_target", "")
        query = shop_search.text().strip().lower()
        reward_selector.clear()
        visible_targets = [
            target
            for target in reward_targets
            if not query or query in str(target["display_name"]).lower()
        ]
        if not visible_targets:
            empty = QListWidgetItem("No reward shop matches this search.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            reward_selector.addItem(empty)
            return
        selected_item = None
        for target in visible_targets:
            item = QListWidgetItem(str(target["display_name"]))
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"kind": "reward_target", "target_id": target["id"]},
            )
            reward_selector.addItem(item)
            if target["id"] == current_target:
                selected_item = item
        if selected_item is not None:
            reward_selector.blockSignals(True)
            reward_selector.setCurrentItem(selected_item)
            reward_selector.blockSignals(False)

    def _collapse_shop_detail() -> None:
        shop_state["shop_id"] = ""
        shop_state["row_id"] = ""
        shop_state["provider"] = ""
        shop_state["reward_target"] = ""
        for selector in (shop_selector, reward_selector):
            selector.blockSignals(True)
            selector.clearSelection()
            selector.setCurrentItem(None)
            selector.blockSignals(False)
        _render_shop_detail()

    def _on_shop_selector_clicked(item: QListWidgetItem) -> None:
        payload = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if not isinstance(payload, dict):
            return
        kind = payload.get("kind")
        shop_state["reward_target"] = ""
        reward_selector.blockSignals(True)
        reward_selector.clearSelection()
        reward_selector.setCurrentItem(None)
        reward_selector.blockSignals(False)
        if kind == "shop":
            shop_state["shop_id"] = str(payload.get("shop_id", ""))
            shop_state["row_id"] = ""
            shop_state["provider"] = ""
            _render_shop_detail()
            return
        if kind == "stock":
            shop_state["shop_id"] = str(payload.get("shop_id", ""))
            shop_state["row_id"] = str(payload.get("row_id", ""))
            shop_state["provider"] = ""
            _render_shop_detail()
            return
        if kind == "provider":
            shop_state["provider"] = str(payload.get("provider", ""))
            shop_state["shop_id"] = ""
            shop_state["row_id"] = ""
            _render_shop_detail()
            return
        if kind in {"service", "vendor_action"}:
            source = SHOP_SERVICES if kind == "service" else SHOP_VENDOR_ACTIONS
            service_row = source.get(str(payload.get("id", "")), {})
            shop_state["provider"] = str(service_row.get("provider", ""))
            shop_state["shop_id"] = ""
            shop_state["row_id"] = ""
            shop_state["service_kind"] = str(kind)
            shop_state["service_id"] = str(payload.get("id", ""))
            _render_shop_detail()
            _refresh_service_preview()

    def _on_reward_selector_clicked(item: QListWidgetItem) -> None:
        payload = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if not isinstance(payload, dict) or payload.get("kind") != "reward_target":
            return
        shop_state["reward_target"] = str(payload.get("target_id", ""))
        shop_state["shop_id"] = ""
        shop_state["row_id"] = ""
        shop_state["provider"] = ""
        shop_selector.blockSignals(True)
        shop_selector.clearSelection()
        shop_selector.setCurrentItem(None)
        shop_selector.blockSignals(False)
        _render_shop_detail()

    def _on_sell_item_clicked(item: QListWidgetItem) -> None:
        item_name = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if isinstance(item_name, str):
            shop_state["sell_item"] = item_name
            _refresh_transaction_panel()

    def _on_service_clicked(item: QListWidgetItem) -> None:
        payload = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if isinstance(payload, dict):
            shop_state["service_kind"] = str(payload.get("kind", ""))
            shop_state["service_id"] = str(payload.get("id", ""))
            _refresh_service_preview()

    shop_search.textChanged.connect(
        lambda _text="": (
            _populate_shop_selector(),
            _populate_reward_selector(),
            _render_shop_detail(),
        )
    )
    shop_selector.itemClicked.connect(_on_shop_selector_clicked)
    shop_selector.currentItemChanged.connect(lambda current, _previous: _on_shop_selector_clicked(current) if current is not None else None)
    reward_selector.itemClicked.connect(_on_reward_selector_clicked)
    reward_selector.currentItemChanged.connect(
        lambda current, _previous: _on_reward_selector_clicked(current)
        if current is not None
        else None
    )
    sell_inventory.itemClicked.connect(_on_sell_item_clicked)
    sell_inventory.currentItemChanged.connect(lambda current, _previous: _on_sell_item_clicked(current) if current is not None else None)
    shop_mode_tabs.currentChanged.connect(lambda _index=0: _refresh_transaction_panel())
    for amount, btn in shop_quantity_buttons.items():
        btn.clicked.connect(lambda _=False, qty=amount: _set_quantity(qty))
    shop_custom_qty.valueChanged.connect(lambda _value=1: _refresh_transaction_panel())
    shop_all_qty.clicked.connect(lambda _=False: _set_all_quantity())
    shop_action_btn.clicked.connect(lambda _=False: _apply_shop_transaction())
    service_list.itemClicked.connect(_on_service_clicked)
    service_list.currentItemChanged.connect(lambda current, _previous: _on_service_clicked(current) if current is not None else None)
    service_qty.valueChanged.connect(lambda _value=1: _refresh_service_preview())
    service_use_btn.clicked.connect(lambda _=False: _apply_service_transaction())
    global_history_btn.toggled.connect(lambda checked=False: global_history.setVisible(bool(checked)))
    shop_collapse_btn.clicked.connect(lambda _=False: _collapse_shop_detail())

    _populate_shop_selector()
    _populate_reward_selector()
    _populate_services()
    _populate_agility_reward_shops()
    _render_shop_detail()

    ctx.refreshers["shop"] = _refresh_shop_views
    return shop_tab
