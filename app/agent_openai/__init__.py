from flask import Blueprint

# 查询/唱歌/绘画
bp = Blueprint('agent_openai', __name__)

from app.agent_openai import agent_facade
