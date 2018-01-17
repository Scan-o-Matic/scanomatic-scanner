pipeline {
  agent none
  stages {
    stage('Test') {
      agent {
        dockerfile {
          filename 'Dockerfile.buildenv'
          label 'scanner'
          args '-v /dev/bus/usb:/dev/bus/usb --privileged'
        }
      }
      steps {
        sh 'scanimage -L'
        sh 'tox -- --with-scanner'
        junit 'pytest.xml'
      }
    }
    stage('Build') {
      agent { label 'scanner' }
      steps {
        sh 'docker build -t scanomaticd .'
      }
    }
    stage('System tests') {
      agent { label 'scanner' }
      steps {
        sh 'tox -e sys'
      }
    }
  }
}
