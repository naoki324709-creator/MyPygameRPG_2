# scenes/title_scene.py
import pygame
import os
from scenes.base_scene import BaseScene
from ui.components import Button

class TitleScene(BaseScene):
    """タイトル画面シーンクラス"""
    
    def __init__(self, screen, font):
        super().__init__(screen, font)
        
        # タイトル用の大きなフォント
        self.title_font = pygame.font.Font(None, 72)
        
        # メニューボタン
        self.menu_buttons = [
            Button(300, 300, 200, 50, "はじめから", font),
            Button(300, 360, 200, 50, "つづきから", font),
            Button(300, 420, 200, 50, "せってい", font),
            Button(300, 480, 200, 50, "おわる", font),
        ]
        
        self.selected_index = 0
        self.save_file_exists = os.path.exists("save_data.json")
        self._update_selection()
    
    def _update_selection(self):
        """選択状態を更新"""
        for i, button in enumerate(self.menu_buttons):
            button.is_selected = (i == self.selected_index)
            # つづきからは未実装なので無効化
            if i == 1: # つづきから
                button.is_enabled = self.save_file_exists # セーブファイルがあれば有効
            elif i == 2: # せってい
                button.is_enabled = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_buttons)
                self._update_selection()
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_buttons)
                self._update_selection()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected_index == 0:  # はじめから
                    return "to_field"
                elif self.selected_index == 1 and self.save_file_exists: # つづきから
                    return "load_game" # ← 追加
                elif self.selected_index == 3:  # おわる
                    return "quit"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.menu_buttons):
                if button.is_clicked(event.pos):
                    if i == 0:
                        return "to_field"
                    elif i == 2:
                        return "load_game"
                    elif i == 3:
                        return "quit"
        
        return None
    
    def update(self, dt):
        """更新処理"""
        pass
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill((50, 50, 100))  # 夜空の色
        
        # タイトル
        title_text = self.title_font.render("Pokemon（仮）", True, self.WHITE)
        title_rect = title_text.get_rect()
        title_rect.center = (400, 150)
        self.screen.blit(title_text, title_rect)
        
        # サブタイトル
        subtitle_text = self.font.render("Pygame Edition", True, self.LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.center = (400, 200)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # メニューボタン
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # 操作説明
        #self.draw_text("↑↓: 選択  Enter/Space: 決定", 400, 550, self.WHITE, center=True)