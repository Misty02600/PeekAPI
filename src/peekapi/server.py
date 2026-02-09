from contextlib import asynccontextmanager
from threading import Thread

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, Response

from .config import config
from .idle import get_idle_info
from .logging import logger, setup_logging
from .record import recorder
from .screenshot import screenshot
from .system_info import get_system_info
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


@app.get("/screen")
def screen_route(
    request: Request,
    r: float = Query(
        default=config.screenshot.radius_threshold, description="模糊半径"
    ),
    k: str = Query(default="", description="API 密钥"),
):
    """获取屏幕截图"""
    client_ip = request.client.host if request.client else "unknown"

    if not config.basic.is_public:
        logger.info(f"[{client_ip}] 截图请求被拒绝: 私密模式")
        raise HTTPException(status_code=403, detail="瑟瑟中")

    # 如果配置了 api_key 且不匹配，则拒绝访问
    if (
        r < config.screenshot.radius_threshold
        and config.basic.api_key
        and k != config.basic.api_key
    ):
        logger.info(f"[{client_ip}] 截图请求被拒绝: 无权限查看高清图 (r={r})")
        raise HTTPException(status_code=401, detail="没有权限查看高清图")

    img_data = screenshot(r, config.screenshot.main_screen_only)
    if not img_data:
        logger.info(f"[{client_ip}] 截图请求失败")
        raise HTTPException(status_code=500, detail="截图失败")

    logger.info(f"[{client_ip}] 截图请求成功 (r={r}, size={len(img_data)} bytes)")
    return Response(content=img_data, media_type="image/jpeg")


@app.get("/record")
def record_route(request: Request):
    """获取录音数据"""
    client_ip = request.client.host if request.client else "unknown"

    if not config.basic.is_public:
        logger.info(f"[{client_ip}] 录音请求被拒绝: 私密模式")
        raise HTTPException(status_code=403, detail="瑟瑟中")

    audio_data = recorder.get_audio()
    if audio_data is None:
        logger.info(f"[{client_ip}] 录音请求失败")
        raise HTTPException(status_code=500, detail="录音获取失败")

    audio_bytes = audio_data.read()
    logger.info(f"[{client_ip}] 录音请求成功")
    return Response(content=audio_bytes, media_type="audio/wav")


@app.get("/idle")
def idle_route(request: Request):
    """获取用户空闲时间"""
    client_ip = request.client.host if request.client else "unknown"

    if not config.basic.is_public:
        logger.info(f"[{client_ip}] 空闲时间请求被拒绝: 私密模式")
        raise HTTPException(status_code=403, detail="瑟瑟中")

    idle_seconds, last_input_time = get_idle_info()
    logger.info(f"[{client_ip}] 空闲时间请求成功 (idle={idle_seconds:.1f}s)")

    return {
        "idle_seconds": round(idle_seconds, 3),
        "last_input_time": last_input_time.isoformat(),
    }


@app.get("/info")
def info_route(request: Request):
    """获取设备信息"""
    client_ip = request.client.host if request.client else "unknown"

    if not config.basic.is_public:
        logger.info(f"[{client_ip}] 设备信息请求被拒绝: 私密模式")
        raise HTTPException(status_code=403, detail="瑟瑟中")

    info = get_system_info(config.basic.device_name)
    logger.info(f"[{client_ip}] 设备信息请求成功")
    return info


@app.get("/check")
@app.post("/check")
def check_route():
    """健康检查"""
    logger.info("健康检查成功")
    return PlainTextResponse(content="ok")


def start_app():
    """启动 FastAPI 服务器"""
    uvicorn.run(
        app,
        host=config.basic.host,
        port=config.basic.port,
        log_level="info",  # 显示 Uvicorn 请求日志
        log_config=None,  # 禁用 uvicorn 日志配置
    )
