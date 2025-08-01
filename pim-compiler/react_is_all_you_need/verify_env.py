#!/usr/bin/env python3
"""
验证React Agent虚拟环境配置
"""

import sys
import subprocess
import pkg_resources

def check_python_path():
    """检查Python路径"""
    print("=== Python路径检查 ===")
    print(f"当前Python路径: {sys.executable}")
    
    if 'react_agent_env' in sys.executable:
        print("✅ 正在使用React Agent虚拟环境")
        return True
    else:
        print("❌ 未使用React Agent虚拟环境")
        return False

def check_jupyter_kernel():
    """检查Jupyter内核"""
    print("\n=== Jupyter内核检查 ===")
    try:
        result = subprocess.run(['jupyter', 'kernelspec', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("可用内核:")
            print(result.stdout)
            if 'react_agent_env' in result.stdout:
                print("✅ React Agent内核已安装")
                return True
            else:
                print("❌ React Agent内核未找到")
                return False
        else:
            print("❌ 无法获取内核列表")
            return False
    except FileNotFoundError:
        print("❌ Jupyter未安装")
        return False

def check_installed_packages():
    """检查已安装的包"""
    print("\n=== 包检查 ===")
    try:
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        
        # 检查关键包
        key_packages = ['jupyter', 'ipykernel', 'notebook']
        missing_packages = []
        
        for package in key_packages:
            if package in installed_packages:
                print(f"✅ {package} 已安装")
            else:
                print(f"❌ {package} 未安装")
                missing_packages.append(package)
        
        print(f"\n总共安装了 {len(installed_packages)} 个包")
        
        if not missing_packages:
            print("✅ 所有关键包都已安装")
            return True
        else:
            print(f"❌ 缺少包: {missing_packages}")
            return False
            
    except Exception as e:
        print(f"❌ 检查包时出错: {e}")
        return False

def main():
    """主验证函数"""
    print("React Agent虚拟环境配置验证")
    print("=" * 50)
    
    python_ok = check_python_path()
    kernel_ok = check_jupyter_kernel()
    packages_ok = check_installed_packages()
    
    print("\n" + "=" * 50)
    print("验证结果:")
    
    if python_ok and kernel_ok and packages_ok:
        print("🎉 所有检查都通过！虚拟环境配置正确。")
        print("\n使用方法:")
        print("1. 运行: ./start_jupyter.sh")
        print("2. 在notebook中选择 'React Agent Environment' 内核")
        return True
    else:
        print("❌ 配置有问题，请检查上述错误。")
        return False

if __name__ == "__main__":
    main() 