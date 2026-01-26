# [TASK005] - 优化打包流程

**Status:** Completed
**Added:** 2026-01-25
**Updated:** 2026-01-26
**Priority:** Medium

## Original Request

优化打包流程，介绍各主流打包方案并比较。

## Thought Process

### 当前打包方式

```bash
uv run pyinstaller --noconsole --onefile --name peekapi --icon peekapi.ico run.py
```

**问题：**
1. 无 `.spec` 文件，配置不可版本控制
2. 未显式声明 `hiddenimports`，可能遗漏动态导入
3. 未添加 Windows 版本信息
4. 打包体积可能较大

---

## 主流 Python 打包方案对比

### 1. PyInstaller（当前方案）

**简介：** 最流行的 Python 打包工具，将 Python 应用打包为独立可执行文件。**最新版本 v6.18.0**（2025年1月发布）。

**原理：**
- 分析代码依赖，收集所有模块
- 打包 Python 解释器 + 依赖 + 代码
- 单文件模式运行时解压到临时目录（`_MEIxxxxxx`）

**Python 支持：** 3.8-3.14

**优点：**
- ✅ 成熟稳定，社区最活跃（12.9k stars, 85k+ 项目使用）
- ✅ 支持单文件打包（`--onefile`）
- ✅ 跨平台支持（Windows/Linux/macOS）
- ✅ `.spec` 文件支持复杂配置
- ✅ 大量 hooks 处理第三方库
- ✅ 文档完善，问题容易搜索解决

**缺点：**
- ❌ 打包体积较大（30-80MB）
- ❌ 单文件模式启动速度慢（需解压，首次 2-5 秒）
- ❌ 代码仍可被逆向提取（.pyc 文件）
- ❌ 杀毒软件可能误报

**适用场景：** 通用 GUI/CLI 应用打包

---

### 2. Nuitka

**简介：** 将 Python 代码编译为 C 代码，再编译为原生机器码。**最新版本持续更新中**（2.6.x，仓库昨天仍有更新）。

**原理：**
- 将 Python 转译为 C 代码
- 使用 C 编译器（MSVC/GCC/Clang/Zig）编译
- 生成真正的原生可执行文件

**Python 支持：** 2.6, 2.7, 3.4-3.14（包括最新的 Python 3.14）

**优点：**
- ✅ 真正编译为机器码，启动极快
- ✅ **性能提升 3.3-3.7 倍**（pystone 基准测试）
- ✅ 更难被逆向（相比 PyInstaller）
- ✅ 打包体积相对较小
- ✅ 支持加速模式（仅加速不打包）
- ✅ 非常活跃的维护（14.4k stars）
- ✅ 支持静态链接 Python（某些环境下）
- ✅ GitHub Actions 集成（Nuitka-Action）

**缺点：**
- ❌ 编译时间长（10-30 分钟）
- ❌ 需要 C 编译器（Windows 推荐 MSVC，或自动下载 MinGW64）
- ❌ 部分动态特性兼容性问题
- ❌ 配置复杂，学习曲线陡
- ❌ Python 3.13+ 不支持 MinGW64

**适用场景：** 追求性能和保护代码的场景

**示例：**
```bash
# 基本打包
python -m nuitka --mode=standalone --onefile --windows-icon-from-ico=peekapi.ico run.py

# 优化打包（推荐）
python -m nuitka --mode=onefile --lto=yes --output-dir=dist run.py
```

---

### 3. cx_Freeze

**简介：** 跨平台打包工具，生成可执行文件和依赖目录。**最新版本 v8.5.3**（活跃维护）。

**特点：** "与原脚本性能相同"（官方声明），即打包后无性能损失。

**原理：**
- 收集依赖到 `lib` 目录
- 生成启动器可执行文件
- 运行时直接加载，无需解压

**Python 支持：** 3.10-3.14（包括自由线程版本）

**优点：**
- ✅ 启动速度比 PyInstaller 快（无解压过程）
- ✅ 跨平台支持好
- ✅ 配置简单（setup.py 风格）
- ✅ 支持 MSI/DMG/RPM/DEB 安装包生成
- ✅ 活跃维护

