from kivy.resources import resource_add_path, resource_find
import sys,os
import cv2
import face_recognition
import pyrebase
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
enc = None

firebaseConf = {
    '''Enter your firebase credentials'''
    }
firebase = pyrebase.initialize_app(firebaseConf)
database = firebase.database()

class Popup_Window(Popup):
    message = ObjectProperty(None)

class Profile_Button(BoxLayout, Button):
    label_1 = StringProperty()
    label_2 = StringProperty()
    id = StringProperty()

class Registration_Screen(Screen):
    employee_name = ObjectProperty(None)
    employee_id = ObjectProperty(None)
    gender_male = ObjectProperty(None)
    gender_female = ObjectProperty(None)
    address = ObjectProperty(None)
    phone_no = ObjectProperty(None)
    email = ObjectProperty(None)
    designation = ObjectProperty(None)
    password = ObjectProperty(None)
    confirm_password = ObjectProperty(None)

    def send_data_to_db(self):
        self.pop = Popup_Window()
        self.imgSelec = ImageSelection()

        if (self.employee_name.text == '' or self.employee_id.text == '' or self.address.text == '' or
                self.phone_no.text == '' or self.email.text == '' or self.password.text == '' or
                self.confirm_password.text == '' or (
                        self.gender_male.active == False and self.gender_female.active == False)):
            self.pop.message.text = 'some fields are empty please recheck all details'
            self.pop.open()

        elif (self.password.text != self.confirm_password.text):
            self.pop.message.text = 'password and confirm password are not same please re-enter'
            self.pop.open()
            self.password.text = ''
            self.confirm_password.text = ''

        elif (enc == None):
            self.pop.message.text = "You Haven't Entered Facial Credentials\nPlease Press 'Add Face' Button"
            self.pop.open()

        else:
            gender = 'male' if (self.gender_male.active == True) else 'female'
            temp_id = self.employee_id.text
            temp_name = self.employee_name.text

            employeeDetails ={'name': self.employee_name.text, 'gender': gender, 'address': self.address.text,
                                 'phone no': self.phone_no.text, 'email': self.email.text,
                                'designation': self.designation.text, 'password': self.password.text}
            database.child('Employee').child(self.employee_id.text).set(employeeDetails)
            database.child('Face Encoding').child(self.employee_id.text).set({self.employee_id.text:enc})

            self.pop.message.text = 'Profile is Successfully created'
            self.pop.open()

            self.employee_name.text = ''
            self.employee_id.text = ''
            self.address.text = ''
            self.phone_no.text = ''
            self.email.text = ''
            self.designation.text = 'select your designation'
            self.password.text = ''
            self.confirm_password.text = ''

            currently_created_profile = Profile_Button(label_1=('Id - ' + temp_id), label_2=('Name - ' + temp_name),id= temp_id)
        
            self.parent.parent.parent.ids.dataBase_screen.profiles_in_boxlayout.add_widget(currently_created_profile)
            currently_created_profile.bind(on_release=self.switch_to_profile)

    def switch_to_profile(self, instance):
        instance.parent.parent.parent.parent.parent.parent.ids.screen_manager_2.current = 'profile_screen'
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.name.text = database.child('Employee').child(instance.id).get().val().get('name')
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.gender.text = database.child('Employee').child(instance.id).get().val().get('gender')
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.designation.text = database.child('Employee').child(instance.id).get().val().get('designation')
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.contact_no.text = database.child('Employee').child(instance.id).get().val().get('phone no')
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.email.text = database.child('Employee').child(instance.id).get().val().get('email')
        instance.parent.parent.parent.parent.parent.parent.ids.profile_screen.ids.address.text = database.child('Employee').child(instance.id).get().val().get('address')

class ImageSelection(Screen):
    imageChooser = ObjectProperty(None)
    # EncodeingList = []

    def encodeImage(self):
        self.pop = Popup_Window()
        self.regScr = Registration_Screen()
        try:
            readImage = cv2.imread(self.imageChooser.selection[0])
            faceLocation = face_recognition.face_locations(readImage)

            if (faceLocation == []):
                self.pop.message.text = 'Cannot Locate Face\n Please Choose A Image With Frontal Profile'
                self.pop.open()
            else:
                faceEncoding = face_recognition.face_encodings(readImage, faceLocation)[0]
                # self.EncodeingList.append(faceEncoding.tolist())
                global enc
                enc = faceEncoding.tolist()
                self.pop.message.text = 'Your Facial Credentials Are Successfully Recorded \nGo On and Submit the Form'
                self.pop.open()
                self.parent.parent.parent.ids.screen_manager_2.current = 'empty_screen'
        except:
            pass

class Box(BoxLayout):
    pass

class DataBase_Screen(Screen):
    profiles_in_boxlayout = ObjectProperty(None)

class MainApp(App):
    box = Box()
    whole_data = database.child('Employee').get().val()

    def build(self):
        Window.maximize()
        return Box()

    def on_start(self):
        try:
            if not os.path.exists('Images'):
                os.makedirs('Images')

        except:
            pass

        try:
            for key, value in self.whole_data.items():
                button =Profile_Button(label_1 = ('Id - ' + key), label_2 = ('Name - ' + value.get('name')), id = str(key))
                self.root.ids.dataBase_screen.profiles_in_boxlayout.add_widget(button)
                button.bind(on_release=self.switch_to_profile)
        except:
            pass

    def switch_to_profile(self, instance):
        self.root.ids.screen_manager_2.current = 'profile_screen'
        self.root.ids.profile_screen.ids.name.text = database.child('Employee').child(instance.id).get().val().get('name')
        self.root.ids.profile_screen.ids.gender.text = database.child('Employee').child(instance.id).get().val().get('gender')
        self.root.ids.profile_screen.ids.designation.text = database.child('Employee').child(instance.id).get().val().get('designation')
        self.root.ids.profile_screen.ids.contact_no.text = database.child('Employee').child(instance.id).get().val().get('phone no')
        self.root.ids.profile_screen.ids.email.text = database.child('Employee').child(instance.id).get().val().get('email')
        self.root.ids.profile_screen.ids.address.text = database.child('Employee').child(instance.id).get().val().get('address')

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
