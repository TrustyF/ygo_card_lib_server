def map_card(uc):
    return {
        'id': uc.card.id,
        'card_id': uc.card.card_id,
        'name': uc.card.name,
        'type': uc.card.type,
        'race': uc.card.race,
        'archetype': uc.card.archetype,
        'code': None,
        'rarity': None,
        'rarity_code': None,
        'card_price': None,
        'card_sell_price': None,
        'card_sets': [{
            'card_code': ac.card_code,
            'card_rarity': ac.card_rarity,
            'card_rarity_code': ac.card_rarity_code,
            'card_price': ac.card_price,
        } for ac in uc.card.association]
    }