**缺点：**
- ❌ 不支持单文件打包
- ❌ 生成文件夹结构
- ❌ 社区规模不如 PyInstaller

**适用场景：** 需要安装程序的桌面应用

---

### 4. py2exe（仅 Windows）

**简介：** Windows 专用打包工具，历史悠久。

**优点：**
- ✅ Windows 专精，兼容性好
- ✅ 配置简单

**缺点：**
- ❌ 仅支持 Windows
- ❌ 不如 PyInstaller 活跃
- ❌ Python 3.12+ 支持有限

**适用场景：** 仅 Windows 的简单应用

---

### 5. ~~PyOxidizer~~ (已停止维护)

**简介：** Rust 实现的打包工具，将 Python 嵌入到 Rust 可执行文件。

> ⚠️ **不推荐使用**：最后更新于 **2022年12月** (v0.24.0)，GitHub 仓库已超过3年无实质性更新。
> 仍有 335+ 未解决 Issues，26 个未合并 PRs。

**原理：**
- 使用 Rust 构建启动器
- 嵌入 Python 解释器和代码
- 生成单文件原生可执行文件

**优点：**
- ✅ 真正单文件（无需解压）
- ✅ 启动速度快
- ✅ 现代化工具链

**缺点：**
- ❌ **已停止维护**
- ❌ 需要 Rust 工具链
- ❌ 配置使用 Starlark 语言
- ❌ 某些 Python 包兼容性问题
- ❌ 文档较少

**适用场景：** ~~追求极致性能的场景~~ → 不再推荐新项目使用

---

### 6. Briefcase (BeeWare)

**简介：** 跨平台应用打包工具，支持移动端。**最新版本 v0.3.26**。

**支持平台：**
- Windows (App 文件夹 / Visual Studio 项目)
- macOS (.app bundle / XCode 项目)
- Linux (原生系统包 / Flatpak / AppImage)
- iOS (XCode 项目)
- Android (Gradle 项目)
- Web (静态网站，使用 PyScript)

**优点：**
- ✅ 支持 Windows/macOS/Linux/iOS/Android/Web
- ✅ 生成原生安装包格式
- ✅ 与 Toga GUI 框架集成
- ✅ 活跃的 BeeWare 生态系统

**缺点：**
- ❌ 主要面向 GUI 应用
- ❌ 不支持单文件打包
- ❌ 学习曲线较陡

**适用场景：** 跨平台 GUI 应用（包括移动端）

---

## 方案对比表（2026年1月最新信息）

| 特性 | PyInstaller | Nuitka | cx_Freeze | Briefcase |
|------|-------------|--------|-----------|-----------|
| **最新版本** | v6.18.0 (活跃) | 2.6.x (活跃) | v8.5.3 (活跃) | v0.3.26 (活跃) |
| **Python 支持** | 3.8-3.14 | 3.4-3.14 | 3.10-3.14 | 3.8+ |
| **单文件** | ✅ | ✅ | ❌ | ❌ |
| **启动速度** | ⚠️ 慢(需解压) | ✅ 快 | ✅ 较快 | ✅ 较快 |
| **打包体积** | ⚠️ 大 | ✅ 较小 | ⚠️ 中等 | ⚠️ 中等 |
| **编译时间** | ✅ 快 | ❌ 慢 | ✅ 快 | ✅ 快 |
| **代码保护** | ❌ 易提取 | ✅ 编译为C | ❌ 易提取 | ❌ 易提取 |
| **兼容性** | ✅ 好 | ⚠️ 中等 | ✅ 好 | ✅ 好 |
| **学习曲线** | ✅ 低 | ⚠️ 中等 | ✅ 低 | ⚠️ 中等 |
| **社区支持** | ✅ 活跃(12.9k⭐) | ✅ 活跃(14.4k⭐) | ✅ 活跃 | ✅ BeeWare生态 |
| **跨平台** | ✅ | ✅ | ✅ | ✅ +移动端 |

