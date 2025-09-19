# monsters_data.py

# モンスターの「種族値」データを定義
MONSTER_DATABASE = {
    "bulbasaur": {
        "name": "フシギダネ",
        "types": ["grass", "poison"],
        "base_hp": 45,
        "base_attack": 49,
        "base_defense": 49,
        "base_sp_attack": 65,
        "base_sp_defense": 65,
        "base_speed": 4,
        "moves": ["taiatari", "ice_beam", "hinoko", "swords_dance"]
    },
    "charmander": {
        "name": "ヒトカゲ",
        "types": ["fire"],
        "base_hp": 39,
        "base_attack": 52,
        "base_defense": 43,
        "base_sp_attack": 60,
        "base_sp_defense": 50,
        "base_speed": 65,
        "moves": ["taiatari"]
    },
    "squirtle": {
        "name": "ゼニガメ",
        "types": ["water"],
        "base_hp": 44,
        "base_attack": 48,
        "base_defense": 65,
        "base_sp_attack": 50,
        "base_sp_defense": 64,
        "base_speed": 43,
        "moves": ["taiatari", "ice_beam"]
    },
    "pidgey": {
        "name": "ポッポ",
        "types": ["normal", "flying"],
        "base_hp": 40,
        "base_attack": 45,
        "base_defense": 40,
        "base_sp_attack": 35,
        "base_sp_defense": 35,
        "base_speed": 56,
        "moves": ["taiatari"]
    }
}