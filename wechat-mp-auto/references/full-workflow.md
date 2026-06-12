# 完整执行手册（迁移自 SKILL.md）

# 公众号全流程自动化

**Version**: 1.0
**触发词**: `/公众号` 或 `/wechat-post`

---

## 定位

这不是两个 skill 的简单拼接。这是一条从选题到读者屏幕的完整管道：

```
写作（原创长文体系）→ 排版（Markdown→微信HTML）→ 发布（Chrome CDP自动化）
```

写作阶段调用 `原创长文` skill 的方法论，发布阶段使用本 skill 内置的脚本工具链（源自宝玉发公众号）。

---

## 发布前必须确认

在任何自动发布公众号动作之前，必须先问用户选择发布模式：

- **轻量图文发布**：适合短正文 + 多图，标题≤20字，正文≤1000字，图片≤9张，使用 `wechat-browser.ts`。
- **长文发布**：适合完整 Markdown 长文 + 正文插图，使用 `wechat-article.ts`。

用户没有明确选择前，不要擅自进入发布脚本。

---

## 三阶段总览

| 阶段 | 名称 | 核心动作 | 产物 |
|------|------|---------|------|
| A | 写作 | 选题→调研→五幕逐幕写作→评审→合并润色 | Markdown 长文 |
| B | 排版 | Markdown→微信HTML转换、配图插入、主题选择 | 排版后HTML + 配图 |
| C | 发布 | Chrome自动化登录→粘贴→图片替换→预览/提交 | 公众号文章上线 |

---

## 阶段A：写作（继承原创长文体系）

> **核心原则**：写作阶段完整继承 `原创长文` skill（v3.1）的方法论。以下为精要提取，完整规则见原 skill。

### 写作灵魂

锐利、结构化、强节奏、带攻击性，但不油腻。每篇文章的终极目标：让读者拿走一个清晰、可执行、可复用的「关键结论」。

### Persona 加载

默认加载 `原创长文/personas/赚钱.md`，可通过参数切换：
- `--persona 成长` → personas/成长.md
- `--persona 科技` → personas/科技.md
- `--persona 生活` → personas/生活.md

### 五幕叙事结构

| 幕 | 名称 | 功能 | 字数 | 情绪 |
|----|------|------|------|------|
| 开场 | Hook钩子 | 爆点事件+悬念，3秒定生死 | 500-800 | 引爆 |
| 第一幕 | 冲突建立 | 痛点放大+认知颠覆+核心案例 | 2000-2500 | 升温 |
| 第二幕 | 深度论证 | 方法论+2-3论点+辅助案例 | 3000-4000 | 高原 |
| 第三幕 | 高潮转折 | 全文最强洞见+认知反转 | 2000-2500 | 爆发 |
| 收尾 | 行动收束 | 3-5条行动清单+力量感结尾 | 800-1200 | 落地 |

**AIDA映射**：Hook=Attention → 冲突=Interest → 论证+高潮=Desire → 收尾=Action
**情绪曲线**：引爆 → 升温 → 高原 → 爆发 → 落地（禁止平铺直叙）

### 核心规则（25条精要）

**结构规则**：五幕结构 | 整体AIDA映射 | 收尾统一行动清单 | 长文9000-12000字

**写作风格**：
- 短句(3-15字)40-50% / 中句(16-30字)35-40% / 长句(30字+)10-20%
- 口语化："你品一下这个逻辑"、"说白了"、"来，我拆给你看"
- 疑问句推进、认知反转、比喻形象化
- 分享姿态而非教导姿态

**说服技术**：预设反驳 | 数字具体化 | 管理预期 | 1核心+2-3辅助案例 | 原创金句为主

**开篇策略**：爆点开头必须蹭最近一周核心新闻 | 借势/悬念/认知冲突可选叠加

**口播适配**：读出来必须顺 | 画面感叙事 | 情绪节奏曲线 | 去模板化

### 7 Phase 共创工作流

```
Phase 1: 战略规划 → 用户定方向、选角度、补素材
    ↓
Phase 2: 逐幕写作 → AI写，用户实时纠偏，一幕一过
    ↓
Phase 3: 段落评审 → 6维度评分（≥8.5通过）
    ↓
Phase 4: 合并润色 → AI合并到80-85分，用户精炼到95分
    ↓
Phase 4.5: 配图生成 → 纽约客风格，z-image-turbo生图
    ↓
→ 进入阶段B（排版）
```

**Phase 1 产出**：爆点搜索、4D分析表、五幕大纲、5标题候选、核心案例清单
**Phase 1 用户决策**：核心角度 | 标题选择 | 案例优先级 | 个人素材补充

**Phase 2 流程**：一幕一过，写完即审，用户实时纠偏
**Phase 3 评分维度**：连贯性×1.0 + 行动性×1.0 + 共鸣度×1.2 + AI-tone×1.0 + 节奏感×1.0 + 口播适配度×1.2

