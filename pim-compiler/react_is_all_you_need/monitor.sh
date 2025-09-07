#!/bin/bash

while true; do
  files=$(ls .inbox/doc_agent/*.md 2>/dev/null)
  if [ -n "$files" ]; then
    for file in $files; do
      # 读取文件内容
      content=$(cat "$file")
      
      # 提取From字段
      from=$(echo "$content" | grep -i "^From:" | sed 's/From: *//i' | tr -d '\n\r')
      
      if [ -n "$from" ]; then
        # 解析任务 - 假设任务是文件内容中的指令
        # 这里简化：假设任务是执行echo或其他，但作为doc_agent，我需要处理文档任务
        # 例如，如果内容是任务描述，执行相应操作
        
        # 为了示例，假设回复是"Task processed by doc_agent"
        reply="Task processed by doc_agent\n\nOriginal task:\n$content"
        
        # 写回复到发送者的inbox
        mkdir -p ".inbox/$from"
        echo -e "From: doc_agent\n\n$reply" > ".inbox/$from/reply_$(date +%s).md"
        
        # 删除已处理的消息
        rm "$file"
      fi
    done
  fi
  sleep 1
done