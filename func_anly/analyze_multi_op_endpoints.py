#!/usr/bin/env python3
"""
统计CSV文件中"多操作端点数量"的平均数、中位数和最大数
"""

import csv
import statistics
from pathlib import Path


def analyze_multi_op_endpoints(csv_file_path):
    """
    分析CSV文件中"多操作端点数量"的统计信息

    Args:
        csv_file_path (str): CSV文件路径

    Returns:
        dict: 包含统计结果的字典
    """
    multi_op_counts = []

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # 读取表头
            headers = next(reader)
            print(f"CSV文件列名: {headers}")

            # 找到"多操作端点数量"列的索引
            target_column = "多操作端点数量"
            if target_column in headers:
                column_index = headers.index(target_column)
                print(f"找到目标列 '{target_column}'，索引: {column_index}")
            else:
                # 如果找不到中文列名，尝试使用索引（第6列，索引5）
                column_index = 5
                print(f"未找到列名 '{target_column}'，使用索引 {column_index}")

            # 读取数据
            row_count = 0
            for row in reader:
                row_count += 1
                if len(row) > column_index:
                    try:
                        value = float(row[column_index])
                        multi_op_counts.append(value)
                    except (ValueError, IndexError):
                        print(f"第 {row_count} 行数据格式错误: {row[column_index] if column_index < len(row) else '索引超出范围'}")
                else:
                    print(f"第 {row_count} 行列数不足，跳过")

            print(f"成功读取 {len(multi_op_counts)} 条有效数据")

            if not multi_op_counts:
                print("警告: 没有找到有效数据")
                return None

            # 计算统计信息
            avg_value = statistics.mean(multi_op_counts)
            median_value = statistics.median(multi_op_counts)
            max_value = max(multi_op_counts)
            min_value = min(multi_op_counts)
            total_count = len(multi_op_counts)

            # 计算标准差
            if len(multi_op_counts) > 1:
                std_dev = statistics.stdev(multi_op_counts)
            else:
                std_dev = 0

            # 计算总和
            sum_value = sum(multi_op_counts)

            # 计算百分位数
            if len(multi_op_counts) >= 5:
                q1 = statistics.quantiles(multi_op_counts, n=4)[0]  # 25%分位数
                q3 = statistics.quantiles(multi_op_counts, n=4)[2]  # 75%分位数
            else:
                q1 = median_value
                q3 = median_value

            return {
                'average': avg_value,
                'median': median_value,
                'max': max_value,
                'min': min_value,
                'std_dev': std_dev,
                'sum': sum_value,
                'count': total_count,
                'q1': q1,
                'q3': q3,
                'data': multi_op_counts
            }

    except FileNotFoundError:
        print(f"错误: 找不到文件 {csv_file_path}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def print_statistics(stats):
    """
    打印统计结果

    Args:
        stats (dict): 统计结果字典
    """
    if not stats:
        print("没有可用的统计结果")
        return

    print("\n" + "="*60)
    print("多操作端点数量统计结果")
    print("="*60)
    print(f"数据总数: {stats['count']}")
    print(f"总和: {stats['sum']:.2f}")
    print(f"平均数: {stats['average']:.4f}")
    print(f"中位数: {stats['median']:.4f}")
    print(f"最大值: {stats['max']:.4f}")
    print(f"最小值: {stats['min']:.4f}")
    print(f"标准差: {stats['std_dev']:.4f}")
    print(f"25%分位数 (Q1): {stats['q1']:.4f}")
    print(f"75%分位数 (Q3): {stats['q3']:.4f}")
    print("="*60)

    # 打印数据分布摘要
    if stats['data']:
        print("\n数据分布摘要:")
        sorted_data = sorted(stats['data'])
        print(f"前5个最小值: {sorted_data[:5]}")
        print(f"前5个最大值: {sorted_data[-5:]}")

        # 统计不同范围的数据
        zero_count = sum(1 for x in stats['data'] if x == 0)
        small_count = sum(1 for x in stats['data'] if 0 < x <= 5)
        medium_count = sum(1 for x in stats['data'] if 5 < x <= 20)
        large_count = sum(1 for x in stats['data'] if x > 20)

        print(f"\n数据分布:")
        print(f"  值为0的项目数: {zero_count} ({zero_count/stats['count']*100:.1f}%)")
        print(f"  1-5之间的项目数: {small_count} ({small_count/stats['count']*100:.1f}%)")
        print(f"  6-20之间的项目数: {medium_count} ({medium_count/stats['count']*100:.1f}%)")
        print(f"  大于20的项目数: {large_count} ({large_count/stats['count']*100:.1f}%)")


def save_statistics_to_file(stats, output_file):
    """
    将统计结果保存到文件

    Args:
        stats (dict): 统计结果字典
        output_file (str): 输出文件路径
    """
    if not stats:
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("多操作端点数量统计结果\n")
            f.write("="*60 + "\n")
            f.write(f"数据总数: {stats['count']}\n")
            f.write(f"总和: {stats['sum']:.2f}\n")
            f.write(f"平均数: {stats['average']:.4f}\n")
            f.write(f"中位数: {stats['median']:.4f}\n")
            f.write(f"最大值: {stats['max']:.4f}\n")
            f.write(f"最小值: {stats['min']:.4f}\n")
            f.write(f"标准差: {stats['std_dev']:.4f}\n")
            f.write(f"25%分位数 (Q1): {stats['q1']:.4f}\n")
            f.write(f"75%分位数 (Q3): {stats['q3']:.4f}\n")
            f.write("="*60 + "\n")

            # 保存原始数据
            f.write("\n原始数据:\n")
            for i, value in enumerate(stats['data'], 1):
                f.write(f"{i}: {value}\n")

        print(f"\n统计结果已保存到: {output_file}")

    except Exception as e:
        print(f"保存文件时发生错误: {e}")


def main():
    """主函数"""
    # CSV文件路径
    csv_file = "result/func_anly_result_web_v5.csv"

    # 检查文件是否存在
    if not Path(csv_file).exists():
        print(f"错误: 文件 {csv_file} 不存在")
        return

    print(f"正在分析文件: {csv_file}")

    # 分析数据
    stats = analyze_multi_op_endpoints(csv_file)

    if stats:
        # 打印统计结果
        print_statistics(stats)

        # 保存结果到文件
        output_file = "result/multi_op_endpoints_statistics.txt"
        save_statistics_to_file(stats, output_file)

        # 生成简化的CSV摘要
        try:
            summary_csv = "result/multi_op_endpoints_summary.csv"
            with open(summary_csv, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["统计项", "值"])
                writer.writerow(["数据总数", stats['count']])
                writer.writerow(["总和", f"{stats['sum']:.2f}"])
                writer.writerow(["平均数", f"{stats['average']:.4f}"])
                writer.writerow(["中位数", f"{stats['median']:.4f}"])
                writer.writerow(["最大值", f"{stats['max']:.4f}"])
                writer.writerow(["最小值", f"{stats['min']:.4f}"])
                writer.writerow(["标准差", f"{stats['std_dev']:.4f}"])
                writer.writerow(["25%分位数", f"{stats['q1']:.4f}"])
                writer.writerow(["75%分位数", f"{stats['q3']:.4f}"])

            print(f"摘要CSV已保存到: {summary_csv}")
        except Exception as e:
            print(f"生成摘要CSV时发生错误: {e}")


if __name__ == "__main__":
    main()