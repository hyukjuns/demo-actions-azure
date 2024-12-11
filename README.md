# demo-actions-azure
azure vm runner and docker ci

### 인프라 구성
1. VM 및 Storage Account / ACR 생성

    - VM System Assigend Identity Enabled > RBAC (블롭 데이터 기여자)
    - StorageAccount > blob container 생성

2. [Runner 설치](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)

3. [서비스 데몬으로 실행](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)

4. [azcli 설치](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)

5. [docker 설치](https://docs.docker.com/engine/install/ubuntu/)

### CI 파이프라인 설계 고려사항
- [Input으로 CPU / GPU 레이블 선택하여 Job 실행할 Runner 선택](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/using-self-hosted-runners-in-a-workflow#using-custom-labels-to-route-jobs)
- 필요 변수 env로 선언 (ACR 및 File 경로 등)
- [Buildkit의 레이어 캐시 설정 - local cache](https://docs.docker.com/build/ci/github-actions/cache/#local-cache)
- [컨테이너 구동시 다운로드 받은 파일 사용 (bind mount)](https://docs.docker.com/engine/storage/bind-mounts/)
- 이미지 태그는 github commit id
- azure login은 vm identity로 대체
- [github action envrionments](https://docs.github.com/ko/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment)로 승인 프로세스 적용
- docker image 용량 정리

    - [docs](https://docs.docker.com/reference/cli/docker/system/prune/)
    - docker system prune -a

- docker log lotate
    - [docs](https://docs.docker.com/engine/logging/drivers/json-file/)
    - /etc/docker/daemon.json
        
        ```json
        {
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "3"
            }
        }
        ```
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


### 파이프라인 순서
```
1. Checkout Repository
2-1. Setup Python
2-2. Install Requirements Package and Excute PyTest
3-1. Azure Login
3-2. Upload PyTest Result to Blob (AzureCLI)
3-3. Upload PyTest Result to GithubActions
3-4. Download File From Blob (AzureCLI)
4-1. Set up Docker Buildx
4-2. Docker build (Save image to local) / Use Buildx Local Cache / Save Image to local
5. Docker Run (bind mount)
6-1. Curl Test (Container)
6-2. Upload Curl Test Result to Blob (AzureCLI)
7. Approve or Deny
8-1. Login to ACR
8-2. Push Image to ACR
9. Stop and Remove Container
```