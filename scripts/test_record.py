"""
录音 API 测试脚本

测试运行中的 PeekAPI 服务的 /record 端点

Usage:
    python -m scripts.test_record [--save]

Examples:
    python -m scripts.test_record         # 只测试端点
    python -m scripts.test_record --save  # 保存录音文件
    python -m scripts.test_record --host 192.168.1.100  # 远程主机
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import httpx

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def ensure_output_dir() -> Path:
    """确保输出目录存在"""
    output_dir = PROJECT_ROOT / ".sandbox" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def main():
    parser = argparse.ArgumentParser(description="测试 /record API")
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
        "--save",
        action="store_true",
        help="保存录音到 .sandbox/audio/",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    print("=" * 50)
    print("🎤 PeekAPI 录音 API 测试")
    print("=" * 50)
    print(f"🌐 目标服务: {base_url}")
    print()

    # 发送请求
    print("📡 发送请求...")
    try:
        with httpx.Client(timeout=60) as client:
            response = client.get(f"{base_url}/record")
    except httpx.ConnectError:
        print(f"❌ 连接失败：无法连接到 {base_url}")
        print("   请确保 PeekAPI 服务正在运行")
        return 1
    except httpx.TimeoutException:
        print("❌ 请求超时（录音生成可能需要较长时间）")
        return 1

    print()
    print(f"📊 响应状态码: {response.status_code}")
    print(f"📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(
        f"📦 响应大小: {len(response.content):,} bytes ({len(response.content) / 1024:.1f} KB)"
    )
    print()

    if response.status_code == 200:
        print("✅ 请求成功！")

        if args.save:
            output_dir = ensure_output_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_audio_{timestamp}.wav"
            output_path = output_dir / filename

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"💾 已保存到: {output_path}")
            print("💡 提示: 使用系统播放器打开文件试听")
        else:
            print("💡 提示: 添加 --save 参数可保存录音")

    elif response.status_code == 403:
        print("⚠️ 访问被拒绝：服务处于私密模式")
        print(f"   响应: {response.text}")

    elif response.status_code == 500:
        print("❌ 服务器错误：录音获取失败")
        print(f"   响应: {response.text}")

    else:
        print(f"❓ 未知响应: {response.text}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
