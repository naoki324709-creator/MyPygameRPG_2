# party.py
from monster import Monster

class Party:
    def __init__(self):
        self.members = [] # 手持ちモンスターのリスト

    def add_monster(self, monster):
        # 追加しようとしているのがNoneでないかチェック
        if monster is None:
            print("エラー：存在しないモンスターは手持ちに追加できません。")
            return # 何もせずに関数を終了

        if len(self.members) < 6:
            self.members.append(monster)
        else:
            print("手持ちがいっぱいです！")

    def get_active_monster(self):
        # 戦闘に出せる、ひんしでない最初のモンスターを返す
        for monster in self.members:
            if not monster.is_fainted():
                return monster
        return None # 全員ひんしの場合
    
    def has_living_monsters(self):
        """まだ戦える（ひんしでない）モンスターが手持ちにいるかを返す"""
        return self.get_active_monster() is not None

    def get_living_monsters(self):
        """ひんしでないモンスターのリストを返す"""
        return [m for m in self.members if not m.is_fainted()]