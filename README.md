# iOS 越狱源（GitHub Pages 托管）— 完整搭建教程

一个可被 **Sileo / Zebra / Cydia** 添加的 iOS 越狱软件源。索引由纯 Python 脚本生成，**无需在本机安装 dpkg**，Windows / macOS / Linux 通用。本教程带你从零把它部署到 GitHub 并上线。

本仓库对应账号：**shu5230**，仓库名：**dream**，源地址：`https://shu5230.github.io/dream/`

---

## 一、前置条件

| 项目 | 说明 |
|---|---|
| GitHub 账号 | shu5230（已注册） |
| Git | 本机已装（Windows 装 Git for Windows 即可，自带 Git Credential Manager） |
| Python 3 | 用于本地生成索引（`python update_repo.py`）；用 GitHub Actions 自动部署时可不装 |
| 认证方式（三选一） | ① Git Credential Manager（弹窗登录，最省事）② SSH key ③ Personal Access Token |

---

## 二、目录结构（当前已就绪）

```
jailbreak-repo/
├── debs/                  # 把你的 .deb 放这里（rootless/Dopamine 用 /var/jb 布局）
├── update_repo.py         # 索引生成器（跨平台，仅标准库）
├── repo.json              # 源元信息（改这里自定义源名/描述）
├── index.html             # GitHub Pages 展示页（自动填源 URL + Sileo 一键添加）
├── README.md              # 本文件
├── .gitignore
├── Packages / .gz / .bz2  # 由脚本生成（不要手改）
├── Release                # 由脚本生成（不要手改）
└── .github/workflows/
    └── deploy.yml         # 可选：push 时自动重建索引并部署 Pages
```

> 本仓库已 `git init` 并提交首个 commit，且已关联远端 `origin` 到 `https://github.com/shu5230/dream.git`。你只需做「建空仓库 + 推送 + 开 Pages」三步。

---

## 三、完整搭建步骤

### 步骤 1：在 GitHub 网页创建空仓库

1. 打开 <https://github.com/new>。
2. **Repository name**：填 `dream`（这就是源 URL 的一部分）。
3. **Visibility**：选 **Public**（私有仓库的 GitHub Pages 不可被外部访问）。
4. **不要**勾选 "Add a README file" / ".gitignore" / "Choose a license" —— 本地已有这些文件，勾了会冲突。
5. 点 **Create repository**。创建后页面会显示一个空仓库和一堆命令，不用管它。

### 步骤 2：关联远端仓库（已帮你做好，可跳过）

本仓库已执行：
```bash
git remote add origin https://github.com/shu5230/dream.git
```
若需改用 SSH：
```bash
git remote set-url origin git@github.com:shu5230/dream.git
```
> 注：本机 git 全局配了 `insteadOf` 代理，`git remote -v` 可能显示为 `https://ghproxy.net/...` 前缀，这是正常的，push 会走代理加速。

### 步骤 3：推送到 GitHub

```bash
git push -u origin main
```

认证按你选的方式：

- **Git Credential Manager（HTTPS）**：首次 push 会弹出浏览器让你登录 GitHub，登录后自动记住，以后无需重复。
- **SSH**：若 `~/.ssh` 已配置且公钥加在 GitHub 上，直接成功。
- **Personal Access Token（HTTPS 备用）**：若弹窗登录不可用，去 GitHub → Settings → Developer settings → **Fine-grained PAT**（或 Classic PAT，勾 `repo` 权限、设短期过期），生成后用 token 当密码填；或：
  ```bash
  git remote set-url origin https://<你的TOKEN>@github.com/shu5230/dream.git
  git push -u origin main
  ```
  > token 用完建议立刻撤销（Settings → Developer settings → 删除该 PAT）。

> 若 `git push` 因代理（ghproxy）不支持写操作而失败，临时绕过：
> `git -c url."https://github.com/".insteadOf="https://ghproxy.net/https://github.com/" push -u origin main`

