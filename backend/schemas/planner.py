from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    audience: str = Field(description="Who this lesson is written for")
    learning_goals: list[str] = Field(
        description="Ordered list of teaching objectives the lesson must cover"
    )
    avoid: list[str] = Field(
        description="Things the lesson must avoid (jargon, advanced math, etc.)"
    )
