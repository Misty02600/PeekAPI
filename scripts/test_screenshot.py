"""
截图 API 测试脚本

测试运行中的 PeekAPI 服务的 /screen 端点

Usage:
    python -m scripts.test_screenshot [--blur RADIUS] [--api-key KEY]

Examples:
    python -m scripts.test_screenshot               # 默认请求
    python -m scripts.test_screenshot --blur 5      # 模糊半径5
    python -m scripts.test_screenshot --api-key xxx # 带 API 密钥
    python -m scripts.test_screenshot --host 192.168.1.100  # 远程主机
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
    output_dir = PROJECT_ROOT / ".sandbox" / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def main():
    parser = argparse.ArgumentParser(description="测试 /screen API")
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
        "--blur",
        type=float,
        default=0,
        help="高斯模糊半径，默认 0（不模糊）",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="",
        help="API 密钥（用于获取高清图）",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存截图到 .sandbox/screenshots/",
    )
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    if args.api_key:
        pass

    # 构建请求参数
    params = {"r": args.blur}
    if args.api_key:
        params["k"] = args.api_key

    # 发送请求
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{base_url}/screen", params=params)
    except httpx.ConnectError:
        return 1
    except httpx.TimeoutException:
        return 1


    if response.status_code == 200:

        if args.save:
            output_dir = ensure_output_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_screenshot_{timestamp}.jpg"
            output_path = output_dir / filename

            with open(output_path, "wb") as f:
                f.write(response.content)

        else:
            pass

    elif response.status_code == 401:
        pass

    elif response.status_code == 403:
        pass

    elif response.status_code == 500:
        pass

    else:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
