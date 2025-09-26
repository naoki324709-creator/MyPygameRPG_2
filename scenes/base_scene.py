# scenes/base_scene.py
from abc import ABC, abstractmethod
import pygame

class BaseScene(ABC):
    """全てのシーンの基底クラス"""
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.next_scene = None
        self.is_finished = False
        
        
        # 共通色定義
        self.WHITE = (255, 255, 255)
        #self.BLACK = (0, 0, 0)
        self.BLACK = (60, 60, 60)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        #self.DARK_GRAY = (60, 60, 60)
        self.LIGHT_GRAY = (200, 200, 200)
        self.HIGHLIGHT_COLOR = (255, 255, 0)
        self.BACKGROUND_GREEN = (96, 176, 80)
    
    @abstractmethod
    def handle_event(self, event):
        """イベント処理（各シーンで実装）"""
        pass
    
    @abstractmethod
    def update(self, dt):
        """更新処理（各シーンで実装）"""
        pass
    
    @abstractmethod
    def draw(self):
        """描画処理（各シーンで実装）"""
        pass
    
    def transition_to(self, scene_type, **kwargs):
        """他のシーンへの遷移を設定"""
        self.next_scene = scene_type
        self.scene_kwargs = kwargs
        self.is_finished = True
    
    def get_next_scene(self):
        """次のシーンとその引数を返す"""
        if self.next_scene:
            return self.next_scene, getattr(self, 'scene_kwargs', {})
        return None, {}
    
    def finish(self):
        """シーンの終了を設定"""
        self.is_finished = True
    
    def draw_text(self, text, x, y, color=None, center=False):
        """テキストを描画するヘルパーメソッド"""
        if color is None:
            color = self.BLACK
        
        text_surface = self.font.render(text, True, color)
        
        if center:
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
    
    def draw_button(self, rect, text, is_selected=False, bg_color=None, text_color=None):
        """ボタンを描画するヘルパーメソッド"""
        if bg_color is None:
            bg_color = self.WHITE
        if text_color is None:
            text_color = self.BLACK
            
        # ボタン背景
        pygame.draw.rect(self.screen, bg_color, rect)
        
        # ボーダー
        border_width = 5 if is_selected else 2
        border_color = self.HIGHLIGHT_COLOR if is_selected else self.BLACK
        pygame.draw.rect(self.screen, border_color, rect, border_width)
        
        # テキスト
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = rect.center
        self.screen.blit(text_surface, text_rect)