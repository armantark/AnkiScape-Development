def safe_deduct_from_inventory(item, amount, player_data):
    current_amount = player_data["inventory"].get(item, 0)
    if current_amount >= amount:
        player_data["inventory"][item] = current_amount - amount
        return True
    return False
