import requests
import json
import openai
import re

from flask import Flask, request, render_template

# Set up Flask application
app = Flask(__name__)

# Set up OpenAI API credentials
openai.api_key = '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'

# YouTube Data API Key
youtube_api_key = 'AIzaSyArucvurCQNYNfGjy2wguha5cb3-MIrvLY'

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = extract_video_id(video_url)
        if video_id:
            transcript = get_video_transcript(video_id)
            flashcards = generate_flashcards(transcript)
            flashcards_table = format_flashcards_table(flashcards)
            return render_template('index.html', flashcards_table=flashcards_table)
    return render_template('index.html')

# Extract video ID from YouTube URL
def extract_video_id(video_url):
    video_id = re.findall(r'(?:v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v=|&v=|\?v=)([^#\&\?\/]*)', video_url)
    return video_id[0] if video_id else None

# Get video transcript from YouTube Data API
def get_video_transcript(video_id):
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={youtube_api_key}'
    response = requests.get(url)
    data = json.loads(response.text)
    transcript = data['items'][0]['snippet']['localized']['title']
    return transcript

# Generate flashcards using ChatGPT
def generate_flashcards(transcript):
    prompt = "Create at least 15 flashcards for the following transcript. Select flash cards that relate to the core idea of the content."
    text = f"\n{transcript}"
    flashcards = []

    chat_input = f"{prompt}\n{text}\n\nFlashcards:\nTerm:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "/prompt Create flashcards."},
            {"role": "user", "content": chat_input}
        ],
        max_tokens=4096,
        temperature=0,
        n=1,
        stop=None,
    )

    flashcards_chunk = response.choices[0]['message']['content']
    flashcards_chunk = flashcards_chunk.replace("Definition:", "").strip()
    flashcards.extend(flashcards_chunk.split("Term:")[1:])

    # Extract term and definition from each flashcard
    flashcards = [card.strip().split("\n", 1) for card in flashcards if card.strip()]

    return flashcards

# Format flashcards table
def format_flashcards_table(flashcards):
    parsed_flashcards = []
    for entry in flashcards:
        parsed_entry = tuple(entry)
        parsed_flashcards.append(parsed_entry)

    flashcards_table = [parsed_flashcards[i:i+2] for i in range(0, len(parsed_flashcards), 2)]

    return parsed_flashcards

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
