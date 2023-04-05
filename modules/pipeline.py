import os,subprocess, requests
import shutil
def pipeline(api_name, base_path, endpoint_url, maintenance_window, traffic_limit, flows):
      

      proxy_name = api_name
      targeturl = endpoint_url
      base_path = base_path
      ratelimit= maintenance_window
      quotalimit = traffic_limit
     
      
                
      flow = flows
      


      print(f"We are setup with proxy name {proxy_name} with given Target URL {targeturl}")
      subprocess.run(["git", "clone", "https://test:glpat-5sVjtSyaDVnn4xMHvriz@gitlab.com/abhishek.chauhan5/testme.git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      os.chdir("testme")
      os.chmod(".git", 0o777)
      for root, dirs, files in os.walk(".git"):
            for dir in dirs:
                  os.chmod(os.path.join(root, dir), 0o777)
            for file in files:
                  os.chmod(os.path.join(root, file), 0o777)
      shutil.rmtree(".git")

      os.chdir("..")

      url = "https://gitlab.com/api/v4/projects?private_token=glpat-5sVjtSyaDVnn4xMHvriz"
      data = {
        "name": proxy_name,
        "namespace_id": "54370654"
      }
      response = requests.post(url, json=data)
      if response.ok:
        # Clone new repo with proxy name
            print(f"Cloning new repo with proxy name as {proxy_name}...")

            subprocess.run(["git", "clone", f"https://test:glpat-5sVjtSyaDVnn4xMHvriz@gitlab.com/neos-trial/{proxy_name}.git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      base_path = os.getcwd()
      src_dir = f'{base_path}'+"/testme"
      dst_dir = f'{base_path}'+f"/{proxy_name}"

      allfiles = os.listdir(src_dir)
 
# iterate on all files to move them to destination folder
      for f in allfiles:
            src_path = os.path.join(src_dir, f)
            dst_path = os.path.join(dst_dir, f)
            shutil.move(src_path, dst_path)

      os.chdir(proxy_name)
      subprocess.run(["git", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      for root, dirs, files in os.walk("."):
            for file in files:
                  if file.endswith(".json") or file.endswith(".xml"):
                        with open(os.path.join(root, file), "r") as f:
                              content = f.read()
                              content = content.replace("APITemplate", proxy_name).replace("targeturl", targeturl).replace("ratelimit", ratelimit).replace("quotalimit", quotalimit)
                        with open(os.path.join(root, file), "w") as f:
                              f.write(content)

      with open("apiproxy/proxies/default.xml", "r") as f:
            content = f.read()
            content = content.replace("<Flows/>", flow)

      with open("apiproxy/proxies/default.xml", "w") as f:
            f.write(content)


# shutil.rmtree(f'{proxy_name}.xml', ignore_errors=True)

      os.rename("apiproxy/APITemplate.xml", f"apiproxy/{proxy_name}.xml")
      subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      subprocess.run(["git", "commit", "-m", "test"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      subprocess.run(["git", "config", "--global", "user.email", "abhishek.chauhan@neosalpha.com"])
      subprocess.run(["git", "config", "--global", "user.name", "abhishek.chauhan"])
      subprocess.run(["git", "push", "origin", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      if subprocess.run(["git", "push", "origin", "main"]).returncode == 0:
    # echo_green("All files are pushed. You are ready...")
            return "All files are pushed. You are ready..."
      else:
    # echo_red("There might be some issue with authorization or you are not an authorized person.")
            return "There might be some issue with authorization or you are not an authorized person."