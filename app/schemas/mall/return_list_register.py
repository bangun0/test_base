from typing import List, Optional
from pydantic import BaseModel
from ..mall.delivery_list_register import GoodsNoDawnDTO # Reusing existing model

class MallApiReturnDTO(BaseModel):
    goodsList: List[GoodsNoDawnDTO]
