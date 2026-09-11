# 분석 환경 구축 실습 — 빈 리눅스에서 직접 설치하기

아무것도 설치되지 않은 우분투 리눅스 안에서 아나콘다 → 가상환경 → JupyterLab
→ JDK → PySpark를 **직접 설치하고 정상 동작을 검증**하는 실습입니다.

> **시작 전 체크**
> 1. 터미널에서 이 폴더로 이동했는지 확인: `cd data-analysis-labs/04-env-setup`
> 2. **이전 회차 환경을 껐는지 확인** (포트가 겹칩니다):
>    직전 회차 폴더에서 `docker compose down` 실행 후 돌아오세요.
>    실행 중인 것이 있는지는 `docker ps`로 확인할 수 있습니다.

---

## 0. 지금 내가 어디 있는지 — 이 실습 내내 가장 중요한 규칙

이 실습은 **두 개의 서로 다른 터미널 환경**을 오갑니다. 명령을 치기 전에
프롬프트 모양을 먼저 확인하는 습관을 들이세요.

| 프롬프트 모양 | 위치 | 여기서 되는 것 |
|---|---|---|
| `PS C:\...>` 또는 `C:\...>` | 내 PC (Windows) | `docker`, `.\lab.ps1` |
| `root@bigdata-lab:~#` | 리눅스 실습실 (컨테이너 안) | `conda`, `pip`, `python`, `apt` |

**conda/pip/python 명령은 반드시 `root@bigdata-lab:~#` 프롬프트에서만 동작합니다.**
Windows 프롬프트에서 치면 "명령을 찾을 수 없다"는 오류가 납니다.

---

## 1. 사전 준비 (Windows에서 최초 1회)

1. Docker Desktop 설치·실행 (WSL2 백엔드 사용)
2. 이 저장소 다운로드 후, 폴더에서:
   ```powershell
   docker compose pull
   ```
3. **PowerShell 스크립트 실행을 허용합니다** (아래 중 하나):
   ```powershell
   # 방법 A: 이번 PowerShell 창을 여는 즉시 한 번 실행 (창 닫으면 초기화)
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

   # 방법 B: 매 명령 앞에 붙이기 (매번 반복해야 함)
   powershell -ExecutionPolicy Bypass -File .\lab.ps1 shell
   ```
   > 이건 실습 내용과 무관한 Windows 보안 정책입니다. "디지털 서명되지
   > 않았습니다" 오류가 뜬다면 이 단계를 건너뛴 것입니다.

macOS/Linux는 대신 아래를 실행합니다.
```bash
chmod +x lab.sh
```

---

## 2. 실습실 입장

```bash
./lab.sh start      # Windows: .\lab.ps1 start
./lab.sh shell      # Windows: .\lab.ps1 shell
```

프롬프트가 `root@bigdata-lab:~#`로 바뀌면 성공입니다. 지금부터 모든
체크리스트 명령은 **이 안에서** 실행합니다. (나가기: `exit`, 다시 입장: `shell`)

> 설치가 꼬여서 처음부터 다시 하고 싶으면: 나간 뒤 `./lab.sh reset`
> `/root/work` 폴더는 내 PC의 `./work`와 공유되어 reset해도 파일이 남습니다.
> **단, conda·JDK·pip로 설치한 것들은 컨테이너 자체에 들어있어서 reset하면
> 전부 사라집니다.** (work 폴더 밖은 전부 초기화된다고 생각하세요.)

---

## 3. 체크리스트 진행

### 0. 기본 도구 준비 (리눅스 첫 걸음)

```bash
apt update && apt install -y wget nano
```

### 1. Miniconda 설치 → `conda --version`

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda3
/root/miniconda3/bin/conda init bash
source ~/.bashrc
conda --version        # 버전이 출력되면 통과
```

**바로 이어서 이용약관에 동의합니다** (최근 Miniconda는 이 단계가 없으면
다음 단계에서 `CondaToSNonInteractiveError`가 납니다):

```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

### 2. 가상환경 'bigdata' 생성·활성화

```bash
conda create -n bigdata python=3.11 -y
conda activate bigdata
# 프롬프트가 (base) → (bigdata) 로 바뀌는지 확인
```

> ⚠️ **이 실습에서 가장 흔한 실수**: `conda init bash`를 해두면 새 세션이
> 열릴 때마다 conda가 자동으로 `(base)`부터 시작합니다. `exit`으로 나갔다가
> `shell`로 다시 들어오면 방금 켰던 `(bigdata)`가 풀려 있습니다.
>
> **이후 모든 단계(3, 5, 6~8번)를 시작하기 전에 프롬프트 맨 앞이
> `(bigdata)`인지 항상 먼저 확인**하세요. 아니라면:
> ```bash
> conda activate bigdata
> ```
> 을 먼저 치고 진행하세요. `(base)`에 뭔가를 설치해버리면 `bigdata`
> 환경에는 없는 채로 남아, 나중에 `ModuleNotFoundError`로 나타납니다.

