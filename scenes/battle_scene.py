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
        self.battle_state = "intro"  # intro, choosing_move, message_display, switching, learn_move, over
        self.battle_result = None
        
        # 技習得用のプロパティ
        self.monster_learning = None
        self.new_move = None
        self.pending_new_move = None
        self.learn_move_buttons = []
        self.selected_learn_move_index = 0

        self.message_box.add_message(f"あ！ やせいの {enemy_monster.name}が とびだしてきた！")
        self._setup_move_buttons()
    
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

    def _setup_learn_move_buttons(self):
        """技入れ替え選択ボタンをセットアップ"""
        self.learn_move_buttons.clear()
        
        # 現在の技4つ
        for i, move in enumerate(self.monster_learning.moves):
            button = Button(50, 100 + i * 60, 300, 50, move['name'], self.font)
            self.learn_move_buttons.append(button)
        
        # 新しい技
        new_button = Button(450, 100, 300, 50, self.new_move['name'], self.font)
        new_button.bg_color = (200, 255, 200) # 新しい技は色を変える
        self.learn_move_buttons.append(new_button)

        # 覚えない選択肢
        cancel_button = Button(450, 310, 300, 50, "おぼえない", self.font)
        self.learn_move_buttons.append(cancel_button)

        # 選択インデックスを必ず0にリセット（重要！）
        self.selected_learn_move_index = 0
        self._update_learn_move_selection()
    
    def _update_button_selection(self):
        """技ボタンの選択状態を更新"""
        for i, button in enumerate(self.move_buttons):
            button.is_selected = (i == self.selected_move_index)
    
    def _update_party_selection(self):
        """パーティボタンの選択状態を更新"""
        for i, button in enumerate(self.party_buttons):
            button.is_selected = (i == self.selected_party_index)

    def _update_learn_move_selection(self):
        """技入れ替えボタンの選択状態を更新"""
        for i, button in enumerate(self.learn_move_buttons):
            button.is_selected = (i == self.selected_learn_move_index)
    
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
        elif self.battle_state == "learn_move":
            return self._handle_learn_move_selection(event)
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
    
    def _handle_learn_move_selection(self, event):
        """技入れ替え選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DOWN, pygame.K_UP]:
                if event.key == pygame.K_DOWN:
                    self.selected_learn_move_index = (self.selected_learn_move_index + 1) % len(self.learn_move_buttons)
                else:
                    self.selected_learn_move_index = (self.selected_learn_move_index - 1) % len(self.learn_move_buttons)
                self._update_learn_move_selection()

            elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                # 技の入れ替えを実行
                if self.selected_learn_move_index < 4: # 既存の技を選択
                    old_move_name = self.monster_learning.moves[self.selected_learn_move_index]['name']
                    self.monster_learning.moves[self.selected_learn_move_index] = self.new_move
                    self.message_box.add_message(f"そして {self.monster_learning.name}は...")
                    self.message_box.add_message(f"{old_move_name}を わすれて {self.new_move['name']}を おぼえた！")
                elif self.selected_learn_move_index == 5: # 「おぼえない」を選択
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえなかった！")

                # 技習得処理完了後、残りの経験値でレベルアップを継続
                additional_messages, next_new_move = self.monster_learning.continue_level_up()
                for msg in additional_messages:
                    self.message_box.add_message(msg)
                
                # 次に覚える技があるかどうかに関わらず、まずメッセージ表示状態に戻る
                if next_new_move:
                    # 次の技習得のために情報を保存しておく
                    self.pending_new_move = next_new_move
                    # 選択インデックスをリセット
                    self.selected_learn_move_index = 0
                else:
                    # 次に覚える技がない場合
                    self.pending_new_move = None
                    self.monster_learning = None
                    self.new_move = None
                
                # 必ずメッセージ表示状態に戻る
                self.battle_state = "message_display"
        return None
    
    def update(self, dt):
        """
        毎フレームの更新処理。
        メッセージボックスの更新と、ゲームの状態遷移を管理する。
        """
        self.message_box.update(dt)

        # 状態1: 登場メッセージの表示中
        if self.battle_state == "intro":
            if self.message_box.is_finished:
                self.battle_state = "choosing_move"
            return

        # 状態2: 何らかのメッセージが表示されている最中
        if self.battle_state == "message_display":
            if self.message_box.is_finished:
                # メッセージ表示完了後の処理
                if hasattr(self, 'pending_new_move') and self.pending_new_move:
                    # 待機中の技習得処理を開始
                    self.new_move = self.pending_new_move
                    self.pending_new_move = None
                    
                    # 技習得メッセージを追加
                    self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.monster_learning:  
                    # 既存の技習得処理（最初の1回目）
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.battle_result:  
                    # バトルが終了している場合
                    self.battle_state = "over"
                else:  
                    # それ以外（通常のターン）
                    self.battle_state = "post_turn_check"
            return

        # 状態3: ターン終了後の判定処理
        if self.battle_state == "post_turn_check":
            # 敵が倒れているか？
            if self.battle.enemy_monster.is_fainted():
                # まだ勝利処理を行っていなければ、1回だけ実行
                if not self.battle_result:
                    self.battle_result = "battle_victory"  # 勝利状態を確定
                    self.message_box.add_message(f"{self.battle.enemy_monster.name} を たおした！")
                    
                    messages, new_move = self.battle._award_exp()
                    for msg in messages: self.message_box.add_message(msg)
                    
                    if new_move:
                        self.monster_learning = self.battle.player_monster
                        self.new_move = new_move
                        self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                        self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                
                # 勝利メッセージなどを表示するために、状態を切り替え
                self.battle_state = "message_display"

            # プレイヤーのポケモンが倒れているか？
            elif self.battle.player_monster.is_fainted():
                if self.player_party.has_living_monsters():
                    self.message_box.add_message("つぎのポケモンを選んでください")
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                else:
                    self.message_box.add_message("全てのポケモンが倒れた...")
                    self.battle_result = "battle_defeat"
                    self.battle_state = "message_display"
            
            # 誰も倒れていなければ、次の行動選択へ
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
        elif self.battle_state == "learn_move": 
            self._draw_learn_move_selection()
        elif self.battle_state == "over":
            self._draw_battle_over()
        
        self.message_box.draw(self.screen)
    
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

    def _draw_learn_move_selection(self):
        """技入れ替え選択UIを描画"""
        # 半透明の背景を描画して、下のバトル画面を少し暗くする
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # ウィンドウ背景
        pygame.draw.rect(self.screen, (240, 240, 240), [20, 20, 760, 380])
        pygame.draw.rect(self.screen, (0, 0, 0), [20, 20, 760, 380], 3)

        self.draw_text("どの わざを わすれさせますか？", 400, 50, self.BLACK, center=True)

        for button in self.learn_move_buttons:
            button.draw(self.screen)