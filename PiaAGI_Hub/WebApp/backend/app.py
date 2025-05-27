import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
from flask_cors import CORS

# Load environment variables from .env file (if it exists)
# For example, you could set a default OPENAI_API_KEY here for development
# if you don't want to pass it from the frontend every time.
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/api/hello')
def hello_world():
    return jsonify({'message': 'Hello from Flask backend!'})

@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        api_key = data.get('apiKey')
        prompt_content = data.get('prompt')
        test_question = data.get('testQuestion')
        llm_model = data.get('llmModel', 'gpt-3.5-turbo') # Default to gpt-3.5-turbo

        if not api_key:
            return jsonify({"error": "API key is missing"}), 400
        if not prompt_content:
            return jsonify({"error": "Prompt content is missing"}), 400
        if not test_question:
            return jsonify({"error": "Test question is missing"}), 400

        # Initialize OpenAI client
        # IMPORTANT: The API key is taken directly from the request for this subtask.
        # In a production environment, this key should be handled securely.
        client = OpenAI(api_key=api_key)

        # Make the API call
        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": test_question}
            ]
        )
        
        llm_response = completion.choices[0].message.content
        return jsonify({"response": llm_response})

    except AuthenticationError as e:
        app.logger.error(f"OpenAI Authentication Error: {e}")
        return jsonify({"error": "OpenAI API Key is invalid or expired."}), 401
    except RateLimitError as e:
        app.logger.error(f"OpenAI Rate Limit Error: {e}")
        return jsonify({"error": "OpenAI API rate limit exceeded. Please try again later."}), 429
    except APIConnectionError as e:
        app.logger.error(f"OpenAI API Connection Error: {e}")
        return jsonify({"error": "Could not connect to OpenAI. Please check your network."}), 500
    except APIError as e: # Catch other OpenAI API errors
        app.logger.error(f"OpenAI API Error: {e}")
        return jsonify({"error": f"An OpenAI API error occurred: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # The FLASK_RUN_PORT environment variable can be used to set the port
    # e.g., FLASK_RUN_PORT=5001 flask run
    # Default to 5000 if not set.
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, port=port)
