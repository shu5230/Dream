# 把 .deb 放在这个目录

- 直接把编译好的 `.deb` 文件丢进 `debs/`（保持 `.deb` 扩展名）。
- rootless（Dopamine / roothide）插件的 deb 内部应装在 `/var/jb/...`。
- 放好后运行 `python update_repo.py` 重建索引（或交给 GitHub Actions 自动处理）。
- 本目录下的非 `.deb` 文件会被脚本忽略。
