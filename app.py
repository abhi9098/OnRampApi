from flask import Flask, render_template, request, session, redirect
import pyrebase, yaml, requests, sys, os,shutil
from openapi_spec_validator import validate_spec

base_path = os.getcwd()
sys.path.insert(0,f'{base_path}'+'/modules')

from customrules import *
from flows import *
from pipeline import *


app = Flask(__name__)
app.secret_key = 'SecretKey'

# Initialize Firebase app with configuration
config = {
  "apiKey": "AIzaSyDT3Nuui7N6jBPh_wxVSJYtun5fCh8aKfI",
  "authDomain": "test-f2904.firebaseapp.com",
  "databaseURL": "https://test-f2904-default-rtdb.firebaseio.com",
  "projectId": "test-f2904",
  "storageBucket": "test-f2904.appspot.com",
  "messagingSenderId": "173178005742",
  "appId": "1:173178005742:web:78e0237bd73fa000226bff",
  "measurementId": "G-5W5BL0TQNT"

}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()




@app.route("/")
def home():
     return render_template('home.html')

@app.route('/spec/')
def spec():
    return render_template('home1.html')


def show_data(msg = None):
    data = db.child('file_data').get().val()
    return render_template('data.html', data=data, msg =msg)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email
        try:
            prefix, postfix, http_method, regex = custom_rules()

        except Exception as e:
             return render_template('home1.html', lint_ =  f"{e}")
    
        if http_method == None:
            method_not_allowed = ""
        else:
             method_not_allowed = True
        if (prefix == None) and (postfix == None):
            add_constraints = ""
        else:
             add_constraints = True
        if regex == False:
            regex_pattern = ""
        else:
             regex_pattern = regex

        try:
            file = request.files['file']
        except KeyError:
            return render_template('home1.html', lint_='No file selected')

        if file.filename == '':
            return render_template('home1.html', lint_='No file selected')
        
        if 'file' not in request.files:
            return render_template('home1.html', lint_ ="No file selected")
        
        file = request.files['file']


# =======================================================================================
#                             STORING FILE INTO FIREBASE
# =======================================================================================
        
        if file:
            # Upload the file directly to Firebase Storage
            file_data = file.read()
            storage.child("Specs/" + file.filename).put(file_data)

            # Read the data from the uploaded file
            file_url = storage.child("Specs/" + file.filename).get_url(None)
            file_data = requests.get(file_url).text
            spec_dict = yaml.safe_load(file_data)
            session['file_link'] =file_url
            session['filename'] = file.filename
            

# ===================================================================================
#                             VALIDATING SPEC 
# ===================================================================================
            try:
                validate_spec(spec_dict)
            except Exception as e:
                return render_template('home1.html', syn='syntactical error...')

# ===================================================================================
#                             CREATING SESSIONS
# ===================================================================================           

            session['method_not_allowed'] = method_not_allowed
            session['http_method'] = http_method
            session['add_constraints'] = add_constraints
            session['prefix'] = prefix
            session['postfix'] = postfix
            session['regex_pattern'] = regex_pattern
                    

#=================================================================================== 
#                              CHECKING THE PATH METHOD
#=================================================================================== 

            try:
                  method_not_allowed = session.pop('method_not_allowed', None)
                  if method_not_allowed != None:
                    http_method = session.pop('http_method', None)
                    method = http_method
                    
                    for i in spec_dict['paths'].keys():
                            for j in spec_dict['paths'][i].keys():
                                if j == method.lower():
                                        raise Exception("Linting error(Path): Spec is not created with predefined rules... ")      
            except Exception as e:
                 return render_template('home1.html',lint_ = f"{e}")

#=================================================================================== 
#                              CHECKING THE TITLE OF SPEC
#===================================================================================
            try:
                  add_constraints = session.pop('add_constraints', None)
                  if add_constraints != None:
                    prefix = session.pop('prefix', None)
                   
                    postfix = session.pop('postfix', None)
                    
                    title_value = spec_dict['info']['title']
                    title_value = title_value.strip()
                    flag1 = title_value.startswith(prefix)
                  
                    flag2 = title_value.endswith(postfix)
                
                    
                    if   (flag1 is False) or (flag2 is False):
                            raise Exception("Linting error(Title): Spec is not created with predefined rules... ")
            except Exception as e:
                  return render_template('home1.html',lint_ = f"{e}")
            
