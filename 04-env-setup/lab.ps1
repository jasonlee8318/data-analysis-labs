# ============================================================
# 분석 환경 구축 실습 — 실습실 관리 스크립트 (Windows PowerShell)
# 사용법: .\lab.ps1 <start|shell|status|reset>
# 실행 정책 오류 시: powershell -ExecutionPolicy Bypass -File .\lab.ps1 start
# ============================================================
param([string]$Cmd = "help")

switch ($Cmd) {
    "start" {
        Write-Host "[START] 빈 리눅스 실습실을 기동합니다"
        docker compose up -d
        Write-Host ""
        Write-Host ">> 입장: .\lab.ps1 shell"
    }
    "shell" {
        Write-Host "[SHELL] 실습실에 입장합니다 (나가기: exit)"
        docker compose exec lab bash
    }
    "status" {
        docker compose ps
    }
    "reset" {
        Write-Host "[RESET] 실습실을 초기화합니다 (설치한 것 전부 삭제)"
        Write-Host "        ※ /root/work 안의 파일은 내 PC의 .\work 폴더에 남습니다."
        docker compose down
        docker compose up -d
        Write-Host "완료. .\lab.ps1 shell 로 다시 입장하세요."
    }
    default {
        Write-Host "사용법: .\lab.ps1 <start|shell|status|reset>"
        Write-Host ""
        Write-Host "  start   실습실(빈 우분투) 기동"
        Write-Host "  shell   실습실 입장 - 이 안에서 체크리스트 1~10 진행"
        Write-Host "  status  실습실 상태 확인"
        Write-Host "  reset   실습실 초기화 (설치 꼬였을 때 처음부터 다시)"
    }
}
