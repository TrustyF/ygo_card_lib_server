def map_card(uc):
    return {
        'id': uc.card.id,
        'card_id': uc.card.card_id,
        'name': uc.card.name,
        'type': uc.card.type,
        'race': uc.card.race,
        'archetype': uc.card.archetype,
        'language': uc.card_language,
        'code': uc.card_code,
        'rarity': uc.card_rarity,
        'rarity_code': uc.card_rarity_code,
        'price': uc.card_price,
        'sell_price': uc.card_sell_price,
        'amount': uc.card_amount,
        'sets': [{
            'card_code': cc.card_code,
            'card_rarity': cc.card_rarity,
            'card_rarity_code': cc.card_rarity_code,
            'card_price': cc.card_price,
        } for cc in uc.card.coded_cards]
    }
