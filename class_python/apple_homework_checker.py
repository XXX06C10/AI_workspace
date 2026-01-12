import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px
from datetime import datetime

# ==========================================
# 页面配置 (Apple Style Aesthetics)
# ==========================================
st.set_page_config(
    page_title="Homework Checker | 简约作业助手",
    page_icon="🍎",
    layout="wide",
)

# 自定义 CSS 注入：打造苹果风
st.markdown("""
<style>
    /* 字体与背景 */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@100;300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #FBFBFD;
    }
    
    /* 卡片容器 */
    .stCard {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        margin-bottom: 25px;
    }
    
    /* 标题样式 */
    h1 {
        font-weight: 600 !important;
        letter-spacing: -0.05em !important;
        color: #1D1D1F;
    }
    
    /* 按钮美化 */
    .stButton>button {
        border-radius: 12px;
        border: none;
        background: #0071E3;
        color: white;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #0077ED;
        box-shadow: 0 4px 15px rgba(0, 113, 227, 0.3);
        transform: translateY(-1px);
    }
    
    /* 指标卡片 */
    [data-testid="stMetricValue"] {
        font-weight: 600;
        color: #1D1D1F;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 核心逻辑 (基于原脚本改进)
# ==========================================

def extract_student_id_from_filename(filename):
    """从文件名提取学号 (Regex 逻辑)"""
    patterns = [
        r'(\d{9})(?![0-9])',    # 9位数字
        r'[_-](\d{9})[_-]',     # 被包裹的9位数字
        r'^(\d{9})',            # 开头的9位数字
    ]
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group()
    return None

# ==========================================
# 标题区
# ==========================================
st.title("🍎 作业提交助手")
st.caption("基于高级 AI 引擎的苹果风格自动化办公工具")

# ==========================================
# 第一阶段：上传与配置 (卡片布局)
# ==========================================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📄 第一步：上传花名册")
    roster_file = st.file_uploader("拖入花名册 Excel 文件", type=["xlsx", "xls"], key="roster")
    
    if roster_file:
        try:
            # 升级逻辑：自动寻找表头
            # 先预览前10行，寻找“学号”关键字
            df_preview = pd.read_excel(roster_file, header=None, nrows=10)
            header_idx = 0
            found = False
            for i, row in df_preview.iterrows():
                if any("学号" in str(val) for val in row.values):
                    header_idx = i
                    found = True
                    break
            
            if not found:
                st.warning("⚠️ 未能自动识别表头，尝试从第3行读取...")
                header_idx = 2

            df_roster_raw = pd.read_excel(roster_file, header=header_idx)
            # 自动清洗列名：去空格，转字符串
            df_roster_raw.columns = [str(c).strip() for c in df_roster_raw.columns]
            
            # 定位核心列：支持“学号”、“学生学号”等模糊匹配
            id_col = next((c for c in df_roster_raw.columns if "学号" in c), None)
            name_col = next((c for c in df_roster_raw.columns if "姓名" in c), None)
            
            if id_col and name_col:
                df_roster = df_roster_raw[[id_col, name_col]].dropna()
                df_roster.columns = ['学号', '姓名'] 
                df_roster['学号'] = df_roster['学号'].astype(str)
                st.success(f"✅ 已加载 {len(df_roster)} 名学生信息")
            else:
                st.error("❌ 无法识别到'学号'或'姓名'列。")
        except Exception as e:
            st.error(f"解析失败: {e}")

with col2:
    st.subheader("📦 第二步：上传作业")
    hw_files = st.file_uploader("拖入作业文件", type=[".py", ".ipynb", ".txt", ".zip", ".rar", ".pdf", ".docx"], accept_multiple_files=True)
    
    if hw_files:
        st.info(f"📁 已识别到 {len(hw_files)} 个待检文件")

# ==========================================
# 核心处理与结果
# ==========================================

if roster_file and hw_files:
    if st.button("开始闪电识别 ⚡️"):
        with st.spinner("正在运用 AI 逻辑清点作业..."):
            
            # 初始化
            roster_ids = set(df_roster['学号'].tolist())
            submitted_info = {} # 学号 -> 文件名列表
            
            # 识别过程
            for f in hw_files:
                sid = extract_student_id_from_filename(f.name)
                if sid:
                    if sid not in submitted_info:
                        submitted_info[sid] = []
                    submitted_info[sid].append(f.name)
            
            submitted_ids = set(submitted_info.keys())
            missing_ids = roster_ids - submitted_ids
            dupe_ids = {sid: names for sid, names in submitted_info.items() if len(names) > 1}
            
            # --- 数据准备 ---
            total = len(roster_ids)
            submitted_count = len(submitted_ids)
            missing_count = len(missing_ids)
            rate = (submitted_count / total) if total > 0 else 0
            
            # ==========================================
            # 结果可视化 (苹果风格仪表盘)
            # ==========================================
            st.divider()
            
            # 指标卡
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("应交人数", f"{total}")
            m2.metric("实交人数", f"{submitted_count}")
            m3.metric("未交人数", f"{missing_count}", delta=-missing_count, delta_color="inverse")
            m4.metric("完成率", f"{rate:.1%}")
            
            # 进度条
            st.progress(rate)
            
            # 结果卡片
            c1, c2 = st.columns([1, 1])
            
            with c1:
                # 饼图
                fig = px.pie(
                    values=[submitted_count, missing_count], 
                    names=['已提交', '未提交'],
                    color_discrete_sequence=['#34C759', '#FF3B30'], # Apple Colors
                    hole=0.6,
                    title="提交比例图"
                )
                fig.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                # 展示未交名单
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.subheader("🚩 未交名单")
                if missing_ids:
                    missing_df = df_roster[df_roster['学号'].isin(missing_ids)]
                    st.dataframe(missing_df, hide_index=True, use_container_width=True)
                else:
                    st.balloons()
                    st.success("完美！全班已全部提交。")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 详细清单
            with st.expander("🔍 查看已交详细列表档案"):
                detail_list = []
                for _, row in df_roster.iterrows():
                    sid = row['学号']
                    status = "✅ 已交" if sid in submitted_ids else "❌ 未交"
                    files = ", ".join(submitted_info.get(sid, []))
                    detail_list.append({
                        "学号": sid,
                        "姓名": row['姓名'],
                        "状态": status,
                        "提交文件名": files
                    })
                st.table(pd.DataFrame(detail_list))

            # 导出报告
            report_df = pd.DataFrame(detail_list)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                report_df.to_excel(writer, index=False, sheet_name='提交分析报告')
            
            st.download_button(
                label="📥 下载精美分析报告 (Excel)",
                data=output.getvalue(),
                file_name=f"作业分析报告_{datetime.now().strftime('%m%d_%H%M')}.xlsx",
                mime="application/vnd.ms-excel"
            )

else:
    # 欢迎页
    st.info("👋 请在上方上传花名册和作业文件以开始分析。")

# 页脚
st.markdown("""
<div style='text-align: center; color: #86868B; margin-top: 50px; font-size: 0.8em;'>
    Design Inspired by Apple | Powered by Gemini 3.0 Agentic Coding
</div>
""", unsafe_allow_html=True)
