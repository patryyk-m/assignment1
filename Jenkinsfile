pipeline {
    agent any

    stages {
        stage('Install Python deps') {
            steps {
                bat 'python -m pip install --user -r requirements.txt'
            }
        }

        stage('Python unit tests') {
            steps {
                bat 'python -m pytest tests/ -v --tb=short'
            }
        }

        stage('Build Docker image') {
            steps {
                bat 'docker compose build'
            }
        }

        stage('Run stack (background)') {
            steps {
                bat 'docker compose up -d'
                bat 'powershell -NoProfile -Command "Start-Sleep -Seconds 20"'
            }
        }

        stage('Newman (Postman collection)') {
            steps {
                bat 'npx --yes newman run postman/Inventory_API.postman_collection.json --env-var "baseUrl=http://localhost:8000"'
            }
        }

        stage('Stop Docker containers') {
            steps {
                bat 'docker compose down -v'
            }
        }

        stage('Generate README.txt') {
            steps {
                bat 'python scripts/generate_readme_txt.py'
            }
        }

        stage('Zip deliverable') {
            steps {
                powershell '''
                    $ts = Get-Date -Format 'yyyy-MM-dd-HH-mm-ss'
                    $zip = "complete-$ts.zip"
                    $items = @(
                        'app',
                        'Dockerfile',
                        'docker-compose.yml',
                        '.dockerignore',
                        'scripts',
                        'requirements.txt',
                        'products.csv',
                        'README.txt',
                        'pytest.ini',
                        'postman',
                        'tests',
                        'Jenkinsfile'
                    )
                    Compress-Archive -Path $items -DestinationPath $zip -Force
                '''
                archiveArtifacts artifacts: 'complete-*.zip', fingerprint: true, onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            bat '''
docker compose down -v
exit /b 0
'''
        }
    }
}
