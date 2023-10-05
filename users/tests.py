from django.test import TestCase
from django.contrib.auth.models import User
from graphene.test import Client
from .schema import schema

# Create your tests here.
class UserMutationTestCase(TestCase):
    def setUp(self):
        # Configuramos el cliente GraphQL para realizar consultas y mutaciones
        self.client = Client(schema)

    def test_create_user_mutation(self):
        # Vamos a comenzar creando un text para CreateUser.
        query = '''
            mutation {
                createUser(username: "testuser", email: "test@example.com", password: "testpassword") {
                    user {
                        id
                        username
                        email
                    }
                }
            }
        '''

        # Enviamos la consulta al servidor GraphQL.
        response = self.client.execute(query)

        # Comprobamos que la respuesta no devuelve errores.
        if 'errors' in response:
            self.assertIsNone(response.errors)  

        # Comprobamos y validamos que username e email se corresponden con la mutation lanzada.
        created_user = response.data['createUser']['user']
        self.assertEqual(created_user['username'], "testuser")
        self.assertEqual(created_user['email'], "test@example.com")