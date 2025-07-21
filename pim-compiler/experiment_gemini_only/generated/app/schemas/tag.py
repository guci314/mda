from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagPublic(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
