import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from users.models import User, Idea, FollowRequest, UserFollowerList


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea
        fields = ("id", "user", "text", "visibility", "created_at")


class FollowRequestType(DjangoObjectType):
    class Meta:
        model = FollowRequest
        fields = ("id", "requester", "target_user", "created_at", "status")


class UserFollowerListType(DjangoObjectType):
    class Meta:
        model = UserFollowerList
        fields = ("id", "user", "following")
    


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
        visibility = graphene.String(required=True)

    idea = graphene.Field(IdeaType)

    def mutate(self, info, text, visibility):
        # Verificamos si el usuario esta autenticado. Me parece buena practica comprobar este tipo de cosas.
        user = info.context.user  # Obtenemos el user
        if user.is_authenticated:
            if visibility not in ["public", "private", "protected"]:
                raise Exception('Visibility debe ser: public, private o protected.')
            
            idea = Idea(user=user, text=text, visibility=visibility)
            idea.save()
            return CreateIdea(idea=idea)
        else:
            raise Exception('Usuario no logueado.')


# CreateFollowRequest
class CreateFollowRequest(graphene.Mutation):
    class Arguments:
        target_username = graphene.String(required=True)

    follow_request = graphene.Field(FollowRequestType)

    def mutate(self, info, target_username):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')

        target_user = User.objects.get(username=target_username)

        # Comprobamos si ya existe una solicitud 
        existing_request = FollowRequest.objects.filter(
            requester=user,
            target_user=target_user,
            status='pending'
        ).exists()
        if existing_request:
            raise Exception('Ya has enviado una solicitud a este usuario.')

        # Creamos una nueva solicitud de seguimiento
        follow_request = FollowRequest(
            requester=user,
            target_user=target_user,
            status='pending'
        )
        follow_request.save()
        return CreateFollowRequest(follow_request=follow_request)
    

# CreateUserFollowerList
class CreateUserFollowerList(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    userfollowerlist = graphene.Field(UserFollowerListType)

    def mutate(self, info, username):
        user = User.objects.get(username=username)

        # Creamos una instancia de UserFollowerList asociada a ese usuario.
        userfollowerlist = UserFollowerList(user=user)
        userfollowerlist.save()

        return CreateUserFollowerList(userfollowerlist=userfollowerlist)
    
    
# DeleteUser
class DeleteUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    message = graphene.String()

    def mutate(self, info, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
            return DeleteUser(message=f"Usuario {username} eliminado correctamente.")
        except User.DoesNotExist:
            return DeleteUser(message=f"Usuario {username} no encontrado.")


# DeleteIdea
class DeleteIdea(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')

        idea = Idea.objects.get(pk=id)
        if idea.user != user:
            raise Exception('No tienes permiso para eliminar esta idea.')
        
        idea.delete()
        return DeleteIdea(success=True)


# UpdateUser
class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password):
        user = User.objects.get(username=username)
        user.username = username
        user.email = email
        user.password = password
        user.save()
        return UpdateUser(user=user)


# UpdateIdea 
class UpdateIdea(graphene.Mutation):
    class Arguments:
        idea_id = graphene.ID(required=True)
        text = graphene.String(required=True)
        visibility = graphene.String(required=True)

    idea = graphene.Field(IdeaType)

    def mutate(self, info, idea_id, text, visibility):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        
        if visibility not in ["public", "private", "protected"]:
            raise Exception('Visibility debe ser: public, private o protected.')

        idea = Idea.objects.get(pk=idea_id)
        if idea.user != user:
            raise Exception('No tienes permiso para editar esta idea.')
        
        # El metodo permitira actualizar tanto el text como la visibility.
        idea.text = text
        idea.visibility = visibility
        idea.save()

        return UpdateIdea(idea=idea)
    


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



##########################################################
### Lista solicitudes recibidas para aprobar o denegar ###
##########################################################

class RespondToFollowRequest(graphene.Mutation):
    class Arguments:
        request_id = graphene.ID(required=True)
        response = graphene.String(required=True)  # Tomara como valores accepted o rejected.

    follow_request = graphene.Field(FollowRequestType)

    def mutate(self, info, request_id, response):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')

        follow_request = FollowRequest.objects.get(pk=request_id)

        # Comprobamos si el usuario logueado es el mismo que el de la solicitud (target_user).
        if user != follow_request.target_user:
            raise Exception('No tienes permiso para responder a esta solicitud.')

        # Comprobamos que la solicitud aun no ha sido respondida.
        if follow_request.status != 'pending':
            raise Exception('Ya has respondido a la solicitud.')

        # Asignamos accepted o rejected.
        if response == 'accepted':
            follow_request.status = 'accepted'
        elif response == 'rejected':
            follow_request.status = 'rejected'
        else:
            raise Exception('follow_request.status debe ser: accepted o rejected.')

        follow_request.save()

        # Actualizamos las relaciones de seguidores y seguidos en el UserFollowerList.
        if response == 'accepted':
            requester_user= follow_request.requester
            target_user = follow_request.target_user

            # Agregamos el solicitante a la lista de seguidores del objetivo.
            target_user.followers.add(requester_user)

            # Agregamos el objetivo a la lista de seguidos del solicitante.
            requester_user.following.add(target_user)

        return RespondToFollowRequest(follow_request=follow_request)
    


########################################################
############# Dejar de seguir a alguien ################
########################################################

class UnfollowUser(graphene.Mutation):
    class Arguments:
        user_to_unfollow = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, user_to_unfollow_id):
        user = info.context.user
        try:
            user_to_unfollow = User.objects.get(username=user_to_unfollow)
        except User.DoesNotExist:
            return UnfollowUser(success=False, message="El usuario que quieres dejar de seguir no existe.")

        # Comprobamos si sigue a ese usuario, en caso contrario no podemos dejar de seguirlo.
        user_follower_list = user.userfollowerlist
        if user_follower_list.following.filter(user=user_to_unfollow).exists():
            user_follower_list.following.remove(user_to_unfollow)
            return UnfollowUser(success=True, message=f"Dejaste de seguir a {user_to_unfollow.username}.")
        else:
            return UnfollowUser(success=False, message=f"No sigues a {user_to_unfollow.username}.")
        


########################################################
############## Eliminar a un seguidor ##################
########################################################
class RemoveFollower(graphene.Mutation):
    class Arguments:
        user_to_remove = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, user_to_remove):
        user = info.context.user
        try:
            user_to_remove_ = User.objects.get(username=user_to_remove)
        except User.DoesNotExist:
            return UnfollowUser(success=False, message="El usuario que quieres sacar de tu lista de seguidores no existe.")

        # Comprobamos si el usuario a eliminar es seguidor del usuario logueado, en caso contrario no podemos eliminarlo.
        user_follower_list = user.userfollowerlist
        if user_follower_list.followers.filter(user=user_to_remove_).exists():
            user_follower_list.followers.remove(user_to_remove_)
            return UnfollowUser(success=True, message=f"Eliminaste a {user_to_remove_.username} de tu lista de seguidores.")
        else:
            return UnfollowUser(success=False, message=f"EL usuario {user_to_remove_.username} no te sigue.")



