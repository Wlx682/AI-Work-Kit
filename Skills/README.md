# Skills

这里是项目 Skill 的唯一真理源。每个 Skill 描述一项可独立调用的能力，不代表部门、阶段或标准路径。

AI 根据当前目标选择最小必要能力；不得因为调用了某个 Skill 而要求补齐前置/后续 Skill、Plan 或模板。Skill 内只保留能改变执行质量的领域知识、权限边界和结果证据。

项目入口由 `scripts/sync-skills.py` 生成：

```bash
python3 scripts/sync-skills.py --sync
python3 scripts/sync-skills.py --check
```

增加或修改 Skill 后运行 `python3 scripts/verify-kit.py`。只有人明确要求部署到用户级目录时才使用 `--global`。
