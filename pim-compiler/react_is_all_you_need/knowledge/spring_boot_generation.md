# Spring Boot生成知识

## 核心理念
Agent根据知识文件直接生成Spring Boot服务，无需生成器代码。

## 生成流程

当需要生成Spring Boot服务时：

1. **分析知识文件**
   - 提取业务实体
   - 识别API端点
   - 理解业务流程

2. **生成项目结构**
   ```
   service-name/
   ├── src/main/java/com/aia/
   │   ├── controller/
   │   ├── service/
   │   ├── repository/
   │   └── model/
   ├── src/main/resources/
   │   └── application.yml
   ├── pom.xml
   └── Dockerfile
   ```

3. **生成Controller**
   ```java
   @RestController
   @RequestMapping("/api")
   public class OrderController {
       // 从知识文件提取的端点
   }
   ```

4. **生成Service**
   ```java
   @Service
   public class OrderService {
       // 从知识文件提取的业务逻辑
   }
   ```

5. **生成配置**
   ```yaml
   spring:
     application:
       name: service-name
   server:
     port: 8080
   ```

## 示例：订单服务生成

### 输入知识
```markdown
# 订单处理知识
实体：
- 订单(id, customerId, items, total, status)
- 订单项(productId, quantity, price)

API：
- POST /order - 创建订单
- GET /order/{id} - 查询订单
- PUT /order/{id}/cancel - 取消订单

业务规则：
- 创建订单前检查库存
- 计算总价含税
- 发送确认邮件
```

### Agent理解后生成

1. **OrderController.java**
2. **OrderService.java**
3. **OrderRepository.java**
4. **Order.java, OrderItem.java**
5. **application.yml**
6. **pom.xml**

## 与条件反射集成

生成的Spring Boot服务自动支持条件反射：

```java
@PostMapping("/reflex")
public ResponseEntity reflexEndpoint(@RequestBody String json) {
    // 专门用于条件反射调用的端点
    // 纯JSON输入输出，无需LLM
    return ResponseEntity.ok(processJson(json));
}
```

## 优势

1. **知识驱动**：修改知识文件即可重新生成
2. **标准Spring Boot**：完全兼容Spring生态
3. **自动集成**：生成的服务自带监控、安全等
4. **条件反射就绪**：预留JSON端点供反射调用

## 注意事项

- Agent生成的代码是起点，可以人工优化
- 保持知识文件与代码同步
- 生成的服务遵循Spring Boot最佳实践