**Phase 4 产出**：合并后的完整Markdown长文，含视频精炼预标注

**Phase 4.5 配图规范**：
| 用途 | 比例 | 像素 | 数量 |
|------|------|------|------|
| 头图 | 2.35:1 | 1504x640 | 1张 |
| 正文配图 | 16:9 | 1344x756 | 3-4张 |

---

## 阶段B：排版转换

> 写作完成后，将 Markdown 转换为微信公众号格式的 HTML。

### B1: Markdown 格式化

确保文章 Markdown 符合以下结构：

```markdown
---
title: 文章标题
author: YOUR_AUTHOR_NAME
---

# 标题

正文内容...

![图片描述](./配图/头图.png)

## 小标题

正文内容...
```

### B2: 排版规则

1. **段落**：每段3-5行，重要数据单独成段加粗
2. **金句**：单独成段，增强记忆点
3. **配图节点**：头图(标题下方) → 配图1(冲突幕后) → 配图2(论证中段) → 配图3(高潮幕后) → 配图4(收尾前，可选)
4. **代码块**：前后留白，语法高亮（技术类文章适用）

### B3: 主题选择

使用内置转换引擎（`scripts/md-to-wechat.ts`），支持三套主题：

| 主题 | 风格 | 适用场景 |
|------|------|---------|
| `default` | 标准排版 | 通用 |
| `grace` | 优雅简约 | 深度分析、商业洞察 |
| `simple` | 极简风格 | 技术教程、工具测评 |

**推荐**：深度长文默认用 `grace`

### B4: Markdown→微信HTML转换

```bash
PUBLISH_DIR="${SKILL_DIR}"
npx -y bun ${PUBLISH_DIR}/scripts/md-to-wechat.ts --input article.md --theme grace
```

产出：带微信样式的HTML文件，图片位置标记为 `[[IMAGE_PLACEHOLDER_N]]`

---

## 阶段C：自动化发布

> 使用 Chrome CDP 自动化将排版后的文章发布到微信公众号。

### C1: 前置条件

- Google Chrome 已安装
- `bun` 运行时（通过 `npx -y bun`）
- 首次运行需在打开的浏览器窗口中扫码登录微信公众号后台

### C2: 文章发布（推荐）

适用于完整的深度长文：

```bash
PUBLISH_DIR="${SKILL_DIR}"

# 发布Markdown文章，使用grace主题
npx -y bun ${PUBLISH_DIR}/scripts/wechat-article.ts \
  --markdown article.md \
  --theme grace \
  --author "YOUR_AUTHOR_NAME"

# 指定摘要
npx -y bun ${PUBLISH_DIR}/scripts/wechat-article.ts \
  --markdown article.md \
  --theme grace \
  --author "YOUR_AUTHOR_NAME" \
  --summary "文章摘要"
```

**发布流程**：
1. 解析 Markdown，提取图片引用
2. 生成带主题样式的 HTML，图片位置标记为占位符
3. 打开 Chrome，导航到微信公众号编辑器
4. 粘贴 HTML 内容
5. 逐个替换图片占位符：定位→删除占位文本→粘贴图片
6. 完成预览

### C3: 图文发布（轻量）

适用于短内容配多图：

```bash
PUBLISH_DIR="${SKILL_DIR}"

# 从Markdown和图片目录发布
npx -y bun ${PUBLISH_DIR}/scripts/wechat-browser.ts \
  --markdown article.md \
  --images ./配图/

# 手动指定
npx -y bun ${PUBLISH_DIR}/scripts/wechat-browser.ts \
  --title "标题" \
  --content "内容" \
  --image img1.png --image img2.png
```

**约束**：标题≤20字（超长自动压缩）| 内容≤1000字 | 图片≤9张

### C4: 发布前检核清单

发布前必须确认：
- [ ] 标题选定（公众号标题和封面标题可不同）
- [ ] 摘要撰写（120字内，带悬念）
- [ ] 封面图设置（头图 2.35:1）
- [ ] 正文配图完整（3-4张已插入正确位置）
- [ ] 排版预览无异常（引用块、加粗、列表渲染正确）
- [ ] 原创声明勾选
- [ ] 作者署名正确

---

## 快速开始

### 完整流程（深度长文）

```bash
# Phase 1: 战略规划
/公众号 phase1 --topic "主题" --persona 赚钱

# Phase 2: 逐幕写作（一幕一过）
/公众号 phase2 --act hook
/公众号 phase2 --act 冲突
/公众号 phase2 --act 论证
/公众号 phase2 --act 高潮
/公众号 phase2 --act 收尾

# Phase 3: 段落评审
/公众号 phase3

# Phase 4: 合并润色
/公众号 phase4

# Phase 4.5: 配图生成
/公众号 phase4.5

# Phase 5: 排版转换
/公众号 format --theme grace

# Phase 6: 发布
/公众号 publish --author "YOUR_AUTHOR_NAME"

# Phase 7: 终检
/公众号 check

# Phase 8: 复盘（发布2-3天后）
/公众号 review --data "阅读量/分享/留言数据"
```

