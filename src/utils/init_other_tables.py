import psycopg2


conn = psycopg2.connect(
    host="postgresql-885217.user-victorjean",
    port=5432,
    database="defaultdb",
    user="user-victorjean",
    password="pr9yh1516s57jjnmw7ll",
)
cur = conn.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS decks (
    deck_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INT NOT NULL,
    card_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);

CREATE TABLE IF NOT EXISTS user_deck_link (
    user_id INT NOT NULL,
    deck_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id INT NOT NULL,
    card_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);

CREATE TABLE IF NOT EXISTS histories (
    history_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    prompt TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""")


conn.commit()
cur.close()
conn.close()


print("All tables created successfully.")
