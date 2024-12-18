# import os
# import re
# import cv2
# from collections import defaultdict
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
# from neo4j import GraphDatabase
# from dotenv import load_dotenv

# # Ensure required NLTK packages are downloaded
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('wordnet')

# # Initialize NLP tools
# lemmatizer = WordNetLemmatizer()
# stop_words = set(stopwords.words('english'))

# # Load environment variables
# load_dotenv(r"C:\Users\shiva\Downloads\BTP_env_variables.env")

# # Get API key and folder paths
# NEO4J_URI = os.getenv('NEO4J_URI')
# NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
# NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# # Function to run Cypher queries
# def run_query(query, parameters=None):
#     with driver.session() as session:
#         session.run(query, parameters)

# # Function to preprocess text (stopword removal, lemmatization)
# def preprocess_text(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             text = file.read()

#         # Improved regex for section detection, handling multiple cases
#         sections = re.split(r'(?i)\b(Abstract|Introduction|Methods|Results|Conclusion)\b', text)
#         section_data = defaultdict(str)
        
#         if len(sections) <= 1:
#             return section_data  # No recognizable sections found

#         for i in range(1, len(sections), 2):
#             section_title = sections[i].strip().lower()  # Normalize section title
#             content = sections[i + 1].strip()

#             # Tokenize, remove stop words, and lemmatize the content
#             words = word_tokenize(content)
#             filtered_content = [lemmatizer.lemmatize(w.lower()) for w in words if w.lower() not in stop_words and w.isalnum()]
#             processed_content = ' '.join(filtered_content)

#             section_data[section_title] = processed_content

#         return section_data

#     except Exception as e:
#         print(f"Error processing text file {file_path}: {e}")
#         return {}

# # Function to process images using OpenCV (basic filtering to check relevance)
# def preprocess_image(image_path):
#     try:
#         image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#         if image is None:
#             raise ValueError(f"Image file {image_path} could not be loaded.")

#         # Example: Check image entropy instead of size to filter out low-information images
#         entropy = cv2.calcHist([image], [0], None, [256], [0, 256]).sum()
#         if entropy < 5000:  # Threshold for relevance (tune as needed)
#             return None

#         return image_path  # Return the valid image path
    
#     except Exception as e:
#         print(f"Error processing image file {image_path}: {e}")
#         return None

# # Define the path to the directory with your data
# data_dir = r"E:\BTP\PDF_Extracted"

# # Process each paper in the directory
# for file_name in os.listdir(data_dir):
#     if file_name.endswith('_text.txt'):
#         try:
#             paper_name = file_name.split('_')[0]
#             page_number = file_name.split('_')[1]
#             txt_file_path = os.path.join(data_dir, file_name)
#             img_file_path = os.path.join(data_dir, f"{paper_name}_{page_number}_image.png")

#             # Preprocess text
#             sections = preprocess_text(txt_file_path)

#             # Add paper node (only once per paper)
#             run_query("MERGE (p:Paper {name: $name})", {"name": paper_name})

#             # Add section nodes and connect to paper
#             for section, content in sections.items():
#                 section_node = f"{paper_name}_{section}"
#                 if content:  # Only create a section if there's actual content
#                     run_query("""
#                         MERGE (s:Section {name: $section, content: $content})
#                         MERGE (p:Paper {name: $paper_name})
#                         MERGE (p)-[:HAS_SECTION]->(s)
#                     """, {"section": section_node, "content": content, "paper_name": paper_name})

#                     # Preprocess and link images (if they exist and are relevant)
#                     if os.path.exists(img_file_path):
#                         image_data = preprocess_image(img_file_path)
#                         if image_data:  # Only add relevant images
#                             image_node = f"{paper_name}_image_{page_number}"
#                             run_query("""
#                                 MERGE (i:Image {name: $image, path: $path})
#                                 MERGE (s:Section {name: $section})
#                                 MERGE (s)-[:HAS_IMAGE]->(i)
#                             """, {"image": image_node, "path": image_data, "section": section_node})

#         except Exception as e:
#             print(f"Error processing paper {file_name}: {e}")

# # Close the Neo4j connection
# driver.close()

# print("Graph creation in Neo4j is complete.")


import os
import re
from collections import defaultdict
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"C:\Users\shiva\Downloads\BTP_env_variables.env")

# Get API key and folder paths
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Function to run Cypher queries
def run_query(query, parameters=None):
    with driver.session() as session:
        session.run(query, parameters)

# Function to preprocess text and extract important sections
def preprocess_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Regular expression to split the document into sections (Abstract, Introduction, Methods, Results, Conclusion)
        sections = re.split(r'(?i)\b(Abstract|Introduction|Methods|Materials|Methodology|Metagenomics|Metabolomics|Results|Discussion|Conclusion|Findings)\b', text)
        section_data = defaultdict(str)

        if len(sections) <= 1:
            return section_data  # No recognizable sections found

        for i in range(1, len(sections), 2):
            section_title = sections[i].strip().lower()  # Normalize section title
            content = sections[i + 1].strip()

            # Only keep content for recognized sections
            if section_title in ['abstract', 'introduction', 'methods', 'results', 'conclusion','materials','methodology','metagenomics','metabolomics','discussion','findings']:
                section_data[section_title] = content

        return section_data

    except Exception as e:
        print(f"Error processing text file {file_path}: {e}")
        return {}

# Define the path to the directory with your data
data_dir = r"E:\BTP_extra\PDF_Extracted\PDF_Extracted"

# Process each paper in the directory
for file_name in os.listdir(data_dir):
    if file_name.endswith('_text.txt'):
        try:
            paper_name = file_name.split('_')[0]
            page_number = file_name.split('_')[1]
            txt_file_path = os.path.join(data_dir, file_name)

            # Preprocess text
            sections = preprocess_text(txt_file_path)

            # Add section nodes and connect to paper
            for section, content in sections.items():
                section_node = f"{paper_name}_{section}"
                if content:  # Only create a section if there's actual content
                    query = """
                        MERGE (p:Section {name: $section_node})
                        SET p.content = $content
                    """
                    run_query(query, {"section_node": section_node, "content": content})

        except Exception as e:
            print(f"Error processing paper {file_name}: {e}")

# Close the Neo4j connection
driver.close()

print("Graph creation in Neo4j is complete.")
