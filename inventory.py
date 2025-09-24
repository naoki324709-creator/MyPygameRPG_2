# inventory.py
from items_data import ITEM_DATABASE

class Inventory:
    """プレイヤーの持ち物を管理するクラス"""
    def __init__(self):
        self.items = {}

    # ★★★ ここを修正 ★★★
    def add_item(self, item_id, count=1, show_message=True):
        """アイテムを追加する"""
        item_data = ITEM_DATABASE.get(item_id)
        if not item_data:
            print(f"エラー: ID '{item_id}' のアイテムは存在しません。")
            return

        if item_id in self.items:
            self.items[item_id]['count'] += count
        else:
            self.items[item_id] = {'data': item_data.copy(), 'count': count}
        
        if show_message:
            print(f"{item_data['name']} を {count}個 手に入れた！")

    def remove_item(self, item_id, count=1):
        """アイテムを消費する"""
        if item_id in self.items:
            self.items[item_id]['count'] -= count
            if self.items[item_id]['count'] <= 0:
                del self.items[item_id]
                return True
        return False

    def get_item_details(self, item_id):
        """アイテムの詳細データを取得する"""
        if item_id in self.items:
            return self.items[item_id]['data']
        return None