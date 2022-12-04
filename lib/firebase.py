from firebase_admin import auth, initialize_app, credentials, storage, db


class Firebase:
    def __init__(self) -> None:
        creds = credentials.Certificate({
            "type": "service_account",
            "project_id": "sid-black",
            "private_key_id": "e4a940f1ccea0354d54321cabf2a5d60e83f9ef1",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCS3isSywOMoBrq\n+Ii6Z7Ep/VKNX1sgnM/LNZeK7O02Io6KibjbkkFSwBu6dJNcR0m4TAIeeh9uMHX7\nO+4m9HDAm4Q9BSbNXoeVgXIdnWcqF3KOPyytkGGPGicca4EJ9bnr+jpuaY1KknMu\n4+LuBYOOBBBrDRXWUXK4oXCxcMcqPPJ2eYpDwzJ7fMN0KbwAAVf8fwuWgejcKsEY\nfEaJQ96T8GJ+Tm4Fp1RJOzZFE6+V8vZm/xqeppUVUi05pbqhDcYyOtDgjsxJZGW8\nJEiki6gvLs+hk6hbtEzij+JGpCFarHOSImeNDwZcI++/BKpumCZSQoXYeZmmEAzi\n/S6TdOM/AgMBAAECggEAQ7zBLAVDSVAsqhPf5+1cOkwSj46b1oJMmmJI1zPoQjAV\nAxN7FZYyl6pv/4K11nkwqJYx4gGcTnN+btXYxNG30TXI+2XNXCoNqahOzBblVnYD\nCVVc015EiL5crJBurvvM+OfrnDIFjw/VnRpQ90vGvbDlK6KY4ESnfz1CXyxvR2yq\n3lDHMqdekezYcIjOiL6Fn/YoK1BfV9GTgJdjfQXv0GfWGkAw3IP3E9s7XPNi4yek\nxb467lVWBIKIkuYMFgJ6+dWx+iDul8iSRRg15Vi1P/hG/1Dweg7VhR84R2jjrFdi\npwhDwqNq4tJs1EmKU3JX72FmJGqW3agXmagS1zjb3QKBgQDDyUgewgIu9ik9kJeZ\nD/pRExrAYBYy7ZTnM+reM0YCzKABdniMQCWc2gTx9AqU7bwqiBi97QCpU/eE4QnB\n/napOmCtXZ7qGf8QoSN6AiVhB59A9ZuqLHtRY39ZhX4iYo3Emng535CMMeI2qM/g\nW4sxXGzP051ifV2SglQx5ahXawKBgQDACWxnp2Mab70Olf5Ok2Fc1F03badMypY/\nGcLLz0P08C+cYzjQ7r/3PGBHBEip/iCU71oDrQab1c+/BxlNJ6gSv0eEq2imopHV\nmxto23PjL0FGZ+jERmi9mjg7JxFQIjdqBNKZsEvA+taVfPQmZ1C78lr0muf8S20f\nz/JH+TecfQKBgEyoNrC0TZ6Ni0ArqO+pLd0omcTQ2mA+XZrY3RD7CmJ2M//envxq\n8U8kneMOJkaBfrc4aleSwDuMQNGqOuPV+ifwT4IRsfL/Ers0HGvdAz2melg40iYj\nHHWVe3tVpTlZVSCxSnl+a144+dVk619w+GLvSTtmI604YLbIiKawwOTZAoGAf8fF\nclNXBkhDrGjyBqbaqkJEpJU6NUa4ItSpYaRQu7L2e0EqlRvIcGKkTZz0HOkUFQYP\nB1Miip8C1UGL/GLe21qb5BOKVxbloxTKcENWIV1YOdj6cV/IYiE0OWgNhRy/crQy\nzkEYpxhBoMa8TrGAbw8cppZMtvwZaImd1XZnIqECgYEAg2ZXToy2HbGej6EeA3fP\nnyA24LGNyqg0+6+FlGk7Z/8J/5tiez/LY8Io4B+BdxPS+fWNz1zrOd1XqIq+mK3b\nxLjQFubVgf0e/3bSJDulwUuEaTkJ8BMhqkIJWPfPHlmtqUnwnmshu/2PJW1okajF\n1fgFZ2067YLIkBkCZShrBXU=\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-8palo@sid-black.iam.gserviceaccount.com",
            "client_id": "109743904374379391777",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-8palo%40sid-black.iam.gserviceaccount.com"
        }
        )
        self.app = initialize_app(creds, {
            'databaseURL': 'https://sid-black.firebaseio.com',
        })

    def get_user_info(self, uid):
        user = db.reference('users/{0}'.format(uid)).get()
        return user
