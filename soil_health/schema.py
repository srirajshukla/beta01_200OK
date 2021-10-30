import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
import channels_graphql_ws
from django_q.tasks import async_task
from .models import SoilHealth
from farmer.models import ExtendUser


class SoilHealthType(DjangoObjectType):
    class Meta:
        model = SoilHealth

class SoilHealthQuery(graphene.ObjectType):
    pass
class SoilHealthCreate(graphene.Mutation):
    soil_health = graphene.Field(SoilHealthType)
    class Arguments:
        soil_type = graphene.String()
        soil_ph = graphene.Float()
        soil_nitrogen = graphene.Float()
        soil_potassium = graphene.Float()
        soil_phosphorus = graphene.Float()
    
    @classmethod
    def mutate(self, root, info,soil_type, soil_ph, soil_nitrogen, soil_potassium, soil_phosphorus):
        soil_health = SoilHealth.objects.create(owner=info.context.user, soil_type=soil_type, 
            soil_ph=soil_ph, soil_nitrogen=soil_nitrogen,
            soil_potassium=soil_potassium, soil_phosphorus=soil_phosphorus)
        return SoilHealthCreate(soil_health = soil_health)

# sends a task to the q to predict
class CheckSoilHealth(graphene.Mutation):
    success = graphene.Boolean()
    class Arguments:
        nitrogen = graphene.Decimal()
        phosphorus = graphene.Decimal()
        potas = graphene.Decimal()
        humidity = graphene.Decimal()
        ph = graphene.Decimal()
        rainfall = graphene.Decimal()
        temp = graphene.Decimal()

    @classmethod
    @login_required
    def mutate(self, root, info, nitrogen, phosphorous, potas, humidity, ph, rainfall, temp):
        # async_task()
        async_task("services.crop_rec.recommend_crop", nitrogen, phosphorous, potas, humidity, ph, rainfall, temp, info.context.user.username, hook="services.crop_rec.send_subscription")
        return CheckSoilHealth(success = True)

# recieves the result from q and broadcasts the result
class SendSoilHealth(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        recs = graphene.List(graphene.String)
        group = graphene.String()

    @classmethod
    def mutate(self, root, info, recs, group):
        BroadcastSoilHealth.broadcast(group = group, payload=recs)
        return SendSoilHealth(success=True)

class SoilHealthMutation(graphene.ObjectType):
    create_soil_health = SoilHealthCreate.Field()
    check_soil_health = CheckSoilHealth.Field()
    send_soil_health = SendSoilHealth.Field()

# broadcast the result
class BroadcastSoilHealth(channels_graphql_ws.Subscription):
    # book = graphene.Field(BookType)
    recommendations = graphene.List(graphene.String)

    @staticmethod
    def subscribe(root, info):
        return [info.context.user.username]

    @staticmethod
    def publish(payload, info):
        return CheckSoilHealth(recommendations=payload)


class SoilHealthSubscriptions(graphene.ObjectType):
    soil_rec = BroadcastSoilHealth.Field()

