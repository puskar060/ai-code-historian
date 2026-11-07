import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

class AIHistorianEngine:
    def __init__(self):
        # Gemini API Key .env bata load hunchha
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3
        )
        
        self.prompt = PromptTemplate(
            input_variables=["commit_msg", "author", "files", "diff_stats"],
            template="""
You are an expert Software Architecture AI Historian.
Analyze the following Git Commit details and explain what happened in terms of software architecture, structural changes, or potential technical debt.

Commit Message: {commit_msg}
Author: {author}
Files Modified: {files}
Changes: {diff_stats}

Provide a concise 3-bullet-point summary explaining:
1. What functional/architectural update occurred.
2. Impact on code evolution.
3. Potential risk or architectural advice.
"""
        )

    async def analyze_commit_narrative(self, commit_info: dict) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({
            "commit_msg": commit_info.get("message"),
            "author": commit_info.get("author"),
            "files": ", ".join(commit_info.get("files_changed", [])),
            "diff_stats": f"+{commit_info.get('additions')} / -{commit_info.get('deletions')}"
        })
        return response.content