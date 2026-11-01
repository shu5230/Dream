#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
越狱源索引生成器（纯 Python，跨平台，Windows 原生可直接运行）

功能：
  - 扫描 debs/ 下所有 .deb
  - 解析每个 deb 的控制信息（无需 dpkg）
  - 生成 Packages / Packages.gz / Packages.bz2 / Release
  - 可被 Sileo / Cydia / Zebra / Sileo(APT) 直接添加

用法：
  python update_repo.py
依赖：仅 Python 3 标准库（无第三方依赖）
"""
import os
import io
import json
import glob
import gzip
import bz2
import hashlib
import tarfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DEBS_DIR = os.path.join(ROOT, "debs")
CONFIG = os.path.join(ROOT, "repo.json")


def load_config():
    default = {
        "origin": "MyJailbreakRepo",
        "label": "My Jailbreak Repo",
        "suite": "stable",
        "components": "main",
        "architectures": "iphoneos-arm",
        "description": "个人 iOS 越狱插件源",
    }
    if os.path.exists(CONFIG):
        with open(CONFIG, "r", encoding="utf-8") as f:
            default.update(json.load(f))
    return default


def file_hashes(path):
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            md5.update(chunk)
            sha.update(chunk)
            size += len(chunk)
    return md5.hexdigest(), sha.hexdigest(), size


def parse_ar(data):
    """解析 .deb 的 ar 容器，返回 {成员名: 字节内容}。"""
    if data[:8] != b"!<arch>\n":
        raise ValueError("不是有效的 .deb (ar) 文件")
    offset = 8
    members = {}
    while offset < len(data):
        if offset + 60 > len(data):
            break
        header = data[offset:offset + 60]
        name = header[0:16].decode("ascii", "replace").strip().rstrip("/")
        size = int(header[48:58].decode("ascii", "replace").strip() or "0")
        offset += 60
        content = data[offset:offset + size]
        members[name] = content
        offset += size
        if size % 2 == 1:
            offset += 1  # ar 奇数长度补 1 字节
    return members


def decompress_control(members):
    for key in list(members.keys()):
        if key.startswith("control.tar"):
            raw = members[key]
            if key.endswith(".gz"):
                return gzip.decompress(raw)
            if key.endswith(".xz"):
                import lzma
                return lzma.decompress(raw)
            if key.endswith(".zst"):
                raise NotImplementedError("control.tar.zst 需 zstandard 库，请改用 .gz/.xz")
            return raw
    raise ValueError("deb 内找不到 control.tar.*")


def read_control_text(deb_path):
    with open(deb_path, "rb") as f:
        data = f.read()
    members = parse_ar(data)
    ctrl = decompress_control(members)
    tar = tarfile.open(fileobj=io.BytesIO(ctrl))
    for m in tar.getmembers():
        base = m.name.lstrip("./")
        if base == "control" or base.endswith("/control"):
            return tar.extractfile(m).read().decode("utf-8", "replace")
    # 兜底：找名字含 control 的文件
    for m in tar.getmembers():
        if "control" in m.name and m.isfile():
            return tar.extractfile(m).read().decode("utf-8", "replace")
    raise ValueError("control.tar 内找不到 control 文件")


def normalize_stanza(control_text, deb_relpath, size, md5, sha):
    """把 control 文本整理成 Packages 的一个 stanza，并追加文件元信息。"""
    lines = [ln.rstrip() for ln in control_text.splitlines() if ln.strip() != ""]
    # 防止重复追加
    drop = {"filename", "size", "md5sum", "sha256"}
    out = []
    for ln in lines:
        key = ln.split(":", 1)[0].strip().lower()
        if key in drop:
            continue
        out.append(ln)
    out.append(f"Filename: {deb_relpath}")
    out.append(f"Size: {size}")
    out.append(f"MD5sum: {md5}")
    out.append(f"SHA256: {sha}")
    return "\n".join(out)


def build_packages():
    stanzas = []
    deb_files = sorted(glob.glob(os.path.join(DEBS_DIR, "*.deb")))
    if not deb_files:
        print("[warn] debs/ 目录为空，将生成空源（可正常被添加，只是没有包）。")
    for deb in deb_files:
        base = os.path.basename(deb)
        rel = "debs/" + base  # APT 相对源根的路径
        md5, sha, size = file_hashes(deb)
        ctrl = read_control_text(deb)
        stanza = normalize_stanza(ctrl, rel, size, md5, sha)
        stanzas.append(stanza)
        print(f"[ok] {base}")
    packages_text = "\n\n".join(stanzas)
    if packages_text:
        packages_text += "\n"
    return packages_text


def write_release(cfg, files):
    """files: [{name, md5, sha256, size}]"""
    lines = [
        f"Origin: {cfg['origin']}",
        f"Label: {cfg['label']}",
        f"Suite: {cfg['suite']}",
        f"Components: {cfg['components']}",
        f"Architectures: {cfg['architectures']}",
        f"Description: {cfg['description']}",
        "",
        "MD5Sum:",
    ]
    for f in files:
        lines.append(f" {f['md5']} {f['size']} {f['name']}")
    lines.append("")
    lines.append("SHA256:")
    for f in files:
        lines.append(f" {f['sha256']} {f['size']} {f['name']}")
    lines.append("")
    return "\n".join(lines)


def main():
    cfg = load_config()
    packages_text = build_packages()

    pkg_path = os.path.join(ROOT, "Packages")
    with open(pkg_path, "w", encoding="utf-8") as f:
        f.write(packages_text)
    pkg_gz = gzip.compress(packages_text.encode("utf-8"), 9)
    with open(os.path.join(ROOT, "Packages.gz"), "wb") as f:
        f.write(pkg_gz)
    pkg_bz2 = bz2.compress(packages_text.encode("utf-8"), 9)
    with open(os.path.join(ROOT, "Packages.bz2"), "wb") as f:
        f.write(pkg_bz2)

    files = []
    for name, blob in (("Packages", open(pkg_path, "rb").read()),
                       ("Packages.gz", pkg_gz),
                       ("Packages.bz2", pkg_bz2)):
        files.append({
            "name": name,
            "md5": hashlib.md5(blob).hexdigest(),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "size": len(blob),
        })

    release_text = write_release(cfg, files)
    with open(os.path.join(ROOT, "Release"), "w", encoding="utf-8") as f:
        f.write(release_text)

    print(f"[done] 已生成 Packages / Packages.gz / Packages.bz2 / Release")
    print(f"       源地址（GitHub Pages）: https://<你的用户名>.github.io/<仓库名>/")
    print(f"       包数量: {len([s for s in packages_text.split('\\n\\n') if s.strip()])}")


if __name__ == "__main__":
    main()
