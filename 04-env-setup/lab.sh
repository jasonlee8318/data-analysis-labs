#!/usr/bin/env bash
# ============================================================
# 분석 환경 구축 실습 — 실습실 관리 스크립트 (macOS/Linux)
# 사용법: ./lab.sh <start|shell|status|reset>
# ============================================================
set -e

case "$1" in
  start)
    echo "[START] 빈 리눅스 실습실을 기동합니다"
    docker compose up -d
    echo ""
    echo "👉 입장: ./lab.sh shell"
    ;;
  shell)
    echo "[SHELL] 실습실에 입장합니다 (나가기: exit)"
    docker compose exec lab bash
    ;;
  status)
    docker compose ps
    ;;
  reset)
    echo "[RESET] 실습실을 초기화합니다 (설치한 것 전부 삭제)"
    echo "        ※ /root/work 안의 파일(노트북, requirements.txt)은"
    echo "           내 PC의 ./work 폴더에 그대로 남습니다."
    docker compose down
    docker compose up -d
    echo "완료. ./lab.sh shell 로 다시 입장하세요."
    ;;
  *)
    echo "사용법: ./lab.sh <start|shell|status|reset>"
    echo ""
    echo "  start   실습실(빈 우분투) 기동"
    echo "  shell   실습실 입장 — 이 안에서 체크리스트 1~10 진행"
    echo "  status  실습실 상태 확인"
    echo "  reset   실습실 초기화 (설치 꼬였을 때 처음부터 다시)"
    ;;
esac
