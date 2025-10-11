# 性能优化策略

## 内存优化

### 1. 流式处理
```python
# 使用生成器避免一次性加载所有文件
def discover_files_streaming(directory_path, max_depth):
    """流式发现文件，避免内存峰值"""
    for root, dirs, files in os.walk(directory_path):
        current_depth = root.replace(directory_path, '').count(os.sep)
        if current_depth > max_depth:
            continue
        
        for file in files:
            yield os.path.join(root, file)
```

### 2. 分批处理内存控制
```python
class MemoryAwareBatchProcessor:
    def __init__(self, max_memory_mb=500):
        self.max_memory_mb = max_memory_mb
        
    def estimate_memory_usage(self, file_paths):
        """估算文件处理的内存使用"""
        total_size = 0
        for file_path in file_paths:
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass
        return total_size / (1024 * 1024)  # MB
    
    def adjust_batch_size(self, file_paths, current_batch_size):
        """根据内存使用调整批次大小"""
        estimated_memory = self.estimate_memory_usage(file_paths[:current_batch_size])
        
        if estimated_memory > self.max_memory_mb * 0.8:
            # 内存使用过高，减少批次大小
            return max(1, current_batch_size // 2)
        elif estimated_memory < self.max_memory_mb * 0.3:
            # 内存使用较低，增加批次大小
            return min(current_batch_size * 2, 1000)
        else:
            return current_batch_size
```

### 3. 及时释放内存
```python
def process_batch_with_cleanup(self, file_batch):
    """处理批次并立即释放内存"""
    batch_entities = []
    
    for file_path in file_batch:
        # 处理单个文件
        entity = self.process_single_file(file_path)
        if entity:
            batch_entities.append(entity)
        
        # 强制垃圾回收大文件
        if entity and entity.get('file:hasContent'):
            del entity['file:hasContent']
            import gc
            gc.collect()
    
    return batch_entities
```

## I/O 优化

### 1. 异步文件读取
```python
import asyncio
import aiofiles

async def read_file_async(file_path):
    """异步读取文件"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return content[:1000]  # 限制内容长度
    except Exception as e:
        return None

async def process_files_async(file_paths):
    """异步处理多个文件"""
    tasks = [read_file_async(file_path) for file_path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 2. 批量写入优化
```python
class BufferedKnowledgeGraphWriter:
    def __init__(self, output_path, buffer_size=1000):
        self.output_path = output_path
        self.buffer_size = buffer_size
        self.buffer = []
        
    def add_entity(self, entity):
        """添加实体到缓冲区"""
        self.buffer.append(entity)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        """将缓冲区写入文件"""
        if not self.buffer:
            return
            
        # 使用追加模式写入
        with open(self.output_path, 'a', encoding='utf-8') as f:
            for entity in self.buffer:
                f.write(json.dumps(entity, ensure_ascii=False) + '\n')
        
        self.buffer.clear()
```

## 处理速度优化

### 1. 并行处理
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ParallelProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
    
    def process_batch_parallel(self, file_batch, include_content=False):
        """并行处理文件批次"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.process_single_file, file_path, include_content)
                for file_path in file_batch
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"处理失败: {e}")
            
            return results
```

### 2. 缓存优化
```python
class FileMetadataCache:
    """文件元数据缓存"""
    
    def __init__(self, cache_file="file_metadata_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self):
        """加载缓存"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"无法保存缓存: {e}")
    
    def get_file_metadata(self, file_path):
        """获取文件元数据（带缓存）"""
        file_stat = os.stat(file_path)
        cache_key = f"{file_path}:{file_stat.st_mtime}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 计算元数据
        metadata = {
            "size": file_stat.st_size,
            "mtime": file_stat.st_mtime,
            "ctime": file_stat.st_ctime
        }
        
        self.cache[cache_key] = metadata
        return metadata
```

## 资源监控

### 1. 内存监控
```python
import psutil
import resource

class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage(self):
        """获取当前内存使用"""
        return self.process.memory_info().rss / 1024 / 1024  # MB
    
    def check_memory_limit(self, limit_mb=1000):
        """检查内存限制"""
        current_usage = self.get_memory_usage()
        if current_usage > limit_mb:
            print(f"警告: 内存使用过高: {current_usage:.1f}MB")
            return True
        return False
    
    def suggest_batch_size(self, current_batch_size):
        """根据内存使用建议批次大小"""
        memory_usage = self.get_memory_usage()
        
        if memory_usage > 800:  # MB
            return max(1, current_batch_size // 2)
        elif memory_usage < 300:
            return min(current_batch_size * 2, 1000)
        else:
            return current_batch_size
```

### 2. 进度监控
```python
class ProgressMonitor:
    def __init__(self, total_files):
        self.total_files = total_files
        self.processed_files = 0
        self.start_time = time.time()
    
    def update(self, processed_count=1):
        """更新进度"""
        self.processed_files += processed_count
        
        elapsed_time = time.time() - self.start_time
        files_per_second = self.processed_files / elapsed_time if elapsed_time > 0 else 0
        
        progress_percent = (self.processed_files / self.total_files) * 100
        estimated_total_time = elapsed_time / (self.processed_files / self.total_files) if self.processed_files > 0 else 0
        remaining_time = estimated_total_time - elapsed_time
        
        print(f"进度: {progress_percent:.1f}% ({self.processed_files}/{self.total_files}) | "
              f"速度: {files_per_second:.1f} 文件/秒 | "
              f"预计剩余: {remaining_time/60:.1f} 分钟")
```

## 配置优化

### 1. 自适应批次大小
```python
def adaptive_batch_processing(directory_path, initial_batch_size=100):
    """自适应批次大小处理"""
    monitor = ResourceMonitor()
    batch_size = initial_batch_size
    
    for file_batch in split_into_batches(all_files, batch_size):
        # 处理当前批次
        process_batch(file_batch)
        
        # 根据内存使用调整批次大小
        batch_size = monitor.suggest_batch_size(batch_size)
        
        # 检查是否需要暂停
        if monitor.check_memory_limit():
            print("内存使用过高，暂停处理...")
            time.sleep(5)  # 暂停5秒让系统回收内存
```

### 2. 智能文件过滤
```python
def smart_file_filter(file_paths, max_file_size_mb=10):
    """智能文件过滤，避免处理过大文件"""
    filtered_files = []
    
    for file_path in file_paths:
        try:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size <= max_file_size_mb:
                filtered_files.append(file_path)
            else:
                print(f"跳过大文件: {file_path} ({file_size:.1f}MB)")
        except:
            filtered_files.append(file_path)  # 无法获取大小，默认处理
    
    return filtered_files
```

这些优化策略可以显著提高大目录处理的性能和稳定性。