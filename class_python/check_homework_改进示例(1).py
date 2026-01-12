# -*- coding: utf-8 -*-
"""
check_homework.py 改进版示例
演示主要改进功能的代码实现
"""

import os
import re
import sys
import pandas as pd
from pathlib import Path
import json
import logging
from datetime import datetime

# ============================================================================
# 改进1：支持多种文件格式
# ============================================================================

def get_supported_extensions():
    """获取支持的文件扩展名列表"""
    return ['.py', '.ipynb', '.txt', '.pdf', '.zip', '.rar', '.docx']

def check_homework_in_folder_v2(folder_path, roster_student_ids, extensions=None):
    """
    检查指定文件夹中的作业文件（改进版）
    
    改进点：
    1. 支持多种文件格式
    2. 记录每个学生提交的具体文件
    3. 返回更详细的信息
    """
    if extensions is None:
        extensions = get_supported_extensions()
    
    folder_name = os.path.basename(folder_path)
    submitted_ids = set()
    submitted_files = {}  # 记录每个学号提交的文件列表
    
    # 查找所有支持格式的文件
    for ext in extensions:
        files = list(Path(folder_path).glob(f"*{ext}"))
        for file in files:
            student_id = extract_student_id_from_filename_v2(file.name)
            if student_id:
                submitted_ids.add(student_id)
                if student_id not in submitted_files:
                    submitted_files[student_id] = []
                submitted_files[student_id].append(file.name)
    
    missing_ids = roster_student_ids - submitted_ids
    
    return submitted_ids, missing_ids, submitted_files


# ============================================================================
# 改进2：增强学号识别能力
# ============================================================================

def extract_student_id_from_filename_v2(filename, patterns=None):
    """
    从文件名中提取学号，支持多种模式（改进版）
    
    改进点：
    1. 支持多种学号格式
    2. 优先级匹配机制
    3. 更高的识别准确率
    
    参数：
        filename: 文件名
        patterns: 自定义匹配模式列表
    
    返回：
        学号字符串或None
    """
    if patterns is None:
        # 默认模式列表（按优先级从高到低排序）
        patterns = [
            r'(\d{9})(?![0-9])',    # 9位数字，后面不跟数字（最常见）
            r'[_-](\d{9})[_-]',     # 被下划线或横线包围的9位数字
            r'^(\d{9})',            # 文件名开头的9位数字
            r'学号[：:_-]?(\d{9})',  # "学号"关键字后的9位数字
            r'ID[：:_-]?(\d{9})',    # "ID"关键字后的9位数字
            r'no[._-]?(\d{9})',     # "no"关键字后的9位数字
        ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            # 如果模式有分组，返回第一个分组
            if match.groups():
                return match.group(1)
            return match.group()
    
    return None


# ============================================================================
# 改进3：配置文件支持
# ============================================================================

def get_default_config():
    """获取默认配置"""
    return {
        "roster_file": "花名册.xlsx",
        "homework_folder_prefix": "学生作业",
        "supported_extensions": [".py", ".ipynb", ".txt", ".pdf"],
        "output_formats": ["txt", "xlsx"],
        "output_directory": "reports",
        "enable_email": False,
        "enable_visualization": True,
        "log_level": "INFO",
        "student_id_patterns": [
            r'(\d{9})(?![0-9])',
            r'[_-](\d{9})[_-]'
        ]
    }

def load_config(config_file='config.json'):
    """
    加载配置文件
    
    改进点：
    1. 外部配置，无需修改代码
    2. 支持JSON格式
    3. 提供默认配置作为备选
    """
    try:
        if not os.path.exists(config_file):
            print(f"配置文件 {config_file} 不存在，使用默认配置")
            return get_default_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"已加载配置文件: {config_file}")
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        print("使用默认配置")
        return get_default_config()

