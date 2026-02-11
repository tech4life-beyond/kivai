import os
from whisper_transcriber import WhisperTranscriber


def test_transcription():
    audio_path = "C:/Users/Master/Desktop/sample.mp3"  # Update if needed
    assert os.path.exists(audio_path), f"Audio file not found: {audio_path}"

    transcriber = WhisperTranscriber()
    text = transcriber.transcribe(audio_path)

    assert isinstance(text, str), "Transcription did not return a string."
    assert len(text.strip()) > 0, "Transcription returned empty text."

    print("✅ Test passed! Transcription successful.")


if __name__ == "__main__":
    test_transcription()
