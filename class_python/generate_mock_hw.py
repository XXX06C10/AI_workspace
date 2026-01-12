import pandas as pd
import os

# 1. 扫描花名册并生成假作业
try:
    path = 'd:/AI_workspace/class_python/花名册.xlsx'
    # 先尝试找到表头所在的行
    df_preview = pd.read_excel(path, header=None)
    header_row = 0
    for i, row in df_preview.iterrows():
        if any('学号' in str(val) for val in row.values):
            header_row = i
            break
            
    df = pd.read_excel(path, header=header_row)
    df.columns = [str(c).strip() for c in df.columns]
    
    # 模糊匹配学号列
    id_col = next((c for c in df.columns if "学号" in c), None)
    
    if id_col:
        ids = df[id_col].dropna().astype(str).tolist()
        
        hw_dir = 'd:/AI_workspace/class_python/mock_homework'
        os.makedirs(hw_dir, exist_ok=True)
        
        # 随机生成一些作业 (选前10个，生成前7个，留3个没交的)
        count = 0
        for sid in ids[:10]:
            if count < 7:
                file_path = os.path.join(hw_dir, f"{sid}_期末作业.py")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("# Mock homework file")
                print(f"已生成作业文件: {sid}_期末作业.py")
                count += 1
        
        print(f"\n✅ 模拟作业已成功生成在: {hw_dir}")
    else:
        print("❌ 未在花名册中找到'学号'列")
except Exception as e:
    print(f"生成过程出错: {e}")
