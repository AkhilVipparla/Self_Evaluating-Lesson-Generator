from pydantic import BaseModel, Field


class LessonOutput(BaseModel):
    title: str = Field(description="Short, beginner-friendly lesson title")
    lesson: str = Field(
        description="Full lesson body in markdown, following the required section headings"
    )
