from __future__ import annotations
from tests.test_main_menu_widget import patch


class DialogFactory:
    def _open(self, player_data: dict, current_skill: str = "Mining", **extra) -> "QDialog":
        from ankiscape.data.construction_data import HOUSE_STYLE_DATA, ROOM_DATA, SERVANT_DATA
        from ankiscape.core.constants import PRAYER_DATA
        from ankiscape.logic_pure.logic_pure import (
            apply_prayer_selection_pure,
            purchase_house_option_pure,
            purchase_house_pure,
            sanitize_prayer_selection_pure,
            unload_combat_supply_loadout_pure,
        )

        def _set_prayer_config(key, value):
            self._prayer_config_calls.append((key, value))
            if key not in {"apply_preset", "save_preset", "pin_target_preset", "target_override"}:
                player_data[key] = value
                player_data["combat_selected_prayers"] = list(
                    sanitize_prayer_selection_pure(player_data, player_data.get("combat_selected_prayers", ()))
                )
            return True

        def _set_prayer_selection(material_id, ui_method_id):
            self._prayer_calls.append((material_id, ui_method_id))
            updated, ok, _reasons = apply_prayer_selection_pure(
                player_data,
                material_id,
                ui_method_id,
                PRAYER_DATA,
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _farming_projection():
            from ankiscape.logic.farming_logic import farming_frontend_projection_pure
            return farming_frontend_projection_pure(player_data)

        def _farming_action(action_id, payload):
            from ankiscape.logic.farming_logic import apply_farming_frontend_action_pure
            self._farming_calls.append((action_id, dict(payload)))
            updated, ok, message = apply_farming_frontend_action_pure(player_data, action_id, payload)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": message}

        def _set_thieving_fight_back(enabled):
            enabled = bool(enabled)
            self._thieving_fight_back_calls.append(enabled)
            player_data["thieving_fight_back_when_caught"] = enabled
            return True

        def _set_target(key, calls, target):
            calls.append(target)
            player_data[key] = target
            return True

        def _unload_combat_loadout():
            self._combat_unload_calls.append(True)
            updated, ok, _reason = unload_combat_supply_loadout_pure(player_data)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _apply_house_result(result):
            updated, ok = result
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _agility_command(action_id, payload):
            from ankiscape.logic.agility_logic import apply_agility_command_pure

            self._agility_command_calls.append((action_id, dict(payload)))
            updated, result = apply_agility_command_pure(player_data, action_id, payload, roll=0.5)
            if result.get("allowed"):
                player_data.clear()
                player_data.update(updated)
            return {"ok": bool(result.get("allowed")), **result}

        def _slayer_command(action_id, payload):
            from ankiscape.logic.slayer_logic import get_slayer_assignment_pure

            self._slayer_command_calls.append((action_id, dict(payload)))
            if action_id == "set_combat_filter":
                player_data["slayer_combat_filter"] = bool(
                    payload.get("enabled", False)
                )
                return {
                    "ok": True,
                    "combat_filter": player_data["slayer_combat_filter"],
                }
            rolls = iter((0.0, 0.0))
            updated, ok, info = get_slayer_assignment_pure(
                player_data,
                master_id=str(payload.get("master_id", "turael_spria")),
                rng=lambda: next(rolls),
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, **info}

        def _warriors_guild_command(action_id, payload):
            from ankiscape.logic.warriors_guild_logic import (
                enter_warriors_guild_cyclops_room_pure,
                leave_warriors_guild_cyclops_room_pure,
                set_warriors_guild_policy_pure,
                show_warriors_guild_defender_pure,
            )

            self._warriors_guild_calls.append((action_id, dict(payload)))
            if action_id == "set_policy":
                result = set_warriors_guild_policy_pure(
                    player_data,
                    automation_mode=payload.get("automation_mode"),
                    payment_mode=payload.get("payment_mode"),
                    single_token=payload.get("single_token"),
                )
            elif action_id == "enter_room":
                result = enter_warriors_guild_cyclops_room_pure(player_data)
            elif action_id == "leave_room":
                result = leave_warriors_guild_cyclops_room_pure(player_data)
            else:
                result = show_warriors_guild_defender_pure(player_data)
            updated, ok, info = result
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("message", info.get("reason", ""))}

        def _livid_farm_command(action_id, payload):
            from ankiscape.logic.livid_farm_logic import (
                apply_arcane_capacitor_charge_pure,
                apply_arcane_capacitor_remove_charge_pure,
                apply_livid_farm_wish_pure,
                set_livid_farm_routine_pure,
            )

            self._livid_farm_calls.append((action_id, dict(payload)))
            if action_id == "set_routine":
                updated, ok, info = set_livid_farm_routine_pure(
                    player_data,
                    payload.get("routine"),
                )
            elif action_id == "buy_wish":
                updated, ok, info = apply_livid_farm_wish_pure(
                    player_data,
                    payload.get("wish_id"),
                )
            elif action_id == "charge_capacitor":
                updated, ok, info = apply_arcane_capacitor_charge_pure(
                    player_data,
                    payload.get("spell_id"),
                )
            elif action_id == "remove_capacitor_charge":
                updated, ok, info = (
                    apply_arcane_capacitor_remove_charge_pure(
                        player_data
                    )
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("message", info.get("reason", "")),
                **info,
            }

        def _big_chinchompa_command(action_id, payload):
            from ankiscape.logic.big_chinchompa_logic import (
                apply_big_chinchompa_reward_purchase_pure,
                set_hunter_private_ground_pure,
            )

            self._big_chinchompa_calls.append((action_id, dict(payload)))
            if action_id == "set_private_ground":
                updated, ok, info = set_hunter_private_ground_pure(
                    player_data,
                    payload.get("target_id", ""),
                    bool(payload.get("enabled", False)),
                )
            elif action_id == "buy_reward":
                updated, ok, info = (
                    apply_big_chinchompa_reward_purchase_pure(
                        player_data, payload.get("reward_id", "")
                    )
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("message", info.get("reason", "")),
                **info,
            }

        def _shooting_star_command(action_id, payload):
            from ankiscape.logic.shooting_star_logic import (
                apply_shooting_star_exchange_pure,
            )

            self._shooting_star_calls.append((action_id, dict(payload)))
            if action_id == "exchange":
                updated, ok, info = apply_shooting_star_exchange_pure(
                    player_data
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("reason", ""),
                **info,
            }

        def _fist_of_guthix_command(action_id, payload):
            from ankiscape.logic.fist_of_guthix_logic import apply_fist_of_guthix_command_pure

            self._fist_of_guthix_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fist_of_guthix_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _sorceress_garden_command(action_id, payload):
            from ankiscape.logic.sorceress_garden_logic import apply_sorceress_garden_command_pure

            self._sorceress_garden_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_sorceress_garden_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _penguin_command(action_id, payload):
            from ankiscape.logic.penguin_hide_and_seek_logic import apply_penguin_command_pure

            self._penguin_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_penguin_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _vinesweeper_command(action_id, payload):
            from ankiscape.logic.vinesweeper_logic import apply_vinesweeper_command_pure

            self._vinesweeper_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_vinesweeper_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fight_caves_command(action_id, payload):
            from ankiscape.logic.fight_caves_logic import apply_fight_caves_command_pure

            self._fight_caves_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fight_caves_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _dagannoth_kings_command(action_id, payload):
            from ankiscape.logic.dagannoth_kings_logic import (
                apply_dagannoth_kings_command_pure,
            )

            self._dagannoth_kings_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_dagannoth_kings_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _phoenix_lair_command(action_id, payload):
            from ankiscape.logic.phoenix_lair_logic import apply_phoenix_lair_command_pure

            self._phoenix_lair_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_phoenix_lair_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _skeletal_horror_command(action_id, payload):
            from ankiscape.logic.skeletal_horror_logic import (
                apply_skeletal_horror_command_pure,
            )

            self._skeletal_horror_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_skeletal_horror_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _enchanted_key_command(action_id, payload):
            from ankiscape.logic.enchanted_key_logic import (
                apply_enchanted_key_command_pure,
            )

            self._enchanted_key_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_enchanted_key_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _tears_of_guthix_command(action_id, payload):
            from ankiscape.logic.tears_of_guthix_logic import (
                apply_tears_of_guthix_command_pure,
            )

            self._tears_of_guthix_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_tears_of_guthix_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _barrows_command(action_id, payload):
            from ankiscape.logic.barrows_logic import apply_barrows_command_pure

            self._barrows_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_barrows_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _stealing_creation_command(action_id, payload):
            from ankiscape.logic.stealing_creation_logic import apply_stealing_creation_command_pure

            self._stealing_creation_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_stealing_creation_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fish_flingers_command(action_id, payload):
            from ankiscape.logic.fish_flingers_logic import apply_fish_flingers_command_pure

            self._fish_flingers_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fish_flingers_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fishing_trawler_command(action_id, payload):
            from ankiscape.logic.fishing_trawler_logic import apply_fishing_trawler_command_pure

            self._fishing_trawler_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fishing_trawler_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _great_orb_project_command(action_id, payload):
            from ankiscape.logic.great_orb_project_logic import apply_great_orb_project_command_pure

            self._great_orb_project_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_great_orb_project_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _managing_miscellania_command(action_id, payload):
            from ankiscape.logic.managing_miscellania_logic import apply_managing_miscellania_command_pure

            self._managing_miscellania_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_managing_miscellania_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _mage_arena_action(action_id, god_id):
            from ankiscape.logic_pure.logic_pure import (
                apply_mage_arena_cape_action_pure,
                set_mage_arena_alignment_pure,
            )

            self._mage_arena_calls.append((action_id, god_id))
            action = (
                set_mage_arena_alignment_pure
                if action_id == "select_alignment"
                else apply_mage_arena_cape_action_pure
            )
            updated, ok, _info = action(player_data, god_id)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _hire_servant(servant_id):
            if not servant_id:
                player_data["house_servant"] = ""
                return True
            return _apply_house_result(
                purchase_house_option_pure(
                    player_data, servant_id, SERVANT_DATA, kind="servant"
                )
            )

        save_skill_callback = extra.pop("on_save_skill", lambda *a: None)
        claim_reward_callback = extra.pop(
            "on_claim_reward",
            lambda claim_id, selected_skill_id=None: self._claim_calls.append(
                (claim_id, selected_skill_id)
            )
            or True,
        )
        combat_action_callback = extra.pop(
            "on_set_combat_action",
            lambda action: self._combat_action_calls.append(action),
        )
        combat_style_callback = extra.pop(
            "on_set_combat_style",
            lambda style: self._combat_style_calls.append(style),
        )
        combat_spell_callback = extra.pop(
            "on_set_combat_spell",
            lambda spell: self._combat_spell_calls.append(spell),
        )
        start_activity_callback = extra.pop(
            "on_start_activity",
            lambda activity: (
                self._activity_start_calls.append(activity),
                player_data.__setitem__("current_utility", activity),
                True,
            )[-1],
        )

        stop_training_callback = extra.pop(
            "on_stop_training",
            lambda: player_data.__setitem__("current_utility", "bankstanding")
            or True,
        )
        skilling_potion_callback = extra.pop(
            "on_set_skilling_potion_target", None
        )
        if skilling_potion_callback is None:
            def skilling_potion_callback(skill_id, target_id, enabled):
                from ankiscape.logic.skilling_boost_logic import (
                    set_skilling_potion_target_enabled_pure,
                )

                self._skilling_potion_calls.append(
                    (skill_id, target_id, bool(enabled))
                )
                updated, ok = set_skilling_potion_target_enabled_pure(
                    player_data, skill_id, target_id, enabled
                )
                if ok:
                    if enabled:
                        updated[
                            "current_craft"
                            if skill_id == "crafting"
                            else "current_fletch"
                        ] = target_id
                    player_data.clear()
                    player_data.update(updated)
                return ok
        self._ui.show_main_menu(
            **extra,
            player_data=player_data,
            current_skill=current_skill,
            on_save_skill=save_skill_callback,
            on_set_ore=lambda *a: None,
            on_set_tree=lambda *a: None,
            on_set_bar=lambda *a: None,
            on_set_smith=lambda rid: self._smith_calls.append(rid),
            on_set_craft=lambda rid: self._craft_calls.append(rid),
            on_set_fletch=lambda *a: None,
            on_set_skilling_potion_target=skilling_potion_callback,
            on_set_firemaking=lambda target: self._firemaking_calls.append(target),
            on_set_fishing=lambda target: self._fishing_calls.append(target),
            on_set_hunter=lambda target: self._hunter_calls.append(target),
            on_set_cooking=lambda target: self._cooking_calls.append(target),
            on_set_runecrafting=lambda target: self._runecrafting_calls.append(target),
            on_set_herblore=lambda target: _set_target(
                "current_herblore", self._herblore_calls, target
            ),
            on_set_thieving=lambda target: _set_target("current_thieving", self._thieving_calls, target),
            on_set_thieving_fight_back=_set_thieving_fight_back,
            on_set_agility=lambda target: _set_target("current_agility", self._agility_calls, target),
            on_set_summoning=lambda target: _set_target(
                "current_summoning", self._summoning_calls, target
            ),
            on_slayer_command=_slayer_command,
            on_agility_command=_agility_command,
            on_warriors_guild_command=_warriors_guild_command,
            on_livid_farm_command=_livid_farm_command,
            on_big_chinchompa_command=_big_chinchompa_command,
            on_shooting_star_command=_shooting_star_command,
            on_fist_of_guthix_command=_fist_of_guthix_command,
            on_sorceress_garden_command=_sorceress_garden_command,
            on_penguin_command=_penguin_command,
            on_vinesweeper_command=_vinesweeper_command,
            on_fight_caves_command=_fight_caves_command,
            on_dagannoth_kings_command=_dagannoth_kings_command,
            on_phoenix_lair_command=_phoenix_lair_command,
            on_skeletal_horror_command=_skeletal_horror_command,
            on_tears_of_guthix_command=_tears_of_guthix_command,
            on_enchanted_key_command=_enchanted_key_command,
            on_barrows_command=_barrows_command,
            on_stealing_creation_command=_stealing_creation_command,
            on_fish_flingers_command=_fish_flingers_command,
            on_fishing_trawler_command=_fishing_trawler_command,
            on_great_orb_project_command=_great_orb_project_command,
            on_managing_miscellania_command=_managing_miscellania_command,
            on_set_prayer_selection=_set_prayer_selection,
            on_set_magic=lambda target: _set_target("current_magic", self._magic_calls, target),
            on_set_construction=lambda target: _set_target("current_construction", self._construction_calls, target),
            on_purchase_house=lambda: _apply_house_result(purchase_house_pure(player_data)),
            on_purchase_room=lambda room_id: _apply_house_result(
                purchase_house_option_pure(player_data, room_id, ROOM_DATA, kind="room")
            ),
            on_hire_servant=_hire_servant,
            on_set_house_style=lambda style_id: _apply_house_result(
                purchase_house_option_pure(player_data, style_id, HOUSE_STYLE_DATA, kind="style")
            ),
            on_set_magic_alchemy_item=lambda item: _set_target("magic_alchemy_item", self._magic_alch_calls, item),
            on_set_farming_spell_patch=lambda patch: _set_target("farming_spell_patch", self._farming_spell_patch_calls, patch),
            on_set_utility=lambda activity: self._utility_calls.append(activity),
            on_start_activity=start_activity_callback,
            on_stop_training=stop_training_callback,
            on_set_combat=lambda target: self._combat_calls.append(target),
            on_set_combat_action=combat_action_callback,
            on_set_combat_style=combat_style_callback,
            on_set_combat_spell=combat_spell_callback,
            on_set_combat_auto_eat_threshold=lambda threshold: self._combat_threshold_calls.append(threshold),
            on_set_combat_auto_eat_food=lambda food: self._combat_food_calls.append(food),
            on_set_combat_prayer_config=_set_prayer_config,
            on_refill_combat_loadout=lambda: self._combat_refill_calls.append(True) or True,
            on_unload_combat_loadout=_unload_combat_loadout,
            on_reclaim_death_office=lambda: self._death_office_calls.append(True) or True,
            on_set_quest=lambda quest_id: self._quest_calls.append(quest_id),
            on_set_quest_route_choice=lambda quest_id, route_id: self._quest_choice_calls.append((quest_id, route_id)) or True,
            on_claim_reward=claim_reward_callback,
            on_claim_stronghold_reward=lambda: self._stronghold_claim_calls.append(True) or True,
            on_mage_arena_action=_mage_arena_action,
            get_farming_projection=_farming_projection,
            on_farming_action=_farming_action,
        )
        self.assertTrue(self._captured, "show_main_menu did not call dialog.exec()")
        return self._captured[-1]
