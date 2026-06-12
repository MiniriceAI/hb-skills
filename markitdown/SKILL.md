---
name: markitdown
description: Convert files (PDF, Word, Excel, PPT, HTML, images, audio) to Markdown using Microsoft MarkItDown CLI. Use when user wants to convert or extract text from documents.
---

# 文档转 Markdown（MarkItDown）

## 核心定位

调用 Microsoft MarkItDown 将各类文件转换为 Markdown 格式。支持 PDF、Word (.docx)、Excel (.xlsx)、PowerPoint (.pptx)、HTML 网页、图片（含 EXIF）、音频（含元数据）、ZIP 压缩包等格式。不适用于需要保留原始排版的场景。

---

## 触发场景

- 用户说"帮我把这个 PDF / Word / Excel 转成 Markdown"
- 用户说"用 markitdown 转换文件"
- 用户想提取文档内容为纯文本或 Markdown 格式
- 用户说"把这个文件转换一下"并提供了文件路径

---

## 工作流

### Step 1：确认文件路径

检查用户提供的文件路径是否存在：

```bash
ls -lh <文件路径>
```

如果文件不存在，告知用户并请其确认路径。

### Step 2：执行转换

```bash
markitdown <文件路径>
```

如果用户想保存到文件：

```bash
markitdown <输入文件> > <输出文件.md>
```

### Step 3：处理转换结果

- 若输出为空或报错，检查文件格式是否受支持
- 若文件为图片且需要 AI 描述，需配置 Azure OpenAI（见 Gotchas）
- 若文件为音频，提取的是元数据而非语音转写内容

### Step 4：呈现结果

- 内容较短（<100 行）：直接展示转换后的 Markdown
- 内容较长：展示前 50 行并说明总行数，询问是否保存到文件
- 已保存到文件：告知保存路径

---

## 输出格式

转换成功时的回复格式：

```
✅ 转换完成：<原文件名>

---

<Markdown 内容（前 50 行，超出时截断）>

---

共 {n} 行。已保存到：<输出路径>（若有）
```

---

## Gotchas

**图片 AI 描述需要额外配置**
- 默认转换图片只提取 EXIF 元数据，不生成 AI 描述
- 需要 AI 描述时，要配置 Azure OpenAI API Key，通过 Python API 调用（非 CLI）：
  ```python
  from markitdown import MarkItDown
  from openai import AzureOpenAI
  client = AzureOpenAI(...)
  md = MarkItDown(llm_client=client, llm_model="gpt-4o")
  ```

**Excel 多 Sheet 处理**
- MarkItDown 会转换所有 Sheet，每个 Sheet 生成一个 Markdown 表格
- 大型 Excel 文件输出可能很长，建议保存到文件

**PowerPoint 转换局限**
- 只提取文字内容，图表、SmartArt、嵌入图片的文字可能丢失
- 转换后告知用户可能存在内容缺失

**PDF 扫描件无法提取文字**
- MarkItDown 不含 OCR，扫描版 PDF 输出为空
- 遇到此情况建议使用其他 OCR 工具（如 tesseract）

**路径含空格时需加引号**
- 执行命令时路径含空格必须用引号包裹：`markitdown "my file.pdf"`

**版本确认**
- 当前安装版本：markitdown 0.1.5
- 验证命令：`markitdown --version`
