import requests
import os
import time
import sys
import urllib3
import yaml


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

conf_path = os.path.basename('config.yml')
namespace_alma_dev = "sanes-shuttlepython-dev"
cluster_type = "CLUSTER_TYPE"
kube_api_bks = "https://api.san01bks.san.dev.bo1.paas.cloudcenter.corp:6443"
kube_api_azure = "https://api.ocp01.san.dev.weu1.azure.paas.cloudcenter.corp:6443"
registry = "registry.global.ccc.srvb.bo.paas.cloudcenter.corp"
registry_azure = "registry.san.dev.weu.azure.paas.cloudcenter.corp"
config_end_point = "CONFIG_END_POINT"
json_config_bks = "http://configuration-service:8080/shuttle-dashboard-front-dev-bks.json"
json_config_azure = "http://configuration-service:8080/shuttle-dashboard-front-dev-azure.json"
region = "REGION"
secret = "config-service-key"
config_service = "configuration-service"

with open(conf_path, "r") as file:
    config = yaml.full_load(file)

def obtener_svc_http_code(api,token,ns,micro):
    request_url = api + "/api/v1/namespaces/"+ns+"/services/"+micro
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    result = requests.get(request_url, headers=headers, verify=False) 
    return result.status_code

def obtener_dc_http_code(url,token,ns,dc):
    request_url = url + "/apis/apps.openshift.io/v1/namespaces/"+ns+"/deploymentconfigs/"+dc
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}    
    result = requests.get(request_url, headers=headers, verify=False)
    return result.status_code

def obtener_route_http_code(url,token,ns,dc):
     request_url = url + "/apis/route.openshift.io/v1/namespaces/"+ns+"/routes/"+dc
     headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}    
     result = requests.get(request_url, headers=headers, verify=False)
     return result.status_code
 
def obtener_config_svc_http_code(url,token,ns,dc):
    request_url = url + "/apis/apps.openshift.io/v1/namespaces/"+ns+"/deploymentconfigs/"+dc
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}    
    result = requests.get(request_url, headers=headers, verify=False)
    return result.status_code

def status_cluster(api_url,token,ns_dev,dc):
    svc = dc
    status_svc = 0
    status_dc = 0
    status_route = 0
    status_config_service = 0
    """saber si existe el servicio"""
    http_code = obtener_svc_http_code(api_url,token,ns_dev,svc)
    if http_code == 200:
        status_svc = 1
    """saber si existe ya el deployment"""
    http_code = obtener_dc_http_code(api_url,token,ns_dev,dc)
    if http_code == 200:
        status_dc = 1
    """saber si existe ya la ruta"""
    http_code = obtener_route_http_code(api_url,token,ns_dev,dc)
    if http_code == 200:
        status_route = 1
    """saber si existe ya el config-service"""
    http_code = obtener_config_svc_http_code(api_url,token,ns_dev,config_service)
    if http_code == 200:
        status_config_service = 1
    dict_result = {}
    dict_result["status_svc"] = status_svc
    dict_result["status_dc"] = status_dc
    dict_result["status_route"] = status_route
    dict_result["status_config"] = status_config_service
    return dict_result

def obtener_svc(api,token,ns,svc):
    request_url = api + "/api/v1/namespaces/"+ns+"/services/"+svc
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    result = requests.get(request_url, headers=headers, verify=False)    
    return result.json()     

def obtener_dc(url,token,ns,dc):
    request_url = url + "/apis/apps.openshift.io/v1/namespaces/"+ns+"/deploymentconfigs/"+dc
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    result = requests.get(request_url, headers=headers, verify=False)
    return result.json() 

def obtener_secret(url,token,ns,secreto):
    request_url = url + "/api/v1/namespaces/"+ns+"/secrets/"+secreto
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    result = requests.get(request_url, headers=headers, verify=False)
    return result.json()

def componer_svc(yaml_svc):
    yaml_svc["metadata"].pop("resourceVersion")
    yaml_svc["spec"].pop("clusterIP")
    return yaml_svc    

