
import logging

log = logging.getLogger("spekulatio")
log.setLevel(logging.INFO)

# add handler
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)
