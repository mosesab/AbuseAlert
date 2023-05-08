"""
 fileName : backend.py
 Author: Moses Bankole
 Run main.py to view the GUI
 Use the requirements.txt file to install the required dependencies.
 """
 # RegisterUser imports
import re #regex - regular expression

import os

class RegisterUser(object):
	""" contains private and public methods for adding user to database """
	@classmethod
	def is_email_valid(self, email):
		""" checks if email is valid """
		# regular expression pattern for email validation
		pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		# check if the email matches the pattern
		if re.match(pattern, email):
		    return True
		return False
	@classmethod
	def is_password_valid(self, password, confirm_password):
		""" checks if password is valid, and if pwd is equal to c_pwd """
		if len(password) > 5 and password == confirm_password:
			return True
		return False
	@classmethod
	def is_valid_nigerian_phone_no(self, phone_number):		
		# Remove any non-digit characters from the phone number
		phone_number = re.sub(r'[^0-9]', '', phone_number)
		phone_number = phone_number.replace(" ", "")
		if len(phone_number) < 10 :
			return False
		# Check if the first digit is 0 or +234
		if phone_number[:3] == '234' :
			phone_number = phone_number[3:]
		if not phone_number[0] == '0' :
			phone_number = "0" + phone_number
		if len(phone_number) == 11 :
				return True
		# If none of the above conditions are met, return False
		return False

	


class Report(object):
    name = None # the name of the reporter
    contact = None  # the email or phone number of the reporter
    incident_location = None # incident location
    incident_details = None # incident details
    incident_images = None # A list of eye-witness images of the incident
    resolved = None # is this report ongoing or ended
    id = None # id is set and used by database to identify reports
    
    def __init__(self, name, contact, incident_location, incident_details, incident_images=None, id=None):
        self.name = name
        self.contact = contact
        self.incident_location = incident_location
        self.incident_details = incident_details
        self.incident_images = incident_images
        self.resolved = False
        
    

	



class ReportActivity(object):
	# Load from existing pickle database, create if unable to load
	database = None
	# is true, when the app user has made memory breaking changes and the app is refreshing.
	refreshing = False
	# List of ongoing reports. One per room
	ongoing_reports = []
	# List of ended reports. Only stores one per room
	ended_reports = []
	
    # init method or constructor
	def __init__(self, db):
		self.database = db
		self.ongoing_reports = []
		self.ended_reports = []
		
	def _start_new_ongoing_report(self, report):
	    self.ongoing_reports.append(report)
		    
	def _end_ongoing_report(self, report):
	    self.ended_reports.append(report)
	    
	    if report in self.ongoing_reports:
	    	self.ongoing_reports.remove(report)
	    	# switch report from home to history frontend
	    	    
	def _is_new_reports(self):
		# if memory is empty, is refreshing, return False
		if  self.refreshing:
			return False
		database_length = self.database.get_reports_length()
		
		if database_length > (len(self.ongoing_reports) + len(self.ended_reports)):
			return True
		return False
    	  					    
	def create_a_new_report(self, name, contact, incident_location, incident_details, incident_images):
	    # Create a Report object
	    new_report = Report(
				name = name,
				contact = contact,
				incident_location = incident_location,
				incident_details = incident_details,
				incident_images = incident_images
			)
	    # Update database
	    self.database.add_report_to_database(new_report)
	    
	def update_report(self, report):
	    # Update database report
	    self.database.update_report_in_database(report)
	    
	
	    
	# usually called once on login and on refresh_all_home_reports, gets all reports from database
	def get_all_reports(self):
		    self.refreshing = True
		    # empty memory
		    self.ongoing_reports , self.ended_reports = [] , []
		    # get ongoing_reports from database, if any 
		    ongoing_reports , ended_reports = self.database.get_all_reports()
		    for report in ongoing_reports:
		    	self._start_new_ongoing_report(report)
		    ongoing_reports = None
		    for report in ended_reports:
		    	self._end_ongoing_report(report)
		    ended_reports = None
		    self.refreshing = False
	    
	# Gets new ongoing and new ended reports
	def get_reports_callback(self):
	    # get ongoing_reports from database, if any
	    if not self._is_new_reports():
	    	return False
	    length_difference = abs(self.database.get_reports_length() - (len(self.ongoing_reports) + len(self.ended_reports)))
	    new_ongoing_reports = self.database.get_new_reports(length_difference)
	    for new_report in new_ongoing_reports:
	    	self._start_new_ongoing_report(new_report)
	    return  True
	
	
	def verify_new_report(self, name, contact, incident_location, incident_details, incident_images):
		error = ""
	 	# Check name, contact, location, details, images.
		if len(name) > 50 :
			error += "Your Name should not be greater than 50."
			return False , error
		elif not len(name) > 2 :
			error += "Your Name is too short."
			return False , error
		elif not RegisterUser.is_email_valid(contact) or RegisterUser.is_valid_nigerian_phone_no(contact):
				error += "Your Contact Info is not a valid email or a valid nigerian phone number."
				return False , error
		elif len(incident_location) > 100:
			error += "The location should not be greater than 100."
			return False , error
		elif len(incident_location) < 3 :
			error += "The location  is too short."
			return False , error
		elif len(incident_details) > 300:
			error += "The Incident Details should not be greater than 300."
			return False , error
		elif len(incident_details) < 4:
			error += "The Incident Details is too short."
			return False , error
		elif len(incident_images) > 10:
			error += "The Incident Images should not be more than 10."
			return False , error
			
		total_size = 0
		for path in incident_images:
			if not os.path.exists(path):
				directory , image_name = os.path.split(path)
				error += f"{image_name} at {directory} is missing."
				return False , error
			else:
				size = os.path.getsize(path)
				# Convert size from bytes to megabytes
				total_size += (size / (1024 * 1024))
				
				if total_size > 5:
					error += f"Your {len(incident_images)} image files are {total_size:.2f}mb, The file limit is 5mb."
					return False , error
						
		return True , ""
    

	    
