import dataclasses
from functools import cached_property
from collections import OrderedDict


@dataclasses.dataclass
class Product:
    name: str
    description: str
    price: int
    url: str
    company: str = None
    company_url: str = None
    material: str = None
    old_price: int = None
    breadcrumb: str = None
    collection_id: str = None
    number_of_colors: int = 1
    id_or_reference: str = None
    images: list = dataclasses.field(default_factory=list)
    composition: str = None
    color: str = None
    date: str = None
    sizes: list = dataclasses.field(default_factory=list)

    @cached_property
    def fields(self):
        fields = dataclasses.fields(self)
        return list(map(lambda x: x.name, fields))

    def as_dict(self):
        data = OrderedDict()
        for field in self.fields:
            data[field] = getattr(self, field)
        return data
