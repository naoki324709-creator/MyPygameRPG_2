# moves_data.py

# 技のデータを辞書形式で定義
MOVE_DATABASE = {
    "taiatari": {
        "id": "taiatari",
        "name": "たいあたり",
        "power": 30,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "normal",
        "effect": None
    },
    "turunomuti": {
        "id": "turunomuti",
        "name": "つるのムチ",
        "power": 45,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "grass",
        "effect": None
    },
    "hinoko": {
        "id": "hinoko",
        "name": "ひのこ",
        "power": 1,
        "accuracy": 1.0, 
        "category": "special",
        "type": "fire",
        "effect": {"type": "burn", "chance": 1}
    },
    "awa": {
        "id": "awa",
        "name": "あわ",
        "power": 40,
        "accuracy": 1.0, 
        "category": "special",
        "type": "water",
        "effect": None
    },
    "poison_sting": {
        "id": "poison_sting",
        "name": "どくばり",
        "power": 15,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "poison",
        "effect": {"type": "poison", "chance": 0.3}
    },
    "thunder_wave": {
        "id": "thunder_wave",
        "name": "でんじは",
        "power": 0,
        "accuracy": 0.7, 
        "category": "status",
        "type": "electric",
        "effect": {"type": "paralysis", "chance": 1.0}
    },
    "toxic": {
        "id": "toxic",
        "name": "どくどく",
        "power": 0,
        "accuracy": 0.9,
        "category": "status",
        "type": "poison",
        "effect": {"type": "toxic", "chance": 1.0}
    },
    "sing": {
        "id": "sing",
        "name": "うたう",
        "power": 0,
        "accuracy": 0.55,
        "category": "status",
        "type": "normal",
        "effect": {"type": "sleep", "chance": 1.0}
    },
    "swords_dance": {
        "id": "swords_dance",
        "name": "つるぎのまい",
        "power": 0,
        "accuracy": 1.0,
        "category": "status",
        "type": "normal",
        "effect": {
            "type": "stat_change",
            "stat": "attack",
            "stages": 2,
            "target": "self"
        }
    },
    "ice_beam": {
        "id": "ice_beam",
        "name": "れいとうビーム",
        "power": 90,
        "accuracy": 1.0,
        "category": "special",
        "type": "ice",
        "effect": {"type": "freeze", "chance": 1}
    }
}