推送成功后，GitHub 仓库里就能看到所有文件。

### 步骤 4：启用 GitHub Pages（二选一）

#### 方式 A：main 分支根目录（最简单，需本地生成索引）

1. 本地生成索引并提交：
   ```bash
   python update_repo.py
   git add .
   git commit -m "build index"
   git push
   ```
2. 仓库 **Settings → Pages → Source** 选 **main** 分支、**/ (root)** 目录 → Save。
3. 源地址：`https://shu5230.github.io/dream/`

#### 方式 B：GitHub Actions 自动部署（推荐，零手动）

1. 仓库 **Settings → Pages → Source** 选 **GitHub Actions**。
2. 之后你只要 `git push` 任意改动（新增 `.deb`、改 `repo.json` 等），`deploy.yml` 会自动跑 `update_repo.py` 并把整个站点部署到 Pages。**无需本地生成索引、无需手动提交索引文件**。
3. 源地址同样是 `https://shu5230.github.io/dream/`。

> 选 A 还是 B？想完全本地可控选 A；想"丢个 deb 进去 push 就自动上线"选 B。二选一即可，不要同时开（B 会用独立的 Pages 部署，A 的 main/root 设置可忽略）。

### 步骤 5：验证源是否可用

- **在越狱设备上**：Sileo/Zebra → Sources → + → 输入 `https://shu5230.github.io/dream/`，能正常添加且能看到包即为成功。
- **快速自查**：浏览器打开 `https://shu5230.github.io/dream/Packages`，应能看到索引文本（`Package:` 开头的段落）。
- **网页展示**：打开 `https://shu5230.github.io/dream/` 会显示 `index.html` 的展示页，含「在 Sileo 中添加」一键链接（`sileo://source/https://shu5230.github.io/dream/`）。

---

## 四、日常使用（往源里加包）

1. 把编译好的 `.deb` 放进 `debs/`。
2. 若用**方式 A**：本地 `python update_repo.py` → `git add .` → `git commit` → `git push`。
   若用**方式 B**：直接 `git add .` → `git commit` → `git push`（CI 自动重建索引并部署）。
3. 设备上刷新源即可看到新包。

---

## 五、关于 rootless（Dopamine / roothide）

- tweak 的 deb 内部文件应装在 `/var/jb/...`，control 里的 `Architecture` 通常仍是 `iphoneos-arm`。
- `repo.json` 的 `architectures` 保持 `iphoneos-arm` 即可，Sileo 会按包内实际路径安装。
- 若需区分 rootless / rooted，可给包名加后缀或分组件管理。

---

## 六、自定义源信息

编辑 `repo.json` 后重新生成索引（`python update_repo.py` 或等 CI）即可生效：

| 字段 | 含义 |
|---|---|
| `origin` / `label` | 源显示名 |
| `description` | 源描述（UTF-8，现代客户端正常显示） |
| `suite` / `components` / `architectures` | 一般保持默认 |

---

## 七、常见问题

- **`LF will be replaced by CRLF` 警告**：Windows 上 Git 自动换行转换的提示，**无害**，不影响源功能。
- **中文在 Release/Packages 里显示为乱码？** 文件本身以 UTF-8 写入，现代 Sileo/Zebra 正常解析；若旧客户端异常，把 `repo.json` 的 `description` 改成英文即可。
- **推不上去提示认证失败**：GitHub 自 2021 年起已**停用账号密码**做 git 认证，必须用 PAT 或 SSH。检查你用的是否为密码（应改用 token/SSH）。
- **私有仓库无法被 Sileo 添加**：Pages 仅对 Public 仓库的外部访问开放，请确认仓库为 Public。
- **添加源后看不到包**：确认 `Packages` 已生成且已 push；方式 A 需本地生成索引并提交，方式 B 需等 CI 运行完成（仓库 Actions 页可看进度）。
