import logging

# get root logger
ROOT_LOG = logging.getLogger()
ROOT_LOG.setLevel(logging.INFO)

# Console logger
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
ROOT_LOG.addHandler(stream_handler)
