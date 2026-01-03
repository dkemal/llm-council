#!/bin/bash
# Visual Polish Verification Script
# Validates all CSS changes for WCAG compliance and implementation completeness

echo "🔍 Visual Polish Verification"
echo "=============================="
echo ""

# Color constants
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FRONTEND_DIR="/Users/djamil/Github/llm-counsel/llm-council/frontend/src"
PASS_COUNT=0
FAIL_COUNT=0

# Function to check if a color exists in files
check_no_color() {
  local color=$1
  local description=$2

  if grep -rq "color: $color" "$FRONTEND_DIR" 2>/dev/null; then
    echo -e "${RED}❌ FAIL${NC}: Found non-compliant color $color ($description)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    grep -rn "color: $color" "$FRONTEND_DIR" | head -3
  else
    echo -e "${GREEN}✅ PASS${NC}: No usage of $color ($description)"
    PASS_COUNT=$((PASS_COUNT + 1))
  fi
}

# Function to check if a pattern exists
check_exists() {
  local pattern=$1
  local file=$2
  local description=$3

  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: $description"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "${RED}❌ FAIL${NC}: Missing $description"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

echo "1. WCAG AA Contrast Compliance"
echo "-------------------------------"
check_no_color "#999" "Low contrast gray"
check_no_color "#888" "Low contrast gray"
check_no_color "color: #666" "Low contrast gray (exclude #666666)"
echo ""

echo "2. Stage Visual Hierarchy"
echo "-------------------------"
check_exists "background: #f0f7ff" "$FRONTEND_DIR/components/Stage2.css" "Stage 2 blue background"
check_exists "border: 2px solid #2d8a2d" "$FRONTEND_DIR/components/Stage3.css" "Stage 3 prominent border"
check_exists "box-shadow: 0 4px 12px rgba(45, 138, 45" "$FRONTEND_DIR/components/Stage3.css" "Stage 3 enhanced shadow"
check_exists "font-size: 18px" "$FRONTEND_DIR/components/Stage3.css" "Stage 3 larger title"
echo ""

echo "3. Loading State Enhancements"
echo "-----------------------------"
check_exists "stage-loading stage-1" "$FRONTEND_DIR/components/ChatInterface.jsx" "Stage 1 loading class"
check_exists "Stage 1/3:" "$FRONTEND_DIR/components/ChatInterface.jsx" "Stage 1/3 progress"
check_exists "Stage 2/3:" "$FRONTEND_DIR/components/ChatInterface.jsx" "Stage 2/3 progress"
check_exists "Stage 3/3:" "$FRONTEND_DIR/components/ChatInterface.jsx" "Stage 3/3 progress"
check_exists "animation: spin 0.8s linear infinite, pulse" "$FRONTEND_DIR/components/ChatInterface.css" "Spinner pulse animation"
echo ""

echo "4. Visual Polish (Shadows & Animations)"
echo "----------------------------------------"
check_exists "box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08)" "$FRONTEND_DIR/components/Stage1.css" "Stage 1 card shadow"
check_exists "animation: slideInUp" "$FRONTEND_DIR/components/Stage1.css" "Stage 1 slide-in animation"
check_exists "@keyframes pulse" "$FRONTEND_DIR/index.css" "Global pulse animation"
check_exists "@keyframes slideInUp" "$FRONTEND_DIR/index.css" "Global slideInUp animation"
echo ""

echo "5. Button Interactions"
echo "----------------------"
check_exists "transform: translateY(-1px)" "$FRONTEND_DIR/components/ChatInterface.css" "Button hover transform"
check_exists "box-shadow: 0 4px 8px rgba(74, 144, 226" "$FRONTEND_DIR/components/ChatInterface.css" "Button hover shadow"
check_exists "transform: translateY(0)" "$FRONTEND_DIR/components/ChatInterface.css" "Button active state"
echo ""

echo "=============================="
echo "Summary"
echo "=============================="
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
  echo -e "${GREEN}✅ All visual polish checks passed!${NC}"
  exit 0
else
  echo -e "${RED}❌ Some checks failed. Review above for details.${NC}"
  exit 1
fi
