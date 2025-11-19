import socket
import logging
import time
import sys

logger = logging.getLogger(__name__)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)

    ip = None

    try:
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    
    return ip

def is_host_reachable(ip, port, timeout=1):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, int(port)))
    except socket.timeout:
        return False
    except Exception as e:
        logger.error("Socket error: {}".format(e))
        return False
    else:
        sock.close()
        return True

def shutdown(timer=1):
    print("shutting down...")
    logger.info("shutting down...")
    time.sleep(timer)
    sys.exit()