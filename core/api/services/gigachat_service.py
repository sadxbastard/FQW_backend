from gigachat import GigaChat

giga = GigaChat(
    credentials="ZTQ3NWZhMmMtZTBkYy00YzVjLWEyNmQtMmQ0YWFjZGMyNGEwOmY1ZmY3ZmE1LTE1YmYtNDhjMi04ZDM1LTA3MDA5MDcwZjRhOA==",
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False  # или certifi.where()
)

def generate_test_text(prompt: str):
    response = giga.chat(prompt)
    return response.choices[0].message.content
