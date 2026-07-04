"""插入测试商品数据：8本书 + 2个水杯"""
from datetime import datetime
from app.database import SessionLocal
from app.models import Product

db = SessionLocal()

try:
    # 8 本书
    books = [
        {
            "slug": "jvm-deep-dive",
            "title": "深入理解Java虚拟机",
            "title_en": "Understanding the JVM",
            "description": "全面讲解Java虚拟机原理、垃圾回收机制与性能优化的经典之作",
            "sale_price": 45.99,
            "original_price": 69.99,
            "condition_grade": "like_new",
            "brand": "机械工业出版社",
            "tags": ["Java", "虚拟机", "编程"],
        },
        {
            "slug": "intro-to-algorithms-4e",
            "title": "算法导论（第四版）",
            "title_en": "Introduction to Algorithms",
            "description": "计算机算法领域的经典教材，涵盖排序、搜索、图论等核心算法",
            "sale_price": 58.00,
            "original_price": 89.00,
            "condition_grade": "good",
            "brand": "MIT Press",
            "tags": ["算法", "计算机科学", "教材"],
        },
        {
            "slug": "one-hundred-years-solitude",
            "title": "百年孤独",
            "title_en": "One Hundred Years of Solitude",
            "description": "加西亚·马尔克斯的代表作，魔幻现实主义文学巅峰",
            "sale_price": 29.99,
            "original_price": 45.00,
            "condition_grade": "like_new",
            "brand": "南海出版公司",
            "tags": ["文学", "小说", "马尔克斯"],
        },
        {
            "slug": "python-crash-course",
            "title": "Python编程：从入门到实践",
            "title_en": "Python Crash Course",
            "description": "适合初学者的Python编程指南，包含项目实战",
            "sale_price": 35.50,
            "original_price": 55.00,
            "condition_grade": "new",
            "brand": "人民邮电出版社",
            "tags": ["Python", "编程", "入门"],
        },
        {
            "slug": "design-patterns-gof",
            "title": "设计模式：可复用面向对象软件的基础",
            "title_en": "Design Patterns",
            "description": "GoF经典设计模式，23种模式的完整解析",
            "sale_price": 39.90,
            "original_price": 59.90,
            "condition_grade": "good",
            "brand": "机械工业出版社",
            "tags": ["设计模式", "软件工程", "编程"],
        },
        {
            "slug": "sapiens-brief-history",
            "title": "人类简史",
            "title_en": "Sapiens: A Brief History of Humankind",
            "description": "尤瓦尔·赫拉利著作，从认知革命到科学革命的人类发展史",
            "sale_price": 32.00,
            "original_price": 49.00,
            "condition_grade": "fair",
            "brand": "中信出版社",
            "tags": ["历史", "社科", "畅销书"],
        },
        {
            "slug": "computer-networking-top-down",
            "title": "计算机网络：自顶向下方法",
            "title_en": "Computer Networking: A Top-Down Approach",
            "description": "计算机网络经典教材，从应用层到物理层的系统讲解",
            "sale_price": 42.00,
            "original_price": 75.00,
            "condition_grade": "good",
            "brand": "Pearson",
            "tags": ["网络", "教材", "计算机"],
        },
        {
            "slug": "to-live-yuhua",
            "title": "活着",
            "title_en": "To Live",
            "description": "余华代表作，讲述中国农村老人福贵的一生",
            "sale_price": 18.99,
            "original_price": 29.00,
            "condition_grade": "like_new",
            "brand": "作家出版社",
            "tags": ["文学", "小说", "余华"],
        },
    ]

    # 2 个水杯
    cups = [
        {
            "slug": "stainless-thermos-500ml",
            "title": "不锈钢保温杯 500ml",
            "title_en": "Stainless Steel Thermos 500ml",
            "description": "304不锈钢真空保温杯，保冷保温12小时，大容量便携设计",
            "sale_price": 25.99,
            "original_price": 45.00,
            "condition_grade": "new",
            "brand": "膳魔师",
            "tags": ["保温杯", "不锈钢", "便携"],
            "weight_kg": 0.35,
        },
        {
            "slug": "glass-tumbler-set-6pcs",
            "title": "玻璃水杯套装 6只装",
            "title_en": "Glass Tumbler Set 6pcs",
            "description": "高硼硅玻璃水杯套装，耐热耐冷，简约北欧风格",
            "sale_price": 22.50,
            "original_price": 38.00,
            "condition_grade": "new",
            "brand": "乐美雅",
            "tags": ["玻璃杯", "套装", "北欧风"],
            "weight_kg": 1.2,
        },
    ]

    created_by = 1  # admin
    category_id_books = 1  # 图书
    category_id_books_used = 2  # 二手书

    all_products = []

    for i, book in enumerate(books):
        # 前4本用"图书"分类，后4本用"二手书"分类
        cat = category_id_books if i < 4 else category_id_books_used
        p = Product(
            category_id=cat,
            status="active",
            created_by=created_by,
            published_at=datetime.now(),
            views_count=0,
            stock_quantity=10,
            auto_manage_stock=1,
            **book,
        )
        db.add(p)
        all_products.append(book["title"])

    for cup in cups:
        p = Product(
            category_id=category_id_books,  # 暂时放在图书分类下
            status="active",
            created_by=created_by,
            published_at=datetime.now(),
            views_count=0,
            stock_quantity=20,
            auto_manage_stock=1,
            **cup,
        )
        db.add(p)
        all_products.append(cup["title"])

    db.commit()

    print(f"成功插入 {len(all_products)} 条商品数据:")
    for name in all_products:
        print(f"  ✓ {name}")

except Exception as e:
    db.rollback()
    print(f"插入失败: {e}")
    raise
finally:
    db.close()
