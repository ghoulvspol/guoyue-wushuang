# 国乐无双

> 可安装的中国传统乐器识别与百器图鉴 APP。  
> 作者：滔哥开发

国乐无双面向传统乐器学习、展示与声纹识别场景，提供智能听音识器、真实乐器照片图鉴、分类检索、结构拆解、流派技法介绍与 PWA 安装体验。项目采用 FastAPI 后端 + 原生前端 PWA，支持本地部署、桌面浏览器访问和移动端添加到主屏幕。

![国乐无双截图](screenshots/atlas-v6.png)

## 在线访问

- GitHub Pages：<https://ghoulvspol.github.io/guoyue-wushuang/>
- GitHub 仓库：<https://github.com/ghoulvspol/guoyue-wushuang>

> GitHub Pages 是静态展示版，支持百器图鉴、真实照片、搜索筛选和 PWA 安装；音频识别需要按下方步骤本地启动后端。

## 功能亮点

- **智能听音识器**：上传 `wav/mp3/m4a/flac/ogg/aac` 音频，调用本地识别模型返回乐器类别。
- **百器图鉴**：内置 `17` 种传统乐器资料，覆盖弹拨、拉弦、击弦、吹管、打击五大门类。
- **真实照片展示**：本地缓存开放授权乐器照片，提升器物质感和学习体验。
- **分类与搜索**：支持按门类筛选，也支持输入中文、拼音或技法关键词搜索。
- **结构工坊**：以照片 + 层叠部件卡片展示乐器结构、技法与传承流派。
- **可安装 PWA**：内置 `manifest.webmanifest` 和 `service-worker.js`，支持 GitHub Pages 静态部署，也支持浏览器安装到桌面或手机主屏幕。
- **本地优先部署**：无需数据库，启动后即可访问；识别模型目录可通过环境变量配置。

## 乐器清单

| 门类 | 乐器 |
| --- | --- |
| 弹拨 | 古筝、琵琶、古琴、中阮、三弦、箜篌 |
| 拉弦 | 二胡、马头琴 |
| 击弦 | 扬琴 |
| 吹管 | 笛子、唢呐、笙、箫、埙、葫芦丝 |
| 打击 | 编钟、钹 |

## 技术栈

- **后端**：FastAPI、Uvicorn、Python Multipart
- **识别桥接**：本地智能识别模型项目，通过 `app/recognition_bridge.py` 动态调用
- **前端**：原生 HTML/CSS/JavaScript，无前端构建依赖
- **PWA**：Web App Manifest、Service Worker、本地缓存
- **素材**：Wikimedia Commons 开放授权图片，本地缓存并保留授权记录

## 项目结构

```text
.
├── app/
│   ├── main.py                  # FastAPI 服务、静态资源、API 路由
│   ├── recognition_bridge.py    # 本地识别模型桥接层
│   ├── instruments.py           # 乐器图鉴数据
│   └── static/
│       ├── index.html           # PWA 主页面
│       ├── app.js               # 前端交互逻辑
│       ├── styles.css           # 视觉样式
│       ├── manifest.webmanifest # PWA 安装配置
│       ├── service-worker.js    # 离线缓存
│       └── photos/              # 真实乐器照片
├── data/
│   └── image_attributions.json  # 图片授权与来源记录，页面不展示
├── scripts/
│   ├── install.sh               # 一键安装依赖
│   ├── run.sh                   # 启动服务
│   └── fetch_commons_images.py  # 重新抓取开放授权照片
├── screenshots/
│   └── atlas-v6.png             # 页面截图
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ghoulvspol/guoyue-wushuang.git
cd guoyue-wushuang
```

### 2. 安装依赖

```bash
./scripts/install.sh
```

脚本会创建 `.venv` 并安装 `requirements.txt` 中的依赖。

### 3. 启动服务

```bash
./scripts/run.sh
```

默认访问地址：

```text
http://127.0.0.1:8088/?v=7
```

## 识别模型配置