################################################
########### Consultas de datos# ################
################################################

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())
    ideas = graphene.List(IdeaType)
    visible_ideas = graphene.List(IdeaType)
    user_ideas = graphene.List(IdeaType)
    follow_requests = graphene.List(FollowRequestType)
    following = graphene.List(UserType)
    followers = graphene.List(UserType)

    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_ideas(self, info):
        return Idea.objects.all()
    
    def resolve_visible_ideas(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        # Ahora nos quedamos solo con las ideas que el usuario puede ver (usuario logueado en 0.0.0.0/admin).
        public_ideas = Idea.objects.filter(visibility='public')
        followed_users = user.followed_users.all()
        protected_ideas = Idea.objects.filter(visibility='protected', user__in=followed_users)
        private_ideas = Idea.objects.filter(visibility='private', user=user)
        # Metemos todas las ideas visibles para ese usuario en una variable y lo devolvemos.
        all_ideas = list(public_ideas) + list(protected_ideas) + list(private_ideas)
        return all_ideas
    
    def resolve_user_ideas(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        # Cogemos todas las ideas de ese usuario y las metemos en una lista ordenadas por fecha de creacion descendente.
        ideas = Idea.objects.filter(user=user).order_by('-created_at')
        return ideas

    def resolve_follow_requests(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        return FollowRequest.objects.filter(target_user=user)
    
    def resolve_following(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        try:
            user_profile = UserFollowerList.objects.get(user=user)
        except UserFollowerList.DoesNotExist:
            raise Exception('Perfil de usuario no encontrado.')
        return user_profile.following.all()

    def resolve_followers(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Usuario no logueado.')
        try:
            user_profile = UserFollowerList.objects.get(user=user)
        except UserFollowerList.DoesNotExist:
            raise Exception('Perfil de usuario no encontrado.')
        return user_profile.followers.all()



################################################
################## Mutation ####################
################################################

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_idea = CreateIdea.Field()
    create_follow_request = CreateFollowRequest.Field()
    create_userfollowerlist = CreateUserFollowerList.Field()
    delete_user = DeleteUser.Field()
    delete_idea = DeleteIdea.Field()
    update_user = UpdateUser.Field()
    update_idea = UpdateIdea.Field()
    token_auth_with_email = TokenAuthWithEmail.Field()
    change_password = ChangePassword.Field()
    send_reset_password_email = SendResetPasswordEmail.Field()
    respond_to_follow_request = RespondToFollowRequest.Field()
    unfollow_user = UnfollowUser.Field()
    remove_follower = RemoveFollower.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)