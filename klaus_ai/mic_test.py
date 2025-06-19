import speech_recognition as sr

def test_microphone(device_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("\nSpeak into your Bluetooth microphone now...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5)
        
        try:
            text = r.recognize_google(audio)
            print(f"\nSUCCESS! Heard: '{text}'")
            return True
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            return False

# Replace with your Bluetooth mic index
test_microphone(device_index=1)  # Change this number