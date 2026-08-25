from pydantic import BaseModel, Field


class SemanticChecks(BaseModel):
    """Checks that require understanding, judged by the LLM."""

    definition: bool = Field(description="Does the lesson clearly define the topic?")
    motivation: bool = Field(description="Does the lesson explain why the topic matters/is needed?")
    workflow: bool = Field(
        description="Does the lesson clearly explain the core process/mechanism of the topic?"
    )
    example: bool = Field(description="Does the lesson include a realistic, concrete beginner example?")
    accuracy: bool = Field(description="Is the lesson free of factual mistakes?")
    reasons: list[str] = Field(
        default_factory=list,
        description="One short reason per failed semantic check, empty if all pass",
    )


class EvaluationReport(BaseModel):
    pass_: bool = Field(alias="pass")
    checks: dict[str, bool]
    reasons: list[str]

    model_config = {"populate_by_name": True}
