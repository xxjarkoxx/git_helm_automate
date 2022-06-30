import groovy.json.JsonBuilder
import groovy.json.JsonSlurperClassic
import groovy.json.JsonOutput


pipeline {
  
    agent {
    kubernetes {
      label 'pruebaPython'
      defaultContainer 'jnlp'
      yaml """
apiVersion: v1
kind: Pod
metadata:
  name: slave
spec:
  securityContext:
    runAsUser: 1000
  serviceAccount: kaniko
  containers:
  - name: slave
    image: registry.global.ccc.srvb.bo.paas.cloudcenter.corp/san-devops/python:1.0
    imagePullPolicy: Always
    env:
      - name: PROXY
        value: http://proxyapps.gsnet.corp:80
    tty: true
"""
        }
    }

    parameters {
        /*choice(name: 'Cluster', choices: ['ALL','PRODARWIN','PROAZURE','DMZDARWIN','PROBKS','DMZBKS','PRCONFLUENT'], description: 'Seleccionando el cluster figura')
        password(name: 'Token_cluster_1', defaultValue: 'El token aquí, joven padawn', description: 'Introducir el token para acceder al cluster PRODARWIN')
        password(name: 'Token_cluster_2', defaultValue: 'la fuerza es intensa en ti', description: 'Introducir el token para acceder al cluster PROAZURE')
        password(name: 'Token_cluster_3', defaultValue: 'yo soy tu padre', description: 'Introducir el token para acceder al cluster DMZDARWIN')
        password(name: 'Token_cluster_4', defaultValue: 'que la fuerza te acompañe', description: 'Introducir el token para acceder al cluster PROBKS')
        password(name: 'Token_cluster_5', defaultValue: 'El miedo es el camino hacia el Lado Oscuro. El miedo lleva a la ira, la ira lleva al odio, el odio lleva al sufrimiento. Percibo mucho miedo en ti', description: 'Introducir el token para acceder al cluster DMZBKS')
        password(name: 'Token_cluster_6', defaultValue: 'Chewie ... estamos en casa', description: 'Introducir el token para acceder al cluster PROCONFLUENT')*/
        string(name: 'Deployments', defaultValue: 'micro', description: 'Introducir micros separados por , por favor')
    }

    environment {
        imagetag = "latest"                
        namespace = "shuttle-san"
        project = "paco"
        timestamp = sh (returnStdout: true, script: '''
                                            #!/busybox/sh                                                  
                                            timestamp=$(date +%Y%m%d%H%M)
                                            tag="${timestamp}"
                                            echo $tag ''')
        LANG="C.UTF-8"
        LC_ALL="C.UTF-8"
    }

    stages {
        stage('Joven Padawan - ejecutando deploy pro') {
            steps {               
                container(name: 'slave', shell: '/bin/bash') {
                    script {
                        retry(3) {
						    sh(script: "pip3 install --proxy http://proxyapps.gsnet.corp:80 --upgrade pip")
                        }
                        retry(3) {
						    sh(script: "pip3 install --proxy http://proxyapps.gsnet.corp:80 --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt")
                        }
                        /*sh(script: "pip3 install --proxy http://proxyapps.gsnet.corp:80 --trusted-host pypi.org -r requirements.txt")*/
                        sh(script: "set +x")
						sh(script: "/usr/bin/python3 ./deploy-dev.py ${Deployments}")                          
                    }
                }
            }
        }        
    }
}