#=================================================================================== 
#                              CHECKING STRING PATTERN CHECK 
#===================================================================================
            try:
                regex_pattern = session.pop('regex_pattern', None)
                if regex_pattern != None:       
                    count=0
                    match_list=['type','pattern']
                    for i in spec_dict['paths'].keys():                    
                        for j in spec_dict['paths'][i].keys():    
                            if 'parameters' in spec_dict['paths'][i][j].keys():
                                count = 0
                                match_list=['type','pattern']
                                for i in spec_dict['paths'].keys():
                                    for j in spec_dict['paths'][i].keys():
                                        if 'parameters' in spec_dict['paths'][i][j].keys():
                                            for k in spec_dict['paths'][i][j]['parameters'][0].keys():
                                                if (k in match_list):
                                                    count += 1
                                                    if (k == 'type') and (spec_dict['paths'][i][j]['parameters'][0][k] == 'string'):
                                                        continue
                                                    if (k == 'pattern') and (len(spec_dict['paths'][i][j]['parameters'][0][k]) != 0):
                                                        continue
                                                    else:
                                                        raise Exception("Linting error(Parameters): Spec is not created with predefined rules...")
                                if count % 2 != 0:
                                    raise Exception("Linting error(Parameters): Spec is not created with predefined rules...")
                            else:
                                raise Exception("Linting error(Parameters): 'parameters' key not found in spec...")
            except Exception as e:
                return render_template('home1.html', lint_=f"{e}")  
            
#=================================================================================== 
#                              DATA COLLECTION
#===================================================================================   
      
            title=spec_dict['info']['title']
            base_path = spec_dict.get('basePath', 'default')
            if base_path == "default":
                    base_path = "/"+title
                    base_path = base_path.lower()
            
            try:
                    information = spec_dict['info']['description']
            except KeyError:
                    information = None
            try:
                    for i in spec_dict['servers']:
                        target_url = i['url']
            except KeyError:
                    try:
                        sh=spec_dict['schemes'][0]
                        domain=spec_dict['host']
                        path=spec_dict['basePath']
                        target_url = sh+"://"+domain+path
                    except KeyError:
                        target_url = ""

            flows = {}
            if len(spec_dict['paths']) == 0:
                session['flows'] = flows
            else:
                    for path, operations in spec_dict['paths'].items():
                        paths,desc=[],[]
                        for operation, details in operations.items():
                                paths.append(operation)
                # Extract the summary and add to the result dictionary
                                summary = details.get('summary')
                                desc.append(summary)
                                if summary:
                                    flows[path] = [paths, desc]
                    session['flows'] = flows
            
            return render_template('form1.html' ,email=email,title=title,basepath=base_path,url=target_url,desc=information,flows=flows)            
                 



@app.route('/modify_data/',methods=['POST'])
def modify():
     # Access data from session object
      up_proxyname = request.form.get('proxyname')
      up_basepath  = request.form.get('basepath')
      up_description = request.form.get('description')
      up_target = request.form.get('targeturl')
      up_email = session['email']
      session['proxyname'] = up_proxyname
     
      up_filename = session['filename']
      up_filepath = session.pop('file_link', None)
      flows = session.get('flows')
      if (len(flows) != 0):
           up_flows = create_flows()
           
      else:
           up_flows = "<Flows/>"
      

      tps_allowed = request.form['tps_allowed']
      quota_allowed_count = request.form['quota_allowed_count']
      quota_allowed_interval = request.form['quota_allowed_interval']
      quota_allowed_timeunit = request.form['timeunit']
      max_tps = request.form['max_tps']
      max_quota_count = request.form['max_quota_count']
      max_quota_interval = request.form['max_quota_interval']
      max_quota_timeunit = request.form['max_timeunit']
      apikey = request.form['apikey']
      username_ba = request.form['username_ba']
      password_ba = request.form['password_ba']
      oauthurl = request.form['oauthurl']
      clinet_id = request.form['clientid']
      clinet_secret = request.form['clientsecret']

    
      updated_data={
           "email_id": up_email,
           "proxyname":up_proxyname,
           "basepath":up_basepath,
           "description":up_description,
           "targeturl":up_target,
           "tps":tps_allowed,
           "quota_count":quota_allowed_count,
           "quota_interval":quota_allowed_interval,
           "quota_timeunit":quota_allowed_timeunit,
           "max_tps":max_tps,
           "max_quota_count":max_quota_count,
           "max_quota_interval":max_quota_interval,
           "max_quota_timeunit":max_quota_timeunit,
           "apikey":apikey,
           "basicauth_username":username_ba,
           "basicauth_password":password_ba,
           "oauthurl":oauthurl,
           "clientid":clinet_id,
           "clientsecret":clinet_secret,
           "flows":up_flows,
           "filename":up_filename,
           "filepath":up_filepath,
           "isapproved":"0"
      }
      db.child('file_data').push(updated_data)
      return render_template("form1.html", msg ="Wait for Approval.")

