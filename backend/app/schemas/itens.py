from pydantic import BaseModel, Field, ConfigDict


class ItensApiExterna(BaseModel):
    id_externo: int = Field(validation_alias="id")
    titulo: str = Field(validation_alias="title")
    numero_referencia: str | None = Field(validation_alias="main_reference_number")
    data_exibicao: str | None = Field(validation_alias="date_display")
    info_artista: str | None = Field(validation_alias="artist_display")
    short_description: str | None = None
    image_id: str = Field(validation_alias="image_id")


class ItemResumo(BaseModel):
    id: int
    titulo: str
    data_exibicao: str | None = None
    info_artista: str | None = None
    imagem_id: str

    model_config = ConfigDict(from_attributes=True)


class ItemDetalhesResponse(ItemResumo):
    id_externo: int
    descricao: str | None = None
    numero_referencia: str | None = None