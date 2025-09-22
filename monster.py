# monster.py

# monsters_data.py から MONSTER_DATABASE をインポート
from monsters_data import MONSTER_DATABASE
from moves_data import MOVE_DATABASE # ← moves_dataをインポート
from exp_data import get_exp_for_level

class Monster:
    # __init__をレベル対応に変更
    def __init__(self, name, types, level, base_stats, moves,growth_rate):
        self.name = name
        self.types = types
        self.level = level
        self.base_stats = base_stats
        self.moves = moves
        self.growth_rate = growth_rate
        self.status_condition = None  # 状態異常を記録（Noneは健康な状態）
        self.toxic_counter = 0  # もうどくの経過ターンを数える
        self.sleep_counter = 0  # ねむりの残りターンを数える
        self.stat_stages = { # 能力ランクを辞書で管理。初期値は全て0。
            "attack": 0,
            "defense": 0,
            "sp_attack": 0,
            "sp_defense": 0,
            "speed": 0
        }
        # 現在のレベルになるための最低経験値
        self.exp = get_exp_for_level(level, self.growth_rate)
        # 次のレベルアップに必要な総経験値
        self.exp_to_next_level = get_exp_for_level(level + 1, self.growth_rate)


        # レベルと種族値から実際のステータスを計算
        self._calculate_stats()

        self.current_hp = self.max_hp

    # ステータスを計算する内部関数
    def _calculate_stats(self):
        # HPの計算式（簡略版）
        self.max_hp = int(self.base_stats['base_hp'] * self.level / 50) + self.level + 10
        #self.current_hp = self.max_hp

        # HP以外のステータスの計算式（簡略版）
        self.attack = int(self.base_stats['base_attack'] * self.level / 50) + 5
        self.defense = int(self.base_stats['base_defense'] * self.level / 50) + 5
        self.sp_attack = int(self.base_stats['base_sp_attack'] * self.level / 50) + 5
        self.sp_defense = int(self.base_stats['base_sp_defense'] * self.level / 50) + 5
        self.speed = int(self.base_stats['base_speed'] * self.level / 50) + 5

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
        print(f"{self.name} は {damage} のダメージを受けた！ 残りHP: {self.current_hp}")

    def is_fainted(self):
        return self.current_hp <= 0

    def gain_exp(self, amount):
        """経験値を獲得し、レベルアップ判定を行う。発生したメッセージをリストで返す。"""
        messages = []
        if self.is_fainted(): return messages

        self.exp += amount
        messages.append(f"{self.name} は {amount} の けいけんちを かくとく！")
        
        # 経験値が次のレベルに達しているかチェック（複数レベルアップも考慮）
        while self.exp >= self.exp_to_next_level:
            level_up_messages = self.level_up()
            messages.extend(level_up_messages)
            
        return messages

    def level_up(self):
        """レベルアップ処理を行い、メッセージをリストで返す。"""
        self.level += 1
        self.exp_to_next_level = get_exp_for_level(self.level + 1, self.growth_rate)
        
        # ステータスを再計算
        # ステータス再計算前の各ステータスを記憶
        old_max_hp = self.max_hp
        old_attack = self.attack
        old_defense = self.defense
        old_sp_attack = self.sp_attack
        old_sp_defense = self.sp_defense
        old_speed = self.speed

        # ステータスを再計算
        self._calculate_stats()

        # HPの上昇分だけ、現在のHPも回復させる
        hp_increase = self.max_hp - old_max_hp
        self.current_hp += hp_increase
        
        # メッセージを作成
        messages = [
            f"{self.name}は レベル {self.level}に あがった！",
            f"さいだいHPが {hp_increase} あがった！",
            f"こうげきが {self.attack - old_attack} あがった！",
            f"ぼうぎょが {self.defense - old_defense} あがった！",
            f"とくこうが {self.sp_attack - old_sp_attack} あがった！",
            f"とくぼうが {self.sp_defense - old_sp_defense} あがった！",
            f"すばやさが {self.speed - old_speed} あがった！"
        ]
        return messages

# モンスターを生成するための「工場」関数
# create_monster関数をレベル指定で生成できるように変更
def create_monster(monster_id, level):
    data = MONSTER_DATABASE.get(monster_id)
    if data:
        monster_moves = []
        for move_id in data["moves"]:
            move_data = MOVE_DATABASE.get(move_id)
            if move_data:
                monster_moves.append(move_data)
        
        # 種族値データだけをまとめて渡す
        base_stats = {
            "id": monster_id,
            "base_hp": data["base_hp"],
            "base_attack": data["base_attack"],
            "base_defense": data["base_defense"],
            "base_sp_attack": data["base_sp_attack"],
            "base_sp_defense": data["base_sp_defense"],
            "base_speed": data["base_speed"],
        }
        
        return Monster(
            name=data["name"],
            types=data["types"],
            level=level,
            base_stats=base_stats,
            moves=monster_moves,
            growth_rate=data["growth_rate"] 
        )
    else:
        print(f"エラー: ID '{monster_id}' のモンスターは存在しません。")
        return None