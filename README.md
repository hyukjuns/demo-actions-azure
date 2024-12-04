# demo-actions-azure
azure vm runner and docker ci

# Runner Setting
1. Runner 추가 및 설정 / 서비스 데몬으로 실행
    1.1 [추가 및 설정](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)
    1.2 [서비스 데몬으로 실행](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)
2. Self-hosted 러너 사용

    ```
    # 사용자 지정 레이블 세팅
    runs-on: [self-hosted, general-cpu]
    ```
3. 실행 기록 등 로그 확인
    - _diag 폴더
    - Runner 앱 실행 로그 -> Runner 로 시작
    - Job 실행 로그 -> Worker 로 시작
