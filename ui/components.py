# ui/components.py - 画像メッセージボックス追加版
import pygame
import os

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
        self.text_color = (60, 60, 60)
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
    def __init__(self, x, y, width, height, change_speed=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.change_speed = change_speed  # HPが1秒間に変化する量

        # HPバーの画像を読み込み、指定されたサイズにリサイズ
        self.bar_images = {
            "green": pygame.transform.scale(pygame.image.load("ui/assets/hp_bar_green.png").convert_alpha(), (width, height)),
            "yellow": pygame.transform.scale(pygame.image.load("ui/assets/hp_bar_yellow.png").convert_alpha(), (width, height)),
            "red": pygame.transform.scale(pygame.image.load("ui/assets/hp_bar_red.png").convert_alpha(), (width, height)),
        }
        
        self.max_hp = 1
        self.current_hp = 1
        self.displayed_hp = 1  # 画面に表示されているHP（アニメーション用）

    def set_initial_pokemon(self, pokemon):
        """対象のポケモンをセットし、HPを初期化する"""
        self.max_hp = pokemon.max_hp
        self.current_hp = pokemon.current_hp
        self.displayed_hp = pokemon.current_hp

    def set_hp_instant(self, pokemon):
        """HPバーの状態をアニメーションなしで瞬時に更新する"""
        self.max_hp = pokemon.max_hp
        self.current_hp = pokemon.current_hp
        self.displayed_hp = pokemon.current_hp # 表示HPも直接更新

    def update(self, dt, current_hp, max_hp):
        """HPバーのアニメーションを更新する"""
        self.current_hp = current_hp
        self.max_hp = max_hp
        
        # 表示HPを実際のHPに近づける
        hp_diff = self.current_hp - self.displayed_hp
        if abs(hp_diff) > 0.1: # わずかな差ならアニメーションしない
            change = self.change_speed * dt
            if hp_diff < 0:
                self.displayed_hp -= change
                if self.displayed_hp < self.current_hp:
                    self.displayed_hp = self.current_hp
            else:
                self.displayed_hp += change
                if self.displayed_hp > self.current_hp:
                    self.displayed_hp = self.current_hp

    def draw(self, screen):
        """HPバーを描画する"""
        if self.max_hp <= 0: return

        hp_ratio = self.displayed_hp / self.max_hp
        
        # HPの割合に応じてバーの色を選択
        if hp_ratio > 0.5:
            bar_image = self.bar_images["green"]
        elif hp_ratio > 0.2:
            bar_image = self.bar_images["yellow"]
        else:
            bar_image = self.bar_images["red"]
            
        # 表示HPの割合に合わせてバーの幅を計算
        current_width = int(self.width * hp_ratio)
        if current_width <= 0: return # 幅が0以下なら描画しない
        
        # 計算した幅のサブサーフェス（画像の一部）を切り出して描画
        bar_subsurface = bar_image.subsurface((0, 0, current_width, self.height))
        screen.blit(bar_subsurface, (self.x, self.y))

class MessageBox:
    """文字を順に表示する機能を持つメッセージボックスクラス（従来版）"""
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.text_color = (60, 60, 60)
        
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

class ImageMessageBox:
    """画像ベースのメッセージボックスクラス"""
    
    def __init__(self, x, y, width, height, font, image_path="ui/textbox.png"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        
        # 画像の読み込み
        self.load_image(image_path)
        
        # テキスト関連
        self.messages = []
        self.current_message = ""
        self.char_index = 0
        self.char_timer = 0
        self.char_speed = 0.03  # 文字表示速度（秒）
        self.line_height = 55
        self.max_lines = 4
        self.text_margin_x = 35  # 左右の余白を大きく
        self.text_margin_y = 25  # 上下の余白を大きく
        
        # 状態管理
        self.is_typing = False
        self.is_finished = True
        self.waiting_for_input = False
    
    def load_image(self, image_path):
        """テキストボックス画像を読み込み"""
        try:
            if os.path.exists(image_path):
                self.bg_image = pygame.image.load(image_path).convert_alpha()
                # 指定されたサイズに画像をリサイズ
                self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))
                print(f"[INFO] テキストボックス画像を読み込み: {image_path}")
            else:
                print(f"[WARNING] 画像が見つかりません: {image_path}")
                self.create_default_image()
        except Exception as e:
            print(f"[ERROR] 画像読み込みエラー: {e}")
            self.create_default_image()
    
    def create_default_image(self):
        """デフォルトのテキストボックス画像を作成"""
        self.bg_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # ポケモン風のテキストボックスを描画
        # ベース色（薄いクリーム色）
        base_color = (248, 248, 240)
        border_color = (72, 72, 72)
        shadow_color = (200, 200, 200)
        accent_color = (100, 150, 255)
        
        # メインのボックス
        pygame.draw.rect(self.bg_image, base_color, (0, 0, self.width, self.height))
        
        # 外枠
        pygame.draw.rect(self.bg_image, border_color, (0, 0, self.width, self.height), 4)
        
        # 内側の影効果
        pygame.draw.rect(self.bg_image, shadow_color, (4, 4, self.width-8, 4))  # 上
        pygame.draw.rect(self.bg_image, shadow_color, (4, 4, 4, self.height-8))  # 左
        
        # 角の装飾
        corner_size = 16
        corners = [
            (8, 8),  # 左上
            (self.width-corner_size-8, 8),  # 右上
            (8, self.height-corner_size-8),  # 左下
            (self.width-corner_size-8, self.height-corner_size-8)  # 右下
        ]
        
        for corner_x, corner_y in corners:
            pygame.draw.rect(self.bg_image, accent_color, 
                           (corner_x, corner_y, corner_size, corner_size))
            pygame.draw.rect(self.bg_image, border_color, 
                           (corner_x, corner_y, corner_size, corner_size), 2)
    
    def add_message(self, message):
        """メッセージを追加"""
        if message:
            self.messages.append(message)
            if not self.is_typing and self.is_finished:
                self._start_next_message()
    
    def _start_next_message(self):
        """次のメッセージの表示開始"""
        if self.messages:
            self.current_message = self.messages.pop(0)
            self.char_index = 0
            self.char_timer = 0
            self.is_typing = True
            self.is_finished = False
            self.waiting_for_input = False
    
    def update(self, dt):
        """更新処理"""
        if self.is_typing:
            self.char_timer += dt
            
            # 文字を1つずつ表示
            if self.char_timer >= self.char_speed:
                self.char_index += 1
                self.char_timer = 0
                
                # メッセージの表示完了
                if self.char_index >= len(self.current_message):
                    self.is_typing = False
                    self.waiting_for_input = True
    
    def handle_input(self):
        """入力処理（Enter/Spaceキー）"""
        if self.is_typing:
            # タイピング中の場合は即座に全文表示
            self.char_index = len(self.current_message)
            self.is_typing = False
            self.waiting_for_input = True
        elif self.waiting_for_input:
            # 次のメッセージへ進む
            if self.messages:
                self._start_next_message()
            else:
                self.is_finished = True
                self.waiting_for_input = False
    
    def draw(self, screen):
        """描画処理"""
        # 背景画像を描画
        screen.blit(self.bg_image, (self.x, self.y))
        
        # テキスト表示領域の設定（左右と上下の余白を個別に設定）
        text_x = self.x + self.text_margin_x
        text_y = self.y + self.text_margin_y
        text_width = self.width - (self.text_margin_x * 2)
        
        if self.current_message:
            # 現在表示中の文字列
            display_text = self.current_message[:self.char_index]
            
            # テキストを行に分割して表示
            self._draw_wrapped_text(screen, display_text, text_x, text_y, text_width)
        
        # 入力待ちインジケーター
        if self.waiting_for_input:
            self._draw_input_indicator(screen)
    
    def _draw_wrapped_text(self, screen, text, x, y, max_width):
        """テキストを複数行に分けて描画"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_surface = self.font.render(test_line, True, (60, 60, 60))
            
            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        # 各行を描画
        for i, line in enumerate(lines[:self.max_lines]):
            line_surface = self.font.render(line, True, (60, 60, 60))
            screen.blit(line_surface, (x, y + i * self.line_height))
    
    def _draw_input_indicator(self, screen):
        """入力待ちのインジケーターを描画"""
        # 右下角に小さな三角形を描画
        indicator_x = self.x + self.width - 30
        indicator_y = self.y + self.height - 25
        
        # 点滅効果
        import time
        if int(time.time() * 2) % 2:  # 0.5秒間隔で点滅
            points = [
                (indicator_x, indicator_y),
                (indicator_x + 15, indicator_y),
                (indicator_x + 7, indicator_y + 10)
            ]
            pygame.draw.polygon(screen, (60, 60, 60), points)

class NumberDisplay:
    """数字を画像の組み合わせで描画するクラス"""
    def __init__(self, x, y, digit_width, digit_height, spacing=0):
        self.x = x
        self.y = y
        self.digit_width = digit_width
        self.digit_height = digit_height
        self.spacing = spacing  # 数字と数字の間のスペース
        self.digit_images = {}
        
        # 0から9までの数字画像を読み込む
        for i in range(10):
            try:
                path = f"ui/assets/num_{i}.png"
                image = pygame.image.load(path).convert_alpha()
                self.digit_images[str(i)] = pygame.transform.scale(image, (digit_width, digit_height))
            except pygame.error:
                print(f"警告: 数字画像が見つかりません: {path}")

    def draw(self, screen, number):
        """指定された数値を画面に描画する"""
        number_str = str(number)

        current_x = self.x
        for digit_char in number_str:
            if digit_char in self.digit_images:
                screen.blit(self.digit_images[digit_char], (current_x, self.y))
            # 次の数字の描画位置を計算
            current_x += self.digit_width + self.spacing

class PokemonInfoPanel:
    """ポケモン情報パネル"""
    def __init__(self, position, size, font, background_image_path, name_pos, name_color):
        self.rect = pygame.Rect(position, size)
        self.font = font
        self.name_pos = name_pos
        self.name_color = name_color
        
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, size)

        # --- レベル表示に関する記述をすべて削除 ---

    def draw(self, screen, pokemon):
        """パネルとポケモンの名前を描画"""
        # 背景
        screen.blit(self.background_image, self.rect.topleft)
        
        # ポケモン名
        # 受け取った座標を使って名前を描画
        name_surface = self.font.render(pokemon.name, True, self.name_color)
        screen.blit(name_surface, self.name_pos)

# デフォルト画像作成用の関数
def create_default_textbox_image():
    """ポケモン風テキストボックス画像を作成"""
    import os
    pygame.init()
    
    width, height = 700, 150
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # ベース色（薄いクリーム色）
    base_color = (248, 248, 240)
    border_color = (72, 72, 72)
    shadow_color = (200, 200, 200)
    accent_color = (100, 150, 255)
    
    # メインのボックス
    pygame.draw.rect(surface, base_color, (0, 0, width, height))
    
    # 外枠
    pygame.draw.rect(surface, border_color, (0, 0, width, height), 4)
    
    # 内側の影効果
    pygame.draw.rect(surface, shadow_color, (4, 4, width-8, 4))  # 上
    pygame.draw.rect(surface, shadow_color, (4, 4, 4, height-8))  # 左
    
    # 角の装飾
    corner_size = 20
    corners = [
        (8, 8),  # 左上
        (width-corner_size-8, 8),  # 右上
        (8, height-corner_size-8),  # 左下
        (width-corner_size-8, height-corner_size-8)  # 右下
    ]
    
    for corner_x, corner_y in corners:
        # 角の背景
        pygame.draw.rect(surface, accent_color, 
                        (corner_x, corner_y, corner_size, corner_size))
        # 角の枠
        pygame.draw.rect(surface, border_color, 
                        (corner_x, corner_y, corner_size, corner_size), 2)
    
    # ディレクトリ作成
    os.makedirs("ui", exist_ok=True)
    
    # 画像を保存
    pygame.image.save(surface, "ui/textbox_default.png")
    print("デフォルトテキストボックス画像を作成: ui/textbox_default.png")
    
    pygame.quit()

if __name__ == "__main__":
    # デフォルト画像の作成
    create_default_textbox_image()