#!/usr/bin/env python3
"""
数据库初始化脚本
用于在部署后初始化Vercel Postgres数据库
"""

import os
import sys
from app import app, db

def init_database():
    """初始化数据库表"""
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功！")
            
            # 可以在这里添加一些初始数据
            # from app import Book
            # if Book.query.count() == 0:
            #     sample_book = Book(
            #         title="示例书籍",
            #         author="示例作者",
            #         price=20.0,
            #         condition="九成新",
            #         description="这是一本示例书籍"
            #     )
            #     db.session.add(sample_book)
            #     db.session.commit()
            #     print("✅ 示例数据添加成功！")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    init_database() 