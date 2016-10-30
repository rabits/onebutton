import logging
from jsonrpctcp import logger, config as JSONRPCConfig, connect as JSONRPCConnect

if __name__ == '__main__':
  logger.addHandler(logging.StreamHandler()) # sends to stdout
  logger.setLevel(logging.DEBUG)

  JSONRPCConfig.append_string = '\n'
  client = JSONRPCConnect('board-1.psa', 8881)
  #print(client.getversion())
  client.setstate("bypassed")
