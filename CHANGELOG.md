# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-XX

### Added
- **跨平台支持** - 新增 macOS 和 Linux 平台支持
- **多语言支持** - 支持中文 / English 实时切换
- **设置界面** - 图形化设置窗口 (基于 tkinter)
- **快捷键录制** - 支持直接按下组合键录制新快捷键
- **状态管理** - 使用单例模式管理全局状态
- **单元测试** - 添加 pytest 测试框架和测试用例
- **统一日志** - 添加统一的日志配置模块

### Changed
- 重构为跨平台架构 (`platforms/` 模块)
- 配置管理使用 dataclass 提供类型安全
- 托盘菜单支持动态语言切换
- 优化托盘菜单生成性能

### Fixed
- 修复配置文件损坏时的异常处理
- 修复快捷键监听器的线程安全问题

## [1.0.0] - 2025-12-XX

### Added
- 全局快捷键置顶窗口 (Ctrl+Space)
- 系统托盘菜单
- 已置顶窗口列表显示
- 一键取消全部置顶
- 开机自启功能
- 气泡通知
- 配置文件支持

[1.1.0]: https://github.com/iuliysii/TopMostTool/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/iuliysii/TopMostTool/releases/tag/v1.0.0
