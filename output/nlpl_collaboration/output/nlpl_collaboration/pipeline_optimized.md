# 优化的数据处理流水线NLPL程序

## Level 4 结构化数据处理流水线（优化版）

### 主流程定义
> [main] 数据处理流水线主流程（优化版）
> [description] 从CSV读取数据到处理后导出的完整流程，包含性能优化和错误处理
> [author] DataEngineer
> [version] 1.1
> [optimizations] 
>> 路径错误处理
>> 灵活的数据清洗策略
>> 性能监控
>> 详细日志记录

### 阶段1：初始化与配置
> [stage] 初始化
> [id] initialization
> [depends] none
> [parallel] false

>> [task] 配置环境和路径验证
>> [id] setup_environment
>> [module] system
>> [action] initialize
>> [params]
>>> log_level: "INFO"
>>> performance_monitoring: true

>> [task] 验证输入文件路径
>> [id] validate_paths
>> [module] data_io
>> [action] validate_file_path
>> [params]
>>> file_path: ${input_file_path}
>>> required: true
>>> fallback_paths: ["./data/input.csv", "./input.csv"]

### 阶段2：数据接入与探索
> [stage] 数据接入
> [id] data_ingestion
> [depends] initialization
> [parallel] true

>> [task] 读取CSV数据
>> [id] read_csv
>> [module] data_io
>> [action] load_csv
>> [params] 
>>> file_path: ${input_file_path}
>>> delimiter: ","
>>> encoding: "utf-8"
>>> error_handling: "graceful"
>>> fallback_encoding: ["gbk", "latin1"]

>> [task] 数据初步探索
>> [id] data_profiling
>> [module] data_analysis
>> [action] quick_profile
>> [params]
>>> sample_size: 1000
>>> include_types: true
>>> include_missing_stats: true

### 阶段3：数据清洗
> [stage] 数据清洗
> [id] data_cleaning
> [depends] data_ingestion
> [parallel] false

>> [task] 空值处理策略选择
>> [id] missing_strategy
>> [module] data_cleaning
>> [action] evaluate_missing_strategy
>> [params]
>>> missing_threshold: 0.5  # 50%阈值
>>> default_strategy: "impute"  # 默认策略: 插补而非删除

>> [task] 空值处理
>> [id] handle_missing
>> [module] data_cleaning
>> [action] process_nulls
>> [params]
>>> strategy: ${missing_strategy.result}  # 动态选择策略
>>> columns: "all"
>>> impute_method: "mean"  # 插补方法
>>> preserve_rows: true  # 保持行数

>> [task] 异常值检测与处理
>> [id] handle_outliers
>> [module] data_cleaning
>> [action] detect_outliers
>> [params]
>>> method: "iqr"  # 可选: iqr, zscore, isolation_forest
>>> threshold: 1.5
>>> action: "cap"  # 可选: remove, cap, transform
>>> preserve_distribution: true

### 阶段4：数据转换
> [stage] 数据转换
> [id] data_transformation
> [depends] data_cleaning
> [parallel] false

>> [task] 数据标准化
>> [id] standardization
>> [module] data_scaling
>> [action] standardize
>> [params]
>>> method: "z-score"
>>> columns: ${numeric_columns}
>>> handle_outliers: true

>> [task] 数据归一化
>> [id] normalization
>> [module] data_scaling
>> [action] normalize
>> [params]
>>> method: "min-max"
>>> range: [0, 1]
>>> columns: ${numeric_columns}

### 阶段5：特征工程
> [stage] 特征工程
> [id] feature_engineering
> [depends] data_transformation
> [parallel] true

>> [task] 创建多项式特征
>> [id] polynomial_features
>> [module] feature_eng
>> [action] create_poly_features
>> [params]
>>> degree: 2
>>> interaction_only: true
>>> skip_columns: ["name", "status"]  # 跳过非数值列

>> [task] 创建统计特征
>> [id] statistical_features
>> [module] feature_eng
>> [action] create_stat_features
>> [params]
>>> windows: [3, 7, 30]
>>> functions: ["mean", "std", "min", "max"]
>>> apply_to_columns: ${numeric_columns}

