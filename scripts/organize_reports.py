from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "单片机答疑数据库"
MARKER = "## 数据库归档补充"


@dataclass(frozen=True)
class Category:
    file_name: str
    title: str
    nav_label: str
    patterns: tuple[str, ...]


CATEGORIES = (
    Category(
        "toolchain.md",
        "工具链与环境踩坑",
        "工具链 / 环境",
        (
            r"keil|proteus|stc|isp|烧录|编译|仿真|hex|头文件|reg52|regx52|安装|cubemx|target not created|driver路径|找不到hex|打不开头文件",
        ),
    ),
    Category(
        "system.md",
        "综合赛题与系统结构踩坑",
        "综合赛题 / 系统",
        (
            r"状态机|调度器|任务|界面|模式|锁定|恢复默认|恢复出厂|副本|综合|统计|运动|参数界面|系统结构|控制流|多界面|模块化底层|主函数无法正常使用|大模板",
        ),
    ),
    Category(
        "sensor.md",
        "温度 / 时钟 / 传感器模块踩坑",
        "温度 / 时钟 / 传感器",
        (
            r"温度|湿度|ds18b20|ds1302|aht10|闹钟|电子钟|时钟|rtc|单总线|传感器|蜂鸣器|继电器",
        ),
    ),
    Category(
        "uart.md",
        "串口模块踩坑",
        "串口",
        (
            r"串口|uart|usart|波特率|接收|发送|rx|tx",
        ),
    ),
    Category(
        "eeprom.md",
        "EEPROM 模块踩坑",
        "EEPROM",
        (
            r"eeprom|at24|at24c02|i2c 存储|掉电保存",
        ),
    ),
    Category(
        "ultrasonic.md",
        "超声波模块踩坑",
        "超声波",
        (
            r"超声波|测距|距离|回波",
        ),
    ),
    Category(
        "ad.md",
        "AD 采集模块踩坑",
        "AD 采集",
        (
            r"\bad\b|adc|采样|光敏|电位器|电压采集|模数转换|ad转换|光照",
        ),
    ),
    Category(
        "da.md",
        "DA 模块踩坑",
        "DA 输出",
        (
            r"\bda\b|dac|电压输出|回放|数模转换",
        ),
    ),
    Category(
        "timer.md",
        "定时与计数模块踩坑",
        "定时 / 计数",
        (
            r"定时器|timer|计时|中断|节拍|tick|计数|频率|delay|延时",
        ),
    ),
    Category(
        "key.md",
        "按键模块踩坑",
        "按键",
        (
            r"按键|短按|长按|松开|抬起|矩阵按键|独立按键|组合键|键盘",
        ),
    ),
    Category(
        "seg.md",
        "数码管模块踩坑",
        "数码管",
        (
            r"数码管|seg|段码|小数点|闪烁|虚闪|显示错位",
        ),
    ),
    Category(
        "led.md",
        "LED 模块踩坑",
        "LED",
        (
            r"led|流水灯|彩灯|指示灯|闪灯",
        ),
    ),
    Category(
        "programming.md",
        "C51 语法与基础逻辑踩坑",
        "C51 语法 / 基础逻辑",
        (
            r"数据类型|局部变量|全局变量|数组|for循环|冒泡|学习方法|资源|符号|==|=和==|c语言|逻辑|取反|位移|_crol|运算符|static|bit 类型|类型定义|概念理解|底层考试的时候给吗|从哪开始学|网站",
        ),
    ),
)


ISSUE_HEADING_RE = re.compile(r"^###\s*(.+?)\s*$", re.MULTILINE)
TITLE_PREFIX_RE = re.compile(r"^(?:#+\s*)?[（(]?[0-9一二三四五六七八九十百零\.、 ]+[）).、 ]*")
SUMMARY_SECTION_RE = re.compile(r"\n##\s+[四五六七八九十].*", re.DOTALL)
FIELD_RE = re.compile(r"^[*\-]\s+\*\*(.+?)\*\*[：:]\s*(.*)$")
TITLE_OVERRIDES: tuple[tuple[str, str], ...] = (
    (r"建立工程到user目录下|driver路径|打不开头文件|找不到regx52\.h|找不到hex文件", "toolchain.md"),
    (r"da转换测电压引脚问题|dac|回放", "da.md"),
    (r"ad转换|adc|光敏|电位器", "ad.md"),
    (r"led_disp无法显示|彩灯控制|流水灯", "led.md"),
    (r"时钟设置界面切换失败|参数设置界面", "system.md"),
)


def normalize_title(raw: str) -> str:
    title = raw.strip()
    title = title.replace("&lt;", "<").replace("&gt;", ">")
    title = TITLE_PREFIX_RE.sub("", title).strip()
    return title or raw.strip()


def extract_report_week(text: str, fallback: str) -> str:
    match = re.search(r"\*\s+\*\*答疑周期\*\*：(.+)", text)
    if match:
        return match.group(1).strip()
    clean = fallback
    if "_" in clean:
        clean = clean.split("_", 1)[1]
    return clean.replace(".md", "").strip()


