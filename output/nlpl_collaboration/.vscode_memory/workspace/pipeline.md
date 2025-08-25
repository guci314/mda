# 数据处理流水线NLPL程序

## Level 3 结构化数据处理流水线

### 主流程定义
> [main] 数据处理流水线主流程
> [description] 从CSV读取数据到处理后导出的完整流程
> [author] DataEngineer
> [version] 1.0

### 阶段1：数据接入与探索
> [stage] 数据接入
> [id] data_ingestion
> [depends] none
> [parallel] true

>> [task] 读取CSV数据
>> [id] read_csv
>> [module] data_io
>> [action] load_csv
>> [params] 
>>> file_path: ${input_file_path}
>>> delimiter: ","
>>> encoding: "utf-8"

>> [task] 数据初步探索
>> [id] data_profiling
>> [module] data_analysis
>> [action] quick_profile
>> [params]
>>> sample_size: 1000
>>> include_types: true

### 阶段2：数据清洗
> [stage] 数据清洗
> [id] data_cleaning
> [depends] data_ingestion
> [parallel] false

>> [task] 空值处理
>> [id] handle_missing
>> [module] data_cleaning
>> [action] process_nulls
>> [params]
>>> strategy: "mean"  # 可选: drop, mean, median, mode
>>> columns: "all"

>> [task] 异常值检测与处理
>> [id] handle_outliers
>> [module] data_cleaning
>> [action] detect_outliers
>> [params]
>>> method: "iqr"  # 可选: iqr, zscore, isolation_forest
>>> threshold: 1.5
>>> action: "cap"  # 可选: remove, cap, transform

### 阶段3：数据转换
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

>> [task] 数据归一化
>> [id] normalization
>> [module] data_scaling
>> [action] normalize
>> [params]
>>> method: "min-max"
>>> range: [0, 1]
>>> columns: ${numeric_columns}

### 阶段4：特征工程
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

>> [task] 创建统计特征
>> [id] statistical_features
>> [module] feature_eng
>> [action] create_stat_features
>> [params]
>>> windows: [3, 7, 30]
>>> functions: ["mean", "std", "min", "max"]

### 阶段5：数据分析
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

>> [task] 相关性分析
>> [id] correlation_analysis
>> [module] statistics
>> [action] correlation_matrix
>> [params]
>>> method: "pearson"  # 可选: pearson, spearman, kendall
>>> threshold: 0.5

### 阶段6：可视化建议
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

### 阶段7：数据导出
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

>> [task] 导出分析报告
>> [id] export_report
>> [module] reporting
>> [action] generate_report
>> [params]
>>> format: "pdf"
>>> include_visualizations: true
>>> output_path: ${report_path}

### 配置参数
> [config] 流水线配置参数
>> input_file_path: "./data/input.csv"
>> output_file_path: "./data/processed_data.csv"
>> report_path: "./reports/analysis_report.pdf"
>> numeric_columns: ["col1", "col2", "col3"]