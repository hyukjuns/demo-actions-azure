# demo-actions-azure
Github Action CI with Self Host Runner (Azure VM)

## Workflow Overview
```
# JOB-01: Applicaion Test, Docker Build and Run (In Local)
1. Checkout Repository
2-1. Setup Python
2-2. Install Requirements Package and PyTest
3-1. Azure Login
3-2. Upload PyTest Result to Blob (AzureCLI)
3-3. Upload PyTest Result to GithubActions
3-4. Download File From Blob (AzureCLI)
4-1. Set up Docker Buildx
4-2. Docker build (Local)
5. Docker Run (bind mount)
6-1. Curl Test (Container)
6-2. Upload Curl Test Result to Blob (AzureCLI)

# JOB-02: PUSH ACR (If Approve)
1. Azure Login
2. Login to ACR (VM Identity) & Push Image to ACR
3. Stop and Remove Container, Image

# JOB-03: Run on GPU Runner - PULL And Run Container (If Approve)
1. Azure Login
2. Download File From Blob (AzureCLI)
3. Login to ACR & Run Container (Image from ACR)
4. Curl Test (Container)
5. Upload Test Result to Blob (AzureCLI)
6. Stop and Remove Container, Image
```

## Setup Infrastructure
### Azure Virtual Machine
- Github Action의 Self hosted Runner로 사용 (2대)
- Virtual Machine의 System Assigned Identity를 활성화 (Workflow에서 Azure 접근시 인증/인가 용도로 사용)

System Assigned Identity Rquired RBAC

  - Role: Storage Blob Data Contributor | Scope: StorageAccount

  - Role: AcrPull, AcrPush | Scope: Azure Container Registry

### Storage Account
- File Up/Download 절차를 위해 Blob Container 사전 생성 필요
- Private Endpoints 사용

### Azure Container Registry
- 빌드된 이미지 저장목적
- Private Endpoints 사용 Premium SKU 사용 필요
### Runner 설치 및 등록

[adding-self-hosted-runners](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)

[configuring-the-self-hosted-runner-application-as-a-service](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)

Step 01. Download Install Files
```bash
# Create a folder
mkdir actions-runner && cd actions-runner

# Download the latest runner package
curl -o actions-runner-linux-x64-2.321.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz

# Optional: Validate the hash
echo "ba46ba7ce3a4d7236b16fbe44419fb453bc08f866b24f04d549ec89f1722a29e  actions-runner-linux-x64-2.321.0.tar.gz" | shasum -a 256 -c

# Extract the installer
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz

```

Step 02. Configure Runner
```bash
# Create the runner and start the configuration experience
./config.sh --url https://github.com/hyukjuns/demo-actions-azure --token <YOURTOKEN>

# Enter Custom Lable
설정 절차 진행 중 사용자 지정 Label 입력하여 추후 Worklfow 실행시 Runner 선택을 위한 Input 변수로 사용
```

Step 03. Enroll Service Daemon
```bash
# Enroll Systemd Service
sudo ./svc.sh install

# Start Service
sudo ./svc.sh start

# Option: Check Service Status
sudo ./svc.sh status
```

(ETC) Runner & Job Log

```bash
actions-runner/_diag/ # Action's Home Directory
            ├── Runner_20241204-085156-utc.log # Runner Application log
            ├── Worker_20241204-095211-utc.log # Job Running log
```

### Install Required Software

- [Install azcli (Ubuntu)](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)

- [Install docker engine (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/)

    - [Docker Log Rotate 설정](https://docs.docker.com/engine/logging/drivers/json-file/)

        `/etc/docker/daemon.json`
        ```json
        {
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "3"
            }
        }
        ```
    - [Docker Image / Cache 데이터 관리](https://docs.docker.com/reference/cli/docker/system/prune/)
    
        `docker system prune -a`

## Design CI Workflow
1. VM Identity로 StorageAccount / ACR 로그인

    1. azure/login@v2 플러그인으로 azure 로그인

        `auth-type: IDENTITY`

    2. Inline-Shell 로 StorageAccount / ACR 로그인

        `az storage blob upload`

        `az acr login`

2. Workflow Input으로 Runner의 Label 선택하여 Job을 실행할 Runner 선택

    [사용자 지정 레이블을 사용하여 작업 라우팅](https://docs.github.com/ko/enterprise-cloud@latest/actions/hosting-your-own-runners/managing-self-hosted-runners/using-self-hosted-runners-in-a-workflow#using-custom-labels-to-route-jobs)

    ```yaml
    on:
        workflow_dispatch:
            inputs:
            runner-type:
                required: true
                type: choice
                options:
                - general-cpu
                - gpu
        job-01-ci:
            runs-on: [self-hosted, "${{ inputs.runner-type }}"]
    ```
3. Docker Build Cache 설정

    docker/build-push-action@v6.9.0 플러그인의 로컬 캐시 옵션 사용 
    
    [Local cache](https://docs.docker.com/build/ci/github-actions/cache/#local-cache)

    ```yaml
    - uses: docker/build-push-action@v6.9.0
      with:
        cache-from: type=local,src=${{ env.BUILDX_CACHE_DIR }}
        cache-to: type=local,dest=${{ env.BUILDX_CACHE_DIR }},mode=max
    ```
4. Docker 기타 설정
    
    Bind Mount로 파일 마운트 및 ENV로 Filepath 설정, 이미지 태그는 github commit id
    
    [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)

    ```bash
    docker run -d -p 8080:8080 \
    --name ${{ env.CONTAINER_NAME }} \
    -v "${{ github.workspace }}/${{ env.DOWNLOAD_FILENAME }}":/home/python/${{ env.DOWNLOAD_FILENAME }} \
    -e FILEPATH="/home/python/${{ env.DOWNLOAD_FILENAME }}" \
    ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    ```
5. 승인 프로세스

    [github action envrionments](https://docs.github.com/ko/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment)


    Github Action의 Environments 로 Job 실행 전 승인 절차 적용

    ```
    job-02-push-acr:
        runs-on: [self-hosted, "${{ inputs.runner-type }}"]
        environment: need-approvals
        needs: job-01-ci
        if: success()
    ```

6. Security 유의사항
    
    퍼블릭 저장소에서 Self Host Runner 사용시 보안 위험성 주의의
        
    - PR 트리거 사용할 경우 외부인이 PR 시 Action Pipe 실행 하게되는 위험 존재
       
    - [Self-hosted runner security](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#self-hosted-runner-security)
