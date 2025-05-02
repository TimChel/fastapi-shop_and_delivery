from fastapi import Body


exampl_create_user = Body(
    openapi_examples={
        "покупатель": {
            "summary": "Создание покупателя",
            "description": "Запрос для ручного создания аккаунта для покупателя (уровень доступа - 'customer')",
            "value": {
                "name": "Иван",
                "email": "abra@gmail.com",
                "access_level": "customer"
            }
        },
        "поставщик": {
            "summary": "Создание поставщика",
            "description": "Запрос для ручного создания аккаунта для поставщика (уровень доступа - 'provider')",
            "value": {
                "name": "Иван",
                "email": "abra@gmail.com",
                "access_level": "provider"
            }
        },
        "администратор": {
            "summary": "Создание администратора",
            "description": "Запрос для ручного создания аккаунта для администратора (уровень доступа - 'admin')",
            "value": {
                "name": "Иван",
                "email": "abra@gmail.com",
                "access_level": "admin"
            }
        }
    }
)