def iter_issue_blocks(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    matches = list(ISSUE_HEADING_RE.finditer(text))
    issues: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = normalize_title(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        block = SUMMARY_SECTION_RE.sub("", block).strip()
        if block:
            issues.append((title, block))
    return issues


def classify_issue(title: str, body: str) -> tuple[Category, list[str]]:
    title_lower = title.lower()
    for pattern, file_name in TITLE_OVERRIDES:
        if re.search(pattern, title_lower):
            primary = next(cat for cat in CATEGORIES if cat.file_name == file_name)
            secondary = [cat.nav_label for cat in CATEGORIES if cat.file_name != file_name and any(re.search(p, title_lower) for p in cat.patterns)]
            return primary, secondary[:3]

    haystack = f"{title}\n{body}".lower()
    scores: list[tuple[int, Category]] = []
    for category in CATEGORIES:
        score = 0
        for pattern in category.patterns:
            title_hits = len(re.findall(pattern, title_lower))
            body_hits = len(re.findall(pattern, haystack))
            score += title_hits * 8 + body_hits
        if category.file_name == "toolchain.md" and re.search(r"界面|模式|状态机|调度器|led|数码管|按键", title_lower):
            score -= 5
        if category.file_name == "sensor.md" and re.search(r"学习|概念|网站|底层考试", title_lower):
            score -= 6
        if category.file_name == "programming.md" and re.search(r"ds18b20|ds1302|蜂鸣器|继电器|超声波|建立工程", title_lower):
            score -= 5
        scores.append((score, category))

    scores.sort(key=lambda item: (-item[0], item[1].file_name))
    primary_score, primary_category = scores[0]
    if primary_score == 0:
        primary_category = next(cat for cat in CATEGORIES if cat.file_name == "programming.md")
    secondary = [cat.nav_label for score, cat in scores[1:] if score >= max(primary_score - 1, 2)]
    return primary_category, secondary[:3]


def count_existing_pits(text: str) -> int:
    preserved = text.split(MARKER)[0]
    return len(re.findall(r"^##\s+坑\s+\d+[:：]", preserved, re.MULTILINE))


def build_entry(
    number: int,
    title: str,
    body: str,
    source_path: Path,
    week_label: str,
    secondary_tags: list[str],
) -> str:
    source_link = f"./单片机答疑数据库/{source_path.name}"
    lines = [
        f"## 坑 {number}：{title}",
        "",
        f"> 来源：[{source_path.name}]({source_link})",
        f"> 周期：{week_label}",
    ]
    if secondary_tags:
        lines.append(f"> 关联模块：{' / '.join(secondary_tags)}")
    lines.extend(["", "### 整理记录", "", body.strip(), ""])
    return "\n".join(lines)


def build_generated_section(entries: list[str], count: int) -> str:
    lines = [
        MARKER,
        "",
        f"> 本节按现有知识库模块口径，从 `单片机答疑数据库` 中抽取整理，共补充 {count} 条记录。",
        "> 原始周报仍保留在 `单片机答疑数据库/`，用于追溯与复核。",
        "",
    ]
    lines.extend(entries)
    return "\n".join(lines).rstrip() + "\n"


def ensure_header(path: Path, category: Category) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").split(MARKER)[0].rstrip() + "\n\n"
    return (
        f"# {category.title}\n\n"
        "---\n\n"
        "> 本页由 `单片机答疑数据库` 按模块归档整理生成，原始周报见 [weekly-index.md](./weekly-index.md)。\n\n"
    )


def extract_issue_count(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"^##\s+坑\s+\d+[:：]", text, re.MULTILINE))


def build_weekly_index(files: list[Path], weekly_stats: dict[str, int]) -> str:
    lines = [
        "# 原始周报索引",
        "",
        "---",
        "",
        "> 本页仅做原始资料索引，模块化整理结果请查看侧边栏对应模块页面。",
        "",
        f"- 原始周报数：{len(files)}",
        f"- 抽取问题条目数：{sum(weekly_stats.values())}",
        "",
        "## 周报目录",
        "",
    ]
    for file in files:
        count = weekly_stats[file.name]
        lines.append(f"- [{file.name}](./单片机答疑数据库/{file.name})")
        lines.append(f"  - 收录问题：{count}")
    return "\n".join(lines) + "\n"


def main() -> None:
    report_files = sorted(DB_DIR.glob("*.md"))
    category_entries: dict[str, list[tuple[str, str, Path, str, list[str]]]] = {
        category.file_name: [] for category in CATEGORIES
    }
    weekly_stats: dict[str, int] = {}

    for report_file in report_files:
        text = report_file.read_text(encoding="utf-8")
        week_label = extract_report_week(text, report_file.stem)
        issues = iter_issue_blocks(report_file)
        weekly_stats[report_file.name] = len(issues)
        for title, body in issues:
            category, secondary_tags = classify_issue(title, body)
            category_entries[category.file_name].append(
                (title, body, report_file, week_label, secondary_tags)
            )

    for category in CATEGORIES:
        path = ROOT / category.file_name
        header = ensure_header(path, category)
        existing_count = count_existing_pits(header)
        generated_entries: list[str] = []
        for offset, (title, body, source_path, week_label, secondary_tags) in enumerate(
            category_entries[category.file_name],
            start=1,
        ):
            generated_entries.append(
                build_entry(
                    existing_count + offset,
                    title,
                    body,
                    source_path,
                    week_label,
                    secondary_tags,
                )
            )
        path.write_text(
            header + build_generated_section(generated_entries, len(generated_entries)),
            encoding="utf-8",
        )

    weekly_index = build_weekly_index(report_files, weekly_stats)
    (ROOT / "weekly-index.md").write_text(weekly_index, encoding="utf-8")

    print("生成完成：")
    for category in CATEGORIES:
        print(f"- {category.file_name}: {len(category_entries[category.file_name])} 条")
    print(f"- weekly-index.md: {len(report_files)} 篇周报")


if __name__ == "__main__":
    main()
