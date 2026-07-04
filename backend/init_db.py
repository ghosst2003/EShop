"""初始化 MySQL 数据库 - 创建表和管理员账号"""
import sys
from sqlalchemy import create_engine, text
from app.config import settings
from app.models import Base
from app.auth import hash_password
from app.database import SessionLocal

def init_database():
    print("=" * 50)
    print("BeCool Market - 数据库初始化")
    print("=" * 50)
    print(f"数据库: {settings.database_url}")
    print()

    try:
        # 测试连接
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表创建完成")

        # 创建默认管理员
        db = SessionLocal()
        try:
            from app.models import User
            existing = db.query(User).filter(User.username == "admin").first()
            if existing:
                print("⚠️  管理员账号 'admin' 已存在")
            else:
                admin = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    role="admin",
                    display_name="管理员",
                    email="",
                )
                db.add(admin)
                db.commit()
                print("✅ 默认管理员创建成功")
                print("   用户名: admin")
                print("   密码: admin123")
        finally:
            db.close()

        print()
        print("=" * 50)
        print("初始化完成！可以启动服务了")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print()
        print("请检查:")
        print("1. .env 文件中的 DATABASE_URL 是否正确")
        print("2. 远程 MySQL 服务器是否允许远程连接")
        print("3. 数据库用户是否有创建表的权限")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
