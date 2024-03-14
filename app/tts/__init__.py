from flask import Blueprint

bp = Blueprint('tts', __name__)

from app.tts import gtts_proxy, gpt_tts_proxy
