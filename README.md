# demo-actions-azure
azure vm runner and docker ci

### 인프라 구성
1. VM 및 Storage 생성

    - VM Identity RBAC (블로 데이터 기여자) 세팅
    - blob container 생성

2. Runner Setting

    2.1 Runner 설치 및 구동
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

        4. 퍼블릭 저장소에서 Self Host Runner 사용시 보안 위험성
            - PR 트리거 사용할 경우 외부인이 PR 시 Action Pipe 실행 하게되는 위험 존재

            - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#self-hosted-runner-security

    2.2 azcli 및 docker 설치


### CI 파이프라인 구성
- Input으로 CPU / GPU Runner 선택
- 필요 변수 env로 선언 (ACR 및 File 경로 등)
- Buildkit의 레이어 캐시 설정
- 이미지 태그는 github commit id
- azure login은 vm identity로 대체
- github action envrionments로 승인 프로세스 적용

#### Steps
1. Checkout Repo
2. Setup Python
3. Install Requirements and Test Application
4. Upload Test Result to Blob
5. Docker build and push (push to ACR)
6. Download Test Tool From Blob
7. Docker run with volume (with download file) (image from ACR)
8. Test Application
9. Approve or Deny
10. Stop and Remove Container

### 참고사항
- Storage 접근 Identity: Azure VM System Assigned Identity
- 사전준비: 러너세팅, azcli, docker engine

