# scenes/battle_scene.py - 完全版
import pygame
from scenes.base_scene import BaseScene
from ui.components import Button, HPBar, ImageMessageBox, PokemonInfoPanel, NumberDisplay
from battle import Battle

# スプライトシステムの読み込み
try:
    from sprite_animation import PokemonSprite
    SPRITES_AVAILABLE = True
except ImportError:
    SPRITES_AVAILABLE = False
    print("Warning: sprite_animation.py not found, using simple rectangles")

class SimplePokemonSprite:
    """スプライトが利用できない場合の代替クラス"""
    def __init__(self, pokemon_id, facing_direction="front"):
        self.pokemon_id = pokemon_id
        self.facing_direction = facing_direction
        self.color = (0, 255, 0) if "bulbasaur" in pokemon_id else (255, 0, 0)
        if facing_direction == "back":
            self.color = tuple(max(0, c - 50) for c in self.color)  # 背面は少し暗く
    
    def update(self, dt):
        pass
    
    def draw(self, screen, x, y, scale=1.0):
        size = int(64 * scale)
        rect = pygame.Rect(x - size//2, y - size//2, size, size)
        pygame.draw.rect(screen, self.color, rect)
        # 背面の場合は「B」、正面の場合は「F」を描画
        font = pygame.font.Font(None, int(24 * scale))
        text = font.render("B" if self.facing_direction == "back" else "F", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

class BattleScene(BaseScene):
    """バトルシーンクラス"""
    
    def __init__(self, screen, font, player_party, inventory, enemy_monster):
        super().__init__(screen, font)
        
        self.player_party = player_party
        self.inventory = inventory
        self.enemy_monster = enemy_monster
        self.battle = Battle(player_party.get_active_monster(), enemy_monster)
        
        # 画像ベースのメッセージボックスを使用
        self.message_box = ImageMessageBox(0, 470, 800, 130, font, "ui/textbox.png")
        
        # アクション選択時専用の画像メッセージボックス
        self.action_message_box = ImageMessageBox(0, 470, 480, 130, font, "ui/textbox.png")
        
        # self.player_info = PokemonInfoPanel(450, 300, 300, 120, font)
        # self.enemy_info = PokemonInfoPanel(50, 50, 300, 120, font)

        # ポケモン名の表示位置をここで定義
        PLAYER_NAME_POS = (495, 335) # (X座標, Y座標)
        PLAYER_NAME_COLOR = (60, 60, 60)
        ENEMY_NAME_POS = (10, 65)   # (X座標, Y座標)
        ENEMY_NAME_COLOR = (60, 60, 60)

        # 情報パネルの初期化
        self.player_info = PokemonInfoPanel(
            position=(442, 180), size=(400, 400), font=font,
            background_image_path="ui/assets/panel_player.png",
            name_pos=PLAYER_NAME_POS,
            name_color=PLAYER_NAME_COLOR
        )
        self.enemy_info = PokemonInfoPanel(
            position=(-43, -100), size=(400, 400), font=font,
            background_image_path="ui/assets/panel_enemy.png",
            name_pos=ENEMY_NAME_POS,
            name_color=ENEMY_NAME_COLOR
        )
        # # パネルのサイズと位置を定義（調整しやすいように定数化）
        # PLAYER_PANEL_WIDTH = 400
        # PLAYER_PANEL_HEIGHT = 400  
        # PLAYER_PANEL_POS = (442, 180)#左右、上下

        # ENEMY_PANEL_WIDTH = 400
        # ENEMY_PANEL_HEIGHT = 400 
        # ENEMY_PANEL_POS = (-43, -100)

        # # プレイヤーの情報パネル画像を読み込み
        # self.player_panel_img = pygame.image.load("ui/assets/panel_player.png").convert_alpha()
        # self.player_panel_img = pygame.transform.scale(self.player_panel_img, (PLAYER_PANEL_WIDTH, PLAYER_PANEL_HEIGHT))
        # self.player_panel_rect = self.player_panel_img.get_rect(topleft=PLAYER_PANEL_POS)
        
        # # 敵の情報パネル画像を読み込み
        # self.enemy_panel_img = pygame.image.load("ui/assets/panel_enemy.png").convert_alpha()
        # self.enemy_panel_img = pygame.transform.scale(self.enemy_panel_img, (ENEMY_PANEL_WIDTH, ENEMY_PANEL_HEIGHT))
        # self.enemy_panel_rect = self.enemy_panel_img.get_rect(topleft=ENEMY_PANEL_POS)

        # HPバーのパラメータを定義
        HP_CHANGE_SPEED = 12  # 1秒間に120HP変化する

        PLAYER_HP_BAR_WIDTH = 143.5
        PLAYER_HP_BAR_HEIGHT = 400

        ENEMY_HP_BAR_WIDTH = 143.5
        ENEMY_HP_BAR_HEIGHT = 410

        # HPバーの初期化
        self.player_hp_bar = HPBar(
            x=631, y=197, width=PLAYER_HP_BAR_WIDTH, height=PLAYER_HP_BAR_HEIGHT,
            change_speed=HP_CHANGE_SPEED
        )
        self.enemy_hp_bar = HPBar(
            x=139, y=-76, width=ENEMY_HP_BAR_WIDTH, height=ENEMY_HP_BAR_HEIGHT,
            change_speed=HP_CHANGE_SPEED
        )

        # レベル数字のパラメータを定義
        LEVEL_DIGIT_WIDTH = 400
        LEVEL_DIGIT_HEIGHT = 400
        LEVEL_DIGIT_SPACING = -378

        # プレイヤーのレベル表示を初期化
        self.player_level_display = NumberDisplay(
            x=534, y=169,
            digit_width=LEVEL_DIGIT_WIDTH,
            digit_height=LEVEL_DIGIT_HEIGHT,
            spacing=LEVEL_DIGIT_SPACING
        )

        # 敵のレベル表示を初期化
        self.enemy_level_display = NumberDisplay(
            x=40, y=-100,
            digit_width=LEVEL_DIGIT_WIDTH,
            digit_height=LEVEL_DIGIT_HEIGHT,
            spacing=LEVEL_DIGIT_SPACING
        )

        # 初期ポケモンをHPバーに設定
        self.player_hp_bar.set_initial_pokemon(self.battle.player_monster)
        self.enemy_hp_bar.set_initial_pokemon(self.battle.enemy_monster)
        
        self.action_buttons = []
        self.move_buttons = []
        self.party_buttons = []
        self.learn_move_buttons = []
        self.item_buttons = []
        self.pocket_buttons = []
        
        self.selected_action_index = 0
        self.selected_move_index = 0
        self.selected_party_index = 0
        self.selected_learn_move_index = 0
        self.selected_item_index = 0
        self.selected_pocket_index = 0
        
        self.battle_state = "intro"
        self.battle_result = None
        
        # 技習得関連
        self.monster_learning = None
        self.new_move = None
        self.pending_new_move = None

        # スプライト初期化
        self._load_pokemon_sprites()

        self.message_box.add_message(f"あ！ やせいの {enemy_monster.name}が とびだしてきた！")

        try:
            panel_image = pygame.image.load("ui/action_panel.png").convert_alpha()
            # パネルのサイズに合わせて画像をリサイズ
            self.action_panel_image = pygame.transform.scale(panel_image, (360, 130))
        except pygame.error:
            print("[WARNING] アクションパネルの画像 'ui/action_panel.png' が見つかりません。")
            self.action_panel_image = None # 画像がない場合はNoneに設定
        
        try:
            # 新しい一枚絵のパネル画像を読み込む
            panel_image = pygame.image.load("ui/move_panel.png").convert_alpha()
            # パネルのサイズを画面下部に合わせて調整
            self.move_panel_image = pygame.transform.scale(panel_image, (800, 130))
        except pygame.error:
            print("[WARNING] 技選択パネルの画像 'ui/move_panel.png' が見つかりません。")
            self.move_panel_image = None
        
         # ドット絵風の縦長カーソル画像を作成
        self.cursor_image = pygame.Surface((30, 30), pygame.SRCALPHA) # カーソルの画像サイズを定義
        # 小さな四角形を組み合わせてドット絵風の「▶」を描画
        pygame.draw.rect(self.cursor_image, self.BLACK, (0, 0, 6, 22))  # 左辺のrect。高さを22にして長くする
        pygame.draw.rect(self.cursor_image, self.BLACK, (6, 4, 6, 14))  # 中央のrect
        pygame.draw.rect(self.cursor_image, self.BLACK, (12, 8, 6, 6))  # 右端（先端）のrect
        
        self._setup_action_buttons()
        
        # アクション選択時のメッセージを準備
        self._setup_action_message()
    
    def _get_japanese_type_name(self, english_type):
        type_map = {
            "normal": "ノーマル", "fire": "ほのお", "water": "みず", "grass": "くさ",
            "electric": "でんき", "ice": "こおり", "fighting": "かくとう", "poison": "どく",
            "ground": "じめん", "flying": "ひこう", "psychic": "エスパー", "bug": "むし",
            "rock": "いわ", "ghost": "ゴースト", "dragon": "ドラゴン", "steel": "はがね",
            "dark": "あく", "fairy": "フェアリー"
        }
        return type_map.get(english_type, english_type)

    def _load_pokemon_sprites(self):
        """ポケモンスプライトを読み込み"""
        player_id = self.battle.player_monster.base_stats['id']
        enemy_id = self.enemy_monster.base_stats['id']
        
        if SPRITES_AVAILABLE:
            # sprite_animation.pyが正面・背面対応している場合
            try:
                self.player_sprite = PokemonSprite(player_id, "back")
                self.enemy_sprite = PokemonSprite(enemy_id, "front")
            except TypeError:
                # 古いsprite_animation.pyの場合（facing_direction引数なし）
                self.player_sprite = PokemonSprite(player_id)
                self.enemy_sprite = PokemonSprite(enemy_id)
        else:
            # 代替スプライト
            self.player_sprite = SimplePokemonSprite(player_id, "back")
            self.enemy_sprite = SimplePokemonSprite(enemy_id, "front")

    def _setup_action_message(self):
        """アクション選択時のメッセージを設定"""
        action_text = f"{self.battle.player_monster.name} は どうする？"
        self.action_message_box.add_message(action_text)
    
    def _update_action_message(self):
        """アクション選択時のメッセージを更新（ポケモンが変わった時用）"""
        # 既存のメッセージをクリア
        self.action_message_box.messages.clear()
        self.action_message_box.current_message = ""
        self.action_message_box.char_index = 0
        self.action_message_box.is_finished = True
        self.action_message_box.waiting_for_input = False
        self.action_message_box.is_typing = False
        
        # 新しいメッセージを設定
        action_text = f"{self.battle.player_monster.name} は どうする？"
        self.action_message_box.add_message(action_text)

    def _setup_action_buttons(self):
        # 4つのButtonオブジェクトを作成する代わりに、アクションのテキストリストを定義
        self.action_texts = ["たたかう", "バッグ", "ポケモン", "にげる"]
        # ボタンの選択状態更新メソッドは描画時に直接行うため、ここでは不要

    def _update_action_selection(self):
        for i, button in enumerate(self.action_buttons):
            button.is_selected = (i == self.selected_action_index)
    
    def _setup_pocket_buttons(self):
        """バッグのポケット選択ボタンを作成する"""
        self.pocket_buttons.clear()
        battle_pockets = ["かいふく", "ボール", "せんとう"]
        for i, pocket_name in enumerate(battle_pockets):
            button = Button(600, 50 + i * 60, 150, 50, pocket_name, self.font)
            button.pocket_name = pocket_name
            self.pocket_buttons.append(button)
        self.selected_pocket_index = 0
        self._update_pocket_selection()

    def _update_pocket_selection(self):
        """ポケットボタンの選択状態を更新"""
        for i, button in enumerate(self.pocket_buttons):
            button.is_selected = (i == self.selected_pocket_index)
    
    def _setup_party_buttons(self):
        self.party_buttons.clear()
        living_monsters = self.player_party.get_living_monsters()
        button_count = 0
        for monster in living_monsters:
            if monster != self.battle.player_monster:
                y = 100 + button_count * 70
                button = Button(100, y, 400, 60, f"{monster.name} (HP: {monster.current_hp}/{monster.max_hp})", self.font)
                button.monster = monster
                self.party_buttons.append(button)
                button_count += 1
        self.selected_party_index = 0
        self._update_party_selection()
    
    def _setup_learn_move_buttons(self):
        self.learn_move_buttons.clear()
        if not self.monster_learning or not self.new_move: 
            return

        # 現在の技4つ
        for i, move in enumerate(self.monster_learning.moves):
            button = Button(50, 100 + i * 60, 300, 50, move['name'], self.font)
            self.learn_move_buttons.append(button)
        
        # 新しい技
        new_button = Button(450, 100, 300, 50, self.new_move['name'], self.font)
        new_button.bg_color = (200, 255, 200)
        self.learn_move_buttons.append(new_button)

        # 覚えない選択肢
        cancel_button = Button(450, 310, 300, 50, "おぼえない", self.font)
        self.learn_move_buttons.append(cancel_button)

        self.selected_learn_move_index = 0
        self._update_learn_move_selection()
    
    def _setup_item_buttons(self, pocket_name):
        """指定されたポケットの所持アイテムからボタンを作成する"""
        self.item_buttons.clear()
        
        items_in_pocket = self.inventory.get_items_by_battle_pocket(pocket_name)
        
        y_offset = 50
        for item_id, item_info in items_in_pocket.items():
            text = f"{item_info['data']['name']} x{item_info['count']}"
            button = Button(50, y_offset, 300, 50, text, self.font)
            button.item_id = item_id
            self.item_buttons.append(button)
            y_offset += 60
            
        self.selected_item_index = 0
        self._update_item_selection()
    
    def _update_item_selection(self):
        """アイテムボタンの選択状態を更新"""
        for i, button in enumerate(self.item_buttons):
            button.is_selected = (i == self.selected_item_index)
    
    def _update_party_selection(self):
        for i, button in enumerate(self.party_buttons):
            button.is_selected = (i == self.selected_party_index)

    def _update_learn_move_selection(self):
        for i, button in enumerate(self.learn_move_buttons):
            button.is_selected = (i == self.selected_learn_move_index)
    
    def _reset_all_stat_stages(self):
        """バトル終了時に全ポケモンの能力ランクをリセットする"""
        for pokemon in self.player_party.members:
            for stat in pokemon.stat_stages:
                pokemon.stat_stages[stat] = 0
        
        if self.enemy_monster:
            for stat in self.enemy_monster.stat_stages:
                self.enemy_monster.stat_stages[stat] = 0
    
    def _execute_turn(self):
        if not self.move_buttons or self.selected_move_index >= len(self.move_buttons): 
            return
        selected_move = self.move_buttons[self.selected_move_index].move_data
        if selected_move.get('current_pp', 0) <= 0:
            self.message_box.add_message("PPがなくて わざが だせない！")
            self.battle_state = "message_display" # メッセージ表示状態へ
            return # ターン処理を中断

        # PPを1消費する
        selected_move['current_pp'] -= 1
        turn_messages = self.battle.execute_turn(selected_move)
        for msg in turn_messages:
            self.message_box.add_message(msg)
        self.battle_state = "message_display"
    
    def _switch_pokemon(self, monster):
        switch_message = self.battle.switch_player_monster(monster)
        self.message_box.add_message(switch_message)
        
        # アクションメッセージも更新
        self._update_action_message()
        
        # ポケモン交代時にスプライトも更新
        player_id = monster.base_stats['id']
        if SPRITES_AVAILABLE:
            try:
                self.player_sprite = PokemonSprite(player_id, "back")
            except TypeError:
                self.player_sprite = PokemonSprite(player_id)
        else:
            self.player_sprite = SimplePokemonSprite(player_id, "back")
        
        self.player_hp_bar.set_hp_instant(monster)
        
        self.battle_state = "message_display"
    
    def handle_event(self, event):
        if self.battle_state in ["intro", "message_display"]:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                self.message_box.handle_input()
        elif self.battle_state == "choosing_action":
            return self._handle_action_selection(event)
        elif self.battle_state == "choosing_move":
            return self._handle_move_selection(event)
        elif self.battle_state == "choosing_item_pocket":
            return self._handle_pocket_selection(event)
        elif self.battle_state == "choosing_item":
            return self._handle_item_selection(event)
        elif self.battle_state == "switching":
            return self._handle_party_selection(event)
        elif self.battle_state == "learn_move":
            return self._handle_learn_move_selection(event)
        elif self.battle_state == "over":
            if event.type == pygame.KEYDOWN:
                return self.battle_result
        return None

    def _handle_action_selection(self, event):
        """メインの行動選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            current_index = self.selected_action_index
            
            if event.key == pygame.K_DOWN:
                # 下キー: インデックスを2増やす（0→2, 1→3）
                if current_index < 2:
                    self.selected_action_index += 2
            elif event.key == pygame.K_UP:
                # 上キー: インデックスを2減らす（2→0, 3→1）
                if current_index >= 2:
                    self.selected_action_index -= 2
            elif event.key == pygame.K_LEFT:
                # 左キー: インデックスを1減らす（1→0, 3→2）
                if current_index % 2 == 1:
                    self.selected_action_index -= 1
            elif event.key == pygame.K_RIGHT:
                # 右キー: インデックスを1増やす（0→1, 2→3）
                if current_index % 2 == 0:
                    self.selected_action_index += 1

            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                # 決定キーのロジックはほぼ同じ
                if self.selected_action_index == 0:  # たたかう
                    self.battle_state = "choosing_move"
                elif self.selected_action_index == 1:  # バッグ
                    self.battle_state = "choosing_item_pocket"
                    self._setup_pocket_buttons()
                elif self.selected_action_index == 2:  # ポケモン
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                elif self.selected_action_index == 3:  # にげる
                    if self.battle.execute_run_turn(): # 逃走処理を呼び出す
                        self.battle_result = "escaped"
                    # 逃走の成否メッセージをbattleクラスから受け取る
                    for msg in self.battle.message_log:
                        self.message_box.add_message(msg)
                    self.battle_state = "message_display"
        return None
    
    def _handle_move_selection(self, event):
        active_monster = self.battle.player_monster
        if not active_monster or not active_monster.moves:
            return None

        num_moves = len(active_monster.moves)
        
        if event.type == pygame.KEYDOWN:
            current_index = self.selected_move_index
            
            if event.key == pygame.K_DOWN:
                if current_index < num_moves - 2:
                    self.selected_move_index += 2
            elif event.key == pygame.K_UP:
                if current_index >= 2:
                    self.selected_move_index -= 2
            elif event.key == pygame.K_LEFT:
                if current_index % 2 == 1:
                    self.selected_move_index -= 1
            elif event.key == pygame.K_RIGHT:
                if current_index % 2 == 0 and current_index + 1 < num_moves:
                    self.selected_move_index += 1
            
            self.selected_move_index = max(0, min(self.selected_move_index, num_moves - 1))

            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                selected_move = active_monster.moves[self.selected_move_index]
                
                if selected_move.get('current_pp', 0) <= 0:
                    self.message_box.add_message("PPがなくて わざが だせない！")
                    self.battle_state = "message_display"
                else:
                    selected_move['current_pp'] -= 1 # PPを1消費
                    turn_messages = self.battle.execute_turn(selected_move)
                    for msg in turn_messages:
                        self.message_box.add_message(msg)
                    self.battle_state = "message_display"

            elif event.key == pygame.K_ESCAPE:
                self.battle_state = "choosing_action"
        
        return None
    
    def _handle_pocket_selection(self, event):
        """バッグのポケット選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_pocket_index = (self.selected_pocket_index + 1) % len(self.pocket_buttons)
            elif event.key == pygame.K_UP:
                self.selected_pocket_index = (self.selected_pocket_index - 1) % len(self.pocket_buttons)
            self._update_pocket_selection()
            
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                self.battle_state = "choosing_item"
                selected_pocket = self.pocket_buttons[self.selected_pocket_index].pocket_name
                self._setup_item_buttons(selected_pocket)
            elif event.key == pygame.K_ESCAPE:
                self.battle_state = "choosing_action"
        return None

    def _handle_item_selection(self, event):
        """バッグのアイテム選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.item_buttons: 
                    self.selected_item_index = (self.selected_item_index + 1) % len(self.item_buttons)
            elif event.key == pygame.K_UP:
                if self.item_buttons: 
                    self.selected_item_index = (self.selected_item_index - 1) % len(self.item_buttons)
            self._update_item_selection()
            
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                if self.item_buttons:
                    selected_button = self.item_buttons[self.selected_item_index]
                    item_data = self.inventory.get_item_details(selected_button.item_id)
                    self.message_box.add_message(f"{item_data['name']} を つかった！")
                    self.message_box.add_message("しかし なにも おこらなかった！")
                    self.battle_state = "message_display"
            elif event.key == pygame.K_ESCAPE:
                self.battle_state = "choosing_item_pocket"
        return None
    
    def _handle_party_selection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: 
                self.selected_party_index = (self.selected_party_index + 1) % len(self.party_buttons) if self.party_buttons else 0
            elif event.key == pygame.K_UP: 
                self.selected_party_index = (self.selected_party_index - 1) % len(self.party_buttons) if self.party_buttons else 0
            self._update_party_selection()
            
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                if self.party_buttons and 0 <= self.selected_party_index < len(self.party_buttons):
                    self._switch_pokemon(self.party_buttons[self.selected_party_index].monster)
            elif event.key == pygame.K_ESCAPE: 
                self.battle_state = "choosing_action"
        return None
    
    def _handle_learn_move_selection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DOWN, pygame.K_UP]:
                if event.key == pygame.K_DOWN: 
                    self.selected_learn_move_index = (self.selected_learn_move_index + 1) % len(self.learn_move_buttons)
                else: 
                    self.selected_learn_move_index = (self.selected_learn_move_index - 1) % len(self.learn_move_buttons)
                self._update_learn_move_selection()
                
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                if self.selected_learn_move_index < 4:  # 既存の技を選択
                    old_move_name = self.monster_learning.moves[self.selected_learn_move_index]['name']
                    self.monster_learning.moves[self.selected_learn_move_index] = self.new_move
                    self.message_box.add_message(f"そして {self.monster_learning.name}は...")
                    self.message_box.add_message(f"{old_move_name}を わすれて {self.new_move['name']}を おぼえた！")
                elif self.selected_learn_move_index == 5:  # おぼえない
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえなかった！")
                
                # 技習得処理完了後、残りの経験値でレベルアップを継続
                additional_messages, next_new_move = self.monster_learning.continue_level_up()
                for msg in additional_messages:
                    self.message_box.add_message(msg)
                
                if next_new_move:
                    self.pending_new_move = next_new_move
                    self.selected_learn_move_index = 0
                else:
                    self.pending_new_move = None
                    self.monster_learning = None
                    self.new_move = None
                
                self.battle_state = "message_display"
        return None

    def update(self, dt):
        self.player_hp_bar.update(dt, self.battle.player_monster.current_hp, self.battle.player_monster.max_hp)
        self.enemy_hp_bar.update(dt, self.battle.enemy_monster.current_hp, self.battle.enemy_monster.max_hp)
        self.message_box.update(dt)
        self.action_message_box.update(dt)  # アクションメッセージボックスの更新

        # 状態1: 登場メッセージの表示中
        if self.battle_state == "intro":
            if self.message_box.is_finished: 
                self.battle_state = "choosing_action"
            return

        # 状態2: 何らかのメッセージが表示されている最中
        if self.battle_state == "message_display":
            if self.message_box.is_finished:
                # 待機中の技習得処理をチェック
                if self.pending_new_move:
                    self.new_move = self.pending_new_move
                    self.pending_new_move = None
                    
                    #self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.monster_learning:  # 最初の技習得
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.battle_result:  # バトル終了
                    self.battle_state = "over"
                else:  # 通常のターン
                    self.battle_state = "post_turn_check"
            return

        # 状態3: ターン終了後の判定処理
        if self.battle_state == "post_turn_check":
            # 敵が倒れているかチェック
            if self.battle.enemy_monster.is_fainted():
                if not self.battle_result:
                    self.battle_result = "battle_victory"
                    self.message_box.add_message(f"{self.battle.enemy_monster.name} を たおした！")
                    
                    # 経験値処理
                    messages, new_move = self.battle._award_exp()
                    for msg in messages: 
                        self.message_box.add_message(msg)
                    
                    if new_move:
                        self.monster_learning = self.battle.player_monster
                        self.new_move = new_move
                        #self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                        self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                    
                    # バトル終了時に能力ランクをリセット
                    self._reset_all_stat_stages()
                    
                self.battle_state = "message_display"

            # プレイヤーのポケモンが倒れているかチェック
            elif self.battle.player_monster.is_fainted():
                if self.player_party.has_living_monsters():
                    self.message_box.add_message("つぎのポケモンをえらんでください")
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                else:
                    self.message_box.add_message("全てのポケモンがたおれた...")
                    self.battle_result = "battle_defeat"
                    # バトル終了時に能力ランクをリセット
                    self._reset_all_stat_stages()
                    self.battle_state = "message_display"
            
            # 誰も倒れていなければ次の行動選択へ
            else:
                self.battle_state = "choosing_action"

        # スプライトアニメーションの更新
        self.player_sprite.update(dt)
        self.enemy_sprite.update(dt)

    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill(self.BACKGROUND_GREEN)
        
        # ポケモン情報パネル
        self.player_info.draw(self.screen, self.battle.player_monster)
        self.enemy_info.draw(self.screen, self.enemy_monster)
        # self.screen.blit(self.player_panel_img, self.player_panel_rect)
        # self.screen.blit(self.enemy_panel_img, self.enemy_panel_rect)

        # HPバーの描画
        self.player_hp_bar.draw(self.screen)
        self.enemy_hp_bar.draw(self.screen)

        # レベルの数字を描画
        self.player_level_display.draw(self.screen, self.battle.player_monster.level)
        self.enemy_level_display.draw(self.screen, self.battle.enemy_monster.level)
        
        # ポケモンスプライトを描画
        self.player_sprite.draw(self.screen, 160, 350, scale=3.0)  # プレイヤー側（背面・左下）
        self.enemy_sprite.draw(self.screen, 550, 180, scale=2.5)   # 敵側（正面・右上）
        
        # 状態に応じたUI描画
        if self.battle_state == "choosing_action": 
            self._draw_action_selection()
        elif self.battle_state == "choosing_move": 
            self._draw_move_selection()
        elif self.battle_state == "choosing_item_pocket": 
            self._draw_bag_ui()
        elif self.battle_state == "choosing_item": 
            self._draw_bag_ui()
        elif self.battle_state == "switching": 
            self._draw_party_selection()
        elif self.battle_state == "learn_move": 
            self._draw_learn_move_selection()
        elif self.battle_state == "over": 
            self._draw_battle_over()
        
        # メッセージボックス
        if self.battle_state not in ["choosing_action", "choosing_move", "choosing_item_pocket", "choosing_item"]:
            self.message_box.draw(self.screen)

    def _draw_action_selection(self):
        # 左側のメッセージボックスはそのまま描画
        self.action_message_box.draw(self.screen)

        # --- 右側の選択パネルの描画処理 ---
        panel_x, panel_y = 440, 470
        panel_width, panel_height = 290, 150
        
        if self.action_panel_image:
            self.screen.blit(self.action_panel_image, (panel_x, panel_y))
        else:
            # 画像がない場合の代替描画
            pygame.draw.rect(self.screen, self.WHITE, (panel_x, panel_y, panel_width, panel_height))
            pygame.draw.rect(self.screen, self.BLACK, (panel_x, panel_y, panel_width, panel_height), 3)

        # --- テキストとカーソルの座標計算を修正 ---
        # パネル内の余白やテキスト間の距離を定義
        margin_x = 100  # 左右の余白
        margin_y = 45  # 上下の余白
        spacing_x = 150 # テキスト間の横の距離
        spacing_y = 50  # テキスト間の縦の距離

        for i, text in enumerate(self.action_texts):
            # 2x2グリッドの座標を計算
            col = i % 2  # 列 (0 or 1)
            row = i // 2 # 行 (0 or 1)
            
            text_x = panel_x + margin_x + (col * spacing_x)
            text_y = panel_y + margin_y + (row * spacing_y)

             # 選択されている項目にカーソル画像を描画
            if i == self.selected_action_index:
                cursor_x = text_x - 65
                
                # text_y を基準にカーソルの中心を合わせる
                cursor_rect = self.cursor_image.get_rect(center=(cursor_x, text_y + 5))
                self.screen.blit(self.cursor_image, cursor_rect)
            
            self.draw_text(text, text_x, text_y, self.BLACK, center=True)

    def _draw_move_selection(self):
        # --- パネル全体の描画 ---
        panel_x, panel_y = 0, 470
        panel_width, panel_height = 700, 150

        if self.move_panel_image:
            self.screen.blit(self.move_panel_image, (panel_x, panel_y))
        else:
            # 画像がない場合の代替描画
            pygame.draw.rect(self.screen, self.WHITE, (panel_x, panel_y, panel_width, panel_height))
            pygame.draw.rect(self.screen, self.BLACK, (panel_x, panel_y, panel_width, panel_height), 3)

        active_monster = self.battle.player_monster
        if not active_monster or not active_monster.moves:
            return

        # --- 左側の技リスト部分 ---
        margin_x_left = 50  # パネル左端からの余白
        margin_y = 20
        spacing_x = 250     # 技同士の横の間隔
        spacing_y = 50      # 技同士の縦の間隔

        for i, move in enumerate(active_monster.moves):
            col = i % 2
            row = i // 2
            
            text_x = panel_x + margin_x_left + (col * spacing_x)
            text_y = panel_y + margin_y + (row * spacing_y)

            if i == self.selected_move_index:
                cursor_x = text_x - 10 
                cursor_rect = self.cursor_image.get_rect(center=(cursor_x, text_y + 25))
                self.screen.blit(self.cursor_image, cursor_rect)
            
            self.draw_text(move['name'], text_x, text_y, self.BLACK)

        # --- 右側の詳細情報部分 ---
        if self.selected_move_index < len(active_monster.moves):
            selected_move = active_monster.moves[self.selected_move_index]
            
            # PP表示（左揃え）
            pp_text_x = panel_x + 560 # X座標を左に調整
            pp_text_y = panel_y + 20
            pp_text = f"PP          {selected_move.get('current_pp', 0)}/{selected_move.get('pp', 0)}"
            self.draw_text(pp_text, pp_text_x, pp_text_y) # center=True を削除

            # わざタイプ表示（左揃え）
            type_text_x = panel_x + 560 # X座標を左に調整
            type_text_y = panel_y + 70
            type_text = f"タイプ/ {self._get_japanese_type_name(selected_move['type'])}"
            self.draw_text(type_text, type_text_x, type_text_y) # center=True を削除
    
    def _draw_party_selection(self):
        for button in self.party_buttons:
            button.draw(self.screen)
        self.draw_text("↑↓: 選択  Enter/Space: 決定  Esc: 戻る", 100, 500, self.BLACK)
    
    def _draw_battle_over(self):
        self.draw_text("何かキーを押してください", 400, 500, self.BLACK, center=True)

    def _draw_learn_move_selection(self):
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
    def _draw_learn_move_selection(self):
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, (240, 240, 240), [20, 20, 760, 380])
        pygame.draw.rect(self.screen, (0, 0, 0), [20, 20, 760, 380], 3)
        self.draw_text("どの わざを わすれさせますか？", 400, 50, self.BLACK, center=True)
        for button in self.learn_move_buttons:
            button.draw(self.screen)

    def _draw_bag_ui(self):
        """バッグのUIを描画（ポケットとアイテムリスト）"""
        # 背景と枠
        pygame.draw.rect(self.screen, (240, 240, 240), [20, 20, 760, 380])
        pygame.draw.rect(self.screen, (0, 0, 0), [20, 20, 760, 380], 3)
        
        # アイテムリストの背景
        pygame.draw.rect(self.screen, (50, 50, 50), [40, 40, 500, 340])
        
        # ポケットのボタンを描画
        for button in self.pocket_buttons:
            button.draw(self.screen)
            
        # アイテムリストのボタンを描画
        for button in self.item_buttons:
            button.draw(self.screen)

        # アイテム説明欄
        if self.battle_state == "choosing_item" and self.item_buttons:
            if 0 <= self.selected_item_index < len(self.item_buttons):
                selected_button = self.item_buttons[self.selected_item_index]
                item_data = self.inventory.get_item_details(selected_button.item_id)
                if item_data:
                    self.draw_text(item_data['description'], 50, 350, self.WHITE)