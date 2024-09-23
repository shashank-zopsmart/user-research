from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional

class QuoteSchema(BaseModel):
    quote: str
    code: str
    keywords: List[str]
    context: str

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class AnalysisSchema(BaseModel):
    codes: List[str]
    keywords: List[str]
    quotes: List[QuoteSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class SegmentSchema(BaseModel):
    title: str
    content: str
    main_idea: str

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class SegmentationSchema(BaseModel):
    summary: str
    segments: List[SegmentSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class ExcerptSchema(BaseModel):
    text: str
    code: str

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class SegmentCodingSchema(BaseModel):
    segment: str
    excerpts: List[ExcerptSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class CodingSchema(BaseModel):
    segments: List[SegmentCodingSchema]
    all_codes: List[str]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class ClusterSchema(BaseModel):
    cluster_name: str
    codes: List[str]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class ThemeSchema(BaseModel):
    theme_name: str
    clusters: List[ClusterSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class ThematicAnalysisSchema(BaseModel):
    themes: List[ThemeSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class PersonaSchema(BaseModel):
    name: str
    background: str
    goals: str
    motivations: str
    needs: str
    challenges: str
    behaviors: str
    attitudes: str
    relevant_quotes: List[str]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class AffinityMappingSchema(BaseModel):
    relationships: str
    personas: List[PersonaSchema]

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()


class ValidationAndRefinementSchema(BaseModel):
    refinements: Optional[List[Dict[str, Any]]] = None
    key_findings: str
    insights: str
    recommendations: str

    def __dir__(self):
        return self.model_dump()

    def __json__(self):
        return self.model_dump_json()
