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
        
        self.message_box = MessageBox(50, 420, 700, 150, font)
        self.player_info = PokemonInfoPanel(450, 300, 300, 120, font)
        self.enemy_info = PokemonInfoPanel(50, 50, 300, 120, font)
        
        self.action_buttons = []
        self.move_buttons = []
        self.party_buttons = []
        self.learn_move_buttons = []
        
        self.selected_action_index = 0
        self.selected_move_index = 0
        self.selected_party_index = 0
        self.selected_learn_move_index = 0
        
        self.battle_state = "intro"
        self.battle_result = None
        
        # 技習得関連
        self.monster_learning = None
        self.new_move = None
        self.pending_new_move = None

        self.message_box.add_message(f"あ！ やせいの {enemy_monster.name}が とびだしてきた！")
        
        self._setup_action_buttons()
        self._setup_move_buttons()

    def _setup_action_buttons(self):
        self.action_buttons.clear()
        actions = ["たたかう", "バッグ", "ポケモン", "にげる"]
        for i, action in enumerate(actions):
            x = 570 + (i % 2) * 110
            y = 440 + (i // 2) * 40
            button = Button(x, y, 100, 35, action, self.font)
            if action in ["バッグ"]: 
                button.is_enabled = False
            self.action_buttons.append(button)
        self._update_action_selection()

    def _update_action_selection(self):
        for i, button in enumerate(self.action_buttons):
            button.is_selected = (i == self.selected_action_index)

    def _setup_move_buttons(self):
        self.move_buttons.clear()
        active_monster = self.battle.player_monster
        if active_monster and active_monster.moves:
            for i, move in enumerate(active_monster.moves):
                x = 570 + (i % 2) * 110
                y = 440 + (i // 2) * 40
                button = Button(x, y, 100, 35, move['name'], self.font)
                button.move_data = move
                self.move_buttons.append(button)
        self.selected_move_index = 0
        self._update_button_selection()
    
    def _setup_party_buttons(self):
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
        self.learn_move_buttons.clear()
        if not self.monster_learning or not self.new_move: 
            return

        # 現在の技4つ
        for i, move in enumerate(self.monster_learning.moves):
            button = Button(50, 100 + i * 60, 300, 50, move['name'], self.font)
            self.learn_move_buttons.append(button)
        
        # 新しい技
        new_button = Button(450, 100, 300, 50, self.new_move['name'], self.font)
        new_button.bg_color = (200, 255, 200)
        self.learn_move_buttons.append(new_button)

        # 覚えない選択肢
        cancel_button = Button(450, 310, 300, 50, "おぼえない", self.font)
        self.learn_move_buttons.append(cancel_button)

        self.selected_learn_move_index = 0
        self._update_learn_move_selection()
    
    def _update_button_selection(self):
        for i, button in enumerate(self.move_buttons):
            button.is_selected = (i == self.selected_move_index)
    
    def _update_party_selection(self):
        for i, button in enumerate(self.party_buttons):
            button.is_selected = (i == self.selected_party_index)

    def _update_learn_move_selection(self):
        for i, button in enumerate(self.learn_move_buttons):
            button.is_selected = (i == self.selected_learn_move_index)
    
    def _reset_all_stat_stages(self):
        """バトル終了時に全ポケモンの能力ランクをリセットする"""
        # プレイヤーの全ポケモンの能力ランクをリセット
        for pokemon in self.player_party.members:
            for stat in pokemon.stat_stages:
                pokemon.stat_stages[stat] = 0
        
        # 敵ポケモンもリセット
        if self.enemy_monster:
            for stat in self.enemy_monster.stat_stages:
                self.enemy_monster.stat_stages[stat] = 0
    
    def _execute_turn(self):
        if not self.move_buttons or self.selected_move_index >= len(self.move_buttons): 
            return
        selected_move = self.move_buttons[self.selected_move_index].move_data
        turn_messages = self.battle.execute_turn(selected_move)
        for msg in turn_messages:
            self.message_box.add_message(msg)
        self.battle_state = "message_display"
    
    def _switch_pokemon(self, monster):
        switch_message = self.battle.switch_player_monster(monster)
        self.message_box.add_message(switch_message)
        self._setup_move_buttons()
        self.battle_state = "message_display"
    
    def handle_event(self, event):
        if self.battle_state in ["intro", "message_display"]:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                self.message_box.handle_input()
        elif self.battle_state == "choosing_action":
            return self._handle_action_selection(event)
        elif self.battle_state == "choosing_move":
            return self._handle_move_selection(event)
        elif self.battle_state == "switching":
            return self._handle_party_selection(event)
        elif self.battle_state == "learn_move":
            return self._handle_learn_move_selection(event)
        elif self.battle_state == "over":
            if event.type == pygame.KEYDOWN:
                return self.battle_result
        return None

    def _handle_action_selection(self, event):
        """メインの行動選択時のイベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_action_index = (self.selected_action_index + 2) % 4
            elif event.key == pygame.K_UP:
                self.selected_action_index = (self.selected_action_index - 2) % 4
            elif event.key == pygame.K_LEFT:
                if self.selected_action_index % 2 == 1: 
                    self.selected_action_index -= 1
            elif event.key == pygame.K_RIGHT:
                if self.selected_action_index % 2 == 0: 
                    self.selected_action_index += 1
            self._update_action_selection()

            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                button = self.action_buttons[self.selected_action_index]
                if not button.is_enabled: 
                    return None

                if self.selected_action_index == 0:  # たたかう
                    self.battle_state = "choosing_move"
                elif self.selected_action_index == 2:  # ポケモン
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                elif self.selected_action_index == 3:  # にげる
                    self.message_box.add_message("うまく にげきれた！")
                    self.battle_result = "escaped"
                    self._reset_all_stat_stages()  # 逃走時も能力ランクリセット
                    self.battle_state = "message_display"
        return None
    
    def _handle_move_selection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: 
                self.selected_move_index = (self.selected_move_index + 2) % len(self.move_buttons) if self.move_buttons else 0
                if self.selected_move_index >= len(self.move_buttons):
                    self.selected_move_index = len(self.move_buttons) - 1
            elif event.key == pygame.K_UP: 
                self.selected_move_index = (self.selected_move_index - 2) % len(self.move_buttons) if self.move_buttons else 0
                if self.selected_move_index < 0:
                    self.selected_move_index = 0
            elif event.key == pygame.K_LEFT:
                if self.selected_move_index % 2 == 1: 
                    self.selected_move_index -= 1
            elif event.key == pygame.K_RIGHT:
                if self.selected_move_index % 2 == 0 and self.selected_move_index + 1 < len(self.move_buttons): 
                    self.selected_move_index += 1
            self._update_button_selection()
            
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]: 
                self._execute_turn()
            elif event.key == pygame.K_ESCAPE: 
                self.battle_state = "choosing_action"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.move_buttons):
                if button.is_clicked(event.pos):
                    self.selected_move_index = i
                    self._update_button_selection()
                    self._execute_turn()
                    break
        return None
    
    def _handle_party_selection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: 
                self.selected_party_index = (self.selected_party_index + 1) % len(self.party_buttons) if self.party_buttons else 0
            elif event.key == pygame.K_UP: 
                self.selected_party_index = (self.selected_party_index - 1) % len(self.party_buttons) if self.party_buttons else 0
            self._update_party_selection()
            
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                if self.party_buttons and 0 <= self.selected_party_index < len(self.party_buttons):
                    self._switch_pokemon(self.party_buttons[self.selected_party_index].monster)
            elif event.key == pygame.K_ESCAPE: 
                self.battle_state = "choosing_action"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.party_buttons:
                if button.is_clicked(event.pos): 
                    self._switch_pokemon(button.monster)
                    break
        return None
    
    def _handle_learn_move_selection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DOWN, pygame.K_UP]:
                if event.key == pygame.K_DOWN: 
                    self.selected_learn_move_index = (self.selected_learn_move_index + 1) % len(self.learn_move_buttons)
                else: 
                    self.selected_learn_move_index = (self.selected_learn_move_index - 1) % len(self.learn_move_buttons)
                self._update_learn_move_selection()
                
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                if self.selected_learn_move_index < 4:  # 既存の技を選択
                    old_move_name = self.monster_learning.moves[self.selected_learn_move_index]['name']
                    self.monster_learning.moves[self.selected_learn_move_index] = self.new_move
                    self.message_box.add_message(f"そして {self.monster_learning.name}は...")
                    self.message_box.add_message(f"{old_move_name}を わすれて {self.new_move['name']}を おぼえた！")
                elif self.selected_learn_move_index == 5:  # おぼえない
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえなかった！")
                
                # 技習得処理完了後、残りの経験値でレベルアップを継続
                additional_messages, next_new_move = self.monster_learning.continue_level_up()
                for msg in additional_messages:
                    self.message_box.add_message(msg)
                
                # 次に覚える技があるかチェック（リスト対応）
                if next_new_move:
                    if isinstance(next_new_move, list):
                        self.pending_new_move = next_new_move[0] if next_new_move else None
                    else:
                        self.pending_new_move = next_new_move
                    self.selected_learn_move_index = 0
                else:
                    self.pending_new_move = None
                    self.monster_learning = None
                    self.new_move = None
                
                self.battle_state = "message_display"
        return None

    def update(self, dt):
        self.message_box.update(dt)

        # 状態1: 登場メッセージの表示中
        if self.battle_state == "intro":
            if self.message_box.is_finished: 
                self.battle_state = "choosing_action"
            return

        # 状態2: 何らかのメッセージが表示されている最中
        if self.battle_state == "message_display":
            if self.message_box.is_finished:
                # 待機中の技習得処理をチェック
                if self.pending_new_move:
                    self.new_move = self.pending_new_move
                    self.pending_new_move = None
                    
                    self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                    self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.monster_learning:  # 最初の技習得
                    self.battle_state = "learn_move"
                    self._setup_learn_move_buttons()
                elif self.battle_result:  # バトル終了
                    self.battle_state = "over"
                else:  # 通常のターン
                    self.battle_state = "post_turn_check"
            return

        # 状態3: ターン終了後の判定処理
        if self.battle_state == "post_turn_check":
            # 敵が倒れているかチェック
            if self.battle.enemy_monster.is_fainted():
                if not self.battle_result:
                    self.battle_result = "battle_victory"
                    self.message_box.add_message(f"{self.battle.enemy_monster.name} を たおした！")
                    
                    # 経験値処理
                    messages, new_move = self.battle._award_exp()
                    for msg in messages: 
                        self.message_box.add_message(msg)
                    
                    # new_moveが技オブジェクトかリストかをチェック
                    if new_move:
                        self.monster_learning = self.battle.player_monster
                        # new_moveがリストの場合は最初の技を取得
                        if isinstance(new_move, list):
                            self.new_move = new_move[0] if new_move else None
                        else:
                            self.new_move = new_move
                        
                        if self.new_move:
                            self.message_box.add_message(f"おや…？ {self.monster_learning.name}の ようすが…")
                            self.message_box.add_message(f"{self.monster_learning.name}は {self.new_move['name']}を おぼえようとしている！")
                    
                    # バトル終了時に能力ランクをリセット
                    self._reset_all_stat_stages()
                    
                self.battle_state = "message_display"

            # プレイヤーのポケモンが倒れているかチェック
            elif self.battle.player_monster.is_fainted():
                if self.player_party.has_living_monsters():
                    self.message_box.add_message("つぎのポケモンを選んでください")
                    self.battle_state = "switching"
                    self._setup_party_buttons()
                else:
                    self.message_box.add_message("全てのポケモンが倒れた...")
                    self.battle_result = "battle_defeat"
                    # バトル終了時に能力ランクをリセット
                    self._reset_all_stat_stages()
                    self.battle_state = "message_display"
            
            # 誰も倒れていなければ次の行動選択へ
            else:
                self.battle_state = "choosing_action"

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
        
        # 状態に応じたUI描画
        if self.battle_state == "choosing_action": 
            self._draw_action_selection()
        elif self.battle_state == "choosing_move": 
            self._draw_move_selection()
        elif self.battle_state == "switching": 
            self._draw_party_selection()
        elif self.battle_state == "learn_move": 
            self._draw_learn_move_selection()
        elif self.battle_state == "over": 
            self._draw_battle_over()
        
        # メッセージボックス
        self.message_box.draw(self.screen)

    def _draw_action_selection(self):
        prompt_rect = pygame.Rect(50, 420, 500, 150)
        pygame.draw.rect(self.screen, (240, 240, 240), prompt_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), prompt_rect, 3)
        self.draw_text(f"{self.battle.player_monster.name} は どうする？", 70, 440)
        for button in self.action_buttons:
            button.draw(self.screen)

    def _draw_move_selection(self):
        for button in self.move_buttons:
            button.draw(self.screen)
        self.draw_text("↑↓←→: 選択  Enter/Space: 決定  Esc: 戻る", 570, 520, self.BLACK)
    
    def _draw_party_selection(self):
        for button in self.party_buttons:
            button.draw(self.screen)
        self.draw_text("↑↓: 選択  Enter/Space: 決定  Esc: 戻る", 100, 500, self.BLACK)
    
    def _draw_battle_over(self):
        self.draw_text("何かキーを押してください", 400, 500, self.BLACK, center=True)

    def _draw_learn_move_selection(self):
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, (240, 240, 240), [20, 20, 760, 380])
        pygame.draw.rect(self.screen, (0, 0, 0), [20, 20, 760, 380], 3)
        self.draw_text("どの わざを わすれさせますか？", 400, 50, self.BLACK, center=True)
        for button in self.learn_move_buttons:
            button.draw(self.screen)