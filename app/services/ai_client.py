import requests
from app.config import Config


class AIClient:

    @staticmethod
    def ask_gemma(session_uuid, user_uuid, question, response_type="general", file_path=None):

        url = Config.AI_API_URL

        # ✅ form-data fields (matches curl)
        data = {
            "session_uuid": session_uuid,
            "user_uuid": user_uuid,
            "question": question,
            "response_type": response_type
        }

        # ✅ ADD DEBUG PRINT HERE
        print("=== AI REQUEST DATA ===")
        print(data)

        files = None

        # ✅ only include file if present
        if file_path:
            files = {
                "files": open(file_path, "rb")
            }

        try:
            response = requests.post(
                url,
                data=data,        # ✅ NOT json=
                files=files,      # ✅ matches curl -F files=
                timeout=Config.AI_RESPONSE_TIMEOUT
            )

            return response.json(), None

        except Exception as e:
            return None, str(e)