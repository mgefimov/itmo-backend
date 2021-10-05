from graphene import ObjectType, Field, String, Int


class Pet(ObjectType):
    name = String()
    age = Int()


class Person(ObjectType):
    first_name = String()
    last_name = String()
    pet = Field(Pet)


class Query(ObjectType):
    person = Field(Person, uid=String())

    def resolve_person(root, info, uid):
        return persons[uid]


persons = {
    '123': Person(first_name='Max', last_name="Efimov", pet=Pet(name='Vasya', age=3)),
    '124': Person(first_name='Ivan', last_name="Ivanov", pet=Pet(name='Vasya', age=4))
}