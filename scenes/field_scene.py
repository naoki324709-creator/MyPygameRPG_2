# scenes/field_scene.py
import pygame
import random
from scenes.base_scene import BaseScene
from ui.components import MessageBox

class FieldScene(BaseScene):
    """フィールド（マップ移動）シーンクラス"""
    
    def __init__(self, screen, font, player_party,start_x, start_y):
        super().__init__(screen, font)
        
        self.player_party = player_party
        
        # プレイヤー位置（ワールド座標）
        self.player_world_x = start_x
        self.player_world_y = start_y
        self.player_speed = 3
        
        # 画面上での固定位置
        self.player_screen_x = 400
        self.player_screen_y = 300
        
        # マップ画像の読み込み
        self.map_image = None
        self.player_image = None
        self._load_images()
        
        # カメラ座標
        self.camera_x = 0
        self.camera_y = 0
        
        # エンカウント関連
        self.encounter_rate = 1  # 1%の確率
        self.steps_since_last_encounter = 0
        
        # UI
        self.message_box = MessageBox(50, 450, 700, 100, font)
        self.show_message = False
        
        # NPCや建物の位置（例）
        self.npcs = [
            {"x": 400, "y": 300, "message": "ようこそ ポケモンの せかいへ！"},
            {"x": 600, "y": 400, "message": "やせいの ポケモンに きをつけて！"},
        ]
        
        self.buildings = [
            {"rect": pygame.Rect(300, 200, 100, 80), "type": "pokecenter", "message": "ポケモンセンター"},
            {"rect": pygame.Rect(500, 250, 120, 100), "type": "shop", "message": "フレンドリィショップ"},
        ]
        
    def _load_images(self):
        """画像を読み込み"""
        try:
            # マップ画像（既存のものがあれば使用）
            #self.map_image = pygame.image.load('map_s.png').convert()
            # 画像がない場合は緑の背景を生成
            self.map_image = pygame.Surface((1200, 1000))
            self.map_image.fill((34, 139, 34))  # 森の緑
            # 簡単な道を描画
            pygame.draw.rect(self.map_image, (139, 69, 19), (450, 0, 100, 1000))  # 縦道
            pygame.draw.rect(self.map_image, (139, 69, 19), (0, 450, 1200, 100))  # 横道
        except pygame.error:
            # 画像がない場合は緑の背景を生成
            self.map_image = pygame.Surface((1200, 1000))
            self.map_image.fill((34, 139, 34))  # 森の緑
            # 簡単な道を描画
            pygame.draw.rect(self.map_image, (139, 69, 19), (450, 0, 100, 1000))  # 縦道
            pygame.draw.rect(self.map_image, (139, 69, 19), (0, 450, 1200, 100))  # 横道
        
        try:
            # プレイヤー画像
            #self.player_image = pygame.image.load('player_s.png').convert_alpha()
            self.player_image = pygame.Surface((32, 32))
            self.player_image.fill((0, 0, 255))
        except pygame.error:
            # 画像がない場合は青い四角を生成
            self.player_image = pygame.Surface((32, 32))
            self.player_image.fill((0, 0, 255))
    
    def _update_camera(self):
        """カメラ位置を更新"""
        # プレイヤーを画面中央に保つ
        self.camera_x = self.player_world_x - self.player_screen_x
        self.camera_y = self.player_world_y - self.player_screen_y
        
        # マップの境界を超えないように制限
        map_width, map_height = self.map_image.get_size()
        screen_width, screen_height = self.screen.get_size()
        
        self.camera_x = max(0, min(self.camera_x, map_width - screen_width))
        self.camera_y = max(0, min(self.camera_y, map_height - screen_height))
    
    def _check_collision(self, new_x, new_y):
        """衝突判定"""
        player_rect = pygame.Rect(new_x - 16, new_y - 16, 32, 32)
        
        # 建物との衝突
        for building in self.buildings:
            if player_rect.colliderect(building["rect"]):
                return True
        
        # マップ境界
        map_width, map_height = self.map_image.get_size()
        if new_x < 16 or new_x > map_width - 16 or new_y < 16 or new_y > map_height - 16:
            return True
        
        return False
    
    def _check_encounters(self):
        """野生ポケモンとのエンカウント判定"""
        self.steps_since_last_encounter += 1
        
        # 草むらエリアかどうかの簡単な判定（緑の部分）
        map_color = self.map_image.get_at((int(self.player_world_x), int(self.player_world_y)))
        is_grass = map_color[1] > 100  # 緑っぽい色
        
        if is_grass and random.random() < self.encounter_rate:
            self.steps_since_last_encounter = 0
            # ランダムな野生ポケモンと遭遇
            wild_pokemon = ["charmander", "squirtle", "bulbasaur", "pidgey"]
            enemy_id = random.choice(wild_pokemon)
            enemy_level = random.randint(3, 7)
            
            return f"wild_battle|{enemy_id}|{enemy_level}"
        
        return None
    
    def _check_npc_interaction(self):
        """NPCとの相互作用をチェック"""
        player_rect = pygame.Rect(self.player_world_x - 20, self.player_world_y - 20, 40, 40)
        
        for npc in self.npcs:
            npc_rect = pygame.Rect(npc["x"] - 20, npc["y"] - 20, 40, 40)
            if player_rect.colliderect(npc_rect):
                self.message_box.clear()
                self.message_box.add_message(npc["message"])
                self.show_message = True
                return True
        
        return False
    
    def _check_building_interaction(self):
        """建物との相互作用をチェック"""
        player_rect = pygame.Rect(self.player_world_x - 16, self.player_world_y - 16, 32, 32)
        
        for building in self.buildings:
            # 建物の入り口付近
            entrance_rect = pygame.Rect(
                building["rect"].x - 10, 
                building["rect"].bottom - 5, 
                building["rect"].width + 20, 
                15
            )
            
            if player_rect.colliderect(entrance_rect):
                if building["type"] == "pokecenter":
                    # ポケモンセンターの処理
                    for pokemon in self.player_party.members:
                        pokemon.current_hp = pokemon.max_hp
                        pokemon.status_condition = None
                    
                    self.message_box.clear()
                    self.message_box.add_message("ポケモンが げんきに なりました！")
                    self.show_message = True
                elif building["type"] == "shop":
                    self.message_box.clear()
                    self.message_box.add_message("いらっしゃいませ！（まだ未実装）")
                    self.show_message = True
                
                return True
        
        return False
    
    def handle_event(self, event):
        if self.show_message:
            # メッセージ表示中
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                    self.show_message = False
                    self.message_box.clear()
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "to_menu"
            elif event.key == pygame.K_z:
                # アクションキー（NPCや建物との相互作用）
                self._check_npc_interaction()
                self._check_building_interaction()
            elif event.key == pygame.K_b:
                # テスト用：強制バトル
                return "to_battle"
        
        return None
    
    def update(self, dt):
        """更新処理"""
        if self.show_message:
            return
        
        # キー入力による移動
        keys = pygame.key.get_pressed()
        new_x, new_y = self.player_world_x, self.player_world_y
        moved = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= self.player_speed
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += self.player_speed
            moved = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= self.player_speed
            moved = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += self.player_speed
            moved = True
        
        # 衝突判定
        if moved and not self._check_collision(new_x, new_y):
            self.player_world_x = new_x
            self.player_world_y = new_y
            
            # エンカウント判定
            encounter_result = self._check_encounters()
            if encounter_result:
                # _check_encountersが返した命令文を、そのまま司令塔に渡す
                self.transition_to(encounter_result)
        
        # カメラ更新
        self._update_camera()
    
    def draw(self):
        """描画処理"""
        # マップを描画（カメラの位置を考慮）
        self.screen.blit(self.map_image, (-self.camera_x, -self.camera_y))
        
        # NPCを描画
        for npc in self.npcs:
            npc_screen_x = npc["x"] - self.camera_x
            npc_screen_y = npc["y"] - self.camera_y
            
            # 画面内にいる場合のみ描画
            if -50 < npc_screen_x < 850 and -50 < npc_screen_y < 650:
                pygame.draw.circle(self.screen, (255, 255, 0), (int(npc_screen_x), int(npc_screen_y)), 15)
                self.draw_text("NPC", npc_screen_x - 15, npc_screen_y - 30, self.BLACK)
        
        # 建物を描画
        for building in self.buildings:
            building_screen_rect = pygame.Rect(
                building["rect"].x - self.camera_x,
                building["rect"].y - self.camera_y,
                building["rect"].width,
                building["rect"].height
            )
            
            # 建物の色を種類によって変える
            if building["type"] == "pokecenter":
                color = (255, 100, 100)  # 赤
            else:
                color = (100, 100, 255)  # 青
                
            pygame.draw.rect(self.screen, color, building_screen_rect)
            self.draw_text(building["message"], building_screen_rect.x, building_screen_rect.y - 25, self.BLACK)
        
        # プレイヤーを描画（画面上の固定位置）
        player_screen_rect = self.player_image.get_rect()
        player_screen_rect.center = (self.player_screen_x, self.player_screen_y)
        self.screen.blit(self.player_image, player_screen_rect)
        
        # UI情報
        self.draw_text("フィールド", 10, 10, self.WHITE)
        self.draw_text(f"座標: ({int(self.player_world_x)}, {int(self.player_world_y)})", 10, 40, self.WHITE)
        self.draw_text("操作: WASD/矢印キー:移動 Z:アクション ESC:メニュー B:バトル(テスト)", 10, 570, self.WHITE)
        
        # メッセージボックス
        if self.show_message:
            self.message_box.draw(self.screen)