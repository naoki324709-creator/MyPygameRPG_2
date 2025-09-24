# monster.py

from monsters_data import MONSTER_DATABASE
from moves_data import MOVE_DATABASE
from exp_data import get_exp_for_level

class Monster:
    def __init__(self, name, types, level, base_stats, moves, growth_rate, learnset):
        self.name = name
        self.types = types
        self.level = level
        self.base_stats = base_stats
        self.moves = moves
        self.growth_rate = growth_rate
        self.learnset = learnset
        self.status_condition = None
        self.toxic_counter = 0
        self.sleep_counter = 0
        self.stat_stages = {
            "attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0
        }
        # 経験値の初期化を修正
        # 現在のレベルの最低必要経験値から開始
        if level <= 1:
            self.exp = 0
        else:
            # 前のレベルの経験値から開始（レベルアップ直後の状態）
            self.exp = get_exp_for_level(level, self.growth_rate)
        
        # 次のレベルに必要な経験値を設定
        self.exp_to_next_level = get_exp_for_level(level + 1, self.growth_rate)

        self._calculate_stats()
        self.current_hp = self.max_hp

    def _calculate_stats(self):
        self.max_hp = int(self.base_stats['base_hp'] * self.level / 50) + self.level + 10
        self.attack = int(self.base_stats['base_attack'] * self.level / 50) + 5
        self.defense = int(self.base_stats['base_defense'] * self.level / 50) + 5
        self.sp_attack = int(self.base_stats['base_sp_attack'] * self.level / 50) + 5
        self.sp_defense = int(self.base_stats['base_sp_defense'] * self.level / 50) + 5
        self.speed = int(self.base_stats['base_speed'] * self.level / 50) + 5

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def is_fainted(self):
        return self.current_hp <= 0

    def gain_exp(self, amount):
        """経験値を獲得し、レベルアップ判定を行う。本家仕様：技習得時にレベルアップ一時停止"""
        messages = []
        new_move = None
        if self.is_fainted(): 
            return messages, new_move

        self.exp += amount
        messages.append(f"{self.name} は {amount} の けいけんちを かくとく！")
        
        # デバッグ用の情報出力
        print(f"[DEBUG] {self.name} - 成長タイプ: {self.growth_rate}")
        print(f"[DEBUG] 経験値獲得後: {self.exp} / 次レベル必要: {self.exp_to_next_level}")
        
        # 経験値が次のレベルに達しているかチェック
        while self.exp >= self.exp_to_next_level:
            level_up_messages, learned_move = self.level_up()
            messages.extend(level_up_messages)
            
            # 技を覚える処理が発生したら、レベルアップを一時停止
            if learned_move:
                new_move = learned_move  # 技オブジェクト（辞書）を返す
                break  # ここでループを中断し、技習得処理へ
            
        return messages, new_move
    
    def continue_level_up(self):
        """技習得処理完了後に残りの経験値でレベルアップを継続する"""
        messages = []
        new_move = None
        
        # まだレベルアップできる経験値があるかチェック
        while self.exp >= self.exp_to_next_level:
            level_up_messages, learned_move = self.level_up()
            messages.extend(level_up_messages)
            
            # また技を覚える場合は再度停止
            if learned_move:
                new_move = learned_move  # 技オブジェクト（辞書）を返す
                break
                
        return messages, new_move

    def level_up(self):
        """レベルアップ処理を行い、メッセージと覚えるべき技（単体）を返す"""
        old_level = self.level
        self.level += 1
        
        # デバッグ用の情報出力
        print(f"[DEBUG] {self.name} レベル {old_level} -> {self.level}")
        # ここに新しいデバッグコードを追加 ↓
        # print(f"[DEBUG] 直接計算テスト:")
        # from exp_data import get_exp_for_level
        # print(f"fast レベル{self.level + 1}: {get_exp_for_level(self.level + 1, 'fast')}")
        # print(f"medium_slow レベル{self.level + 1}: {get_exp_for_level(self.level + 1, 'medium_slow')}")
        # print(f"slow レベル{self.level + 1}: {get_exp_for_level(self.level + 1, 'slow')}")
        # print(f"実際の計算 get_exp_for_level({self.level + 1}, '{self.growth_rate}'): {get_exp_for_level(self.level + 1, self.growth_rate)}")
        # ここまで追加 ↑
        self.exp_to_next_level = get_exp_for_level(self.level + 1, self.growth_rate)
        
        print(f"[DEBUG] 次のレベル必要経験値: {self.exp_to_next_level} (成長タイプ: {self.growth_rate})")
        
        old_max_hp = self.max_hp
        old_attack = self.attack
        old_defense = self.defense
        old_sp_attack = self.sp_attack
        old_sp_defense = self.sp_defense
        old_speed = self.speed

        self._calculate_stats()

        hp_increase = self.max_hp - old_max_hp
        self.current_hp += hp_increase
        
        messages = [
            f"{self.name}は レベル {self.level}に あがった！",
            f"さいだいHPが {hp_increase} あがった！",
            f"こうげきが {self.attack - old_attack} あがった！",
            f"ぼうぎょが {self.defense - old_defense} あがった！",
            f"とくこうが {self.sp_attack - old_sp_attack} あがった！",
            f"とくぼうが {self.sp_defense - old_sp_defense} あがった！",
            f"すばやさが {self.speed - old_speed} あがった！"
        ]

        # 技習得チェック
        new_move_to_learn = None
        new_move_id = self.learnset.get(self.level)
        if new_move_id:
            move_data = MOVE_DATABASE.get(new_move_id)
            if move_data and move_data not in self.moves:
                if len(self.moves) < 4:
                    # 技スロットに空きがあればそのまま覚える
                    self.moves.append(move_data)
                    messages.append(f"{self.name}は {move_data['name']}を おぼえた！")
                else:
                    # 技スロットが満杯なら技習得選択画面へ
                    new_move_to_learn = move_data
        
        return messages, new_move_to_learn

def create_monster(monster_id, level):
    data = MONSTER_DATABASE.get(monster_id)
    if data:
        monster_moves = []
        for move_id in data["moves"]:
            move_data = MOVE_DATABASE.get(move_id)
            if move_data:
                monster_moves.append(move_data)
        
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
            growth_rate=data["growth_rate"],
            learnset=data.get("learnset", {}) 
        )
    else:
        print(f"エラー: ID '{monster_id}' のモンスターは存在しません。")
        return None