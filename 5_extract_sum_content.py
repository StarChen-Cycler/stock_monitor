import json

def extract_and_combine(input_file,output_file):
    # Read the JSON data from the file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Initialize an empty list to store the content
    contents = []
    
    # Iterate through each chunk and extract the content
    for chunk in data['files_summary']:
        for choice in chunk.get('choices', []):
            message = choice.get('message', {})
            content = message.get('content', '')
            print(content)
            # Remove the JSON markers and extract the actual content
            # if content.startswith('{') and content.endswith('}'):
                # Add the content to the list
            contents.append(content)
    
    # Save the extracted data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(contents, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_file = "final_summary.json"
    output_file = "extracted_content.json"
    extract_and_combine(input_file, output_file)