### Phase 8: 发布后复盘

**触发时机**：发布2-3天后，用户提供阅读量等数据
**输入**：阅读量、分享数、留言数、在看数、完读率（如有）
**产出**：
1. 本篇效果评分（对比历史数据或同类文章基准）
2. 标题点击率分析（标题策略是否有效）
3. 内容结构复盘（哪一幕留住了人、哪里掉了人）
4. 可迁移的写作经验（更新到 skill 的规则库和 Gotchas）
5. 下一篇选题建议（基于本篇数据反馈）

**目标**：形成"写→发→数据→迭代"的闭环，每一篇文章都让 skill 变得更好

### 快速模式（已有素材直接发）

```bash
# 已有写好的Markdown，直接排版+发布
/公众号 publish --markdown ./my-article.md --theme grace --author "YOUR_AUTHOR_NAME"
```

---

## 输出管理

**项目文件夹**: `YOUR_LOCAL_PATH/Desktop/深度视频文案/`

每篇文章创建独立子文件夹：`YYYYMMDD_文章主题简称/`

```
深度视频文案/
├── 20260324_AI时代副业/
│   ├── 00_参考资料/
│   ├── 01_Phase1_战略规划.md
│   ├── 02_Phase2_逐幕草稿/
│   │   ├── Hook_v1.md
│   │   ├── 冲突_v1.md
│   │   ├── 论证_v1.md
│   │   ├── 高潮_v1.md
│   │   └── 收尾_v1.md
│   ├── 03_Phase3_评审记录.md
│   ├── 04_公众号长文_v1.md          ← 阶段A产物
│   ├── 05_配图/
│   │   ├── 头图.png
│   │   ├── 配图1_冲突.png
│   │   ├── 配图2_论证.png
│   │   ├── 配图3_高潮.png
│   │   └── 配图4_收尾.png
│   ├── 06_排版预览.html             ← 阶段B产物
│   ├── 07_视频文案_v1.md
│   └── 08_终检报告.md
```

---

## 依赖 Skill

| Skill | 路径 | 用途 |
|-------|------|------|
| 原创长文 | `../原创长文/` | 写作方法论、Persona、模板、规则库 |
| (内置) scripts/ | `./scripts/` | 发布脚本、Markdown转换引擎、主题CSS（源自宝玉发公众号） |
| z-image-turbo | `../z-image-turbo/` | 配图生成（纽约客风格） |

---

## Gotchas（踩过的坑）

1. **Phase 2 逐幕纠偏比事后改稿效率高10倍** — 不要跳过用户审阅直接写完全文，每一幕写完立刻过审。AI 在 Phase 2 被纠正过的表达问题，后续幕不再犯
2. **中文路径导致 import.meta.url 编码错误** — 脚本路径含中文字符时，`import.meta.url` 返回 URL 编码路径（%E5%85%AC 之类），导致文件读取失败。修复方案：用 `decodeURIComponent()` 解码，或用 `fileURLToPath()`（render.ts 已正确使用）
3. **osascript Cmd+C 在后台 Chrome 窗口无法复制** — `copyHtmlFromBrowser` 函数用 osascript 发送 Cmd+C，但 Chrome 在后台时按键发到了别的应用，导致正文粘贴为空。修复方案：改用 CDP 的 `document.execCommand('copy')` + `userGesture: true`，不依赖窗口焦点
4. **封面图无法通过脚本自动上传** — 微信公众号编辑器的封面图上传按钮无法被 CDP 自动化操作，需要用户手动上传
5. **[已验证] 首次运行需手动扫码登录** — Chrome CDP 打开独立浏览器实例，首次需扫码。Session 在同一 Chrome profile 下能保持
6. **[待验证] 标题20字限制的自动压缩可能丢关键词** — 微信图文标题严格20字，脚本自动压缩但效果未知，建议手动拟定短标题
7. **去AI味应在全文合并后统一做一次** — 逐幕去AI味会打断写作节奏且合并时还要再润色，等于做两遍无用功
8. **正文禁止出现Markdown语法标记** — 公众号正文里绝对不能出现 `**加粗**`、`# 标题` 等原始Markdown语法。终稿必须是纯净的自然文本，加粗/标题等格式由排版引擎（md-to-wechat.ts）转换为HTML实现，不是留在正文里给读者看的


---

<!-- article-posting.md -->

# Article Posting (文章发表)

Post markdown articles to WeChat Official Account with full formatting support.

## Usage