### 3. JupyterLab 설치·실행 확인

```bash
pip install jupyterlab
jupyter lab --version
# 실행(백그라운드): 컨테이너 안이므로 --ip, --allow-root 필요
nohup jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --no-browser \
  --NotebookApp.token='' --notebook-dir=/root/work > /root/jupyter.log 2>&1 &
```
→ 내 PC 브라우저에서 http://localhost:8888 접속 확인

### 4. Java JDK 17 설치 → `java -version`

```bash
apt install -y openjdk-17-jdk-headless
java -version          # openjdk version "17..." 확인
```

### 5. PySpark 설치

```bash
pip install pyspark numpy
pip list | grep -E "pyspark|numpy"
python -c "import pyspark; print(pyspark.__version__)"
```

### 6~8. SparkSession / DataFrame / MLlib 검증

JupyterLab(localhost:8888)에서 새 노트북을 만들고 `spark_smoke_test.py`의
코드를 셀별로 붙여넣어 실행하세요. 또는 터미널에서:

```bash
conda activate bigdata          # ⚠️ 재입장했다면 반드시 먼저! (위 2번 참고)
cd /root/work && python spark_smoke_test.py
```

- [6] `spark.version` 출력 확인
- [7] `df.show()` 표 출력 확인
- [8] Coefficients / Intercept 출력 확인

이 스크립트는 마지막에 아래처럼 멈춥니다:
```
브라우저에서 http://localhost:4040 (Spark UI) 접속을 확인한 뒤 Enter를 누르세요...
```
**여기서 바로 Enter 치지 말고** 브라우저로 `localhost:4040`을 먼저 열어
Spark Jobs 화면(체크리스트 10번)을 확인한 뒤 터미널로 돌아와 Enter를 누르세요.

> 💡 **Spark Jobs 화면 활용 팁**: 코드에서 진짜 액션은 `show()`, `count()`,
> `fit()` 세 번뿐인데 Job은 5개 안팎으로 찍힙니다. "코드 한 줄이 Spark
> 내부에서 여러 하위 작업으로 쪼개진다"는 걸 이 차이로 보여주면 좋습니다.

### 9. requirements.txt 작성 (팀 공유용)

```bash
pip freeze > /root/work/requirements.txt
head /root/work/requirements.txt
```
→ 내 PC의 `work/requirements.txt`로도 저장됩니다.

### 10. Spark UI 접속 확인

6~8번 스크립트 실행 중(Enter 누르기 전) 위에서 이미 확인했다면 통과입니다.

---

## 4. 최종 점검

```bash
bash /root/work/verify.sh
```

1~8번을 자동으로 채점해 ✅/❌로 보여줍니다(9번 Spark UI는 세션 실행
중에만 열리므로 수동 확인). 1~8번이 전부 ✅면 완료!

---

## 자주 겪는 문제

**Windows / 위치 관련**
- **"디지털 서명되지 않았습니다" 오류** → 1단계의 실행 정책 설정을 안 한
  것입니다. `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
  실행 후 재시도
- **PowerShell에서 "conda 용어가 인식되지 않습니다"** → Windows 프롬프트
  (`PS C:\...>`)에서 친 것입니다. `.\lab.ps1 shell`로 리눅스 실습실에
  들어간 뒤(`root@bigdata-lab:~#`) 다시 시도하세요 (위 "0. 지금 내가
  어디 있는지" 참고)

**conda 관련**
- **`CondaToSNonInteractiveError`(이용약관 미동의)** → 1번 항목의
  `conda tos accept` 두 줄을 먼저 실행
- **`(bigdata)`가 아닌 `(base)`에서 pip install 함** →
  `conda activate bigdata` 후 재설치. 재입장할 때마다 `(base)`로
  초기화된다는 걸 기억하세요 (2번 항목 참고)
- **`conda: command not found`** → `source ~/.bashrc` 실행 또는
  재입장(`exit` 후 `shell`)
- **`EnvironmentNameNotFound: bigdata`** → `conda env list`로 실제
  존재하는 환경을 확인. 없다면 `./lab.sh reset`을 실행했거나 컨테이너가
  재생성된 것입니다 — 2번(가상환경 생성)부터 다시 진행하면 됩니다

**실행 관련**
- **jupyter lab이 브라우저에 안 열림** → 컨테이너 안이라 자동으로 안
  열립니다. 주소창에 localhost:8888 직접 입력
- **4040이 안 열림** → SparkSession이 실행 중일 때만 열립니다. 세션
  종료(Enter) 전에 확인
- **전부 꼬임** → `exit` → `./lab.sh reset` → 처음부터 (work 폴더
  파일은 안전, 단 conda/JDK 등 설치했던 것은 전부 사라지므로 1번부터
  다시 진행)
