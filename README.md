# 越狱源（GitHub Pages 托管）

一个可被 Sileo / Cydia / Zebra 添加的 iOS 越狱软件源。索引由纯 Python 脚本生成，**无需在本机安装 dpkg**。

## 目录结构

```
.
├── debs/                 # 把你的 .deb 放这里（rootless/Dopamine 用 /var/jb 布局）
├── update_repo.py        # 索引生成器（跨平台，仅标准库）
├── repo.json             # 源元信息（改这里自定义源名/描述）
├── Packages             # 自动生成
├── Packages.gz          # 自动生成
├── Packages.bz2         # 自动生成
├── Release              # 自动生成
├── index.html           # GitHub Pages 展示页
└── .github/workflows/   # 可选：push 时自动重建并部署
```

## 本地使用（Windows / macOS / Linux 通用）

1. 把编译好的 `.deb` 放进 `debs/`。
2. 运行：
   ```bash
   python update_repo.py
   ```
   会扫描 `debs/` 下所有 deb，生成 `Packages` / `Packages.gz` / `Packages.bz2` / `Release`。
3. 提交并 push 到 GitHub：
   ```bash
   git add .
   git commit -m "add packages"
   git push
   ```

## 启用 GitHub Pages（两种选法）

### 方式 A：分支根目录（最简单）
仓库 Settings → Pages → Source 选 **main** 分支、**/ (root)** 目录 → Save。
源地址即 `https://<用户名>.github.io/<仓库名>/`。

### 方式 B：GitHub Actions 自动部署（推荐，零手动）
1. 仓库 Settings → Pages → Source 选 **GitHub Actions**。
2. 直接 push（含 `.deb` 或改 `repo.json`），`deploy.yml` 会自动跑 `update_repo.py` 并部署。
   无需本地生成索引，也无需手动 commit 索引文件。

## 在越狱设备上添加源

- **Sileo / Zebra**：「Sources → + → 输入源 URL」填
  `https://<用户名>.github.io/<仓库名>/`
- 一键添加链接（放网页/聊天里）：
  `sileo://source/https://<用户名>.github.io/<仓库名>/`
- **Cydia**：「Sources → Edit → Add」填同样的 URL。

## 关于 rootless（Dopamine / roothide）

- 你的 tweak deb 内部文件应装在 `/var/jb/...`，control 里的 `Architecture` 通常仍是 `iphoneos-arm`。
- `repo.json` 的 `architectures` 保持 `iphoneos-arm` 即可，Sileo 会按包内实际路径安装。
- 若需区分 rootless / rooted，可在 `deps/` 之外另开组件，或给包名加后缀区分。

## 自定义

编辑 `repo.json`：
- `origin` / `label`：源显示名
- `description`：源描述
- `suite` / `components` / `architectures`：一般保持默认
