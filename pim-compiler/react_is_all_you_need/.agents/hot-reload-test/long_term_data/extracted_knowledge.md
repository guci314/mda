```markdown
# 知识库

## 元知识
- 可通过Python交互式环境输入`import this`查看Python设计哲学（Python之禅）
- React官方文档是获取核心概念最权威的来源

## 原理与设计
- Python设计哲学核心原则：
  1. 简洁优于复杂
  2. 明确优于隐晦
  3. 扁平优于嵌套
  4. 可读性很重要
  5. 实用胜过纯粹
  6. 错误不应悄悄传递
  7. 面对歧义拒绝猜测
  8. 现在做比不做好
  9. 难以解释的实现是坏主意
  10. 容易解释的实现可能是好主意

- React核心设计理念：
  1. 组件化开发
  2. 虚拟DOM与高效渲染
  3. 单向数据流
  4. JSX语法扩展
  5. 状态与属性分离
  6. 钩子函数机制
  7. 上下文共享数据
  8. 副作用管理
  9. 增量渲染(Fiber架构)

## 接口与API
- React核心API：
  - 组件定义：函数组件/类组件
  - 状态管理：useState/this.setState
  - 生命周期：useEffect/类生命周期方法
  - 上下文：createContext/Provider/useContext
  - 性能优化：memo/useMemo/useCallback

## 实现细节（需验证）
- Python之禅实现位置：Python标准库this.py
- React虚拟DOM diff算法实现可能位于react-reconciler包
- React Fiber架构实现可能位于react-dom包
- 注：实现细节可能已变化，使用前需验证

## 用户偏好与项目特点
- Python开发者通常重视代码可读性和简洁性
- React项目常见技术栈组合：
  - 状态管理：Redux/MobX/Context
  - 路由：React Router
  - 样式：CSS-in-JS/模块化CSS
```