# Copyright 2023 iwatake2222
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Logger Factory
"""
import logging


class LoggerFactory():
  '''Logger Factory'''
  level: int = logging.DEBUG
  log_filename: str = None

  @classmethod
  def create(cls, name) -> logging.Logger:
    '''Create logger'''
    logger = logging.getLogger(name)
    logger.setLevel(cls.level)
    stream_handler = logging .StreamHandler()
    stream_handler.setLevel(cls.level)
    handler_format = logging.Formatter('[%(levelname)-7s][%(filename)s:%(lineno)s] %(message)s')
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)
    if cls.log_filename:
      file_handler = logging.FileHandler(cls.log_filename)
      file_handler.setLevel(cls.level)
      handler_format = logging.Formatter(
        '[%(asctime)s][%(levelname)-7s][%(filename)s:%(lineno)s] %(message)s')
      file_handler.setFormatter(handler_format)
      logger.addHandler(file_handler)
    return logger

  @classmethod
  def config(cls, level, log_filename) -> None:
    '''Config'''
    LoggerFactory.level = level
    LoggerFactory.log_filename = log_filename
