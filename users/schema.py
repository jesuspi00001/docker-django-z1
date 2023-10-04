import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from users.models import User, Idea


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea
        fields = ("id", "user", "text", "created_at")
    


################################################
########## Metodos tipicos CRUD ################
################################################

# CreateUser
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

# CreateIdea
class CreateIdea(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True)

    idea = graphene.Field(IdeaType)

    def mutate(self, info, text):
        # Verificamos si el usuario esta autenticado.
        user = info.context.user  # Obtenemos el user
        if user.is_authenticated:
            idea = Idea(user=user, text=text)
            idea.save()
            return CreateIdea(idea=idea)
        else:
            raise Exception('Usuario no logueado.')
        
    
# Delete
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

# Update
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
    


################################################
##### Autenticacion mediante email y pass ######
################################################

class TokenAuthWithEmail(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)
    


################################################
########### Cambio de password #################
################################################

class ChangePassword(graphene.Mutation):
    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()

    @login_required # El usuario debe haber iniciado sesion previamente antes de intentar cambiar su contraseña (en 0.0.0.0/admin). 
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise Exception("La contraseña actual es incorrecta.")
        user.set_password(new_password)
        user.save()
        return ChangePassword(success=True)
    


################################################
########## Correo con magic link ###############
################################################

# Esta historia de usuario ¡no funciona!. Es una simulacion de como podria hacerse.
# Se explica a lo largo del metodo.
class SendResetPasswordEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, email):
        try:
            user = User.objects.get(email=email)

            # Generamos un token
            reset_token = default_token_generator.make_token(user)

            # Lo asignamos al campo reset_password_token del user
            user.reset_password_token = reset_token
            user.save()

            # Url con el token
            reset_url = f'url/{reset_token}/'

            # Enviamos el correo
            subject = 'Restaurar password'
            message = 'Cambia tu password.'
            from_email = 'app_url@example'
            user_email = 'url_user@example'

            # El metodo recibe un asunto, un cuerpo, y los email y deberia enviar el correo de restablecimiento.
            send_mail(subject, message, from_email, user_email)

            return SendResetPasswordEmail(success=True)
        except User.DoesNotExist:
            return SendResetPasswordEmail(success=False)
        
        # Posteriormente habria que validar el token, que se suele crear con un tiempo de validez limitado.
        # Una vez validado se podria cambiar la contraseña. ¡Este metodo solo enviar el correo con el magic link!



################################################
########### Consultas de datos# #################
################################################

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())

    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    def resolve_users(self, info):
        return User.objects.all()



################################################
################## Mutation ####################
################################################

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_idea = CreateIdea.Field()
    delete_user = DeleteUser.Field()
    update_user = UpdateUser.Field()
    token_auth_with_email = TokenAuthWithEmail.Field()
    change_password = ChangePassword.Field()
    send_reset_password_email = SendResetPasswordEmail.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)