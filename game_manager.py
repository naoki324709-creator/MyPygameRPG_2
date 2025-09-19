# game_manager.py
import pygame
import sys
import json
import os
from monster import create_monster
from party import Party

class GameManager:
    """ゲーム全体を管理するクラス"""
    
    def __init__(self):
        # Pygame初期化
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("ポケットモンスターイオナズン（仮）")
        
        # フォント読み込み
        try:
            self.font = pygame.font.Font("pkmn_w.ttf", 28)
        except:
            print("[WARNING] pkmn_w.ttf が見つからないため、デフォルトフォントを使用します")
            self.font = pygame.font.Font(None, 28)
        
        self.clock = pygame.time.Clock()

        self.save_file_path = "save_data.json" # セーブファイルの名前を定義
        
        # ゲーム状態
        self.running = True
        self.current_scene = None
        
        # プレイヤーデータ
        self.player_party = Party()
        self.player_world_x = 500  # 主人公の初期位置X
        self.player_world_y = 500  # 主人公の初期位置Y
        self._initialize_player_data()
        
        # シーン管理
        self.scene_stack = []
    
    def _initialize_player_data(self):
        """プレイヤーの初期データを設定"""
        self.player_party.add_monster(create_monster("bulbasaur", level=5))
        self.player_party.add_monster(create_monster("squirtle", level=4))
        self.player_party.add_monster(create_monster("pidgey", level=3))
    
    def start_battle(self, enemy_monster_id, enemy_level=5):
        """バトルシーンを開始"""
        from scenes.battle_scene import BattleScene
        from scenes.field_scene import FieldScene
        if self.current_scene and isinstance(self.current_scene, FieldScene):
            self.player_world_x = self.current_scene.player_world_x
            self.player_world_y = self.current_scene.player_world_y
        enemy_monster = create_monster(enemy_monster_id, enemy_level)
        battle_scene = BattleScene(self.screen, self.font, self.player_party, enemy_monster)
        self.change_scene(battle_scene)
    
    def start_field(self):
        """フィールドシーンを開始"""
        from scenes.field_scene import FieldScene
        field_scene = FieldScene(self.screen, self.font, self.player_party,self.player_world_x, self.player_world_y)
        self.change_scene(field_scene)
    
    def start_menu(self):
        """メニューシーンを開始"""
        from scenes.menu_scene import MenuScene
        from scenes.field_scene import FieldScene
        if self.current_scene and isinstance(self.current_scene, FieldScene):
            self.player_world_x = self.current_scene.player_world_x
            self.player_world_y = self.current_scene.player_world_y
        menu_scene = MenuScene(self.screen, self.font, self.player_party)
        self.push_scene(menu_scene)
    
    def start_title(self):
        """タイトルシーンを開始"""
        from scenes.title_scene import TitleScene
        title_scene = TitleScene(self.screen, self.font)
        self.change_scene(title_scene)
    
    def change_scene(self, new_scene):
        """シーンを切り替え（現在のシーンを破棄）"""
        self.current_scene = new_scene
        self.scene_stack.clear()
    
    def push_scene(self, new_scene):
        """シーンをスタックにプッシュ（現在のシーンを保持）"""
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
        self.current_scene = new_scene
    
    def pop_scene(self):
        """シーンをポップ（前のシーンに戻る）"""
        if self.scene_stack:
            self.current_scene = self.scene_stack.pop()
        else:
            self.running = False

    def save_game(self):
        """現在のゲームの状態をJSONファイルに保存する。"""
        print("レポートを きろくしています...")
        
        # 1. 保存するデータをまとめる
        save_data = {
            "player_position": {
                "x": self.player_world_x,
                "y": self.player_world_y
            },
            "player_party": []
        }
        
        for monster in self.player_party.members:
            monster_data = {
                "id": monster.base_stats['id'], # ← 将来のためにIDも保存
                "level": monster.level,
                "current_hp": monster.current_hp,
                "status_condition": monster.status_condition,
                # (経験値などもここに追加)
            }
            save_data["player_party"].append(monster_data)
            
        # 2. JSONファイルに書き出す
        try:
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            print("レポートに しっかり かきのこした！")
        except Exception as e:
            print(f"セーブに失敗しました: {e}")

    def load_game(self):
        """JSONファイルからゲームの状態を復元する。"""
        if not os.path.exists(self.save_file_path):
            print("レポートがありません。")
            return False

        print("レポートを よみこんでいます...")
        try:
            with open(self.save_file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # 1. プレイヤーの位置を復元
            self.player_world_x = save_data["player_position"]["x"]
            self.player_world_y = save_data["player_position"]["y"]
            
            # 2. 手持ちパーティを復元
            self.player_party.members.clear()
            for monster_data in save_data["player_party"]:
                # create_monsterで基本のモンスターを生成
                monster = create_monster(monster_data["id"], monster_data["level"])
                # 保存されていたHPや状態異常を上書き
                monster.current_hp = monster_data["current_hp"]
                monster.status_condition = monster_data["status_condition"]
                self.player_party.add_monster(monster)
            
            print("レポートを よみこみました。")
            return True
        except Exception as e:
            print(f"ロードに失敗しました: {e}")
            return False
    
    def handle_scene_result(self, result):
        """シーンの結果を処理"""
        if result == "battle_victory":
            print("バトル勝利！")
            self.start_field()
        elif result == "battle_defeat":
            print("バトル敗北...")
            self.start_field()  # とりあえずフィールドに戻る
        elif result == "to_field":
            self.start_field()
        elif result == "to_battle":
            self.start_battle("charmander", 5)
        elif result == "to_menu":
            self.start_menu()
        elif result == "to_title":
            self.start_title()
        elif result == "back":
            self.pop_scene()
        elif result == "quit":
            self.running = False
        elif result.startswith("wild_battle"):
            # "wild_battle|enemy_id|enemy_level" の形式
            parts = result.split("|")
            if len(parts) == 3:
                enemy_id = parts[1]
                enemy_level = int(parts[2])
                self.start_battle(enemy_id, enemy_level)
        elif result == "save_game":
            self.save_game()
        elif result == "load_game":
            if self.load_game():
                self.start_field()
            else:
                self.start_title() # ロード失敗時はタイトルへ
    
    def run(self):
        """メインゲームループ"""
        # 最初はタイトル画面から開始
        self.start_title()
        #self.start_battle("charmander", enemy_level=5)
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # デルタタイム（秒）
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F4 and pygame.key.get_pressed()[pygame.K_LALT]:
                        self.running = False
                
                # 現在のシーンにイベントを渡す
                if self.current_scene:
                    result = self.current_scene.handle_event(event)
                    if result:
                        self.handle_scene_result(result)
            
            # 更新処理
            if self.current_scene:
                self.current_scene.update(dt)
                
                # シーンの終了チェック
                if self.current_scene.is_finished:
                    next_scene_type, kwargs = self.current_scene.get_next_scene()
                    if next_scene_type:
                        self.handle_scene_result(next_scene_type)
                    elif not self.scene_stack:
                        self.running = False
                    else:
                        self.pop_scene()
            
            # 描画処理
            self.screen.fill((0, 0, 0))  # 黒背景でクリア
            
            if self.current_scene:
                self.current_scene.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()