# battle.py
# 機能：戦闘に関する全てのロジックを管理する

import random
from monster import Monster
from types_data import get_effectiveness
from stats_data import STAGE_MULTIPLIERS

# 状態異常の内部名（英語）と表示名（日本語）の対応表
STATUS_NAME_MAP = {
    "poison": "どく", "paralysis": "まひ", "toxic": "もうどく",
    "burn": "やけど", "sleep": "ねむり", "freeze": "こおり"
}

# ステータスの内部名（英語）と表示名（日本語）の対応表
STAT_NAME_MAP = {
    "attack": "こうげき", "defense": "ぼうぎょ", "sp_attack": "とくこう",
    "sp_defense": "とくぼう", "speed": "すばやさ"
}

class Battle:
    """
    1回の戦闘を管理するクラス。
    プレイヤーと敵のモンスターオブジェクトを受け取り、ターンの進行を制御する。
    """
    def __init__(self, player_monster, enemy_monster):
        """戦闘の初期化。参加するモンスターとターン数を設定する。"""
        self.player_monster = player_monster
        self.enemy_monster = enemy_monster
        self.turn = 1
        self.message_log = [] # ← メッセージを溜めるリスト
    
    def _log_message(self, message):
        """メッセージをログに追加する。"""
        if message:
            # メッセージがリストの場合（レベルアップ時など）は連結する
            if isinstance(message, list):
                self.message_log.extend(message)
            else:
                self.message_log.append(message)

    def _calculate_damage(self, attacker, defender, move):
        """
        ダメージを計算する関数。急所、ランク、タイプ相性などを考慮する。
        """
        # --- 1. 急所(クリティカルヒット)の判定 ---
        is_critical = random.random() < (1 / 24)  # 約4.17%の確率
        critical_multiplier = 1.5 if is_critical else 1.0
        if is_critical:
            self._log_message("きゅうしょに あたった！")

        # --- 2. 技のカテゴリに応じたステータス計算 ---
        if move['category'] == 'physical':
            # a. 攻撃側のステータスを決定
            attack_stage = attacker.stat_stages['attack']
            # 急所の場合、攻撃側のマイナスランクは無視する
            if is_critical and attack_stage < 0:
                attack_stage = 0
            attack_multiplier = STAGE_MULTIPLIERS[attack_stage]
            attack_stat = attacker.attack * attack_multiplier
            # 急所の場合、やけどの攻撃半減効果も無視する
            if attacker.status_condition == 'burn' and not is_critical:
                attack_stat /= 2
            
            # b. 防御側のステータスを決定
            defense_stage = defender.stat_stages['defense']
            # 急所の場合、防御側のプラスランクは無視する
            if is_critical and defense_stage > 0:
                defense_stage = 0
            defense_multiplier = STAGE_MULTIPLIERS[defense_stage]
            defense_stat = defender.defense * defense_multiplier

        elif move['category'] == 'special':
            # 特殊技も同様に、急所の場合は有利な補正を無視する
            sp_attack_stage = attacker.stat_stages['sp_attack']
            if is_critical and sp_attack_stage < 0:
                sp_attack_stage = 0
            sp_attack_multiplier = STAGE_MULTIPLIERS[sp_attack_stage]
            attack_stat = attacker.sp_attack * sp_attack_multiplier

            sp_defense_stage = defender.stat_stages['sp_defense']
            if is_critical and sp_defense_stage > 0:
                sp_defense_stage = 0
            sp_defense_multiplier = STAGE_MULTIPLIERS[sp_defense_stage]
            defense_stat = defender.sp_defense * sp_defense_multiplier
        else:
            return 0
        
        # --- 3. タイプ一致ボーナス（STAB）の判定 ---
        stab_multiplier = 1.0 # デフォルトは1.0倍
        if move['type'] in attacker.types:
            stab_multiplier = 1.5 # タイプが一致すれば1.5倍

        # 4. タイプ相性の倍率を計算
        attack_type = move['type']
        effectiveness_total = 1.0
        for defense_type in defender.types:
            effectiveness_total *= get_effectiveness(attack_type, defense_type)

        # 5. ポケモンのダメージ計算式（簡略版）に基づいてダメージを算出
        power = move['power']
        level = attacker.level
        damage = int((((level * 2 / 5 + 2) * power * (attack_stat / defense_stat)) / 50) + 2)
        final_damage = int(damage * stab_multiplier * effectiveness_total * critical_multiplier)
        
        # 6. 相性メッセージの表示
        if effectiveness_total > 1.0: self._log_message("こうかは ばつぐんだ！")
        elif 0 < effectiveness_total < 1.0: self._log_message("こうかは いまひとつの ようだ…")
        elif effectiveness_total == 0.0: self._log_message("こうかが ない みたいだ…")
        
        return max(1, final_damage) # 最低でも1ダメージは保証

    def _apply_status_effect(self, target, move):
        """技の追加効果（状態異常）を適用する関数。"""
        if not move.get("effect"): return

        if random.random() < move["effect"]["chance"]:
            effect_type = move["effect"]["type"]

            # 【修正点1】すでに同じ状態異常の場合、メッセージを出さずに終了
            if target.status_condition == effect_type:
                return

            if target.status_condition is None:
                # タイプによる無効化をチェック
                if effect_type == "paralysis" and "electric" in target.types:
                    if move['power'] == 0: self._log_message(f"{target.name} には こうかがないようだ…")
                    return
                # (他の無効化チェックも同様)
                # ...
                
                # 状態異常を適用
                target.status_condition = effect_type
                if effect_type == "sleep": target.sleep_counter = random.randint(1, 3)
                elif effect_type == "toxic": target.toxic_counter = 1
                
                status_name = STATUS_NAME_MAP.get(effect_type, effect_type)
                self._log_message(f"{target.name} は {status_name} 状態になった！")
            else:
                # すでに別の状態異常だった場合のメッセージ
                existing_status_name = STATUS_NAME_MAP.get(target.status_condition)
                self._log_message(f"{target.name} は すでに {existing_status_name} 状態なので、効果がなかった！")

    def _handle_end_of_turn_status(self, monster):
        """ターン終了時に発生する状態異常ダメージなどを処理する。"""
        if monster.status_condition == "poison":
            damage = monster.max_hp // 8
            self._log_message(f"{monster.name} は どくのダメージを受けている！")
            monster.take_damage(damage)
        elif monster.status_condition == "toxic":
            damage = (monster.max_hp // 16) * monster.toxic_counter
            self._log_message(f"{monster.name} は もうどくのダメージが きざみこまれていく！")
            monster.take_damage(damage)
            monster.toxic_counter += 1
        elif monster.status_condition == "burn":
            damage = monster.max_hp // 16
            self._log_message(f"{monster.name} は やけどのダメージを受けている！")
            monster.take_damage(damage)

    def _handle_status_move(self, user, target, move):
        """へんかわざの効果を処理する専用の関数。"""
        if not move.get("effect"): return
        
        effect = move["effect"]
        effect_type = effect.get("type")

        if effect_type == "stat_change":
            stat = effect["stat"]
            stages = effect["stages"]
            current_stage = user.stat_stages[stat]
            stat_name_jp = STAT_NAME_MAP.get(stat, stat)
            
            if stages > 0: # 能力を上げる効果
                if current_stage == 6: self._log_message(f"{user.name} の {stat_name_jp}は もう これいじょう あがらない！")
                else:
                    user.stat_stages[stat] = min(6, current_stage + stages)
                    self._log_message(f"{user.name} の {stat_name_jp} が ぐーんと あがった！")
            else: # 能力を下げる効果
                if current_stage == -6: self._log_message(f"{user.name} の {stat_name_jp}は もう これいじょう さがらない！")
                else:
                    user.stat_stages[stat] = max(-6, current_stage + stages)
                    self._log_message(f"{user.name} の {stat_name_jp} が がくっと さがった！")
        else: # 状態異常をかける効果
            self._apply_status_effect(target, move)

    def switch_player_monster(self, new_monster):
        """プレイヤーの戦闘モンスターを交代させる"""
        self.player_monster = new_monster
        # 交代して出てきたポケモンの能力ランクはリセットされる
        for stat in self.player_monster.stat_stages:
            self.player_monster.stat_stages[stat] = 0
            return f"\nゆけっ！ {self.player_monster.name}！"
    
    def _award_exp(self):
        """戦闘に参加したプレイヤーのポケモンに経験値を与える。"""
        # 経験値の計算式（簡略版）
        exp_yield = self.enemy_monster.level * 15
        
        # 経験値を獲得し、メッセージを受け取る
        messages = self.player_monster.gain_exp(exp_yield)
        return messages

    def execute_turn(self, player_move):
        """
        1ターン分の戦闘の流れを管理・実行する。
        この関数は勝敗判定を行わず、単純に1ターン分の処理を進めるだけ。
        """
        self.message_log.clear() # ターン開始時にログをリセット
        print(f"\n--- ターン {self.turn} ---")

        # 1. すばやさを比較して行動順を決定
        player_speed = self.player_monster.speed
        if self.player_monster.status_condition == "paralysis": player_speed /= 2
        enemy_speed = self.enemy_monster.speed
        if self.enemy_monster.status_condition == "paralysis": enemy_speed /= 2
        player_goes_first = player_speed >= enemy_speed
        
        enemy_move = random.choice(self.enemy_monster.moves)

        def attack(attacker, defender, move):
            """1体のモンスターが1回の攻撃を行う処理。"""
            # 行動開始前の状態異常チェック（こおり、ねむり、まひ）
            if attacker.status_condition == "freeze":
                if random.random() < 0.2:
                    self._log_message(f"{attacker.name} の こおりが とけた！")
                    attacker.status_condition = None
                else:
                    self._log_message(f"{attacker.name} は こおってて うごけない！")
                    return # 攻撃失敗
            #if attacker.status_condition == "sleep":
                if attacker.sleep_counter > 0:
                    self._log_message(f"{attacker.name} は ぐうぐう ねむっている！")
                    attacker.sleep_counter -= 1 # 睡眠ターンを1減らす
                    return # 攻撃失敗
                else:
                    self._log_message(f"{attacker.name} は めを さました！")
                    attacker.status_condition = None # ねむり状態を解除
            
            if attacker.status_condition == "paralysis":
                if random.random() < 0.25:
                    self._log_message(f"{attacker.name} は からだがしびれて うごけない！")
                    return # 攻撃失敗
            
            self._log_message(f"{attacker.name} の {move['name']}！")

            # 命中判定を全ての技に適用
            if 'accuracy' in move and random.random() > move['accuracy']:
                self._log_message("しかし こうげきは はずれた！")
                return # 攻撃失敗

            # 技のカテゴリに応じて処理を分岐
            if move['category'] in ['physical', 'special']:
                damage = self._calculate_damage(attacker, defender, move)
                msg = defender.take_damage(damage) # メッセージを受け取る
                self._log_message(msg) # ログに追加
                defender.take_damage(damage)
                if defender.status_condition == "freeze" and move['type'] == 'fire':
                    self._log_message(f"{defender.name} の こおりが とけた！")
                    defender.status_condition = None
                self._apply_status_effect(defender, move)
            elif move['category'] == 'status':
                target = attacker if move["effect"].get("target") == "self" else defender
                self._handle_status_move(attacker, target, move)
            return defender.is_fainted()

        # 2. 行動順に沿って攻撃処理を実行
        attacker_1, defender_1, move_1 = (self.player_monster, self.enemy_monster, player_move) if player_goes_first else (self.enemy_monster, self.player_monster, enemy_move)
        attacker_2, defender_2, move_2 = (self.enemy_monster, self.player_monster, enemy_move) if player_goes_first else (self.player_monster, self.enemy_monster, player_move)
        
        if player_goes_first: print("(プレイヤーが先手！)")
        else: print("(あいてが先手！)")
        
        # 1体目の攻撃
        if attack(attacker_1, defender_1, move_1):
            if defender_1 == self.enemy_monster: # 敵が倒れた場合
                exp_messages = self._award_exp()
                # ここでexp_messagesをmain.pyに渡す必要があるが、
                # まずはprintで表示して動作確認
                for msg in exp_messages:
                    self._log_message(msg)
        

        # もし1体目の攻撃で相手が倒れたら、2体目の攻撃は行わない
        elif not defender_1.is_fainted():
            if attack(attacker_2, defender_2, move_2):
                # ▼▼▼ 変更点 ▼▼▼
                if defender_2 == self.enemy_monster: # 敵が倒れた場合
                    exp_messages = self._award_exp()
                    for msg in exp_messages:
                        self._log_message(msg)

        # 3. ターン終了時の状態異常ダメージなどを処理
        # どちらかのポケモンが倒れていない場合のみ実行
        if not self.player_monster.is_fainted() and not self.enemy_monster.is_fainted():
            print("\n-ターン終了時-")
            self._handle_end_of_turn_status(self.player_monster)
            # プレイヤーが毒ダメージで倒れた場合、敵の処理は行わない
            if not self.player_monster.is_fainted():
                self._handle_end_of_turn_status(self.enemy_monster)
        
        self.turn += 1
        return self.message_log

    def is_battle_over(self):
        """戦闘が終了したかどうかを判定する。（現在この関数は未使用）"""
        return self.player_monster.is_fainted() or self.enemy_monster.is_fainted()