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
Test logger_factory module
"""
import os
import logging
import tempfile

from src.dear_ros_node_viewer.logger_factory import LoggerFactory


class TestLoggerFactoryCreate:
    """Tests for LoggerFactory.create method"""

    def test_create_basic(self):
        """Test basic logger creation"""
        logger = LoggerFactory.create('test_logger')

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'

    def test_create_multiple_loggers(self):
        """Test creating multiple loggers with different names"""
        logger1 = LoggerFactory.create('test_logger_1')
        logger2 = LoggerFactory.create('test_logger_2')

        assert logger1.name == 'test_logger_1'
        assert logger2.name == 'test_logger_2'
        assert logger1 is not logger2

    def test_create_same_name_returns_same_logger(self):
        """Test that creating logger with same name returns same instance"""
        logger1 = LoggerFactory.create('same_name_logger')
        logger2 = LoggerFactory.create('same_name_logger')

        # logging.getLogger returns same instance for same name
        assert logger1 is logger2

    def test_create_logger_has_handlers(self):
        """Test that created logger has handlers attached"""
        logger = LoggerFactory.create('test_handler_logger')

        assert len(logger.handlers) > 0

    def test_create_logger_level(self):
        """Test that logger has correct level set"""
        original_level = LoggerFactory.level
        LoggerFactory.level = logging.WARNING

        logger = LoggerFactory.create('test_level_logger')

        assert logger.level == logging.WARNING

        # Restore original level
        LoggerFactory.level = original_level


class TestLoggerFactoryConfig:
    """Tests for LoggerFactory.config method"""

    def test_config_level(self):
        """Test configuring log level"""
        original_level = LoggerFactory.level
        original_filename = LoggerFactory.log_filename

        LoggerFactory.config(logging.ERROR, None)

        assert LoggerFactory.level == logging.ERROR

        # Restore original settings
        LoggerFactory.level = original_level
        LoggerFactory.log_filename = original_filename

    def test_config_filename(self):
        """Test configuring log filename"""
        original_level = LoggerFactory.level
        original_filename = LoggerFactory.log_filename

        LoggerFactory.config(logging.DEBUG, 'test.log')

        assert LoggerFactory.log_filename == 'test.log'

        # Restore original settings
        LoggerFactory.level = original_level
        LoggerFactory.log_filename = original_filename

    def test_config_with_file_handler(self):
        """Test that file handler is added when filename is configured"""
        original_level = LoggerFactory.level
        original_filename = LoggerFactory.log_filename

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_log_path = f.name

        try:
            LoggerFactory.config(logging.DEBUG, temp_log_path)
            logger = LoggerFactory.create('test_file_handler_logger')

            # Logger should have file handler
            has_file_handler = any(
                isinstance(h, logging.FileHandler) for h in logger.handlers
            )
            assert has_file_handler

            # Test that logging works
            logger.info('Test message')

        finally:
            # Restore original settings
            LoggerFactory.level = original_level
            LoggerFactory.log_filename = original_filename
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)


class TestLoggerFactoryLogging:
    """Tests for actual logging functionality"""

    def test_logger_can_log_debug(self):
        """Test that logger can log debug messages"""
        original_level = LoggerFactory.level
        LoggerFactory.level = logging.DEBUG

        logger = LoggerFactory.create('test_debug_logger')

        # Should not raise exception
        logger.debug('Debug message')

        LoggerFactory.level = original_level

    def test_logger_can_log_info(self):
        """Test that logger can log info messages"""
        logger = LoggerFactory.create('test_info_logger')

        # Should not raise exception
        logger.info('Info message')

    def test_logger_can_log_warning(self):
        """Test that logger can log warning messages"""
        logger = LoggerFactory.create('test_warning_logger')

        # Should not raise exception
        logger.warning('Warning message')

    def test_logger_can_log_error(self):
        """Test that logger can log error messages"""
        logger = LoggerFactory.create('test_error_logger')

        # Should not raise exception
        logger.error('Error message')

    def test_logger_format(self):
        """Test that logger uses correct format"""
        logger = LoggerFactory.create('test_format_logger')

        # Check that stream handler has formatter
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.formatter is not None


class TestLoggerFactoryClassAttributes:
    """Tests for LoggerFactory class attributes"""

    def test_default_level(self):
        """Test default log level"""
        # Default level should be DEBUG
        assert LoggerFactory.level == logging.DEBUG

    def test_default_filename(self):
        """Test default log filename"""
        # Default filename should be None
        assert LoggerFactory.log_filename is None
