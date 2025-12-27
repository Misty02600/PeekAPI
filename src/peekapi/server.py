import io
import logging
from threading import Thread

from flask import Flask, request, send_file

from .config import config, ICON_PATH
from .record import recorder
from .screenshot import screenshot
from .system_tray import show_notification, start_system_tray


app = Flask(__name__)

def parse_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

@app.route('/screen', methods=["GET"])
def screen_route():
    r = parse_float(request.args.get("r"))
    k = request.args.get("k")
    if r < config.radius_threshold and k != config.api_key:
        return "没有权限查看高清图", 401

    if config.is_public:
        img_data = screenshot(r, config.main_screen_only)
        if not img_data:
            return "截图失败", 500
        return send_file(io.BytesIO(img_data), mimetype='image/jpeg')
    return "瑟瑟中", 403

@app.route('/record', methods=["GET"])
def record_route():
    audio_data = recorder.get_audio()
    if config.is_public:
        if audio_data is None:
            return "录音获取失败", 500
        return send_file(audio_data, mimetype='audio/wav')
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
    show_notification("Peek API已启动", "")
    try:
        # 启动录音
        recorder.start_recording()

        # 启动系统托盘
        Thread(target=start_system_tray, daemon=True).start()

        # 启动 Flask 服务器
        server = Thread(target=lambda: app.run(
            host=config.host,
            port=config.port,
            debug=False,
            use_reloader=False
        ), daemon=True)
        server.start()
        server.join()
    except Exception as e:
        logging.error(f"服务器错误: {e}")
    finally:
        recorder.stop_recording()
