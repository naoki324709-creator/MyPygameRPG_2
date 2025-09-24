# exp_data.py

def get_exp_for_level(level, growth_rate="medium_fast"):
    """
    指定されたレベルと成長タイプに基づき、
    レベルアップに必要な総経験値を返す。
    """
    if level <= 1:
        return 0
        
    n = level

    if growth_rate == "fast":
        return (4 * n**3) // 5
    
    elif growth_rate == "medium_fast":
        return int(n**3)
        
    elif growth_rate == "medium_slow":
        return (6 * n**3) // 5 - 15 * n**2 + 100 * n - 140
        
    elif growth_rate == "slow":
        return (5 * n**3) // 4
        
    # 「すごく早い」「すごく遅い」は計算式が特殊
    elif growth_rate == "erratic":
        if n <= 50:
            return (n**3 * (100 - n)) // 50
        elif n <= 68:
            return (n**3 * (150 - n)) // 100
        elif n <= 98:
            return (n**3 * (1911 - 10*n) // 3) // 500
        else:
            return (n**3 * (160 - n)) // 100
            
    elif growth_rate == "fluctuating":
        if n <= 15:
            return (n**3 * ((n+1)//3 + 24)) // 50
        elif n <= 36:
            return (n**3 * (n + 14)) // 50
        else:
            return (n**3 * (n//2 + 32)) // 50
            
    # 不明な成長タイプの場合は "普通" を使う
    else:
        return int(n**3)
    
# # exp_data.py に直接テスト用コードを追加
# if __name__ == "__main__":
#     print(f"fast レベル8: {get_exp_for_level(8, 'fast')}")
#     print(f"medium_slow レベル8: {get_exp_for_level(8, 'medium_slow')}")
#     print(f"medium_fast レベル8: {get_exp_for_level(8, 'medium_fast')}")
#     print(f"slow レベル8: {get_exp_for_level(8, 'slow')}")
#     print(f"erratic レベル8: {get_exp_for_level(8, 'erratic')}")
#     print(f"fluctuating レベル8: {get_exp_for_level(8, 'fluctuating')}")