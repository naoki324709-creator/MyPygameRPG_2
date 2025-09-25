# sprite_working_version_with_back.py - 動作版に背面対応を追加
import pygame
from PIL import Image, ImageSequence
import os
import json

def gif_to_spritesheet_clean(gif_path, output_path, info_path, frames_per_row=8):
    """GIFファイルをスプライトシートに変換（残像修正版）"""
    try:
        print(f"[DEBUG] GIF変換開始: {gif_path}")
        
        # GIFを開く
        gif = Image.open(gif_path)
        frames = []
        
        # GIFの全フレームを適切に処理
        for frame_index, frame in enumerate(ImageSequence.Iterator(gif)):
            print(f"[DEBUG] フレーム {frame_index} を処理中...")
            
            # 各フレームを個別に処理（合成しない）
            if frame.mode == 'P':
                # パレットモードの場合、透明色を考慮してRGBAに変換
                if 'transparency' in frame.info:
                    frame = frame.convert('RGBA')
                else:
                    frame = frame.convert('RGB').convert('RGBA')
            elif frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            
            # フレームの透明度をチェック（PILで直接チェック）
            pixels = list(frame.getdata())
            if len(pixels) > 0 and len(pixels[0]) == 4:  # RGBAチェック
                alpha_values = [pixel[3] for pixel in pixels]
                non_transparent_pixels = sum(1 for alpha in alpha_values if alpha > 30)
                transparency_ratio = non_transparent_pixels / len(alpha_values)
                
                # 透明度が高すぎる（90%以上透明）フレームをスキップ
                if transparency_ratio < 0.1:
                    print(f"[WARNING] フレーム {frame_index} は透明度が高いためスキップします (不透明度: {transparency_ratio:.1%})")
                    continue
                
                print(f"[DEBUG] フレーム {frame_index}: 不透明度 {transparency_ratio:.1%}")
            
            # フレームをコピーして追加（参照ではなく実体をコピー）
            frames.append(frame.copy())
        
        print(f"[DEBUG] 有効なフレーム {len(frames)} 個を抽出完了")
        
        if not frames:
            print("有効なフレームが見つかりません")
            return False
        
        # フレームサイズを取得
        frame_width, frame_height = frames[0].size
        print(f"[DEBUG] フレームサイズ: {frame_width}x{frame_height}")
        
        # スプライトシートのサイズを計算
        total_frames = len(frames)
        rows = (total_frames + frames_per_row - 1) // frames_per_row
        sheet_width = frame_width * min(frames_per_row, total_frames)
        sheet_height = frame_height * rows
        
        print(f"[DEBUG] スプライトシートサイズ: {sheet_width}x{sheet_height}")
        
        # 完全に透明な背景でスプライトシートを作成
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # フレームをスプライトシートに配置
        for i, frame in enumerate(frames):
            col = i % frames_per_row
            row = i // frames_per_row
            x = col * frame_width
            y = row * frame_height
            
            # フレームを直接貼り付け（アルファブレンドなし）
            sprite_sheet.paste(frame, (x, y))
        
        # ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # スプライトシートを保存
        sprite_sheet.save(output_path, 'PNG')
        
        # フレーム情報をJSONで保存
        frame_info = {
            "frame_width": frame_width,
            "frame_height": frame_height,
            "total_frames": total_frames,
            "frames_per_row": min(frames_per_row, total_frames),
            "sheet_width": sheet_width,
            "sheet_height": sheet_height,
            "original_frames": frame_index + 1,
            "filtered_frames": total_frames
        }
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(frame_info, f, indent=2)
        
        print(f"スプライトシート作成完了: {output_path}")
        print(f"フレーム情報保存完了: {info_path}")
        print(f"元フレーム数: {frame_index + 1} → 有効フレーム数: {total_frames}")
        
        return True
        
    except Exception as e:
        print(f"変換エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

class SpriteSheet:
    """スプライトシートから個別フレームを切り出すクラス"""
    def __init__(self, image_path, frame_width, frame_height, frames_per_row=None):
        # pygame.display が初期化されていない場合の対策
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.set_mode((1, 1))
        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = []
        
        # スプライトシートから個別フレームを切り出し
        sheet_width, sheet_height = self.image.get_size()
        if frames_per_row is None:
            frames_per_row = sheet_width // frame_width
        
        rows = sheet_height // frame_height
        
        print(f"[DEBUG] スプライトシート情報:")
        print(f"  画像サイズ: {sheet_width}x{sheet_height}")
        print(f"  フレームサイズ: {frame_width}x{frame_height}")
        print(f"  1行あたりのフレーム数: {frames_per_row}")
        print(f"  行数: {rows}")
        
        for row in range(rows):
            for col in range(frames_per_row):
                x = col * frame_width
                y = row * frame_height
                
                # 範囲チェック
                if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                    frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                    frame_surface = self.image.subsurface(frame_rect).copy()
                    
                    # 基本的な透明度チェック（中心と4隅をサンプル）
                    test_points = [
                        (frame_width//2, frame_height//2),  # 中心
                        (frame_width//4, frame_height//4),  # 左上寄り
                        (3*frame_width//4, frame_height//4),  # 右上寄り
                        (frame_width//4, 3*frame_height//4),  # 左下寄り
                        (3*frame_width//4, 3*frame_height//4),  # 右下寄り
                    ]
                    
                    alpha_sum = 0
                    for px, py in test_points:
                        if 0 <= px < frame_width and 0 <= py < frame_height:
                            color = frame_surface.get_at((px, py))
                            alpha_sum += color.a
                    
                    avg_alpha = alpha_sum / len(test_points)
                    
                    # より寛容な透明度チェック（少しでも不透明部分があれば採用）
                    if avg_alpha > 5:  # 閾値を下げる
                        self.frames.append(frame_surface)
                        print(f"  フレーム {len(self.frames)}: ({x}, {y}) - アルファ平均: {avg_alpha:.1f}")
                    else:
                        print(f"  スキップ: ({x}, {y}) - 透明フレーム (アルファ平均: {avg_alpha:.1f})")
        
        print(f"  有効フレーム数: {len(self.frames)}")
        
        # フレームが1つも有効でない場合は、すべて追加
        if len(self.frames) == 0:
            print("[WARNING] 有効フレームが0個のため、すべてのフレームを追加します")
            for row in range(rows):
                for col in range(frames_per_row):
                    x = col * frame_width
                    y = row * frame_height
                    
                    if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                        frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                        frame_surface = self.image.subsurface(frame_rect).copy()
                        self.frames.append(frame_surface)
            print(f"  強制追加フレーム数: {len(self.frames)}")

class AnimatedSprite:
    """アニメーションスプライトクラス"""
    def __init__(self, sprite_sheet, animation_speed=0.12):
        self.frames = sprite_sheet.frames
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.animation_timer = 0
        self.playing = True
        self.loop = True
        
        print(f"[DEBUG] AnimatedSprite初期化: {len(self.frames)}フレーム, 速度: {animation_speed}")
    
    def update(self, dt):
        """アニメーションの更新"""
        if self.playing and len(self.frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                if self.loop:
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                else:
                    if self.current_frame < len(self.frames) - 1:
                        self.current_frame += 1
                    else:
                        self.playing = False
                self.animation_timer = 0
    
    def get_current_frame(self):
        """現在のフレームを取得"""
        if self.frames and 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def play(self):
        self.playing = True
    
    def pause(self):
        self.playing = False
    
    def reset(self):
        self.current_frame = 0
        self.animation_timer = 0
        self.playing = True

class PokemonSprite:
    """ポケモン用のスプライトクラス（正面・背面対応版）"""
    def __init__(self, pokemon_id, facing_direction="front"):
        """
        pokemon_id: ポケモンのID (例: "bulbasaur")
        facing_direction: "front" (正面) または "back" (背面)
        """
        self.pokemon_id = pokemon_id
        self.facing_direction = facing_direction
        self.sprite_sheets = {}
        self.current_animation = "idle"
        self.animated_sprite = None
        
        # スプライトファイルを読み込み
        self.load_sprites()
    
    def load_sprites(self):
        """スプライトファイルを読み込み"""
        sprite_dir = f"sprites/{self.pokemon_id}"
        
        # まずGIFから変換を試行
        self.convert_gifs_if_needed()
        
        # 向きに応じたファイル名を設定
        if self.facing_direction == "back":
            file_suffix = "_back"
        else:
            file_suffix = "_front"
        
        # 各アニメーション用のスプライトシートを読み込み
        animations = ["idle", "attack", "hurt", "faint"]
        
        for animation in animations:
            sprite_path = f"{sprite_dir}/{animation}{file_suffix}.png"
            info_path = f"{sprite_dir}/{animation}{file_suffix}_info.json"
            
            # 背面ファイルが無い場合は正面を試行
            if not os.path.exists(sprite_path) and self.facing_direction == "back":
                sprite_path = f"{sprite_dir}/{animation}.png"
                info_path = f"{sprite_dir}/{animation}_info.json"
                print(f"[INFO] {animation} 背面が見つからないため正面を使用: {sprite_path}")
            
            if os.path.exists(sprite_path) and os.path.exists(info_path):
                try:
                    # フレーム情報を読み込み
                    with open(info_path, 'r', encoding='utf-8') as f:
                        frame_info = json.load(f)
                    
                    print(f"[INFO] {animation}{file_suffix} 情報: {frame_info.get('filtered_frames', 'N/A')}フレーム (元: {frame_info.get('original_frames', 'N/A')})")
                    
                    # 正しいフレームサイズでスプライトシートを読み込み
                    sprite_sheet = SpriteSheet(
                        sprite_path, 
                        frame_info["frame_width"], 
                        frame_info["frame_height"],
                        frame_info["frames_per_row"]
                    )
                    
                    if sprite_sheet.frames:
                        self.sprite_sheets[animation] = AnimatedSprite(sprite_sheet)
                        print(f"[DEBUG] {animation}{file_suffix} アニメーション読み込み完了")
                    else:
                        print(f"[WARNING] {animation}{file_suffix} のフレームが見つかりません")
                        
                except Exception as e:
                    print(f"[ERROR] {animation}{file_suffix} の読み込みエラー: {e}")
                    import traceback
                    traceback.print_exc()
        
        # デフォルトアニメーションを設定
        if "idle" in self.sprite_sheets:
            self.animated_sprite = self.sprite_sheets["idle"]
            print(f"[DEBUG] デフォルトアニメーション設定: idle ({self.facing_direction})")
        elif self.sprite_sheets:
            first_animation = list(self.sprite_sheets.keys())[0]
            self.animated_sprite = self.sprite_sheets[first_animation]
            print(f"[DEBUG] デフォルトアニメーション設定: {first_animation} ({self.facing_direction})")
    
    def convert_gifs_if_needed(self):
        """必要に応じてGIFをスプライトシートに変換"""
        gif_dir = f"pokemon_gifs"
        sprite_dir = f"sprites/{self.pokemon_id}"
        
        # 向きに応じたGIFファイルとファイル名を設定
        if self.facing_direction == "back":
            gif_patterns = [f"{self.pokemon_id}_b.gif", f"{self.pokemon_id}_back.gif"]
            output_suffix = "_back"
        else:  # front
            gif_patterns = [f"{self.pokemon_id}_f.gif", f"{self.pokemon_id}_front.gif", f"{self.pokemon_id}.gif"]
            output_suffix = "_front"
        
        # 対応するGIFファイルを探して変換
        for pattern in gif_patterns:
            gif_path = os.path.join(gif_dir, pattern)
            if os.path.exists(gif_path):
                output_path = os.path.join(sprite_dir, f"idle{output_suffix}.png")
                info_path = os.path.join(sprite_dir, f"idle{output_suffix}_info.json")
                
                # まだ変換されていない場合のみ変換
                if not os.path.exists(output_path) or not os.path.exists(info_path):
                    print(f"[INFO] GIF変換中 ({self.facing_direction}): {gif_path}")
                    gif_to_spritesheet_clean(gif_path, output_path, info_path)
                    break
        else:
            # 対応するGIFが見つからない場合
            if self.facing_direction == "back":
                # 背面GIFがない場合は正面を使用
                front_patterns = [f"{self.pokemon_id}_f.gif", f"{self.pokemon_id}.gif"]
                for pattern in front_patterns:
                    gif_path = os.path.join(gif_dir, pattern)
                    if os.path.exists(gif_path):
                        output_path = os.path.join(sprite_dir, f"idle_back.png")
                        info_path = os.path.join(sprite_dir, f"idle_back_info.json")
                        
                        if not os.path.exists(output_path) or not os.path.exists(info_path):
                            print(f"[INFO] 背面GIFが見つからないため正面GIFを使用: {gif_path}")
                            gif_to_spritesheet_clean(gif_path, output_path, info_path)
                            break
                else:
                    print(f"[WARNING] {self.pokemon_id} の GIF ファイルが見つかりません")
    
    def play_animation(self, animation_name):
        """指定されたアニメーションを再生"""
        if animation_name in self.sprite_sheets:
            self.current_animation = animation_name
            self.animated_sprite = self.sprite_sheets[animation_name]
            self.animated_sprite.reset()
            self.animated_sprite.play()
            print(f"[DEBUG] アニメーション変更: {animation_name} ({self.facing_direction})")
        else:
            print(f"[WARNING] アニメーション '{animation_name}' ({self.facing_direction}) が見つかりません")
    
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
                return True
        return False

def clean_and_convert_working_version():
    """動作版をベースに正面・背面変換"""
    pokemon_list = ["bulbasaur", "charmander", "squirtle", "pidgey"]
    
    for pokemon in pokemon_list:
        sprite_dir = f"sprites/{pokemon}"
        
        # 既存の正面・背面ファイルを削除
        for direction in ["_front", "_back"]:
            for filename in [f"idle{direction}.png", f"idle{direction}_info.json"]:
                filepath = os.path.join(sprite_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"[INFO] 削除しました: {filepath}")
        
        # 正面と背面の両方を変換
        print(f"\n=== {pokemon} の動作版ベース変換開始 ===")
        
        # 正面スプライト
        front_sprite = PokemonSprite(pokemon, "front")
        
        # 背面スプライト
        back_sprite = PokemonSprite(pokemon, "back")
        
        print(f"=== {pokemon} の変換完了 ===\n")

def test_front_back_working():
    """正面・背面動作版のテスト"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("正面・背面動作版テスト")
    clock = pygame.time.Clock()
    
    # テスト用のポケモンスプライト（正面と背面）
    pokemon_front = PokemonSprite("bulbasaur", "front")  # 相手（正面）
    pokemon_back = PokemonSprite("bulbasaur", "back")    # 味方（背面）
    
    current_pokemon = "bulbasaur"
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # アニメーションリセット
                    pokemon_front.play_animation("idle")
                    pokemon_back.play_animation("idle")
                elif event.key == pygame.K_1:
                    current_pokemon = "bulbasaur"
                    pokemon_front = PokemonSprite(current_pokemon, "front")
                    pokemon_back = PokemonSprite(current_pokemon, "back")
                elif event.key == pygame.K_2:
                    current_pokemon = "charmander"
                    pokemon_front = PokemonSprite(current_pokemon, "front")
                    pokemon_back = PokemonSprite(current_pokemon, "back")
                elif event.key == pygame.K_3:
                    current_pokemon = "squirtle"
                    pokemon_front = PokemonSprite(current_pokemon, "front")
                    pokemon_back = PokemonSprite(current_pokemon, "back")
                elif event.key == pygame.K_4:
                    current_pokemon = "pidgey"
                    pokemon_front = PokemonSprite(current_pokemon, "front")
                    pokemon_back = PokemonSprite(current_pokemon, "back")
        
        # 更新
        pokemon_front.update(dt)
        pokemon_back.update(dt)
        
        # 描画
        screen.fill((100, 200, 100))
        
        # 左側に味方（背面）、右側に相手（正面）を表示
        pokemon_back.draw(screen, 200, 400, scale=4.0)   # 味方（背面・左下）
        pokemon_front.draw(screen, 600, 200, scale=4.0)  # 相手（正面・右上）
        
        # ラベル
        font = pygame.font.Font(None, 24)
        text1 = font.render("Player (Back)", True, (255, 255, 255))
        text2 = font.render("Enemy (Front)", True, (255, 255, 255))
        text3 = font.render(f"Current: {current_pokemon}", True, (255, 255, 255))
        text4 = font.render("1-4: Change Pokemon, Space: Reset", True, (255, 255, 255))
        text5 = font.render("Based on Working Version", True, (255, 255, 0))
        
        screen.blit(text1, (120, 500))
        screen.blit(text2, (520, 100))
        screen.blit(text3, (10, 10))
        screen.blit(text4, (10, 35))
        screen.blit(text5, (10, 60))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    # 動作版ベースで正面・背面変換
    clean_and_convert_working_version()
    
    # テストを実行
    print("\n動作版ベース 正面・背面テストを起動中...")
    print("左下: 味方（背面）, 右上: 相手（正面）")
    test_front_back_working()