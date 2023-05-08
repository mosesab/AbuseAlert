
"""
Github: cloud_storage_examples/pyrebase4_example/main.py
By RobertFlatt
@RobertFlatt
"""

from kivy.utils import platform
from kivy.clock import Clock

from threading import Thread
from os.path import exists, join
from os import remove as remove_file
import json
import requests
import traceback 
if platform == 'android':
    from android.storage import app_storage_path
    
import pyrebase

"""
# A pyrebase Bug Patch: i override pyrebase quote function with function that does nothing.
# this Patch, allows me to use pyrebase order_by_child without errors occuring.
def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote
# Dedicided to patch this bug, by moving over to pyrebase4
"""



class Database(object):
    call_back = None
    screen = None
    firebase_config = None
    refresh_timer = None
    user = None
    user_id = None
    EMAIL  = None
    PASSWORD   = None  
    IS_SIGNUP_ACTION = None
    ###############################
    # init method or constructor
    ###############################  
    def __init__(self):        
		# my normal init code:
        self.call_back = ToastCallBack()
        self.screen = ScreenCallBack()
        self.user = {'idToken' : '', 'localId' : '', 'refreshToken' : ''}
        self.user_id = ''
        # Your web app's Firebase configuration
        self.firebase_config = {
      	  "apiKey" : "AIzaSyB_4bPk4bgarWZ3cUvHmFG3VJc_ZCWLcnM",
			"authDomain" : "abusealert-c7e85.firebaseapp.com",
			"projectId" : "abusealert-c7e85",
			"storageBucket" : "abusealert-c7e85.appspot.com",
			"messagingSenderId" : "131644695943",
			"appId" : "1:131644695943:web:c971de06c3e32c4cc9df22",
			"measurementId" : "G-XJR0BFWVDL",
			  "databaseURL": "https://abusealert-c7e85-default-rtdb.firebaseio.com"
			}
        self.pyre = pyrebase.initialize_app(self.firebase_config)
        
        

        
			    
	###############################
    # Connect To Databse Utilities
    ###############################
    
    def create_token_file(self, email=None, password=None, is_login=None):
        # app behavior depends on token file existance.
        # connect_to_db_without_token: start, authorized by sign in.
        # connect_to_db_with_token: resume or restart, authorized by token file.
        if exists(self.token_file_path()) and self.user['refreshToken'] != "":
            	Thread(target = self.connect_to_db_with_token, daemon = True).start()
        else:
            # tell the database if the user's intended action is a signup or login action.
            self.EMAIL = email
            self.PASSWORD = password
            self.IS_SIGNUP_ACTION = not is_login
            
            Thread(target = self.connect_to_db_without_token,
                   daemon = True).start()

    
    def connect_to_db_without_token(self):
        auth = self.pyre.auth()
        db = self.pyre.database()
        
        #print("Accessed the connect_to_db_without_token Block.")
        # if the user's intended action is a signup action
        if self.IS_SIGNUP_ACTION == True :
	        # Create user
	        #print("Accessed the IF SIGNUP Block.")
	        try:
		        response = auth.create_user_with_email_and_password(self.EMAIL, self.PASSWORD)
		        #print('"' + self.EMAIL + '" Account created.')
		        self.IS_SIGNUP_ACTION = False 
		        # load home screen
		        self.call_back.toast( "Welcome to Electora")
		        self.screen.change_screen(self.screen.home_screen)

		    # read message in HTTPError
	        except requests.HTTPError as e:
	            #traceback.#print_exc() # #printing stack trace
	            error_json = e.args[1]
	            error = json.loads(error_json)['error']['message']
	            # if account with this email already exists.
	            if error == "EMAIL_EXISTS":
	            	self.call_back.toast( "Account Already Exists.")
	            	self.screen.change_screen(self.screen.login_screen)
	            return
	        # if any other error occurs while signing up
	        except Exception as e:
	            #traceback.#print_exc() # #printing stack trace
	            self.call_back.toast( "A Database Error Occured.")
	            self.screen.change_screen(self.screen.login_screen)
	    
	    # if the user's intended action is a login action
        if self.IS_SIGNUP_ACTION == False :
	        #print("Accessed the IF LOGIN Block.")
             # LogIn user
	        try:
	            if not self.sign_in(auth, self.EMAIL , self.PASSWORD):
	                return
	            # load home screen
	            self.call_back.toast( "You've Signed In")
	            self.screen.change_screen(self.screen.home_screen)
             # read message in HTTPError
	        except requests.HTTPError as e:
	            #traceback.#print_exc() # #printing stack trace
	            error_json = e.args[1]
	            error = json.loads(error_json)['error']['message']
	            # if account with this email doesn't exist.
	            if error == "USER_NOT_FOUND" or error == "EMAIL_NOT_FOUND":
	            	self.call_back.toast( "No Account Found. Sign Up.")
	            elif error == "INVALID_PASSWORD":
	                self.call_back.toast( "Wrong Password.")
	            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error:
	            	self.call_back.toast( "Failed too often. Account Temporarily Disabled.")
	            return
	        # if any other error occurs while signing up
	        except Exception as e:
	            #traceback.#print_exc() # #printing stack trace
	            #print("A Database Error Occured.")
	            self.call_back.toast( "A Database Error Occured.")
	            return
       
    def connect_to_db_with_token(self):
        if not self.authorize_with_token_file():
           # Token based authorization failed.
            self.call_back.toast( "Session Expired, Log Back In")
            self.error_cleanup()
            self.screen.change_screen(self.screen.login_screen)
            return
        self.call_back.toast( "'Welcome Back.")
        self.screen.change_screen(self.screen.home_screen)
         

        
    ###############################
    # Authentication Utilities
    ###############################
	    
    def sign_in(self, auth, user, password):
        try:
	        response = auth.sign_in_with_email_and_password(user, password)
	        success = self.authorize_actions(response)
	        if not success:
	            self.call_back.toast( "Login Failed, Try Again.")
	        return success
        except requests.ConnectionError:
	        # No internet connection
	        self.call_back.toast("Server Connection Failed")
	        return False
   
    def reset_password(self, email):
    	auth = self.pyre.auth()
    	# Construct and send password reset email
    	auth.send_password_reset_email(email)
    	self.call_back.toast("Reset Password Has Been Sent")
    	
    def send_verification_email(self):
    	auth = self.pyre.auth()
    	# You can only send_verification_email after a successful login or during an active token session.
    	auth.send_email_verification(self.user_id)
    	self.call_back.toast("Email Verification Has Been Sent")
    	
    def does_email_exist(self, email, password="password"):
        # it can trigger the Firebase TOO_MANY_ATTEMPTS_TRY_LATER flag, if it's used too many times.
        try:
            #print("Does Email Exist Reached")
            auth = self.pyre.auth()
            response = auth.sign_in_with_email_and_password(email, password)
             # read message in HTTPError
        except requests.HTTPError as e:
	        ##traceback.#print_exc() # #printing stack trace
	        error_json = e.args[1]
	        error = json.loads(error_json)['error']['message']
	        # if account with this email doesn't exist.
	        if error == "USER_NOT_FOUND" or error == "EMAIL_NOT_FOUND":
	        	return False
        except requests.ConnectionError:
	        # No internet connection
	        self.call_back.toast("Server Connection Failed")
	        return False
        return True
        
    def authorize_with_token_file(self):
        refresh_token = self.read_token_file()
        auth = self.pyre.auth()
        response = auth.refresh(refresh_token)
        return self.authorize_actions(response)

    def refresh_user(self):
        auth = self.pyre.auth()
        response = auth.refresh(self.user['refreshToken'])
        self.refresh_timer = None
        success = self.authorize_actions(response)
        if not success:
            # if token failed to refresh, then try to log back in quietly.
            if not self.sign_in(auth, self.EMAIL , self.PASSWORD):
	                return

    def authorize_actions(self, response):
        fail = 'error' in response
        if self.refresh_timer:
            Clock.unschedule(self.refresh_timer)
        if fail:
            self.user = {'idToken' : '', 'localId' : '', 'refreshToken' : ''}
            self.user_id = ''
            self.delete_token_file()
            self.refresh_timer = None
        else:
            self.user = response
            if 'localId' in response:
                self.user_id = response['localId']
            elif 'userId' in response:
                self.user_id = response['userId']
            else:
                self.user_id = ''
            self.write_token_file()
            self.refresh_timer = Clock.schedule_once(self.refresh_user, 3500)
        return not fail


    ###############################
    # token file utilities
    ###############################

    def token_file_path(self):
        file_name = 'token.txt'
        if platform == 'android':
            file_path = join(app_storage_path(), file_name)
        elif platform == 'ios':
            file_path = join(getattr(self, 'user_data_dir'), file_name)
        else:
            file_path = join('./', file_name)
        return file_path

    def write_token_file(self):
        if self.user:
            with open(self.token_file_path(), 'w') as f:
                f.write(self.user['refreshToken'])

    def read_token_file(self):
        if exists(self.token_file_path()):
            with open(self.token_file_path(), 'r') as f:
                refresh_token = f.read()
            return refresh_token
        else:
            return ''

    def delete_token_file(self):
        if exists(self.token_file_path()):
            remove_file(self.token_file_path())
    def delete_user(self, id_token):
        REST_IDENTITY = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/'
        payload = json.dumps({"idToken": id_token})
        url = REST_IDENTITY + 'deleteAccount?key=' + self.firebase_config["apiKey"]
        try:
            r = requests.post(url, data=payload)
            return json.loads(r.text)
        except Exception as e:
            return {'error' : str(e)}
            
    def error_cleanup(self):
        self.delete_token_file()
        self.delete_user(self.user['idToken'])
            
    ###############################
    # report utilities
    # used by backend, for creating, reading and deleting reports in online database.
    ###############################
    def add_report_to_database(self, report):
    	try:
    		db = self.pyre.database()
	    	new_id = self.get_reports_length()
	    	new_db_report = {
	    			"id" : new_id,
					"name" : report.name,
					"contact" : report.contact,
					"incident_location" : report.incident_location,
					"resolved" : report.resolved,
					"incident_details" : report.incident_details,
	    	}
	    	db.child("Abuse Cases").child("Reports").push(new_db_report)
    	except Exception as e:
            #print(str(e))
            self.call_back.toast("Failed To Create A New report.")
            return
    	self.call_back.toast("Successfully Created a new report.")
       
    def get_all_reports(self):
    	db = self.pyre.database()
    	_ongoing_reports = []
    	_ended_reports = []
    	all_reports = list(db.child("Abuse Cases").child("Reports").get().val().items())
    	for i in range(len(all_reports)):
    		report = all_reports[i][1]
    		if not report['resolved'] :
		      	_ongoing_reports.append(report)
    		else :
		      	_ended_reports.append(report)
    	return _ongoing_reports , _ended_reports
    	              
    def get_new_reports(self, length_difference):
    	db = self.pyre.database()
    	new_reports_list = []
    	# new_reports is an ordered dict
    	new_reports = db.child("Abuse Cases").child("Reports").order_by_key().limit_to_last(length_difference).get().val()
    	new_reports = list(new_reports.items())
    	for i in range(len(new_reports)):
    		new_report = new_reports[i][1]
    		new_reports_list.append(new_report)
    	return new_reports_list
   
   
    def get_reports_length(self):
    	db = self.pyre.database()
    	# last_report_key_dict is an ordered dict
    	last_report_key_dict = db.child("Abuse Cases").child("Reports").order_by_key().limit_to_last(1).get().val()
    	if last_report_key_dict == None:
    		return 0
    	# get the first key in the dict
    	first_key = next(iter(last_report_key_dict))
    	last_report = last_report_key_dict [first_key]
    	# id starts from 0, so we add 1 to get the actual length instead of the index.
    	last_id = last_report["id"] + 1
    	return last_id
    	
    def update_report_in_database(self, report):
    	try:
    		db = self.pyre.database()
    		specific_report_key_dict = db.child("Abuse Cases").child("Reports").order_by_key().limit_to_first((int(report["id"]) + 1)).get().val()
    		for key in specific_report_key_dict:    			
    			if specific_report_key_dict[key]["id"] == report["id"]:
    				db.child("Abuse Cases").child("Reports").child(str(key)).update(report)
    				break 			
    	except Exception as e:
    		traceback.print_exc()
    		self.call_back.toast("Failed to Update Report.")
    		return
    	self.call_back.toast("Report Update Successful.")
       
			

