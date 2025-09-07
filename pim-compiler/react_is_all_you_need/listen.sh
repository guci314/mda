#!/bin/bash
for i in {1..20}; do
  files=$(ls .inbox/李四/msg_*.md 2>/dev/null)
  if [ -n "$files" ]; then
    file=$(echo $files | awk '{print $1}')
    content=$(cat "$file")
    if echo "$content" | grep -q "2+2"; then
      timestamp=$(date +%s)
      reply_file=".inbox/张三/reply_$timestamp.md"
      echo -e "From: 李四\nTo: 张三\nAnswer: 4" > "$reply_file"
      rm "$file"
      echo "Message processed and replied."
      break
    fi
  fi
  sleep 1
done
echo "No message with 2+2 found after 20 attempts."
