# game_manager.py
import pygame
import sys
import json
import os
from monster import create_monster
from party import Party
from inventory import Inventory

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
        self.inventory = Inventory()
        self.player_world_x = 500  # 主人公の初期位置X
        self.player_world_y = 500  # 主人公の初期位置Y
        
        # ゲーム進行データ
        self.game_flags = {}  # イベントフラグなど
        self.play_time = 0    # プレイ時間（秒）
        
        self._initialize_player_data()
        
        # シーン管理
        self.scene_stack = []
    
    def _initialize_player_data(self):
        """プレイヤーの初期データを設定"""
        self.player_party.add_monster(create_monster("bulbasaur", level=5))
        self.player_party.add_monster(create_monster("squirtle", level=5))
        self.player_party.add_monster(create_monster("pidgey", level=5))

        # ★初期アイテムを設定
        self.inventory.add_item("monster_ball", 10)
        self.inventory.add_item("potion", 5)
        self.inventory.add_item("x_attack", 2)
        self.inventory.add_item("tm_case", 1)
    
    def start_battle(self, enemy_monster_id, enemy_level=5):
        """バトルシーンを開始"""
        from scenes.battle_scene import BattleScene
        from scenes.field_scene import FieldScene
        if self.current_scene and isinstance(self.current_scene, FieldScene):
            self.player_world_x = self.current_scene.player_world_x
            self.player_world_y = self.current_scene.player_world_y
        enemy_monster = create_monster(enemy_monster_id, enemy_level)
        battle_scene = BattleScene(self.screen, self.font, self.player_party, self.inventory, enemy_monster)
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

    def _serialize_monster(self, monster):
        """モンスターオブジェクトを辞書形式にシリアライズ"""
        return {
            "id": monster.base_stats['id'],
            "name": monster.name,
            "level": monster.level,
            "current_hp": monster.current_hp,
            "max_hp": monster.max_hp,
            "exp": monster.exp,
            "exp_to_next_level": monster.exp_to_next_level,
            "status_condition": monster.status_condition,
            "toxic_counter": monster.toxic_counter,
            "sleep_counter": monster.sleep_counter,
            # 能力ランク補正は保存しない（バトル外では常に0）
            "types": monster.types.copy(),
            # 覚えている技のIDのみを保存（技データは moves_data.py から復元）
            "move_ids": [move.get('id', move['name']) for move in monster.moves]
        }
    
    def _deserialize_monster(self, monster_data):
        """辞書形式のデータからモンスターオブジェクトを復元"""
        from moves_data import MOVE_DATABASE
        
        # 基本のモンスターを生成
        monster = create_monster(monster_data["id"], monster_data["level"])
        
        # 保存されたデータで上書き
        monster.current_hp = monster_data["current_hp"]
        monster.max_hp = monster_data["max_hp"]
        monster.exp = monster_data["exp"]
        monster.exp_to_next_level = monster_data["exp_to_next_level"]
        monster.status_condition = monster_data.get("status_condition")
        monster.toxic_counter = monster_data.get("toxic_counter", 0)
        monster.sleep_counter = monster_data.get("sleep_counter", 0)
        # 能力ランクは必ず0でリセット（バトル外では常に0）
        monster.stat_stages = {
            "attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0
        }
        
        # 技を復元
        monster.moves = []
        for move_id in monster_data.get("move_ids", []):
            if move_id in MOVE_DATABASE:
                monster.moves.append(MOVE_DATABASE[move_id])
            else:
                # 技名で検索（後方互換性のため）
                for move_data in MOVE_DATABASE.values():
                    if move_data['name'] == move_id:
                        monster.moves.append(move_data)
                        break
        
        return monster

    def save_game(self):
        """現在のゲームの状態をJSONファイルに保存する。"""
        print("レポートを きろくしています...")
        
        try:
            # 現在のシーンから座標を取得
            from scenes.field_scene import FieldScene
            if self.current_scene and isinstance(self.current_scene, FieldScene):
                self.player_world_x = self.current_scene.player_world_x
                self.player_world_y = self.current_scene.player_world_y
            
            # 保存するデータをまとめる
            save_data = {
                "version": "1.0",  # セーブデータのバージョン
                "timestamp": pygame.time.get_ticks(),  # 保存時刻
                "play_time": self.play_time,
                "player_position": {
                    "x": self.player_world_x,
                    "y": self.player_world_y
                },
                "game_flags": self.game_flags.copy(),
                "player_party": []
            }
            
            # パーティのモンスターをシリアライズ
            for monster in self.player_party.members:
                save_data["player_party"].append(self._serialize_monster(monster))
            
            # バックアップファイルを作成（既存のセーブファイルがあれば）
            if os.path.exists(self.save_file_path):
                backup_path = self.save_file_path + ".backup"
                try:
                    os.rename(self.save_file_path, backup_path)
                except OSError as e:
                    print(f"バックアップ作成に失敗: {e}")
            
            # JSONファイルに書き出す
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print("レポートに しっかり かきのこした！")
            return True
            
        except Exception as e:
            print(f"セーブに失敗しました: {e}")
            # エラーが発生した場合、バックアップから復元を試行
            backup_path = self.save_file_path + ".backup"
            if os.path.exists(backup_path):
                try:
                    os.rename(backup_path, self.save_file_path)
                    print("バックアップから復元しました。")
                except OSError:
                    pass
            return False

    def load_game(self):
        """JSONファイルからゲームの状態を復元する。"""
        if not os.path.exists(self.save_file_path):
            print("レポートがありません。")
            return False

        print("レポートを よみこんでいます...")
        
        try:
            with open(self.save_file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # バージョンチェック
            version = save_data.get("version", "0.0")
            if version != "1.0":
                print(f"警告: セーブデータのバージョンが異なります ({version})")
            
            # プレイヤーの位置を復元
            player_pos = save_data.get("player_position", {"x": 500, "y": 500})
            self.player_world_x = player_pos["x"]
            self.player_world_y = player_pos["y"]
            
            # ゲーム進行データを復元
            self.play_time = save_data.get("play_time", 0)
            self.game_flags = save_data.get("game_flags", {})
            
            # 手持ちパーティを復元
            self.player_party.members.clear()
            party_data = save_data.get("player_party", [])
            
            if not party_data:
                print("警告: パーティデータが空です。")
                return False
            
            for monster_data in party_data:
                try:
                    monster = self._deserialize_monster(monster_data)
                    if monster:
                        self.player_party.add_monster(monster)
                    else:
                        print(f"警告: モンスター {monster_data.get('name', '不明')} の復元に失敗")
                except Exception as e:
                    print(f"警告: モンスターデータの復元エラー: {e}")
                    continue
            
            if not self.player_party.members:
                print("エラー: 有効なポケモンが1匹も復元できませんでした。")
                return False
            
            print("レポートを よみこみました。")
            print(f"復元されたポケモン: {len(self.player_party.members)}匹")
            return True
            
        except json.JSONDecodeError as e:
            print(f"セーブファイルが破損しています: {e}")
            return False
        except FileNotFoundError:
            print("セーブファイルが見つかりません。")
            return False
        except Exception as e:
            print(f"ロードに失敗しました: {e}")
            return False
    
    def create_backup(self):
        """手動バックアップ作成"""
        if not os.path.exists(self.save_file_path):
            print("セーブファイルが存在しません。")
            return False
        
        try:
            import shutil
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"save_data_backup_{timestamp}.json"
            shutil.copy2(self.save_file_path, backup_name)
            print(f"バックアップを作成しました: {backup_name}")
            return True
        except Exception as e:
            print(f"バックアップ作成に失敗: {e}")
            return False
    
    def handle_scene_result(self, result):
        """シーンの結果を処理"""
        if result == "battle_victory":
            print("バトル勝利！")
            self.start_field()
        elif result == "battle_defeat":
            print("バトル敗北...")
            self.start_field()  # とりあえずフィールドに戻る
        elif result == "escaped":  # 逃走時の処理を追加
            print("バトルから逃走しました")
            self.start_field()
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
        elif result == "create_backup":
            self.create_backup()
    
    def run(self):
        """メインゲームループ"""
        # 最初はタイトル画面から開始
        self.start_title()
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # デルタタイム（秒）
            
            # プレイ時間を更新
            self.play_time += dt
            
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