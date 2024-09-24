from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import platform
from anthropic import Anthropic
import base64
import os
import threading
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# if platform == 'android':
#     from android.permissions import request_permissions, Permission
#     request_permissions([Permission.READ_EXTERNAL_STORAGE])

class ImageDescriberApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.select_button = Button(text='Select Image', size_hint_y=None, height=50)
        self.select_button.bind(on_press=self.select_image)
        self.layout.add_widget(self.select_button)
        
        self.image_widget = Image(source='', size_hint=(1, 0.7))
        self.layout.add_widget(self.image_widget)
        
        self.describe_button = Button(text='Describe Image', size_hint_y=None, height=50)
        self.describe_button.bind(on_press=self.describe_image)
        self.layout.add_widget(self.describe_button)
        
        self.description_label = Label(text='', size_hint_y=0.3, text_size=(Window.width - 20, None))
        self.layout.add_widget(self.description_label)
        
        return self.layout

    def select_image(self, instance):
        # if platform == 'android':
        #     from android.storage import primary_external_storage_path
        #     from jnius import autoclass
        #     Intent = autoclass('android.content.Intent')
        #     Uri = autoclass('android.net.Uri')
            
        #     intent = Intent(Intent.ACTION_GET_CONTENT)
        #     intent.setType("image/*")
            
        #     activity = autoclass('org.kivy.android.PythonActivity').mActivity
        #     activity.startActivityForResult(intent, 1)
            
        # elif platform == 'ios':
        #     # iOS implementation would go here
        #     pass
        # else:
            # For desktop testing
            from plyer import filechooser
            path = filechooser.open_file(title="Select Image", filters=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                self.image_widget.source = path[0]

    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 1 and result_code == -1:  # RESULT_OK
            uri = intent.getData()
            self.image_widget.source = uri.getPath()

    def describe_image(self, instance):
        if not self.image_widget.source:
            self.description_label.text = "Please select an image first."
            return
        
        self.description_label.text = "Analyzing image..."
        threading.Thread(target=self._get_description).start()

    def _get_description(self):
        try:
            with open(self.image_widget.source, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            message = anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                            "type": "text",
                            "text": "Describe this image, and extract all information that would help you price this book. Provide a potential Price. Just a sentence with the potential price and why. Don't add any other text.",
                            }
                        ],
                    }
                ]
            )
            
            description = message.content[0].text
            self.description_label.text = description
        except Exception as e:
            self.description_label.text = f"Error: {str(e)}"

if __name__ == '__main__':
    ImageDescriberApp().run()