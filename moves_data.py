# moves_data.py

# 技のデータを辞書形式で定義
MOVE_DATABASE = {
    "tackle": {
        "id": "tackle",
        "name": "すいりゅうれんだ",
        "power": 30,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "fairy",
        "pp": 1, 
        "effect": None
    },
    "vine_whip": {
        "id": "vine_whip",
        "name": "つるのムチ",
        "power": 45,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "grass",
        "pp": 25, 
        "effect": None
    },
    "ember": {
        "id": "ember",
        "name": "ひのこ",
        "power": 1,
        "accuracy": 1.0, 
        "category": "special",
        "type": "fire",
        "pp": 25, 
        "effect": {"type": "burn", "chance": 1}
    },
    "awa": {
        "id": "awa",
        "name": "あわ",
        "power": 40,
        "accuracy": 1.0, 
        "category": "special",
        "type": "water",
        "pp": 25, 
        "effect": None
    },
    "poison_sting": {
        "id": "poison_sting",
        "name": "どくばり",
        "power": 15,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "poison",
        "pp": 25, 
        "effect": {"type": "poison", "chance": 0.3}
    },
    "thunder_wave": {
        "id": "thunder_wave",
        "name": "でんじは",
        "power": 0,
        "accuracy": 0.7, 
        "category": "status",
        "type": "electric",
        "pp": 25, 
        "effect": {"type": "paralysis", "chance": 1.0}
    },
    "toxic": {
        "id": "toxic",
        "name": "どくどく",
        "power": 0,
        "accuracy": 0.9,
        "category": "status",
        "type": "poison",
        "pp": 25, 
        "effect": {"type": "toxic", "chance": 1.0}
    },
    "sing": {
        "id": "sing",
        "name": "うたう",
        "power": 0,
        "accuracy": 0.55,
        "category": "status",
        "type": "normal",
        "pp": 25, 
        "effect": {"type": "sleep", "chance": 1.0}
    },
    "swords_dance": {
        "id": "swords_dance",
        "name": "つるぎのまい",
        "power": 0,
        "accuracy": 1.0,
        "category": "status",
        "type": "normal",
        "pp": 20, 
        "effect": {
            "type": "stat_change",
            "stat": "attack",
            "stages": 2,
            "target": "self"
        }
    },
    "ice_beam": {
        "id": "ice_beam",
        "name": "あんこくきょうだ",
        "power": 90,
        "accuracy": 1.0,
        "category": "special",
        "type": "ice",
        "pp": 10,
        "effect": {"type": "freeze", "chance": 1}
    }
}