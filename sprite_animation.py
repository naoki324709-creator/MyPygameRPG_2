# sprite_animation.py
import pygame
from PIL import Image
import os

class SpriteSheet:
    """スプライトシートから個別フレームを切り出すクラス"""
    def __init__(self, image_path, frame_width, frame_height, frames_per_row=None):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = []
        
        # スプライトシートから個別フレームを切り出し
        sheet_width, sheet_height = self.image.get_size()
        if frames_per_row is None:
            frames_per_row = sheet_width // frame_width
        
        rows = sheet_height // frame_height
        
        for row in range(rows):
            for col in range(frames_per_row):
                x = col * frame_width
                y = row * frame_height
                frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                frame = self.image.subsurface(frame_rect).copy()
                self.frames.append(frame)

class AnimatedSprite:
    """アニメーションスプライトクラス"""
    def __init__(self, sprite_sheet, animation_speed=0.1):
        self.frames = sprite_sheet.frames
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.animation_timer = 0
        self.playing = True
    
    def update(self, dt):
        """アニメーションの更新"""
        if self.playing and len(self.frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
    
    def get_current_frame(self):
        """現在のフレームを取得"""
        if self.frames:
            return self.frames[self.current_frame]
        return None
    
    def play(self):
        self.playing = True
    
    def pause(self):
        self.playing = False
    
    def reset(self):
        self.current_frame = 0
        self.animation_timer = 0

def gif_to_spritesheet(gif_path, output_path, frames_per_row=8):
    """GIFファイルをスプライトシートに変換"""
    try:
        # GIFを開く
        gif = Image.open(gif_path)
        frames = []
        
        # 全フレームを抽出
        try:
            while True:
                # フレームをRGBAに変換
                frame = gif.copy().convert('RGBA')
                frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        
        if not frames:
            print("GIFにフレームが見つかりません")
            return False
        
        # フレームサイズを取得
        frame_width, frame_height = frames[0].size
        
        # スプライトシートのサイズを計算
        total_frames = len(frames)
        rows = (total_frames + frames_per_row - 1) // frames_per_row
        sheet_width = frame_width * min(frames_per_row, total_frames)
        sheet_height = frame_height * rows
        
        # スプライトシートを作成
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # フレームをスプライトシートに配置
        for i, frame in enumerate(frames):
            col = i % frames_per_row
            row = i // frames_per_row
            x = col * frame_width
            y = row * frame_height
            sprite_sheet.paste(frame, (x, y))
        
        # スプライトシートを保存
        sprite_sheet.save(output_path)
        print(f"スプライトシート作成完了: {output_path}")
        print(f"フレーム数: {total_frames}, サイズ: {sheet_width}x{sheet_height}")
        return True
        
    except Exception as e:
        print(f"変換エラー: {e}")
        return False

class PokemonSprite:
    """ポケモン用のスプライトクラス"""
    def __init__(self, pokemon_id):
        self.pokemon_id = pokemon_id
        self.sprite_sheets = {}
        self.current_animation = "idle"
        self.animated_sprite = None
        
        # スプライトファイルを読み込み
        self.load_sprites()
    
    def load_sprites(self):
        """スプライトファイルを読み込み"""
        sprite_dir = f"sprites/{self.pokemon_id}"
        
        # 各アニメーション用のスプライトシートを読み込み
        animations = ["idle", "attack", "hurt", "faint"]
        
        for animation in animations:
            sprite_path = f"{sprite_dir}/{animation}.png"
            if os.path.exists(sprite_path):
                # スプライトシートを読み込み（64x64ピクセルのフレームと仮定）
                sprite_sheet = SpriteSheet(sprite_path, 64, 64)
                self.sprite_sheets[animation] = AnimatedSprite(sprite_sheet)
        
        # デフォルトアニメーションを設定
        if "idle" in self.sprite_sheets:
            self.animated_sprite = self.sprite_sheets["idle"]
    
    def play_animation(self, animation_name):
        """指定されたアニメーションを再生"""
        if animation_name in self.sprite_sheets:
            self.current_animation = animation_name
            self.animated_sprite = self.sprite_sheets[animation_name]
            self.animated_sprite.reset()
            self.animated_sprite.play()
    
    def update(self, dt):
        """スプライトの更新"""
        if self.animated_sprite:
            self.animated_sprite.update(dt)
    
    def draw(self, screen, x, y, scale=1.0):
        """スプライトを描画"""
        if self.animated_sprite:
            frame = self.animated_sprite.get_current_frame()
            if frame:
                if scale != 1.0:
                    # スケーリング
                    width = int(frame.get_width() * scale)
                    height = int(frame.get_height() * scale)
                    frame = pygame.transform.scale(frame, (width, height))
                
                # 中央揃えで描画
                rect = frame.get_rect()
                rect.center = (x, y)
                screen.blit(frame, rect)

# 使用例
def convert_pokemon_gifs():
    """ポケモンのGIFファイルをスプライトシートに変換"""
    pokemon_list = ["bulbasaur", "charmander", "squirtle", "pidgey"]
    
    for pokemon in pokemon_list:
        gif_path = f"pokemon_gifs/{pokemon}_f.gif"
        output_path = f"sprites/{pokemon}/f.png"
        
        # ディレクトリを作成
        os.makedirs(f"sprites/{pokemon}", exist_ok=True)
        
        if os.path.exists(gif_path):
            gif_to_spritesheet(gif_path, output_path)
        else:
            print(f"GIFファイルが見つかりません: {gif_path}")

if __name__ == "__main__":
    # GIFからスプライトシートに変換
    convert_pokemon_gifs()