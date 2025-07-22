# 解决 Pylance 导入错误

## 项目结构

```
mda/                        # 项目根目录
├── pim-engine/            # PIM 执行引擎
│   ├── src/
│   └── tests/
├── pim-compiler/          # PIM 编译器
│   ├── src/
│   │   ├── compiler/
│   │   └── cli/
│   └── tests/
├── pyrightconfig.json     # Pyright/Pylance 配置
└── .vscode/              
    └── settings.json      # VS Code 配置
```

## 已配置的内容

### 1. pyrightconfig.json (项目根目录)
- 包含了 `pim-compiler/src` 和 `pim-compiler/tests`
- 添加了 `./pim-compiler/src` 到 `extraPaths`
- 为 pim-compiler 配置了执行环境

### 2. .vscode/settings.json
- 添加了 `${workspaceFolder}/pim-compiler/src` 到 `python.analysis.extraPaths`
- 包含了 `pim-compiler/tests` 到 pytest 路径

## 解决方案

### 方法 1：重新加载 VS Code
按 `Ctrl+Shift+P`，输入 "Developer: Reload Window"

### 方法 2：手动运行测试
测试文件中的 `sys.path.insert()` 确保运行时能正确导入：

```bash
cd /home/guci/aiProjects/mda/pim-compiler
python tests/test_compiler.py
```

### 方法 3：使用 pytest
```bash
cd /home/guci/aiProjects/mda
pytest pim-compiler/tests/test_compiler.py
```

## 验证

运行以下命令验证导入是否正常：

```bash
cd /home/guci/aiProjects/mda/pim-compiler
python -c "import sys; sys.path.insert(0, 'src'); from compiler.core.compiler_config import CompilerConfig; print('✅ 导入成功')"
```

## 注意事项

1. Pylance 的静态分析可能无法理解运行时的 `sys.path` 修改
2. 这些导入错误不影响代码的实际运行
3. 测试可以正常执行