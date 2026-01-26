from contextlib import asynccontextmanager
from threading import Thread

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import Response

from .config import config
from .logging import logger, setup_logging
from .record import recorder
from .screenshot import screenshot
from .system_tray import start_system_tray


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    logger.info("PeekAPI 已启动")

    # 启动录音
    recorder.start_recording()

    # 启动系统托盘
    Thread(target=start_system_tray, daemon=True).start()
    logger.info("系统托盘线程已启动")

    yield

    # 关闭时
    recorder.stop_recording()
    logger.info("PeekAPI 已关闭")


app = FastAPI(
    title="PeekAPI",
    description="屏幕截图和音频录制 API 服务",
    version="0.1.0",
    lifespan=lifespan,
)


def parse_float(value: str | None, default: float = 0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


@app.get("/screen")
def screen_route(
    request: Request,
    r: float = Query(default=0, description="模糊半径"),
    k: str = Query(default="", description="API 密钥"),
):
    """获取屏幕截图"""
    client_ip = request.client.host if request.client else "unknown"

    # 如果配置了 api_key 且不匹配，则拒绝访问
    if (
        r < config.screenshot.radius_threshold
        and config.basic.api_key
        and k != config.basic.api_key
    ):
        logger.debug(f"[{client_ip}] 截图请求被拒绝: 无权限查看高清图 (r={r})")
        return Response(content="没有权限查看高清图", status_code=401)

    if config.basic.is_public:
        img_data = screenshot(r, config.screenshot.main_screen_only)
        if not img_data:
            logger.warning(f"[{client_ip}] 截图请求失败")
            return Response(content="截图失败", status_code=500)
        logger.debug(f"[{client_ip}] 截图请求成功 (r={r}, size={len(img_data)} bytes)")
        return Response(content=img_data, media_type="image/jpeg")

    logger.debug(f"[{client_ip}] 截图请求被拒绝: 私密模式")
    return Response(content="瑟瑟中", status_code=403)


@app.get("/record")
def record_route(request: Request):
    """获取录音数据"""
    client_ip = request.client.host if request.client else "unknown"
    audio_data = recorder.get_audio()

    if config.basic.is_public:
        if audio_data is None:
            logger.warning(f"[{client_ip}] 录音请求失败")
            return Response(content="录音获取失败", status_code=500)

        # 读取 BytesIO 内容
        audio_bytes = audio_data.read()
        logger.debug(f"[{client_ip}] 录音请求成功")
        return Response(content=audio_bytes, media_type="audio/wav")

    logger.debug(f"[{client_ip}] 录音请求被拒绝: 私密模式")
    return Response(content="瑟瑟中", status_code=403)


@app.get("/check")
@app.post("/check")
def check_route():
    """健康检查"""
    return Response(content="ok", status_code=200)


@app.get("/favicon.ico")
def favicon_route():
    """返回网站图标"""
    from .constants import BASE_DIR

    icon_path = BASE_DIR / "peekapi.ico"
    if icon_path.exists():
        return Response(
            content=icon_path.read_bytes(),
            media_type="image/x-icon",
        )
    return Response(status_code=204)


def start_app():
    """启动 FastAPI 服务器"""
    uvicorn.run(
        app,
        host=config.basic.host,
        port=config.basic.port,
        log_level="warning",  # 减少 Uvicorn 日志，使用我们自己的 logger
        log_config=None,  # 禁用 uvicorn 日志配置，修复 PyInstaller windowed 模式问题
    )
