## Сборка и запуск
```shell
pip install -r requirements.txt
uvicorn main:app --reload
```

## Запуск всех тестов
```shell
pytest
```

## Схема GraphQL
```
type Query {
    person: Person
}

type Person {
    first_name: String
    last_name: String
    pet: Pet
}

type Pet {
    name: String
    age: Int
}
```

## Документация
- [GraphQL](http://127.0.0.1:8000/graphql)
- [API](http://127.0.0.1:8000/docs)