def componer_dc(yml,dc,api,forma,yml_existente):
    if forma == "1":      
        yml["metadata"]["uid"] = yml_existente["metadata"]["uid"]
        try:
            yml["metadata"]["selfLink"] = yml_existente["metadata"]["selfLink"]
        except:
            print("Atacando a cluster sin selfLink")
        yml["metadata"]["creationTimestamp"] = yml_existente["metadata"]["creationTimestamp"]
        yml["metadata"]["generation"] = yml_existente["metadata"]["generation"]
        yml["metadata"]["resourceVersion"] = yml_existente["metadata"]["resourceVersion"]
    else:
        yml["metadata"].pop("resourceVersion")
    try:
        yml["metadata"].pop("annotations")
    except:
        print("El micro %s no tiene annotations en metadata",yml["metadata"]["name"])
    if api == kube_api_azure:
        imagen = yml["spec"]["template"]["spec"]["containers"][0]["image"]
        image = str(imagen)
        imagen_azure = image.replace(registry,registry_azure)
        yml["spec"]["template"]["spec"]["containers"][0]["image"] = imagen_azure
    env_vars = yml["spec"]["template"]["spec"]["containers"][0].get("env")     
    for i in range(len(env_vars)):
        if yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["name"] == cluster_type:   
            if api == kube_api_bks:
                yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["value"] = "bks"        
        elif yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["name"] == region:
            if api == kube_api_azure:
                yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["value"] = "weu1"
        elif yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["name"] == config_end_point:
            if api == kube_api_bks:
                yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["value"] = json_config_bks
            elif api == kube_api_azure:
                yml["spec"]["template"]["spec"]["containers"][0]["env"][i]["value"] = json_config_azure   
    yml.pop("status")                             
    return yml

def componer_route(dc):
    yml = {}    
    yml["apiVersion"] = "route.openshift.io/v1"
    yml["kind"] = "Route"
    yml["metadata"] = {}
    yml["metadata"]["name"] = dc
    yml["metadata"]["namespace"] = namespace_alma_dev
    yml["spec"] = {}
    yml["spec"]["host"] = ""
    yml["spec"]["path"] = ""
    yml["spec"]["port"] = {}
    yml["spec"]["port"]["targetPort"] = dc
    yml["spec"]["tls"] = {}
    yml["spec"]["tls"]["termination"] = "edge"
    yml["spec"]["to"] = {}
    yml["spec"]["to"]["kind"] = "Service"
    yml["spec"]["to"]["name"] = dc
    yml["spec"]["to"]["weight"] = 100
    yml["spec"]["wildcardPolicy"] = "None"
    return yml
    
def componer_secret(yml):
    yml["metadata"].pop("creationTimestamp")
    yml["metadata"].pop("resourceVersion")
    yml["metadata"].pop("selfLink")
    yml["metadata"].pop("uid")
    return yml
    
def create_service(yaml_svc,api,token,micro):
    request_url = api +"/api/v1/namespaces/"+namespace_alma_dev+"/services"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
               "Content-type": "application/json"}
    result = requests.post(request_url, headers=headers, verify=False, json=yaml_svc) 
    return result.status_code

def create_dc(yml,url,token):
    request_url = url+"/apis/apps.openshift.io/v1/namespaces/"+namespace_alma_dev+"/deploymentconfigs"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
               "Content-type": "application/json"}
    result = requests.post(request_url, headers=headers, verify=False, json=yml) 
    return result.status_code

def crear_route(url,token,ns,micro,yml):
    request_url = url+"/apis/route.openshift.io/v1/namespaces/"+ns+"/routes"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
               "Content-type": "application/json"}
    result = requests.post(request_url, headers=headers, verify=False, json=yml) 
    return result.status_code    

def create_secret(url,token,ns,yml):
    request_url = url +"/api/v1/namespaces/"+ns+"/secrets"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
               "Content-type": "application/json"}
    result = requests.post(request_url, headers=headers, verify=False, json=yml) 
    return result.status_code

def reemplazar_dc(yml,api,token,ns,dc):
    request_url = api+"/apis/apps.openshift.io/v1/namespaces/"+ns+"/deploymentconfigs/"+dc
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
               "Content-type": "application/json"}
    result = requests.put(request_url, headers=headers, verify=False, json=yml) 
    return result.status_code

