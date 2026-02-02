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


    # 发送请求
    try:
        with httpx.Client(timeout=60) as client:
            response = client.get(f"{base_url}/record")
    except httpx.ConnectError:
        return 1
    except httpx.TimeoutException:
        return 1


    if response.status_code == 200:

        if args.save:
            output_dir = ensure_output_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_audio_{timestamp}.wav"
            output_path = output_dir / filename

            with open(output_path, "wb") as f:
                f.write(response.content)

        else:
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
