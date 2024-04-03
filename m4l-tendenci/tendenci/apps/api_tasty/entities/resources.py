from tendenci.apps.entities.models import Entity
from tendenci.apps.api_tasty.resources import TendenciResource

class EntityResource(TendenciResource):
    class Meta(TendenciResource.Meta):
        queryset = Entity.objects.all()
        resource_name = 'entity'
        object_class = Entity
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
