"""
健康检查 API 测试脚本

测试运行中的 PeekAPI 服务的 /check 端点

Usage:
    python -m scripts.test_check

Examples:
    python -m scripts.test_check                    # 默认请求
    python -m scripts.test_check --host 192.168.1.100  # 远程主机
    python -m scripts.test_check --method post      # 使用 POST 方法
"""

import argparse
import sys

import httpx


def main():
    parser = argparse.ArgumentParser(description="测试 /check API")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="API 服务器主机地址，默认 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1920,
        help="API 服务器端口，默认 22334",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["get", "post"],
        default="get",
        help="HTTP 方法，默认 get",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    print("=" * 50)
    print("🏥 PeekAPI 健康检查 API 测试")
    print("=" * 50)
    print(f"🌐 目标服务: {base_url}")
    print(f"📝 请求方法: {args.method.upper()}")
    print()

    # 发送请求
    print("📡 发送请求...")
    try:
        with httpx.Client(timeout=10) as client:
            if args.method == "get":
                response = client.get(f"{base_url}/check")
            else:
                response = client.post(f"{base_url}/check")
    except httpx.ConnectError:
        print(f"❌ 连接失败：无法连接到 {base_url}")
        print("   请确保 PeekAPI 服务正在运行")
        return 1
    except httpx.TimeoutException:
        print("❌ 请求超时")
        return 1

    print()
    print(f"📊 响应状态码: {response.status_code}")
    print(f"📋 响应内容: {response.text}")
    print()

    if response.status_code == 200 and response.text == "ok":
        print("✅ 服务健康！PeekAPI 正常运行")
    else:
        print("⚠️ 服务状态异常")

    return 0


if __name__ == "__main__":
    sys.exit(main())
