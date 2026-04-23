import unittest

from core import CommandLine
from config import AppConfig

class RadioOperatorProxy:
    
    def _send_to_operator_proxy(self):
        ...

class TestCommandLine(unittest.TestCase):
    
    def create_default_cmd(self) -> CommandLine:
        config: AppConfig = AppConfig.default()
        operator: RadioOperatorProxy = RadioOperatorProxy()
        
        return CommandLine(config, operator._send_to_operator_proxy)
    
    def test_validate_row(self):
        cmd: CommandLine = self.create_default_cmd()
    
    def test_validate_col(self):
        ...
    
    def test_validate_sec(self):
        ...