> **注意：** PyOxidizer 最后更新于 2022年12月 (v0.24.0)，已超过3年未维护，不建议新项目使用。

---

## 运行时资源占用对比

### 内存占用

| 工具 | 运行时内存特点 |
|------|---------------|
| **PyInstaller** | 运行时内存占用与原生 Python 相似。单文件模式在启动时需要解压到临时目录，会短暂占用额外磁盘空间和内存。 |
| **Nuitka** | 内存占用通常**更低**，因为编译为 C 代码后优化了内存结构。某些场景可节省 10-30% 内存。 |
| **cx_Freeze** | 与 PyInstaller 相似，因为原理类似（打包解释器+依赖）。 |
| **Briefcase** | 与原生 Python 相似，打包为目录结构。 |

### 启动速度

| 工具 | 启动特点 |
|------|---------|
| **PyInstaller (onefile)** | **最慢**：需要先解压到临时目录（`_MEIxxxxxx`），首次启动可能需要 2-5 秒。 |
| **PyInstaller (onefolder)** | 较快：直接从文件夹加载，无需解压。 |
| **Nuitka** | **最快**：编译为原生机器码，启动几乎与 C 程序一样快。 |
| **cx_Freeze** | 较快：直接从安装目录加载。 |

### 运行时性能

根据 Nuitka 官方 pystone 基准测试：
- **Nuitka 编译后**：性能提升约 **3.3-3.7 倍**（相比解释执行）
- **PyInstaller/cx_Freeze**：性能与原生 Python 解释器相同（无优化）

**结论：** 如果追求运行时性能和低内存占用，Nuitka 是最佳选择；如果只需简单打包分发，PyInstaller 足够。

---

## 最终决策

**选择方案：PyInstaller**

**决策理由：**
1. 项目已有 PyInstaller 配置基础，团队熟悉
2. 依赖（pystray, winotify, soundcard, numpy）在 PyInstaller 有成熟的 hooks
3. 单文件分发便于用户使用
4. 打包速度快，开发迭代效率高
5. 不追求极致性能，启动速度 2-5 秒可接受

**关于 numpy 体积问题：**
- soundcard 库强制依赖 numpy，无法移除
- 接受 numpy 带来的体积增加（压缩后约 15-20MB）
- 通过 PyInstaller 的 `--exclude-module` 排除不需要的子模块优化

---

## 具体优化内容

### 1. 创建 `peekapi.spec` 文件

**目的：** 将打包配置版本控制，方便维护和复现。

**文件位置：** 项目根目录 `peekapi.spec`

