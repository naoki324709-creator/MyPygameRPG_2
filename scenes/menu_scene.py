# scenes/menu_scene.py
import pygame
from scenes.base_scene import BaseScene
from ui.components import Button, PokemonInfoPanel

class MenuScene(BaseScene):
    """メニュー画面シーンクラス"""
    
    def __init__(self, screen, font, player_party):
        super().__init__(screen, font)
        
        self.player_party = player_party
        
        # メニューボタン
        self.menu_buttons = [
            Button(50, 100, 200, 50, "ポケモン", font),
            Button(50, 160, 200, 50, "どうぐ", font),
            Button(50, 220, 200, 50, "セーブ", font),
            Button(50, 280, 200, 50, "もどる", font),
        ]
        
        self.selected_index = 0
        self.menu_state = "main"  # "main", "pokemon"
        
        # ポケモン一覧用
        self.pokemon_buttons = []
        self.selected_pokemon_index = 0
        
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
                # 未実装機能は無効化
                if i == 1:  # どうぐ
                    button.is_enabled = False
                elif i == 2: # セーブ
                    button.is_enabled = True
        elif self.menu_state == "pokemon":
            for i, button in enumerate(self.pokemon_buttons):
                button.is_selected = (i == self.selected_pokemon_index)
    
    def handle_event(self, event):
        if self.menu_state == "main":
            return self._handle_main_menu(event)
        elif self.menu_state == "pokemon":
            return self._handle_pokemon_menu(event)
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
                elif self.selected_index == 2: # セーブ
                    return "save_game" # ← 追加
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
                    elif i == 2:
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
            elif event.key == pygame.K_ESCAPE:
                self.menu_state = "main"
                self._update_selection()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.pokemon_buttons:
                if button.is_clicked(event.pos):
                    # ポケモンの詳細表示（未実装）
                    pass
        
        return None
    
    def update(self, dt):
        """更新処理"""
        pass
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill((40, 40, 40))
        
        if self.menu_state == "main":
            self._draw_main_menu()
        elif self.menu_state == "pokemon":
            self._draw_pokemon_menu()
    
    def _draw_main_menu(self):
        """メインメニュー描画"""
        # タイトル
        self.draw_text("メニュー", 400, 50, self.WHITE, center=True)
        
        # メニューボタン
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # 操作説明
        self.draw_text("↑↓: 選択  Enter/Space: 決定  Esc: 戻る", 50, 550, self.WHITE)
    
    def _draw_pokemon_menu(self):
        """ポケモンメニュー描画"""
        # タイトル
        self.draw_text("ポケモン", 400, 50, self.WHITE, center=True)
        
        # 戻るボタン
        back_button = Button(50, 50, 100, 40, "< もどる", self.font)
        back_button.draw(self.screen)
        
        # ポケモンリスト
        for button in self.pokemon_buttons:
            button.draw(self.screen)
        
        # 選択されたポケモンの詳細情報
        if self.pokemon_buttons and 0 <= self.selected_pokemon_index < len(self.pokemon_buttons):
            selected_pokemon = self.pokemon_buttons[self.selected_pokemon_index].pokemon
            
            # 詳細パネル
            detail_panel = PokemonInfoPanel(50, 400, 700, 120, self.font)
            detail_panel.draw(self.screen, selected_pokemon)
        
        # 操作説明
        self.draw_text("↑↓: 選択  Esc: 戻る", 50, 550, self.WHITE)