@app.route('/admin/')
def admin():
    return render_template('login.html')

@app.route('/admin_login/', methods=['POST'])
def admin_login():
    

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "admin":
        data = db.child('file_data').get().val()
        return render_template('data.html', data=data)
    

@app.route('/approve/', methods=['POST'])
def approve_files():
   
    if request.method == 'POST':
        # Get the list of approved items from the form
        email_id = session.pop('email', None)
        proxy_title = session.pop('proxyname', None)
        file_name = session.pop('filename', None)
        approved_items = request.form.getlist('approved[]')
        
        # Update the isapproved value in Firebase for each approved item
        for item_id in approved_items:
            if (email_id == db.child('file_data').child(item_id).get().val()['email_id']) and (proxy_title == db.child('file_data').child(item_id).get().val()['proxyname']) and (file_name == db.child('file_data').child(item_id).get().val()['filename']) :
                db.child('file_data').child(item_id).update({"isapproved": 1})
                stored_data = db.child('file_data').child(item_id).get().val()
                break

        for key, value in stored_data.items():
            if key == "email_id":
                email = value
            if key == "proxyname":
                proxyname = value
                session['api_name'] = proxyname
            if key == "basepath":
                basepath = value
                session['base_path'] = basepath
            if key == "description":
                description = value
            if key == "targeturl":
                targeturl = value
                session['endpoint_url'] = targeturl
            if key == "tps":
                tps_allowed = value
                session['tps_allowed'] = tps_allowed
            if key == "quota_count":
                quota_allowed_count = value
                session['quota_allowed_count'] = quota_allowed_count
            if key == "quota_interval":
                quota_allowed_interval = value
            if key == "quota_timeunit":
                quota_allowed_timeunit = value
            if key == "max_tps":
                max_tps = value
            if key == "max_quota_count":
                max_quota_count = value
            if key == "max_quota_interval":
                max_quota_interval = value
            if key == "max_quota_timeunit":
                max_quota_timeunit = value
            if key == "apikey":
                apikey = value
            if key == "basicauth_username":
                username_ba = value
            if key == "basicauth_password":
                password_ba = value
            if key == "oauthurl":
                oauthurl = value
            if key == "clientid":
                clientid = value
            if key == "clientsecret":
                clientsecret = value
            if key == "flows":
                flows = value
                session['flows'] = flows
      
                

        # Redirect to the same page with a success message
        
    
        return render_template('alldata.html', email=email, proxyname=proxyname, basepath=basepath, description=description, targeturl=targeturl, tps=tps_allowed, quota_count=quota_allowed_count, quota_interval=quota_allowed_interval, quota_timeunit=quota_allowed_timeunit, max_tps=max_tps, max_quota_count=max_quota_count, max_quota_interval=max_quota_interval, max_quota_timeunit=max_quota_timeunit, apikey=apikey, basicauth_username=username_ba, basicauth_password=password_ba, oauthurl=oauthurl, clientid=clientid, clientsecret=clientsecret, flows=flows)

@app.route('/pipeline/',methods=['POST'])
def pipeline_flow():
    api_name = session.pop('api_name', None)
    base_path = session.pop('base_path', None)
    endpoint_url = session.pop('endpoint_url', None)
    
    maintenance_window = session.pop('tps_allowed', None)
    traffic_limit = session.pop('quota_allowed_count', None)
    flows = session.pop('flows', None)
    ans = pipeline(api_name, base_path, endpoint_url, maintenance_window, traffic_limit, flows)
    f1_path = f"{api_name}"
    
    os.chmod(".git", 0o777)
    for root, dirs, files in os.walk(".git"):
      for dir in dirs:
            os.chmod(os.path.join(root, dir), 0o777)
      for file in files:
            os.chmod(os.path.join(root, file), 0o777)
    shutil.rmtree(".git")
    os.chdir("..")
    shutil.rmtree(f1_path)
    shutil.rmtree("testme")
    session.clear()
    return ans 
  

@app.route('/admin_logout')
def admin_logout():
    # Clear the session and redirect to the login page
    session.clear()
    return render_template('home.html')



if __name__ == '__main__':
    app.run(host="localhost",port=5000,debug=True)