class EmergencyAgencies (object):
	nigerian_emergency_agencies = {
	    "Nigerian Police Force (NPF)": [ "+234 806 939 7227",  "Louis Edet House, Shehu Shagari Way, Central Business District, Abuja" , "police-station"  ],
	    "Department of State Services (DSS)": [ "+234 9 904 4750","Aso Drive, Asokoro, Abuja"  , "security"  ],	    
	    "National Drug Law Enforcement Agency (NDLEA)": [ "+234 803 3255 947", "No.6 Port Harcourt Crescent, Off Gimbiya Street, Area11 Garki Abuja" , "biohazard"  ],
	    "Economic and Financial Crimes Commission (EFCC)": ["+234-9-9044751", "No.5 Fomella Street, Off Adetokunbo Ademola Crescent Wuse II Abuja", "cash-marker"  ],
	    "Nigerian Immigration Service (NIS)": ["+234-1-4624200", "Nnamdi Azikiwe Airport Road Sauka Abuja" , "nature-people"  ],
	    "Nigerian Customs Service (NCS)": ["+234-9-4621597","Wuse Zone III, Abuja FCT Nigeria", "shield-home"  ],
	    "Federal Road Safety Corps (FRSC)": ["+234-8037876071","Zone RS2 Command Headquarters , Lagos - Ibadan Expressway Ojota Lagos", "car-emergency"  ],
	    "National Intelligence Agency (NIA)": ["+234-9-4603824", "Plot 243 Muhammadu Buhari Way Central Business District Abuja", "glasses"  ],
	    "Defence Intelligence Agency (DIA)": [ "+234-9-8700285", "Mogadishu Cantonment, Asokoro, Abuja" , "police-badge"  ],
	    "Nigerian Security and Civil Defence Corps (NSCDC)": [  "+234 9 290 6502","Plot 157 Abidjan Street, Wuse Zone 3, Abuja"  , "bird"  ]
	}

	







	    																																							
"""


		# Code Snippet to generate 10 reports to be added to the database for testing.
		place_holder_reports= {
			    "key1": {
			        "name": "John",
			        "contact": "john@example.com",
			        "incident_location": "Aho, Benin Ckty, Edo",
			        "resolved": False,
			        "incident_details": "The child is a suspected witch. They beat her with brooms, in church."
			    },
			    "key2": {
			        "name": "Jane",
			        "contact": "jane@example.com",
			        "incident_location": "Asokoro Abuja",
			        "resolved": True,
			        "incident_details": "Emotional Abuse, Beratings and Insults."
			    },
			    "key3": {
			        "name": "Bob",
			        "contact": "",
			        "incident_location": "Oshodi, Lagos",
			        "resolved": False,
			        "incident_details": "Physical Abuse, used stone to beat a child"
			    }
		}


		for _key in place_holder_reports:
			report = Report(
				name = place_holder_reports[_key]["name"],
				contact = place_holder_reports[_key]["contact"],
				incident_location = place_holder_reports[_key] ["incident_location"],
				incident_details = place_holder_reports[_key] ["incident_details"],				
			)
			report.resolved = place_holder_reports[_key]["resolved"]
			#incident_images = []
			
			print(f" report:  name : {report.name} , contact : {report.contact}, location : {report.incident_location}, details : {report.incident_details}, resolved : {report.resolved} ")
			self.database.add_report_to_database(report)
		return None
	
		

"""


