import os
from datetime import date
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase

from kivymd.uix.list import OneLineIconListItem, TwoLineIconListItem,ThreeLineIconListItem,MDList,IconLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFlatButton 
from kivymd.uix.dialog import MDDialog
from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import  StringProperty, NumericProperty, BooleanProperty, ListProperty

from kivymd.toast import toast
from kivy.animation import Animation
from kivy.graphics.texture import Texture

from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField	
from kivy.utils import platform

from backend import RegisterUser, Report, ReportActivity, EmergencyAgencies
from db import Database
import time


class MyTab(FloatLayout, MDTabsBase):
	''' A Tab class that inherits from MDTabsBase. '''
	pass
	
	
class SecurityAgencyList(ThreeLineIconListItem):
	''' A list item, used for selecting what security agency in the agencies tab.  '''
	icon = StringProperty()
	
	
class SettingsList(TwoLineIconListItem):
	''' A list item, used for selecting what settings to change in the settings tab.  '''
	icon = StringProperty()

class ReportsListItem(TwoLineIconListItem):
	''' A list item, used for selecting s in the home screen.  '''
	id = NumericProperty()
	reporterName = StringProperty()
	reporterContact = StringProperty()
	incidentLocation = StringProperty()
	incidentDetails = StringProperty()
	imagesPath = ListProperty()
	resolved= BooleanProperty()
	
	
class MyTheme(OneLineIconListItem):
	''' handles most of the operations involved with changing the app's theme '''
	divider = None
	dialog = None
	# a class method is always attached to a class with the first argument as the class itself.
	@classmethod
	def show_theme_dialog(self):
		#self.dialog = None
		if not self.dialog: 
			self.dialog = MDDialog( title="App theme", type="confirmation", auto_dismiss=True, 
			items=[
				MyTheme(text="Luna"),
				MyTheme(text="Callisto"), 
				MyTheme(text="Night"), 
				MyTheme(text="Solo"), 
				MyTheme(text="Phobos"), 
				MyTheme(text="Diamond"), 
				MyTheme(text="Sirena"), 
				MyTheme(text="Red music"), 
				MyTheme(text="Allergio"), 
				MyTheme(text="Magic"), 
				MyTheme(text="Tic-tac"),], 
				#buttons=[
				#MDFlatButton( text="CANCEL", on_release= revert_theme(), theme_text_color="Custom", text_color=self.theme_cls.primary_color,),
				#MDFlatButton( text="OK", on_release=save_theme(), theme_text_color="Custom", text_color=self.theme_cls.primary_color,),],
				)
			self.dialog.open()
		else:
			self.dialog.open()
	# handle check in dialog box
	def set_theme_dialog_icon(self, instance_check, current_theme_name): 
		instance_check.active = True
		#print(current_theme_name)
		# set theme
		MainApp.set_theme(current_theme_name)
		#print(dir(self.dialog))
		self.dialog.dismiss()
		check_list = instance_check.get_widgets(instance_check.group)
		for check in check_list: 
			if check != instance_check: 
				check.active = False
				

