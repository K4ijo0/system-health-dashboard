pipeline {
    agent any

    environment {
        IMAGE_NAME = 'system-health-dashboard'
        CONTAINER_NAME = 'system-health-dashboard-jenkins'
        HOST_PORT = '5001'
        STAGING_DEPLOYED = 'false'
        PRODUCTION_DEPLOYED = 'false'
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
                bat '"C:/Users/Fahad/AppData/Local/Programs/Python/Python313/python.exe" -m venv .venv'
                bat '.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat '.\\.venv\\Scripts\\python.exe -m pytest -q'
            }
        }

        stage('Build') {
            steps {
                bat 'set "DOCKER_BUILDKIT=1" && docker build -t %IMAGE_NAME%:build-%BUILD_NUMBER% .'
            }
        }

        stage('Tag') {
            steps {
                // The release tag is the immutable image promoted through both environments.
                bat 'docker tag %IMAGE_NAME%:build-%BUILD_NUMBER% %IMAGE_NAME%:release-%BUILD_NUMBER%'
            }
        }

        stage('Local health check') {
            steps {
                bat 'docker rm -f %CONTAINER_NAME% >NUL 2>&1 || exit /b 0'
                bat 'docker run -d --name %CONTAINER_NAME% -p %HOST_PORT%:5000 -e ENVIRONMENT=jenkins %IMAGE_NAME%:release-%BUILD_NUMBER%'
                bat 'powershell -NoProfile -Command "Start-Sleep 5; $r=Invoke-WebRequest -UseBasicParsing -Uri http://localhost:%HOST_PORT%/health -ErrorAction Stop; if ($r.StatusCode -ne 200) { exit 1 }"'
            }
        }

        stage('Prepare deployment network') {
            steps {
                // The application Compose files join this shared external network.
                bat 'docker network inspect system-health-network >NUL 2>&1 || docker network create system-health-network'
            }
        }

        stage('Deploy staging') {
            steps {
                script {
                    env.STAGING_DEPLOYED = 'true'
                }
                bat '''
                    docker image inspect %IMAGE_NAME%:staging-current >NUL 2>&1
                    if not errorlevel 1 docker tag %IMAGE_NAME%:staging-current %IMAGE_NAME%:staging-previous
                    set "APP_IMAGE=%IMAGE_NAME%:release-%BUILD_NUMBER%"
                    docker compose -f docker-compose.staging.yml up -d --no-build --force-recreate
                    if errorlevel 1 exit /b 1
                    docker tag %IMAGE_NAME%:release-%BUILD_NUMBER% %IMAGE_NAME%:staging-current
                '''
            }
        }

        stage('Staging smoke tests') {
            steps {
                bat 'powershell -NoProfile -Command "Start-Sleep 5; $health=Invoke-WebRequest -UseBasicParsing -Uri http://localhost:5001/health -ErrorAction Stop; if ($health.StatusCode -ne 200) { exit 1 }; $metrics=Invoke-WebRequest -UseBasicParsing -Uri http://localhost:5001/metrics -ErrorAction Stop; if ($metrics.StatusCode -ne 200) { exit 1 }"'
            }
        }

        stage('Production approval') {
            steps {
                input message: 'Staging smoke tests passed. Deploy this same image to production?', ok: 'Deploy to production'
            }
        }

        stage('Deploy production') {
            steps {
                script {
                    env.PRODUCTION_DEPLOYED = 'true'
                }
                bat '''
                    docker image inspect %IMAGE_NAME%:production-current >NUL 2>&1
                    if not errorlevel 1 docker tag %IMAGE_NAME%:production-current %IMAGE_NAME%:production-previous
                    set "APP_IMAGE=%IMAGE_NAME%:release-%BUILD_NUMBER%"
                    docker compose -f docker-compose.production.yml up -d --no-build --force-recreate
                    if errorlevel 1 exit /b 1
                    docker tag %IMAGE_NAME%:release-%BUILD_NUMBER% %IMAGE_NAME%:production-current
                '''
            }
        }

        stage('Production smoke tests') {
            steps {
                bat 'powershell -NoProfile -Command "Start-Sleep 5; $health=Invoke-WebRequest -UseBasicParsing -Uri http://localhost:5002/health -ErrorAction Stop; if ($health.StatusCode -ne 200) { exit 1 }; $metrics=Invoke-WebRequest -UseBasicParsing -Uri http://localhost:5002/metrics -ErrorAction Stop; if ($metrics.StatusCode -ne 200) { exit 1 }"'
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %CONTAINER_NAME% >NUL 2>&1 || exit /b 0'
        }
        failure {
            script {
                // Restore the last known image after a failed deployment or smoke test.
                if (env.PRODUCTION_DEPLOYED == 'true') {
                    bat '''
                        docker image inspect %IMAGE_NAME%:production-previous >NUL 2>&1
                        if not errorlevel 1 (
                            set "APP_IMAGE=%IMAGE_NAME%:production-previous"
                            docker compose -f docker-compose.production.yml up -d --no-build --force-recreate
                            docker tag %IMAGE_NAME%:production-previous %IMAGE_NAME%:production-current
                        )
                    '''
                }
                if (env.STAGING_DEPLOYED == 'true') {
                    bat '''
                        docker image inspect %IMAGE_NAME%:staging-previous >NUL 2>&1
                        if not errorlevel 1 (
                            set "APP_IMAGE=%IMAGE_NAME%:staging-previous"
                            docker compose -f docker-compose.staging.yml up -d --no-build --force-recreate
                            docker tag %IMAGE_NAME%:staging-previous %IMAGE_NAME%:staging-current
                        )
                    '''
                }
            }
        }
    }
}
