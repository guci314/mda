# Jupyter Notebook 虚拟环境配置说明

## 配置完成情况

✅ **虚拟环境内核已安装**

- 内核名称: `react_agent_env`
- 显示名称: `React Agent Environment`
- 内核路径: `/home/guci/.local/share/jupyter/kernels/react_agent_env`

## 使用方法

### 方法 1：使用启动脚本（推荐）

```bash
cd pim-compiler/react_is_all_you_need
./start_jupyter.sh
```

### 方法 2：手动启动

```bash
# 激活虚拟环境
cd pim-compiler
source react_agent_env/bin/activate

# 启动Jupyter Notebook
cd react_is_all_you_need
jupyter notebook
```

### 方法 3：在现有 Jupyter 中选择内核

1. 启动 Jupyter Notebook
2. 打开 `agent_research.ipynb`
3. 在菜单栏选择：`Kernel` → `Change kernel` → `React Agent Environment`

## 验证配置

### 检查可用内核

```bash
jupyter kernelspec list
```

应该看到：

```
Available kernels:
  python3            /home/guci/aiProjects/mda/pim-compiler/react_agent_env/share/jupyter/kernels/python3
  react_agent_env    /home/guci/.local/share/jupyter/kernels/react_agent_env
```

### 验证虚拟环境包

在 notebook 中运行：

```python
import sys
print(sys.executable)
# 应该显示: /home/guci/aiProjects/mda/pim-compiler/react_agent_env/bin/python

# 检查已安装的包
import pkg_resources
installed_packages = [d.project_name for d in pkg_resources.working_set]
print("已安装的包数量:", len(installed_packages))
```

## 虚拟环境信息

- **Python 版本**: 3.10.12
- **虚拟环境路径**: `/home/guci/aiProjects/mda/pim-compiler/react_agent_env`
- **主要包**:
  - jupyter
  - ipykernel
  - notebook
  - 以及其他项目依赖包

## 故障排除

### 如果内核不显示

1. 重新安装内核：

```bash
source react_agent_env/bin/activate
python -m ipykernel install --user --name=react_agent_env --display-name="React Agent Environment"
```

### 如果包导入错误

1. 确保在正确的虚拟环境中
2. 检查包是否安装：

```bash
source react_agent_env/bin/activate
pip list
```

### 如果 Jupyter 无法启动

1. 检查端口是否被占用：

```bash
lsof -i :8888
```

2. 使用不同端口：

```bash
jupyter notebook --port=8889
```

## 注意事项

- 确保在运行 notebook 之前激活了正确的虚拟环境
- 如果修改了虚拟环境中的包，可能需要重新安装内核
- 建议使用启动脚本以确保环境一致性
