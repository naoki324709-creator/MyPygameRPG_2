# scenes/battle_scene.py
import pygame
from scenes.base_scene import BaseScene
from ui.components import Button, HPBar, MessageBox, PokemonInfoPanel
from battle import Battle

class BattleScene(BaseScene):
    """バトルシーンクラス"""
    
    def __init__(self, screen, font, player_party, enemy_monster):
        super().__init__(screen, font)
        
        self.player_party = player_party
        self.enemy_monster = enemy_monster
        self.battle = Battle(player_party.get_active_monster(), enemy_monster)
        
        # UI コンポーネント
        self.message_box = MessageBox(50, 420, 500, 150, font)
        self.player_info = PokemonInfoPanel(450, 300, 300, 120, font)
        self.enemy_info = PokemonInfoPanel(50, 50, 300, 120, font)
        
        # ボタンリスト
        self.move_buttons = []
        self.party_buttons = []
        
        # 選択状態
        self.selected_move_index = 0
        self.selected_party_index = 0
        
        # バトル状態
        self.battle_state = "choosing_move"  # "choosing_move", "switching", "animating", "over"
        self.battle_result = None
        
        self._setup_move_buttons()

        self.battle_state = "intro" # intro, choosing_move, animating, switching, over, message_display
        self.message_box.add_message(f"あ！ やせいの {enemy_monster.name}が とびだしてきた！")
    
    def _setup_move_buttons(self):
        """技選択ボタンをセットアップ"""
        self.move_buttons.clear()
        active_monster = self.battle.player_monster
        
        if active_monster and active_monster.moves:
            for i, move in enumerate(active_monster.moves):
                x = 570 + (i % 2) * 110
                y = 440 + (i // 2) * 40
                button = Button(x, y, 100, 35, move['name'], self.font)
                button.move_data = move
                self.move_buttons.append(button)
        
        self._update_button_selection()
    
    def _setup_party_buttons(self):
        """パーティ選択ボタンをセットアップ"""
        self.party_buttons.clear()
        living_monsters = self.player_party.get_living_monsters()
        
        button_count = 0
        for monster in living_monsters:
            if monster != self.battle.player_monster:
                y = 100 + button_count * 70
                button = Button(100, y, 400, 60, f"{monster.name} (HP: {monster.current_hp}/{monster.max_hp})", self.font)
                button.monster = monster
                self.party_buttons.append(button)
                button_count += 1
        
        self.selected_party_index = 0
        self._update_party_selection()
    
    def _update_button_selection(self):
        """技ボタンの選択状態を更新"""
        for i, button in enumerate(self.move_buttons):
            button.is_selected = (i == self.selected_move_index)
    
    def _update_party_selection(self):
        """パーティボタンの選択状態を更新"""
        for i, button in enumerate(self.party_buttons):
            button.is_selected = (i == self.selected_party_index)
    
    def _execute_turn(self):
        """ターンを実行し、発生したメッセージをメッセージボックスにセットする。"""
        if not self.move_buttons or self.selected_move_index >= len(self.move_buttons):
            return
            
        selected_move = self.move_buttons[self.selected_move_index].move_data
        
        turn_messages = self.battle.execute_turn(selected_move)
        
        for msg in turn_messages:
            self.message_box.add_message(msg)
        
        # 状態を「メッセージ表示中」に変更
        self.battle_state = "message_display"

    
    def _switch_pokemon(self, monster):
        """ポケモンを交代し、メッセージ表示状態に移行する"""
        # battle.pyから交代メッセージを受け取る
        switch_message = self.battle.switch_player_monster(monster)
        # 受け取ったメッセージをメッセージボックスに追加
        self.message_box.add_message(switch_message)
        # 新しいポケモンの技でボタンを準備
        self._setup_move_buttons()
        # 状態を「メッセージ表示中」に変更して、メッセージが表示されるのを待つ
        self.battle_state = "message_display"
    
    def handle_event(self, event):
        # メッセージ表示中（introまたはmessage_display）の入力処理
        if self.battle_state in ["intro", "message_display"]:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                self.message_box.handle_input()
        elif self.battle_state == "choosing_move":
            return self._handle_move_selection(event)
        elif self.battle_state == "switching":
            return self._handle_party_selection(event)
        elif self.battle_state == "over":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    return self.battle_result
        return None
    
    def _handle_move_selection(self, event):
        """技選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_move_index = (self.selected_move_index + 2) % len(self.move_buttons) if self.move_buttons else 0
                if self.selected_move_index >= len(self.move_buttons):
                    self.selected_move_index = len(self.move_buttons) - 1
                self._update_button_selection()
            elif event.key == pygame.K_UP:
                self.selected_move_index = (self.selected_move_index - 2) % len(self.move_buttons) if self.move_buttons else 0
                if self.selected_move_index < 0:
                    self.selected_move_index = 0
                self._update_button_selection()
            elif event.key == pygame.K_LEFT:
                if self.selected_move_index % 2 == 1:
                    self.selected_move_index -= 1
                    self._update_button_selection()
            elif event.key == pygame.K_RIGHT:
                if self.selected_move_index % 2 == 0 and self.selected_move_index + 1 < len(self.move_buttons):
                    self.selected_move_index += 1
                    self._update_button_selection()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self._execute_turn()
            elif event.key == pygame.K_ESCAPE:
                return "back"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.move_buttons):
                if button.is_clicked(event.pos):
                    self.selected_move_index = i
                    self._update_button_selection()
                    self._execute_turn()
                    break
        
        return None
    
    def _handle_party_selection(self, event):
        """パーティ選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_party_index = (self.selected_party_index + 1) % len(self.party_buttons) if self.party_buttons else 0
                self._update_party_selection()
            elif event.key == pygame.K_UP:
                self.selected_party_index = (self.selected_party_index - 1) % len(self.party_buttons) if self.party_buttons else 0
                self._update_party_selection()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.party_buttons and 0 <= self.selected_party_index < len(self.party_buttons):
                    selected_monster = self.party_buttons[self.selected_party_index].monster
                    self._switch_pokemon(selected_monster)
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.party_buttons:
                if button.is_clicked(event.pos):
                    self._switch_pokemon(button.monster)
                    break
        
        return None
    
    def update(self, dt):
        """
        毎フレームの更新処理。
        メッセージボックスの更新と、ゲームの状態遷移を管理する。
        """
        # 1. メッセージボックスの文字送り処理を常に実行する
        self.message_box.update(dt)

        # 2. ゲームの状態に応じた遷移ロジック
        
        # a. 登場メッセージの表示が完了したら、技選択へ移行
        if self.battle_state == "intro" and self.message_box.is_finished:
            self.battle_state = "choosing_move"
            
        # b. ターン中の攻撃メッセージ表示が完了したら、「ターン終了後チェック」状態へ移行
        elif self.battle_state == "message_display" and self.message_box.is_finished:
            self.battle_state = "post_turn_check"

        # c. 「ターン終了後チェック」状態で、ひんし判定や勝敗判定を行う
        #    この状態は一瞬で次の状態へ移行する
        elif self.battle_state == "post_turn_check":
            # i. 敵が倒れたか？
            if self.battle.enemy_monster.is_fainted():
                self.message_box.add_message(f"{self.enemy_monster.name} を たおした！")
                self.battle_state = "over"
                self.battle_result = "battle_victory"
            
            # ii. （敵が倒れていないなら）味方が倒れたか？
            elif self.battle.player_monster.is_fainted():
                # iii. 手持ちにまだ戦えるポケモンはいるか？
                if self.player_party.has_living_monsters():
                    self.message_box.add_message("つぎのポケモンを選んでください")
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                else:
                    self.message_box.add_message("全てのポケモンが倒れた...")
                    self.battle_state = "over"
                    self.battle_result = "battle_defeat"
            
            # iv. （誰も倒れていないなら）戦闘は続く
            else:
                self.battle_state = "choosing_move"

    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill(self.BACKGROUND_GREEN)
        
        # ポケモン描画エリア
        player_area = pygame.Rect(100, 280, 120, 100)
        enemy_area = pygame.Rect(500, 120, 100, 80)
        pygame.draw.rect(self.screen, self.DARK_GRAY, player_area)
        pygame.draw.rect(self.screen, self.DARK_GRAY, enemy_area)
        
        # ポケモン情報パネル
        self.player_info.draw(self.screen, self.battle.player_monster)
        self.enemy_info.draw(self.screen, self.enemy_monster)
        
        # メッセージボックス
        self.message_box.draw(self.screen)
        
        # 状態に応じたUI描画
        if self.battle_state == "choosing_move":
            self._draw_move_selection()
        elif self.battle_state == "switching":
            self._draw_party_selection()
        elif self.battle_state == "over":
            self._draw_battle_over()
    
    def _draw_move_selection(self):
        """技選択UI描画"""
        for button in self.move_buttons:
            button.draw(self.screen)
        
        # 操作説明
        self.draw_text("↑↓←→: 選択  Enter/Space: 決定  Esc: 戻る", 570, 520, self.BLACK)
    
    def _draw_party_selection(self):
        """パーティ選択UI描画"""
        for button in self.party_buttons:
            button.draw(self.screen)
        
        # 操作説明
        self.draw_text("↑↓: 選択  Enter/Space: 決定", 100, 500, self.BLACK)
    
    def _draw_battle_over(self):
        """バトル終了UI描画"""
        self.draw_text("何かキーを押してください", 400, 500, self.BLACK, center=True)