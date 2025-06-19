import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("\nAvailable Audio Devices:")
    print("-----------------------")
    
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"Index {i}: {dev['name']}")
        print(f"   Input Channels: {dev['maxInputChannels']} | Output Channels: {dev['maxOutputChannels']}")
        print(f"   Default Sample Rate: {dev['defaultSampleRate']} Hz")
        print("---")

    p.terminate()

if __name__ == "__main__":
    list_audio_devices()