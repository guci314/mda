"""
测试日志模块
"""
import sys
import logging
import pytest
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import get_logger, setup_logging  # type: ignore


class TestLogger:
    """测试日志功能"""
    
    def test_get_logger(self):
        """测试获取日志器"""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert logger.level == logging.INFO  # 默认级别是 INFO
    
    def test_multiple_loggers(self):
        """测试获取多个日志器"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 != logger2
    
    def test_same_logger_instance(self):
        """测试相同名称返回相同实例"""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        
        assert logger1 is logger2
    
    def test_logger_inheritance(self):
        """测试日志器继承"""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        
        assert child_logger.parent == parent_logger
    
    def test_setup_logging(self):
        """测试设置日志"""
        # 调用 setup_logging
        setup_logging()
        
        # 获取根日志器
        root_logger = logging.getLogger()
        
        # 检查是否有处理器
        assert len(root_logger.handlers) > 0
        
        # 检查日志级别
        assert root_logger.level == logging.INFO
    
    def test_logger_output_format(self, caplog):
        """测试日志输出格式"""
        logger = get_logger("test_format")
        
        with caplog.at_level(logging.INFO):
            logger.info("Test message")
        
        assert "Test message" in caplog.text
        assert "test_format" in caplog.text
    
    def test_logger_levels(self, caplog):
        """测试不同日志级别"""
        logger = get_logger("test_levels")
        logger.setLevel(logging.DEBUG)  # 设置为 DEBUG 级别以捕获所有消息
        
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
        
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
    
    def test_logger_exception(self, caplog):
        """测试异常日志"""
        logger = get_logger("test_exception")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            with caplog.at_level(logging.ERROR):
                logger.exception("Exception occurred")
        
        assert "Exception occurred" in caplog.text
        assert "ValueError: Test exception" in caplog.text
        assert "Traceback" in caplog.text


if __name__ == "__main__":
    # 直接运行此文件时使用 pytest
    pytest.main([__file__, "-v"])