###############################
    # Front-End  Action Utilities
    # they perform front-end tasks: like app.change_screen and toast.
###############################
    
class ToastCallBack(object):
	message = []
	def toast(self, text):
		self.message.append(text)
	def clean_first(self):
		self.message.pop(0)
		
		
class ScreenCallBack(object):
	queue_screen = []
	login_screen = "home_screen"
	home_screen = "admin_reports_screen"
	def change_screen(self, new_queue_screen):
		self.queue_screen.append(new_queue_screen)
	def clean_first(self):
		self.queue_screen.pop(0)
	
	
	
	

"""
###############################
    # Document utilities
    # for reading and writing data to online database.
    # document name is user_id
    ###############################

    def create_private_document(self, db, collection, payload):
        try:
            db.child(collection).child(self.user_id).set(payload,
                                                         self.user['idToken'])
        except Exception as e:
            #print(str(e))

    def read_private_document(self, db, collection):
        try:
            return db.child(collection).child(self.user_id).get(self.user['idToken'])
        except Exception as e:
            #print(str(e))
            return None

    def update_private_document(self, db, collection, payload):
        try:
            db.child(collection).child(self.user_id).update(payload,
                                                            self.user['idToken'])
        except Exception as e:
            #print(str(e))

    def delete_private_document(self, db, collection):
        try:
            db.child(collection).child(self.user_id).remove(self.user['idToken'])
        except Exception as e:
            #print(str(e))

    

    
###############################
    # other utilities
    ###############################

    def get_user_name(self,db):
        saved = self.read_private_document(db, 'id')
        try:
            return saved.val()['name']
        except Exception as e:
            #print(str(e))
            return 'Nameless Fool'

    

# Demonstrate CRUD operations
        #print('Demonstrate CRUD operations')
        
        # Create
        data = {'age': 20, 'location': 'lunar orbit'} 
        self.create_private_document(db, 'data', data)

        # Read
        saved = self.read_private_document(db, 'data')
        if not saved or saved.val()['age'] != 20:
            #print('Document Create and Read failed.')
            self.error_cleanup()
            return
        else:
            #print('Document Create and Read succeeded.')

        # Update
        data = {'age': 25}
        self.update_private_document(db, 'data', data)

        # Read
        saved = self.read_private_document(db, 'data')
        if not saved or saved.val()['age'] != 25:
            #print('Document Update failed.')
            self.error_cleanup()
            return
        else:
            #print('Document Update succeeded.')

        # Delete
        self.delete_private_document(db, 'data')
        result = self.read_private_document(db, 'data')
        if not result or result.val():
            #print('Document Delete failed.')
            self.error_cleanup()
            return
        else:
            #print('Document Delete succeeded.')

        #print('CRUD demonstration succeeded.\n')

        if account_created:
            # Save DEMO_NAME in the db
            #print('Save user name.\n')
            self.create_private_document(db, 'id', {'name' : DEMO_NAME})

        # Create some different data
        #print('Save some more data.\n')
        data = {'status' : {'win': 43, 'loose': 21, 'draw': 7}}
        self.create_private_document(db, 'more_data', data)

        # User instructions
        if platform == 'android':
            #print('Pause, then resume (or restart) app.')
        else:
            #print('Exit, then restart app.')


# do I remember my name?
        #print('Welcome Back "' + self.get_user_name(db) + '"')

        # what else do I remember?
        try:
            saved = self.read_private_document(db, 'more_data')
            if saved and saved.val()['status']['win'] == 43:
                #print('Success reading previous data.')
            else:
                #print('Previous data incorrect.')
                self.error_cleanup()
                return
        except Exception as e:
            #print('Error: ' + str(e))
            self.error_cleanup()
            return
        
        # Delete data and user
        self.delete_private_document(db, 'more_data')
        self.delete_private_document(db, 'id')
        self.delete_token_file()
        #print('\nDeleted demonstration data.')
        self.delete_user(self.user['idToken'])
        self.user = None
        #print('Deleted demonstration account.')
        #print('\nSUCCESS.')
        

"""
		