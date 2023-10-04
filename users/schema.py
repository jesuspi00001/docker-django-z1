import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphene_django.types import DjangoObjectType
from users.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
    

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password):
        user = User(username=username, email=email, password=password)
        user.set_password(password)
        user.save()
        return CreateUser(user=user)
    

class DeleteUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    message = graphene.String()

    def mutate(self, info, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
            return DeleteUser(message=f"Usuario {username} eliminado correctamente")
        except User.DoesNotExist:
            return DeleteUser(message=f"Usuario {username} no encontrado")


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, id, username, email, password):
        user = User.objects.get(pk=id)
        user.username = username
        user.email = email
        user.password = password
        user.save()
        return UpdateUser(user=user)
    
class TokenAuthWithEmail(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())

    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    def resolve_users(self, info):
        return User.objects.all()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    delete_user = DeleteUser.Field()
    update_user = UpdateUser.Field()
    token_auth_with_email = TokenAuthWithEmail.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)