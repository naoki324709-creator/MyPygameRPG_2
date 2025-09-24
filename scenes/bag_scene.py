# scenes/bag_scene.py
import pygame
from scenes.base_scene import BaseScene
from ui.components import Button

class BagScene(BaseScene):
    """冒険中のバッグ画面シーンクラス"""
    
    def __init__(self, screen, font, inventory):
        super().__init__(screen, font)
        self.inventory = inventory
        
        self.pockets = self.inventory.pockets # ["どうぐ", "ボール", ...]
        self.current_pocket_index = 0
        
        self.item_buttons = []
        self.selected_item_index = 0
        
        self._setup_item_buttons()

    def _setup_item_buttons(self):
        """現在のポケットの中身でアイテムボタンを作成する"""
        self.item_buttons.clear()
        current_pocket_name = self.pockets[self.current_pocket_index]
        
        items_in_pocket = self.inventory.get_items_by_pocket(current_pocket_name)
        
        y_offset = 100
        for item_id, item_info in items_in_pocket.items():
            text = f"{item_info['data']['name']} x{item_info['count']}"
            button = Button(150, y_offset, 400, 50, text, self.font)
            button.item_id = item_id
            self.item_buttons.append(button)
            y_offset += 60
        
        self.selected_item_index = 0
        self._update_item_selection()

    def _update_item_selection(self):
        """アイテムボタンの選択状態を更新"""
        for i, button in enumerate(self.item_buttons):
            button.is_selected = (i == self.selected_item_index)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back" # メニュー画面に戻る
            
            # ← → キーでポケットを切り替え
            elif event.key == pygame.K_RIGHT:
                self.current_pocket_index = (self.current_pocket_index + 1) % len(self.pockets)
                self._setup_item_buttons()
            elif event.key == pygame.K_LEFT:
                self.current_pocket_index = (self.current_pocket_index - 1) % len(self.pockets)
                self._setup_item_buttons()
            
            # ↑ ↓ キーでアイテムを選択
            elif event.key == pygame.K_DOWN:
                if self.item_buttons:
                    self.selected_item_index = (self.selected_item_index + 1) % len(self.item_buttons)
                    self._update_item_selection()
            elif event.key == pygame.K_UP:
                if self.item_buttons:
                    self.selected_item_index = (self.selected_item_index - 1) % len(self.item_buttons)
                    self._update_item_selection()
        return None

    def update(self, dt):
        pass

    def draw(self):
        """描画処理"""
        self.screen.fill((40, 40, 40))
        
        # ポケット名の表示
        pocket_name = self.pockets[self.current_pocket_index]
        self.draw_text(f"＜ {pocket_name} ＞", 400, 50, self.WHITE, center=True)
        
        # アイテムボタンの描画
        for button in self.item_buttons:
            button.draw(self.screen)
        
        # アイテム説明欄
        if self.item_buttons and 0 <= self.selected_item_index < len(self.item_buttons):
            selected_button = self.item_buttons[self.selected_item_index]
            item_data = self.inventory.get_item_details(selected_button.item_id)
            if item_data:
                self.draw_text(item_data['description'], 50, 500, self.WHITE)
        else:
            self.draw_text("この ポケットは からっぽだ！", 50, 120, self.WHITE)

        # 操作説明
        self.draw_text("↑↓: 選択  ←→: ポケット切替  Esc: もどる", 50, 550, self.WHITE)