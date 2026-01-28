"""
完整 API 测试脚本

测试运行中的 PeekAPI 服务的所有端点

Usage:
    python -m scripts.test_all

Examples:
    python -m scripts.test_all                    # 默认测试
    python -m scripts.test_all --host 192.168.1.100  # 测试远程主机
    python -m scripts.test_all --api-key xxx      # 带 API 密钥测试
"""

import argparse
import sys
from datetime import datetime

import httpx


def test_endpoint(
    base_url: str, method: str, path: str, params: dict = None, name: str = ""
) -> dict:
    """测试单个端点"""
    url = f"{base_url}{path}"
    result = {
        "name": name,
        "path": path,
        "method": method.upper(),
        "status": None,
        "success": False,
        "size": 0,
        "error": None,
    }

    try:
        with httpx.Client(timeout=30) as client:
            if method == "get":
                response = client.get(url, params=params)
            else:
                response = client.post(url)

            result["status"] = response.status_code
            result["size"] = len(response.content)
            result["success"] = response.status_code == 200

    except httpx.ConnectError:
        result["error"] = "连接失败"
    except httpx.TimeoutException:
        result["error"] = "请求超时"

    return result


def main():
    parser = argparse.ArgumentParser(description="测试所有 API 端点")
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
        "--api-key",
        type=str,
        default="",
        help="API 密钥",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    print("=" * 60)
    print("🔬 PeekAPI 完整 API 测试")
    print("=" * 60)
    print(f"🌐 目标服务: {base_url}")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 定义测试用例
    test_cases = [
        ("get", "/check", None, "健康检查 (GET)"),
        ("post", "/check", None, "健康检查 (POST)"),
        ("get", "/screen", {"r": 0}, "截图 (无模糊)"),
        ("get", "/screen", {"r": 5}, "截图 (模糊 r=5)"),
        ("get", "/record", None, "录音"),
        ("get", "/favicon.ico", None, "网站图标"),
    ]

    # 如果有 API 密钥，添加额外测试
    if args.api_key:
        test_cases.append(
            ("get", "/screen", {"r": 0, "k": args.api_key}, "截图 (带密钥)")
        )

    print("📋 测试用例:")
    for method, path, params, name in test_cases:
        print(f"   • {name}: {method.upper()} {path}")
    print()

    # 执行测试
    print("🚀 开始测试...")
    print("-" * 60)

    results = []
    for method, path, params, name in test_cases:
        print(f"   测试: {name}...", end=" ")
        result = test_endpoint(base_url, method, path, params, name)
        results.append(result)

        if result["error"]:
            print(f"❌ {result['error']}")
        elif result["success"]:
            print(f"✅ {result['status']} ({result['size']:,} bytes)")
        else:
            print(f"⚠️ {result['status']}")

    print("-" * 60)
    print()

    # 汇总结果
    success_count = sum(1 for r in results if r["success"])
    error_count = sum(1 for r in results if r["error"])
    total_count = len(results)

    print("📊 测试结果汇总:")
    print(f"   ✅ 成功: {success_count}/{total_count}")
    print(f"   ⚠️ 非 200: {total_count - success_count - error_count}/{total_count}")
    print(f"   ❌ 错误: {error_count}/{total_count}")
    print()

    if error_count > 0:
        print("💡 提示: 有连接错误，请检查服务是否正在运行")
        return 1
    elif success_count == total_count:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("💡 提示: 部分端点返回非 200 状态码，可能是正常的权限限制")
        return 0


if __name__ == "__main__":
    sys.exit(main())
