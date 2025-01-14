import whisper
import sounddevice as sd
import soundfile as sf
from pathlib import Path
import time

def transcribe_audio(audio_source=None, duration=5, sample_rate=16000):
    """
    Transcribe audio from either a microphone or an audio file using OpenAI's Whisper.
    
    Args:
        audio_source (str, optional): Path to audio file. If None, records from microphone
        duration (int, optional): Recording duration in seconds if using microphone
        sample_rate (int, optional): Sample rate for recording/processing
        
    Returns:
        str: Transcribed text
    """
    # Load Whisper model
    model = whisper.load_model("base")
    
    if audio_source is None:
        # Record from microphone
        print(f"Recording for {duration} seconds...")
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        print("Recording complete...")
        
        # Save recording temporarily in the script's directory
        script_dir = Path(__file__).parent
        temp_file = str(script_dir / "temp_recording.wav")
        print(f"Debug: Will save file to: {temp_file}")
        audio_data = audio_data.squeeze()
        try:
            sf.write(temp_file, audio_data, sample_rate)
            time.sleep(0.5)  # Add a small delay to ensure file is written
            audio_path = temp_file
            
            if not Path(audio_path).is_file():
                print(f"Error: Audio file not found at {audio_path}")
                return None
                
            print(f"Debug: About to transcribe file at: {audio_path}")
        except Exception as e:
            print(f"Error saving temporary audio file: {str(e)}")
            return None
        
    else:
        # Use provided audio file
        audio_path = audio_source
    
    # Transcribe the audio
    try:
        print(f"Debug: About to transcribe file at: {audio_path}")
        # Add error handling for model transcription
        try:
            result = model.transcribe(audio_path, fp16=False)  # Explicitly disable FP16
            transcribed_text = result["text"]
            
            # Clean up temporary file if it was created
            if audio_source is None:
                Path(temp_file).unlink(missing_ok=True)
                
            return transcribed_text.strip()
        
        except RuntimeError as re:
            print(f"Runtime Error during transcription: {str(re)}")
            return None
        except Exception as e:
            print(f"Detailed transcription error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return None
            
    except Exception as e:
        print(f"Outer error during transcription: {str(e)}")
        import traceback
        print(f"Full outer traceback: {traceback.format_exc()}")
        return None

# Example usage:
if __name__ == "__main__":
    # Example 1: Record from microphone
    print("Recording from microphone:")
    text = transcribe_audio(duration=5)
    print(f"Transcribed text: {text}")
