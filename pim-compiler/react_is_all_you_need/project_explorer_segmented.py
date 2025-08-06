#!/usr/bin/env python3
"""分段项目探索器 - 解决输出长度限制问题"""

import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from project_explorer import ProjectExplorer


class SegmentedProjectExplorer(ProjectExplorer):
    """分段探索项目，避免输出被截断"""
    
    # UML四个视图的单独提示词
    USE_CASE_PROMPT = """# Use Case视图分析

请专注分析项目的Use Case视图（用例视图）：

1. 识别主要的Actor（用户、外部系统、定时任务等）
2. 列出核心用例，包括名称和简要描述
3. 分析用例之间的关系（包含、扩展、泛化）
4. 用mermaid画出用例图

控制输出在2000字符以内，只包含Use Case视图的内容。
"""

    PACKAGE_PROMPT = """# Package视图分析

请专注分析项目的Package视图（包视图）：

1. 识别主要的包/模块及其职责
2. 分析包之间的依赖关系
3. 识别分层架构（如果有）
4. 如果有子项目，展示子项目间的依赖关系
5. 用mermaid画出包图

控制输出在2000字符以内，只包含Package视图的内容。
"""

    CLASS_PROMPT = """# Class视图分析

请专注分析项目的Class视图（类视图）：

1. 识别核心类和接口
2. 列出重要的属性和方法
3. 分析类之间的关系（继承、实现、关联、聚合/组合、依赖）
4. 用mermaid画出类图

控制输出在2000字符以内，只包含Class视图的内容。
"""

    INTERACTION_PROMPT = """# Interaction视图分析

请专注分析项目的Interaction视图（交互视图）：

1. 选择2-3个关键的业务流程
2. 展示对象/组件间的消息传递
3. 标注同步/异步调用
4. 说明关键的业务规则
5. 用mermaid画出序列图

控制输出在2000字符以内，只包含Interaction视图的内容。
"""

    SUMMARY_PROMPT = """# 项目综合分析

基于前面的分析，请提供：

1. 项目的整体架构特点总结
2. 如果是多子项目，总结整体架构模式（如微服务、单体应用、插件架构等）
3. 关键发现和潜在问题
4. 改进建议（如果有）

控制输出在1500字符以内。
"""
    
    async def explore_project(self) -> None:
        """分段探索项目，生成完整的UML分析"""
        try:
            print("🔍 [项目探索] 开始分段分析项目结构...")
            start_time = datetime.now()
            
            # 收集项目基础信息
            project_info = self._gather_project_info()
            
            # 分段探索各个视图
            segments = []
            
            # 1. 项目概述
            print("   📊 分析项目概述...")
            overview = await self._explore_segment("项目概述", project_info, 
                "请简要介绍这个项目的目的、技术栈和整体结构。控制在1000字符以内。")
            segments.append(("# 项目概述\n\n" + overview))
            
            # 2. Use Case视图
            print("   📊 分析Use Case视图...")
            use_case = await self._explore_segment("Use Case视图", project_info, self.USE_CASE_PROMPT)
            segments.append(("\n## 1. Use Case视图\n\n" + use_case))
            
            # 3. Package视图
            print("   📊 分析Package视图...")
            package = await self._explore_segment("Package视图", project_info, self.PACKAGE_PROMPT)
            segments.append(("\n## 2. Package视图\n\n" + package))
            
            # 4. Class视图
            print("   📊 分析Class视图...")
            class_view = await self._explore_segment("Class视图", project_info, self.CLASS_PROMPT)
            segments.append(("\n## 3. Class视图\n\n" + class_view))
            
            # 5. Interaction视图
            print("   📊 分析Interaction视图...")
            interaction = await self._explore_segment("Interaction视图", project_info, self.INTERACTION_PROMPT)
            segments.append(("\n## 4. Interaction视图\n\n" + interaction))
            
            # 6. 综合分析
            print("   📊 生成综合分析...")
            summary = await self._explore_segment("综合分析", project_info, self.SUMMARY_PROMPT)
            segments.append(("\n## 5. 综合分析\n\n" + summary))
            
            # 合并所有段落
            full_understanding = "\n".join(segments)
            full_understanding = f"# {self.work_dir.name} - UML四视图分析\n\n生成时间：{datetime.now().isoformat()}\n\n" + full_understanding
            
            # 保存结果
            self.understanding_file.write_text(full_understanding, encoding='utf-8')
            
            # 记录探索历史
            self._log_exploration(start_time, len(full_understanding))
            
            print(f"✅ [项目探索] 完成！已生成完整的UML分析文档 ({len(full_understanding)} 字符)")
            print(f"   📄 包含：项目概述 + 4个UML视图 + 综合分析")
            
            # 触发完成回调
            if self.on_complete_callback:
                try:
                    self.on_complete_callback()
                except Exception as callback_error:
                    print(f"⚠️ 探索完成回调执行失败: {callback_error}")
            
        except Exception as e:
            print(f"⚠️ [项目探索] 探索过程中出错: {e}")
            if os.environ.get('DEBUG'):
                import traceback
                traceback.print_exc()
    
    async def _explore_segment(self, segment_name: str, project_info: str, prompt: str) -> str:
        """探索单个视图段落"""
        try:
            full_prompt = f"{prompt}\n\n## 项目信息\n\n{project_info}"
            response = await self.llm.ainvoke(full_prompt)
            return response.content
        except Exception as e:
            print(f"   ⚠️ {segment_name}分析失败: {e}")
            return f"{segment_name}分析失败：{str(e)}"


if __name__ == "__main__":
    # 测试分段探索
    print("分段项目探索器 - 解决输出长度限制")