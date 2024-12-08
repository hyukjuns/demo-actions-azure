# demo-actions-azure
azure vm runner and docker ci

### 인프라 구성
1. VM 및 StorageAccount 생성

    - VM System Assigend Identity Enabled > RBAC (블롭 데이터 기여자)
    - StorageAccount > blob container 생성

2. [Runner 설치](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)

3. [서비스 데몬으로 실행](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)

4. [azcli 설치](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)

5. [docker 설치](https://docs.docker.com/engine/install/ubuntu/)

> 참고내용
- pipeline에서 self-hosted runner 사용

    ```yaml
        # 사용자 지정 레이블 세팅
        runs-on: [self-hosted, general-cpu]
    ```
- Log 확인
    
    ```bash
        actions-runner/_diag/ # Action Home Directory
                    ├── Runner_20241204-085156-utc.log # Runner Application log
                    ├── Worker_20241204-095211-utc.log # Job Running log
    ```

- security 유의사항
    
    - 퍼블릭 저장소에서 Self Host Runner 사용시 보안 위험성
        - PR 트리거 사용할 경우 외부인이 PR 시 Action Pipe 실행 하게되는 위험 존재
        - https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#self-hosted-runner-security

### CI 파이프라인 디자인
- Input으로 CPU / GPU Runner 선택
- 필요 변수 env로 선언 (ACR 및 File 경로 등)
- Buildkit의 레이어 캐시 설정
- 이미지 태그는 github commit id
- azure login은 vm identity로 대체
- github action envrionments로 승인 프로세스 적용

### CI Steps
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

