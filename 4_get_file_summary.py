import requests
import time
import os
import json

def simulate_typing(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Add a new line at the end

# Function to retrieve all files in the set
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
app_files_json = os.path.join(PROJECT_ROOT, "app_files.json")

def read_app_files():
    print("Reading app files from:", app_files_json)
    if os.path.exists(app_files_json):
        with open(app_files_json, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    print("No file content found in:", app_files_json)
    return []

# Function to read the content of a file
def read_file_content(file_path):
    full_file_path = os.path.join(PROJECT_ROOT, file_path)
    with open(full_file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Function to summarize files using DeepSeek API
def get_summary_from_deepseek(files_content):
    print(f"Creating prompt for {len(files_content)} files.")
    # print(files_content)
    url = "https://api.siliconflow.cn/v1/chat/completions"
    print("Requesting summary from DeepSeek API...")
    # print(f"{json.dumps(files_content, ensure_ascii=False, indent=4)}")
    # Create the prompt to ask for summaries in a structured format
    prompt = (
        "You are a code summarization assistant. Please summarize the following code files "
        "and return the results as a JSON object where each key is the file name and the "
        "value is a brief summary of the file's content. The summary should be concise and "
        "focus on the key elements and functionality of each file. Here are the files to summarize:\n"
    )

    # Extend the prompt with the JSON structure
    prompt += json.dumps(files_content, ensure_ascii=False, indent=4)
    
    # Print the first part of the prompt as a sample
    # print("\nSample prompt given to the model:\n")
    # print(prompt[:500])  # Print only the first 500 characters for readability

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.3,  # Reduced randomness for consistency
        "top_p": 0.9,        # Higher top_p to focus on more probable outputs
        "top_k": 50,         # Limit to the top 50 tokens to avoid too many variations
        "frequency_penalty": 0.3,  # Encourage diverse output but within reason
        "n": 1,
        "response_format": {"type": "text"}
    }

    headers = {
        "Authorization": "Bearer sk-pslfsadqmaolfpncuucdtiytsumfckvnlvpfukvbalovxujs",  # Replace with your actual API key
        "Content-Type": "application/json"
    }

    try:
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"OOps: Something Else: {err}")

    if response.status_code == 200:
        print("\nModel Response (First part):\n")
        print(response.text[:500])  # Print only the first 500 characters for readability
        return response.json()
    else:
        print(f"Failed to get response from API: {response.status_code}")
        return None

# Main code to process the files in chunks and summarize them
def process_files():
    print("Starting the file processing...")
    
    file_paths = read_app_files()
    print(f"Total files to process: {file_paths}")
    files_content = {}
    pass
    # Read the content of each file and store it
    print(f"Reading the content of {len(file_paths)} files...")
    for file_path in file_paths:
        full_file_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.exists(full_file_path):
            content = read_file_content(file_path)
            files_content[file_path] = content
        else:
            print(f"File not found: {full_file_path}")

    # Chunk the files into groups of 5
    print(f"Chunking files into groups of 5...")
    file_chunks = [list(files_content.keys())[i:i + 5] for i in range(0, len(files_content), 5)]

    all_summaries = []

    # Process each chunk
    for i, chunk in enumerate(file_chunks):
        print(chunk)
        # break
        print(f"\nProcessing chunk {i+1}/{len(file_chunks)} with {len(chunk)} files.")
        chunk_content = {file: files_content[file] for file in chunk}
        print(chunk_content)
        # break
        # chunk_content = {file: files_content[file] for file in chunk}
        summary = get_summary_from_deepseek(chunk_content)

        if summary:
            all_summaries.append(summary)

    # Concatenate all summaries into a structured JSON format
    print("\nConcatenating all summaries into a final JSON structure...")
    final_summary = {"files_summary": all_summaries}

    # Output the result as JSON
    with open(os.path.join(PROJECT_ROOT, "final_summary.json"), 'w', encoding='utf-8') as json_file:
        json.dump(final_summary, json_file, ensure_ascii=False, indent=4)
    print("Final summary saved to final_summary.json.")

if __name__ == '__main__':
    process_files()