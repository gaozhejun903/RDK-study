#!/usr/bin/env bash
set -e
echo "=== RDK-study environment check ==="
echo "Ubuntu:"
lsb_release -d 2>/dev/null || true
echo "Python:"
python3 --version
echo "Git:"
git --version
echo "ROS_DISTRO: ${ROS_DISTRO:-<not sourced>}"
if command -v ros2 >/dev/null 2>&1; then
  echo "[OK] ros2 found"
else
  echo "[FAIL] ros2 not found"
  echo "Run: source /opt/ros/humble/setup.bash"
  exit 1
fi
echo "=== PASS ==="
