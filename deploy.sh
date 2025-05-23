#!/bin/bash

# Vercel Postgres 快速部署脚本
echo "🚀 开始部署Flask书店管理系统到Vercel..."

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装"
    echo "请运行: npm i -g vercel"
    exit 1
fi

# 检查是否已登录Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 请先登录Vercel..."
    vercel login
fi

echo "📦 准备部署文件..."

# 确保所有必要文件存在
required_files=("vercel.json" "api/index.py" "requirements.txt" "app.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少必要文件: $file"
        exit 1
    fi
done

echo "✅ 所有必要文件已就绪"

# 部署到Vercel
echo "🌐 正在部署到Vercel..."
vercel --prod

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 在Vercel控制台添加Postgres存储"
echo "2. 设置环境变量：SECRET_KEY 和 ADMIN_PASSWORD"
echo "3. 重新部署项目"
echo ""
echo "📖 详细指南请查看: VERCEL_POSTGRES_SETUP.md"
echo "" 