class ReportsUI(OneLineIconListItem):
	''' handles most of the operations that are involved when creating a new '''
	
	@classmethod
	def on_created_clean_data(self):
		MainApp.get_running_app().root.ids.create_reports_name_field.text  = ""		
		MainApp.get_running_app().root.ids.create_reports_contact_field.text  = ""
		MainApp.get_running_app().root.ids.create_reports_location_field.text  = ""
		MainApp.get_running_app().root.ids.create_reports_details_field.text =""		
		MainApp.get_running_app().root.ids.create_reports_image_desc_field.hint_text =""
				
		
	@classmethod
	def generate_new_report(self):
		# MAIN.py: clean text and cards in create  fields if successful
		# Store the 's input data 
		name = MainApp.get_running_app().root.ids.create_reports_name_field.text
		contact = MainApp.get_running_app().root.ids.create_reports_contact_field.text
		
		location = MainApp.get_running_app().root.ids.create_reports_location_field.text #icon
		details = MainApp.get_running_app().root.ids.create_reports_details_field.text
		images = MainApp.get_running_app().image_file_paths
		backend = MainApp.get_running_app()._backend
		# verify the input data
		is_clean, message = backend.verify_new_report(name, contact, location, details, images)
		if not is_clean:
			toast(message)
			return
		backend.create_a_new_report(name, contact, location, details, images)
		# clean input data from UI
		self.on_created_clean_data()
		
	@classmethod
	def refresh_all_home_reports(self):
		MainApp.get_running_app()._backend.get_all_reports()
		home_parent = MainApp.get_running_app().root.ids.admin_reports_box
		history_parent = MainApp.get_running_app().root.ids.admin_history_box
		for list_item in home_parent.children:
			if list_item.name == "hidden_list_item":
				continue
			home_parent.remove_widget(list_item)
		for list_item in history_parent.children:
			if list_item.name == "hidden_list_item":
				continue
			history_parent.remove_widget(list_item)
		MainApp.get_running_app()._frontend.generate_all_home_reports()
		
								
	@classmethod
	def generate_all_home_reports(self):
		''' generate's or updates the VoteLiveResultCard UI for each candidate in a report '''
		home_parent = MainApp.get_running_app().root.ids.admin_reports_box
		history_parent = MainApp.get_running_app().root.ids.admin_history_box
		
		if  not len(home_parent.children) > 50:
			for _report in MainApp.get_running_app()._backend.ongoing_reports:
				home_parent.add_widget(ReportsListItem(reporterName = str(_report["name"]), reporterContact = str(_report["contact"]),
				incidentLocation = _report["incident_location"], id = int(_report["id"]), incidentDetails = _report["incident_details"], resolved = _report["resolved"]), index = 0 )
		if  not len(history_parent.children) > 50:
			for _report in MainApp.get_running_app()._backend.ended_reports:
				history_parent.add_widget(ReportsListItem(reporterName = str(_report["name"]), reporterContact = str(_report["contact"]), 
				incidentLocation = _report["incident_location"], id = _report["id"], incidentDetails = _report["incident_details"], resolved = _report["resolved"]), index = 0)
						
	@classmethod
	def generate_new_home_reports(self):
		home_parent = MainApp.get_running_app().root.ids.admin_reports_box
		history_parent = MainApp.get_running_app().root.ids.admin_history_box
		backend = MainApp.get_running_app()._backend
		length_difference = abs(MainApp.get_running_app().database.get_reports_length() - (len(backend.ongoing_reports) + len(backend.ended_reports)))
		new_reports = backend.ongoing_reports[ length_difference : ]
		for _report in new_reports:
			if _report["resolved"]:
					history_parent.add_widget(ReportsListItem(reporterName = str(_report["name"]), reporterContact = str(_report["contact"]),
					incidentLocation = _report["incident_location"], id = int(_report["id"]), incidentDetails = _report["incident_details"], resolved = _report["resolved"]), index = 0 )
			else:
				print("called generate_new_home_reports for {str(_report['name'])} ")
				home_parent.add_widget(ReportsListItem(reporterName = str(_report["name"]), reporterContact = str(_report["contact"]),
					incidentLocation = _report["incident_location"], id = int(_report["id"]), incidentDetails = _report["incident_details"], resolved = _report["resolved"]), index = 0 )


	

	
		

