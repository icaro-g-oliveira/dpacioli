import whisper
import os

# Caminho do áudio
audio_path = "audiodipacioli.wav"
#necessário instalar o ffmpeg e o definir como variavel do sistema



# Nome do arquivo de saída (sem extensão)
nome_base = os.path.splitext(os.path.basename(audio_path))[0]
output_txt = f"{nome_base}_transcricao.txt"

# Carrega modelo Whisper
model = whisper.load_model("small")  # ou "medium" se quiser mais precisão

# Transcreve o áudio com segmentação automática
print("Transcrevendo... isso pode levar alguns minutos.")
resultado = model.transcribe(audio_path, language="pt", verbose=True)

# Extrai a transcrição completa
texto_final = resultado["text"]

# Salva no .txt
with open(output_txt, "w", encoding="utf-8") as f:
     for segmento in resultado["segments"]:
        f.write(segmento["text"].strip() + "\n")

print(f"\n✅ Transcrição salva em: {output_txt}")
