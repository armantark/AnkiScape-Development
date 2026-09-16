"""Shop service and vendor action rows for the item reachability audit."""

from collections import defaultdict
from typing import Any, Callable, Mapping


def build_shop_service_rows(
    shop_services: Mapping[str, Mapping[str, Any]],
    names: Callable[[Any], set[str]],
    shop_access_reachable: Callable[..., bool],
) -> tuple[list[dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    actions: list[dict[str, Any]] = []
    consumers: dict[str, set[str]] = defaultdict(set)
    producers: dict[str, set[str]] = defaultdict(set)

    for service_id, service in shop_services.items():
        if (
            service.get("visibility") != "visible"
            or service.get("action_type") != "item_conversion"
        ):
            continue
        required = names(service.get("inputs"))
        if int(service.get("price", 0) or 0) > 0:
            required.add(str(service.get("currency_item_name", "Coins")))
        outputs = names(service.get("outputs"))
        if not outputs:
            continue
        key = f"Shop service:{service_id}"
        action = {
            "id": key,
            "required": required,
            "alternatives": (),
            "outputs": outputs,
        }
        if isinstance(service.get("access"), Mapping):
            action["is_accessible"] = (
                lambda completed, startable, reachable, progress, service=service: (
                    shop_access_reachable(
                        service,
                        completed,
                        startable,
                        reachable,
                        progress,
                    )
                )
            )
        actions.append(action)
        for item in required:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    return actions, consumers, producers


def build_vendor_action_rows(
    shop_vendor_actions: Mapping[str, Mapping[str, Any]],
    names: Callable[[Any], set[str]],
    shop_access_reachable: Callable[..., bool],
) -> tuple[list[dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    actions: list[dict[str, Any]] = []
    consumers: dict[str, set[str]] = defaultdict(set)
    producers: dict[str, set[str]] = defaultdict(set)

    for action_id, vendor_action in shop_vendor_actions.items():
        if vendor_action.get("visibility") != "visible":
            continue
        required = names(vendor_action.get("inputs"))
        if int(vendor_action.get("price", 0) or 0) > 0:
            required.add(str(vendor_action.get("currency_item_name", "Coins")))
        outputs = names(vendor_action.get("outputs"))
        key = f"Shop vendor:{action_id}"
        action = {
            "id": key,
            "required": required,
            "alternatives": (),
            "outputs": outputs,
        }
        if isinstance(vendor_action.get("access"), Mapping):
            action["is_accessible"] = (
                lambda completed, startable, reachable, progress, vendor_action=vendor_action: (
                    shop_access_reachable(
                        vendor_action,
                        completed,
                        startable,
                        reachable,
                        progress,
                    )
                )
            )
        actions.append(action)
        for item in required:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    return actions, consumers, producers