class RegisterVoter(OneLineIconListItem):
	''' handles most of the UI operations that are involved when creating a user'''
	@classmethod
	def show_or_hide_password(self, widget_index):
		''' show's or hides the text for the Password TextField UIs' '''
		if widget_index == 0:
			login_password_field = MainApp.get_running_app().root.ids.pwd_field_login
			# switches pwd_visiblity to False, if True and vice versa.
			login_password_field.password = not login_password_field.password
		elif widget_index == 1:
			signup_password_field = MainApp.get_running_app().root.ids.pwd_field
			signup_password_field.password = not signup_password_field.password
		elif widget_index == 2:
			current_password_field = MainApp.get_running_app().root.ids.c_pwd_field
			current_password_field.password = not current_password_field.password
	@classmethod
	def send_otp (self):
		temp_email = str(MainApp.get_running_app().root.ids.email_field.text)
		temp_password = str(MainApp.get_running_app().root.ids.pwd_field.text)
		temp_current_password = str(MainApp.get_running_app().root.ids.c_pwd_field.text)
		
		if RegisterUser.is_email_valid(temp_email) and RegisterUser.is_password_valid(temp_password, temp_current_password):
			if temp_email in MainApp.get_running_app().existing_emails or MainApp.get_running_app().database.does_email_exist(temp_email):
				toast("Account With Email Already Exists.")
				if temp_email not in MainApp.get_running_app().existing_emails:
					MainApp.get_running_app().existing_emails.append(temp_email)
				return
			MainApp.get_running_app().email = temp_email
			MainApp.get_running_app().password = temp_password
			MainApp.get_running_app().root.ids.signup_slide.load_next(mode='next')			
			"""
			if MainApp.get_running_app().generated_otp == "202023":
				MainApp.get_running_app().generated_otp = str(random.randint(100000, 999999))
				MainApp.get_running_app().root.ids.otp_display.text = "The OTP is " + MainApp.get_running_app().generated_otp
			"""
			toast("Confirm Admin Pin.")
			MainApp.get_running_app().start_signup_timer = True
		else:
			if not RegisterUser.is_email_valid(temp_email):
				toast("Invalid Email.")
			elif not RegisterUser.is_password_valid(temp_password, temp_current_password):
				toast("Password should be at least 6 characters and equal.")

	@classmethod
	def verify_otp(self):
		otp = str(MainApp.get_running_app().root.ids.otp_field.text)
		if otp == MainApp.get_running_app().generated_otp :
			#self.root.ids.toolbar_biometric_screen.title = "Face Verification"
			self.login_voter(is_login = False)
			#MainApp.change_screen(MainApp.get_running_app(), "admin_reports_screen")
		else:
			toast("Invalid Admin Pin.")
	@classmethod
	def login_voter(self, is_login):
		if is_login:
			temp_email = str(MainApp.get_running_app().root.ids.email_field_login.text)
			temp_password = str(MainApp.get_running_app().root.ids.pwd_field_login.text)
		else:
			temp_email = str(MainApp.get_running_app().root.ids.email_field.text)
			temp_password = str(MainApp.get_running_app().root.ids.pwd_field.text)
			
		if RegisterUser.is_email_valid(temp_email) and RegisterUser.is_password_valid(temp_password, temp_password):
			MainApp.get_running_app().email = temp_email
			MainApp.get_running_app().password = temp_password
			MainApp.get_running_app().database.create_token_file(temp_email, temp_password, is_login)
		else:
			if not RegisterUser.is_email_valid(temp_email):
				toast("Invalid Email.")
			elif not RegisterUser.is_password_valid(temp_password, temp_password):
				toast("Password should be at least 6 characters.")
	@classmethod
	def send_reset_password(self):
		temp_email = str(MainApp.get_running_app().root.ids.reset_password_field.text)		
		if not RegisterUser.is_email_valid(temp_email):
			toast("Invalid Email.")
			return
		if not MainApp.get_running_app().database.does_email_exist(temp_email):
			toast("Account With Email Does Not Exist.")
			return 
		MainApp.get_running_app().database.reset_password(temp_email)
		toast("Password Reset Has Been Sent to Email.")
			
			
			

# This needs to be here to display the  images on Android
#os.environ['KIVY_IMAGE'] = 'pil,sdl2'


