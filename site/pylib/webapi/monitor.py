
import sys
import time
import logging


APACHE_LOG_FORMAT = '''%(ip)s - - [%(time)s] "%(request)s" %(status)s %(bytes)s "%(referer)s" "%(agent)s"\n'''

def monitor(app):
    """Monitors performance of request serving."""
    def wrapper(e, o):
        path = _get_fullpath(e)
        start = time.time()
        result = app(e, o)

        end = time.time()
        logging.info("Served: %s %sms", path, int((end - start) * 1000))
        return result
    return wrapper

def sleep(app):
    def wrapper(e, o):
        time.sleep(3)
        return app(e, o)
    return wrapper

def apachelog(app, level=None):
    def wrapper(env, start_response):
        statuses = ["200"]
        def xstart_response(status, response_headers, *args):
            statuses[0] = status.split(" ", 1)[0]
            return start_response(status, response_headers, *args)

        start = time.time()
        result = app(env, xstart_response)
        end = time.time()

        fullpath = _get_fullpath(env)
        bytes = "-"
        if isinstance(result, list) or isinstance(result, tuple):
            bytes = str(sum(len(v) for v in result))

        line = APACHE_LOG_FORMAT % {
                "ip": env.get("REMOTE_ADDR", "-"),
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                    time.gmtime(start)),
                "request": "%s %s" % (
                    env.get("REQUEST_METHOD", ""), fullpath),
                "status": statuses[0],
                "bytes": bytes,
                "referer": env.get("HTTP_REFERER", "-"),
                "agent": env.get("HTTP_USER_AGENT", "-"),
                }
        if level is None:
            sys.stderr.write(line)
        else:
            ms = int((end - start) * 1000)
            logging.log(level, "%s ms: %s", ms, line.rstrip())
        return result
    return wrapper


def _get_fullpath(env):
    path = env.get("PATH_INFO", "")
    if env.get('QUERY_STRING'):
        path += '?' + env.get('QUERY_STRING', '')
    return path

