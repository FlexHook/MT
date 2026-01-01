from sqlitedict import SqliteDict
import os
import atexit
from pathlib import Path

class Preferences:
    _instance = None
    _db_path = ""

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if db_path is None:
                # 确保使用绝对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                db_path = os.path.join(current_dir, "app_prefs.sqlite")
            else:
                # 如果是相对路径，转换为绝对路径
                if not os.path.isabs(db_path):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    db_path = os.path.join(current_dir, db_path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            cls._instance._db_path = db_path
            cls._instance.db = SqliteDict(db_path, autocommit=True)
            
            # 注册关闭时的清理函数
            atexit.register(cls._instance.close)
        return cls._instance

    def get(self, key, default=None):
        try:
            return self.db.get(key, default)
        except Exception:
            return default

    def put(self, key, value):
        self.db[key] = value
        self.db.commit()

    def remove(self, key):
        if key in self.db:
            del self.db[key]
            self.db.commit()

    def clear(self):
        self.db.clear()
        self.db.commit()

    def keys(self):
        return list(self.db.keys())

    def items(self):
        return list(self.db.items())

    def __contains__(self, key):
        return key in self.db

    def close(self):
        if hasattr(self, 'db'):
            self.db.close()
        self.__class__._instance = None

    def __del__(self):
        self.close()

    def get_db_path(self):
        """获取数据库文件路径"""
        return self._db_path

    def save_to_git(self):
        """保存数据库文件到Git（这是一个可选功能，应该从类中分离出来）"""
        db_path = self.get_db_path()
        if os.path.exists(db_path):
            try:
                # 首先提交数据库文件
                if os.system(f'git add "{db_path}"') == 0:
                    os.system('git config --local user.name "github-actions[bot]"')
                    os.system('git config --local user.email "github-actions[bot]@users.noreply.github.com"')
                    os.system('git commit -m "更新数据库文件"')
                    os.system('git push --quiet --force-with-lease')
            except Exception as e:
                print(f"Git操作失败: {e}")

# 创建单例实例
prefs = Preferences()

# 可选：创建数据库文件并保存到Git的函数
def save_prefs_to_git():
    """将数据库文件保存到Git"""
    db_path = prefs.get_db_path()
    if not os.path.exists(db_path):
        # 如果数据库文件不存在，创建一个测试数据
        prefs.put("last_updated", "2026-01-01")
        prefs.db.commit()
    
    if os.path.exists(db_path):
        try:
            # 添加数据库文件到Git
            os.system(f'git add "{db_path}"')
            os.system('git config --local user.name "github-actions[bot]"')
            os.system('git config --local user.email "github-actions[bot]@users.noreply.github.com"')
            os.system('git commit -m "更新数据库"')
            os.system('git push --quiet')
        except Exception as e:
            print(f"Git操作失败: {e}")