### 阶段6：数据分析
> [stage] 数据分析
> [id] data_analysis
> [depends] feature_engineering
> [parallel] true

>> [task] 描述性统计分析
>> [id] descriptive_stats
>> [module] statistics
>> [action] describe
>> [params]
>>> include_percentiles: true
>>> include_distribution: true
>>> export_results: true

>> [task] 相关性分析
>> [id] correlation_analysis
>> [module] statistics
>> [action] correlation_matrix
>> [params]
>>> method: "pearson"  # 可选: pearson, spearman, kendall
>>> threshold: 0.5
>>> visualize: true

### 阶段7：可视化建议
> [stage] 可视化建议
> [id] visualization
> [depends] data_analysis
> [parallel] true

>> [task] 生成可视化建议
>> [id] viz_recommendations
>> [module] visualization
>> [action] suggest_plots
>> [params]
>>> data_type_analysis: true
>>> correlation_insights: true
>>> distribution_insights: true

### 阶段8：数据导出
> [stage] 数据导出
> [id] data_export
> [depends] visualization
> [parallel] false

>> [task] 导出处理后的数据
>> [id] export_data
>> [module] data_io
>> [action] export_processed
>> [params]
>>> format: "csv"  # 可选: csv, parquet, json
>>> compression: "gzip"
>>> output_path: ${output_file_path}
>>> include_metadata: true

>> [task] 导出分析报告
>> [id] export_report
>> [module] reporting
>> [action] generate_report
>> [params]
>>> format: "pdf"
>>> include_visualizations: true
>>> output_path: ${report_path}

### 错误处理与恢复机制
> [error_handling] 全局错误处理策略
>> [strategy] 流水线容错机制
>>> 文件路径错误: 尝试多个备选路径
>>> 编码错误: 尝试多种编码格式
>>> 数据质量问题: 使用插补而非删除策略
>>> 性能问题: 监控并记录各阶段耗时
>> [recovery] 恢复机制
>>> 阶段性保存: 关键阶段后保存中间结果
>>> 日志记录: 详细记录执行过程和错误信息
>>> 通知机制: 执行完成后发送状态报告

### 配置参数
> [config] 流水线配置参数
>> input_file_path: "./data/input.csv"
>> output_file_path: "./data/processed_data.csv"
>> report_path: "./reports/analysis_report.pdf"
>> numeric_columns: ["age", "score"]
>> log_file: "./logs/pipeline.log"
>> temp_dir: "./temp/"

### 性能监控
> [monitoring] 性能指标
>> [metrics] 关键性能指标
>>> 各阶段执行时间
>>> 内存使用情况
>>> 数据行数变化
>>> 错误发生次数
>> [thresholds] 性能阈值
>>> 阶段执行时间预警: >30秒
>>> 内存使用预警: >80%可用内存
>>> 数据丢失预警: >10%行数减少

## 优化说明

基于执行报告中的反馈，此优化版本解决了以下关键问题：

1. **路径错误处理**：
   - 添加了路径验证任务，确保输入文件存在
   - 提供了多个备选路径，防止因单一路径错误导致执行失败
   - 增加了更详细的错误信息和恢复机制

2. **数据清洗改进**：
   - 用更灵活的插补策略替代了直接删除包含空值的行
   - 添加了空值处理策略评估，根据数据情况动态选择最佳处理方法
   - 保留了更多原始数据，避免不必要的数据丢失

3. **性能监控**：
   - 添加了性能监控机制，跟踪各阶段执行时间
   - 增加了内存使用监控，防止资源耗尽
   - 实现了阶段性保存，支持从失败点恢复

4. **错误处理增强**：
   - 添加了全局错误处理策略
   - 实现了多种编码格式尝试机制
   - 增加了详细的日志记录和通知机制

5. **配置灵活性**：
   - 使用参数化配置，便于在不同环境中运行
   - 添加了临时目录和日志文件配置
   - 支持多种数据格式的输入和输出

此优化版本在保持原有功能的基础上，显著提高了程序的健壮性、性能和可维护性。