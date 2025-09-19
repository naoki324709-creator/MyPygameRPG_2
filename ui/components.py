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
    """文字を順に表示する機能を持つメッセージボックスクラス"""
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        
        self.message_queue = []       # 表示待ちのメッセージリスト
        self.current_message = ""     # 現在表示中のメッセージ
        self.visible_chars = 0        # 現在表示されている文字数
        self.text_speed = 50          # 1秒間に表示する文字数
        self.timer = 0                # 文字送り用のタイマー
        
        self.is_finished = True       # 全てのメッセージを表示し終えたか
        self.is_line_finished = True  # 1行のメッセージを表示し終えたか

    def add_message(self, message):
        """表示したいメッセージをキューに追加する"""
        self.message_queue.append(message)
        if self.is_finished:
            self._start_next_message()

    def _start_next_message(self):
        """キューから次のメッセージを取り出して表示を開始する"""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.visible_chars = 0
            self.is_finished = False
            self.is_line_finished = False
        else:
            self.current_message = ""
            self.is_finished = True
            self.is_line_finished = True

    def handle_input(self):
        """入力処理。決定キーで文字送りや次のメッセージへ進める"""
        if self.is_line_finished:
            # 1行の表示が終わっていれば、次のメッセージへ
            self._start_next_message()
        else:
            # 表示途中なら、全ての文字を瞬時に表示
            self.visible_chars = len(self.current_message)
            self.is_line_finished = True

    def update(self, dt):
        """時間経過で文字を1文字ずつ表示する"""
        if not self.is_line_finished:
            self.timer += dt
            # text_speedに応じて表示文字数を増やす
            self.visible_chars = self.timer * self.text_speed
            
            if self.visible_chars >= len(self.current_message):
                self.visible_chars = len(self.current_message)
                self.is_line_finished = True

    def draw(self, screen):
        """メッセージボックスを描画"""
        if self.is_finished: return # 表示すべきメッセージがなければ描画しない

        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 3)
        
        # 表示する部分のテキストを切り出す
        text_to_draw = self.current_message[:int(self.visible_chars)]
        text_surface = self.font.render(text_to_draw, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + 15, self.rect.y + 10))

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