import whisper
import traceback

print("Loading model...")
model = whisper.load_model('tiny')
print("Transcribing...")
try:
    res = model.transcribe('test.ogg')
    print("Success:", res['text'])
except Exception as e:
    traceback.print_exc()
