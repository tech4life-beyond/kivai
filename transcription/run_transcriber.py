from whisper_transcriber import WhisperTranscriber


def main():
    audio_file = "C:/Users/Master/Desktop/sample.mp3"  # Full path to the file
    transcriber = WhisperTranscriber(model_size="base")
    text = transcriber.transcribe(audio_file)
    print("\n--- Transcription Output ---\n")
    print(text)


if __name__ == "__main__":
    main()
