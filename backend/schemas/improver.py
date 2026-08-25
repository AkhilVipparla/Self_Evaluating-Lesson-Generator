from pydantic import BaseModel, Field


class ImproverOutput(BaseModel):
    updated_lesson: str = Field(
        description="Full lesson markdown with only the failed sections rewritten; "
        "passing sections copied over unchanged"
    )
