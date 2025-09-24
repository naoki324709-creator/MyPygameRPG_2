# inventory.py

from items_data import ITEM_DATABASE

class Inventory:
    """プレイヤーの持ち物を管理するクラス"""
    def __init__(self):
        # {"item_id": {"data": item_data, "count": count}} の形式
        self.items = {} 
        # 本家を参考にポケットを定義
        self.pockets = ["どうぐ", "ボール", "わざマシン", "きのみ", "たいせつなもの"]

    def add_item(self, item_id, count=1, show_message=True):
        """アイテムを追加する"""
        item_data = ITEM_DATABASE.get(item_id)
        if not item_data:
            print(f"エラー: ID '{item_id}' のアイテムは存在しません。")
            return

        if item_id in self.items:
            self.items[item_id]['count'] += count
        else:
            # アイテムデータをコピーして所持数（count）を追加
            self.items[item_id] = {'data': item_data.copy(), 'count': count}
        
        if show_message:
            # ★★★ ここを修正 ★★★
            # item_dataから直接'name'を取得する
            print(f"{item_data['name']} を {count}個 手に入れた！")

    def remove_item(self, item_id, count=1):
        """アイテムを消費する"""
        if item_id in self.items:
            self.items[item_id]['count'] -= count
            if self.items[item_id]['count'] <= 0:
                del self.items[item_id]

    def get_items_by_pocket(self, pocket_name):
        """指定されたポケットのアイテムリストを返す"""
        return {
            item_id: item_info for item_id, item_info in self.items.items()
            if item_info['data']['pocket'] == pocket_name
        }

    def get_items_by_battle_pocket(self, battle_pocket_name):
        """戦闘中に指定されたポケットのアイテムリストを返す"""
        print("--- デバッグ情報 ---")
        print(f"探しているポケット: {battle_pocket_name}")
        print(f"現在の所持アイテム一覧: {self.items}")
        items_found = {
            item_id: item_info for item_id, item_info in self.items.items()
            if 'data' in item_info and item_info['data'].get('battle_pocket') == battle_pocket_name
        }

        print(f"見つかったアイテム: {items_found}")
        print("--------------------")

        return items_found

    def get_item_details(self, item_id):
        """アイテムの詳細データを取得する"""
        if item_id in self.items:
            return self.items[item_id]['data']
        return None