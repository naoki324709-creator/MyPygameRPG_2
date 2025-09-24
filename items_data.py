# items_data.py

ITEM_DATABASE = {
    # ボール
    "monster_ball": {
        "name": "モンスターボール",
        "pocket": "ボール", # アイテムのカテゴリ分け
        "battle_pocket": "ボール", # 戦闘中のカテゴリ分け
        "effect": "capture",
        "power": 1.0,
        "description": "やせいの ポケモンを つかまえる ための どうぐ。"
    },
    # 回復アイテム
    "potion": {
        "name": "キズぐすり",
        "pocket": "どうぐ",
        "battle_pocket": "かいふく",
        "effect": "heal_hp",
        "power": 20,
        "description": "ポケモンの たいりょくを 20だけ かいふくする。"
    },
    # 戦闘用アイテム
    "x_attack": {
        "name": "プラスパワー",
        "pocket": "どうぐ",
        "battle_pocket": "せんとう",
        "effect": "stat_boost",
        "stat": "attack",
        "stages": 1,
        "description": "せんとうちゅう どうぐを つかって ポケモンの こうちょうを あげる。"
    },
    # わざマシン（まだ使えない）
    "tm_case": {
        "name": "わざマシンケース",
        "pocket": "わざマシン",
        "battle_pocket": None, # 戦闘中には使えない
        "effect": None,
        "description": "たくさんの わざマシンを しまって おけるべんりな ケース。"
    }
}