# oss-ready 中文说明

`oss-ready` 是一个零运行时依赖的命令行工具，用于检查仓库是否具备健康开源协作所需的基础设施。它只在本地读取文件，不会上传代码。

## 能检查什么

- README、开源许可证、项目元数据与 `.gitignore`
- 贡献指南、行为准则、支持政策、Issue 和 PR 模板
- 安全政策与依赖更新自动化
- 自动化测试与持续集成
- 更新日志与发布准备情况

## 安装与使用

```bash
python -m pip install oss-ready
oss-ready
```

生成 Markdown 报告：

```bash
oss-ready . --format markdown --output reports/oss-ready.md
```

生成 JSON 并且不以分数决定退出码：

```bash
oss-ready . --format json --fail-on never
```

## 配置

在 `pyproject.toml` 中添加：

```toml
[tool.oss-ready]
min-score = 80
fail-on = "score"
ignore = ["community.support"]
```

也可以新建 `.oss-ready.toml` 并直接填写这些键。该文件优先于 `pyproject.toml`。

## 重要说明

分数衡量的是仓库协作准备程度，不代表项目代码质量、受欢迎程度或安全性。请结合实际项目需求判断每条建议。

欢迎通过 Issue 报告问题，也欢迎提交 Pull Request。详细流程见 [贡献指南](../CONTRIBUTING.md)。

