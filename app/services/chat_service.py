'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from email import message
import requests
from datetime import datetime, timedelta
from app.extensions import db
from app.models.usage import ClientUsage
from app.models.chat import ChatHistory, ChatMessage
from app.services.ai_service import call_ai
from app.services.cache_service import set_cache
from app.services.cache_service import get_cache
from app.services.rate_limiter import check_rate_limit
from app.utils.token_counter import count_tokens


# ---------------- CHECK QUOTA ----------------
def check_quota(client_uuid, tokens_used): 

    # 1. Get usage first
    usage = ClientUsage.query.filter_by(client_uuid=client_uuid).first()

    # 2. Create if missing
    if not usage:
        usage = ClientUsage(
            client_uuid=client_uuid,
            token_counter=0,
            token_limit=1000,
            token_reset_time=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add(usage)
        db.session.commit()

    # 3. Reset logic
    if usage.token_reset_time and usage.token_reset_time < datetime.utcnow():
        usage.token_counter = 0
        usage.token_reset_time = datetime.utcnow() + timedelta(days=1)

    # 4. Quota check
    if usage.token_counter + tokens_used > usage.token_limit:
        return False, "Quota exceeded"

    # 5. Update usage
    usage.token_counter += tokens_used
    usage.last_used_at = datetime.utcnow()

    db.session.commit()

    return True, None

# ---------------- CREATE CHAT ----------------
def create_chat(client_uuid, title):

    chat = ChatHistory(
        client_uuid=client_uuid,
        chat_title=title,
        chat_description=""
    )

    db.session.add(chat)
    db.session.commit()

    return chat


# ---------------- SEND MESSAGE ----------------
def send_message(client_uuid, chat_id, message):

    cache_key = f"chat:{chat_id}:{message}"

    # ---------------- CACHE CHECK ----------------
    cached = get_cache(cache_key)
    if cached:
        return cached, None

    # ---------------- RATE LIMIT ----------------
    if not check_rate_limit(client_uuid):
        return None, "AI_ERROR", None, "Rate limit exceeded. Try again later." 
      
    try:
        # ---------------- SAVE USER MESSAGE ----------------
        user_msg = ChatMessage(
            chat_history_uuid=chat_id,
            chat_message=message,
            message_type="user"
        )
        db.session.add(user_msg)

        # ---------------- CHAT HISTORY ----------------
        history = ChatMessage.query.filter_by(
            chat_history_uuid=chat_id
        ).order_by(ChatMessage.created_at).all()

        messages = [
            {
                "role": "user" if m.message_type == "user" else "assistant",
                "content": m.chat_message
            }
            for m in history
        ]

        # ---------------- QUOTA ----------------
        tokens_used = count_tokens(message)

        ok, error = check_quota(client_uuid, tokens_used)
        if not ok:
            db.session.rollback()
            return None, "AI_ERROR", str(error), None
 
        # ---------------- AI CALL ----------------
        payload = {
            "session_uuid": str(chat_id),
            "user_uuid": str(client_uuid),
            "question": message,
            "response_type": "session"
        }

        ai_response, error = call_ai(payload)

        # ❌ AI FAILURE
        if error:
            return None, "AI_UNAVAILABLE", str(error), None
            
        # ❌ INVALID RESPONSE
        if not ai_response or not isinstance(ai_response, dict):
            # AI down
            return None, "AI_DOWN", None, None
          
        # ---------------- PARSE ----------------
        ai_text = ai_response.get("answer", "No response")

        # ---------------- SAVE AI MESSAGE ----------------
        ai_msg = ChatMessage(
            chat_history_uuid=chat_id,
            chat_message=ai_text,
            message_type="ai"
        )

        db.session.add(ai_msg)
        db.session.commit()

        # ---------------- CACHE RESULT ----------------
        set_cache(cache_key, ai_text)

        return ai_text, None

    except Exception as e:
        db.session.rollback()
        return None, "AI_ERROR", str(e), None 
        