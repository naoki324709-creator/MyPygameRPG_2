# ui/components.py
import pygame

class Button:
    """ボタンクラス"""
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_selected = False
        self.is_enabled = True
        
        # 色設定
        self.bg_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.border_color = (0, 0, 0)
        self.selected_color = (255, 255, 0)
        self.disabled_color = (128, 128, 128)
    
    def draw(self, screen):
        """ボタンを描画"""
        # 背景色
        bg_color = self.disabled_color if not self.is_enabled else self.bg_color
        pygame.draw.rect(screen, bg_color, self.rect)
        
        # ボーダー
        border_width = 5 if self.is_selected else 2
        border_color = self.selected_color if self.is_selected else self.border_color
        pygame.draw.rect(screen, border_color, self.rect, border_width)
        
        # テキスト
        text_color = self.text_color if self.is_enabled else (64, 64, 64)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        """マウス位置がボタン内かチェック"""
        return self.rect.collidepoint(pos) and self.is_enabled

class HPBar:
    """HPバークラス"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = (0, 0, 0)
        self.hp_color = (0, 255, 0)
        self.border_color = (0, 0, 0)
    
    def draw(self, screen, current_hp, max_hp):
        """HPバーを描画"""
        # 背景
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # HP部分
        if max_hp > 0:
            hp_ratio = current_hp / max_hp
            hp_width = (self.rect.width - 4) * hp_ratio
            hp_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, hp_width, self.rect.height - 4)
            
            # HPが少ないときは色を変える
            if hp_ratio > 0.5:
                color = (0, 255, 0)  # 緑
            elif hp_ratio > 0.2:
                color = (255, 255, 0)  # 黄
            else:
                color = (255, 0, 0)  # 赤
                
            pygame.draw.rect(screen, color, hp_rect)

class MessageBox:
    """メッセージボックスクラス"""
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        self.messages = []
        self.max_lines = 4
    
    def add_message(self, message):
        """メッセージを追加"""
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
    
    def clear(self):
        """メッセージをクリア"""
        self.messages.clear()
    
    def draw(self, screen):
        """メッセージボックスを描画"""
        # 背景
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 3)
        
        # メッセージ
        line_height = 30
        start_y = self.rect.y + 10
        
        for i, message in enumerate(self.messages):
            text_surface = self.font.render(message, True, self.text_color)
            screen.blit(text_surface, (self.rect.x + 15, start_y + i * line_height))

class PokemonInfoPanel:
    """ポケモン情報パネル"""
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.hp_bar = HPBar(x + 10, y + height - 30, width - 20, 20)
        
    def draw(self, screen, pokemon):
        """ポケモン情報を描画"""
        if not pokemon:
            return
            
        # 背景
        pygame.draw.rect(screen, (240, 240, 240), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # 名前
        name_text = self.font.render(pokemon.name, True, (0, 0, 0))
        screen.blit(name_text, (self.rect.x + 10, self.rect.y + 10))
        
        # レベル
        level_text = self.font.render(f"Lv.{pokemon.level}", True, (0, 0, 0))
        screen.blit(level_text, (self.rect.x + 10, self.rect.y + 40))
        
        # HP数値
        hp_text = self.font.render(f"HP: {pokemon.current_hp}/{pokemon.max_hp}", True, (0, 0, 0))
        screen.blit(hp_text, (self.rect.x + 10, self.rect.y + 70))
        
        # HPバー
        self.hp_bar.draw(screen, pokemon.current_hp, pokemon.max_hp)
        
        # 状態異常
        if pokemon.status_condition:
            status_map = {
                "poison": "どく", "paralysis": "まひ", "toxic": "もうどく",
                "burn": "やけど", "sleep": "ねむり", "freeze": "こおり"
            }
            status_text = status_map.get(pokemon.status_condition, pokemon.status_condition)
            status_surface = self.font.render(status_text, True, (255, 0, 0))
            screen.blit(status_surface, (self.rect.x + 200, self.rect.y + 10))