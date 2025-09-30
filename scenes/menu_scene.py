# scenes/menu_scene.py
import pygame
from scenes.base_scene import BaseScene
from ui.components import Button, PokemonInfoPanel

class MenuScene(BaseScene):
    """メニュー画面シーンクラス"""
    
    def __init__(self, screen, font, player_party, inventory):
        super().__init__(screen, font)
        
        self.player_party = player_party
        self.inventory = inventory # ★ inventory を受け取って保存
        
        # メニューボタン
        self.menu_buttons = [
            Button(50, 100, 200, 50, "ポケモン", font),
            Button(50, 160, 200, 50, "どうぐ", font),
            Button(50, 220, 200, 50, "セーブ", font),
            Button(50, 280, 200, 50, "もどる", font),
        ]
        
        self.selected_index = 0
        self.menu_state = "main"
        
        self.pokemon_buttons = []
        self.selected_pokemon_index = 0
        self.rearranging_index = None
        
        self._setup_pokemon_buttons()
        self._update_selection()
    
    def _setup_pokemon_buttons(self):
        """ポケモン一覧ボタンをセットアップ"""
        self.pokemon_buttons.clear()
        for i, pokemon in enumerate(self.player_party.members):
            status = "ひんし" if pokemon.is_fainted() else f"HP: {pokemon.current_hp}/{pokemon.max_hp}"
            button_text = f"{pokemon.name} Lv.{pokemon.level} ({status})"
            button = Button(300, 100 + i * 60, 400, 50, button_text, self.font)
            button.pokemon = pokemon
            self.pokemon_buttons.append(button)
    
    def _update_selection(self):
        """選択状態を更新"""
        if self.menu_state == "main":
            for i, button in enumerate(self.menu_buttons):
                button.is_selected = (i == self.selected_index)
                button.is_enabled = True
        
        # --- ここから変更 ---
        elif self.menu_state == "pokemon" or self.menu_state == "rearranging":
            for i, button in enumerate(self.pokemon_buttons):
                # カーソルのある場所を選択状態にする
                button.is_selected = (i == self.selected_pokemon_index)
                
                # 並び替え中のポケモンは背景色を変える
                if self.menu_state == "rearranging" and i == self.rearranging_index:
                    button.bg_color = (180, 220, 255) # 水色
                else:
                    button.bg_color = self.WHITE # 通常の色
        # --- ここまで変更 ---
    
    def handle_event(self, event):
        if self.menu_state == "main":
            return self._handle_main_menu(event)
        elif self.menu_state == "pokemon":
            return self._handle_pokemon_menu(event)
        # --- ここから追加 ---
        elif self.menu_state == "rearranging":
            return self._handle_rearranging_menu(event)
        # --- ここまで追加 ---
        return None
    
    def _handle_main_menu(self, event):
        """メインメニューのイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_buttons)
                self._update_selection()
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_buttons)
                self._update_selection()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected_index == 0:  # ポケモン
                    self.menu_state = "pokemon"
                    self.selected_pokemon_index = 0
                    self._update_selection()
                elif self.selected_index == 1: # ★ どうぐ
                    return "to_bag"
                elif self.selected_index == 2 and self.menu_buttons[2].is_enabled: # セーブ
                    return "save_game"
                elif self.selected_index == 3:  # もどる
                    return "back"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.menu_buttons):
                if button.is_clicked(event.pos):
                    if i == 0:
                        self.menu_state = "pokemon"
                        self.selected_pokemon_index = 0
                        self._update_selection()
                    elif i == 1: # ★ どうぐ
                        return "to_bag"
                    elif i == 2 and button.is_enabled:
                        return "save_game"
                    elif i == 3:
                        return "back"
        
        return None
    
    def _handle_pokemon_menu(self, event):
        """ポケモンメニューのイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_pokemon_index = (self.selected_pokemon_index + 1) % len(self.pokemon_buttons)
                self._update_selection()
            elif event.key == pygame.K_UP:
                self.selected_pokemon_index = (self.selected_pokemon_index - 1) % len(self.pokemon_buttons)
                self._update_selection()
            # --- ここから変更 ---
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # 決定キーで並び替えモードに移行
                self.rearranging_index = self.selected_pokemon_index
                self.menu_state = "rearranging"
                self._update_selection()
            # --- ここまで変更 ---
            elif event.key == pygame.K_ESCAPE:
                self.menu_state = "main"
                self._update_selection()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.pokemon_buttons):
                if button.is_clicked(event.pos):
                    # クリックで並び替えモードに移行
                    self.selected_pokemon_index = i
                    self.rearranging_index = i
                    self.menu_state = "rearranging"
                    self._update_selection()
                    break
        
        return None

    # --- ここから新しい関数を追加 ---
    def _handle_rearranging_menu(self, event):
        """ポケモン並び替え中のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_pokemon_index = (self.selected_pokemon_index + 1) % len(self.pokemon_buttons)
                self._update_selection()
            elif event.key == pygame.K_UP:
                self.selected_pokemon_index = (self.selected_pokemon_index - 1) % len(self.pokemon_buttons)
                self._update_selection()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # 決定キーでポケモンを入れ替え
                p = self.player_party.members
                p[self.rearranging_index], p[self.selected_pokemon_index] = \
                    p[self.selected_pokemon_index], p[self.rearranging_index]
                
                # 並び替えモードを終了
                self.rearranging_index = None
                self.menu_state = "pokemon"
                # ボタンの表示を更新
                self._setup_pokemon_buttons()
                self._update_selection()
            
            elif event.key == pygame.K_ESCAPE:
                # キャンセルキーで並び替えモードを終了
                self.rearranging_index = None
                self.menu_state = "pokemon"
                self._update_selection()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.pokemon_buttons):
                if button.is_clicked(event.pos):
                    p = self.player_party.members
                    p[self.rearranging_index], p[i] = p[i], p[self.rearranging_index]
                    self.rearranging_index = None
                    self.menu_state = "pokemon"
                    self._setup_pokemon_buttons()
                    self._update_selection()
                    break
        
        return None
    # --- ここまで新しい関数を追加 ---
    
    def update(self, dt):
        """更新処理"""
        pass
    
    def draw(self):
        """描画処理"""
        self.screen.fill((40, 40, 40))
        
        if self.menu_state == "main":
            self._draw_main_menu()
        elif self.menu_state == "pokemon" or self.menu_state == "rearranging": # 変更
            self._draw_pokemon_menu()
    
    def _draw_main_menu(self):
        """メインメニュー描画"""
        self.draw_text("メニュー", 400, 50, self.WHITE, center=True)
        for button in self.menu_buttons:
            button.draw(self.screen)
        self.draw_text("↑↓: 選択  Enter/Space: 決定  Esc: 戻る", 50, 550, self.WHITE)
    
    def _draw_pokemon_menu(self):
        """ポケモンメニュー描画"""
        self.draw_text("ポケモン", 400, 50, self.WHITE, center=True)
        
        # 戻るボタンの代わりに操作説明を表示
        if self.menu_state == "rearranging":
            self.draw_text("いれかえたい ばしょを えらんでください", 50, 20, self.WHITE)
            self.draw_text("↑↓: 選択  Enter: 決定  Esc: キャンセル", 50, 550, self.WHITE)
        else:
            self.draw_text("いれかえたい ポケモンを えらんでください", 50, 20, self.WHITE)
            self.draw_text("↑↓: 選択  Enter: 決定  Esc: もどる", 50, 550, self.WHITE)
        
        # ポケモンリスト
        for button in self.pokemon_buttons:
            button.draw(self.screen)
        
        # 選択されたポケモンの詳細情報
        if self.pokemon_buttons and 0 <= self.selected_pokemon_index < len(self.pokemon_buttons):
            selected_pokemon = self.pokemon_buttons[self.selected_pokemon_index].pokemon
            
            # PokemonInfoPanelの呼び出し方を新しい仕様に合わせる
            panel_x, panel_y = 50, 400
            detail_panel = PokemonInfoPanel(
                position=(panel_x, panel_y),
                size=(700, 120),
                font=self.font,
                background_image_path="ui/assets/panel_player.png", # 背景画像を仮指定
                name_pos=(panel_x + 20, panel_y + 10),              # 名前の位置を仮指定
                name_color=(255, 255, 255)                          # 名前の色を仮指定（白）
            )
            detail_panel.draw(self.screen, selected_pokemon)