**关键配置说明：**
- `console=False` - 无控制台窗口，所有日志通过 loguru 写入文件
- `datas` - 包含图标和默认配置
- `hiddenimports` - 显式声明动态导入的模块
- `excludes` - 排除不需要的大型模块减小体积
- `upx=True` - 启用 UPX 压缩（可选）
        'numpy',
        'numpy.core',

        # 其他
        'PIL._tkinter_finder',
        'pystray._win32',
        'winotify',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型模块
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'pytest',
        'setuptools',

        # 排除 numpy 测试和文档
        'numpy.testing',
        'numpy.distutils',
        'numpy.f2py',
        'numpy.doc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='peekapi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                           # 启用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                      # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='peekapi.ico',
    version='version_info.txt',         # Windows 版本信息
)
```

---

### 2. 创建 Windows 版本信息文件

**目的：** 右键查看 exe 属性时显示版本、公司、描述等信息。

**文件位置：** 项目根目录 `version_info.txt`

**具体内容：**
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName', u'PeekAPI'),
          StringStruct(u'FileDescription', u'Screen Capture & Audio Recording API'),
          StringStruct(u'FileVersion', u'1.0.0.0'),
          StringStruct(u'InternalName', u'peekapi'),
          StringStruct(u'LegalCopyright', u'MIT License'),
          StringStruct(u'OriginalFilename', u'peekapi.exe'),
          StringStruct(u'ProductName', u'PeekAPI'),
          StringStruct(u'ProductVersion', u'1.0.0.0'),
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

---

### 3. 移除无用依赖

**目的：** 清理 pyproject.toml 中不需要显式声明的依赖。

**操作：**
- 移除 `wave`（Python 标准库，无需安装）

---

### 4. 新的打包命令

**之前：**
```bash
uv run pyinstaller --noconsole --onefile --name peekapi --icon peekapi.ico run.py
```

**之后：**
```bash
uv run pyinstaller peekapi.spec
```

**优势：**
- 配置可版本控制
- 包含 hiddenimports 避免缺失模块
- 自动包含数据文件（图标、配置）
- 自动应用 Windows 版本信息
- 自动排除不需要的大模块

---

### 5. （可选）安装 UPX 压缩工具

**目的：** 减小可执行文件体积（约可减少 20-30%）。

**操作：**
1. 从 https://github.com/upx/upx/releases 下载 UPX
2. 解压到 PATH 目录或 PyInstaller 同目录
3. spec 文件中 `upx=True` 会自动使用

---

## Implementation Plan

- [x] 1.1 创建 `peekapi.spec` 打包配置文件
- [x] 1.2 创建 `version_info.txt` Windows 版本信息
- [x] 1.3 测试打包流程，验证功能
- [x] 1.4 更新 README 打包说明
- [x] 1.5 简化代码（移除 --console 参数相关代码）
- [ ] 1.6 （可选）下载安装 UPX 并测试压缩效果

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 创建 peekapi.spec | Complete | 2026-01-26 | 包含 hiddenimports 和 excludes |
| 1.2 | 创建 version_info.txt | Complete | 2026-01-26 | Windows 文件属性 |
| 1.3 | 测试打包 | Complete | 2026-01-26 | 28.5MB，所有 API 正常 |
| 1.4 | 更新 README | Complete | 2026-01-26 | 新打包命令 |
| 1.5 | 简化代码 | Complete | 2026-01-26 | 移除 console 参数 |
| 1.6 | 安装 UPX | Skipped | - | 可选，暂不需要 |

## Progress Log

### 2026-01-25
- 创建任务记录
- 调研主流打包方案并对比
- 调研运行时内存/性能差异
- 确认 PyOxidizer 已停止维护（不推荐）
- 分析 numpy 依赖问题（soundcard 强制依赖，无法移除）
- **最终决策：采用 PyInstaller**
- 细化具体优化内容和实施步骤

### 2026-01-26
- 更新任务文档，移除 wave 依赖相关内容（已在 TASK006 处理）
- 移除 --console 参数相关内容（日志现在仅写入文件）
- 创建 `peekapi.spec` 打包配置文件
- 创建 `version_info.txt` Windows 版本信息文件
- 执行打包测试：`uv run pyinstaller peekapi.spec --clean`
- 打包成功，生成 28.5MB 可执行文件
- 测试验证：
  - ✅ /check API 正常响应
  - ✅ /screen API 返回截图 (1MB JPEG)
  - ✅ /record API 返回录音 (1.7MB WAV)
  - ✅ 系统托盘正常显示
  - ✅ 日志正常写入 logs 目录
- 简化代码：
  - 移除 `server.py` 中的 `--console` 参数检测
  - 移除 `logging.py` 中的 console 参数和相关代码
  - 移除不再需要的 `sys` 导入
- 更新 README 打包说明
- 73 个单元测试全部通过
- 根据需求调整为 onefolder 模式：
  - 原因：应用本身需要 config.toml 配置文件，单文件模式意义不大
  - 修改 `peekapi.spec` 使用 COLLECT 生成文件夹
  - `config.toml` 和 `peekapi.ico` 放在 exe 同级目录，方便用户修改
  - 更新 `constants.py` 中的 `ICON_PATH` 直接指向 `BASE_DIR / "peekapi.ico"`
  - 修复代码中 "要求" 注释标记的问题
  - 更新 README 打包说明
- 73 个单元测试全部通过
- **任务完成**

## References

- [PyInstaller 文档](https://pyinstaller.org/)
- [PyInstaller Spec 文件](https://pyinstaller.org/en/stable/spec-files.html)
- [UPX 压缩](https://upx.github.io/)
