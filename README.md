# Weekly AI 3D Robotics Digest

每周 AI 总结机器人行业进展。

这个仓库用于保存每周自动/半自动整理的行业进展报告，重点覆盖 SLAM、visual-inertial odometry、SfM、feed-forward 3D reconstruction、3D generation、具身智能、世界模型和机器人导航等方向。

## 内容结构

- `reports/index.html`：报告索引页，最新报告在最上方。
- `reports/*.html`：按覆盖日期和关键词命名的结构化周报。

## 报告命名

报告文件名采用：

```text
YYYY-MM-DD_YYYY-MM-DD_关键词1-关键词2.html
```

两个日期表示本次覆盖范围，关键词来自当周最重要的论文或开源项目事件。

## 使用方式

直接用浏览器打开 `reports/index.html`，再跳转到具体报告。

## 报告索引

- [2026-05-29 至 2026-06-06：ScaRF-SLAM、ZipSplat 与 WAM-Nav](reports/2026-05-29_2026-06-06_ScaRF-SLAM-ZipSplat-WAM-Nav.html)
  - 覆盖 SLAM / VIO / SfM / FeedForward 3DR / 3DGS / 具身智能 / 世界模型 / 机器人导航方向。
- [2026-05-21 至 2026-05-28：GLUEMAP、TriSplat 与 WorldEngine](reports/2026-05-21_2026-05-28_GLUEMAP-TriSplat-WorldEngine.html)
  - 覆盖 SLAM / VIO / SfM / FeedForward 3DR / 具身智能 / 世界模型 / 机器人方向。

## 在 GitHub 上查看 HTML

GitHub 仓库文件页会把 `.html` 当作源码展示，不会直接渲染页面。要直接查看渲染后的 HTML，推荐启用 GitHub Pages：

1. 打开仓库的 `Settings`。
2. 进入 `Pages`。
3. `Source` 选择 `Deploy from a branch`。
4. `Branch` 选择 `main`，目录选择 `/ (root)`。
5. 保存后等待部署完成。

启用后可以访问：

- `https://alalagong.github.io/weekly-ai-3d-robotics-digest/`
- `https://alalagong.github.io/weekly-ai-3d-robotics-digest/reports/index.html`

## 数据来源

报告优先引用可验证来源，包括 arXiv、GitHub、官方项目页、论文项目页和公开文档。若某些来源需要登录或触发访问限制，会在报告中注明。
