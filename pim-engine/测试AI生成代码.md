# 测试 AI 生成代码

## 快速测试步骤

### 1. 启动服务
```bash
cd /home/guci/aiProjects/mda/pim-engine
./start-with-gemini-linux.sh
```

### 2. 打开模型管理页面
访问: http://localhost:8001/models

### 3. 刷新模型列表
点击 "刷新列表" 按钮，确认 `todo_management` 模型出现在列表中。

### 4. 生成代码
在 "代码生成" 区域：
1. 选择模型：`todo_management`
2. 选择平台：`FastAPI`
3. **重要**：勾选 "使用 AI" 复选框
4. 点击 "生成代码"

### 5. 等待生成
AI 生成需要 30-60 秒，请耐心等待。

### 6. 对比结果

#### 模板生成（不使用 AI）的代码示例：
```python
async def createTodo(self, todoData: TodoCreate) -> Todo:
    """Create a new todo item"""
    # TODO: Implement business logic
    raise NotImplementedError("createTodo not implemented")
```

#### AI 生成的代码示例：
```python
async def createTodo(self, todoData: TodoCreate) -> Todo:
    """Create a new todo item with validation"""
    
    # Validate title is not empty
    if not todoData.title or todoData.title.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail="Title must not be empty or contain only whitespace"
        )
    
    # Create todo in database
    try:
        new_todo = Todo(
            title=todoData.title.strip(),
            description=todoData.description,
            completed=False,
            priority=todoData.priority or "medium",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(new_todo)
        self.db.commit()
        self.db.refresh(new_todo)
        
        # Log creation event
        logger.info(f"Created todo: {new_todo.id} - {new_todo.title}")
        
        return new_todo
        
    except Exception as e:
        self.db.rollback()
        logger.error(f"Failed to create todo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create todo")
```

## 关键差异

1. **模板生成**：
   - 包含 TODO 注释
   - 抛出 NotImplementedError
   - 需要手动实现所有逻辑

2. **AI 生成**：
   - 完整的业务逻辑实现
   - 包含验证逻辑
   - 错误处理
   - 日志记录
   - 数据库操作
   - 遵循 PIM 中定义的业务规则

## 使用 Puppeteer 自动化测试

```bash
# 安装依赖
npm install puppeteer

# 运行自动化测试
./run_puppeteer_test.sh
```

测试脚本会：
1. 自动打开浏览器
2. 导航到模型页面
3. 选择模型和平台
4. 启用 AI 生成
5. 分析生成的代码质量
6. 保存截图

## 故障排除

### 如果 Gemini 连接失败
1. 检查 API Key 是否正确设置
2. 检查代理配置：
   ```bash
   # 查看容器日志
   docker compose -f docker-compose.llm.yml logs pim-engine
   ```

### 如果生成超时
- AI 生成比模板慢是正常的
- 复杂模型可能需要更长时间
- 检查网络连接和代理设置

### 查看 AI 提供商状态
```bash
curl http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool
```

预期输出：
```json
{
  "available_providers": [
    {
      "name": "gemini",
      "available": true,
      "type": "GeminiCLIProvider"
    }
  ],
  "current_provider": "gemini"
}
```