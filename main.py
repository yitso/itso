# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()


if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer
    from app import create_app
    from app.config import get_config

    app = create_app()
    cfg = get_config()
    server = WSGIServer((cfg.HOST, cfg.PORT), app)
    print(f"[gevent] Serving on http://{cfg.HOST}:{cfg.PORT} (ENV={cfg.__class__.__name__})")
    server.serve_forever()
