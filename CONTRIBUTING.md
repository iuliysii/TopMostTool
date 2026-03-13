# 贡献指南

感谢你对 TopMost Tool 的关注！本文档将帮助你了解如何为项目做出贡献。

## 🤝 如何贡献

### 报告 Bug

如果你发现了 bug，请创建一个 [Issue](https://github.com/iuliysii/TopMostTool/issues)，并包含以下信息：

- 操作系统和版本
- Python 版本
- 复现步骤
- 预期行为和实际行为
- 相关日志（如果有）

### 提交功能请求

欢迎提出新功能建议！请在 Issue 中详细描述：

- 功能描述
- 使用场景
- 可能的实现方式

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TopMostTool.git
   cd TopMostTool
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **安装开发依赖**
   ```bash
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt  # Windows
   pip install pytest pytest-cov  # 测试工具
   ```

4. **编写代码**
   - 遵循 PEP 8 代码风格
   - 添加类型注解
   - 编写文档字符串

5. **运行测试**
   ```bash
   python -m pytest tests/ -v
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述你的更改
   - 关联相关 Issue
   - 等待代码审查

## 📝 代码规范

### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具

### 代码风格

- 遵循 PEP 8
- 使用 4 空格缩进
- 最大行长度 100 字符
- 添加类型注解

## 📜 许可证

提交代码即表示你同意你的贡献将按照 [MIT License](LICENSE) 授权。
