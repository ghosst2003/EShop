"""创建初始管理员账号"""
import argparse
import getpass
import sys

from app.auth import hash_password
from app.database import SessionLocal, engine
from app.models import Base, User


def create_admin(username: str, password: str, display_name: str = "管理员", email: str = ""):
    # 确保表存在
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"管理员 '{username}' 已存在")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
            display_name=display_name,
            email=email,
        )
        db.add(user)
        db.commit()
        print(f"管理员 '{username}' 创建成功")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建初始管理员")
    parser.add_argument("--username", default="admin", help="管理员用户名")
    parser.add_argument("--password", help="管理员密码；省略时安全交互输入")
    parser.add_argument("--display-name", default="管理员", help="显示名称")
    parser.add_argument("--email", default="", help="邮箱")
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass("管理员密码（至少 12 个字符）: ")
        confirmation = getpass.getpass("再次输入管理员密码: ")
        if password != confirmation:
            parser.error("两次输入的密码不一致")

    if len(password) < 12:
        parser.error("管理员密码至少需要 12 个字符")

    create_admin(args.username, password, args.display_name, args.email)
