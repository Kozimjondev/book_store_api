from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


    # {
    #     "email": "test@gmail.com",
    #     "first_name": "test1",
    #     "last_name": "testov",
    #     "phone_number": "998950301580",
    #     "password": "rewardof0829",
    #     "password2": "rewardof0829"
    # }
    #
    # {
    #     "email": "test1@gmail.com",
    #     "password": "rewardof0829"
    # }
