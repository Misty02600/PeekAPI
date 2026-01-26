import io
from threading import Thread

from flask import Flask, request, send_file

from .config import config
from .constants import ICON_PATH
from .logging import logger, setup_logging
from .record import recorder
from .screenshot import screenshot
from .system_tray import start_system_tray


app = Flask(__name__)

def parse_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

@app.route('/screen', methods=["GET"])
def screen_route():
    client_ip = request.remote_addr
    r = parse_float(request.args.get("r"))
    k = request.args.get("k", "")
    # 如果配置了 api_key 且不匹配，则拒绝访问
    if r < config.screenshot.radius_threshold and config.basic.api_key and k != config.basic.api_key:
        logger.debug(f"[{client_ip}] 截图请求被拒绝: 无权限查看高清图 (r={r})")
        return "没有权限查看高清图", 401

    if config.basic.is_public:
        img_data = screenshot(r, config.screenshot.main_screen_only)
        if not img_data:
            logger.warning(f"[{client_ip}] 截图请求失败")
            return "截图失败", 500
        logger.debug(f"[{client_ip}] 截图请求成功 (r={r}, size={len(img_data)} bytes)")
        return send_file(io.BytesIO(img_data), mimetype='image/jpeg')
    logger.debug(f"[{client_ip}] 截图请求被拒绝: 私密模式")
    return "瑟瑟中", 403

@app.route('/record', methods=["GET"])
def record_route():
    client_ip = request.remote_addr
    audio_data = recorder.get_audio()
    if config.basic.is_public:
        if audio_data is None:
            logger.warning(f"[{client_ip}] 录音请求失败")
            return "录音获取失败", 500
        logger.debug(f"[{client_ip}] 录音请求成功")
        return send_file(audio_data, mimetype='audio/wav')
    logger.debug(f"[{client_ip}] 录音请求被拒绝: 私密模式")
    return "瑟瑟中", 403

@app.route('/check', methods=["GET", "POST"])
def check_route():
    return "ok", 200

@app.route('/favicon.ico')
def favicon():
    try:
        return send_file(ICON_PATH)
    except Exception:
        return '', 204

def start_app():
    # 初始化日志系统（日志仅写入文件）
    setup_logging()

    logger.info("PeekAPI 已启动")
    try:
        # 启动录音
        recorder.start_recording()

        # 启动系统托盘
        Thread(target=start_system_tray, daemon=True).start()
        logger.info("系统托盘线程已启动")

        # 启动 Flask 服务器
        server = Thread(target=lambda: app.run(
            host=config.basic.host,
            port=config.basic.port,
            debug=False,
            use_reloader=False
        ), daemon=True)
        server.start()
        logger.info(f"Flask 服务器线程已启动: {config.basic.host}:{config.basic.port}")
        server.join()
    except Exception as e:
        logger.error(f"服务器错误: {e}")
    finally:
        recorder.stop_recording()
