pipeline {
    agent any

    environment {
        IMAGE_NAME = 'system-health-dashboard'
        CONTAINER_NAME = 'system-health-dashboard-jenkins'
        HOST_PORT = '5001'
    }

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                bat 'python -m venv .venv'
                bat '.venv/Scripts/python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat '.venv/Scripts/python.exe -m pytest -q'
            }
        }

        stage('Build') {
            steps {
                bat 'set DOCKER_BUILDKIT=1 && docker build -t %IMAGE_NAME%:build-%BUILD_NUMBER% .'
            }
        }

        stage('Tag') {
            steps {
                bat 'docker tag %IMAGE_NAME%:build-%BUILD_NUMBER% %IMAGE_NAME%:%BUILD_NUMBER%'
            }
        }

        stage('Health check') {
            steps {
                bat 'docker rm -f %CONTAINER_NAME% >NUL 2>&1 || exit /b 0'
                bat 'docker run -d --name %CONTAINER_NAME% -p %HOST_PORT%:5000 -e ENVIRONMENT=jenkins %IMAGE_NAME%:%BUILD_NUMBER%'
                bat 'powershell -NoProfile -Command "Start-Sleep 5; $r=Invoke-WebRequest http://localhost:%HOST_PORT%/health; if ($r.StatusCode -ne 200) { exit 1 }"'
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %CONTAINER_NAME% >NUL 2>&1 || exit /b 0'
        }
    }
}