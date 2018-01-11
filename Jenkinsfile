pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile.jenkins-arm'
      label 'scanner'
      args '-v /tmp:/tmp'
    }
  }
  stages {
    stage('Test') {
      steps {
        sh 'tox -- --with-scanner'
        junit 'pytest.xml'
      }
    }
  }
}