```bash
# Post markdown article
npx -y bun ./scripts/wechat-article.ts --markdown article.md

# With theme
npx -y bun ./scripts/wechat-article.ts --markdown article.md --theme grace

# With explicit options
npx -y bun ./scripts/wechat-article.ts --markdown article.md --author "作者名" --summary "摘要"
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--markdown <path>` | Markdown file to convert and post |
| `--theme <name>` | Theme: default, grace, or simple |
| `--title <text>` | Override title (auto-extracted from markdown) |
| `--author <name>` | Author name (default: 宝玉) |
| `--summary <text>` | Article summary |
| `--html <path>` | Pre-rendered HTML file (alternative to markdown) |
| `--profile <dir>` | Chrome profile directory |

## Markdown Format

```markdown
---
title: Article Title
author: Author Name
---

# Title (becomes article title)

Regular paragraph with **bold** and *italic*.

## Section Header

![Image description](./image.png)

- List item 1
- List item 2

> Blockquote text

[Link text](https://example.com)
```

## Image Handling

1. **Parse**: Images in markdown are replaced with `[[IMAGE_PLACEHOLDER_N]]`
2. **Render**: HTML is generated with placeholders in text
3. **Paste**: HTML content is pasted into WeChat editor
4. **Replace**: For each placeholder:
   - Find and select the placeholder text
   - Scroll into view
   - Press Backspace to delete the placeholder
   - Paste the image from clipboard

## Scripts

| Script | Purpose |
|--------|---------|
| `wechat-article.ts` | Main article publishing script |
| `md-to-wechat.ts` | Markdown to HTML with placeholders |
| `md/render.ts` | Markdown rendering with themes |

## Example Session

```
User: /post-to-wechat --markdown ./article.md

Claude:
1. Parses markdown, finds 5 images
2. Generates HTML with placeholders
3. Opens Chrome, navigates to WeChat editor
4. Pastes HTML content
5. For each image:
   - Selects [[IMAGE_PLACEHOLDER_1]]
   - Scrolls into view
   - Presses Backspace to delete
   - Pastes image
6. Reports: "Article composed with 5 images."
```


---

<!-- image-text-posting.md -->

# Image-Text Posting (图文发表)

Post image-text messages with multiple images to WeChat Official Account.

## Usage

```bash
# Post with images and markdown file (title/content extracted automatically)
npx -y bun ./scripts/wechat-browser.ts --markdown source.md --images ./images/

# Post with explicit title and content
npx -y bun ./scripts/wechat-browser.ts --title "标题" --content "内容" --image img1.png --image img2.png

# Save as draft
npx -y bun ./scripts/wechat-browser.ts --markdown source.md --images ./images/ --submit
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--markdown <path>` | Markdown file for title/content extraction |
| `--images <dir>` | Directory containing images (sorted by name) |
| `--title <text>` | Article title (max 20 chars, auto-compressed if too long) |
| `--content <text>` | Article content (max 1000 chars, auto-compressed if too long) |
| `--image <path>` | Single image file (can be repeated) |
| `--submit` | Save as draft (default: preview only) |
| `--profile <dir>` | Chrome profile directory |

## Auto Title/Content from Markdown

When using `--markdown`, the script:

1. **Parses frontmatter** for title and author:
   ```yaml
   ---
   title: 文章标题
   author: 作者名
   ---
   ```

2. **Falls back to H1** if no frontmatter title:
   ```markdown
   # 这将成为标题
   ```

3. **Compresses title** to 20 characters if too long:
   - Original: "如何在一天内彻底重塑你的人生"
   - Compressed: "一天彻底重塑你的人生"

4. **Extracts first paragraphs** as content (max 1000 chars)

## Image Directory Mode

When using `--images <dir>`:

- All PNG/JPG files in directory are uploaded
- Files are sorted alphabetically by name
- Naming convention: `01-cover.png`, `02-content.png`, etc.

## Constraints

| Field | Max Length | Notes |
|-------|------------|-------|
| Title | 20 chars | Auto-compressed if longer |
| Content | 1000 chars | Auto-compressed if longer |
| Images | 9 max | WeChat limit |

## Example Session

```
User: /post-to-wechat --markdown ./article.md --images ./xhs-images/

Claude:
1. Parses markdown meta:
   - Title: "如何在一天内彻底重塑你的人生" → "一天内重塑你的人生"
   - Author: from frontmatter or default
2. Extracts content from first paragraphs
3. Finds 7 images in xhs-images/
4. Opens Chrome, navigates to WeChat "图文" editor
5. Uploads all images
6. Fills title and content
7. Reports: "Image-text posted with 7 images."
```

## Scripts

| Script | Purpose |
|--------|---------|
| `wechat-browser.ts` | Main image-text posting script |
| `cdp.ts` | Chrome DevTools Protocol utilities |
| `copy-to-clipboard.ts` | Clipboard operations |
