from app.agent_openai.agent.agent_template import introduce_template


def introduce(input: str):
    '''这个方法在用户需要Agent自我介绍时使用'''
    return introduce_template


def default(input: str):
    '''当无法分类问题或者AI认为可以回答时使用这个方法'''
    '''Use this when it is impossible to categorize the question or when AI assistant thinks it can be answered'''
    return input
