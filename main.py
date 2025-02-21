from pytubefix import YouTube
from pytubefix.cli import on_progress
import whisper
import os
import requests
import json

#Transcreve video do yt em audio

url = "https://www.youtube.com/watch?v=npSkqowqB90&ab_channel=RaulFilmes"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_audio_only()
arquivo_audio=ys.download(filename="audio.mp4")

arquivo_final = "audio.mp3"
os.system(f"ffmpeg -i audio.mp4 -q:a 0 -map a {arquivo_final} -y")  

#Transcreve audio em texto

modelo = whisper.load_model("base")
resposta = modelo.transcribe("audio.mp4")
transcricao = resposta["text"]

def dividir_texto(texto, tamanho_max=1000):
    partes = []
    while len(texto) > tamanho_max:
        corte = texto[:tamanho_max].rfind('.')  # Corta na última frase completa
        if corte == -1:  # Se não encontrar um ponto, corta direto
            corte = tamanho_max
        partes.append(texto[:corte + 1])
        texto = texto[corte + 1:].strip()
    partes.append(texto)
    return partes

partes_transcricao = dividir_texto(transcricao)


lmstudio_url="http://127.0.0.1:1234/v1/chat/completions"
resumos = []

for i, parte in enumerate(partes_transcricao):
    print(f"\n🔹 Resumindo parte {i + 1}/{len(partes_transcricao)}...")
    payload = {
        "model": "llama-3.2-1b-instruct",  # Nome do modelo conforme LmStudio
        "messages": [
            {"role": "system", "content": "Você é um assistente que resume textos."},
            {"role": "user", "content": f"Resuma o seguinte texto de maneira completa me trazendo as principais informações do video:\n\n{parte}"}
        ],
        "temperature": 0.5,
        "max_tokens": 150  # Reduz tokens para gerar resumos curtos
    }

headers = {"Content-Type": "application/json"}
response = requests.post(lmstudio_url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    resumo = response.json()["choices"][0]["message"]["content"]
    print("\n📌 Resumo do vídeo:\n", resumo)
else:
    print("\n⚠️ Erro ao gerar o resumo:", response.text)