def save_config(config, config_file='config.json'):
    """保存配置文件"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"配置已保存到: {config_file}")
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


# ============================================================================
# 改进4：日志记录系统
# ============================================================================

def setup_logger(log_file=None, log_level='INFO'):
    """
    配置日志系统
    
    改进点：
    1. 持久化日志记录
    2. 支持不同日志级别
    3. 同时输出到文件和控制台
    4. 便于问题追踪和调试
    
    参数：
        log_file: 日志文件路径，None则自动生成
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR）
    """
    if log_file is None:
        # 创建logs目录
        os.makedirs('logs', exist_ok=True)
        log_file = f"logs/check_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 创建logger
    logger = logging.getLogger('homework_checker')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重复添加处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# 改进5：统计分析功能
# ============================================================================

def generate_statistics(all_missing_students, roster_student_ids, student_id_to_name):
    """
    生成详细的统计分析
    
    改进点：
    1. 提供多维度统计数据
    2. 计算各种比率和趋势
    3. 识别问题学生
    
    返回：
        统计信息字典
    """
    stats = {
        'total_students': len(roster_student_ids),
        'total_homeworks': len(all_missing_students),
        'homework_stats': [],
        'student_stats': {},
        'overall_completion_rate': 0.0,
        'problem_students': []  # 未交作业超过50%的学生
    }
    
    # 按作业统计
    for hw_name, missing_ids in all_missing_students.items():
        submitted_count = stats['total_students'] - len(missing_ids)
        completion_rate = (submitted_count / stats['total_students'] * 100) if stats['total_students'] > 0 else 0
        
        stats['homework_stats'].append({
            'name': hw_name,
            'submitted': submitted_count,
            'missing': len(missing_ids),
            'completion_rate': completion_rate
        })
    
    # 按学生统计
    for student_id in roster_student_ids:
        missing_count = sum(1 for missing_ids in all_missing_students.values() 
                          if student_id in missing_ids)
        completion_rate = ((stats['total_homeworks'] - missing_count) / stats['total_homeworks'] * 100) if stats['total_homeworks'] > 0 else 0
        
        stats['student_stats'][student_id] = {
            'name': student_id_to_name.get(student_id, '未知'),
            'submitted': stats['total_homeworks'] - missing_count,
            'missing': missing_count,
            'completion_rate': completion_rate
        }
        
        # 识别问题学生（完成率低于50%）
        if completion_rate < 50 and stats['total_homeworks'] > 0:
            stats['problem_students'].append({
                'student_id': student_id,
                'name': student_id_to_name.get(student_id, '未知'),
                'completion_rate': completion_rate,
                'missing_count': missing_count
            })
    
    # 计算总体完成率
    total_submissions = sum(hw['submitted'] for hw in stats['homework_stats'])
    total_possible = stats['total_students'] * stats['total_homeworks']
    stats['overall_completion_rate'] = (total_submissions / total_possible * 100) if total_possible > 0 else 0
    
    # 按完成率排序问题学生
    stats['problem_students'].sort(key=lambda x: x['completion_rate'])
    
    return stats

def print_statistics_report(stats):
    """打印统计报告"""
    print("\n" + "=" * 80)
    print("作业提交情况统计分析")
    print("=" * 80)
    
    print(f"\n总体情况：")
    print(f"  学生总数: {stats['total_students']}")
    print(f"  作业批次: {stats['total_homeworks']}")
    print(f"  总体完成率: {stats['overall_completion_rate']:.2f}%")
    
    print(f"\n各次作业提交情况：")
    print(f"  {'作业名称':<30} {'已交':<10} {'未交':<10} {'完成率':<10}")
    print("  " + "-" * 70)
    for hw in stats['homework_stats']:
        print(f"  {hw['name']:<30} {hw['submitted']:<10} {hw['missing']:<10} {hw['completion_rate']:.2f}%")
    
    if stats['problem_students']:
        print(f"\n需要关注的学生（完成率<50%）：")
        print(f"  {'学号':<12} {'姓名':<15} {'已交':<10} {'未交':<10} {'完成率':<10}")
        print("  " + "-" * 70)
        for student in stats['problem_students'][:10]:  # 只显示前10个
            submitted = stats['total_homeworks'] - student['missing_count']
            print(f"  {student['student_id']:<12} {student['name']:<15} "
                  f"{submitted:<10} {student['missing_count']:<10} "
                  f"{student['completion_rate']:.2f}%")
    else:
        print(f"\n所有学生完成率都在50%以上，表现良好！")
    
    print("\n" + "=" * 80)


# ============================================================================
# 改进6：生成更详细的报告
# ============================================================================

def generate_detailed_report(all_missing_students, submitted_files_dict, 
                            student_id_to_name, stats, output_file):
    """
    生成详细的分析报告
    
    改进点：
    1. 包含统计分析
    2. 列出具体提交文件
    3. 标注问题学生
    4. 提供改进建议
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("作业检查详细报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # 总体统计
        f.write("一、总体统计\n")
        f.write("-" * 80 + "\n")
        f.write(f"学生总数: {stats['total_students']}\n")
        f.write(f"作业批次: {stats['total_homeworks']}\n")
        f.write(f"总体完成率: {stats['overall_completion_rate']:.2f}%\n\n")
        
        # 各次作业详情
        f.write("二、各次作业提交详情\n")
        f.write("-" * 80 + "\n")
        for hw in stats['homework_stats']:
            f.write(f"\n【{hw['name']}】\n")
            f.write(f"已提交: {hw['submitted']}人, 未提交: {hw['missing']}人, ")
            f.write(f"完成率: {hw['completion_rate']:.2f}%\n")
            
            # 未交名单
            missing_ids = all_missing_students[hw['name']]
            if missing_ids:
                f.write("\n未交名单：\n")
                for student_id in sorted(missing_ids):
                    name = student_id_to_name.get(student_id, '未知')
                    f.write(f"  {student_id} - {name}\n")
        
        # 问题学生分析
        f.write("\n\n三、需要关注的学生\n")
        f.write("-" * 80 + "\n")
        if stats['problem_students']:
            for student in stats['problem_students']:
                f.write(f"\n学号: {student['student_id']}, 姓名: {student['name']}\n")
                f.write(f"完成率: {student['completion_rate']:.2f}%\n")
                f.write(f"已交: {stats['total_homeworks'] - student['missing_count']}次, ")
                f.write(f"未交: {student['missing_count']}次\n")
                
                # 列出未交的具体作业
                missing_hws = []
                for hw_name, missing_ids in all_missing_students.items():
                    if student['student_id'] in missing_ids:
                        missing_hws.append(hw_name)
                if missing_hws:
                    f.write(f"未交作业: {', '.join(missing_hws)}\n")
        else:
            f.write("所有学生表现良好！\n")
        
        # 改进建议
        f.write("\n\n四、改进建议\n")
        f.write("-" * 80 + "\n")
        if stats['overall_completion_rate'] < 80:
            f.write("1. 总体完成率较低，建议：\n")
            f.write("   - 加强作业重要性的宣传\n")
            f.write("   - 适当延长提交时间\n")
            f.write("   - 提供作业辅导答疑\n")
        if stats['problem_students']:
            f.write("2. 存在问题学生，建议：\n")
            f.write("   - 单独沟通了解情况\n")
            f.write("   - 提供补交机会\n")
            f.write("   - 必要时联系家长或辅导员\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")


# ============================================================================
# 示例：如何使用改进功能
# ============================================================================

def demo_improved_features():
    """演示改进功能的使用"""
    print("=" * 80)
    print("check_homework.py 改进功能演示")
    print("=" * 80)
    
    # 1. 配置文件示例
    print("\n1. 配置文件功能")
    print("-" * 40)
    config = get_default_config()
    save_config(config, 'config_example.json')
    loaded_config = load_config('config_example.json')
    print(f"配置项: {list(loaded_config.keys())}")
    
    # 2. 日志系统示例
    print("\n2. 日志系统功能")
    print("-" * 40)
    logger = setup_logger(log_level='INFO')
    logger.info("程序开始运行")
    logger.debug("这是调试信息（不会显示在控制台）")
    logger.warning("这是警告信息")
    
    # 3. 增强的学号识别
    print("\n3. 增强的学号识别")
    print("-" * 40)
    test_filenames = [
        "852203108_谭明雨_作业1.py",
        "作业_852403102_李咏.ipynb",
        "学号:852203205_作业.txt",
        "ID_852403204.py",
        "python-852203211.zip"
    ]
    
    for filename in test_filenames:
        student_id = extract_student_id_from_filename_v2(filename)
        print(f"文件: {filename:40} -> 学号: {student_id}")
    
    # 4. 统计分析示例
    print("\n4. 统计分析功能")
    print("-" * 40)
    
    # 模拟数据
    roster_student_ids = {f"85220310{i}" for i in range(8)}
    student_id_to_name = {f"85220310{i}": f"学生{i}" for i in range(8)}
    
    all_missing_students = {
        '学生作业1': {'852203100', '852203101'},
        '学生作业2': {'852203100'},
        '学生作业3': set()
    }
    
    stats = generate_statistics(all_missing_students, roster_student_ids, student_id_to_name)
    print_statistics_report(stats)
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    # 运行演示
    demo_improved_features()
    
    print("\n\n使用说明：")
    print("1. 这个文件展示了主要的改进功能")
    print("2. 可以直接运行查看效果")
    print("3. 可以将这些改进整合到原程序中")
    print("4. 详细说明请查看 'Python期末报告_完整版.txt'")
