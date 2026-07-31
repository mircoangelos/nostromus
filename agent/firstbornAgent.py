import os
import json
import logging
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import generatorFirstVersion

### execution layer
base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "nostromus.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NostromusAgent")

## setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
model_id = os.getenv("MODEL_NAME")

client = genai.Client(api_key=api_key)

def load_skills():
    """Load the agent's rule set from the Markdown file."""
    skills_path = os.path.join(base_dir, "agentSkills.md")
    try:
        with open(skills_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Skill set file 'agentSkills.md' not found.")
        return "You are a Security Analyst. If login attempts > 5, lock the user and generate a report."

def process_event(event_file):
    """Simulate processing a message from the RabbitMQ queue."""
    logger.info(f"Processing event file: {event_file}")
    
    try:
        #  read jsonfile
        if not os.path.exists(event_file):
            logger.error(f"File {event_file} does not exist.")
            return

        with open(event_file, 'r', encoding='utf-8') as f:
            event_data = json.load(f)

        user_id = event_data.get('data', {}).get('user_id', 'Unknown')
        logger.info(f"Analyzing activity for user: {user_id}")

        # reasoning Layer
        skills = load_skills()
        
        # call Gemini agent with AFC
        response = client.models.generate_content(
            model=model_id,
            contents=f"Analyze this security event and execute required tools: {json.dumps(event_data)}",
            config=types.GenerateContentConfig(
                system_instruction=skills,
                tools=[
                    generatorFirstVersion.update_user_status, 
                    generatorFirstVersion.generate_security_report
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )
        )

        # display Agent conclusion
        if response.text:
            print(f"\n[GEMINI AGENT]: {response.text}")
        else:
            print("\n[GEMINI AGENT]: Preventive actions successfully executed.")

    except Exception as e:
        logger.error(f"Critical failure processing {event_file}: {e}")


if __name__ == "__main__":
    
    demo_events = [
        "event01.json", 
        "event02.json",
        "eventBruteForce.json"
    ]
    
    logger.info("====================================================")
    logger.info("    STARTING NOSTROMUS AI SECURITY MONITOR          ")
    logger.info("====================================================")
    
    
    try:
        with open(os.path.join(base_dir, "test_write.txt"), "w") as f:
            f.write("File system is ready.")
    except Exception as e:
        logger.error(f"Folder permission error: {e}")

    for file in demo_events:
        process_event(file)
        time.sleep(45) 

    logger.info("====================================================")
    logger.info("    DEMO SEQUENCE COMPLETED SUCCESSFULLY           ")
    logger.info("====================================================")