# Agent知识库

## 成功模式

### PSM高效生成模式
- **适用场景**: 需要快速生成PSM技术规范文档
- **解决方案**: 
  1. 使用预定义模板结构
  2. 参数化配置驱动
  3. 一次性完整生成
  4. 专用Python脚本执行
- **效果**: 从15-20轮优化到1-2轮完成，100%成功率
- **注意事项**: 需要预先设计好模板和配置结构

### 大文件一次性写入模式
- **适用场景**: 生成大型结构化文档（>4KB）
- **解决方案**:
  ```python
  # 预构建完整内容
  content = build_complete_document(config)
  # 一次性写入
  with open('output.md', 'w') as f:
      f.write(content)
  ```
- **效果**: 工具调用次数从50+次降低到1-3次
- **注意事项**: 必须在内存中完整构建，避免分块追加

## 最佳实践

### PSM文档生成
- **原则**: 模板化 + 参数化 + 一次性生成
- **示例**:
  ```bash
  # 一键生成
  python3 quick_psm_generate.py --project MyProject
  ```
- **收益**: 10秒内完成，零错误率

### 配置驱动设计
- **原则**: 将变化部分提取到配置中
- **结构**:
  ```json
  {
    "models": [...],
    "services": [...],
    "endpoints": [...],
    "configurations": [...],
    "test_suites": [...]
  }
  ```
- **收益**: 支持快速定制，无需修改代码

## 错误模式

### 低效生成模式
- **表现**: 逐章节分别调用工具，15-20轮完成
- **原因**: 没有预定义模板，临时决策
- **解决**: 使用专用PSM生成器
- **预防**: 建立标准化模板库

### 重复写入问题
- **表现**: 多次write_file覆盖同一文件
- **原因**: 没有规划好文档结构
- **解决**: 先完整构建，再一次性写入
- **预防**: 使用内存构建模式

## 工具集

### 核心工具
1. **quick_psm_generate.py** - 一键PSM生成
2. **psm_generator.py** - 高级定制生成器
3. **PSM_TEMPLATES** - 预定义模板库

### 使用模式
```bash
# 快速开始
python3 quick_psm_generate.py --project BlogSystem

# 自定义配置
python3 quick_psm_generate.py --config custom.json --output my_psm.md

# 高级定制
from psm_generator import PSMGenerator
generator = PSMGenerator("MyProject")
content = generator.generate_psm_document(config)
```

---
更新时间: 2024-12-25 12:10:00