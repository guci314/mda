#!/bin/bash
# ReactAgent v3 三级记忆使用示例

echo "=== ReactAgent v3 Memory Usage Examples ==="
echo

# 1. 无记忆模式 - 快速生成
echo "1. No Memory Mode (Fast):"
echo "python direct_react_agent_v3_fixed.py --memory none"
echo "  用途：一次性代码生成，模板项目"
echo

# 2. 智能记忆模式 - 默认推荐
echo "2. Smart Memory Mode (Default):"
echo "python direct_react_agent_v3_fixed.py --memory smart"
echo "  用途：迭代开发，错误修复，功能增强"
echo

# 3. 专业记忆模式 - 长期项目
echo "3. Professional Memory Mode:"
echo "python direct_react_agent_v3_fixed.py --memory pro --session-id project_crm_v1"
echo "  用途：长期项目，团队协作，需要历史追溯"
echo

# 高级用法
echo "=== Advanced Usage ==="
echo

# 4. 自定义输出目录
echo "4. Custom Output Directory:"
echo "python direct_react_agent_v3_fixed.py --memory smart --output-dir output/my_project"
echo

# 5. 使用不同的PIM文件
echo "5. Different PIM File:"
echo "python direct_react_agent_v3_fixed.py --memory pro --pim-file ../models/domain/order_management.md --session-id order_system"
echo

# 6. 恢复之前的会话（专业模式）
echo "6. Resume Previous Session:"
echo "python direct_react_agent_v3_fixed.py --memory pro --session-id project_crm_v1"
echo "  说明：使用相同的session-id可以恢复之前的对话历史"
echo

# 实际场景示例
echo "=== Real World Scenarios ==="
echo

# 场景1：快速原型
echo "Scenario 1 - Quick Prototype:"
echo "python direct_react_agent_v3_fixed.py --memory none --output-dir output/prototype"
echo

# 场景2：功能迭代
echo "Scenario 2 - Feature Development:"
echo "python direct_react_agent_v3_fixed.py --memory smart --output-dir output/feature_auth"
echo

# 场景3：企业项目
echo "Scenario 3 - Enterprise Project:"
echo "python direct_react_agent_v3_fixed.py --memory pro --session-id enterprise_erp_2024 --output-dir output/erp_system"