from pydantic import BaseModel, Field


class ItensApiExterna(BaseModel):
    id_externo: int = Field(validation_alias="id")
    titulo: str = Field(validation_alias="title")
    numero_referencia: str = Field(validation_alias="main_reference_number")
    data_exibicao: str = Field(validation_alias="date_display")
    info_artista: str = Field(validation_alias="artist_display")
    short_description: str
