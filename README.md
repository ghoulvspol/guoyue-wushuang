# 国乐无双

国乐无双是一款可安装的中国传统乐器 APP：提供智能听音识器、真实乐器照片图鉴、结构拆解、分类检索、流派传承与移动端 PWA 安装体验。

作者：滔哥开发

## 核心能力

- **听音识器**：上传 wav/mp3/m4a/flac/ogg/aac，后端调用本地智能模型完成传统乐器识别。
- **百器图鉴**：覆盖古筝、琵琶、二胡、扬琴、笛子、唢呐、古琴、中阮、三弦、箜篌、笙、箫、埙、葫芦丝、马头琴、编钟、钹等 17 种乐器。
- **真实照片**：本地缓存 Wikimedia Commons 开放授权照片，并在页面展示作者与授权信息。
- **分类搜索**：支持弹拨、拉弦、击弦、吹管、打击分类筛选和关键词搜索。
- **结构工坊**：以交互卡片模拟沉浸式拆解，展示乐器组成部件。
- **可安装 APP**：内置 manifest 与 service worker，支持 Chrome/Edge 安装，iOS 可添加到主屏幕。

## 快速安装

```bash
cd /Users/harden/workspace/guoyue-wushuang
./scripts/install.sh
./scripts/run.sh
```

打开：<http://127.0.0.1:8088/?v=6>

## 识别模型目录

默认会查找相邻的本地识别模型项目。如果模型项目在其他位置：

```bash
GUOYUE_RECOGNITION_DIR=/path/to/model-project ./scripts/run.sh
```

首次加载模型会下载或读取本地缓存，耗时取决于网络和设备环境。

## 图片授权

图片授权记录保存在：`data/image_attributions.json`，页面通过 `/api/image-attributions` 展示来源。

## 项目结构

```text
app/main.py                  FastAPI 服务与识别 API
app/recognition_bridge.py    本地识别模型桥接层
app/instruments.py           乐器图鉴内容数据
app/static/photos/           真实乐器照片
app/static/                  PWA 前端、样式、图标、Service Worker
scripts/install.sh           一键安装依赖
scripts/run.sh               启动服务
```
