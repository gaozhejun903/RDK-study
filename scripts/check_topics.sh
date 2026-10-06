#!/usr/bin/env bash
set -e
for t in /cmd_vel /odom /scan /tf; do
  if ros2 topic list | grep -qx "$t"; then
    echo "[OK] $t"
  else
    echo "[MISS] $t"
  fi
done
