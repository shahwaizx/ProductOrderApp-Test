pipeline {
    agent any

    environment {
        MAIN_REPO = 'https://github.com/shahwaizx/ProductOrderDB.git'
        TEST_REPO = 'https://github.com/shahwaizx/ProductOrderApp-Test.git'
        MAIN_DIR  = '/var/lib/jenkins/ProductOrderApp-Selenium'
        TEST_DIR  = '/var/lib/jenkins/ProductOrderApp-Test'
    }

    stages {
        stage('Clean workspace') {
            steps {
                sh '''
                echo "🧹 Cleaning workspace..."
                rm -rf $MAIN_DIR $TEST_DIR
                mkdir -p $MAIN_DIR $TEST_DIR
                '''
            }
        }

        stage('Clone Repositories') {
            steps {
                sh '''
                echo "📥 Cloning Main App..."
                git clone $MAIN_REPO $MAIN_DIR

                echo "📥 Cloning Test Suite..."
                git clone $TEST_REPO $TEST_DIR
                '''
            }
        }

        stage('Build & Run Selenium Tests') {
            steps {
                dir("$TEST_DIR") {
                    sh '''
                    echo "🐳 Building Docker image for tests..."
                    docker build -t productorderapp-tests .

                    echo "🧪 Running Selenium tests..."
                    # capture output even if tests fail
                    docker run --rm productorderapp-tests > test_output.txt || true
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                // get the committer email from the main repo
                def authorEmail = sh(
                    script: "cd $MAIN_DIR && git log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                // send the raw test output as attachment
                emailext(
                    to: authorEmail,
                    subject: "Jenkins Test Results — Build ${env.BUILD_NUMBER} (${currentBuild.currentResult})",
                    body: """\
Hi there,

Your recent push to ProductOrderApp triggered an automated Selenium test run.

• Build number: ${env.BUILD_NUMBER}  
• Status: ${currentBuild.currentResult}  
• Details: ${env.BUILD_URL}

Please see the attached test_output.txt for the full console logs.

Regards,  
Jenkins Bot
""",
                    // use a glob so Jenkins can locate the file
                    attachmentsPattern: "**/test_output.txt"
                )
            }
        }
    }
}
