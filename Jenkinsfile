pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Python deps') {
            steps {
                sh 'python3 -m pip install --user -r requirements.txt'
            }
        }

        stage('Python unit tests') {
            steps {
                sh 'python3 -m pytest tests/ -v --tb=short'
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Run stack (background)') {
            steps {
                sh 'docker compose up -d'
                sh 'sleep 20'
            }
        }

        stage('Newman (Postman collection)') {
            steps {
                sh '''
                    if command -v newman >/dev/null 2>&1; then
                        newman run postman/Inventory_API.postman_collection.json --env-var "baseUrl=http://localhost:8000"
                    elif command -v npx >/dev/null 2>&1; then
                        npx --yes newman run postman/Inventory_API.postman_collection.json --env-var "baseUrl=http://localhost:8000"
                    else
                        echo "Install Node.js; then: npm install -g newman"
                        exit 1
                    fi
                '''
            }
        }

        stage('Stop Docker containers') {
            steps {
                sh 'docker compose down -v || true'
            }
        }

        stage('Generate README.txt') {
            steps {
                sh 'python3 scripts/generate_readme_txt.py'
            }
        }

        stage('Zip deliverable') {
            steps {
                sh '''
                    TS=$(date +%Y-%m-%d-%H-%M-%S)
                    ZIP="complete-${TS}.zip"
                    zip -r "${ZIP}" \
                        app \
                        Dockerfile docker-compose.yml .dockerignore \
                        scripts requirements.txt products.csv README.txt pytest.ini \
                        postman tests Jenkinsfile
                '''
                archiveArtifacts artifacts: 'complete-*.zip', fingerprint: true, onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v || true'
        }
    }
}
