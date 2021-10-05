CREATE TABLE items
(
    id    serial primary key,
    name  text,
    price money
);

INSERT INTO items (name, price)
VALUES ('item 123', 100),
       ('item 124', 200),
       ('item 124', 350)