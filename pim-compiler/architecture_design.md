## 模块接口定义

### 前端解析模块
- 输入接口: 接收源代码文件
- 输出接口: 生成抽象语法树(AST)
- 关键方法: parse(source_code) -> AST

### 中间表示模块
- 输入接口: 接收AST
- 输出接口: 生成中间表示(IR)
- 关键方法: transform(ast) -> IR

### 后端生成模块
- 输入接口: 接收IR
- 输出接口: 生成目标代码
- 关键方法: generate(ir) -> target_code