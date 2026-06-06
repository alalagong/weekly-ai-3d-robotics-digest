$ErrorActionPreference = "Stop"

$file = "C:\Users\gongy\.codex\automations\automation\automation.toml"
if (-not (Test-Path -LiteralPath $file)) {
    throw "Automation TOML not found: $file"
}

$backup = "$file.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -LiteralPath $file -Destination $backup

$content = @'
version = 1
id = "automation"
kind = "cron"
name = "每周行业进展自动总结"
prompt = """自动去 arXiv 网站搜集最新的论文信息，去 GitHub 搜集新开源的代码，总结领域进展。总结成结构化信息，存成网页信息到本地。用日期和重大事项命名网页文件。具体信息如下：

领域：
1. 我 focus 的领域是：SLAM（同步定位与建图）、visual-inertial odometry、SfM、FeedForward 3DR。
2. 此外我还感兴趣的方向包括：AI、具身智能、世界模型、机器人等，相关内容也可以包括进来。

论文部分：
3. 时间范围是最近的一周，也就是上一次搜集到这一次搜集之间。
4. 总结要说明：论文要解决的问题、核心方法是什么、背后的 insight 是什么、实验相关情况、效果如何。如果有开源代码请列出来。
5. 实验部分尽量摆数据，可量化，简明扼要少陈述，说清楚实验平台、方法、结果和新颖点。

代码部分：
6. 开源代码可以来自 GitHub 热榜，也可以来自我 followed 的人的 star repo。以 star/fork 数量高、相关性大的为主。可以操控我的 Chrome。
7. 允许使用电脑、运行使用 MCP、允许运行低风险命令。"""
status = "ACTIVE"
rrule = "RRULE:FREQ=WEEKLY;BYHOUR=9;BYMINUTE=0;BYDAY=SU"
model = "gpt-5.5"
reasoning_effort = "high"
execution_environment = "local"
cwds = ["C:\\Users\\gongy\\Documents\\每周行业进展-fromAI"]
created_at = 1779905011449
updated_at = 1779907475313
'@

Set-Content -LiteralPath $file -Value $content -Encoding UTF8

Write-Host "Repaired: $file"
Write-Host "Backup:   $backup"
Select-String -LiteralPath $file -Pattern "每周行业进展自动总结", "每周行业进展-fromAI", "SLAM"
