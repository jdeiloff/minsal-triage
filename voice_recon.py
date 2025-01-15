import whisper
import sounddevice as sd
import soundfile as sf
from pathlib import Path
import time
import numpy as np
import tempfile
import subprocess
import sys
import platform

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        os_name = platform.system().lower()
        if os_name == 'linux':
            print("Please install ffmpeg using: sudo apt update && sudo apt install ffmpeg")
        elif os_name == 'darwin':
            print("Please install ffmpeg using: brew install ffmpeg")
        elif os_name == 'windows':
            print("Please download ffmpeg from https://www.gyan.dev/ffmpeg/builds/ and add it to your PATH")
        return False

def transcribe_audio(duration=5, sample_rate=44100):
    """
    Record audio from microphone and transcribe it using Whisper.
    """
    try:
        # Check for ffmpeg first
        if not check_ffmpeg():
            raise RuntimeError("ffmpeg is required but not installed. Please install ffmpeg first.")

        # Try to use PulseAudio by default
        try:
            devices = sd.query_devices()
            input_device = None
            
            # First try to find PulseAudio
            for device in devices:
                if 'pulse' in str(device['name']).lower():
                    input_device = device['index']
                    break
            
            # If no PulseAudio, try any input device
            if input_device is None:
                for device in devices:
                    if device['max_input_channels'] > 0:
                        input_device = device['index']
                        break
                    
            if input_device is None:
                raise RuntimeError("No input device found")

            # Get device info to use its native sample rate
            device_info = sd.query_devices(input_device, 'input')
            if device_info is not None:
                sample_rate = int(device_info['default_samplerate'])

            # Create a temporary directory that will be automatically cleaned up
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / "temp_recording.wav"
                
                # Record audio with explicit device selection
                print(f"Recording for {duration} seconds using device {input_device} at {sample_rate}Hz...")
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype='float32',
                    device=input_device,
                    blocking=True
                )
                
                # Normalize audio data
                audio_data = audio_data.squeeze()
                audio_data = np.clip(audio_data, -1, 1)
                
                # Save to temporary file
                sf.write(str(temp_path), audio_data, sample_rate)
                
                # Load Whisper model
                model = whisper.load_model("base")
                
                # Transcribe
                result = model.transcribe(str(temp_path), fp16=False)
                transcribed_text = result["text"].strip()
                
                return transcribed_text
                
        except Exception as e:
            raise RuntimeError(f"Error recording audio: {str(e)}")
            
    except Exception as e:
        print(f"Error in audio transcription: {str(e)}")
        # Print available audio devices for debugging
        print("\nAvailable audio devices:")
        print(sd.query_devices())
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    # Test recording
    print("Testing audio recording and transcription:")
    text = transcribe_audio(duration=5)
    print(f"Transcribed text: {text}")