def orquestador_creacion_modificacion_dc_svc(status,api_url,token,micro,api_origen,token_origen):
    if status["status_config"] == 0 and micro == config_service:
        """No existe el configuration service"""
        print("Joven padawan no existe el configuration service")
        yaml_svc = obtener_svc(api_origen,token_origen,namespace_alma_dev,config_service)
        yaml_svc_created = componer_svc(yaml_svc)
        http_code = create_service(yaml_svc_created,api_url,token,config_service)
        if http_code in (200,201):
            print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el service o svc %s"%(namespace_alma_dev,api_url,config_service))
            yaml_secret = obtener_secret(api_origen,token_origen,namespace_alma_dev,secret)
            yaml_secret_created = componer_secret(yaml_secret)
            http_code_secret = create_secret(api_url,token,namespace_alma_dev,yaml_secret_created)
            if http_code_secret in (200,201):
                print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el service o svc %s"%(namespace_alma_dev,api_url,config_service))
                yaml_dc = obtener_dc(api_origen,token_origen,namespace_alma_dev,config_service)
                yaml_dc_created = componer_dc(yaml_dc,micro,api_url,"0","")
                http_code = create_dc(yaml_dc_created,api_url,token)
                if http_code in (200,201):
                    print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el dc %s"%(micro,api_url,micro))
    if status["status_svc"] == 0:
        """No existe el servicio"""
        print("Joven padawan, no existe svc para el micro %s por tanto se procede a crearlo."%micro)
        yaml_svc = obtener_svc(api_origen,token_origen,namespace_alma_dev,micro)
        yaml_svc_created = componer_svc(yaml_svc)
        http_code = create_service(yaml_svc_created,api_url,token,micro)
        if http_code in (200,201):
            print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el service o svc %s"%(namespace_alma_dev,api_url,micro))   
    if status["status_dc"] == 0:
        """No existe el deployment config"""
        print("Joven padawan, no existe dc para el micro %s por tanto se procede a crearlo."%micro)
        yaml_dc = obtener_dc(api_origen,token_origen,namespace_alma_dev,micro)
        yaml_dc_created = componer_dc(yaml_dc,micro,api_url,"0","")
        http_code = create_dc(yaml_dc_created,api_url,token)
        if http_code in (200,201):
            print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el dc %s"%(micro,api_url,micro))
    else:
        """Ya existe el micro asi que hay que reemplazar"""
        print("Joven padawan, el micro ya existe por lo que se procede a modificar")
        yml_origen = obtener_dc(api_origen,token_origen,namespace_alma_dev,micro)
        yml_destino = obtener_dc(api_url,token,namespace_alma_dev,micro)
        yaml_dc_created = componer_dc(yml_origen,micro,api_url,"1",yml_destino)
        http_code = reemplazar_dc(yaml_dc_created,api_url,token,namespace_alma_dev,micro)
        if http_code in (200,201):
            print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el service o svc %s"%(micro,api_url,micro))
    if status["status_route"] == 0:
        """No existe route"""
        print("Joven padawan, generando la ruta")
        yml_created = componer_route(micro)
        http_code = crear_route(api_url,token,namespace_alma_dev,micro,yml_created)    
        if http_code in (200,201):
            print("Joven padawan, atacando a %s en el cluster %s. Se ha creado el service o svc %s"%(micro,api_url,micro))
            
def main(dc):
    """Obteniendo información y tokenes"""
    start_time = time.time()
    openshift_clusters = config["openshift_clusters"]
    token_dev_darwin = openshift_clusters[0]["token"]
    api_dev_darwin = openshift_clusters[0]["api_url"]    
    token_dev_bks = openshift_clusters[1]["token"]
    api_dev_bks = openshift_clusters[1]["api_url"]
    token_dev_azure = openshift_clusters[2]["token"]
    api_dev_azure = openshift_clusters[2]["api_url"]
    deployment = str.lower(dc)    
    lista_dc = deployment.find(",")
    if lista_dc == -1:
        """Un solo micro"""
        cluster_dev_bks = status_cluster(api_dev_bks,token_dev_bks,namespace_alma_dev,deployment)        
        orquestador_creacion_modificacion_dc_svc(cluster_dev_bks,api_dev_bks,token_dev_bks,deployment,api_dev_darwin,token_dev_darwin)
        cluster_dev_azure = status_cluster(api_dev_azure,token_dev_azure,namespace_alma_dev,deployment)
        orquestador_creacion_modificacion_dc_svc(cluster_dev_azure,api_dev_azure,token_dev_azure,deployment,api_dev_darwin,token_dev_darwin)
    else:
        separador = ","
        subcadenas_dc = deployment.split(separador)
        contador = 0
        for i in range(len(subcadenas_dc)):
            contador += 1
            func_dc = subcadenas_dc[i]
            print("Joven padawan, has introducido más de 1 dc, pero podemos con ello")
            cluster_dev_bks = status_cluster(api_dev_bks,token_dev_bks,namespace_alma_dev,func_dc)        
            orquestador_creacion_modificacion_dc_svc(cluster_dev_bks,api_dev_bks,token_dev_bks,func_dc,api_dev_darwin,token_dev_darwin)
            cluster_dev_azure = status_cluster(api_dev_azure,token_dev_azure,namespace_alma_dev,func_dc)
            orquestador_creacion_modificacion_dc_svc(cluster_dev_azure,api_dev_azure,token_dev_azure,func_dc,api_dev_darwin,token_dev_darwin)
    print("--- %s seconds ---" % (time.time() - start_time))   

if __name__ == "__main__":
    main(sys.argv[1]) 
    #main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])    
    #uvicorn.run("server.app:app", host="0.0.0.0", port=8080, reload=True, timeout_keep_alive=300)