class FileActivity():
	""" Handles File Manager operations """
	def __init__(self, **kwargs): 
		super().__init__(**kwargs) 
		Window.bind(on_keyboard=self.events) 
		self.manager_open = False 
		self.file_manager = MDFileManager( 
								exit_manager=self.exit_manager, 
								preview = False,
								selector = "multi",
								ext=[".png", ".jpg", ".jpeg"],
								select_path=self.select_path)
		
								
	def file_manager_open(self):
		#self.file_manager.show(os.getcwd())
		if platform == 'android':
		  from android.storage import primary_external_storage_path
		  primary_ext_storage = primary_external_storage_path()		  
		  
		  from android.permissions import request_permissions, Permission
		  request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
		  
		  self.file_manager.show(primary_ext_storage)
		else :
			self.file_manager.show(os.path.expanduser("~")) 
		#self.file_manager.show_disks()
		# output manager to the screen 
		self.manager_open = True
		
	def file_manager_refresh(self):
		MainApp.get_running_app().image_file_paths = []
		MainApp.get_running_app().root.ids.create_reports_image_desc_field.hint_text = "Images: None. "
		
	def select_path(self, path):
		'''It will be called when you click on the file name or the catalog selection button.
		:param path: path to the selected directory or file; 
		'''
		self.exit_manager() 
				
		singular = " File"
		if len(self.file_manager.selection) > 1:
			singular = singular + "s"
		
		for file in self.file_manager.selection:
			MainApp.get_running_app().image_file_paths.append(file)		
		total_size = 0
		total_length = len (MainApp.get_running_app().image_file_paths)		
		for path in MainApp.get_running_app().image_file_paths:
			print(type(path))
			size = os.path.getsize(path)
			# Convert size from bytes to megabytes
			total_size += (size / (1024 * 1024))			
		MainApp.get_running_app().root.ids.create_reports_image_desc_field.hint_text = f"{total_length} {singular} selected, {total_size:.2f}mb selected. "
		toast( str(len (self.file_manager.selection)) + singular + " Selected")
		
	def exit_manager(self, *args): 
		'''Called when the user reaches the root of the directory tree.'''
		self.manager_open = False 
		self.file_manager.close()
	
	def events(self, instance, keyboard, keycode, text, modifiers): 
		'''Called when buttons are pressed on the mobile device.'''
		if keyboard in (1001, 27): 
			if self.manager_open: self.file_manager.back()
		return True
		
						
										
														
																		
																										
