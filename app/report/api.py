import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the secret OpenAI API key and other important configurations from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("REPORT_MODEL", "gpt-4o-2024-08-06")

# Set up your OpenAI client with your API key
client = OpenAI(api_key=openai_api_key)

# Define the JSON schema using Pydantic for different sections of the report
class ReportSection(BaseModel):
    Overview: str  # A brief overview of issues and suggestions for improvements
    ActionableRecommendations: Optional[List[str]] = Field(default_factory=list)  # Optional list of specific, detailed changes to address issues

# Define the complete structure of the chapter report using Pydantic
class ChapterReport(BaseModel):
    ChapterOverview: ReportSection
    ConsistencyInNarrativeElements: Optional[ReportSection] = None  # Optional section
    DetailConsistencyCheck: Optional[ReportSection] = None  # Optional section

# Define a detailed system prompt
system_prompt = """
You are a literary analysis expert tasked with generating a structured JSON report for chapter {{chapter_number}} of a manuscript. You will be provided with all chapters up to chapter {{chapter_number}} for reference. Use these chapters to ensure consistency, detect plot holes, and maintain continuity. Each section of the report should include:

Each of the three sections should consist of:
1. A short overview summarizing the main findings or observations in that area.
2. A list of actionable recommendations based on the listed consistency checks, specifying exact changes or additions to be made. Provide as many actionable recommendations as are necessary to address the specific issues identified in each section. If no actionable recommendations are needed, do not include any.

**Important Instructions:**
- The report should focus on identifying specific, factual discrepancies or inconsistencies within the manuscript.
- Reference exact lines, paragraphs, or sections of the text where discrepancies are found.
- Use concrete examples to illustrate recommended changes, showing the original text and the proposed revision. Ensure the changes directly address the identified inconsistencies.
- Avoid general or vague recommendations. Each recommendation should be based on precise issues found in the text and should provide a clear, factual basis for the suggested change.

**Section 1: Chapter Overview**
   - **Chapter Overview:** Provide a concise description of the main events, character actions, and any significant shifts in setting or tone within the chapter.
   - **Actionable Recommendations:**
     - Identify exact points where the clarity of events or character actions could be enhanced. Provide direct references to specific sentences or paragraphs.
     - Suggest precise modifications to improve plot coherence or character actions, demonstrating how the text should be altered.
     - If additional details or clarifications are needed, specify the exact location within the chapter for these additions, showing sample sentences or paragraphs.

**Section 2: Consistency in Narrative Elements**
   - **Consistency Checks:**
     - Check for exact alignment of characters' behaviors and motivations with their established traits in previous chapters. Reference specific text where inconsistencies occur.
     - Evaluate dialogue for its effectiveness in revealing character and advancing the plot. Suggest precise changes to dialogue where it may not align with character traits or plot needs.
     - Identify exact instances where pacing may be inappropriate for the chapter's events. Recommend specific adjustments, referencing the exact lines or scenes.
     - Highlight specific sections where conflict, tension, or emotional impact could be enhanced. Suggest concrete changes, such as additional sentences or rephrased text.
     - Ensure setting descriptions consistently match previous chapters. Point out exact discrepancies and provide revised text for consistency.
     - Confirm that key themes are conveyed consistently. Reference specific sections where themes could be better integrated or where inconsistencies occur.
     - Review the use of foreshadowing and symbolism. Identify specific instances where these elements should be clarified or enhanced.
     - Check for consistency in each character's use of language and speech patterns. Provide specific examples and corrections, such as use of contractions or lack of contractions.
     - Check for consistency in the use of compound words and hyphenation. Provide specific examples and corrections.

**Section 3: Detail Consistency Check**
   - **Consistency Checks:**
     - Verify consistency of character details such as eye color, hair color, hairstyles, and clothing by referencing specific descriptions.
     - Ensure continuity in character relationships, attitudes, and feelings towards each other. Identify exact discrepancies and suggest precise text changes.
     - Check consistency of events, timelines, and schedules. Reference specific timeline inconsistencies and provide corrected sequences or time references.
     - Look for exact discrepancies in recurring events or activities. Suggest concrete changes to maintain consistency.
     - Verify the accuracy of locations, objects, and background details by referencing specific descriptions.
     - Ensure consistent portrayal of weather, seasons, and time of day. Identify any mismatches and recommend specific corrections.
     - Check cultural, historical, or geographical references for accuracy. Provide specific corrections if inaccuracies are found.
     - Identify inconsistencies in the use of technology, language, or societal norms relevant to the story’s setting. Suggest exact changes where inconsistencies are found.
     - Look for discrepancies in recurring symbols or motifs. Provide specific examples and corrections.

Ensure the report is comprehensive and detailed, addressing each section with specific insights and actionable steps to improve the manuscript. If there are no actionable recommendations in the `Consistency in Narrative Elements` or `Detail Consistency Check` sections, exclude that part from the report to indicate thorough evaluation without necessary changes.
"""

# Function to generate a structured report for a given chapter
def generate_structured_report(chapter, chapter_number):
    try:
        # Replace placeholder in the system prompt with the actual chapter number
        formatted_prompt = system_prompt.replace("{{chapter_number}}", str(chapter_number))

        # Print what is being sent to the API for debugging purposes
        print(f"Sending to API for chapter {chapter_number}")

        # Use OpenAI client to create a completion request with structured parsing
        completion = client.beta.chat.completions.parse(
            model=openai_model,  # Specify the model to use (e.g., gpt-4o)
            messages=[
                {
                    "role": "system",
                    "content": formatted_prompt,
                },  # System prompt with replaced chapter number
                {
                    "role": "user",
                    "content": chapter,
                },  # User input containing the chapter text
            ],
            response_format=ChapterReport,  # Define the expected response format using Pydantic model
        )

        # Print the API response for debugging purposes
        print(f"API response for chapter {chapter_number}:")
        print(completion.choices[0].message.parsed)

        # Return the parsed message from the first choice of completions
        return completion.choices[0].message.parsed

    except Exception as e:
        # Print error message for debugging
        print(f"Error generating structured report for chapter {chapter_number}: {e}")
        return None
