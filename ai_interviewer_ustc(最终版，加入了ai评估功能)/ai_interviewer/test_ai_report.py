# -*- coding: utf-8 -*-
"""
测试 ai_report 模块：使用模拟对话历史验证报告生成功能。
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent))

from modules.ai_report import ai_report, ai_report_stream

# ==================== 模拟面试对话历史 ====================
MOCK_HISTORY = [
    {"role": "assistant", "content": "你好，欢迎参加今天的技术面试。请先简单做一下自我介绍吧。"},
    {"role": "user", "content": "面试官好，我叫张三，本科就读于某大学计算机科学与技术专业，目前大四。在校期间主要学习了数据结构、操作系统、计算机网络等课程，做过一个基于 Spring Boot 的在线商城项目，也参加过 ACM 校赛拿了三等奖。"},
    {"role": "assistant", "content": "不错，你提到了数据结构。那我先问你一个基础问题：请介绍一下哈希表的原理，以及如何处理哈希冲突？"},
    {"role": "user", "content": "哈希表是通过哈希函数把 key 映射到数组下标来实现 O(1) 查找的数据结构。哈希冲突的处理方法主要有两种：一种是链地址法，就是在每个桶后面挂一个链表，冲突的元素追加到链表里；另一种是开放寻址法，发生冲突时往后探测空位，比如线性探测、二次探测。Java 的 HashMap 用的是链地址法，在链表长度超过 8 时会转成红黑树来优化查找性能。"},
    {"role": "assistant", "content": "回答得很好。那你能说说 TCP 三次握手的过程吗？为什么不是两次？"},
    {"role": "user", "content": "TCP 三次握手的流程是：客户端发 SYN 包，服务端收到后回 SYN+ACK，客户端再发 ACK 确认，连接就建立了。不能用两次握手，是因为如果只有两次，假如客户端的一个旧的 SYN 延迟到达了服务端，服务端会认为是新连接并分配资源，但客户端其实不会响应，这样就浪费了服务端资源。三次握手可以确保双方都确认彼此的收发能力正常。"},
    {"role": "assistant", "content": "很好。再深入一点，你了解 TCP 的拥塞控制机制吗？"},
    {"role": "user", "content": "了解一些。TCP 拥塞控制主要有四个阶段：慢启动、拥塞避免、快重传和快恢复。慢启动阶段窗口从 1 开始指数增长，到达慢启动阈值后进入拥塞避免阶段，窗口改为线性增长。如果检测到丢包（收到三个重复 ACK），就进入快重传立即重发丢失的包，然后快恢复把阈值设为当前窗口的一半，窗口从新阈值开始线性增长。不过具体的一些细节比如 CUBIC 算法我了解得不太深入。"},
    {"role": "assistant", "content": "没关系，能说到这里已经很不错了。最后一个问题：如果让你设计一个短链接服务，你会怎么做？"},
    {"role": "user", "content": "我大概的思路是这样的：首先用一个自增 ID 或者分布式 ID 生成器来给每个长链接分配唯一 ID，然后把这个 ID 转成 62 进制的短字符串作为短链接的 key。存储的话可以用 MySQL 存长短链接的映射关系，前面加一层 Redis 做缓存提高读取速度。用户访问短链接时，服务端查到对应长链接后返回 301 或 302 重定向。如果要考虑高并发，可以做水平分库分表，按短链接 key 做哈希分片。"},
]


def test_ai_report():
    """测试同步版 ai_report"""
    print("=" * 60)
    print("测试 ai_report（同步版）")
    print(f"对话轮数：{len(MOCK_HISTORY)} 条消息")
    print("=" * 60)
    print("正在调用 Qwen-max 生成面试评价报告，请稍候...\n")

    try:
        report = ai_report(MOCK_HISTORY)
        print(report)
        print("\n" + "=" * 60)
        print("✅ 同步版测试通过！")
    except Exception as e:
        print(f"\n❌ 同步版测试失败: {e}")


def test_ai_report_stream():
    """测试流式版 ai_report_stream"""
    print("=" * 60)
    print("测试 ai_report_stream（流式版）")
    print(f"对话轮数：{len(MOCK_HISTORY)} 条消息")
    print("=" * 60)
    print("正在调用 Qwen-max 流式生成面试评价报告...\n")

    try:
        final_report = ""
        for partial in ai_report_stream(MOCK_HISTORY):
            final_report = partial
            # 每次输出当前最新一个字符，模拟实时打印效果
            print(f"\r已生成 {len(final_report)} 字...", end="", flush=True)

        print("\n\n--- 完整报告 ---\n")
        print(final_report)
        print("\n" + "=" * 60)
        print("✅ 流式版测试通过！")
    except Exception as e:
        print(f"\n❌ 流式版测试失败: {e}")


if __name__ == "__main__":
    # 默认测试同步版，传入 --stream 参数测试流式版
    if "--stream" in sys.argv:
        test_ai_report_stream()
    else:
        test_ai_report()