class MainApp(MDApp):
	''' The Main App class handles many diverse in-app operations '''
	__version__ = "0.1"
	update_count = 0
	first_login_session = True
	start_signup_timer =  False
	generated_otp = "202023"
	otp_timer = 59
	database = None
	_frontend =None
	_backend = None
	email = None
	password = None
	existing_emails = []
	filemanager = None
	image_file_paths = []
	dialog = None
	current_report = None
	theme_color_palette = {
				"Luna":  ["BlueGray", "LightBlue" ],
				"Night":  ["DeepPurple", "Purple" ],
				"Solo":  ["Gray", "BlueGray" ],
				"Phobos" :  ["Green", "Lime" ],
				"Diamond" :  ["LightGreen", "BlueGray" ],
				"Sirena":  ["Pink", "DeepPurple" ],
				"Callisto":  ["BlueGray", "Amber" ],
				"Red music":  ["Red", "DeepOrange" ],
				"Allergio": ["Teal", "Cyan" ],
				"Magic":  ["LightBlue", "Cyan" ],
				"Tic-tac": ["Brown", "Orange" ]
				}
	text_theme_style_color = None
	
	def build(self):
		return Builder.load_file("styling.kv")
		
	def on_start(self):
		self.set_theme( "Luna")
		# use Clock to schedule a method  that runs every second.
		#self.current_i = 0
		Clock.schedule_interval(self.update, 1)
		self.database = Database()
		self._backend =ReportActivity(self.database)
		self.filemanager = FileActivity()
		self._frontend = ReportsUI()
				    
	def on_resume(self):
		if self.email is not None:
			self.database.create_token_file()
		
			
	def update(self, *args):
		''' this method is called every second '''
		#Clock.unschedule(self.update) #to stop 
		#print(self.root.ids.screen_manager.current)
		self.update_count += 1
		#print("update called: " + str(self.update_count) + " times.")
		if self.first_login_session and self.database.user_id != '':
			self._backend.get_all_reports()
			self.first_login_session = False
			self._frontend.generate_all_home_reports()
		elif len(self.database.screen.queue_screen) >= 1:
			self.change_screen(str(self.database.screen.queue_screen[0]))
			self.database.screen.clean_first()
		elif len(self.database.call_back.message) >= 1:
			toast(self.database.call_back.message[0])
			self.database.call_back.clean_first()
		elif self.start_signup_timer:
			self.otp_timer -= 1
			if self.otp_timer <= 2:
				self.start_signup_timer =  False
			self.root.ids.otp_timer.text = "0:" + str(self.otp_timer)
			
		if self.update_count % 10 ==0:
			self.late_update()
			
	def late_update(self): 
		''' this method is called every 10 seconds '''
		print("late update called: " + str(self.update_count //10) + " times.")		
		#print(f" ONGOING: \n {self._backend.ongoing_reports}")
		#print(f" ENDED : \n {self._backend.ended_reports}")		 		
		if self.database.user_id != "" and self._backend.get_reports_callback():
		 	self._frontend.generate_new_home_reports()
		 	
		

	def change_screen(self, screen_name, curr = None):
		self.root.ids.screen_manager.current = screen_name
		if curr is not None:
			self.root.ids.screen_manager.transition.direction = 'right'
		else:
			self.root.ids.screen_manager.transition.direction = 'left'
		
				
	def on_tab_switch( self, instance_tabs, instance_tab, instance_tab_label):
		# called when the settings tab in navigation drawer is clicked.
		#print(dir(instance_tab))
		#print(instance_tab.text)		
		if (instance_tab.name == "security-agencies"):
			if (len(self.root.ids.agency_content_box.children) > 1):
				return
			agencies =  EmergencyAgencies.nigerian_emergency_agencies
			for agency in agencies:
					self.root.ids.agency_content_box.add_widget(SecurityAgencyList(icon = agencies[agency][2],
					text = agency,
					secondary_text = agencies[agency][0],
					tertiary_text = agencies[agency][1]
					))
	
		elif (instance_tab.name == "options"):
			if (len(self.root.ids.settings_md_list.children) > 1):
				return
			settings_icons_item = {
			    "flash-auto": "Switch Theme",
	            "brush": "Color",
	            "exit-to-app": "Exit App"
			}
			settings_icons_item_secondary_text = {
				"flash-auto": "The light, so bright.",
	            "brush": "If you could say it all in words, there would be no reason to paint",
	            "exit-to-app": "It is so hard to leave, until you leave "
	       	 }
			for list_item in settings_icons_item.keys():
				self.root.ids.settings_md_list.add_widget(
	                SettingsList(icon=list_item,
	                             text=settings_icons_item[list_item],
	                             secondary_text=settings_icons_item_secondary_text[list_item]
	                             )
	            )
	            
	 #Handles a list of objects in the settings tab.
	def set_settings(self, setting_name):
		if setting_name == "Switch Theme":
			if self.theme_cls.theme_style == "Light":
				self.theme_cls.theme_style = "Dark"
			else:
				self.theme_cls.theme_style = "Light"
		elif setting_name == "Color":
			MyTheme.show_theme_dialog()
		elif setting_name == "Exit App":
			self.stop() # closing application
			
	
	
	#Handles some arbituary system actions.
	def handle_action(self, action_name, action_variable=None):
		if action_name == "RegisterUser":
			RegisterVoter.send_otp()
		elif action_name == "CheckOTP":
			RegisterVoter.verify_otp()
		elif action_name == "ResetPassword": 
			RegisterVoter.send_reset_password()
		elif action_name == "LoginUser":
			RegisterVoter.login_voter(is_login =action_variable)
		elif action_name == "FinishBiometric":
			# send email and password to database, and then go to home_screen.
			RegisterVoter.login_voter(False)
			# send face image to database.
		
			
			
	#Handles some arbituary UI actions.
	def handle_UI_action(self, action_name, action_variable=None): 
		if action_name == "Delete Card Candidate":
			pass
		elif action_name == "View Close-Report-Dialog":
			pass
		elif action_name == "Generate New-Report":
			self._frontend.generate_new_report()
			#self._frontend.place_holder_generate__live_results_card()
		elif action_name == "Return SignUp-Carousel":
			self.root.ids.signup_slide.load_previous()
		elif action_name == "Switch Password":
			RegisterVoter.show_or_hide_password(action_variable)
		elif action_name == "Open Admin-Login-Screen":
			if self.database.user_id != '' :
				self.change_screen("admin_reports_screen")
		elif action_name == "Leave Admin-Login-Screen":
			self.change_screen("home_screen", "back")
			self.root.ids.bottom_nav_panel.switch_tab("main-report")
			
			
				
			
	def set_report_screen(self, report ):
		self.change_screen("admin_view_report_screen")
		self.root.ids.admin_view_name.text = report.reporterName
		self.root.ids.admin_view_contact.text = report.reporterContact
		self.root.ids.admin_view_location.text = report.incidentLocation
		self.root.ids.admin_view_details.text = report.incidentDetails
		self.root.ids.toolbar_admin_view_report_screen.title = f"Report #{report.id + 1}."
		self.current_report = report
		if report.resolved :
			pass
		

	def show_end_report_dialog(self, is_dialog=True):
		def on_accept(instance=None):
			for _report in self._backend.ongoing_reports:
				if int(_report["id"]) == self.current_report.id:
					if _report["resolved"]:
						self.dialog.dismiss(force=True)
						toast("This Report Has Already Been Closed")
						return
					_report["resolved"] = True
					#print (_report)
					self._backend.update_report(_report)
					self._frontend.refresh_all_home_reports()
					self.dialog.dismiss(force=True)
		def on_cancel(instance=None):
			self.dialog.dismiss(force=True)
						
		if is_dialog:
			self.dialog = MDDialog( title="Close this report?", text="Accept to mark this report as resolved and close this report.", buttons=[
			MDFlatButton( text="CANCEL", theme_text_color="Custom", text_color=self.theme_cls.primary_color, on_press = on_cancel ),
			MDFlatButton( text="ACCEPT", theme_text_color="Custom", text_color = self.theme_cls.primary_color, on_press = on_accept), ],
			)
			self.dialog.open()
		
			
	
	def show_agency_dialog(self, text, text1, text2):
			self.dialog = MDDialog( title=text, type="custom",
			content_cls=MDBoxLayout(
			MDLabel(text = text1, theme_text_color = "Custom" , text_color = self.theme_cls.accent_color,
					            font_style = 'Button', font_size = 40, pos_hint = {"center_x": .5}),
					            
			MDLabel(text = text2, theme_text_color = "Custom" , text_color = self.theme_cls.opposite_bg_dark,
					            font_style = 'Button', font_size = 40, pos_hint = {"center_x": .5}), orientation = "vertical", spacing="10dp", size_hint_y=None, height="120dp",),)
			self.dialog.open()
			
	
	# change the app's theme.
	# a class method is always attached to a class with the first argument as the class itself.
	@classmethod
	def set_theme(self, theme_name):
		#print(dir(self.get_running_app().theme_cls))
		self.get_running_app().theme_cls.theme_style_switch_animation = True
		self.get_running_app().theme_cls.theme_style_switch_animation_duration = 0.8
		self.get_running_app().theme_cls.primary_palette = self.theme_color_palette[theme_name] [0]
		self.get_running_app().theme_cls.accent_palette = self.theme_color_palette[theme_name] [1]
	
	

if __name__ == '__main__':
	MainApp().run()