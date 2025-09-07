#!/bin/bash

mkdir -p .inbox/李四/

cat > .inbox/李四/msg_20250908_025941.md << 'EOF'
# Message
From: 张三
To: 李四  
Time: 2025-09-08 02:59:41.628015

## Content
2+2等于几？
EOF

echo "Message sent to 李四"

for i in {1..10}
do
  sleep 2
  files=$(ls .inbox/张三/ 2>/dev/null | grep msg_)
  if [ -n "$files" ]; then
    for file in $files; do
      echo "Reply received:"
      cat .inbox/张三/$file
      exit 0
    done
  fi
done

echo "No reply received after 10 checks"