默认会尝试查找相邻目录中的本地识别模型项目。如果你的模型项目放在其他位置，请设置：

```bash
GUOYUE_RECOGNITION_DIR=/path/to/model-project ./scripts/run.sh
```

兼容旧环境变量：

```bash
CTIS_DIR=/path/to/model-project ./scripts/run.sh
```

首次识别可能需要加载模型和缓存，耗时取决于设备与网络环境。

## 常用命令

```bash
# 安装依赖
./scripts/install.sh

# 启动服务
./scripts/run.sh

# 自定义端口
GUOYUE_PORT=9000 ./scripts/run.sh

# 自定义监听地址
GUOYUE_HOST=127.0.0.1 ./scripts/run.sh

# 重新抓取开放授权照片
./scripts/fetch_commons_images.py
```

## API 说明

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | PWA 主页面 |
| `GET` | `/api/health` | 服务健康检查 |
| `GET` | `/api/instruments` | 乐器图鉴数据 |
| `GET` | `/api/models` | 当前可用识别模型 |
| `POST` | `/api/recognize` | 上传音频并识别乐器 |
| `GET` | `/api/image-attributions` | 图片授权记录 |

### 识别接口示例

```bash
curl -F "audio=@example.wav" http://127.0.0.1:8088/api/recognize
```

返回示例：

```json
{
  "ok": true,
  "status": "Success",
  "filename": "input.wav",
  "instrument": "Nan2_yin1_dong4_xiao1",
  "model": "regnet_y_32gf_cqt_2024-12-02_15-05-57"
}
```

## PWA 安装

### 桌面 Chrome / Edge

1. 打开 `http://127.0.0.1:8088/?v=7`
2. 点击浏览器地址栏右侧的安装图标，或使用页面中的“安装 APP”按钮
3. 安装后可像桌面应用一样打开

### iOS Safari

1. 用 Safari 打开页面
2. 点击分享按钮
3. 选择“添加到主屏幕”

## 测试与验证

已完成的验证包括：

- Python 文件编译检查：`python3 -m py_compile app/main.py app/instruments.py app/recognition_bridge.py`
- 前端语法检查：`node --check app/static/app.js`
- `/api/instruments` 返回 `17` 种乐器、`5` 个门类
- `/api/image-attributions` 返回 `17` 条授权记录
- `17` 张真实照片全部可读且尺寸满足展示要求
- Playwright 验证图鉴渲染、搜索、分类筛选和未选音频提示
- 真实音频上传识别接口返回 `ok: true`
- PWA `manifest` 与 `service-worker` 可正常访问

## 图片授权

乐器照片来自 Wikimedia Commons 等开放授权来源，已经缓存到 `app/static/photos/`。授权信息保存在：

```text
data/image_attributions.json
```

页面不展示来源区块，但项目保留授权记录以便审计。

## 部署建议

### GitHub Pages

项目已配置 `.github/workflows/pages.yml`，推送到 `main` 后会自动将 `app/static` 打包为静态站点并部署到 GitHub Pages。静态站点会使用 `app/static/data/instruments.json` 作为图鉴数据源。

### 本地长期运行

可以使用 `nohup`：

```bash
nohup ./scripts/run.sh > guoyue.log 2>&1 & echo $! > guoyue.pid
```

停止服务：

```bash
kill $(cat guoyue.pid)
```

### 服务器部署

建议使用反向代理暴露服务：

```bash
GUOYUE_HOST=127.0.0.1 GUOYUE_PORT=8088 ./scripts/run.sh
```

再通过 Nginx / Caddy 将公网域名转发到 `127.0.0.1:8088`。

## 注意事项

- 当前项目不包含大型识别模型权重，识别能力依赖本地模型项目。
- 图片文件已本地缓存，仓库体积约数 MB，适合直接部署。
- 如果浏览器缓存旧页面，可访问 `/?v=7` 或强制刷新。

## 开发者

- 作者：滔哥开发
- 项目名：国乐无双
