# PeekAPI Justfile
# 在 Windows 上使用 PowerShell
set shell := ["powershell", "-NoLogo", "-Command"]

# 默认命令：显示帮助
default:
    @just --list

# ===== 运行 =====

# 启动服务器
run:
    uv run peekapi

# ===== 测试 =====

# 运行所有测试
test:
    uv run pytest -n auto

# 运行单元测试
test-unit:
    uv run pytest tests/unit -n auto

# 运行集成测试
test-integration:
    uv run pytest tests/integration -n auto

# ===== 打包 =====

# 打包为 exe
build:
    uv run pyinstaller peekapi.spec --noconfirm

# 清理构建产物
clean:
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist

# 打包并显示大小
build-size: build
    $size = (Get-ChildItem -Path "dist/peekapi" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ("打包完成: {0:N2} MB" -f $size)

# ===== 代码质量 =====

# 格式化代码
format:
    uv run ruff format .

# 检查代码
lint:
    uv run ruff check . --fix

# 类型检查
check:
    uv run basedpyright

# ===== 版本管理 =====

# 版本发布（更新版本号、更新 lock 文件）
bump:
    uv run cz bump
    uv lock

# 生成 changelog
changelog:
    uv run git-cliff --latest

# ===== prek =====

# 安装 prek hooks
hooks:
    uv run prek install

# 更新 prek hooks
update:
    uv run prek auto-update
