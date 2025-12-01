import logging
from typing import Dict

logger = logging.getLogger("Auth")

class AuthService:
    def __init__(self):
        self.failed_attempts = 0
        self.is_locked = False
        self.MAX_ATTEMPTS = 5
        self.default_user = "admin"
        self.default_pass = "password"

    def check_login(self, username: str, password: str, config_pass: str = None) -> Dict:
        if self.is_locked:
            logger.warning(f"Login blocked. System is locked.")
            return {
                "success": False, 
                "locked": True, 
                "msg": "系统已锁定！请重启容器以解锁。"
            }

        valid_pass = config_pass if config_pass else self.default_pass
        
        if username == self.default_user and password == valid_pass:
            self.failed_attempts = 0
            return {"success": True, "locked": False, "token": "admin-session"}
        else:
            self.failed_attempts += 1
            remaining = self.MAX_ATTEMPTS - self.failed_attempts
            logger.warning(f"Login failed. Attempt {self.failed_attempts}/{self.MAX_ATTEMPTS}")
            
            if self.failed_attempts >= self.MAX_ATTEMPTS:
                self.is_locked = True
                return {
                    "success": False, 
                    "locked": True, 
                    "msg": "错误次数过多，系统已锁定！请重启容器。"
                }
            
            return {
                "success": False, 
                "locked": False, 
                "msg": f"用户名或密码错误。剩余尝试次数: {remaining}"
            }

auth_service = AuthService()
