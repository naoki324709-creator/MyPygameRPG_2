# moves_data.py

# 技のデータを辞書形式で定義
MOVE_DATABASE = {
    "taiatari": {
        "name": "たいあたり",
        "power": 30,
        "accuracy": 1.0, 
        "category": "physical",  # ← カテゴリを追加
        "type": "normal",  # ← タイプを追加
        "effect": None # 追加効果なし
    },
    "turunomuti": {
        "name": "つるのムチ",
        "power": 45,
        "accuracy": 1.0, 
        "category": "physical",  # ← カテゴリを追加
        "type": "grass",   # ← タイプを追加
        "effect": None # 追加効果なし
    },
    "hinoko": {
        "name": "ひのこ",
        "power": 1,#40
        "accuracy": 1.0, 
        "category": "special",   # ← カテゴリを追加
        "type": "fire",    # ← タイプを追加
        "effect": {"type": "burn", "chance": 1} # ← 10%の確率で「やけど」
    },
    "awa": {
        "name": "あわ",
        "power": 40,
        "accuracy": 1.0, 
        "category": "special",   # ← カテゴリを追加
        "type": "water",   # ← タイプを追加
        "effect": None # 追加効果なし
    },
    "poison_sting": { # 新しい技を追加
        "name": "どくばり",
        "power": 15,
        "accuracy": 1.0, 
        "category": "physical",
        "type": "poison",
        "effect": {"type": "poison", "chance": 0.3} # 30%の確率で「どく」
    },
    "thunder_wave": { # 新しい技を追加
        "name": "でんじは",
        "power": 0, # ダメージはない
        "accuracy": 0.7, 
        "category": "status",
        "type": "electric",
        "effect": {"type": "paralysis", "chance": 1.0} # 100%の確率で「まひ」
    },
    "toxic": {
        "name": "どくどく",
        "power": 0,
        "accuracy": 0.9,
        "category": "status",
        "type": "poison",
        "effect": {"type": "toxic", "chance": 1.0} # 100%の確率で「もうどく」
    },
    "sing": {
        "name": "うたう",
        "power": 0,
        "accuracy": 0.55,
        "category": "status",
        "type": "normal",
        "effect": {"type": "sleep", "chance": 1.0} # 100%の確率で「ねむり」
    },
    "swords_dance": {
        "name": "つるぎのまい",
        "power": 0,
        "accuracy": 1.0, # 必中技だが念のため設定
        "category": "status",
        "type": "normal",
        "effect": {
            "type": "stat_change", # 効果の種類
            "stat": "attack",     # どの能力か
            "stages": 2,          # 何段階変化させるか
            "target": "self"      # 誰に使うか (self=自分)
        }
    },
    "ice_beam": {
        "name": "れいとうビーム",
        "power": 90,
        "accuracy": 1.0,
        "category": "special",
        "type": "ice",
        "effect": {"type": "freeze", "chance": 1} # 10%の確率で「こおり」
    }
}